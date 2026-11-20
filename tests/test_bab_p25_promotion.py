"""Acceptance tests for P25 WP2: equal-vs-rank out-of-sample promotion bake-off.

These tests are the claim that ``scripts/bab_promotion_bakeoff.py`` runs the
equal-weight default and the Frazzini-Pedersen rank-weighted BAB book on
identical causal walk-forward folds of the P25 WP0 wide synthetic universe
fixture, producing per-fold OOS comparison evidence (Sharpe, beta neutrality,
turnover, wealth) plus a delta Sharpe for the WP3 promote/no-promote decision.

They prove the mechanical contract the P25 spec declares:

* the bake-off script runs standalone and produces the JSON + markdown artifacts;
* both ``weighting="equal"`` and ``weighting="rank"`` run on identical folds;
* the JSON schema carries the chartered run metadata (seed, windows, quantiles,
  rank safety valves, weightings, fixture SHA256 provenance, synthetic flag);
* the fixture SHA256 references the P25 WP0 wide-universe fixture;
* every fold produces OOS non-flat rows (> 0) for both weightings;
* every fold is beta-neutral (|portfolio beta| < 1e-2) for both weightings;
* the recovered planted beta spread is positive for both weightings;
* seed determinism: two runs produce byte-identical JSON;
* CLI rerun produces byte-identical artifact;
* no lookahead: the weight used for a return depends on data through t-1 only;
* delta Sharpe (rank minus equal) is finite and reported in the aggregate;
* zero ruff errors on new files;
* 20+ acceptance tests pass.
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

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
FIXTURE_META = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
BAKEOFF_SCRIPT = REPO_ROOT / "scripts" / "bab_promotion_bakeoff.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p25"
JSON_ARTIFACT = ARTIFACT_DIR / "promotion_bakeoff.json"
MD_ARTIFACT = ARTIFACT_DIR / "promotion_bakeoff.md"

SEED = 20261120
BETA_WINDOW = 90
TRAIN_WINDOW = 180
TEST_WINDOW = 40
N_FOLDS = 5
LONG_QUANTILE = 0.3
SHORT_QUANTILE = 0.3
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
BETA_NEUTRAL_TOL = 1e-2
EXPECTED_RETURN_ROWS = 398
EXPECTED_PRICE_ROWS = 399
TOTAL_OOS_ROWS = N_FOLDS * TEST_WINDOW
WEIGHTINGS = ("equal", "rank")

CHARTERED_CONFIG = dict(
    benchmark="BTC",
    beta_window=BETA_WINDOW,
    min_observations=60,
    long_quantile=LONG_QUANTILE,
    short_quantile=SHORT_QUANTILE,
    transaction_costs=0.001,
    beta_neutral=True,
    rank_min_leg_beta=RANK_MIN_LEG_BETA,
    rank_max_gross=RANK_MAX_GROSS,
)


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_bakeoff():
    spec = importlib.util.spec_from_file_location("bab_promotion_bakeoff", BAKEOFF_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- Existence & entry point -------------------------------------------------

def test_bakeoff_script_exists():
    assert BAKEOFF_SCRIPT.is_file(), f"missing {BAKEOFF_SCRIPT}"


def test_json_artifact_exists():
    assert JSON_ARTIFACT.is_file(), f"missing {JSON_ARTIFACT}"


def test_md_artifact_exists():
    assert MD_ARTIFACT.is_file(), f"missing {MD_ARTIFACT}"


def test_bakeoff_has_run_and_build():
    mod = _import_bakeoff()
    assert callable(getattr(mod, "run_promotion_bakeoff", None))
    assert callable(getattr(mod, "build_promotion_bakeoff", None))


def test_run_promotion_bakeoff_returns_dict():
    mod = _import_bakeoff()
    payload = mod.run_promotion_bakeoff()
    assert isinstance(payload, dict)
    assert "folds" in payload and "aggregate" in payload


# --- Schema & chartered metadata -------------------------------------------

def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p25.promotion_bakeoff/1"


def test_metadata_fields_chartered():
    d = _load_json()
    assert d["seed"] == SEED
    assert d["n_folds"] == N_FOLDS
    assert d["train_window"] == TRAIN_WINDOW
    assert d["test_window"] == TEST_WINDOW
    assert d["beta_window"] == BETA_WINDOW
    assert d["long_quantile"] == LONG_QUANTILE
    assert d["short_quantile"] == SHORT_QUANTILE
    assert d["rank_min_leg_beta"] == RANK_MIN_LEG_BETA
    assert d["rank_max_gross"] == RANK_MAX_GROSS
    assert d["weightings"] == list(WEIGHTINGS)
    assert d["synthetic"] is True
    assert isinstance(d["fixture_sha256"], str) and len(d["fixture_sha256"]) == 64
    prov = d["provenance"]
    assert isinstance(prov, dict)
    assert isinstance(prov.get("provenance"), str) and len(prov["provenance"]) > 0
    assert prov.get("no_lookahead")


def test_fixture_sha256_matches_wp0():
    d = _load_json()
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    assert d["fixture_sha256"] == actual, "JSON fixture_sha256 must match the actual fixture"
    assert d["fixture_sha256"] == meta["fixture_sha256"], (
        "JSON must reference the WP0 meta sidecar hash"
    )


def test_provenance_declares_both_weightings():
    d = _load_json()
    prov = d["provenance"]
    assert prov.get("weightings") == list(WEIGHTINGS)


# --- Fold structure & windows ----------------------------------------------

def test_fold_count_and_windows():
    d = _load_json()
    assert len(d["folds"]) == N_FOLDS
    for k, fold in enumerate(d["folds"]):
        assert fold["fold"] == k
        assert fold["train_start"] == 0
        assert fold["train_end"] == TRAIN_WINDOW + TEST_WINDOW * k
        assert fold["test_start"] == fold["train_end"]
        assert fold["test_end"] == fold["test_start"] + TEST_WINDOW
        assert fold["n_train"] == fold["train_end"]
        assert fold["n_test"] == TEST_WINDOW


def test_total_oos_rows():
    d = _load_json()
    assert d["aggregate"]["total_oos_rows"] == TOTAL_OOS_ROWS


# --- Both weightings run on identical folds --------------------------------

def test_both_weightings_present_in_every_fold():
    d = _load_json()
    for fold in d["folds"]:
        for w in WEIGHTINGS:
            assert w in fold, f"fold {fold['fold']} missing weighting {w}"
            for key in (
                "oos_sharpe", "oos_vol", "oos_max_drawdown", "oos_turnover",
                "oos_realized_beta", "oos_wealth", "portfolio_beta",
                "beta_spread", "long_leg_beta", "short_leg_beta", "nonflat_rows",
            ):
                assert key in fold[w], f"fold {fold['fold']} {w} missing {key}"


def test_identical_folds_across_weightings():
    d = _load_json()
    for fold in d["folds"]:
        assert fold["n_test"] == TEST_WINDOW
        assert fold["equal"]["oos_wealth"] is not None
        assert fold["rank"]["oos_wealth"] is not None


# --- OOS empirical evaluability -------------------------------------------

def test_oos_nonflat_rows_per_fold_per_weighting():
    d = _load_json()
    for fold in d["folds"]:
        for w in WEIGHTINGS:
            assert fold[w]["nonflat_rows"] > 0, (
                f"fold {fold['fold']} {w} has no OOS rows"
            )


def test_beta_neutrality_per_fold_per_weighting():
    d = _load_json()
    for fold in d["folds"]:
        for w in WEIGHTINGS:
            pb = fold[w]["portfolio_beta"]
            assert pb is not None, f"fold {fold['fold']} {w} portfolio beta missing"
            assert abs(pb) < BETA_NEUTRAL_TOL, (
                f"fold {fold['fold']} {w} portfolio beta {pb} not beta-neutral"
            )


def test_beta_spread_positive():
    d = _load_json()
    for fold in d["folds"]:
        for w in WEIGHTINGS:
            spread = fold[w]["beta_spread"]
            assert spread is not None, f"fold {fold['fold']} {w} missing beta spread"
            assert spread > 0.0, (
                f"fold {fold['fold']} {w} beta spread must be positive"
            )
    agg = d["aggregate"]
    assert agg["equal"]["mean_beta_spread"] is not None and agg["equal"]["mean_beta_spread"] > 0.0
    assert agg["rank"]["mean_beta_spread"] is not None and agg["rank"]["mean_beta_spread"] > 0.0


def test_long_short_leg_ordering():
    d = _load_json()
    for fold in d["folds"]:
        for w in WEIGHTINGS:
            lb, sb = fold[w]["long_leg_beta"], fold[w]["short_leg_beta"]
            assert lb is not None and sb is not None
            assert lb < sb, f"fold {fold['fold']} {w} long leg must be lower beta than short leg"


def test_oos_sharpe_finite():
    d = _load_json()
    for fold in d["folds"]:
        for w in WEIGHTINGS:
            s = fold[w]["oos_sharpe"]
            assert s is None or (isinstance(s, float) and np.isfinite(s))


# --- Delta -----------------------------------------------------------------

def test_delta_sharpe_finite_and_reported():
    d = _load_json()
    delta = d["aggregate"]["delta_mean_oos_sharpe"]
    assert delta is not None and isinstance(delta, float) and np.isfinite(delta)
    equal_mean = d["aggregate"]["equal"]["mean_oos_sharpe"]
    rank_mean = d["aggregate"]["rank"]["mean_oos_sharpe"]
    assert delta == round(rank_mean - equal_mean, 6)


def test_delta_per_fold_present():
    d = _load_json()
    for fold in d["folds"]:
        dlt = fold["delta"]
        for key in ("oos_sharpe", "oos_wealth", "portfolio_beta", "oos_turnover", "beta_spread"):
            assert key in dlt, f"fold {fold['fold']} delta missing {key}"


# --- Determinism & no lookahead -------------------------------------------

def test_determinism_byte_identical():
    mod = _import_bakeoff()
    p1 = json.dumps(mod.build_promotion_bakeoff(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_promotion_bakeoff(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "bake-off must be byte-identical across reruns"


def test_cli_rerun_byte_identical():
    sha1 = hashlib.sha256(JSON_ARTIFACT.read_bytes()).hexdigest()
    subprocess.check_output([sys.executable, str(BAKEOFF_SCRIPT)], cwd=REPO_ROOT)
    sha2 = hashlib.sha256(JSON_ARTIFACT.read_bytes()).hexdigest()
    assert sha1 == sha2, "CLI rerun must produce byte-identical artifact"


def test_no_lookahead_weights_both_weightings():
    mod = _import_bakeoff()
    returns = load_prices(FIXTURE_CSV, benchmark="BTC", quality=False)
    horizon = 300
    for weighting in WEIGHTINGS:
        cfg = dict(CHARTERED_CONFIG, weighting=weighting)
        w_full = BABStrategy(**cfg).run(returns_df=returns.iloc[:horizon]).weights
        for t in (270, 290):
            w_full_row = w_full.iloc[t]
            w_trunc = BABStrategy(**cfg).run(returns_df=returns.iloc[:t + 1]).weights.iloc[-1]
            pd.testing.assert_series_equal(w_full_row, w_trunc)


# --- Loader compatibility ---------------------------------------------------

def test_fixture_loads_via_load_prices():
    r = load_prices(str(FIXTURE_CSV), benchmark="BTC", quality=False)
    assert isinstance(r, pd.DataFrame)
    assert len(r) == EXPECTED_RETURN_ROWS
    assert "BTC" in r.columns
    assert "DEL" not in r.columns, "loader must drop the all-NaN DEL column"


# --- Aggregate fields -------------------------------------------------------

def test_aggregate_fields_present():
    d = _load_json()
    agg = d["aggregate"]
    equal_agg = agg["equal"]
    rank_agg = agg["rank"]
    for weighting_agg in (equal_agg, rank_agg):
        for key in (
            "mean_oos_sharpe",
            "mean_oos_vol",
            "mean_oos_max_drawdown",
            "mean_oos_turnover",
            "mean_oos_realized_beta",
            "mean_oos_wealth",
            "mean_portfolio_beta",
            "mean_beta_spread",
            "mean_long_leg_beta",
            "mean_short_leg_beta",
            "mean_nonflat_rows",
        ):
            assert key in weighting_agg, f"aggregate weighting missing key {key}"
    for key in (
        "delta_mean_oos_sharpe",
        "rank_beta_neutral_folds",
        "total_oos_rows",
        "folds",
        "candidates_evaluated",
        "weightings",
    ):
        assert key in agg, f"aggregate missing key {key}"
    assert agg["weightings"] == list(WEIGHTINGS)
    assert agg["candidates_evaluated"] == N_FOLDS * len(WEIGHTINGS)
    assert agg["rank_beta_neutral_folds"] == N_FOLDS
    assert agg["total_oos_rows"] == TOTAL_OOS_ROWS


def test_fold_fields_present():
    d = _load_json()
    for fold in d["folds"]:
        for key in (
            "fold", "train_start", "train_end", "test_start", "test_end",
            "n_train", "n_test", "delta",
        ):
            assert key in fold, f"fold missing key {key}"
        for w in WEIGHTINGS:
            for key in (
                "oos_sharpe", "oos_vol", "oos_max_drawdown", "oos_turnover",
                "oos_realized_beta", "oos_wealth", "portfolio_beta",
                "beta_spread", "long_leg_beta", "short_leg_beta", "nonflat_rows",
            ):
                assert key in fold[w], f"fold {fold['fold']} {w} missing {key}"


# --- Ruff -------------------------------------------------------------------

def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(BAKEOFF_SCRIPT), str(__file__)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
