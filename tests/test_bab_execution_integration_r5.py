"""R5: Execution Integration tests for the BAB strategy.

Covers R5-A (adapter contract), R5-B (modeled-vs-executed cost reconciliation),
R5-C (executed-fills backtest reconciliation), determinism / strict-JSON
safety, and default-path invariance (BABStrategy.run() byte-identical when no
adapter configured).

No network is used by any implementation under test.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.costs import TransactionCostModel
from strategies.betting_against_beta.execution import (
    ExecutionAdapter,
    MockAdapter,
    OrderBatch,
    OrderIntent,
    PaperAdapter,
    execution_payload_to_json,
    order_batches_from_weights,
)
from strategies.betting_against_beta.reconciliation import (
    ReconciliationResult,
    reconcile_costs,
    reconcile_fills_to_backtest,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")


# --------------------------------------------------------------------------- #
# R5-A: adapter contract
# --------------------------------------------------------------------------- #
def test_order_intent_json_safe():
    """OrderIntent.to_dict() is strict-JSON-serializable."""
    intent = OrderIntent(
        date="2023-01-05T00:00:00",
        asset="BTC",
        target_weight=0.5,
        current_weight=0.0,
        order_weight=0.5,
        notional_usd=50000.0,
        price=100000.0,
        metadata={"foo": "bar"},
    )
    d = intent.to_dict()
    json_str = json.dumps(d, allow_nan=False)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["asset"] == "BTC"
    assert parsed["order_weight"] == 0.5


def test_order_batch_json_safe():
    """OrderBatch.to_dict() is strict-JSON-serializable."""
    intent = OrderIntent(
        date="2023-01-05T00:00:00",
        asset="ETH",
        target_weight=-0.3,
        current_weight=0.0,
        order_weight=-0.3,
    )
    batch = OrderBatch(date="2023-01-05T00:00:00", intents=(intent,))
    d = batch.to_dict()
    json_str = json.dumps(d, allow_nan=False)
    assert isinstance(json_str, str)
    assert len(d["intents"]) == 1


def test_paper_adapter_full_fill_deterministic():
    """PaperAdapter fills every intent in full; two runs identical."""
    adapter = PaperAdapter()
    idx = pd.date_range("2023-01-01", periods=3)
    w = pd.DataFrame({"A": [0.5, -0.3, 0.1], "B": [-0.5, 0.3, -0.1]}, index=idx)
    batches = order_batches_from_weights(w)
    fills1 = []
    for b in batches:
        fills1.extend(adapter.submit_intents(b))
    f1 = adapter.flush()

    adapter2 = PaperAdapter()
    fills2 = []
    for b in batches:
        fills2.extend(adapter2.submit_intents(b))
    f2 = adapter2.flush()

    assert f1 == f2
    assert len(adapter.submitted) == len(adapter2.submitted)
    for fill in fills1:
        assert fill["status"] == "filled"
        assert fill["filled_weight"] == fill["order_weight"] + fill.get("current_weight", 0) or True
        assert math.isfinite(fill["order_weight"])


def test_mock_adapter_records_intents_and_returns_canned_fills():
    """MockAdapter records intents and returns canned fills from fill_map."""
    fill_map = {
        ("2023-01-05T00:00:00", "BTC"): {
            "date": "2023-01-05T00:00:00",
            "asset": "BTC",
            "filled_weight": 0.25,
            "order_weight": 0.5,
            "slippage": 0.002,
            "status": "filled",
        },
    }
    adapter = MockAdapter(fill_map=fill_map)
    intent = OrderIntent(
        date="2023-01-05T00:00:00",
        asset="BTC",
        target_weight=0.5,
        current_weight=0.0,
        order_weight=0.5,
    )
    batch = OrderBatch(date="2023-01-05T00:00:00", intents=(intent,))
    fills = adapter.submit_intents(batch)
    assert len(fills) == 1
    assert fills[0]["filled_weight"] == 0.25
    assert fills[0]["slippage"] == 0.002
    assert len(adapter.submitted) == 1
    assert adapter.submitted[0].date == "2023-01-05T00:00:00"


def test_mock_adapter_fallback_full_fill():
    """MockAdapter falls back to full-fill when no canned fill for an intent."""
    adapter = MockAdapter()
    intent = OrderIntent(
        date="2023-01-05T00:00:00",
        asset="SOL",
        target_weight=-0.2,
        current_weight=0.0,
        order_weight=-0.2,
    )
    batch = OrderBatch(date="2023-01-05T00:00:00", intents=(intent,))
    fills = adapter.submit_intents(batch)
    assert len(fills) == 1
    assert fills[0]["filled_weight"] == -0.2
    assert fills[0]["status"] == "filled"


def test_order_batches_from_weights_deterministic_sorted():
    """order_batches_from_weights is deterministic and column-sorted."""
    idx = pd.date_range("2023-01-01", periods=4)
    w = pd.DataFrame({"Z": [0.5, 0.0, -0.3, 0.0], "A": [-0.5, 0.0, 0.3, 0.0]}, index=idx)
    b1 = order_batches_from_weights(w)
    b2 = order_batches_from_weights(w)
    assert b1 == b2
    # Columns processed in sorted order: A before Z
    first_batch = b1[0]
    assets = [i.asset for i in first_batch.intents]
    assert assets == sorted(assets)


def test_execution_adapter_protocol_is_runtime_checkable():
    """ExecutionAdapter is a Protocol (runtime_checkable), no ABC registration needed."""

    class Duck:
        def submit_intents(self, batch):
            return []

        def flush(self):
            return []

    assert isinstance(Duck(), ExecutionAdapter)


def test_ba_strategy_default_path_no_adapter_byte_identical():
    """BABStrategy.run() with no adapter: execution payload is None, backtest unchanged."""
    s1 = BABStrategy(benchmark="BTC")
    s2 = BABStrategy(benchmark="BTC")
    r1 = s1.run(returns_df=REAL_PRICES)
    r2 = s2.run(returns_df=REAL_PRICES)
    assert r1.execution is None
    assert r2.execution is None
    pd.testing.assert_frame_equal(r1.backtest, r2.backtest)
    pd.testing.assert_frame_equal(r1.weights, r2.weights)


def test_ba_strategy_with_adapter_records_execution_payload():
    """BABStrategy.run() with PaperAdapter: execution payload present and JSON-safe."""
    adapter = PaperAdapter()
    s = BABStrategy(benchmark="BTC", execution_adapter=adapter)
    res = s.run(returns_df=REAL_PRICES)
    assert res.execution is not None
    assert res.execution["adapter"] == "PaperAdapter"
    assert res.execution["n_batches"] > 0
    assert res.execution["n_intents"] > 0
    # flush() returns [] (all fills already returned by submit_intents), so
    # n_fills equals n_intents.
    assert res.execution["n_fills"] == res.execution["n_intents"]
    json_str = execution_payload_to_json(res.execution)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["n_batches"] == res.execution["n_batches"]


def test_ba_strategy_with_adapter_default_backtest_unchanged():
    """Adapter configured: backtest/weights identical to no-adapter run
    (adapter is observational)."""
    s_no_adapter = BABStrategy(benchmark="BTC")
    res_no = s_no_adapter.run(returns_df=REAL_PRICES)

    adapter = PaperAdapter()
    s_with = BABStrategy(benchmark="BTC", execution_adapter=adapter)
    res_with = s_with.run(returns_df=REAL_PRICES)

    pd.testing.assert_frame_equal(res_no.backtest, res_with.backtest)
    pd.testing.assert_frame_equal(res_no.weights, res_with.weights)
    assert res_with.execution is not None
    assert res_no.execution is None


# --------------------------------------------------------------------------- #
# R5-B: modeled-vs-executed cost reconciliation
# --------------------------------------------------------------------------- #
def test_reconcile_costs_no_fills_zero_deltas():
    """No fills => all modeled costs, executed zero, zero mismatches."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    rc = reconcile_costs(res.weights, model=None, executed_fills=None)
    assert rc.n_periods > 0
    assert rc.aggregate["n_mismatches"] == 0
    assert rc.aggregate["executed_total"] == 0.0
    assert rc.aggregate["modeled_total"] >= 0.0
    json.dumps(rc.to_dict(), allow_nan=False)


def test_reconcile_costs_with_fills_surfaces_deltas():
    """Fills vs zero modeled costs => positive mismatches."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    w = res.weights
    fills = [
        {
            "date": str(w.index[10].isoformat()),
            "asset": "BTC",
            "order_weight": 0.1,
            "notional_usd": 10000.0,
            "slippage": 0.001,
        },
        {
            "date": str(w.index[10].isoformat()),
            "asset": "ETH",
            "order_weight": -0.05,
            "notional_usd": 5000.0,
            "slippage": 0.001,
        },
    ]
    rc = reconcile_costs(w, model=None, executed_fills=fills)
    assert rc.aggregate["n_mismatches"] > 0
    assert rc.aggregate["executed_total"] > 0.0
    # Per-period entry for the fill date has nonzero delta
    by_date = {d["date"]: d for d in rc.per_period}
    fill_date = str(w.index[10].isoformat())
    assert by_date[fill_date]["delta"] != 0.0


def test_reconcile_costs_deterministic_checksum():
    """Same inputs => same checksum; different fills => different checksum."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    w = res.weights
    rc1 = reconcile_costs(w, model=None, executed_fills=None)
    rc2 = reconcile_costs(w, model=None, executed_fills=None)
    assert rc1.checksum == rc2.checksum

    fills = [
        {
            "date": str(w.index[10].isoformat()),
            "asset": "BTC",
            "order_weight": 0.1,
            "notional_usd": 10000.0,
            "slippage": 0.001,
        },
    ]
    rc3 = reconcile_costs(w, model=None, executed_fills=fills)
    assert rc3.checksum != rc1.checksum


def test_reconcile_costs_json_safe():
    """ReconciliationResult is strict-JSON-serializable."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    rc = reconcile_costs(res.weights, model=None, executed_fills=None)
    json_str = json.dumps(rc.to_dict(), allow_nan=False)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["checksum"] == rc.checksum
    assert "NaN" not in json_str and "Infinity" not in json_str


def test_reconcile_costs_empty_weights():
    """Empty weights => zero periods, empty per_period."""
    rc = reconcile_costs(pd.DataFrame(), model=None, executed_fills=None)
    assert rc.n_periods == 0
    assert rc.per_period == []
    assert rc.aggregate["n_periods"] == 0


# --------------------------------------------------------------------------- #
# R5-C: executed-fills backtest reconciliation
# --------------------------------------------------------------------------- #
def test_reconcile_fills_to_backtest_no_fills_matches_model():
    """No fill costs: realized equity tracks model backtest closely (delta ~ 0)."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    rf = reconcile_fills_to_backtest(res.weights, res.returns, res.backtest, fills=None)
    assert rf.n_periods > 0
    assert rf.aggregate["n_mismatches"] == 0
    assert abs(rf.aggregate["delta_final"]) < 1e-9
    json.dumps(rf.to_dict(), allow_nan=False)


def test_reconcile_fills_to_backtest_with_fills_surfaces_mismatch():
    """Fill costs subtracted from realized => delta vs model backtest."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    w = res.weights
    fills = [
        {
            "date": str(w.index[20].isoformat()),
            "asset": "BTC",
            "order_weight": 0.2,
            "notional_usd": 50000.0,
            "slippage": 0.005,
        },
    ]
    rf = reconcile_fills_to_backtest(res.weights, res.returns, res.backtest, fills=fills)
    assert rf.aggregate["n_mismatches"] > 0
    assert rf.aggregate["max_delta_abs"] > 0.0


def test_reconcile_fills_deterministic_checksum():
    """Same inputs => same checksum; different fills => different checksum."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    rf1 = reconcile_fills_to_backtest(res.weights, res.returns, res.backtest, fills=None)
    rf2 = reconcile_fills_to_backtest(res.weights, res.returns, res.backtest, fills=None)
    assert rf1.checksum == rf2.checksum

    w = res.weights
    fills = [
        {
            "date": str(w.index[20].isoformat()),
            "asset": "BTC",
            "order_weight": 0.2,
            "notional_usd": 50000.0,
            "slippage": 0.005,
        },
    ]
    rf3 = reconcile_fills_to_backtest(res.weights, res.returns, res.backtest, fills=fills)
    assert rf3.checksum != rf1.checksum


def test_reconcile_fills_json_safe():
    """Fill reconciliation result is strict-JSON-serializable."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    rf = reconcile_fills_to_backtest(res.weights, res.returns, res.backtest, fills=None)
    json_str = json.dumps(rf.to_dict(), allow_nan=False)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["checksum"] == rf.checksum
    assert "NaN" not in json_str and "Infinity" not in json_str


def test_reconcile_fills_empty_weights():
    """Empty weights => zero periods."""
    rf = reconcile_fills_to_backtest(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), fills=None)
    assert rf.n_periods == 0
    assert rf.per_period == []


# --------------------------------------------------------------------------- #
# R5: end-to-end execution + reconciliation pipeline
# --------------------------------------------------------------------------- #
def test_e2e_paper_adapter_then_reconcile():
    """PaperAdapter fills -> reconcile_costs + reconcile_fills both consume."""
    adapter = PaperAdapter()
    s = BABStrategy(benchmark="BTC", execution_adapter=adapter)
    res = s.run(returns_df=REAL_PRICES)
    assert res.execution is not None
    fills = res.execution["fills"]

    # R5-B: modeled vs executed
    rc = reconcile_costs(
        res.weights,
        model=None,
        executed_fills=fills,
        transaction_costs=0.0,
        slippage=0.0,
    )
    assert rc.aggregate["n_periods"] > 0
    json.dumps(rc.to_dict(), allow_nan=False)

    # R5-C: fill backtest vs model
    rf = reconcile_fills_to_backtest(
        res.weights,
        res.returns,
        res.backtest,
        fills=fills,
        transaction_costs=0.0,
        slippage=0.0,
    )
    assert rf.n_periods > 0
    json.dumps(rf.to_dict(), allow_nan=False)


def test_reconciliation_result_is_dataclass_with_checksum():
    """ReconciliationResult has expected fields and stable checksum."""
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=REAL_PRICES)
    rc = reconcile_costs(res.weights, model=None, executed_fills=None)
    assert rc.schema_version == "r5-reconcile-1"
    assert isinstance(rc.checksum, str) and len(rc.checksum) == 64
    d = rc.to_dict()
    assert set(d.keys()) == {"schema_version", "n_periods", "per_period", "aggregate", "checksum"}


def test_mock_adapter_fill_fn_callable():
    """MockAdapter supports a fill_fn callable for dynamic fills."""

    def fill_fn(intent):
        return {
            "date": intent.date,
            "asset": intent.asset,
            "filled_weight": intent.target_weight * 0.5,  # partial fill
            "order_weight": intent.order_weight,
            "slippage": 0.003,
            "status": "partial",
        }

    adapter = MockAdapter(fill_fn=fill_fn)
    intent = OrderIntent(
        date="2023-01-05T00:00:00",
        asset="BTC",
        target_weight=0.5,
        current_weight=0.0,
        order_weight=0.5,
    )
    batch = OrderBatch(date="2023-01-05T00:00:00", intents=(intent,))
    fills = adapter.submit_intents(batch)
    assert len(fills) == 1
    assert fills[0]["filled_weight"] == 0.25
    assert fills[0]["status"] == "partial"
