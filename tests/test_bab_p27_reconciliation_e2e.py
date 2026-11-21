"""Acceptance tests for P27 WP2: reconciliation enforcement end-to-end.

These tests assert reconciliation-enforcement CORRECTNESS, not a forced
outcome. The campaign runs on the P25 WP0 wide fixture (read-only) plus
synthetic cost/equity drift paths and validates that every reconciliation gate
trips safely before any real-market deployment is contemplated.

Contract (from HANDOFF.md P27 WP2):

* scripts/bab_reconciliation_e2e.py — deterministic seeded campaign;
  run_reconciliation_e2e() returns a results dict and writes JSON + markdown
  artifacts; build_reconciliation_e2e() does no writes.
* research_state/bab_p27/reconciliation_e2e.json — committed machine artifact.
* research_state/bab_p27/reconciliation_e2e.md — committed human artifact.
* Runs reconcile_costs (R5-B modeled-vs-executed) and
  reconcile_fills_to_backtest (R5-C fills-vs-backtest) from
  strategies.betting_against_beta.reconciliation plus
  evaluate_reconciliation_gate(costs_rec, fills_rec,
  cost_tolerance=..., mismatch_tolerance=...) after a paper run on the P25 WP0
  fixture read-only.
* Stress-scenario battery: (a) drift strictly above tolerance -> ok=False /
  violation present; (b) tolerance exactly equal to observed drift -> passes;
  (c) mismatch count strictly above limit -> fails closed;
  (d) emit-only (no tolerance, no max-mismatch) -> passes;
  (e) clean path (no drift) -> passes.
* rank_min_leg_beta=0.20 / rank_max_gross=4.0 unchanged; never weakened.
* Deterministic seeded; byte-identical reruns of build_reconciliation_e2e();
  fixture SHA256 provenance matches P25 WP0 (a6d390fc…163b); synthetic,
  no network.
* 20+ acceptance tests; zero ruff errors on new files; full gate 100%
  coverage.
* No edits to any P20-P26 artifact or any P27 WP0-WP1 artifact; P27 WP2
  consumes them read-only.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.reconciliation import (
    evaluate_reconciliation_gate,
    reconcile_costs,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
FIXTURE_META = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_reconciliation_e2e.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p27"
JSON_ARTIFACT = ARTIFACT_DIR / "reconciliation_e2e.json"
MD_ARTIFACT = ARTIFACT_DIR / "reconciliation_e2e.md"

SEED = 20261121
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
P25_WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_harness():
    spec = importlib.util.spec_from_file_location("bab_reconciliation_e2e", HARNESS_SCRIPT)
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


def test_harness_has_entry_points():
    mod = _import_harness()
    assert callable(getattr(mod, "run_reconciliation_e2e", None))
    assert callable(getattr(mod, "build_reconciliation_e2e", None))


def test_run_reconciliation_e2e_returns_dict():
    mod = _import_harness()
    payload = mod.run_reconciliation_e2e()
    assert isinstance(payload, dict)
    assert "paper_run" in payload
    assert "stress_scenarios" in payload
    assert "all_gates_trip" in payload
    assert "determinism" in payload


# --------------------------------------------------------------------------- #
# Schema & chartered metadata
# --------------------------------------------------------------------------- #
def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p27.reconciliation_e2e/1"


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
    assert prov["no_network"] is True


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
# Real paper run gates (P25 WP0 fixture, read-only)
# --------------------------------------------------------------------------- #
def test_paper_emit_only_gate_passes():
    d = _load_json()
    assert d["paper_run"]["gate_emit_only_ok"] is True
    assert d["paper_run"]["gate_emit_only_violations"] == 0


def test_paper_drift_zero_tolerance_fails_closed():
    d = _load_json()
    assert d["paper_run"]["gate_drift_zero_ok"] is False
    assert d["paper_run"]["gate_drift_zero_violations"] > 0


def test_paper_tolerance_exact_equal_passes():
    d = _load_json()
    assert d["paper_run"]["gate_drift_exact_ok"] is True
    assert d["paper_run"]["gate_drift_exact_violations"] == 0


def test_paper_max_mismatch_zero_fails_closed():
    d = _load_json()
    assert d["paper_run"]["gate_max_mismatch_zero_ok"] is False
    assert d["paper_run"]["gate_max_mismatch_zero_violations"] > 0


def test_paper_reconciliation_enforced():
    d = _load_json()
    assert d["paper_run"]["reconciliation_enforced"] is True


def test_paper_run_has_periods_and_fills():
    d = _load_json()
    assert d["paper_run"]["n_periods_costs"] > 0
    assert d["paper_run"]["n_periods_fills"] > 0
    assert d["paper_run"]["n_fills"] > 0


# --------------------------------------------------------------------------- #
# Stress-scenario battery (a)-(e)
# --------------------------------------------------------------------------- #
def test_stress_a_drift_above_tolerance_fails_closed():
    d = _load_json()
    s = d["stress_scenarios"]["a_drift_above_tolerance"]
    assert s["ok"] is False
    assert s["violations"] > 0


def test_stress_b_tolerance_exact_equal_passes():
    d = _load_json()
    s = d["stress_scenarios"]["b_tolerance_exact_equal"]
    assert s["ok"] is True
    assert s["violations"] == 0


def test_stress_c_mismatch_above_limit_fails_closed():
    d = _load_json()
    s = d["stress_scenarios"]["c_mismatch_above_limit"]
    assert s["ok"] is False
    assert s["violations"] > 0


def test_stress_d_emit_only_passes():
    d = _load_json()
    s = d["stress_scenarios"]["d_emit_only"]
    assert s["ok"] is True
    assert s["violations"] == 0


def test_stress_e_clean_path_passes():
    d = _load_json()
    s = d["stress_scenarios"]["e_clean_path"]
    assert s["ok"] is True
    assert s["violations"] == 0


def test_stress_observed_drift_recorded():
    d = _load_json()
    assert d["stress_scenarios"]["observed_drift_max_abs"] > 0
    assert d["stress_scenarios"]["observed_n_mismatches"] > 0


# --------------------------------------------------------------------------- #
# Aggregate
# --------------------------------------------------------------------------- #
def test_all_gates_trip():
    d = _load_json()
    assert d["all_gates_trip"] is True


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def test_determinism_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_reconciliation_e2e(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_reconciliation_e2e(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "campaign must be byte-identical across reruns"
    d = _load_json()
    assert d["determinism"]["byte_identical"] is True


def test_no_network_no_ccxt_import():
    mod = _import_harness()
    source = HARNESS_SCRIPT.read_text(encoding="utf-8")
    assert "ccxt" not in source, "reconciliation script must not import ccxt (no network)"
    assert "socket" not in source, "reconciliation script must not open network sockets"


# --------------------------------------------------------------------------- #
# Gate semantics exercised directly on synthetic inputs
# --------------------------------------------------------------------------- #
def test_gate_clean_path_with_zero_tolerance():
    idx = pd.date_range("2021-01-04", periods=3, freq="D")
    weights = pd.DataFrame({"A": [0.1] * 3, "B": [-0.1] * 3}, index=idx)
    fills = [
        {"date": d.isoformat(), "asset": "a", "filled_weight": 0.1, "order_weight": 0.1,
         "slippage": 0.0, "status": "filled"}
        for d in idx
    ]
    rec = reconcile_costs(
        weights, model=None, executed_fills=fills,
        transaction_costs=0.0, slippage=0.0,
    )
    gate = evaluate_reconciliation_gate(rec, None, cost_tolerance=0.0, mismatch_tolerance=0)
    assert gate["ok"] is True
    assert gate["violations"] == []


def test_gate_drift_above_tolerance_violates():
    idx = pd.date_range("2021-01-04", periods=3, freq="D")
    weights = pd.DataFrame({"A": [0.1] * 3, "B": [-0.1] * 3}, index=idx)
    fills = [
        {"date": d.isoformat(), "asset": "a", "filled_weight": 0.1, "order_weight": 0.1,
         "transaction_costs": 0.05, "slippage": 0.0, "status": "filled"}
        for d in idx
    ]
    rec = reconcile_costs(
        weights, model=None, executed_fills=fills,
        transaction_costs=TRANSACTION_COSTS, slippage=0.0,
    )
    gate = evaluate_reconciliation_gate(rec, None, cost_tolerance=0.0, mismatch_tolerance=0)
    assert gate["ok"] is False
    assert len(gate["violations"]) > 0


def test_gate_tolerance_equal_to_drift_passes():
    idx = pd.date_range("2021-01-04", periods=3, freq="D")
    weights = pd.DataFrame({"A": [0.1] * 3, "B": [-0.1] * 3}, index=idx)
    fills = [
        {"date": d.isoformat(), "asset": "a", "filled_weight": 0.1, "order_weight": 0.1,
         "transaction_costs": 0.05, "slippage": 0.0, "status": "filled"}
        for d in idx
    ]
    rec = reconcile_costs(
        weights, model=None, executed_fills=fills,
        transaction_costs=TRANSACTION_COSTS, slippage=0.0,
    )
    drift = float(rec.aggregate["delta_max_abs"])
    gate = evaluate_reconciliation_gate(
        rec, None, cost_tolerance=drift, mismatch_tolerance=int(rec.aggregate["n_mismatches"]),
    )
    assert gate["ok"] is True
    assert gate["violations"] == []


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
