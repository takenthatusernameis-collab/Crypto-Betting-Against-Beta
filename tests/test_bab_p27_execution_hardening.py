"""Acceptance tests for P27 WP0: execution adapter hardening & dry-run paper campaign.

These tests assert execution-hardening CORRECTNESS, not a forced outcome. The
campaign runs on the P25 WP0 wide fixture (read-only) and validates that the
paper adapter, dry-run live adapter, risk controls, and reconciliation
enforcement all behave safely and deterministically before any real-market
deployment is contemplated.

Contract (from HANDOFF.md P27 WP0):

* scripts/bab_execution_hardening.py — deterministic seeded campaign;
  run_execution_hardening() returns a results dict and writes JSON + markdown
  artifacts plus paper_orders.jsonl / paper_diagnostics.jsonl sidecars;
  build_execution_hardening() does no writes.
* research_state/bab_p27/execution_hardening.json — committed machine artifact.
* research_state/bab_p27/execution_hardening.md — committed human artifact.
* research_state/bab_p27/paper_orders.jsonl — timestamped orders.
* research_state/bab_p27/paper_diagnostics.jsonl — diagnostics sidecar.
* Paper adapter end-to-end on the P25 WP0 fixture read-only: order->fill->
  position lifecycle (no orphan fills, no double-submit, no fill without order;
  weights sum to zero and sum(w_i*beta_i) ~= 0).
* Dry-run live adapter health check: strict JSON with mode/exchange/connected/
  dry_run/testnet/n_submitted/n_fills; dry_run=true; never network, never
  implicit live execution.
* Risk controls: kill switch on max drawdown, max position size, max staleness
  (position age), per-leg exposure caps; gates trip on synthetic stress.
* Reconciliation enforcement end-to-end: R5-B + R5-C; fail closed (rc 2
  equivalent) on drift; emit-only passes.
* rank_min_leg_beta=0.20 / rank_max_gross=4.0 unchanged; never weakened.
* Deterministic seeded; byte-identical reruns; fixture SHA256 provenance
  matches P25 WP0 (a6d390fc…163b).
* 20+ acceptance tests; zero ruff errors on new files; full gate 100% coverage.
* No edits to any P20-P26 artifact; P27 consumes them read-only.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.risk import RiskLimits, RiskManager, apply_kill_switch

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
FIXTURE_META = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_execution_hardening.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p27"
JSON_ARTIFACT = ARTIFACT_DIR / "execution_hardening.json"
MD_ARTIFACT = ARTIFACT_DIR / "execution_hardening.md"
ORDERS_JSONL = ARTIFACT_DIR / "paper_orders.jsonl"
DIAGNOSTICS_JSONL = ARTIFACT_DIR / "paper_diagnostics.jsonl"

SEED = 20261121
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
DECIMALS = 6
WEIGHT_SUM_TOL = 1e-9
BETA_NEUTRAL_TOL = 1e-2
P25_WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_harness():
    spec = importlib.util.spec_from_file_location("bab_execution_hardening", HARNESS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------- #
# Existence & entry points
# --------------------------------------------------------------------------- #
def test_harness_script_exists():
    assert HARNESS_SCRIPT.is_file(), f"missing {HARNESS_SCRIPT}"


def test_json_artifact_exists():
    assert JSON_ARTIFACT.is_file(), f"missing {JSON_ARTIFACT}"


def test_md_artifact_exists():
    assert MD_ARTIFACT.is_file(), f"missing {MD_ARTIFACT}"


def test_paper_orders_jsonl_exists():
    assert ORDERS_JSONL.is_file(), f"missing {ORDERS_JSONL}"


def test_paper_diagnostics_jsonl_exists():
    assert DIAGNOSTICS_JSONL.is_file(), f"missing {DIAGNOSTICS_JSONL}"


def test_harness_has_entry_points():
    mod = _import_harness()
    assert callable(getattr(mod, "run_execution_hardening", None))
    assert callable(getattr(mod, "build_execution_hardening", None))


def test_run_execution_hardening_returns_dict():
    mod = _import_harness()
    payload = mod.run_execution_hardening()
    assert isinstance(payload, dict)
    assert "paper" in payload and "live_health_check" in payload
    assert "risk_controls" in payload and "reconciliation" in payload
    assert "determinism" in payload


# --------------------------------------------------------------------------- #
# Schema & chartered metadata
# --------------------------------------------------------------------------- #
def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p27.execution_hardening/1"


def test_metadata_chartered():
    d = _load_json()
    assert d["seed"] == SEED
    assert d["synthetic"] is True
    assert d["benchmark"] == "BTC"
    assert d["beta_window"] == BETA_WINDOW
    assert d["min_observations"] == MIN_OBSERVATIONS
    assert d["rank_min_leg_beta"] == RANK_MIN_LEG_BETA
    assert d["rank_max_gross"] == RANK_MAX_GROSS
    assert d["transaction_costs"] == TRANSACTION_COSTS
    assert d["no_network"] is True
    assert isinstance(d["fixture_sha256"], str) and len(d["fixture_sha256"]) == 64
    prov = d["provenance"]
    assert isinstance(prov, dict)
    assert isinstance(prov.get("provenance"), str) and len(prov["provenance"]) > 0


def test_fixture_sha256_matches_wp0():
    d = _load_json()
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    assert d["fixture_sha256"] == actual
    assert d["fixture_sha256"] == P25_WP0_FIXTURE_SHA256
    assert d["fixture_sha256"] == meta["fixture_sha256"]
    assert d["provenance"]["fixture_sha256"] == actual


def test_rank_min_leg_beta_unchanged():
    d = _load_json()
    assert d["rank_min_leg_beta_unchanged"] is True
    assert d["rank_min_leg_beta"] == RANK_MIN_LEG_BETA


def test_rank_max_gross_unchanged():
    d = _load_json()
    assert d["rank_max_gross_unchanged"] is True
    assert d["rank_max_gross"] == RANK_MAX_GROSS


# --------------------------------------------------------------------------- #
# Paper adapter end-to-end (lifecycle)
# --------------------------------------------------------------------------- #
def test_paper_end_to_end_emits_orders_and_fills():
    d = _load_json()
    paper = d["paper"]
    assert paper["n_orders"] > 0, "paper run must emit orders"
    assert paper["n_fills"] > 0, "paper run must emit fills"
    assert paper["adapter_present"] is True
    assert paper["adapter_fills_match_engine"] is True


def test_paper_n_fills_equals_n_orders():
    d = _load_json()
    life = d["paper"]["lifecycle"]
    assert life["n_fills_equals_n_orders"] is True


def test_no_double_submit():
    d = _load_json()
    assert d["paper"]["lifecycle"]["no_double_submit"] is True


def test_no_orphan_fills():
    d = _load_json()
    assert d["paper"]["lifecycle"]["no_orphan_fills"] is True


def test_no_fill_without_order():
    d = _load_json()
    assert d["paper"]["lifecycle"]["no_fill_without_order"] is True


def test_weights_sum_to_zero():
    d = _load_json()
    assert d["paper"]["lifecycle"]["weights_sum_zero"] is True


def test_beta_neutrality():
    d = _load_json()
    assert d["paper"]["lifecycle"]["beta_neutral"] is True


def test_lifecycle_valid():
    d = _load_json()
    assert d["paper"]["lifecycle"]["lifecycle_valid"] is True


def test_jsonl_sidecars_well_formed():
    order_text = ORDERS_JSONL.read_text(encoding="utf-8")
    diag_text = DIAGNOSTICS_JSONL.read_text(encoding="utf-8")
    order_lines = [line for line in order_text.splitlines() if line.strip()]
    diag_lines = [line for line in diag_text.splitlines() if line.strip()]
    orders = [json.loads(line) for line in order_lines]
    diags = [json.loads(line) for line in diag_lines]
    assert len(orders) > 0
    assert len(diags) > 0
    for o in orders:
        assert "date" in o and "asset" in o and "weight" in o and "status" in o
    for g in diags:
        assert "date" in g and "turnover" in g and "hhi" in g


# --------------------------------------------------------------------------- #
# Dry-run live adapter health check
# --------------------------------------------------------------------------- #
def test_live_health_check_strict_json():
    d = _load_json()
    lc = d["live_health_check"]
    assert lc["strict_json"] is True


def test_live_health_check_required_keys():
    d = _load_json()
    lc = d["live_health_check"]
    assert lc["has_required_keys"] is True
    for key in ("mode", "exchange", "connected", "dry_run", "testnet", "n_submitted", "n_fills"):
        assert key in lc["health"], f"missing health key {key}"


def test_live_never_implicit_live_execution():
    d = _load_json()
    lc = d["live_health_check"]
    assert lc["dry_run_true"] is True
    assert lc["mode_live"] is True
    assert lc["never_implicit_live"] is True
    assert lc["health"]["dry_run"] is True


# --------------------------------------------------------------------------- #
# Risk controls
# --------------------------------------------------------------------------- #
def test_kill_switch_triggers_on_drawdown_breach():
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    weights = pd.DataFrame({"A": [0.5] * 4, "B": [-0.5] * 4}, index=idx)
    _, event = apply_kill_switch(weights, cumulative, 0.10)
    assert event.triggered is True
    assert event.observed_drawdown < -0.10


def test_kill_switch_flattens_positions():
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    weights = pd.DataFrame({"A": [0.5] * 4, "B": [-0.5] * 4}, index=idx)
    w_breach, event = apply_kill_switch(weights, cumulative, 0.10)
    assert event.triggered is True
    breach_row = w_breach.loc[event.date] if event.date is not None else w_breach.iloc[-1]
    assert float(breach_row.abs().sum()) == 0.0


def test_kill_switch_none_limit_not_triggered():
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    weights = pd.DataFrame({"A": [0.5] * 4, "B": [-0.5] * 4}, index=idx)
    w_none, event_none = apply_kill_switch(weights, cumulative, None)
    assert event_none.triggered is False
    assert w_none.equals(weights)


def test_max_position_weight_rejected():
    limits = RiskLimits(max_drawdown=0.10, max_position_weight=0.20, max_gross_exposure=1.0)
    rm = RiskManager(limits=limits, kill_switch_enabled=True)
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    current = pd.Series({"A": 0.0, "B": 0.0})
    big_w = pd.DataFrame({"A": [0.5], "B": [-0.5]}, index=pd.date_range("2021-01-05", periods=1))
    from strategies.betting_against_beta.execution import order_batches_from_weights
    batch = order_batches_from_weights(big_w)[0]
    result = rm.pre_trade_check(batch, current, cumulative, "2021-01-05")
    assert result.allowed is False or len(result.rejected_intents) > 0
    assert any(e.event_type == "order_rejected" for e in result.events)


def test_gross_exposure_cap_rejected():
    limits = RiskLimits(max_drawdown=0.10, max_position_weight=1.0, max_gross_exposure=1.0)
    rm = RiskManager(limits=limits, kill_switch_enabled=True)
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    current = pd.Series({"A": 0.0, "B": 0.0})
    gross_w = pd.DataFrame({"A": [0.9], "B": [0.9]}, index=pd.date_range("2021-01-06", periods=1))
    from strategies.betting_against_beta.execution import order_batches_from_weights
    batch = order_batches_from_weights(gross_w)[0]
    result = rm.pre_trade_check(batch, current, cumulative, "2021-01-06")
    assert result.allowed is False or len(result.rejected_intents) > 0


def test_position_age_staleness_cap_trips():
    limits = RiskLimits(max_position_age_days=1, max_position_weight=1.0)
    rm = RiskManager(limits=limits, kill_switch_enabled=False)
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    aged_w = pd.DataFrame({"A": [0.3]}, index=pd.date_range("2021-01-07", periods=1))
    from strategies.betting_against_beta.execution import order_batches_from_weights
    batch = order_batches_from_weights(aged_w)[0]
    current_aged = pd.Series({"A": 0.3})
    rm.pre_trade_check(batch, current_aged, cumulative, "2021-01-07")
    result_day2 = rm.pre_trade_check(batch, current_aged, cumulative, "2021-01-07")
    age_events = [
        e
        for e in result_day2.events
        if e.event_type == "limit_breach" and "age" in e.message.lower()
    ]
    assert len(age_events) > 0


def test_risk_controls_all_trip():
    d = _load_json()
    assert d["risk_controls"]["risk_gates_all_trip"] is True


# --------------------------------------------------------------------------- #
# Reconciliation enforcement (R5-B + R5-C)
# --------------------------------------------------------------------------- #
def test_reconciliation_emit_only_passes():
    d = _load_json()
    recon = d["reconciliation"]
    assert recon["gate_emit_only_ok"] is True
    assert recon["gate_emit_only_violations"] == 0


def test_reconciliation_fail_closed_on_drift():
    d = _load_json()
    recon = d["reconciliation"]
    assert recon["gate_drift_breached"] is True
    assert recon["gate_drift_violations"] > 0


def test_reconciliation_max_mismatch_gate_breached():
    d = _load_json()
    recon = d["reconciliation"]
    assert recon["gate_max_mismatch_breached"] is True


def test_reconciliation_enforced():
    d = _load_json()
    assert d["reconciliation"]["reconciliation_enforced"] is True


def test_reconciliation_r5b_r5c_aggregates():
    d = _load_json()
    r5b = d["reconciliation"]["r5b"]
    r5c = d["reconciliation"]["r5c"]
    assert r5b["n_periods"] > 0
    assert "delta_max_abs" in r5b["aggregate"]
    assert "n_mismatches" in r5b["aggregate"]
    assert r5c["n_periods"] > 0
    assert "max_delta_abs" in r5c["aggregate"]
    assert "n_mismatches" in r5c["aggregate"]
    assert isinstance(r5b["checksum"], str) and len(r5b["checksum"]) == 64
    assert isinstance(r5c["checksum"], str) and len(r5c["checksum"]) == 64


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def test_determinism_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_execution_hardening(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_execution_hardening(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "campaign must be byte-identical across reruns"
    d = _load_json()
    assert d["determinism"]["byte_identical"] is True


def test_no_network_no_ccxt_import():
    mod = _import_harness()
    source = HARNESS_SCRIPT.read_text(encoding="utf-8")
    assert "ccxt" not in source, "hardening script must not import ccxt (no network)"
    assert "socket" not in source, "hardening script must not open network sockets"


# --------------------------------------------------------------------------- #
# Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(HARNESS_SCRIPT), str(__file__)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
