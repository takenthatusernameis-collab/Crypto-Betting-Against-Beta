"""Acceptance tests for P26 WP0: signal-to-noise validation of rank-weighted BAB.

These tests assert battery CORRECTNESS, not a forced p-value. The verdict
(SIGNAL / NO-SIGNAL) is data-driven: on the no-alpha P25 WP0 fixture
(asset returns are beta * r_BTC + idio, idio iid N(0, 0.003), so no
cross-sectional alpha is planted) the expected honest outcome is NO-SIGNAL.
These tests never assert p_rank < 0.05 as a pass condition — that is the
hypothesis under test, not a correctness criterion.

Contract (from HANDOFF.md INITIAL TASK MESSAGE):

* scripts/bab_signal_null_battery.py — deterministic seeded battery;
  run_signal_null_battery() returns a results dict and writes JSON + markdown
  artifacts; build_signal_null_battery() does no writes.
* research_state/bab_p26/signal_null_battery.json — committed artifact.
* research_state/bab_p26/signal_null_battery.md — rendered companion.
* 1000 stable beta-neutral-preserving permuted null books on the P25 WP0
  fixture read-only; rank p-value/z-score/percentile and equal
  p-value/z-score/percentile; honest SIGNAL / NO-SIGNAL verdict;
  rank_min_leg_beta=0.20 / rank_max_gross=4.0 unchanged; fixture SHA256
  provenance matches P25 WP0; 20+ acceptance tests; deterministic seeded
  no-network; ruff clean; full gate 100% coverage.
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

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
FIXTURE_META = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_signal_null_battery.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p26"
JSON_ARTIFACT = ARTIFACT_DIR / "signal_null_battery.json"
MD_ARTIFACT = ARTIFACT_DIR / "signal_null_battery.md"

SEED = 20261120
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
TRAIN_WINDOW = 180
TEST_WINDOW = 40
N_FOLDS = 5
LONG_QUANTILE = 0.3
SHORT_QUANTILE = 0.3
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
N_NULL_REPLICATIONS = 1000
P_LEVEL = 0.05
DECIMALS = 6
WEIGHTINGS = ("equal", "rank")
BETA_NEUTRAL_TOL = 1e-2
EXPECTED_RETURN_ROWS = 398
EXPECTED_PRICE_ROWS = 399
WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"

# Committed P25 WP2 reference values the observed path must reproduce (6 dp).
OBSERVED_REFERENCE = {"rank": 0.437311, "equal": 0.170267}


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_harness():
    spec = importlib.util.spec_from_file_location("bab_signal_null_battery", HARNESS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- Existence & entry points -----------------------------------------------

def test_harness_script_exists():
    assert HARNESS_SCRIPT.is_file(), f"missing {HARNESS_SCRIPT}"


def test_json_artifact_exists():
    assert JSON_ARTIFACT.is_file(), f"missing {JSON_ARTIFACT}"


def test_md_artifact_exists():
    assert MD_ARTIFACT.is_file(), f"missing {MD_ARTIFACT}"


def test_harness_has_entry_points():
    mod = _import_harness()
    assert callable(getattr(mod, "run_signal_null_battery", None))
    assert callable(getattr(mod, "build_signal_null_battery", None))


def test_run_signal_null_battery_returns_dict():
    mod = _import_harness()
    payload = mod.run_signal_null_battery()
    assert isinstance(payload, dict)
    assert "verdict" in payload
    assert "observed" in payload
    assert "null" in payload


# --- Schema & chartered metadata -------------------------------------------

def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p26.signal_null_battery/1"


def test_metadata_fields_chartered():
    d = _load_json()
    assert d["seed"] == SEED
    assert d["n_folds"] == N_FOLDS
    assert d["train_window"] == TRAIN_WINDOW
    assert d["test_window"] == TEST_WINDOW
    assert d["beta_window"] == BETA_WINDOW
    assert d["min_observations"] == MIN_OBSERVATIONS
    assert d["long_quantile"] == LONG_QUANTILE
    assert d["short_quantile"] == SHORT_QUANTILE
    assert d["rank_min_leg_beta"] == RANK_MIN_LEG_BETA
    assert d["rank_max_gross"] == RANK_MAX_GROSS
    assert d["transaction_costs"] == TRANSACTION_COSTS
    assert d["n_null_replications"] == N_NULL_REPLICATIONS
    assert d["p_level"] == P_LEVEL
    assert d["synthetic"] is True
    assert d["weightings"] == list(WEIGHTINGS)
    assert isinstance(d["fixture_sha256"], str) and len(d["fixture_sha256"]) == 64
    prov = d["provenance"]
    assert isinstance(prov, dict)
    assert isinstance(prov.get("provenance"), str) and len(prov["provenance"]) > 0


def test_verdict_rule_chartered():
    d = _load_json()
    expected_rule = f"SIGNAL iff p_rank < {P_LEVEL} and p_equal > {P_LEVEL}; otherwise NO-SIGNAL."
    assert d["verdict_rule"] == expected_rule
    assert d["provenance"]["verdict_rule"].startswith("SIGNAL iff")


# --- Fixture provenance ------------------------------------------------------

def test_fixture_sha256_matches_wp0():
    d = _load_json()
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    assert d["fixture_sha256"] == actual
    assert d["fixture_sha256"] == WP0_FIXTURE_SHA256
    assert d["fixture_sha256"] == meta["fixture_sha256"]
    assert d["provenance"]["fixture_sha256"] == actual


# --- Observed values reproduce P25 WP2 --------------------------------------

def test_observed_rank_reproduces_p25_wp2():
    d = _load_json()
    got = d["observed"]["rank"]["mean_oos_sharpe"]
    assert got is not None
    assert round(got, DECIMALS) == OBSERVED_REFERENCE["rank"], (
        f"observed rank mean OOS Sharpe {got} != P25 WP2 {OBSERVED_REFERENCE['rank']}"
    )


def test_observed_equal_reproduces_p25_wp2():
    d = _load_json()
    got = d["observed"]["equal"]["mean_oos_sharpe"]
    assert got is not None
    assert round(got, DECIMALS) == OBSERVED_REFERENCE["equal"], (
        f"observed equal mean OOS Sharpe {got} != P25 WP2 {OBSERVED_REFERENCE['equal']}"
    )


def test_observed_per_fold_structure():
    d = _load_json()
    for w in WEIGHTINGS:
        per_fold = d["observed"][w]["per_fold"]
        assert len(per_fold) == N_FOLDS, f"{w}: expected {N_FOLDS} per-fold entries"
        for entry in per_fold:
            assert "fold" in entry and "test_start" in entry and "test_end" in entry
            assert entry["oos_sharpe"] is None or (
                isinstance(entry["oos_sharpe"], float) and math.isfinite(entry["oos_sharpe"])
            )


# --- Null distribution sanity ----------------------------------------------

def test_null_has_full_replications():
    d = _load_json()
    for w in WEIGHTINGS:
        assert d["null"][w]["n_null_replications"] == N_NULL_REPLICATIONS, (
            f"{w}: expected {N_NULL_REPLICATIONS} null replications, "
            f"got {d['null'][w]['n_null_replications']}"
        )


def test_null_sharpes_finite_and_bounded():
    d = _load_json()
    for w in WEIGHTINGS:
        sharpes = d["null"][w]["null_sharpes"]
        assert len(sharpes) == N_NULL_REPLICATIONS
        for s in sharpes:
            assert s is not None and math.isfinite(s)


def test_null_stats_consistent():
    d = _load_json()
    for w in WEIGHTINGS:
        st = d["null"][w]
        sharpes = [s for s in st["null_sharpes"] if s is not None and math.isfinite(s)]
        assert len(sharpes) == N_NULL_REPLICATIONS
        assert st["null_mean"] is not None and math.isfinite(st["null_mean"])
        assert st["null_std"] is not None and st["null_std"] > 0.0
        assert st["null_min"] is not None and st["null_max"] is not None
        assert st["null_min"] <= st["null_mean"] <= st["null_max"]
        # z = (observed - null_mean) / null_std
        obs = d["observed"][w]["mean_oos_sharpe"]
        expected_z = round((obs - st["null_mean"]) / st["null_std"], DECIMALS)
        assert st["z_score"] is not None
        assert round(st["z_score"], DECIMALS) == expected_z, (
            f"{w}: z_score={st['z_score']} != expected {expected_z}"
        )


def test_p_value_in_unit_interval():
    d = _load_json()
    for w in WEIGHTINGS:
        p = d["null"][w]["p_value"]
        assert p is not None and 0.0 <= p <= 1.0, f"{w}: p_value={p} not in [0, 1]"


def test_percentile_in_zero_to_hundred():
    d = _load_json()
    for w in WEIGHTINGS:
        pct = d["null"][w]["empirical_percentile"]
        assert pct is not None and 0.0 <= pct <= 100.0, (
            f"{w}: empirical_percentile={pct} not in [0, 100]"
        )


def test_null_centered_near_zero_stability():
    """Null mean must not exhibit extreme drift - catches the turnover/instability
    failure mode (per-row random selection produced null equal mean = -37). A
    fixed-per-fold null stays well within +/-1.0."""
    d = _load_json()
    for w in WEIGHTINGS:
        nm = d["null"][w]["null_mean"]
        assert nm is not None and math.isfinite(nm)
        assert abs(nm) < 1.0, f"{w}: null_mean={nm} shows extreme drift (turnover/instability)"


# --- Verdict consistency (data-driven, never forced) ------------------------

def test_verdict_is_valid_string():
    d = _load_json()
    assert d["verdict"] in {"SIGNAL", "NO-SIGNAL"}, f"invalid verdict: {d['verdict']}"


def test_verdict_consistent_with_p_values():
    """Verdict must be the boolean identity of the p-value rule, whatever the values."""
    d = _load_json()
    p_rank = d["null"]["rank"]["p_value"]
    p_equal = d["null"]["equal"]["p_value"]
    expected = "SIGNAL" if (
        p_rank is not None and p_equal is not None
        and p_rank < P_LEVEL and p_equal > P_LEVEL
    ) else "NO-SIGNAL"
    assert d["verdict"] == expected, (
        f"verdict={d['verdict']} inconsistent with p_rank={p_rank}, p_equal={p_equal}"
    )


def test_no_forced_p_value_pass_condition():
    """This test must pass regardless of the data-driven p-values."""
    d = _load_json()
    p_rank = d["null"]["rank"]["p_value"]
    p_equal = d["null"]["equal"]["p_value"]
    # The test passes whether p_rank < 0.05 or not; it only checks the field exists.
    assert p_rank is not None and isinstance(p_rank, float)
    assert p_equal is not None and isinstance(p_equal, float)


# --- Determinism & no lookahead ---------------------------------------------

def test_determinism_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_signal_null_battery(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_signal_null_battery(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "battery must be byte-identical across reruns"


def test_no_lookahead_weights():
    """Weights at row t depend on data through t-1; OOS return at t not used."""
    mod = _import_harness()
    returns = load_prices(FIXTURE_CSV, benchmark="BTC", quality=False)
    for t in (220, 300):
        w_full = BABStrategy(
            benchmark="BTC", beta_window=BETA_WINDOW, min_observations=MIN_OBSERVATIONS,
            long_quantile=LONG_QUANTILE, short_quantile=SHORT_QUANTILE,
            transaction_costs=TRANSACTION_COSTS, beta_neutral=True, weighting="rank",
            rank_min_leg_beta=RANK_MIN_LEG_BETA, rank_max_gross=RANK_MAX_GROSS,
        ).run(returns_df=returns.iloc[:t + 2])
        w_trunc = BABStrategy(
            benchmark="BTC", beta_window=BETA_WINDOW, min_observations=MIN_OBSERVATIONS,
            long_quantile=LONG_QUANTILE, short_quantile=SHORT_QUANTILE,
            transaction_costs=TRANSACTION_COSTS, beta_neutral=True, weighting="rank",
            rank_min_leg_beta=RANK_MIN_LEG_BETA, rank_max_gross=RANK_MAX_GROSS,
        ).run(returns_df=returns.iloc[:t + 1])
        pd.testing.assert_series_equal(
            w_full.weights.iloc[t], w_trunc.weights.iloc[t]
        )


# --- Loader compatibility ----------------------------------------------------

def test_fixture_loads_via_load_prices():
    r = load_prices(str(FIXTURE_CSV), benchmark="BTC", quality=False)
    assert isinstance(r, pd.DataFrame)
    assert len(r) == EXPECTED_RETURN_ROWS
    assert "BTC" in r.columns
    assert "DEL" not in r.columns, "loader must drop the all-NaN DEL column"


# --- Ruff -------------------------------------------------------------------

def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(HARNESS_SCRIPT), str(__file__)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
