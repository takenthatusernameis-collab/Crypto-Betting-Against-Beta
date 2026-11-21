"""Acceptance tests for P27 WP1: risk controls & kill switches.

These tests assert risk-control CORRECTNESS, not a forced outcome. The
campaign runs on the P25 WP0 wide fixture (read-only) plus synthetic stress
paths and validates that every risk gate trips safely before any real-market
deployment is contemplated.

Contract (from HANDOFF.md P27 WP1):

* scripts/bab_risk_controls.py — deterministic seeded campaign;
  run_risk_controls() returns a results dict and writes JSON + markdown
  artifacts; build_risk_controls() does no writes.
* research_state/bab_p27/risk_controls.json — committed machine artifact.
* research_state/bab_p27/risk_controls.md — committed human artifact.
* Risk controls exercised: RiskLimits + RiskManager + apply_kill_switch;
  kill switch on max drawdown (trigger + flatten positions from first breach
  date onward), max position weight (per-leg exposure cap rejects oversized
  legs), max staleness/position age (holding beyond max_position_age_days
  trips), per-leg and portfolio exposure caps (gross exposure cap rejects
  batches); limit=None -> not triggered, weights unchanged.
* Stress-scenario battery: (a) drawdown breach -> kill switch + flattened;
  (b) per-leg weight above max_position_weight -> order_rejected;
  (c) gross exposure above max_gross_exposure -> batch rejected;
  (d) position age beyond max_position_age_days -> staleness limit_breach;
  (e) limit=None -> not triggered, weights unchanged.
* rank_min_leg_beta=0.20 / rank_max_gross=4.0 unchanged; never weakened.
* Deterministic seeded; byte-identical reruns of build_risk_controls();
  fixture SHA256 provenance matches P25 WP0 (a6d390fc…163b); synthetic,
  no network.
* 20+ acceptance tests; zero ruff errors on new files; full gate 100%
  coverage.
* No edits to any P20-P26 artifact or any P27 WP0 artifact; P27 WP1 consumes
  them read-only.
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
from strategies.betting_against_beta.risk import (
    RiskLimits,
    RiskManager,
    apply_kill_switch,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
FIXTURE_META = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_risk_controls.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p27"
JSON_ARTIFACT = ARTIFACT_DIR / "risk_controls.json"
MD_ARTIFACT = ARTIFACT_DIR / "risk_controls.md"

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
    spec = importlib.util.spec_from_file_location("bab_risk_controls", HARNESS_SCRIPT)
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
    assert callable(getattr(mod, "run_risk_controls", None))
    assert callable(getattr(mod, "build_risk_controls", None))


def test_run_risk_controls_returns_dict():
    mod = _import_harness()
    payload = mod.run_risk_controls()
    assert isinstance(payload, dict)
    assert "kill_switch" in payload
    assert "position_weight" in payload
    assert "gross_exposure" in payload
    assert "staleness" in payload
    assert "risk_gates_all_trip" in payload
    assert "determinism" in payload


# --------------------------------------------------------------------------- #
# Schema & chartered metadata
# --------------------------------------------------------------------------- #
def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p27.risk_controls/1"


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
# Stress-scenario battery (a): drawdown breach -> kill switch + flattened
# --------------------------------------------------------------------------- #
def test_kill_switch_triggers_on_drawdown_breach():
    d = _load_json()
    assert d["kill_switch"]["triggered"] is True
    assert d["kill_switch"]["observed_drawdown"] < -0.10


def test_kill_switch_flattens_positions():
    d = _load_json()
    assert d["kill_switch"]["positions_flattened"] is True
    assert d["kill_switch"]["flattened_from_breach_date_onward"] is True


def test_kill_switch_breach_date_is_first_breach():
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    weights = pd.DataFrame({"A": [0.5] * 4, "B": [-0.5] * 4}, index=idx)
    _, event = apply_kill_switch(weights, cumulative, 0.10)
    assert event.triggered is True
    assert event.date == idx[2]


def test_kill_switch_risk_manager_emits_events():
    d = _load_json()
    rm = d["kill_switch_risk_manager"]
    assert rm["kill_switch_triggered"] is True
    assert rm["position_flattened"] is True
    assert "kill_switch" in rm["event_types"]
    assert "position_flattened" in rm["event_types"]


# --------------------------------------------------------------------------- #
# Stress-scenario battery (e): limit=None -> not triggered, unchanged
# --------------------------------------------------------------------------- #
def test_kill_switch_none_limit_not_triggered():
    d = _load_json()
    assert d["kill_switch_none"]["not_triggered"] is True


def test_kill_switch_none_weights_unchanged():
    d = _load_json()
    assert d["kill_switch_none"]["weights_unchanged"] is True


def test_kill_switch_none_byte_identical_default_path():
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    weights = pd.DataFrame({"A": [0.5] * 4, "B": [-0.5] * 4}, index=idx)
    w_none, event_none = apply_kill_switch(weights, cumulative, None)
    assert event_none.triggered is False
    assert w_none.equals(weights)


# --------------------------------------------------------------------------- #
# Stress-scenario battery (b): per-leg weight -> order_rejected
# --------------------------------------------------------------------------- #
def test_max_position_weight_order_rejected():
    d = _load_json()
    assert d["position_weight"]["rejected"] is True
    assert d["position_weight"]["order_rejected"] is True
    assert any(
        e["event_type"] == "order_rejected" for e in d["position_weight"]["events"]
    )


def test_max_position_weight_direct():
    limits = RiskLimits(
        max_drawdown=0.10,
        max_position_weight=0.20,
        max_gross_exposure=1.0,
    )
    rm = RiskManager(limits=limits, kill_switch_enabled=True)
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    current = pd.Series({"A": 0.0, "B": 0.0})
    big_w = pd.DataFrame(
        {"A": [0.5], "B": [-0.5]},
        index=pd.date_range("2021-01-05", periods=1),
    )
    from strategies.betting_against_beta.execution import order_batches_from_weights

    batch = order_batches_from_weights(big_w)[0]
    result = rm.pre_trade_check(batch, current, cumulative, "2021-01-05")
    assert result.allowed is False or len(result.rejected_intents) > 0
    assert any(e.event_type == "order_rejected" for e in result.events)


# --------------------------------------------------------------------------- #
# Stress-scenario battery (c): gross exposure -> batch rejected
# --------------------------------------------------------------------------- #
def test_gross_exposure_cap_batch_rejected():
    d = _load_json()
    assert d["gross_exposure"]["rejected"] is True
    assert d["gross_exposure"]["limit_breach"] is True
    assert any(
        e["event_type"] == "limit_breach" for e in d["gross_exposure"]["events"]
    )


def test_gross_exposure_cap_direct():
    limits = RiskLimits(
        max_drawdown=0.10,
        max_position_weight=1.0,
        max_gross_exposure=1.0,
    )
    rm = RiskManager(limits=limits, kill_switch_enabled=True)
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    current = pd.Series({"A": 0.0, "B": 0.0})
    gross_w = pd.DataFrame(
        {"A": [0.9], "B": [0.9]},
        index=pd.date_range("2021-01-06", periods=1),
    )
    from strategies.betting_against_beta.execution import order_batches_from_weights

    batch = order_batches_from_weights(gross_w)[0]
    result = rm.pre_trade_check(batch, current, cumulative, "2021-01-06")
    assert result.allowed is False or len(result.rejected_intents) > 0


# --------------------------------------------------------------------------- #
# Stress-scenario battery (d): position age -> staleness limit_breach
# --------------------------------------------------------------------------- #
def test_position_age_staleness_cap_trips():
    d = _load_json()
    assert d["staleness"]["trips"] is True
    assert d["staleness"]["limit_breach_events"] > 0
    assert any(
        e["event_type"] == "limit_breach" for e in d["staleness"]["events"]
    )


def test_position_age_staleness_direct():
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


# --------------------------------------------------------------------------- #
# Aggregates
# --------------------------------------------------------------------------- #
def test_risk_controls_all_trip():
    d = _load_json()
    assert d["risk_gates_all_trip"] is True


def test_required_event_types_present():
    d = _load_json()
    event_types = set()
    for section in (
        "position_weight",
        "gross_exposure",
        "staleness",
    ):
        for e in d[section]["events"]:
            event_types.add(e["event_type"])
    rm_types = set(d["kill_switch_risk_manager"]["event_types"])
    event_types |= rm_types
    assert "kill_switch" in event_types
    assert "limit_breach" in event_types
    assert "order_rejected" in event_types
    assert "position_flattened" in event_types


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def test_determinism_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_risk_controls(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_risk_controls(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "campaign must be byte-identical across reruns"
    d = _load_json()
    assert d["determinism"]["byte_identical"] is True


def test_no_network_no_ccxt_import():
    mod = _import_harness()
    source = HARNESS_SCRIPT.read_text(encoding="utf-8")
    assert "ccxt" not in source, "risk script must not import ccxt (no network)"
    assert "socket" not in source, "risk script must not open network sockets"


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
