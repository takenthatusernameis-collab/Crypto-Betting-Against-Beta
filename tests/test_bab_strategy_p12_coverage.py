"""P12 coverage campaign for strategy.py orchestration branches (strategy.py).

Covers real missed orchestration branches with synthetic data + fakes/mocks only
(no network): non-daily rebalance_freq, shorting_constraints error/apply,
position_sizer dict/normalize/apply/error, regime_filter scaling path,
beta-neutral enforcement incl. tracking-error tolerance, finite-guard cleanup.

No production logic is modified. Assert observable behavior.
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.config import BABConfig, BABConfigError
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.risk import KillSwitchEvent
from strategies.betting_against_beta.strategy import _apply_rebalance


def _returns_df(n=120, seed=0):
    rng = np.random.default_rng(seed)
    bench = rng.normal(0, 0.01, n)
    assets = {f"ASSET_{i}": 0.5 * bench + rng.normal(0, 0.005, n) for i in range(4)}
    assets["BTC"] = bench
    return pd.DataFrame(assets, index=pd.date_range("2023-01-01", periods=n, freq="D"))


# ---------------------------------------------------------------------------
# _apply_rebalance non-daily path
# ---------------------------------------------------------------------------


def test_apply_rebalance_weekly():
    signals = pd.DataFrame(
        {"BTC": [0.5, 0.5, 0.5, 0.5, 0.5], "ETH": [-0.5, -0.5, -0.5, -0.5, -0.5]},
        index=pd.date_range("2023-01-01", periods=5, freq="D"),
    )
    out = _apply_rebalance(signals, "weekly")
    # Weekly rebalance should hold signals constant within each week
    assert (out.iloc[0] == out.iloc[-1]).all()
    assert out.shape == signals.shape


def test_apply_rebalance_monthly():
    signals = pd.DataFrame(
        {"BTC": [0.5] * 10, "ETH": [-0.5] * 10},
        index=pd.date_range("2023-01-01", periods=10, freq="D"),
    )
    out = _apply_rebalance(signals, "monthly")
    assert out.shape == signals.shape


def test_apply_rebalance_invalid_freq():
    signals = pd.DataFrame(
        {"BTC": [0.5] * 5, "ETH": [-0.5] * 5},
        index=pd.date_range("2023-01-01", periods=5, freq="D"),
    )
    # Invalid freq should be handled gracefully (falls through to daily)
    out = _apply_rebalance(signals, "invalid")
    assert out.shape == signals.shape


# ---------------------------------------------------------------------------
# _safe_float in report (lines 643, 646-647) - tested via report() method
# ---------------------------------------------------------------------------


def test_strategy_report_safe_float():
    cfg = BABConfig(benchmark="BTC", beta_window=10, long_quantile=0.3, short_quantile=0.3)
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    result = strat.run(rets)
    report = strat.report(result)
    assert "metrics" in report
    assert "config" in report
    # Verify no crash with non-finite values
    assert report["metrics"]["final_cumulative"] >= 0.0


def _cfg_with_cost_model(cm):
    cfg = BABConfig()
    object.__setattr__(cfg, "cost_model", cm)
    return cfg


def test_resolve_cost_model_invalid_dict_raises():
    strat = BABStrategy(_cfg_with_cost_model({"type": "bogus", "fee_bps": 1.0}))
    with pytest.raises(BABDataError, match="cost_model dict is invalid"):
        strat._resolve_cost_model(strat.config)


def test_resolve_cost_model_wrong_type_raises():
    strat = BABStrategy(_cfg_with_cost_model("not-a-model"))
    with pytest.raises(BABDataError, match="cost_model must be a TransactionCostModel"):
        strat._resolve_cost_model(strat.config)


# ---------------------------------------------------------------------------
# _safe_float / empty universe / non-daily rebalance in dry_run
# ---------------------------------------------------------------------------


def test_dry_run_safe_float_nonfinite_defaults():
    cfg = BABConfig()
    object.__setattr__(cfg, "transaction_costs", float("nan"))
    object.__setattr__(cfg, "slippage", float("inf"))
    out = BABStrategy(cfg).dry_run(returns_df=_returns_df(60, seed=2))
    assert out["config"]["transaction_costs"] == 0.0
    assert out["config"]["slippage"] == 0.0


def test_dry_run_safe_float_none_and_invalid_defaults():
    cfg = BABConfig()
    object.__setattr__(cfg, "transaction_costs", None)
    out = BABStrategy(cfg).dry_run(returns_df=_returns_df(30, seed=2))
    assert out["config"]["transaction_costs"] == 0.0

    cfg2 = BABConfig()
    object.__setattr__(cfg2, "transaction_costs", "not-a-number")
    out2 = BABStrategy(cfg2).dry_run(returns_df=_returns_df(30, seed=2))
    assert out2["config"]["transaction_costs"] == 0.0


def test_dry_run_empty_universe_raises_valueerror(monkeypatch):
    monkeypatch.setattr(BABConfig, "resolved_universe", lambda self, columns=None: [])
    strat = BABStrategy(BABConfig(benchmark="BTC"))
    with pytest.raises(ValueError, match="No tradable assets remain"):
        strat.dry_run(returns_df=_returns_df(30, seed=1))


def test_dry_run_non_daily_rebalance_path():
    strat = BABStrategy(
        BABConfig(rebalance_freq="weekly", beta_window=10, min_observations=5)
    )
    out = strat.dry_run(returns_df=_returns_df(30, seed=2))
    assert out["config"]["rebalance_freq"] == "weekly"
    assert "portfolio_risk" in out


# ---------------------------------------------------------------------------
# shorting_constraints error/apply paths (lines 712-721)
# ---------------------------------------------------------------------------


def test_strategy_shorting_constraints_invalid_type():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        shorting_constraints="not-a-dict-or-object",
    )
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    with pytest.raises(
        BABDataError, match="shorting_constraints must be a ShortingConstraints or dict"
    ):
        strat.dry_run(rets)


def test_strategy_shorting_constraints_valid_object():
    from strategies.betting_against_beta.shorting import ShortingConstraints

    sc = ShortingConstraints(max_short_weight=0.5, max_short_notional_per_asset=0.5)
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        shorting_constraints=sc,
    )
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    out = strat.dry_run(rets)
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


def test_strategy_shorting_constraints_exception_path():
    with pytest.raises(BABConfigError, match="shorting_constraints dict is invalid"):
        BABConfig(
            benchmark="BTC",
            beta_window=10,
            long_quantile=0.3,
            short_quantile=0.3,
            shorting_constraints={"invalid": "dict"},
        )


# ---------------------------------------------------------------------------
# position_sizer dict/normalize/apply/error paths (lines 727-742)
# ---------------------------------------------------------------------------


def test_strategy_position_sizer_dict_normalizes():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        position_sizer={"type": "vol_target", "target_vol": 0.15},
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(30, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


def test_strategy_position_sizer_string_shorthand():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        position_sizer="vol_target",
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(30, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


def test_strategy_position_sizer_invalid_type():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        position_sizer=123,  # Not a dict, string, or sizer
    )
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    with pytest.raises(BABDataError, match="position_sizer must be a sizer or string shorthand"):
        strat.dry_run(rets)


def test_strategy_position_sizer_exception_path():
    # Invalid dict that passes type check but fails at application
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        position_sizer={"type": "nonexistent_sizer"},
    )
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    with pytest.raises(BABDataError, match="position_sizer dict has unknown type"):
        strat.dry_run(rets)


def test_strategy_shorting_constraints_apply_failure_wraps_babdataerror():
    from strategies.betting_against_beta.shorting import ShortingConstraints

    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        shorting_constraints=ShortingConstraints(),
    )
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    with mock.patch(
        "strategies.betting_against_beta.strategy.shorting.apply_shorting_constraints",
        side_effect=TypeError("bad weights"),
    ):
        with pytest.raises(BABDataError, match="shorting_constraints failed"):
            strat.dry_run(rets)


def test_strategy_position_sizer_apply_failure_wraps_babdataerror():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        position_sizer={"type": "equal"},
    )
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    with mock.patch(
        "strategies.betting_against_beta.strategy.sizing.apply_position_sizing",
        side_effect=ValueError("sizing blew up"),
    ):
        with pytest.raises(BABDataError, match="position_sizer failed"):
            strat.dry_run(rets)


# ---------------------------------------------------------------------------
# regime_filter scaling path (lines 747-752)
# ---------------------------------------------------------------------------


def test_strategy_regime_filter_enabled():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        regime_filter=True,
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(60, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


# ---------------------------------------------------------------------------
# beta_neutral enforcement with tracking error tolerance (lines 759-784)
# ---------------------------------------------------------------------------


def test_strategy_beta_neutral_enabled():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        beta_neutral=True,
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(60, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


def test_strategy_beta_neutral_with_tolerance():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        beta_neutral=True,
        beta_tolerance=0.01,
        max_beta_drift=0.02,
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(60, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


def test_strategy_beta_neutral_tracking_error():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        beta_neutral=True,
        tracking_error_tolerance=0.05,
        enable_tracking_error_monitoring=True,
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(60, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


def test_strategy_beta_neutral_correction_false():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        beta_neutral=True,
        beta_neutral_correction=False,
    )
    strat = BABStrategy(cfg)
    out = strat.dry_run(_returns_df(60, seed=1))
    assert out["tradable_universe"]
    assert "portfolio_risk" in out


# ---------------------------------------------------------------------------
# finite-guard cleanup (lines 790-798)
# ---------------------------------------------------------------------------


def test_strategy_finite_guard_cleans_nonfinite_weights():
    cfg = BABConfig(benchmark="BTC", beta_window=10, long_quantile=0.3, short_quantile=0.3)
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)

    def _weights_with_nonfinite(signals, **_kwargs):
        return pd.DataFrame({"BTC": [np.inf] * len(signals)}, index=signals.index)

    from strategies.betting_against_beta import strategy as strategy_mod

    with mock.patch.object(
        strategy_mod, "construct_portfolio", side_effect=_weights_with_nonfinite
    ):
        out = strat.dry_run(rets)
    assert out["tradable_universe"]
    assert out["portfolio_risk"]["gross_exposure"]["max"] == 0.0


def test_strategy_finite_guard_exception_fallback():
    cfg = BABConfig(benchmark="BTC", beta_window=10, long_quantile=0.3, short_quantile=0.3)
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    from strategies.betting_against_beta import strategy as strategy_mod

    class _BadWeights:
        def __init__(self, df):
            self._df = df

        def to_numpy(self, *args, **kwargs):
            raise TypeError("no numpy")

        def replace(self, *args, **kwargs):
            return self._df.replace(*args, **kwargs)

        def __getattr__(self, name):
            return getattr(self._df, name)

    def _bad_weights(signals, **_kwargs):
        return _BadWeights(pd.DataFrame({"BTC": [0.5] * len(signals)}, index=signals.index))

    with mock.patch.object(strategy_mod, "construct_portfolio", side_effect=_bad_weights):
        out = strat.dry_run(rets)
    assert out["tradable_universe"]
    assert out["portfolio_risk"]["gross_exposure"]["max"] == 0.5


def test_strategy_finite_guard_cleanup_failure_raises():
    cfg = BABConfig(benchmark="BTC", beta_window=10, long_quantile=0.3, short_quantile=0.3)
    strat = BABStrategy(cfg)
    rets = _returns_df(30, seed=1)
    from strategies.betting_against_beta import strategy as strategy_mod

    class _BrokenWeights:
        def to_numpy(self, *args, **kwargs):
            raise TypeError("no numpy")

        def replace(self, *args, **kwargs):
            raise RuntimeError("replace broken")

    with mock.patch.object(strategy_mod, "construct_portfolio", return_value=_BrokenWeights()):
        with pytest.raises(BABDataError, match="weight finiteness cleanup failed"):
            strat.dry_run(rets)


# ---------------------------------------------------------------------------
# _load_returns unknown prices type (line 306) - actually in _resolve_cost_model
# ---------------------------------------------------------------------------


def test_resolve_cost_model_unknown_prices_type():
    from strategies.betting_against_beta.strategy import BABStrategy

    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        cost_model={"linear_fee": 0.001},
        prices=123,  # Unknown type
    )
    strat = BABStrategy(cfg)
    # Should not raise, just skip impact term
    _cm, prices_df, _adv = strat._resolve_cost_model(cfg)
    assert prices_df is None


def test_resolve_cost_model_string_path_error():
    cfg = BABConfig(
        benchmark="BTC",
        beta_window=10,
        long_quantile=0.3,
        short_quantile=0.3,
        cost_model={"linear_fee": 0.001},
        prices="/nonexistent/path.csv",
    )
    strat = BABStrategy(cfg)
    with pytest.raises(BABDataError, match="failed to load prices"):
        strat._resolve_cost_model(cfg)


# ---------------------------------------------------------------------------
# report() kill_switch.to_dict exception fallback (lines 982-983)
# ---------------------------------------------------------------------------


def test_report_kill_switch_to_dict_failure_falls_back_to_none():
    strat = BABStrategy(BABConfig(max_drawdown_limit=0.5))
    result = strat.run(_returns_df(60, seed=4))
    with mock.patch.object(KillSwitchEvent, "to_dict", side_effect=RuntimeError("boom")):
        rep = strat.report(result)
    assert rep["kill_switch"] is None
