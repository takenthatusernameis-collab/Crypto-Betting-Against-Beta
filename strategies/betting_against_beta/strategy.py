"""High-level Betting Against Beta (BAB) strategy entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as _np

from .backtest import run_backtest
from .beta import calculate_rolling_beta
from .config import BABConfig
from .data import generate_synthetic_returns
from .data_loader import load_returns
from .portfolio import construct_portfolio
from .signals import generate_bab_signals
from . import sizing
from . import shorting
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
        try:
            beta_neutral_flag = (
                bool(getattr(cfg, "beta_neutral", False))
                or bool(getattr(cfg, "beta_neutral_enforcement", False))
                or bool(getattr(cfg, "beta_neutral_correction", False))
                or bool(getattr(cfg, "beta_neutral_adjustment", False))
            )
            if beta_neutral_flag:
                from . import portfolio as _portfolio
                target_beta = getattr(cfg, "beta_target", 0.0)
                tol = getattr(cfg, "beta_tolerance", getattr(cfg, "max_beta_drift", 1e-4))
                max_drift = getattr(cfg, "max_beta_drift", tol)
                te_tol = getattr(cfg, "tracking_error_tolerance", None) or getattr(cfg, "tracking_error_limit", None)
                enable_te = bool(getattr(cfg, "enable_tracking_error_monitoring", False)) or te_tol is not None
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
                    correction=True,
                )
        except BABDataError:
            raise
        except Exception:
            pass

        # Explicit finiteness guard (single pass; construct_portfolio already
        # returns finite weights, this is a defensive final clamp).
        weights = weights.replace([_np.inf, -_np.inf], _np.nan).fillna(0.0)
        if not _np.isfinite(weights.to_numpy(dtype=float)).all():
            weights_arr = weights.to_numpy(dtype=float)
            weights_arr[~_np.isfinite(weights_arr)] = 0.0
            weights = type(weights)(weights_arr, index=weights.index, columns=weights.columns)
        backtest = run_backtest(returns, weights, transaction_costs=cfg.transaction_costs, slippage=getattr(cfg, "slippage", 0.0))

        return BABResult(
            config=cfg,
            returns=returns,
            betas=betas,
            signals=signals,
            weights=weights,
            backtest=backtest,
        )