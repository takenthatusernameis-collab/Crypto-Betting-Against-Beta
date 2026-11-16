"""P18-1 characterization tests for the reconciliation drift gate.

These tests MUST fail on HEAD: ``evaluate_reconciliation_gate`` does not exist
and the CLI has no ``--reconcile-tolerance`` enforcement. They pass after the
P18-1 fix. Deterministic, no network.
"""

from __future__ import annotations

import pandas as pd

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.costs import TransactionCostModel
from strategies.betting_against_beta.reconciliation import (
    evaluate_reconciliation_gate,
    reconcile_costs,
    reconcile_fills_to_backtest,
)

_ZERO_MODEL = TransactionCostModel(
    linear_fee=0.0,
    bid_ask_bps=0.0,
    impact_coefficient=0.0,
    borrow_bps_per_year=0.0,
    fixed_fee_per_trade=0.0,
)

_DATES = pd.date_range("2024-01-01", periods=3, freq="D")


def _weights():
    return pd.DataFrame({"BTC": [0.5, 0.0, 0.0], "ETH": [-0.5, 0.0, 0.0]}, index=_DATES)


def _prices():
    return pd.DataFrame(
        {"BTC": [50000.0, 50000.0, 50000.0], "ETH": [3000.0, 3000.0, 3000.0]},
        index=_DATES,
    )


def _returns():
    return pd.DataFrame({"BTC": [0.0, 0.0, 0.0], "ETH": [0.0, 0.0, 0.0]}, index=_DATES)


def _backtest():
    return pd.DataFrame({"cumulative": [1.0, 1.0, 1.0]}, index=_DATES)


def _fill(asset="BTC", filled_weight=1.0, date="2024-01-02", tx=0.01, slip=0.0):
    return {
        "date": date,
        "asset": asset,
        "filled_weight": filled_weight,
        "order_weight": filled_weight,
        "status": "filled",
        "transaction_costs": tx,
        "slippage": slip,
    }


def _costs_rec(fills=None, tx=0.01, slip=0.0):
    return reconcile_costs(
        _weights(),
        prices=_prices(),
        model=_ZERO_MODEL,
        executed_fills=fills or [],
        transaction_costs=tx,
        slippage=slip,
    )


def _fills_rec(fills=None, tx=0.01, slip=0.0):
    return reconcile_fills_to_backtest(
        _weights(),
        _returns(),
        _backtest(),
        fills=fills or [],
        transaction_costs=tx,
        slippage=slip,
    )


def test_clean_fills_gate_ok():
    costs = _costs_rec([])
    fills = _fills_rec([])
    out = evaluate_reconciliation_gate(
        costs,
        fills,
        cost_tolerance=0.0,
        equity_tolerance=0.0,
        mismatch_tolerance=0,
    )
    assert out["ok"] is True
    assert out["violations"] == []


def test_cost_drift_beyond_tolerance_violation():
    costs = _costs_rec([_fill()])
    fills = _fills_rec([])
    out = evaluate_reconciliation_gate(
        costs,
        fills,
        cost_tolerance=0.005,
        equity_tolerance=None,
        mismatch_tolerance=None,
    )
    assert out["ok"] is False
    assert any(
        v["check"] == "delta_max_abs" and v["source"] == "costs" and v["actual"] == 0.01
        for v in out["violations"]
    )


def test_equity_drift_beyond_tolerance_violation():
    costs = _costs_rec([])
    fills = _fills_rec([_fill()])
    out = evaluate_reconciliation_gate(
        costs,
        fills,
        cost_tolerance=None,
        equity_tolerance=0.005,
        mismatch_tolerance=None,
    )
    assert out["ok"] is False
    assert any(
        v["check"] == "max_delta_abs" and v["source"] == "fills"
        for v in out["violations"]
    )


def test_tolerance_boundary_exact_passes_just_above_fails():
    costs = _costs_rec([_fill()])  # delta_max_abs == 0.01 exactly
    fills = _fills_rec([])
    at_tol = evaluate_reconciliation_gate(
        costs, fills, cost_tolerance=0.01, equity_tolerance=None, mismatch_tolerance=None
    )
    assert at_tol["ok"] is True
    assert at_tol["violations"] == []
    just_above = evaluate_reconciliation_gate(
        costs, fills, cost_tolerance=0.009999, equity_tolerance=None, mismatch_tolerance=None
    )
    assert just_above["ok"] is False


def test_mismatch_count_violation():
    costs = _costs_rec([_fill()])  # n_mismatches == 1
    fills = _fills_rec([])
    out = evaluate_reconciliation_gate(
        costs, fills, cost_tolerance=None, equity_tolerance=None, mismatch_tolerance=0
    )
    assert out["ok"] is False
    assert any(v["check"] == "n_mismatches" and v["source"] == "costs" for v in out["violations"])


def test_gate_is_json_safe_and_non_mutating():
    import json

    costs = _costs_rec([_fill()])
    fills = _fills_rec([_fill()])
    before_costs = costs.to_dict()
    before_fills = fills.to_dict()
    out = evaluate_reconciliation_gate(
        costs,
        fills,
        cost_tolerance=0.005,
        equity_tolerance=0.005,
        mismatch_tolerance=0,
    )
    assert costs.to_dict() == before_costs
    assert fills.to_dict() == before_fills
    json.dumps(out)  # must serialize strictly


def test_cli_reconcile_alone_stays_green(tmp_path):
    out = tmp_path / "out.json"
    rc = main(
        ["--synthetic", "--adapter", "paper", "--reconcile", "--output", str(out)]
    )
    assert rc == 0


def test_cli_tolerance_below_drift_returns_nonzero(tmp_path):
    out = tmp_path / "out.json"
    rc = main(
        [
            "--synthetic",
            "--adapter",
            "paper",
            "--reconcile",
            "--transaction-costs",
            "0.01",
            "--reconcile-tolerance",
            "0.0",
            "--output",
            str(out),
        ]
    )
    assert rc == 2


def test_cli_tolerance_above_drift_stays_green(tmp_path):
    out = tmp_path / "out.json"
    rc = main(
        [
            "--synthetic",
            "--adapter",
            "paper",
            "--reconcile",
            "--transaction-costs",
            "0.01",
            "--reconcile-tolerance",
            "0.5",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
