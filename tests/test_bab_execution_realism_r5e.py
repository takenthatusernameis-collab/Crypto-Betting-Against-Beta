"""R5-E: execution-adapter realism + reconciliation hardening tests.

Consumes the already-shipped R3 cost-model knobs (``partial_fill``,
``max_participation``, ``adv_usd``, ``prices``, ``cost_model``) in the
execution-adapter and reconciliation layers.

Deterministic only: no network, no credentials, no live venue data. Hostile
regime builders are reused from ``tests/test_bab_stress_regimes.py`` and the
fixture-backed market frame from the R5 suite; nothing is duplicated here.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_returns
from strategies.betting_against_beta.execution import (
    MockAdapter,
    OrderBatch,
    OrderIntent,
    PaperAdapter,
    configure_paper_adapter,
    execution_payload_to_json,
    order_batches_from_weights,
)
from strategies.betting_against_beta.reconciliation import (
    _fill_cost,
    _fill_executed_weight,
    reconcile_costs,
    reconcile_fills_to_backtest,
)
from tests.test_bab_stress_regimes import (
    BACKTEST_COLUMNS,
    DN_TOL,
    REGIME_BUILDERS,
    REGIMES,
    _base_frame,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")

REGIME_NAMES = [name for name, _ in REGIMES]
REQUIRED_FILL_FIELDS = (
    "date",
    "asset",
    "requested_weight",
    "filled_weight",
    "fill_ratio",
    "order_weight",
    "notional_usd",
    "price",
    "slippage",
    "status",
)


def _prices_from_returns(returns: pd.DataFrame) -> pd.DataFrame:
    """Cumulative price path from a returns frame (deterministic, positive)."""
    return (1.0 + returns.fillna(0.0)).cumprod()


def _adv(cols, value: float = 1_000_000.0) -> dict:
    """ADV for every traded asset, including the benchmark (BTC can be shorted)."""
    return dict.fromkeys(cols, value)


def _realism_adapter(
    returns: pd.DataFrame,
    max_participation: float = 0.01,
    adv_value: float = 5_000.0,
) -> PaperAdapter:
    """PaperAdapter configured with tight ADV so participation binds."""
    cols = list(returns.columns)
    adapter = PaperAdapter()
    adapter.prices = _prices_from_returns(returns)
    adapter.adv_usd = _adv(cols, adv_value)
    adapter.partial_fill = True
    adapter.max_participation = max_participation
    return adapter


def _frame_from_real() -> pd.DataFrame:
    """Real market fixture -> validated returns frame (loader converts prices)."""
    return load_returns(REAL_PRICES, benchmark="BTC", min_rows=1)


# --------------------------------------------------------------------------- #
# Fill-record contract
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("regime_name", REGIME_NAMES)
def test_paper_adapter_partial_fill_and_slippage_under_tight_adv(regime_name):
    """Tight ADV forces partial fills with slippage and explicit reasons."""
    frame = REGIME_BUILDERS[regime_name](_base_frame())
    prices = _prices_from_returns(frame)
    # Weights are fractions of a $1 book, so ADV must be tiny to bind.
    adv = _adv(frame.columns, 1.0)
    cap = 0.01
    adapter = PaperAdapter()
    adapter.prices = prices
    adapter.adv_usd = adv
    adapter.partial_fill = True
    adapter.max_participation = cap

    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=frame)
    # Use the run's own weights so intents are realistic.
    batches = order_batches_from_weights(
        res.weights, prices_df=prices, adv_usd=adv, max_participation=cap
    )
    fills = [f for b in batches for f in adapter.submit_intents(b)]

    assert fills, f"{regime_name}: no fills produced"
    for fill in fills:
        for field in REQUIRED_FILL_FIELDS:
            assert field in fill, f"{regime_name}: fill missing {field}"
        assert math.isfinite(fill["filled_weight"])
        assert math.isfinite(fill["slippage"]) and fill["slippage"] >= 0.0
        assert fill["status"] in {"filled", "partial"}
        assert 0.0 < fill["fill_ratio"] <= 1.0 + 1e-12
        assert fill["adv_usd"] is not None and fill["adv_usd"] > 0

    partials = [f for f in fills if f["status"] == "partial"]
    assert partials, f"{regime_name}: expected partial fills under tight ADV"
    for fill in partials:
        assert fill["reason"] == "participation_cap"
        assert fill["fill_ratio"] < 1.0 - 1e-12
        assert abs(fill["filled_weight"]) <= abs(fill["order_weight"]) + 1e-12
        # Realized participation never exceeds the cap.
        assert fill["participation"] * fill["fill_ratio"] <= cap + 1e-12

    json.dumps(fills, allow_nan=False)


def test_participation_cap_limits_fill_ratio_monotonically():
    """A larger order against fixed ADV yields a smaller fill ratio."""
    dates = pd.date_range("2024-01-01", periods=2)
    prices = pd.DataFrame({"BTC": [100.0, 100.0], "ETH": [10.0, 10.0]}, index=dates)
    adv = {"BTC": 1_000.0, "ETH": 1_000.0}

    def fill_for(order_weight: float) -> dict:
        adapter = PaperAdapter()
        adapter.prices = prices
        adapter.adv_usd = adv
        adapter.partial_fill = True
        adapter.max_participation = 0.10
        intent = OrderIntent(
            date=dates[0].isoformat(),
            asset="BTC",
            target_weight=order_weight,
            current_weight=0.0,
            order_weight=order_weight,
        )
        batch = OrderBatch(date=dates[0].isoformat(), intents=(intent,))
        return adapter.submit_intents(batch)[0]

    # ADV 1000 / price 100 => 10 units of ADV budget; weight is notional/ADV.
    small = fill_for(0.01)  # notional 1.0 -> participation 0.001
    large = fill_for(1.0)  # notional 100.0 -> participation 0.10 (== cap, fills)
    huge = fill_for(5.0)  # notional 500.0 -> participation 0.5 (cap binds)
    assert small["status"] == "filled"
    assert huge["status"] == "partial"
    assert huge["fill_ratio"] < 1.0
    # Realized participation never exceeds the cap.
    assert huge["participation"] * huge["fill_ratio"] <= 0.10 + 1e-12
    assert huge["filled_weight"] == pytest.approx(
        huge["order_weight"] * (0.10 / huge["participation"])
    )
    assert large["fill_ratio"] == pytest.approx(1.0)


def test_default_adapter_path_is_full_fill_zero_slippage():
    """No prices/ADV/partial_fill => byte-identical full-fill behavior."""
    dates = pd.date_range("2024-01-01", periods=2)
    w = pd.DataFrame({"BTC": [0.5, -0.2], "ETH": [-0.5, 0.2]}, index=dates)
    batches = order_batches_from_weights(w)
    adapter = PaperAdapter()
    fills = [f for b in batches for f in adapter.submit_intents(b)]
    assert fills
    for fill in fills:
        assert fill["status"] == "filled"
        assert fill["fill_ratio"] == 1.0
        assert fill["slippage"] == 0.0
        assert abs(fill["filled_weight"]) == pytest.approx(abs(fill["order_weight"]))
        assert fill["reason"] is None


def test_adapter_determinism_and_strict_json():
    """Same inputs => identical fills; output is strict-JSON-safe."""
    dates = pd.date_range("2024-01-01", periods=3)
    w = pd.DataFrame({"Z": [0.4, 0.0, -0.1], "A": [-0.4, 0.0, 0.1]}, index=dates)
    prices = pd.DataFrame({"Z": [10.0, 11.0, 12.0], "A": [5.0, 5.5, 6.0]}, index=dates)
    adv = {"Z": 100.0, "A": 100.0}

    def run() -> list[dict]:
        adapter = PaperAdapter()
        adapter.prices = prices
        adapter.adv_usd = adv
        adapter.partial_fill = True
        adapter.max_participation = 0.05
        out: list[dict] = []
        for batch in order_batches_from_weights(w, prices, adv, 0.05):
            out.extend(adapter.submit_intents(batch))
        return out

    first, second = run(), run()
    assert first == second
    payload = {"fills": first}
    text = execution_payload_to_json(payload)
    assert "NaN" not in text and "Infinity" not in text
    assert json.loads(text)["fills"] == first


def test_mock_adapter_keeps_canned_and_default_behavior():
    """MockAdapter still honors fill_map and full-fill fallback (R5-A contract)."""
    dates = pd.date_range("2024-01-01", periods=1)
    intent = OrderIntent(
        date=dates[0].isoformat(),
        asset="BTC",
        target_weight=0.3,
        current_weight=0.0,
        order_weight=0.3,
    )
    batch = OrderBatch(date=dates[0].isoformat(), intents=(intent,))

    canned = MockAdapter(
        fill_map={
            (intent.date, "BTC"): {
                "date": intent.date,
                "asset": "BTC",
                "requested_weight": 0.3,
                "filled_weight": 0.1,
                "fill_ratio": 1.0 / 3.0,
                "order_weight": 0.3,
                "slippage": 0.002,
                "status": "partial",
                "reason": "canned",
            }
        }
    )
    fill = canned.submit_intents(batch)[0]
    assert fill["filled_weight"] == 0.1
    assert fill["slippage"] == 0.002

    fallback = MockAdapter().submit_intents(batch)[0]
    assert fallback["filled_weight"] == 0.3
    assert fallback["status"] == "filled"


def test_configure_paper_adapter_consumes_config_knobs():
    """R5-E wiring: adapter picks up prices/adv/partial_fill/max_participation."""
    frame = _frame_from_real()
    prices = _prices_from_returns(frame)
    adv = _adv(frame.columns)
    strat = BABStrategy(
        benchmark="BTC",
        cost_model={"impact_coefficient": 0.0005},
        prices=prices,
        adv_usd=adv,
        partial_fill=True,
        max_participation=0.05,
    )
    adapter = configure_paper_adapter(PaperAdapter(), strat)
    assert adapter.prices is not None
    assert adapter.adv_usd is not None
    assert adapter.partial_fill is True
    assert adapter.max_participation == pytest.approx(0.05)


def test_configure_paper_adapter_respects_explicit_adapter_values():
    """An explicit adapter participation cap wins over the config value."""
    strat = BABStrategy(benchmark="BTC", partial_fill=True, max_participation=0.2)
    adapter = PaperAdapter()
    adapter.partial_fill = True
    adapter.max_participation = 0.5
    configure_paper_adapter(adapter, strat)
    assert adapter.max_participation == pytest.approx(0.5)


# --------------------------------------------------------------------------- #
# Order-intent / batch plumbing
# --------------------------------------------------------------------------- #
def test_order_intent_carries_participation_inputs_to_adapter():
    """ADV/participation actually reaches the adapter via OrderIntent (no stub)."""
    dates = pd.date_range("2024-01-01", periods=2)
    w = pd.DataFrame({"BTC": [0.5, 0.5], "ETH": [-0.5, -0.5]}, index=dates)
    prices = pd.DataFrame({"BTC": [100.0, 100.0], "ETH": [10.0, 10.0]}, index=dates)
    adv = pd.DataFrame({"BTC": [1_000.0, 1_000.0], "ETH": [1_000.0, 1_000.0]}, index=dates)
    batches = order_batches_from_weights(w, prices, adv, 0.10)
    assert batches
    for batch in batches:
        for intent in batch.intents:
            assert intent.adv_usd == pytest.approx(1_000.0)
            assert intent.max_participation == pytest.approx(0.10)
            assert intent.notional_usd is not None and intent.notional_usd > 0
            assert intent.price is not None and intent.price > 0
            assert intent.requested_weight == pytest.approx(intent.order_weight)
            # Strict-JSON-safe intent payload.
            json.dumps(intent.to_dict(), allow_nan=False)


def test_order_batches_ignores_adv_when_absent_is_safe():
    """Absent ADV yields None participation inputs but still deterministic batches."""
    dates = pd.date_range("2024-01-01", periods=2)
    w = pd.DataFrame({"BTC": [0.5, -0.5]}, index=dates)
    b1 = order_batches_from_weights(w)
    b2 = order_batches_from_weights(w)
    assert b1 == b2
    for batch in b1:
        for intent in batch.intents:
            assert intent.adv_usd is None
            assert intent.max_participation is None


# --------------------------------------------------------------------------- #
# Reconciliation correctness
# --------------------------------------------------------------------------- #
def test_fill_cost_uses_realized_weight_not_target():
    """Cost is charged on executed weight, so partial fills cost less."""
    partial = {
        "filled_weight": 0.05,
        "order_weight": 0.20,
        "slippage": 0.0,
        "status": "partial",
    }
    full = {"filled_weight": 0.20, "order_weight": 0.20, "slippage": 0.0}
    c_partial = _fill_cost(partial, transaction_costs=0.001, slippage=0.0)
    c_full = _fill_cost(full, transaction_costs=0.001, slippage=0.0)
    assert c_partial < c_full
    assert c_partial == pytest.approx(0.05 * 0.001)


def test_fill_cost_canonical_order_weight_schema_still_charged():
    """Canonical R5-B/C fills (order_weight only) keep shipped cost semantics."""
    fill = {"order_weight": 0.10, "slippage": 0.0, "status": "filled"}
    assert _fill_executed_weight(fill) == pytest.approx(0.10)
    assert _fill_cost(fill, transaction_costs=0.001, slippage=0.0) == pytest.approx(0.10 * 0.001)
    # Per-fill slippage is added to the traded weight, matching R5-B.
    with_slip = {"order_weight": 0.10, "slippage": 0.001, "status": "filled"}
    assert _fill_cost(with_slip, transaction_costs=0.001, slippage=0.0) == pytest.approx(
        0.10 * 0.002
    )


def test_fill_cost_rejected_fill_is_zero_cost():
    """Rejected/unfilled orders execute nothing and cost nothing."""
    for status in ("rejected", "cancelled", "unfilled", "failed"):
        fill = {
            "order_weight": 0.5,
            "filled_weight": 0.0,
            "slippage": 0.01,
            "status": status,
        }
        assert _fill_executed_weight(fill) == 0.0
        assert _fill_cost(fill, transaction_costs=0.001, slippage=0.01) == 0.0


def test_reconcile_costs_partial_fills_produce_deltas():
    """Partial fills create per-period executed/model deltas."""
    frame = _frame_from_real()
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=frame)
    w = res.weights
    date_key = str(w.index[10].isoformat())
    fills = [
        {
            "date": date_key,
            "asset": "BTC",
            "requested_weight": 0.10,
            "filled_weight": 0.02,
            "fill_ratio": 0.2,
            "order_weight": 0.10,
            "notional_usd": 1000.0,
            "slippage": 0.001,
            "status": "partial",
            "reason": "participation_cap",
        }
    ]
    rc = reconcile_costs(w, executed_fills=fills, transaction_costs=0.001, slippage=0.0)
    by_date = {d["date"]: d for d in rc.per_period}
    assert by_date[date_key]["delta"] != 0.0
    assert rc.aggregate["n_mismatches"] > 0
    json.dumps(rc.to_dict(), allow_nan=False)


def test_reconcile_fills_partial_shortfall_changes_realized_equity():
    """Unfilled remainder must move realized equity away from the model."""
    frame = _frame_from_real()
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=frame)
    w = res.weights

    base = reconcile_fills_to_backtest(w, res.returns, res.backtest, fills=None)

    date_key = str(w.index[30].isoformat())
    asset = str(w.columns[0])
    partial = [
        {
            "date": date_key,
            "asset": asset,
            "requested_weight": 0.2,
            "filled_weight": 0.0,
            "fill_ratio": 0.0,
            "order_weight": 0.2,
            "notional_usd": 1000.0,
            "slippage": 0.0,
            "status": "rejected",
            "reason": "rejected",
        }
    ]
    rf = reconcile_fills_to_backtest(w, res.returns, res.backtest, fills=partial)
    assert rf.aggregate["realized_final_equity"] != pytest.approx(
        base.aggregate["realized_final_equity"]
    )
    json.dumps(rf.to_dict(), allow_nan=False)


def test_reconcile_fills_zero_cost_full_fill_tracks_model():
    """Zero-cost full fills reproduce the model book (no fabricated mismatch)."""
    frame = _frame_from_real()
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=frame)
    adapter = PaperAdapter()
    adapter.prices = _prices_from_returns(frame)
    batches = order_batches_from_weights(res.weights, adapter.prices)
    fills = [f for b in batches for f in adapter.submit_intents(b)]
    rf = reconcile_fills_to_backtest(
        res.weights,
        res.returns,
        res.backtest,
        fills=fills,
        transaction_costs=0.0,
        slippage=0.0,
    )
    assert rf.aggregate["n_mismatches"] == 0
    assert abs(rf.aggregate["delta_final"]) < 1e-9


def test_reconcile_determinism_and_checksum_sensitivity():
    """Reconciliation is deterministic and checksum reacts to fill changes."""
    frame = _frame_from_real()
    strat = BABStrategy(benchmark="BTC")
    res = strat.run(returns_df=frame)
    w = res.weights
    a = reconcile_costs(w, executed_fills=None)
    b = reconcile_costs(w, executed_fills=None)
    assert a.checksum == b.checksum

    date_key = str(w.index[10].isoformat())
    fills = [
        {
            "date": date_key,
            "asset": "BTC",
            "order_weight": 0.1,
            "notional_usd": 10000.0,
            "slippage": 0.001,
        }
    ]
    c = reconcile_costs(w, executed_fills=fills)
    assert c.checksum != a.checksum

    fa = reconcile_fills_to_backtest(w, res.returns, res.backtest, fills=None)
    fb = reconcile_fills_to_backtest(w, res.returns, res.backtest, fills=None)
    assert fa.checksum == fb.checksum


# --------------------------------------------------------------------------- #
# Strategy/CLI integration + default-path invariance
# --------------------------------------------------------------------------- #
def test_strategy_run_with_realism_adapter_records_fills():
    """Strategy wiring consumes config knobs and records deterministic fills."""
    frame = _frame_from_real()
    prices = _prices_from_returns(frame)
    adv = _adv(frame.columns)

    def run() -> BABStrategy:
        adapter = PaperAdapter()
        adapter.prices = prices
        adapter.adv_usd = adv
        adapter.partial_fill = True
        adapter.max_participation = 0.01
        strat = BABStrategy(benchmark="BTC", execution_adapter=adapter)
        res = strat.run(returns_df=frame)
        assert res.execution is not None
        assert res.execution["n_fills"] > 0
        fills = res.execution["fills"]
        for fill in fills:
            assert fill["adv_usd"] is not None and fill["adv_usd"] > 0
            json.dumps(fill, allow_nan=False)
        return res

    first, second = run(), run()
    assert first.execution["fills"] == second.execution["fills"]
    pd.testing.assert_frame_equal(first.backtest, second.backtest)


def test_default_path_without_adapter_is_unchanged():
    """No adapter => execution is None and backtest matches shipped columns."""
    frame = _frame_from_real()
    res = BABStrategy(benchmark="BTC").run(returns_df=frame)
    assert res.execution is None
    assert list(res.backtest.columns) == BACKTEST_COLUMNS
    net = res.weights.sum(axis=1).to_numpy(dtype=float)
    assert np.isfinite(net).all()
    assert float(np.abs(net).max()) <= DN_TOL


def test_adapter_does_not_mutate_backtest_or_weights():
    """Configured adapter is observational: backtest/weights identical."""
    frame = _frame_from_real()
    plain = BABStrategy(benchmark="BTC").run(returns_df=frame)

    adapter = PaperAdapter()
    adapter.prices = _prices_from_returns(frame)
    adapter.adv_usd = _adv(frame.columns)
    adapter.partial_fill = True
    adapter.max_participation = 0.01
    with_adapter = BABStrategy(benchmark="BTC", execution_adapter=adapter).run(returns_df=frame)

    pd.testing.assert_frame_equal(plain.backtest, with_adapter.backtest)
    pd.testing.assert_frame_equal(plain.weights, with_adapter.weights)
