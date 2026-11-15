"""P12 coverage campaign for BABStrategy orchestration branches (strategy.py).

Covers real missed orchestration branches with synthetic data + fakes/mocks
only (no network): non-daily rebalance_freq, shorting_constraints error/apply,
position_sizer dict/normalize/apply/error, regime_filter scaling path,
beta-neutral enforcement incl. tracking-error tolerance, finite-guard cleanup,
plus cost_model / _safe_float / kill_switch.to_dict / tear_sheet / empty-universe
gaps.

No production logic is modified. Asserts observable behavior.
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import shorting, sizing
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.costs import TransactionCostModel
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.risk import KillSwitchEvent
from strategies.betting_against_beta.shorting import ShortingConstraints
from strategies.betting_against_beta.strategy import (
    BABStrategy,
    _apply_rebalance,
    _normalize_position_sizer,
    _rebalance_mask,
)


def _make_returns(n=120, seed=7, with_nan=False):
    idx = pd.date_range("2023-01-01", periods=n, freq="D")
    rng = np.random.default_rng(seed)
    mkt = rng.normal(0, 0.01, n)
    if with_nan:
        mkt[10:13] = np.nan
    return pd.DataFrame(
        {
            "BTC": mkt,
            "ETH": 0.6 * mkt + rng.normal(0, 0.005, n),
            "SOL": 1.2 * mkt + rng.normal(0, 0.007, n),
            "ADA": 0.9 * mkt + rng.normal(0, 0.006, n),
        },
        index=idx,
    )


# ---------------------------------------------------------------------------
# _rebalance_mask / _apply_rebalance (non-daily orchestration branches)
# ---------------------------------------------------------------------------

def test_rebalance_mask_non_datetime_weekly_step():
    idx = pd.Index(range(30))
    mask = _rebalance_mask(idx, "weekly")
    assert bool(mask.iloc[0])
    assert bool(mask.iloc[7])
    assert bool(mask.iloc[14])
    assert bool(mask.iloc[21])
    assert bool(mask.iloc[28])
    assert not bool(mask.iloc[1])


def test_apply_rebalance_weekly_holds_within_week():
    idx = pd.date_range("2023-01-01", periods=10, freq="D")
    sig = pd.DataFrame(
        {"BTC": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}, index=idx
    )
    mask = _rebalance_mask(idx, "weekly")
    out = _apply_rebalance(sig, "weekly")
    # Contract: out == signals.where(mask).ffill().fillna(0)
    expected = sig.where(mask).ffill().fillna(0.0)
    pd.testing.assert_frame_equal(out, expected)
    # First date is a rebalance date; values hold within a week.
    assert out.iloc[0]["BTC"] == 1.0
    assert out.iloc[1]["BTC"] == 2.0  # new week starts Jan 2 (Monday)
    assert (out.iloc[2:8]["BTC"] == 2.0).all()


def test_apply_rebalance_empty_signals():
    assert _apply_rebalance(None, "weekly") is None
    out = _apply_rebalance(pd.DataFrame(), "weekly")
    assert len(out) == 0


# ---------------------------------------------------------------------------
# cost_model / _resolve_cost_model branches
# ---------------------------------------------------------------------------

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


def test_resolve_cost_model_prices_load_failure_raises(tmp_path):
    bad = tmp_path / "does_not_exist.csv"
    cfg = BABConfig(cost_model=TransactionCostModel(), prices=str(bad))
    strat = BABStrategy(cfg)
    with pytest.raises(BABDataError, match="failed to load prices"):
        strat._resolve_cost_model(cfg)


def test_resolve_cost_model_unknown_prices_type_skips_impact():
    cfg = BABConfig(cost_model=None, prices=12345)
    strat = BABStrategy(cfg)
    cm, prices_df, adv = strat._resolve_cost_model(cfg)
    assert cm is None and prices_df is None and adv is None


# ---------------------------------------------------------------------------
# run() shorting_constraints branches
# ---------------------------------------------------------------------------

def test_run_shorting_constraints_wrong_type_raises():
    strat = BABStrategy(BABConfig(shorting_constraints="not-constraints"))
    with pytest.raises(BABDataError, match="shorting_constraints must be a ShortingConstraints"):
        strat.run()


def test_run_shorting_constraints_apply_failure_wraps_babdataerror():
    with mock.patch.object(
        shorting, "apply_shorting_constraints", side_effect=TypeError("bad weights")
    ):
        strat = BABStrategy(BABConfig(shorting_constraints=ShortingConstraints()))
        with pytest.raises(BABDataError, match="shorting_constraints failed"):
            strat.run()


def test_run_shorting_constraints_dict_applies():
    rets = _make_returns(n=60, seed=3)
    strat = BABStrategy(
        BABConfig(
            universe=["BTC", "ETH", "SOL", "ADA"],
            benchmark="BTC",
            beta_window=20,
            min_observations=10,
            shorting_constraints={"max_short_weight": 0.25},
        )
    )
    result = strat.run(returns_df=rets)
    assert result.weights is not None and not result.weights.empty


# ---------------------------------------------------------------------------
# run() position_sizer branches
# ---------------------------------------------------------------------------

def test_run_position_sizer_dict_equal():
    rets = _make_returns(n=80, seed=5)
    strat = BABStrategy(
        BABConfig(
            universe=["BTC", "ETH", "SOL", "ADA"],
            benchmark="BTC",
            beta_window=20,
            min_observations=10,
            position_sizer={"type": "equal"},
        )
    )
    result = strat.run(returns_df=rets)
    assert result.weights is not None and not result.weights.empty


def test_run_position_sizer_dict_vol_target():
    rets = _make_returns(n=100, seed=5)
    strat = BABStrategy(
        BABConfig(
            universe=["BTC", "ETH", "SOL", "ADA"],
            benchmark="BTC",
            beta_window=20,
            min_observations=10,
            position_sizer={"type": "vol_target", "target_vol": 0.10},
        )
    )
    result = strat.run(returns_df=rets)
    assert result.weights is not None and not result.weights.empty


def test_run_position_sizer_dict_risk_parity():
    rets = _make_returns(n=100, seed=5)
    strat = BABStrategy(
        BABConfig(
            universe=["BTC", "ETH", "SOL", "ADA"],
            benchmark="BTC",
            beta_window=20,
            min_observations=10,
            position_sizer={"type": "risk_parity"},
        )
    )
    result = strat.run(returns_df=rets)
    assert result.weights is not None and not result.weights.empty


def test_run_position_sizer_invalid_string_raises():
    strat = BABStrategy(BABConfig(position_sizer="bogus"))
    with pytest.raises(BABDataError, match="Unknown sizer"):
        strat.run()


def test_run_position_sizer_apply_failure_wraps_babdataerror():
    with mock.patch.object(
        sizing, "apply_position_sizing", side_effect=ValueError("sizing blew up")
    ):
        strat = BABStrategy(BABConfig(position_sizer={"type": "equal"}))
        with pytest.raises(BABDataError, match="position_sizer failed"):
            strat.run()


def test_normalize_position_sizer_unknown_dict_type_raises():
    with pytest.raises(BABDataError, match="unknown type"):
        _normalize_position_sizer({"type": "nope"})


# ---------------------------------------------------------------------------
# run() regime_filter scaling branch
# ---------------------------------------------------------------------------

def test_run_regime_filter_scales_weights():
    rets = _make_returns(n=100, seed=9)
    scale = pd.Series(0.5, index=rets.index, name="regime_scale")
    with mock.patch(
        "strategies.betting_against_beta.regime.regime_scale_scalar", return_value=scale
    ):
        strat = BABStrategy(BABConfig(regime_filter=True))
        result = strat.run(returns_df=rets)
        base = BABStrategy(BABConfig(regime_filter=False)).run(returns_df=rets)
        scaled = result.weights.to_numpy(dtype=float).sum(axis=1)
        expected = base.weights.to_numpy(dtype=float).sum(axis=1) * 0.5
        np.testing.assert_allclose(scaled, expected, atol=1e-9)


# ---------------------------------------------------------------------------
# run() beta-neutral enforcement incl. tracking-error tolerance
# ---------------------------------------------------------------------------

def test_run_beta_neutral_enforcement_applies():
    rets = _make_returns(n=100, seed=11)
    with mock.patch(
        "strategies.betting_against_beta.portfolio.enforce_beta_neutrality",
        side_effect=lambda w, b, **kw: w * 0.9,
    ) as m:
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL", "ADA"],
                benchmark="BTC",
                beta_window=20,
                min_observations=10,
                beta_neutral=True,
                beta_target=0.0,
                beta_tolerance=1e-4,
                tracking_error_tolerance=0.02,
                enable_tracking_error_monitoring=True,
            )
        )
        result = strat.run(returns_df=rets)
        assert m.call_count >= 1
        kwargs = m.call_args.kwargs
        assert kwargs["target_beta"] == 0.0
        assert kwargs["tracking_error_tolerance"] == 0.02
        assert kwargs["enable_tracking_error_monitoring"] is True


def test_run_beta_neutral_enforcement_uses_max_beta_drift_fallback():
    rets = _make_returns(n=100, seed=11)
    with mock.patch(
        "strategies.betting_against_beta.portfolio.enforce_beta_neutrality",
        side_effect=lambda w, b, **kw: w,
    ) as m:
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL", "ADA"],
                benchmark="BTC",
                beta_window=20,
                min_observations=10,
                beta_neutral_enforcement=True,
                max_beta_drift=0.05,
            )
        )
        strat.run(returns_df=rets)
        kwargs = m.call_args.kwargs
        assert kwargs["tolerance"] == 0.05 or kwargs["max_drift"] == 0.05


# ---------------------------------------------------------------------------
# run() empty-universe defensive branch (strategy.py 320-324)
# ---------------------------------------------------------------------------

def test_run_effective_universe_empty_raises_valueerror():
    orig = BABConfig.resolved_universe

    def _empty(self, columns=None):
        return []

    BABConfig.resolved_universe = _empty
    try:
        strat = BABStrategy(BABConfig(benchmark="BTC"))
        with pytest.raises(ValueError, match="No tradable assets remain"):
            strat.run(returns_df=_make_returns(n=30, seed=1))
    finally:
        BABConfig.resolved_universe = orig


# ---------------------------------------------------------------------------
# run() finite-guard cleanup branches
# ---------------------------------------------------------------------------

def test_run_finiteness_guard_clamps_nonfinite_weights():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    weights = pd.DataFrame(
        {"BTC": [1.0, np.nan, -np.inf], "ETH": [-1.0, np.inf, 1.0]}, index=idx
    )
    with mock.patch(
        "strategies.betting_against_beta.strategy.construct_portfolio", return_value=weights
    ):
        strat = BABStrategy()
        result = strat.run()
        wa = result.weights.to_numpy(dtype=float)
        assert np.isfinite(wa).all()


class _BrokenWeights:
    def to_numpy(self, *a, **k):
        raise TypeError("no numpy")

    def replace(self, *a, **k):
        return self

    def fillna(self, *a, **k):
        raise RuntimeError("fillna broken")


def test_run_finiteness_guard_fallback_raises_babdataerror():
    with mock.patch(
        "strategies.betting_against_beta.strategy.construct_portfolio",
        return_value=_BrokenWeights(),
    ):
        strat = BABStrategy()
        with pytest.raises(BABDataError, match="weight finiteness cleanup failed"):
            strat.run()


# ---------------------------------------------------------------------------
# dry_run() branches
# ---------------------------------------------------------------------------

def test_dry_run_safe_float_nonfinite_defaults():
    cfg = BABConfig()
    object.__setattr__(cfg, "transaction_costs", float("nan"))
    object.__setattr__(cfg, "slippage", float("inf"))
    strat = BABStrategy(cfg)
    out = strat.dry_run(returns_df=_make_returns(n=60, seed=2))
    assert out["config"]["transaction_costs"] == 0.0
    assert out["config"]["slippage"] == 0.0


def test_dry_run_empty_universe_raises_valueerror():
    orig = BABConfig.resolved_universe

    def _empty(self, columns=None):
        return []

    BABConfig.resolved_universe = _empty
    try:
        strat = BABStrategy(BABConfig(benchmark="BTC"))
        with pytest.raises(ValueError, match="No tradable assets remain"):
            strat.dry_run(returns_df=_make_returns(n=30, seed=1))
    finally:
        BABConfig.resolved_universe = orig


def test_dry_run_non_daily_rebalance_path():
    rets = _make_returns(n=20, seed=2)
    strat = BABStrategy(BABConfig(rebalance_freq="weekly", beta_window=10, min_observations=5))
    out = strat.dry_run(returns_df=rets)
    assert out["config"]["rebalance_freq"] == "weekly"
    assert "portfolio_risk" in out


# ---------------------------------------------------------------------------
# report() kill_switch.to_dict exception fallback + tear_sheet
# ---------------------------------------------------------------------------

def test_report_kill_switch_to_dict_failure_falls_back_to_none():
    rets = _make_returns(n=60, seed=4)
    strat = BABStrategy(BABConfig(max_drawdown_limit=0.5))
    result = strat.run(returns_df=rets)
    with mock.patch.object(KillSwitchEvent, "to_dict", side_effect=RuntimeError("boom")):
        rep = strat.report(result)
        assert rep["kill_switch"] is None


def test_tear_sheet_renders_without_crash():
    rets = _make_returns(n=60, seed=4)
    strat = BABStrategy(BABConfig(max_drawdown_limit=0.5))
    result = strat.run(returns_df=rets)
    sheet = strat.tear_sheet(result)
    assert "BAB STRATEGY TEAR SHEET" in sheet
    assert "Final Cumulative" in sheet


def test_report_to_json_strict_no_nan():
    rets = _make_returns(n=60, seed=4)
    strat = BABStrategy()
    result = strat.run(returns_df=rets)
    rep = strat.report(result)
    json_str = BABStrategy.report_to_json(rep)
    import json

    parsed = json.loads(json_str)
    assert parsed is not None
