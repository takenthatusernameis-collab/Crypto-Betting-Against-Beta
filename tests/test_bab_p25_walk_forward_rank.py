"""Acceptance tests for P25 WP1: rank-weighted walk-forward harness.

These tests are the claim that ``scripts/bab_walk_forward_rank.py`` produces a
deterministic, seeded, no-network out-of-sample rank-weighted BAB evaluation on
the P25 WP0 wide synthetic universe fixture, proving rank weighting is
empirically evaluable OOS and enabling evidence-based promotion of
``weighting="rank"`` from the equal-weight default.

They prove the mechanical contract the P25 spec declares:

* the harness script runs standalone and produces the JSON + markdown artifacts;
* the JSON schema carries the chartered run metadata (seed, windows, quantiles,
  rank safety valves, fixture SHA256 provenance, synthetic flag);
* the fixture SHA256 references the P25 WP0 wide-universe fixture;
* every fold produces OOS non-flat rank rows (> 0);
* every fold is beta-neutral (|portfolio beta| < 1e-2);
* the recovered planted beta spread is positive (long low-beta, short high-beta);
* seed determinism: two runs produce byte-identical JSON;
* no lookahead: the weight used for a return depends on data through t-1 only;
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
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_walk_forward_rank.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p25"
JSON_ARTIFACT = ARTIFACT_DIR / "walk_forward_rank.json"
MD_ARTIFACT = ARTIFACT_DIR / "walk_forward_rank.md"

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

CHARTERED_CONFIG = dict(
    benchmark="BTC",
    beta_window=BETA_WINDOW,
    min_observations=60,
    long_quantile=LONG_QUANTILE,
    short_quantile=SHORT_QUANTILE,
    transaction_costs=0.001,
    beta_neutral=True,
    weighting="rank",
    rank_min_leg_beta=RANK_MIN_LEG_BETA,
    rank_max_gross=RANK_MAX_GROSS,
)


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_harness():
    spec = importlib.util.spec_from_file_location("bab_walk_forward_rank", HARNESS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- Existence & entry point -------------------------------------------------

def test_harness_script_exists():
    assert HARNESS_SCRIPT.is_file(), f"missing {HARNESS_SCRIPT}"


def test_json_artifact_exists():
    assert JSON_ARTIFACT.is_file(), f"missing {JSON_ARTIFACT}"


def test_md_artifact_exists():
    assert MD_ARTIFACT.is_file(), f"missing {MD_ARTIFACT}"


def test_harness_has_run_walk_forward_rank():
    mod = _import_harness()
    assert callable(getattr(mod, "run_walk_forward_rank", None))
    assert callable(getattr(mod, "build_walk_forward_rank", None))


def test_run_walk_forward_rank_returns_dict():
    mod = _import_harness()
    payload = mod.run_walk_forward_rank()
    assert isinstance(payload, dict)
    assert "folds" in payload and "aggregate" in payload


# --- Schema & chartered metadata -------------------------------------------

def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p25.walk_forward_rank/1"


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
    assert d["synthetic"] is True
    assert isinstance(d["fixture_sha256"], str) and len(d["fixture_sha256"]) == 64
    prov = d["provenance"]
    assert isinstance(prov, dict)
    assert isinstance(prov.get("provenance"), str) and len(prov["provenance"]) > 0


def test_fixture_sha256_matches_wp0():
    d = _load_json()
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    assert d["fixture_sha256"] == actual, "JSON fixture_sha256 must match the actual fixture"
    assert d["fixture_sha256"] == meta["fixture_sha256"], (
        "JSON must reference the WP0 meta sidecar hash"
    )


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


# --- OOS empirical evaluability -------------------------------------------

def test_oos_nonflat_rows_per_fold():
    d = _load_json()
    for fold in d["folds"]:
        assert fold["nonflat_rows"] > 0, f"fold {fold['fold']} has no OOS rank rows"


def test_beta_neutrality_per_fold():
    d = _load_json()
    for fold in d["folds"]:
        pb = fold["portfolio_beta"]
        assert pb is not None, f"fold {fold['fold']} portfolio beta missing"
        assert abs(pb) < BETA_NEUTRAL_TOL, (
            f"fold {fold['fold']} portfolio beta {pb} not beta-neutral"
        )


def test_portfolio_beta_per_row_strict():
    mod = _import_harness()
    returns = load_prices(FIXTURE_CSV, benchmark="BTC", quality=False)
    fold = _load_json()["folds"][2]
    test_start, test_end = fold["test_start"], fold["test_end"]
    result = BABStrategy(**CHARTERED_CONFIG).run(returns_df=returns.iloc[:test_end])
    w = result.weights.iloc[test_start:test_end]
    b = result.betas.iloc[test_start:test_end]
    common = w.columns.intersection(b.columns)
    wv = w[common].to_numpy(dtype=float)
    bv = b[common].to_numpy(dtype=float)
    finite = np.isfinite(bv)
    wv = np.where(finite, wv, 0.0)
    bv = np.where(finite, bv, 0.0)
    gross = np.abs(wv).sum(axis=1)
    mask = gross > 1e-18
    pb = np.full(len(w), np.nan)
    pb[mask] = (wv[mask] * bv[mask]).sum(axis=1) / gross[mask]
    finite_pb = pb[np.isfinite(pb)]
    assert len(finite_pb) > 0
    assert np.abs(finite_pb).max() < BETA_NEUTRAL_TOL, "per-row portfolio beta not neutral"


def test_beta_spread_positive():
    d = _load_json()
    spreads = [fold["beta_spread"] for fold in d["folds"] if fold["beta_spread"] is not None]
    assert len(spreads) == N_FOLDS, "every fold must recover a beta spread"
    assert all(s > 0.0 for s in spreads), "beta spread must be positive (short high, long low)"
    agg = d["aggregate"]["mean_beta_spread"]
    assert agg is not None and agg > 0.0


def test_long_short_leg_ordering():
    d = _load_json()
    for fold in d["folds"]:
        lb, sb = fold["long_leg_beta"], fold["short_leg_beta"]
        assert lb is not None and sb is not None
        assert lb < sb, "long leg must be lower beta than short leg"


def test_oos_sharpe_finite():
    d = _load_json()
    for fold in d["folds"]:
        s = fold["oos_sharpe"]
        assert s is None or (isinstance(s, float) and np.isfinite(s))


# --- Determinism & no lookahead -------------------------------------------

def test_determinism_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_walk_forward_rank(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_walk_forward_rank(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "walk-forward must be byte-identical across reruns"


def test_cli_rerun_byte_identical():
    sha1 = hashlib.sha256(JSON_ARTIFACT.read_bytes()).hexdigest()
    subprocess.check_output([sys.executable, str(HARNESS_SCRIPT)], cwd=REPO_ROOT)
    sha2 = hashlib.sha256(JSON_ARTIFACT.read_bytes()).hexdigest()
    assert sha1 == sha2, "CLI rerun must produce byte-identical artifact"


def test_no_lookahead_weights():
    mod = _import_harness()
    returns = load_prices(FIXTURE_CSV, benchmark="BTC", quality=False)
    result = BABStrategy(**CHARTERED_CONFIG).run(returns_df=returns.iloc[:300])
    weights = result.weights
    for t in (270, 290):
        w_full = weights.iloc[t]
        truncated = BABStrategy(**CHARTERED_CONFIG).run(returns_df=returns.iloc[:t + 1])
        w_trunc = truncated.weights.iloc[-1]
        pd.testing.assert_series_equal(w_full, w_trunc)


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
    for key in (
        "mean_oos_sharpe",
        "median_oos_sharpe",
        "fraction_positive_oos_sharpe",
        "total_oos_rows",
        "mean_oos_vol",
        "mean_oos_max_drawdown",
        "mean_oos_turnover",
        "mean_portfolio_beta",
        "mean_beta_spread",
        "mean_nonflat_rows",
        "candidates_evaluated",
        "folds",
    ):
        assert key in agg, f"aggregate missing key {key}"
    assert agg["candidates_evaluated"] == N_FOLDS


def test_fold_fields_present():
    d = _load_json()
    for fold in d["folds"]:
        for key in (
            "fold",
            "train_start",
            "train_end",
            "test_start",
            "test_end",
            "n_train",
            "n_test",
            "oos_sharpe",
            "oos_vol",
            "oos_max_drawdown",
            "oos_turnover",
            "oos_realized_beta",
            "portfolio_beta",
            "oos_wealth",
            "beta_spread",
            "long_leg_beta",
            "short_leg_beta",
            "nonflat_rows",
        ):
            assert key in fold, f"fold missing key {key}"


# --- Ruff -------------------------------------------------------------------

def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(HARNESS_SCRIPT), str(__file__)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
