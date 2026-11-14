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
from .data_loader import load_prices, load_returns
from .portfolio import construct_portfolio
from .signals import generate_bab_signals
from . import metrics
from . import sizing
from . import shorting
from .attribution import trade_attribution, attribution_totals
from .errors import BABDataError
from .shorting import ShortingConstraints
from .sizing import KellySizer, VolatilityTargetSizer, RiskParitySizer, EqualWeightSizer
from . import risk as _risk
from .risk import KillSwitchEvent


def _normalize_position_sizer(ps):
        """Coerce a dict shorthand into a sizer instance, or return as-is.

        Recognized shorthands:
          * ``{"type": "equal"}`` -> :class:`EqualWeightSizer`
          * ``{"type": "kelly", ...}`` -> :class:`KellySizer`
          * ``{"type": "vol_target", ...}`` -> :class:`VolatilityTargetSizer`
          * ``{"type": "risk_parity", ...}`` -> :class:`RiskParitySizer`

        Any other dict raises ``BABDataError`` so misconfiguration surfaces loudly
        instead of being silently ignored.
        """
        if not isinstance(ps, dict):
            return ps
        s = str(ps.get("type", "")).lower()
        if s == "equal":
            return EqualWeightSizer(max_leverage=float(ps.get("max_leverage", 1.0)))
        if s in ("kelly", "kelly_fraction"):
            return KellySizer(
                lookback=int(ps.get("lookback", 60)),
                max_leverage=float(ps.get("max_leverage", 1.0)),
                fraction=float(ps.get("fraction", 1.0)),
            )
        if s in ("vol_target", "volatility_target", "voltarget"):
            return VolatilityTargetSizer(
                target_vol=float(ps.get("target_vol", 0.10)),
                lookback=int(ps.get("lookback", 60)),
                annualize=int(ps.get("annualize", 252)),
                max_leverage=float(ps.get("max_leverage", 2.0)),
            )
        if s in ("risk_parity", "riskparity", "rp"):
            return RiskParitySizer(
                lookback=int(ps.get("lookback", 60)),
                max_leverage=float(ps.get("max_leverage", 1.0)),
                target_vol=ps.get("target_vol"),
                annualize=int(ps.get("annualize", 252)),
            )
        raise BABDataError(f"position_sizer dict has unknown type: {s!r}")


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
    kill_switch: object = None  # KillSwitchEvent from risk.py


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

    def __init__(self, config: BABConfig | None = None, **kwargs) -> None:
        if config is None and kwargs:
            # Support flexible kwargs
            cfg_kwargs = {}
            for k in ['universe', 'benchmark', 'beta_window', 'rebalance_freq', 'long_quantile',
                      'short_quantile', 'dollar_neutral', 'min_observations', 'data_source',
                      'min_rows', 'transaction_costs', 'slippage', 'max_turnover', 'max_position_size',
                      'max_total_turnover', 'rolling_min_window', 'synthetic_seed', 'synthetic_n_days',
                      'universe_override', 'position_sizer', 'shorting_constraints', 'regime_filter',
                      'regime_method', 'vol_window', 'vol_use_ewma', 'vol_thresholds', 'vol_percentiles',
                      'vol_hysteresis', 'trend_ma_window', 'trend_z_window', 'regime_scale_high',
                      'regime_scale_low', 'beta_neutral', 'beta_neutral_enforcement', 'beta_target',
                      'beta_tolerance', 'max_beta_drift', 'tracking_error_tolerance', 'tracking_error_limit',
                      'enable_tracking_error_monitoring', 'beta_neutral_correction', 'beta_neutral_adjustment',
                      # R3-A: realistic execution cost model plumbing
                      'cost_model', 'prices', 'adv_usd', 'partial_fill', 'max_participation']:
                if k in kwargs:
                    cfg_kwargs[k] = kwargs[k]
            # aliases
            if 'window' in kwargs and 'beta_window' not in cfg_kwargs:
                cfg_kwargs['beta_window'] = kwargs['window']
            if 'min_obs' in kwargs and 'min_observations' not in cfg_kwargs:
                cfg_kwargs['min_observations'] = kwargs['min_obs']
            config = BABConfig(**cfg_kwargs)
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

    @staticmethod
    def _resolve_cost_model(cfg) -> tuple:
        """Resolve the R3-A execution-cost plumbing from config.

        Returns ``(cost_model, prices_df, adv_usd)`` where ``cost_model`` is a
        ``TransactionCostModel`` instance or ``None``. When ``cost_model`` is
        ``None`` the returned tuple is ``(None, None, None)`` so the caller can
        pass the whole tuple into ``run_backtest`` and get byte-identical
        pre-R3 behavior (flat ``transaction_costs``/``slippage`` only).

        Raises ``BABDataError`` on a wrong-typed ``cost_model`` so a
        misconfiguration surfaces loudly instead of being silently ignored.
        """
        import pandas as pd  # local import keeps module import light

        from .costs import TransactionCostModel as _TCM

        cm = getattr(cfg, "cost_model", None)
        if cm is None:
            return None, None, None
        if isinstance(cm, dict):
            try:
                cm = _TCM(**cm)
            except (TypeError, ValueError) as e:
                raise BABDataError(f"cost_model dict is invalid: {e}") from e
        if not isinstance(cm, _TCM):
            raise BABDataError(
                f"cost_model must be a TransactionCostModel, dict, or None, "
                f"got {type(cm).__name__}"
            )

        prices = getattr(cfg, "prices", None)
        adv = getattr(cfg, "adv_usd", None)

        # Resolve prices: a path string is loaded via the data loader; a
        # DataFrame is used directly; anything else is treated as absent so
        # the impact term is skipped (not an error) for that asset.
        prices_df = None
        if prices is not None:
            if isinstance(prices, str):
                try:
                    prices_df = load_prices(prices, benchmark=getattr(cfg, "benchmark", None))
                except Exception as e:
                    raise BABDataError(f"failed to load prices from {prices!r}: {e}") from e
            elif isinstance(prices, pd.DataFrame):
                prices_df = prices
            else:
                # Unknown prices type: skip impact rather than crash.
                prices_df = None
        return cm, prices_df, adv

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
        # Subset returns to the effective tradable universe + benchmark. Without
        # this, --universe/config subsets are accepted and reported but silently
        # ignored by beta/signal/portfolio computation (all data columns used).
        subset_cols = []
        bench = getattr(cfg, "benchmark", None)
        if bench is not None and bench in returns.columns and bench not in subset_cols:
            subset_cols.append(bench)
        for a in effective_universe:
            if a in returns.columns and a not in subset_cols:
                subset_cols.append(a)
        if subset_cols:
            returns = returns.loc[:, [c for c in subset_cols if c in returns.columns]].copy()
        try:
            object.__setattr__(cfg, "universe", effective_universe)
            object.__setattr__(cfg, "_frozen", True)
        except (AttributeError, TypeError):
            # Fallback for dataclasses with slots or other attribute restrictions.
            # A frozen dataclass raises FrozenInstanceError (subclass of
            # AttributeError) on assignment; we catch only that family rather
            # than a bare ``Exception`` so programming errors surface loudly.
            cfg.universe = effective_universe

        try:
            betas = calculate_rolling_beta(
                returns,
                cfg.benchmark,
                window=cfg.beta_window,
                min_obs=min(getattr(cfg, 'min_observations', cfg.beta_window), cfg.beta_window),
            )
        except Exception as e:
            raise BABDataError(f"beta calculation failed: {e}") from e


        try:
            signals = generate_bab_signals(
                betas, long_quantile=cfg.long_quantile, short_quantile=cfg.short_quantile
            )
        except Exception as e:
            raise BABDataError(f"signal generation failed: {e}") from e

        try:
            rebalance_freq = getattr(cfg, "rebalance_freq", "daily") or "daily"
            rebalance_freq = str(rebalance_freq).lower()
            if rebalance_freq != "daily" and len(signals) > 0:
                # Hold signals constant between rebalance dates so weights (and
                # therefore turnover/costs) only change on rebalance dates.
                signals = _apply_rebalance(signals, rebalance_freq)
        except BABDataError:
            raise
        except Exception as e:
            raise BABDataError(f"rebalance application failed: {e}") from e

        try:
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
        except BABDataError:
            raise
        except Exception as e:
            raise BABDataError(f"portfolio construction failed: {e}") from e
        # Apply shorting constraints if configured
        try:
            sc = getattr(cfg, "shorting_constraints", None)
            if sc is not None:
                if not isinstance(sc, (ShortingConstraints, dict)):
                    raise BABDataError(
                        f"shorting_constraints must be a ShortingConstraints or dict, "
                        f"got {type(sc).__name__}"
                    )
                weights = shorting.apply_shorting_constraints(weights, sc)
        except BABDataError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise BABDataError(f"shorting_constraints failed: {e}") from e
        # Optional dynamic position sizing
        try:
            ps = getattr(cfg, "position_sizer", None)
            if ps is not None:
                if isinstance(ps, dict):
                    ps = _normalize_position_sizer(ps)
                if not isinstance(ps, (KellySizer, VolatilityTargetSizer, RiskParitySizer, EqualWeightSizer, str)):
                    raise BABDataError(
                        f"position_sizer must be a sizer or string shorthand, "
                        f"got {type(ps).__name__}"
                    )
                weights = sizing.apply_position_sizing(signals, returns=returns, betas=betas, sizer=ps)
        except BABDataError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise BABDataError(f"position_sizer failed: {e}") from e

        # Optional regime-based position scaling.  Regime at date t is computed
        # from returns up to t (causal, no lookahead); the backtest shifts
        # weights by one day, so weights at t are applied to returns at t+1.
        # Scaling every weight by a single scalar per date preserves dollar
        # neutrality exactly (per-asset regime factors would break it), so the
        # public portfolio API contract is unchanged.
        try:
            regime_flag = getattr(cfg, "regime_filter", False)
            if not isinstance(regime_flag, bool):
                raise BABDataError(
                    f"regime_filter must be a bool, got {type(regime_flag).__name__}"
                )
            if regime_flag:
                from . import regime as _regime
                scale = _regime.regime_scale_scalar(returns, cfg)
                if scale is not None and not scale.empty:
                    aligned = scale.reindex(index=weights.index).fillna(1.0)
                    weights = weights.mul(aligned, axis=0)
        except BABDataError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise BABDataError(f"regime_filter failed: {e}") from e

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
        # returns finite weights, this is a defensive final clamp).  One
        # conversion + one clamp + one write; the previous second read/clamp
        # pass was provably redundant (the first pass already made every entry
        # finite, so the second isfinite check could only ever be all-True).
        try:
            wa = weights.to_numpy(dtype=float)
            if not _np.isfinite(wa).all():
                if not wa.flags.writeable:
                    wa = wa.copy()
                wa[~_np.isfinite(wa)] = 0.0
                weights.iloc[:] = wa
        except Exception as exc:
            try:
                weights = weights.replace([_np.inf, -_np.inf], 0.0).fillna(0.0)
            except Exception as exc2:
                # The fallback also failed: weights is uncoercible (exotic
                # dtype, read-only buffer, overridden replace/fillna).  A
                # silent swallow here would pass a corrupt, non-finite frame
                # into run_backtest and silently produce wrong P&L, so surface
                # it as a BABDataError with both exceptions chained.
                raise BABDataError(
                    f"weight finiteness cleanup failed: {exc2} (outer: {exc})"
                ) from exc2
        # R3-A: resolve the realistic execution-cost plumbing. When cost_model is
        # None this returns (None, None, None) and the run_backtest call below
        # falls through to the flat transaction_costs/slippage path, which is
        # byte-identical to pre-R3 behavior.
        cost_model, prices_df, adv_usd = self._resolve_cost_model(cfg)
        partial_fill = bool(getattr(cfg, "partial_fill", False))

        backtest = run_backtest(
            returns,
            weights,
            transaction_costs=cfg.transaction_costs,
            slippage=getattr(cfg, "slippage", 0.0),
            cost_model=cost_model,
            prices_df=prices_df,
            adv_usd=adv_usd,
            partial_fill=partial_fill,
            max_participation=getattr(cfg, "max_participation", 0.10),
        )

        # R4-B: Apply drawdown-limit kill switch
        # Extract cumulative returns from backtest to monitor drawdown
        from .risk import apply_kill_switch, KillSwitchEvent

        cumulative = None
        if isinstance(backtest, pd.DataFrame) and not backtest.empty:
            if "cumulative" in backtest.columns:
                cumulative = backtest["cumulative"]

        kill_switch_event = KillSwitchEvent(triggered=False, date=None, observed_drawdown=0.0, limit=None)
        final_weights = weights
        final_backtest = backtest

        mdd_limit = getattr(cfg, "max_drawdown_limit", None)
        if mdd_limit is not None and cumulative is not None:
            killed_weights, kill_switch_event = apply_kill_switch(weights, cumulative, mdd_limit)
            if kill_switch_event.triggered:
                # Re-run backtest with killed weights (flattened from breach date)
                final_weights = killed_weights
                final_backtest = run_backtest(
                    returns,
                    killed_weights,
                    transaction_costs=cfg.transaction_costs,
                    slippage=getattr(cfg, "slippage", 0.0),
                    cost_model=cost_model,
                    prices_df=prices_df,
                    adv_usd=adv_usd,
                    partial_fill=partial_fill,
                    max_participation=getattr(cfg, "max_participation", 0.10),
                )

        result = BABResult(
            config=cfg,
            returns=returns,
            betas=betas,
            signals=signals,
            weights=final_weights,
            backtest=final_backtest,
            kill_switch=kill_switch_event,
        )
        # Cache so report()/tear_sheet() can be called without re-running.
        self._last_result = result
        return result

    def dry_run(self, returns_df: object | None = None) -> dict:
        """Validate inputs and return a portfolio-risk summary without executing trades.

        Returns a strict-JSON-safe dict containing:
        - resolved config (benchmark, universe, beta_window, quantiles, costs, etc.)
        - tradable universe (effective assets after intersection with data)
        - beta window/quantiles
        - portfolio-risk summary: gross exposure, net exposure, gross leverage,
          max single-position weight, estimated turnover/cost drag
        - data-health: rows, columns, NaN counts, benchmark presence

        Raises ``BABDataError``/``BABConfigError`` on invalid inputs (no silent fallback).
        """
        import math
        import numpy as _np
        import pandas as pd

        def _safe_float(value, default=0.0):
            try:
                if value is None:
                    return float(default)
                f = float(value)
                return f if _np.isfinite(f) else float(default)
            except (TypeError, ValueError):
                return float(default)

        cfg = self.config
        returns = self._load_returns(returns_df)

        # Resolve effective universe (same logic as run())
        effective_universe = cfg.resolved_universe(list(returns.columns))
        if not effective_universe:
            raise ValueError(
                "No tradable assets remain after intersecting the configured "
                f"universe {cfg.universe} with data columns {list(returns.columns)}"
            )

        # Subset returns to effective universe + benchmark
        subset_cols = []
        bench = getattr(cfg, "benchmark", None)
        if bench is not None and bench in returns.columns and bench not in subset_cols:
            subset_cols.append(bench)
        for a in effective_universe:
            if a in returns.columns and a not in subset_cols:
                subset_cols.append(a)
        if subset_cols:
            returns = returns.loc[:, [c for c in subset_cols if c in returns.columns]].copy()

        # Compute betas
        betas = calculate_rolling_beta(
            returns,
            cfg.benchmark,
            window=cfg.beta_window,
            min_obs=min(getattr(cfg, 'min_observations', cfg.beta_window), cfg.beta_window),
        )

        # Generate signals
        signals = generate_bab_signals(
            betas, long_quantile=cfg.long_quantile, short_quantile=cfg.short_quantile
        )

        # Apply rebalance
        rebalance_freq = getattr(cfg, "rebalance_freq", "daily") or "daily"
        rebalance_freq = str(rebalance_freq).lower()
        if rebalance_freq != "daily" and len(signals) > 0:
            signals = _apply_rebalance(signals, rebalance_freq)

        # Construct portfolio (weights)
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
                if not isinstance(sc, (ShortingConstraints, dict)):
                    raise BABDataError(
                        f"shorting_constraints must be a ShortingConstraints or dict, "
                        f"got {type(sc).__name__}"
                    )
                weights = shorting.apply_shorting_constraints(weights, sc)
        except BABDataError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise BABDataError(f"shorting_constraints failed: {e}") from e

        # Optional dynamic position sizing
        try:
            ps = getattr(cfg, "position_sizer", None)
            if ps is not None:
                if isinstance(ps, dict):
                    ps = _normalize_position_sizer(ps)
                if not isinstance(ps, (KellySizer, VolatilityTargetSizer, RiskParitySizer, EqualWeightSizer, str)):
                    raise BABDataError(
                        f"position_sizer must be a sizer or string shorthand, "
                        f"got {type(ps).__name__}"
                    )
                weights = sizing.apply_position_sizing(signals, returns=returns, betas=betas, sizer=ps)
        except BABDataError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise BABDataError(f"position_sizer failed: {e}") from e

        # Regime filter
        regime_flag = getattr(cfg, "regime_filter", False)
        if regime_flag:
            from . import regime as _regime
            scale = _regime.regime_scale_scalar(returns, cfg)
            if scale is not None and not scale.empty:
                aligned = scale.reindex(index=weights.index).fillna(1.0)
                weights = weights.mul(aligned, axis=0)

        # Beta-neutral enforcement
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

        # Finite guard
        try:
            wa = weights.to_numpy(dtype=float)
            if not _np.isfinite(wa).all():
                if not wa.flags.writeable:
                    wa = wa.copy()
                wa[~_np.isfinite(wa)] = 0.0
                weights.iloc[:] = wa
        except Exception as exc:
            try:
                weights = weights.replace([_np.inf, -_np.inf], 0.0).fillna(0.0)
            except Exception as exc2:
                raise BABDataError(
                    f"weight finiteness cleanup failed: {exc2} (outer: {exc})"
                ) from exc2

        # ---- Portfolio-risk summary ----
        # Gross exposure: sum of absolute weights per period
        gross_exposure = weights.abs().sum(axis=1)
        # Net exposure: sum of weights per period (should be ~0 for dollar-neutral)
        net_exposure = weights.sum(axis=1)
        # Gross leverage: same as gross exposure for this strategy
        gross_leverage = gross_exposure
        # Max single-position weight per period
        max_single_weight = weights.abs().max(axis=1)
        # Estimated turnover: sum of absolute weight changes per period
        weight_changes = weights.diff().abs().sum(axis=1)
        # First period turnover is the full weight (from zero)
        if len(weight_changes) > 0:
            weight_changes.iloc[0] = weights.iloc[0].abs().sum()
        avg_turnover = _safe_float(weight_changes.mean())
        max_turnover_est = _safe_float(weight_changes.max())
        # Estimated cost drag: avg_turnover * (transaction_costs + slippage)
        cost_drag_estimate = avg_turnover * (_safe_float(cfg.transaction_costs) + _safe_float(getattr(cfg, "slippage", 0.0)))

        # Data-health
        n_rows = int(len(returns))
        n_cols = int(len(returns.columns))
        nan_counts = {str(k): int(v) for k, v in returns.isna().sum().items()}
        total_nans = int(returns.isna().sum().sum())
        benchmark_present = bool(bench is not None and bench in returns.columns)

        # Build strict-JSON-safe output
        output = {
            "config": {
                "benchmark": str(bench) if bench else None,
                "universe": [str(u) for u in effective_universe],
                "beta_window": int(cfg.beta_window),
                "min_observations": int(getattr(cfg, "min_observations", cfg.beta_window)),
                "long_quantile": _safe_float(cfg.long_quantile),
                "short_quantile": _safe_float(cfg.short_quantile),
                "dollar_neutral": bool(cfg.dollar_neutral),
                "rebalance_freq": str(rebalance_freq),
                "transaction_costs": _safe_float(cfg.transaction_costs),
                "slippage": _safe_float(getattr(cfg, "slippage", 0.0)),
            },
            "tradable_universe": [str(u) for u in effective_universe],
            "beta_window": int(cfg.beta_window),
            "long_quantile": _safe_float(cfg.long_quantile),
            "short_quantile": _safe_float(cfg.short_quantile),
            "portfolio_risk": {
                "gross_exposure": {
                    "mean": _safe_float(gross_exposure.mean()),
                    "max": _safe_float(gross_exposure.max()),
                    "min": _safe_float(gross_exposure.min()),
                },
                "net_exposure": {
                    "mean": _safe_float(net_exposure.mean()),
                    "max": _safe_float(net_exposure.max()),
                    "min": _safe_float(net_exposure.min()),
                },
                "gross_leverage": {
                    "mean": _safe_float(gross_leverage.mean()),
                    "max": _safe_float(gross_leverage.max()),
                    "min": _safe_float(gross_leverage.min()),
                },
                "max_single_weight": {
                    "mean": _safe_float(max_single_weight.mean()),
                    "max": _safe_float(max_single_weight.max()),
                    "min": _safe_float(max_single_weight.min()),
                },
                "estimated_turnover": {
                    "mean": avg_turnover,
                    "max": max_turnover_est,
                },
                "estimated_cost_drag": _safe_float(cost_drag_estimate),
            },
            "data_health": {
                "rows": n_rows,
                "columns": n_cols,
                "nan_counts": nan_counts,
                "total_nans": total_nans,
                "benchmark_present": benchmark_present,
                "benchmark": str(bench) if bench else None,
            },
        }
        return output

    def report(self, result: "BABResult | None" = None) -> dict:
        """Return a structured performance report for the last (or given) run.

        The report bundles the scalar summary metrics, the per-period
        trade-attribution frame, and the attribution totals so callers can
        consume a single object without re-running the pipeline.  All metrics
        are causal (no lookahead) and deterministic for a fixed input.

        Raises ``RuntimeError`` if no result has been run and ``result`` is
        ``None``.

        This method is defensive against malformed/None results: a missing
        backtest frame, empty weights, or a benchmark absent from the returns
        frame yields zero-filled metrics rather than raising, so the report
        path never crashes on degenerate pipeline output.
        """
        res = result if result is not None else self._last_result
        if res is None:
            raise RuntimeError(
                "BABStrategy.report() called before run(). Call run() first "
                "or pass an explicit BABResult."
            )

        import math
        import numpy as _np
        import pandas as pd

        def _safe_metric(value, default=0.0):
            """Coerce a possibly-nan/inf scalar to a finite float, never raising."""
            try:
                if value is None:
                    return float(default)
                f = float(value)
                return f if _np.isfinite(f) else float(default)
            except (TypeError, ValueError):
                return float(default)

        backtest = getattr(res, "backtest", None)
        weights = getattr(res, "weights", None)
        returns = getattr(res, "returns", None)

        # Extract the per-period strategy return series defensively.
        strat_returns = None
        if isinstance(backtest, pd.DataFrame) and not backtest.empty:
            if "returns" in backtest.columns:
                strat_returns = backtest["returns"]
            else:
                for col in backtest.columns:
                    if "return" in str(col).lower():
                        strat_returns = backtest[col]
                        break

        # Benchmark return series (optional; missing benchmark yields NaN beta).
        benchmark_returns = None
        bench = getattr(getattr(res, "config", None), "benchmark", None)
        if bench is not None and isinstance(returns, pd.DataFrame) and not returns.empty:
            if bench in returns.columns:
                benchmark_returns = returns[bench]

        summary = metrics.summary(
            strat_returns if strat_returns is not None else pd.Series(dtype="float64"),
            weights_df=weights if isinstance(weights, pd.DataFrame) else None,
            benchmark_returns=benchmark_returns,
            betas_df=getattr(res, "betas", None) if isinstance(getattr(res, "betas", None), pd.DataFrame) else None,
        )
        # Ensure every summary value is a finite scalar so downstream formatting
        # and JSON serialization never encounter NaN/inf tokens.
        sanitized_summary = {k: _safe_metric(v) for k, v in summary.items()}

        attribution = trade_attribution(backtest if isinstance(backtest, pd.DataFrame) else pd.DataFrame())
        totals = attribution_totals(attribution)
        sanitized_totals = {k: _safe_metric(v) for k, v in totals.items()}

        # Rebalances: count non-all-NaN weight rows defensively.
        try:
            if isinstance(weights, pd.DataFrame) and not weights.empty:
                rebalances = int(len(weights.dropna(how="all")))
            else:
                rebalances = 0
        except Exception:
            rebalances = 0

        cfg = getattr(res, "config", None)
        # R4-B: Include kill_switch event if present
        kill_switch = getattr(res, "kill_switch", None)
        kill_switch_dict = None
        if kill_switch is not None:
            try:
                kill_switch_dict = kill_switch.to_dict()
            except Exception:
                kill_switch_dict = None
        return {
            "config": {
                "universe": list(getattr(cfg, "universe", []) or []),
                "benchmark": getattr(cfg, "benchmark", None),
                "beta_window": getattr(cfg, "beta_window", 90),
                "min_observations": getattr(cfg, "min_observations", 60),
                "long_quantile": getattr(cfg, "long_quantile", 0.3),
                "short_quantile": getattr(cfg, "short_quantile", 0.3),
                "transaction_costs": getattr(cfg, "transaction_costs", 0.0),
                "data_source": getattr(cfg, "data_source", None),
            },
            "rebalances": rebalances,
            "metrics": sanitized_summary,
            "attribution": attribution,
            "attribution_totals": sanitized_totals,
            "kill_switch": kill_switch_dict,
        }

    def tear_sheet(self, result: "BABResult | None" = None) -> str:
        """Return a human-readable tear-sheet string for the last (or given) run.

        Combines the summary metrics and trade-attribution breakdown into a
        single printable block suitable for console output or persistence.

        Defensive: any non-finite or missing metric is rendered as ``0.0`` /
        ``0.00%`` so a degenerate pipeline output never raises here.
        """
        rep = self.report(result)

        def _fmt(value, spec):
            """Format a scalar defensively, substituting 0.0 for non-finite."""
            try:
                f = float(value)
                if not math.isfinite(f):
                    f = 0.0
                return format(f, spec)
            except (TypeError, ValueError):
                return format(0.0, spec)

        m = rep["metrics"]
        t = rep["attribution_totals"]
        cfg = rep["config"]
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("BAB STRATEGY TEAR SHEET")
        lines.append("=" * 60)
        lines.append(f"Universe: {', '.join(cfg['universe'])}")
        lines.append(f"Benchmark: {cfg['benchmark']}")
        lines.append(f"Beta window: {cfg['beta_window']} days (min {cfg['min_observations']} obs)")
        lines.append(f"Long/Short quantiles: {cfg['long_quantile']}/{cfg['short_quantile']}")
        lines.append(f"Rebalances: {rep['rebalances']}")
        lines.append("-" * 60)
        lines.append(f"Final Cumulative: {_fmt(m['final_cumulative'], '.4f')}x ({_fmt(m['total_return'], '.2%')})")
        lines.append(f"Sharpe Ratio (ann.): {_fmt(m['sharpe_ratio'], '.4f')}")
        lines.append(f"Annualized Volatility: {_fmt(m['annualized_volatility'], '.2%')}")
        lines.append(f"Max Drawdown: {_fmt(m['max_drawdown'], '.2%')}")
        lines.append(f"Turnover (avg): {_fmt(m['turnover'], '.4f')}")
        lines.append(f"Strategy Beta vs {cfg['benchmark']}: {_fmt(m['strategy_beta'], '.4f')}")
        lines.append(f"Portfolio Beta (gross-exp wt): {_fmt(m.get('portfolio_beta', float('nan')), '.4f')}")
        lines.append(f"Observations: {int(m.get('n_observations', 0))}")
        lines.append("-" * 60)
        lines.append("Trade Attribution (cumulative):")
        lines.append(f"  Gross Return:   {_fmt(t['gross_return'], '.6f')}")
        lines.append(f"  Cost Drag:      {_fmt(t['cost_drag'], '.6f')}")
        lines.append(f"  Slippage Drag:  {_fmt(t['slippage_drag'], '.6f')}")
        lines.append(f"  Net Return:     {_fmt(t['net_return'], '.6f')}")
        lines.append(f"  Cost Share:     {_fmt(t['cost_share'], '.2%')}")
        lines.append(f"  Slippage Share: {_fmt(t['slippage_share'], '.2%')}")
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