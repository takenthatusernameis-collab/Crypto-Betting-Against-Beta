"""High-level Betting Against Beta (BAB) strategy entrypoint."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as _np

from .backtest import run_backtest
from .beta import calculate_rolling_beta
from .config import BABConfig
from .data import generate_synthetic_returns
from .data_loader import load_returns
from .portfolio import construct_portfolio
from .signals import generate_bab_signals
from . import metrics
from . import sizing
from . import shorting
from .attribution import trade_attribution, attribution_totals
from .errors import BABDataError


def _rebalance_mask(index, freq: str) -> "pd.Series":  # noqa: ANN401
    """Return a boolean Series (aligned to ``index``) marking rebalance dates.

    The first date is always a rebalance date. For ``daily`` every date is a
    rebalance date. For ``weekly``/``monthly`` only the first date within each
    calendar week/month is marked, so weights are held constant between
    rebalance dates.
    """
    import pandas as pd  # local import keeps module import light

    freq = (freq or "daily").lower()
    mask = pd.Series(False, index=index)
    if len(index) == 0:
        return mask
    mask.iloc[0] = True
    if freq == "daily":
        mask[:] = True
        return mask

    if isinstance(index, pd.DatetimeIndex):
        if freq.startswith("week"):
            period = index.to_period("W")
        elif freq.startswith("month"):
            period = index.to_period("M")
        else:
            mask[:] = True
            return mask
        mask = pd.Series(~pd.Series(period).duplicated(keep="first").to_numpy(), index=index)
        mask.iloc[0] = True
        return mask

    # Non-datetime index: fall back to a fixed step between rebalance dates.
    step = 7 if freq.startswith("week") else 21
    for i in range(0, len(index), step):
        mask.iloc[i] = True
    return mask


def _apply_rebalance(signals, freq: str):
    """Hold signals constant between rebalance dates.

    Returns the rebalanced signals frame. On the first rebalance date of each
    window the freshly computed signal is used; between rebalance dates the
    signal from the most recent rebalance date is forward-filled so that
    weights (and therefore turnover) only change on rebalance dates.
    """
    import pandas as pd  # local import keeps module import light

    if signals is None or len(signals) == 0:
        return signals
    freq = (freq or "daily").lower()
    if freq == "daily":
        return signals
    mask = _rebalance_mask(signals.index, freq)
    # Wherever the mask is True, keep the freshly computed signal. Where it is
    # False, carry forward the last rebalanced signal. Rows before the first
    # rebalance date remain as computed (typically all-zero while betas are NaN).
    held = signals.where(mask).ffill()
    # Any rows still NaN after ffill (pre-first-rebalance) stay flat at zero.
    return held.fillna(0)


@dataclass
class BABResult:
    """Output of running the BAB strategy."""

    config: BABConfig
    returns: object  # pd.DataFrame of input returns
    betas: object  # pd.DataFrame of rolling betas
    signals: object  # pd.DataFrame of long/short signals
    weights: object  # pd.DataFrame of portfolio weights
    backtest: object  # pd.DataFrame of backtest results


class BABStrategy:
    """Betting Against Beta strategy: long low-beta, short high-beta crypto assets.

    Pipeline:
        1. Load/validate returns (synthetic by default, or from a CSV/JSON/DataFrame).
        2. Estimate rolling beta of each asset vs the benchmark.
        3. Rank assets by beta each period.
        4. Go long the lowest-beta quantile, short the highest-beta quantile.
        5. Construct dollar-neutral (or long-only) equal weights.
        6. Backtest with one-day lagged weights (no lookahead).
    """

    def __init__(self, config: BABConfig | None = None) -> None:
        self.config = config or BABConfig()
        # Cached result of the last ``run()``; powers the report()/tear_sheet()
        # accessors without requiring callers to re-run the pipeline.
        self._last_result: object | None = None  # noqa: ANN401

    def _load_returns(self, returns_df: object | None) -> "pd.DataFrame":  # noqa: ANN401
        """Resolve the returns DataFrame, validating it for the pipeline."""
        import pandas as pd  # local import keeps module import light

        cfg = self.config
        if returns_df is not None:
            # Explicit override wins over config.data_source.
            return load_returns(
                returns_df,
                benchmark=cfg.benchmark,
                min_rows=cfg.min_rows,
            )

        if cfg.data_source is not None:
            return load_returns(
                cfg.data_source,
                benchmark=cfg.benchmark,
                min_rows=cfg.min_rows,
            )

        universe = list(cfg.universe) if cfg.universe else None
        n_assets = len(universe) if universe else 5
        return generate_synthetic_returns(
            n_days=cfg.synthetic_n_days,
            n_assets=n_assets,
            asset_names=universe,
            benchmark_name=cfg.benchmark,
            seed=cfg.synthetic_seed,
        )

    def run(self, returns_df: object | None = None) -> BABResult:  # noqa: ANN401
        """Run the full strategy pipeline and return results."""
        import pandas as pd

        cfg = self.config
        returns = self._load_returns(returns_df)

        # Resolve the effective universe from the validated data and persist it so
        # downstream consumers (reports, diagnostics) see the actual tradable
        # set rather than the configured default.
        effective_universe = cfg.resolved_universe(list(returns.columns))
        if not effective_universe:
            raise ValueError(
                "No tradable assets remain after intersecting the configured "
                f"universe {cfg.universe} with data columns {list(returns.columns)}"
            )
        try:
            object.__setattr__(cfg, "universe", effective_universe)
            object.__setattr__(cfg, "_frozen", True)
        except Exception:
            cfg.universe = effective_universe

        betas = calculate_rolling_beta(
            returns,
            cfg.benchmark,
            window=cfg.beta_window,
            min_obs=cfg.min_observations,
        )
        signals = generate_bab_signals(
            betas, long_quantile=cfg.long_quantile, short_quantile=cfg.short_quantile
        )

        rebalance_freq = getattr(cfg, "rebalance_freq", "daily") or "daily"
        rebalance_freq = str(rebalance_freq).lower()
        if rebalance_freq != "daily" and len(signals) > 0:
            # Hold signals constant between rebalance dates so weights (and
            # therefore turnover/costs) only change on rebalance dates.
            signals = _apply_rebalance(signals, rebalance_freq)

        _max_turnover = getattr(cfg, "max_turnover", None) or getattr(cfg, "max_total_turnover", None)
        _enforce_risk = bool(getattr(cfg, "enforce_risk_checks", False) or getattr(cfg, "risk_checks", False))
        weights = construct_portfolio(
            signals,
            dollar_neutral=cfg.dollar_neutral,
            max_position_size=getattr(cfg, "max_position_size", None),
            max_turnover=_max_turnover,
            enforce_risk_checks=_enforce_risk,
            gross_exposure_limit=getattr(cfg, "gross_exposure_limit", None),
            net_exposure_limit=getattr(cfg, "net_exposure_limit", None),
            max_single_weight=getattr(cfg, "max_single_weight", None),
        )
        # Apply shorting constraints if configured
        try:
            sc = getattr(cfg, "shorting_constraints", None)
            if sc is not None:
                weights = shorting.apply_shorting_constraints(weights, sc)
        except BABDataError:
            raise
        except Exception:
            pass
        # Optional dynamic position sizing
        try:
            ps = getattr(cfg, "position_sizer", None)
            if ps is not None:
                weights = sizing.apply_position_sizing(signals, returns=returns, betas=betas, sizer=ps)
        except Exception:
            # Do not break default behavior on sizing errors; fall back to weights
            pass

        # Optional regime-based position scaling.  Regime at date t is computed
        # from returns up to t (causal, no lookahead); the backtest shifts
        # weights by one day, so weights at t are applied to returns at t+1.
        # Scaling every weight by a positive factor preserves dollar neutrality,
        # so the public portfolio API contract is unchanged.
        try:
            if bool(getattr(cfg, "regime_filter", False)):
                from . import regime as _regime
                scale_factors = _regime.regime_scale_factors(returns, cfg)
                if scale_factors is not None and not scale_factors.empty:
                    scale_factors = scale_factors.reindex(
                        index=weights.index, columns=weights.columns
                    ).fillna(1.0)
                    weights = weights * scale_factors
        except Exception:
            # Do not break default behavior on regime errors; fall back to unscaled weights
            pass

        # Beta-neutral enforcement / drift detection (multi-file, no lookahead)
        beta_neutral_enabled = bool(getattr(cfg, "beta_neutral", False)) or bool(
            getattr(cfg, "beta_neutral_enforcement", False)
        )
        if beta_neutral_enabled:
            from . import portfolio as _portfolio
            target_beta = getattr(cfg, "beta_target", 0.0)
            tol = getattr(cfg, "beta_tolerance", getattr(cfg, "max_beta_drift", 1e-4))
            max_drift = getattr(cfg, "max_beta_drift", tol)
            te_tol = getattr(cfg, "tracking_error_tolerance", None) or getattr(cfg, "tracking_error_limit", None)
            enable_te = bool(getattr(cfg, "enable_tracking_error_monitoring", False)) or te_tol is not None
            correction = bool(getattr(cfg, "beta_neutral_correction", True))
            # Use betas up to t only (causal) - betas are already computed causally
            benchmark_ret = returns[cfg.benchmark] if cfg.benchmark in returns.columns else None
            weights = _portfolio.enforce_beta_neutrality(
                weights,
                betas,
                target_beta=target_beta,
                tolerance=tol,
                max_drift=max_drift,
                returns=returns,
                benchmark_returns=benchmark_ret,
                tracking_error_tolerance=te_tol,
                tracking_error_limit=te_tol,
                enable_tracking_error_monitoring=enable_te,
                correction=correction,
            )

        # Explicit finiteness guard (single pass; construct_portfolio already
        # returns finite weights, this is a defensive final clamp). Operate
        # in-place on the existing DataFrame to avoid an extra allocation.
        wa = weights.to_numpy(dtype=float)
        if not _np.isfinite(wa).all():
            if not wa.flags.writeable:
                wa = wa.copy()
            wa[~_np.isfinite(wa)] = 0.0
            weights.iloc[:] = wa
        backtest = run_backtest(returns, weights, transaction_costs=cfg.transaction_costs, slippage=getattr(cfg, "slippage", 0.0))

        result = BABResult(
            config=cfg,
            returns=returns,
            betas=betas,
            signals=signals,
            weights=weights,
            backtest=backtest,
        )
        # Cache so report()/tear_sheet() can be called without re-running.
        self._last_result = result
        return result

    def report(self, result: "BABResult | None" = None) -> dict:
        """Return a structured performance report for the last (or given) run.

        The report bundles the scalar summary metrics, the per-period
        trade-attribution frame, and the attribution totals so callers can
        consume a single object without re-running the pipeline.  All metrics
        are causal (no lookahead) and deterministic for a fixed input.

        Raises ``RuntimeError`` if no result has been run and ``result`` is
        ``None``.
        """
        res = result if result is not None else self._last_result
        if res is None:
            raise RuntimeError(
                "BABStrategy.report() called before run(). Call run() first "
                "or pass an explicit BABResult."
            )

        returns = res.backtest["returns"]
        benchmark_returns = res.returns[str(res.config.benchmark)] if res.config.benchmark in res.returns.columns else None
        summary = metrics.summary(
            returns,
            weights_df=res.weights,
            benchmark_returns=benchmark_returns,
        )
        attribution = trade_attribution(res.backtest)
        totals = attribution_totals(attribution)

        return {
            "config": {
                "universe": list(res.config.universe),
                "benchmark": res.config.benchmark,
                "beta_window": res.config.beta_window,
                "min_observations": res.config.min_observations,
                "long_quantile": res.config.long_quantile,
                "short_quantile": res.config.short_quantile,
                "transaction_costs": res.config.transaction_costs,
                "data_source": res.config.data_source,
            },
            "rebalances": int(len(res.weights.dropna(how="all"))),
            "metrics": summary,
            "attribution": attribution,
            "attribution_totals": totals,
        }

    def tear_sheet(self, result: "BABResult | None" = None) -> str:
        """Return a human-readable tear-sheet string for the last (or given) run.

        Combines the summary metrics and trade-attribution breakdown into a
        single printable block suitable for console output or persistence.
        """
        rep = self.report(result)
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("BAB STRATEGY TEAR SHEET")
        lines.append("=" * 60)
        lines.append(f"Universe: {', '.join(rep['config']['universe'])}")
        lines.append(f"Benchmark: {rep['config']['benchmark']}")
        lines.append(f"Beta window: {rep['config']['beta_window']} days (min {rep['config']['min_observations']} obs)")
        lines.append(f"Long/Short quantiles: {rep['config']['long_quantile']}/{rep['config']['short_quantile']}")
        lines.append(f"Rebalances: {rep['rebalances']}")
        lines.append("-" * 60)
        lines.append(f"Final Cumulative: {rep['metrics']['final_cumulative']:.4f}x ({rep['metrics']['total_return']:.2%})")
        lines.append(f"Sharpe Ratio (ann.): {rep['metrics']['sharpe_ratio']:.4f}")
        lines.append(f"Annualized Volatility: {rep['metrics']['annualized_volatility']:.2%}")
        lines.append(f"Max Drawdown: {rep['metrics']['max_drawdown']:.2%}")
        lines.append(f"Turnover (avg): {rep['metrics']['turnover']:.4f}")
        lines.append(f"Strategy Beta vs {rep['config']['benchmark']}: {rep['metrics']['strategy_beta']:.4f}")
        lines.append(f"Observations: {rep['metrics']['n_observations']}")
        lines.append("-" * 60)
        lines.append("Trade Attribution (cumulative):")
        lines.append(f"  Gross Return:   {rep['attribution_totals']['gross_return']:.6f}")
        lines.append(f"  Cost Drag:      {rep['attribution_totals']['cost_drag']:.6f}")
        lines.append(f"  Slippage Drag:  {rep['attribution_totals']['slippage_drag']:.6f}")
        lines.append(f"  Net Return:     {rep['attribution_totals']['net_return']:.6f}")
        lines.append(f"  Cost Share:     {rep['attribution_totals']['cost_share']:.2%}")
        lines.append(f"  Slippage Share: {rep['attribution_totals']['slippage_share']:.2%}")
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def report_to_json(report: dict) -> str:
        """Serialize a report dict to a strict, JSON-safe string.

        NaN/inf tokens are coerced to 0.0 so the output is always valid JSON
        per RFC 8259 (strict parsers such as Go/Rust reject bare NaN/Infinity).
        """
        def _clean(obj):
            if isinstance(obj, dict):
                return {str(k): _clean(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [_clean(v) for v in obj]
            if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                return 0.0
            return obj

        return json.dumps(_clean(report), indent=2, default=str, allow_nan=False)