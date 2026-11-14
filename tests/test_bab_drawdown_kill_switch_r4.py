"""Tests for R4-B: drawdown-limit kill switch."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.risk import (
    KillSwitchEvent,
    apply_kill_switch,
    compute_running_drawdown,
)
from strategies.betting_against_beta.strategy import BABStrategy

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")


def _make_breaching_returns():
    """Create a returns series that will breach a 20% drawdown limit."""
    # Create a cumulative path that drops 30% then recovers
    # Strategy returns: steady small gains with noise, then a big crash
    # Use smaller beta_window so betas are computed earlier
    rng = np.random.RandomState(42)
    dates = pd.date_range("2023-01-01", periods=200)
    base_btc = rng.normal(0.001, 0.0005, 200)
    base_eth = rng.normal(0.0015, 0.0005, 200)
    base_sol = rng.normal(0.002, 0.0005, 200)
    # Add crash on day 100 (after beta window of 60)
    base_btc[100] = -0.40
    base_eth[100] = -0.35
    base_sol[100] = -0.30
    returns = pd.DataFrame(
        {
            "BTC": base_btc,
            "ETH": base_eth,
            "SOL": base_sol,
        },
        index=dates,
    )
    return returns


def _make_non_breaching_returns():
    """Create a returns series that will NOT breach a 20% drawdown limit."""
    rng = np.random.RandomState(42)
    dates = pd.date_range("2023-01-01", periods=100)
    returns = pd.DataFrame(
        {
            "BTC": rng.normal(0.001, 0.0005, 100),
            "ETH": rng.normal(0.0015, 0.0005, 100),
            "SOL": rng.normal(0.002, 0.0005, 100),
        },
        index=dates,
    )
    return returns


def test_kill_switch_breaching_fixture_triggers_once_and_flattens():
    """Breaching fixture triggers exactly once and flattens weights."""
    # Use real market prices which we know can trigger drawdown
    strat = BABStrategy(
        config=BABConfig(
            benchmark="BTC",
            max_drawdown_limit=0.10,  # 10% limit - should trigger on real data
        )
    )
    result = strat.run(returns_df=REAL_PRICES)

    # Check kill_switch event exists and is triggered
    assert result.kill_switch is not None
    assert result.kill_switch.triggered is True
    assert result.kill_switch.date is not None
    assert result.kill_switch.limit == 0.10
    assert result.kill_switch.observed_drawdown < -0.10  # More than 10% drawdown

    # Check weights are flattened from breach date onward
    breach_pos = result.weights.index.get_loc(result.kill_switch.date)
    post_breach_weights = result.weights.iloc[breach_pos:]
    assert (post_breach_weights.abs().sum(axis=1) < 1e-9).all(), (
        "Weights should be zero after breach"
    )

    # Check report includes kill_switch
    report = strat.report(result)
    assert "kill_switch" in report
    ks = report["kill_switch"]
    assert ks is not None
    assert ks["triggered"] is True
    assert ks["limit"] == 0.10
    assert math.isfinite(ks["observed_drawdown"])
    assert ks["date"] is not None


def test_kill_switch_non_breaching_fixture_does_not_trigger():
    """Non-breaching fixture does not trigger kill switch."""
    strat = BABStrategy(
        config=BABConfig(
            benchmark="BTC",
            max_drawdown_limit=0.20,
        )
    )
    returns = _make_non_breaching_returns()
    result = strat.run(returns_df=returns)

    assert result.kill_switch is not None
    assert result.kill_switch.triggered is False
    assert result.kill_switch.date is None
    assert result.kill_switch.limit == 0.20

    # Weights should not be flattened
    assert not (result.weights.abs().sum(axis=1) < 1e-9).all()

    # Report includes kill_switch with triggered=False
    report = strat.report(result)
    assert "kill_switch" in report
    ks = report["kill_switch"]
    assert ks["triggered"] is False
    assert ks["date"] is None


def test_kill_switch_none_limit_is_noop_and_matches_baseline():
    """None limit is a no-op and matches baseline behavior."""
    # Without kill switch
    strat_baseline = BABStrategy(config=BABConfig(benchmark="BTC"))
    returns = _make_breaching_returns()
    result_baseline = strat_baseline.run(returns_df=returns)

    # With kill switch set to None
    strat_none = BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit=None))
    result_none = strat_none.run(returns_df=returns)

    # Weights should be identical (byte-identical)
    pd.testing.assert_frame_equal(result_baseline.weights, result_none.weights)
    pd.testing.assert_frame_equal(result_baseline.backtest, result_none.backtest)

    # kill_switch event should be not triggered
    assert result_none.kill_switch is not None
    assert result_none.kill_switch.triggered is False
    assert result_none.kill_switch.limit is None

    # Report should have kill_switch with triggered=False
    report = strat_none.report(result_none)
    assert "kill_switch" in report
    assert report["kill_switch"]["triggered"] is False


def test_kill_switch_invalid_limit_raises():
    """Invalid limit raises BABConfigError."""
    # Limit <= 0
    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit=0.0))

    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit=-0.1))

    # Limit > 1
    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit=1.5))

    # Non-numeric
    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit="0.2"))


def test_kill_switch_event_json_safe():
    """Kill switch event is finite and JSON-safe."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit=0.20))
    returns = _make_breaching_returns()
    result = strat.run(returns_df=returns)

    # Event to_dict should be JSON-safe
    ks_dict = result.kill_switch.to_dict()
    assert isinstance(ks_dict["triggered"], bool)
    assert ks_dict["date"] is None or isinstance(ks_dict["date"], str)
    assert math.isfinite(ks_dict["observed_drawdown"])
    assert math.isfinite(ks_dict["limit"])

    # Should serialize without error
    json_str = json.dumps(ks_dict, allow_nan=False)
    assert isinstance(json_str, str)


def test_compute_running_drawdown_basic():
    """compute_running_drawdown works correctly."""
    # Simple cumulative path: 1.0 -> 1.1 -> 0.9 -> 1.05
    cumulative = pd.Series([1.0, 1.1, 0.9, 1.05], index=pd.date_range("2023-01-01", periods=4))
    dd = compute_running_drawdown(cumulative)

    # Running max: 1.0, 1.1, 1.1, 1.1
    # Drawdown: 0, 0, (0.9-1.1)/1.1 = -0.1818, (1.05-1.1)/1.1 = -0.0455
    assert len(dd) == 4
    assert dd.iloc[0] == 0.0  # First period: no drawdown
    assert dd.iloc[1] == 0.0  # New high
    assert dd.iloc[2] < -0.18 and dd.iloc[2] > -0.19  # ~18% drawdown
    assert dd.iloc[3] < 0.0 and dd.iloc[3] > -0.05  # Recovering

    # All values should be <= 0
    assert (dd <= 0).all()


def test_compute_running_drawdown_empty_handling():
    """compute_running_drawdown handles empty/None inputs gracefully."""
    # None input
    dd = compute_running_drawdown(None)
    assert isinstance(dd, pd.Series)
    assert len(dd) == 0

    # Empty series
    dd = compute_running_drawdown(pd.Series(dtype=float))
    assert isinstance(dd, pd.Series)
    assert len(dd) == 0

    # Non-finite values
    cumulative = pd.Series([1.0, np.inf, -np.inf, np.nan, 0.9])
    dd = compute_running_drawdown(cumulative)
    assert (dd <= 0).all()
    assert dd.notna().all()


def test_apply_kill_switch_none_limit_returns_unchanged():
    """apply_kill_switch with None limit returns weights unchanged."""
    weights = pd.DataFrame(
        {"A": [0.5, -0.5], "B": [-0.3, 0.3]}, index=pd.date_range("2023-01-01", periods=2)
    )
    cumulative = pd.Series([1.0, 0.95], index=weights.index)

    out_weights, event = apply_kill_switch(weights, cumulative, None)
    pd.testing.assert_frame_equal(out_weights, weights)
    assert event.triggered is False
    assert event.limit is None


def test_apply_kill_switch_empty_weights_returns_not_triggered():
    """apply_kill_switch with empty weights returns not-triggered event."""
    weights = pd.DataFrame()
    cumulative = pd.Series([1.0, 0.9, 0.8])

    _out_weights, event = apply_kill_switch(weights, cumulative, 0.20)
    assert event.triggered is False
    assert event.limit == 0.20


def test_kill_switch_with_real_fixture():
    """Kill switch works with real market prices fixture."""
    strat = BABStrategy(
        config=BABConfig(
            benchmark="BTC",
            max_drawdown_limit=0.15,  # 15% limit - should trigger on real data
        )
    )
    result = strat.run(returns_df=REAL_PRICES)

    # Should have a kill_switch event
    assert result.kill_switch is not None
    assert isinstance(result.kill_switch.limit, float)
    assert result.kill_switch.limit == 0.15

    # Report should include it
    report = strat.report(result)
    assert "kill_switch" in report
    assert report["kill_switch"]["limit"] == 0.15


def test_kill_switch_byte_identical_when_none():
    """Verify byte-identical behavior when max_drawdown_limit=None."""
    # This test ensures the default path is completely unchanged
    returns = _make_breaching_returns()

    # Run multiple times with None limit
    results = []
    for _ in range(3):
        strat = BABStrategy(config=BABConfig(benchmark="BTC", max_drawdown_limit=None))
        result = strat.run(returns_df=returns)
        results.append(result)

    # All should be identical
    for i in range(1, len(results)):
        pd.testing.assert_frame_equal(results[0].weights, results[i].weights)
        pd.testing.assert_frame_equal(results[0].backtest, results[i].backtest)
        assert results[0].kill_switch.triggered == results[i].kill_switch.triggered
        assert results[0].kill_switch.limit == results[i].kill_switch.limit
