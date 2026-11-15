"""P11 coverage campaign for reconciliation.py real error/unhappy branches.

Deterministic, no network. Targets missed _sanitize/_fill_executed_weight/
_fill_cost branches and reconcile_costs/reconcile_fills_to_backtest edge paths.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from strategies.betting_against_beta.reconciliation import (
    ReconciliationResult,
    _checksum,
    _date_key,
    _fill_cost,
    _fill_executed_weight,
    _sanitize,
    reconcile_costs,
    reconcile_fills_to_backtest,
)


def test_sanitize_primitives_and_containers():
    assert _sanitize(None) is None
    assert _sanitize(True) is True
    assert _sanitize(False) is False
    assert _sanitize(3) == 3
    assert _sanitize(1.5) == 1.5
    assert _sanitize(float("inf")) == 0.0
    assert _sanitize(float("nan")) == 0.0
    assert _sanitize("x") == "x"
    assert _sanitize([1, 2.0, "a"]) == [1, 2.0, "a"]
    assert _sanitize((1, 2)) == [1, 2]
    assert _sanitize({"k": 1, 2: [3]}) == {"k": 1, "2": [3]}
    ts = pd.Timestamp("2024-01-01T00:00:00Z")
    assert _sanitize(ts) == ts.isoformat()
    assert _sanitize(pd.Series([1, 2])) == [1, 2]
    assert _sanitize(np.array([1, 2])) == [1, 2]
    assert _sanitize(np.int64(7)) == 7
    assert _sanitize(np.float64(2.5)) == 2.5
    assert _sanitize(np.float64(np.inf)) == 0.0
    assert _sanitize(np.bool_(True)) is True

    class X:
        def __str__(self):
            return "X()"

    assert _sanitize(X()) == "X()"


def test_fill_executed_weight_status_and_fields():
    assert _fill_executed_weight({"status": "rejected", "order_weight": 1.0}) == 0.0
    assert _fill_executed_weight({"status": "cancelled", "filled_weight": 1.0}) == 0.0
    assert _fill_executed_weight({"status": "canceled", "filled_weight": 1.0}) == 0.0
    assert _fill_executed_weight({"status": "unfilled", "filled_weight": 1.0}) == 0.0
    assert _fill_executed_weight({"status": "failed", "filled_weight": 1.0}) == 0.0
    assert _fill_executed_weight({"filled_weight": 0.25, "order_weight": 1.0}) == 0.25
    assert _fill_executed_weight({"fill_ratio": 0.5, "requested_weight": 0.8}) == 0.4
    assert _fill_executed_weight({"fill_ratio": 0.5, "order_weight": 0.8}) == 0.4
    # bad fill_ratio falls through to order_weight
    assert _fill_executed_weight({"fill_ratio": "bad", "order_weight": 0.8}) == 0.8
    assert _fill_executed_weight({"order_weight": 0.3}) == 0.3
    assert _fill_executed_weight({}) == 0.0
    # bad value paths
    assert _fill_executed_weight({"filled_weight": "bad", "order_weight": 0.2}) == 0.2
    assert _fill_executed_weight({"filled_weight": float("inf"), "order_weight": 0.2}) == 0.2


def test_fill_cost_uses_executed_weight_and_overrides():
    fill = {"filled_weight": 0.5, "transaction_costs": 0.01, "slippage": 0.002}
    assert math.isclose(_fill_cost(fill, 0.0, 0.0), 0.006)
    fill2 = {"order_weight": -0.2}
    assert math.isclose(_fill_cost(fill2, 0.001, 0.001), 0.0004)
    fill3 = {"filled_weight": 0.0}
    assert _fill_cost(fill3, 0.01, 0.01) == 0.0


def test_date_key_fallback():
    class Bad:
        def __str__(self):
            return "BAD"

    assert _date_key("2024-01-01") == pd.Timestamp("2024-01-01").isoformat()
    # unparseable path returns str
    assert _date_key(Bad()) == "BAD"


def test_reconcile_costs_empty_weights():
    res = reconcile_costs(pd.DataFrame())
    assert isinstance(res, ReconciliationResult)
    assert res.n_periods == 0
    assert res.aggregate["n_mismatches"] == 0
    d = res.to_dict()
    assert d["checksum"] == res.checksum
    assert _checksum(d) == res.checksum


def test_reconcile_costs_with_executed_fills_and_mismatches():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])
    weights = pd.DataFrame({"A": [0.1, 0.2], "B": [-0.1, -0.2]}, index=idx)
    fills = [
        {"date": "2024-01-01T00:00:00", "asset": "A", "order_weight": 0.1},
        {"date": "2024-01-02T00:00:00", "asset": "A", "filled_weight": 0.05, "order_weight": 0.1},
    ]
    res = reconcile_costs(
        weights,
        executed_fills=fills,
        transaction_costs=0.001,
        slippage=0.001,
    )
    assert res.n_periods == 2
    assert res.aggregate["n_periods"] == 2
    assert "delta_max_abs" in res.aggregate
    assert res.aggregate["executed_total"] >= 0.0
    assert len(res.per_period) == 2
    assert all("date" in p for p in res.per_period)


def test_reconcile_fills_to_backtest_empty_weights():
    res = reconcile_fills_to_backtest(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert res.n_periods == 0
    assert res.aggregate["model_final_equity"] == 1.0
    assert res.aggregate["realized_final_equity"] == 1.0
    assert _checksum(res.to_dict()) == res.checksum


def test_reconcile_fills_to_backtest_partial_and_rejected_fills():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    weights = pd.DataFrame({"A": [0.5, 0.5, 0.2], "B": [-0.5, -0.5, -0.2]}, index=idx)
    returns = pd.DataFrame({"A": [0.01, -0.02, 0.01], "B": [0.0, 0.01, -0.01]}, index=idx)
    # model backtest cumulative roughly from target-weight replay
    backtest = pd.DataFrame({"cumulative": [1.0, 0.99, 1.005]}, index=idx)
    fills = [
        {"date": "2024-01-01T00:00:00", "asset": "A", "order_weight": 0.5, "filled_weight": 0.25},
        {"date": "2024-01-01T00:00:00", "asset": "B", "order_weight": -0.5, "status": "rejected"},
        {"date": "2024-01-02T00:00:00", "asset": "A", "order_weight": 0.0},
        {
            "date": "2024-01-03T00:00:00",
            "asset": "A",
            "order_weight": -0.3,
            "fill_ratio": 0.5,
            "requested_weight": -0.3,
        },
        {
            "date": "2024-01-03T00:00:00",
            "asset": "Z",
            "order_weight": 1.0,
            "filled_weight": 1.0,
        },  # unknown asset ignored
        {
            "date": "2024-01-03T00:00:00",
            "asset": "B",
            "order_weight": "bad",
            "filled_weight": 0.1,
        },
    ]
    res = reconcile_fills_to_backtest(
        weights, returns, backtest, fills=fills, transaction_costs=0.001, slippage=0.0005
    )
    assert res.n_periods == 3
    assert len(res.per_period) == 3
    assert "delta_final" in res.aggregate
    assert res.aggregate["n_periods"] == 3
    assert math.isfinite(res.aggregate["realized_final_equity"])
    assert all(math.isfinite(p["delta"]) for p in res.per_period)


def test_reconcile_fills_no_overlap_columns():
    idx = pd.to_datetime(["2024-01-01"])
    weights = pd.DataFrame({"A": [0.1]}, index=idx)
    returns = pd.DataFrame({"B": [0.01]}, index=idx)
    backtest = pd.DataFrame({"cumulative": [1.0]}, index=idx)
    # cols are taken from weights; returns may lack them -> treated as 0 returns
    res = reconcile_fills_to_backtest(weights, returns, backtest, fills=[])
    assert res.n_periods == 1
    assert res.aggregate["n_periods"] == 1
    assert math.isfinite(res.aggregate["realized_final_equity"])


def test_reconcile_fills_nonfinite_returns_and_backtest_missing():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])
    weights = pd.DataFrame({"A": [0.5, 0.5]}, index=idx)
    returns = pd.DataFrame({"A": [float("nan"), float("inf")]}, index=idx)
    backtest = pd.DataFrame({"other": [1.0, 1.0]}, index=idx)
    res = reconcile_fills_to_backtest(weights, returns, backtest, fills=None)
    assert res.n_periods == 2
    assert res.aggregate["model_final_equity"] == 1.0
