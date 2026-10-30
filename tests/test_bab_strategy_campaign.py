"""Campaign tests for BABStrategy pipeline edge and guard paths."""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta import shorting
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.shorting import ShortingConstraints
from strategies.betting_against_beta.strategy import BABStrategy, _apply_rebalance, _rebalance_mask


def _make_returns(n=100, seed=11):
    idx = pd.date_range("2023-01-01", periods=n, freq="D")
    rng = np.random.default_rng(seed)
    mkt = rng.normal(0, 0.01, n)
    return pd.DataFrame(
        {"BTC": mkt, "ETH": 0.6 * mkt + rng.normal(0, 0.005, n),
         "SOL": 1.2 * mkt + rng.normal(0, 0.007, n)},
        index=idx,
    )


def test_rebalance_mask_empty_index():
    idx = pd.DatetimeIndex([])
    mask = _rebalance_mask(idx, "weekly")
    assert len(mask) == 0


def test_rebalance_mask_unknown_freq_daily_fallback():
    idx = pd.date_range("2023-01-01", periods=10, freq="D")
    mask = _rebalance_mask(idx, "yearly")
    assert bool(mask.all())


def test_rebalance_mask_non_datetime_weekly_step():
    idx = pd.Index(range(30))
    mask = _rebalance_mask(idx, "weekly")
    assert bool(mask.iloc[0])
    assert bool(mask.iloc[7])
    assert bool(mask.iloc[14])
    assert bool(mask.iloc[21])
    assert bool(mask.iloc[28])


def test_apply_rebalance_empty_signals():
    assert _apply_rebalance(None, "weekly") is None
    out = _apply_rebalance(pd.DataFrame(), "weekly")
    assert len(out) == 0


def test_apply_rebalance_daily_returns_as_is():
    df = pd.DataFrame({"BTC": [1.0, -1.0]}, index=pd.date_range("2023-01-01", periods=2))
    out = _apply_rebalance(df, "daily")
    pd.testing.assert_frame_equal(out, df)


def test_run_empty_universe_after_intersection_raises():
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=3))
    cfg = BABConfig(universe=["ZZZ"], benchmark="BTC", beta_window=5, min_observations=2,
                    synthetic_n_days=30, synthetic_seed=1)
    strat = BABStrategy(cfg)
    with pytest.raises(ValueError):
        strat.run(returns_df=df)


def test_run_shorting_constraints_error_propagates():
    with mock.patch.object(shorting, "apply_shorting_constraints",
                           side_effect=BABDataError("shorting failed")):
        strat = BABStrategy(BABConfig(shorting_constraints=ShortingConstraints()))
        with pytest.raises(BABDataError):
            strat.run()


def test_run_sizing_exception_swallowed():
    strat = BABStrategy(BABConfig(position_sizer="bogus"))
    result = strat.run()
    assert result is not None and result.backtest is not None


def test_run_regime_exception_swallowed():
    with mock.patch("strategies.betting_against_beta.regime.regime_scale_factors",
                    side_effect=RuntimeError("boom")):
        strat = BABStrategy(BABConfig(regime_filter=True))
        result = strat.run()
        assert result is not None


def test_run_finiteness_guard_clamp_nonfinite_weights():
    idx = pd.date_range("2023-01-01", periods=30, freq="D")
    weights = pd.DataFrame({"BTC": [1.0, np.nan, -1.0], "ETH": [-1.0, np.inf, 1.0]}, index=idx[:3])
    with mock.patch("strategies.betting_against_beta.strategy.construct_portfolio",
                    return_value=weights):
        strat = BABStrategy()
        result = strat.run()
        wa = result.weights.to_numpy(dtype=float)
        assert np.isfinite(wa).all()
