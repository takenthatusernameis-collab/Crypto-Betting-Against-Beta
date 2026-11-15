"""P14-D: ops/safety coverage push (replay / portfolio / reconciliation / risk).

Targets the reachable lines still missed after P14-A..C, plus a few remaining
defensive-but-reachable lines in metrics/config/data_loader/data_sources. The
unreachable residue (e.g. portfolio 152-153/170-177/180, reconciliation
309/82-83, replay 172) is deliberately not chased: it is dead under every
documented input contract and the TOTAL floor governs.

Fakes/monkeypatches only — no network, no credentials, no live execution.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _drop_all_nan_columns,
)
from strategies.betting_against_beta.data_sources import (
    validate_freshness as validate_feed_freshness,
)
from strategies.betting_against_beta.execution import OrderBatch, OrderIntent
from strategies.betting_against_beta.metrics import portfolio_beta, turnover
from strategies.betting_against_beta.reconciliation import (
    _fill_executed_weight,
    _sanitize,
    reconcile_fills_to_backtest,
)
from strategies.betting_against_beta.replay import ReplayHarness
from strategies.betting_against_beta.risk import RiskLimits, RiskManager
from strategies.betting_against_beta.strategy import BABResult


def _result(weights: pd.DataFrame, returns: pd.DataFrame | None = None) -> BABResult:
    if returns is None:
        returns = pd.DataFrame(0.0, index=weights.index, columns=weights.columns)
    return BABResult(
        config=BABConfig(benchmark="BTC"),
        returns=returns,
        betas=None,
        signals=None,
        weights=weights,
        backtest=None,
    )


# ---------------------------------------------------------------------------
# risk.py: concentration HHI compute/breach, position-age zero pop,
# drawdown None/empty short-circuits, get_events(since) filter.
# ---------------------------------------------------------------------------
def _wide_limits(**over) -> RiskLimits:
    base = dict(
        max_gross_exposure=10.0,
        max_net_exposure=10.0,
        max_position_weight=10.0,
    )
    base.update(over)
    return RiskLimits(**base)


def test_risk_hhi_computed_no_breach():
    mgr = RiskManager(_wide_limits(max_concentration=0.9))
    current = pd.Series({"A": 0.5, "B": 0.5})
    res = mgr.pre_trade_check(OrderBatch(date="2024-01-01"), current)
    assert res.allowed
    assert res.rejected_intents == []


def test_risk_concentration_breach_rejects_portfolio():
    mgr = RiskManager(_wide_limits(max_concentration=0.3))
    current = pd.Series({"A": 0.5, "B": 0.5})
    res = mgr.pre_trade_check(OrderBatch(date="2024-01-01"), current)
    reasons = [r["reason"] for r in res.rejected_intents]
    assert any("Concentration" in r for r in reasons)


def test_risk_position_age_zero_weight_pops():
    mgr = RiskManager(_wide_limits(max_position_age_days=5))
    mgr._position_ages["A"] = 99
    mgr.pre_trade_check(
        OrderBatch(date="2024-01-01"), pd.Series({"A": 0.0}), date="2024-01-01"
    )
    assert "A" not in mgr._position_ages


def test_risk_drawdown_none_short_circuits():
    mgr = RiskManager(_wide_limits(max_drawdown=None))
    res = mgr.pre_trade_check(
        OrderBatch(date="2024-01-01"),
        pd.Series({"A": 0.1}),
        cumulative=pd.Series([1.0, 0.9]),
    )
    assert res.allowed


def test_risk_drawdown_empty_series_short_circuits():
    mgr = RiskManager(_wide_limits(max_drawdown=0.1))
    res = mgr.pre_trade_check(
        OrderBatch(date="2024-01-01"),
        pd.Series({"A": 0.1}),
        cumulative=pd.Series(dtype="float64"),
    )
    assert res.allowed


def test_risk_get_events_since_filter():
    mgr = RiskManager(RiskLimits(max_position_weight=0.0))
    intent = OrderIntent(
        date="2024-01-01", asset="A", target_weight=0.5, current_weight=0.0, order_weight=0.5
    )
    batch = OrderBatch(date="2024-01-01", intents=(intent,))
    mgr.pre_trade_check(batch, pd.Series(dtype="float64"))
    assert mgr.events
    assert len(mgr.get_events(since="2000-01-01T00:00:00+00:00")) == len(mgr.events)
    assert mgr.get_events(since="2999-01-01T00:00:00+00:00") == []


# ---------------------------------------------------------------------------
# reconciliation.py: numpy scalar sanitize (np.float32 is NOT a float subclass),
# fill_ratio with non-numeric requested_weight, overflow / inf-cost paths.
# ---------------------------------------------------------------------------
def test_sanitize_numpy_scalar_branches():
    assert _sanitize(np.float32(1.5)) == 1.5
    assert _sanitize(np.float32(float("inf"))) == 0.0
    assert _sanitize(np.int64(7)) == 7
    assert _sanitize(np.bool_(True)) is True


def test_fill_ratio_non_numeric_requested_weight_returns_zero():
    assert _fill_executed_weight(
        {"fill_ratio": 0.5, "requested_weight": "bad", "order_weight": 0.2}
    ) == 0.0


def test_reconcile_fills_period_return_overflow():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])
    weights = pd.DataFrame({"A": [1.0, 1.0], "B": [1.0, 1.0]}, index=idx)
    returns = pd.DataFrame({"A": [0.0, 1.7e308], "B": [0.0, 1.7e308]}, index=idx)
    res = reconcile_fills_to_backtest(weights, returns, pd.DataFrame(index=idx), fills=None)
    assert res.n_periods == 2
    assert all(np.isfinite(p["delta"]) for p in res.per_period)


def test_reconcile_fills_infinite_cost_zeroes_net_return():
    idx = pd.to_datetime(["2024-01-01"])
    weights = pd.DataFrame({"A": [1.0]}, index=idx)
    returns = pd.DataFrame({"A": [0.0]}, index=idx)
    fills = [{"date": "2024-01-01T00:00:00", "asset": "A", "order_weight": 2.0}]
    res = reconcile_fills_to_backtest(
        weights, returns, pd.DataFrame(index=idx), fills=fills, transaction_costs=1e308
    )
    assert res.n_periods == 1
    assert res.aggregate["realized_final_equity"] == 1.0


def test_reconcile_fills_equity_overflow_resets():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    weights = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    returns = pd.DataFrame({"A": [0.0, 1e307, 1e307]}, index=idx)
    res = reconcile_fills_to_backtest(weights, returns, pd.DataFrame(index=idx), fills=None)
    assert res.aggregate["realized_final_equity"] == 1.0


# ---------------------------------------------------------------------------
# replay.py: non-finite weights zeroed, equity overflow reset,
# _date_key fallback, _sanitize container/Timestamp/fallback branches.
# ---------------------------------------------------------------------------
def test_replay_nonfinite_weights_zeroed():
    idx = pd.date_range("2024-01-01", periods=2)
    weights = pd.DataFrame({"A": [np.nan, 0.5], "B": [np.inf, 0.5]}, index=idx)
    artifact = ReplayHarness(_result(weights)).replay()
    assert artifact["equity"][-1]["equity"] == 1.0


def test_replay_equity_overflow_resets():
    idx = pd.date_range("2024-01-01", periods=3)
    weights = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    returns = pd.DataFrame({"A": [0.0, 1e307, 1e307]}, index=idx)
    artifact = ReplayHarness(_result(weights, returns)).replay()
    assert artifact["equity"][-1]["equity"] == 1.0


def test_replay_date_key_fallback():
    assert ReplayHarness._date_key("not-a-date") == "not-a-date"


def test_replay_sanitize_branches():
    assert ReplayHarness._sanitize(None) is None
    ts = pd.Timestamp("2024-01-01T00:00:00Z")
    assert ReplayHarness._sanitize(ts) == ts.isoformat()
    assert ReplayHarness._sanitize(pd.Series([1, 2])) == [1, 2]
    assert ReplayHarness._sanitize(np.array([1, 2])) == [1, 2]

    class X:
        def __str__(self):
            return "X()"

    assert ReplayHarness._sanitize(X()) == "X()"


# ---------------------------------------------------------------------------
# metrics.py: turnover NaN mean, portfolio_beta empty/misaligned guards.
# ---------------------------------------------------------------------------
def test_metrics_turnover_single_row_returns_zero():
    assert turnover(pd.DataFrame({"A": [0.1]})) == 0.0


def test_metrics_portfolio_beta_empty_betas():
    assert np.isnan(portfolio_beta(pd.DataFrame({"A": [0.1]}), pd.DataFrame()))


def test_metrics_portfolio_beta_no_common_columns():
    weights = pd.DataFrame({"A": [0.1]})
    betas = pd.DataFrame({"B": [0.2]})
    assert np.isnan(portfolio_beta(weights, betas))


def test_metrics_portfolio_beta_no_common_index():
    weights = pd.DataFrame({"A": [0.1, 0.2]}, index=[1, 2])
    betas = pd.DataFrame({"A": [0.3, 0.4]}, index=[3, 4])
    assert np.isnan(portfolio_beta(weights, betas))


# ---------------------------------------------------------------------------
# config.py: max_participation non-numeric rejection.
# ---------------------------------------------------------------------------
def test_config_max_participation_non_numeric_raises():
    with pytest.raises(BABConfigError):
        BABConfig(max_participation="bad")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# data_loader.py: all-NaN object frame hits the slow-path raise.
# ---------------------------------------------------------------------------
def test_drop_all_nan_columns_object_frame_raises():
    df = pd.DataFrame({"a": [None, None], "b": [None, None]}, dtype=object)
    with pytest.raises(BABDataError):
        _drop_all_nan_columns(df)


# ---------------------------------------------------------------------------
# data_sources.py: reference_date=None uses now() (deterministic recent index).
# ---------------------------------------------------------------------------
def test_feed_validate_freshness_default_reference():
    idx = pd.date_range("2026-11-15", periods=3, freq="D")
    df = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    assert validate_feed_freshness(df, max_staleness_days=100000.0) is True
