"""Acceptance tests for P26 WP1: regime-conditional rank stress of rank-weighted BAB.

These tests assert regime-stress CORRECTNESS, not a forced gate outcome. The
falsification gate (rank > 0 in calm AND rank < equal in stress) is
data-driven: on the no-alpha P25 WP0 fixture the rank premium need not survive
stress. These tests never assert the gate must pass — that is the hypothesis
under test, not a correctness criterion. Instead they verify that each
assertion field is the boolean identity of the underlying numbers.

Contract (from HANDOFF.md INITIAL TASK MESSAGE):

* scripts/bab_p26_regime_stress.py — deterministic seeded regime stress;
  run_regime_stress() returns a results dict and writes JSON + markdown
  artifacts; build_regime_stress() does no writes.
* research_state/bab_p26/regime_stress.json — committed artifact.
* research_state/bab_p26/regime_stress.md — rendered companion.
* Splits the P25 WP0 wide fixture into calm vs stress regimes by 60-day
  rolling BTC volatility (median split), runs P25 WP2 rank walk-forward per
  regime (train 180 / test 40, rank_min_leg_beta=0.20, rank_max_gross=4.0),
  records regime means/deltas/pass-fail per assertion; byte-identical
  deterministic JSON + markdown; fixture SHA256 provenance matches P25 WP0;
  20+ acceptance tests; zero ruff errors; green full gate.
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
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_p26_regime_stress.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p26"
JSON_ARTIFACT = ARTIFACT_DIR / "regime_stress.json"
MD_ARTIFACT = ARTIFACT_DIR / "regime_stress.md"

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
VOL_WINDOW = 60
DECIMALS = 6
WEIGHTINGS = ("equal", "rank")
REGIMES = ("calm", "stress")
BETA_NEUTRAL_TOL = 1e-2
EXPECTED_RETURN_ROWS = 398
EXPECTED_PRICE_ROWS = 399
WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_harness():
    spec = importlib.util.spec_from_file_location("bab_p26_regime_stress", HARNESS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- Existence & entry points -------------------------------------------------

def test_harness_script_exists():
    assert HARNESS_SCRIPT.is_file(), f"missing {HARNESS_SCRIPT}"


def test_json_artifact_exists():
    assert JSON_ARTIFACT.is_file(), f"missing {JSON_ARTIFACT}"


def test_md_artifact_exists():
    assert MD_ARTIFACT.is_file(), f"missing {MD_ARTIFACT}"


def test_harness_has_entry_points():
    mod = _import_harness()
    assert callable(getattr(mod, "run_regime_stress", None))
    assert callable(getattr(mod, "build_regime_stress", None))


def test_run_regime_stress_returns_dict():
    mod = _import_harness()
    payload = mod.run_regime_stress()
    assert isinstance(payload, dict)
    assert "regimes" in payload
    assert "assertions" in payload
    assert "provenance" in payload


# --- Schema & chartered metadata ---------------------------------------------

def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p26.regime_stress/1"


def test_metadata_fields_chartered():
    d = _load_json()
    assert d["seed"] == SEED
    assert d["n_folds"] == N_FOLDS
    assert d["train_window"] == TRAIN_WINDOW
    assert d["test_window"] == TEST_WINDOW
    assert d["beta_window"] == BETA_WINDOW
    assert d["min_observations"] == MIN_OBSERVATIONS
    assert d["vol_window"] == VOL_WINDOW
    assert d["long_quantile"] == LONG_QUANTILE
    assert d["short_quantile"] == SHORT_QUANTILE
    assert d["rank_min_leg_beta"] == RANK_MIN_LEG_BETA
    assert d["rank_max_gross"] == RANK_MAX_GROSS
    assert d["transaction_costs"] == TRANSACTION_COSTS
    assert d["synthetic"] is True
    assert d["weightings"] == list(WEIGHTINGS)
    assert d["provenance"]["regimes"] == list(REGIMES)
    assert isinstance(d["fixture_sha256"], str) and len(d["fixture_sha256"]) == 64
    prov = d["provenance"]
    assert isinstance(prov, dict)
    assert isinstance(prov.get("provenance"), str) and len(prov["provenance"]) > 0
    assert isinstance(prov.get("regime_split_rule"), str) and len(prov["regime_split_rule"]) > 0
    assert isinstance(prov.get("falsification_gate"), str) and len(prov["falsification_gate"]) > 0


# --- Fixture provenance --------------------------------------------------------

def test_fixture_sha256_matches_wp0():
    d = _load_json()
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    assert d["fixture_sha256"] == actual
    assert d["fixture_sha256"] == WP0_FIXTURE_SHA256
    assert d["fixture_sha256"] == meta["fixture_sha256"]
    assert d["provenance"]["fixture_sha256"] == actual


# --- Regime structure ---------------------------------------------------------

def test_regimes_have_both_weightings():
    d = _load_json()
    for regime_name in REGIMES:
        reg = d["regimes"][regime_name]
        assert set(reg.keys()) >= {"regime", "n_folds_assigned", "folds_assigned", "equal", "rank"}
        assert reg["regime"] == regime_name
        for w in WEIGHTINGS:
            assert w in reg
            assert "mean_oos_sharpe" in reg[w]
            assert "per_fold" in reg[w]


def test_calm_regime_has_folds():
    d = _load_json()
    calm = d["regimes"]["calm"]
    assert calm["n_folds_assigned"] >= 1
    assert len(calm["folds_assigned"]) == calm["n_folds_assigned"]
    assert len(calm["equal"]["per_fold"]) == calm["n_folds_assigned"]
    assert len(calm["rank"]["per_fold"]) == calm["n_folds_assigned"]


def test_stress_regime_has_folds():
    d = _load_json()
    stress = d["regimes"]["stress"]
    assert stress["n_folds_assigned"] >= 1
    assert len(stress["folds_assigned"]) == stress["n_folds_assigned"]
    assert len(stress["equal"]["per_fold"]) == stress["n_folds_assigned"]
    assert len(stress["rank"]["per_fold"]) == stress["n_folds_assigned"]


def test_all_folds_assigned_at_most_once():
    d = _load_json()
    assigned = []
    for regime_name in REGIMES:
        assigned.extend(d["regimes"][regime_name]["folds_assigned"])
    assert len(assigned) == len(set(assigned)), "a fold must not be assigned to two regimes"
    assert set(assigned) <= set(range(N_FOLDS))


def test_per_fold_has_required_fields():
    d = _load_json()
    for regime_name in REGIMES:
        for w in WEIGHTINGS:
            for f in d["regimes"][regime_name][w]["per_fold"]:
                for field in ("fold", "test_start", "test_end", "train_end", "regime",
                              "oos_sharpe", "portfolio_beta", "nonflat_rows"):
                    assert field in f, f"missing {field} in {regime_name}/{w} fold {f.get('fold')}"
                assert f["regime"] == regime_name
                assert f["nonflat_rows"] > 0, f"fold {f['fold']} has zero nonflat rows"


def test_portfolio_beta_neutral_per_fold():
    d = _load_json()
    for regime_name in REGIMES:
        for w in WEIGHTINGS:
            for f in d["regimes"][regime_name][w]["per_fold"]:
                pb = f["portfolio_beta"]
                assert pb is None or abs(pb) < BETA_NEUTRAL_TOL, (
                    f"{regime_name}/{w} fold {f['fold']}: portfolio_beta={pb} not beta-neutral"
                )


# --- Assertion correctness (data-driven, never forced) ------------------------

def test_assertions_structure():
    d = _load_json()
    a = d["assertions"]
    for key in ("assertion_a_calm_rank_positive",
                "assertion_b_stress_rank_below_equal",
                "falsification_gate_passed",
                "calm_rank_mean_oos_sharpe",
                "stress_rank_mean_oos_sharpe",
                "stress_equal_mean_oos_sharpe"):
        assert key in a, f"missing assertion field {key}"
    assert isinstance(a["assertion_a_calm_rank_positive"], bool)
    assert isinstance(a["assertion_b_stress_rank_below_equal"], bool)
    assert isinstance(a["falsification_gate_passed"], bool)


def test_assertion_a_matches_data():
    """Assertion A must equal (calm rank mean OOS Sharpe > 0)."""
    d = _load_json()
    calm = d["regimes"]["calm"]
    rank_sharpe = calm["rank"]["mean_oos_sharpe"]
    a = d["assertions"]
    expected = rank_sharpe is not None and rank_sharpe > 0
    assert a["assertion_a_calm_rank_positive"] == expected, (
        f"assertion_a={a['assertion_a_calm_rank_positive']} != expected {expected}"
    )
    assert a["calm_rank_mean_oos_sharpe"] == rank_sharpe


def test_assertion_b_matches_data():
    """Assertion B must equal (stress rank mean OOS Sharpe < equal mean OOS Sharpe)."""
    d = _load_json()
    stress = d["regimes"]["stress"]
    rank_sharpe = stress["rank"]["mean_oos_sharpe"]
    equal_sharpe = stress["equal"]["mean_oos_sharpe"]
    a = d["assertions"]
    expected = (
        rank_sharpe is not None and equal_sharpe is not None and rank_sharpe < equal_sharpe
    )
    assert a["assertion_b_stress_rank_below_equal"] == expected, (
        f"assertion_b={a['assertion_b_stress_rank_below_equal']} != expected {expected}"
    )
    assert a["stress_rank_mean_oos_sharpe"] == rank_sharpe
    assert a["stress_equal_mean_oos_sharpe"] == equal_sharpe


def test_falsification_gate_matches_assertions():
    d = _load_json()
    a = d["assertions"]
    expected = a["assertion_a_calm_rank_positive"] and a["assertion_b_stress_rank_below_equal"]
    assert a["falsification_gate_passed"] == expected, (
        f"gate={a['falsification_gate_passed']} != A&B={expected}"
    )


# --- Determinism ---------------------------------------------------------------

def test_build_deterministic_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_regime_stress(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_regime_stress(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "regime stress must be byte-identical across reruns"


def test_cli_rerun_byte_identical():
    import subprocess as _sp
    out1 = _sp.run(
        [sys.executable, str(HARNESS_SCRIPT)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert out1.returncode == 0, f"CLI failed: {out1.stderr}"
    json_before = JSON_ARTIFACT.read_bytes()
    out2 = _sp.run(
        [sys.executable, str(HARNESS_SCRIPT)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert out2.returncode == 0, f"CLI rerun failed: {out2.stderr}"
    json_after = JSON_ARTIFACT.read_bytes()
    assert json_before == json_after, "CLI rerun must produce byte-identical JSON"


# --- No lookahead --------------------------------------------------------------

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
        pd.testing.assert_series_equal(w_full.weights.iloc[t], w_trunc.weights.iloc[t])


# --- Loader compatibility -------------------------------------------------------

def test_fixture_loads_via_load_prices():
    r = load_prices(str(FIXTURE_CSV), benchmark="BTC", quality=False)
    assert isinstance(r, pd.DataFrame)
    assert len(r) == EXPECTED_RETURN_ROWS
    assert "BTC" in r.columns
    assert "DEL" not in r.columns, "loader must drop the all-NaN DEL column"


# --- Ruff ----------------------------------------------------------------------

def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(HARNESS_SCRIPT), str(__file__)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
