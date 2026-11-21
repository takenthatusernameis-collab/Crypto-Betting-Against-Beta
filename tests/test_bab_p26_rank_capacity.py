"""Acceptance tests for P26 WP2: capacity & turnover of the rank-weighted BAB book.

These tests assert sweep CORRECTNESS, not a forced capacity verdict. The
verdict (rank survives capacity / rank does not survive capacity) is
data-driven: on the no-alpha P25 WP0 fixture the rank premium is noise
(P26 WP0 NO-SIGNAL) and does not survive regime stress (P26 WP1 gate NOT
passed). These tests never assert the verdict must be one way or the other
— that is the hypothesis under test, not a correctness criterion. Instead
they verify each reported field is the boolean/numeric identity of the
underlying committed JSON.

Contract (from HANDOFF.md INITIAL TASK MESSAGE):

* scripts/bab_rank_capacity.py — deterministic seeded capacity sweep;
  run_capacity_sweep() returns a results dict and writes JSON + markdown
  artifacts; build_capacity_sweep() does no writes.
* research_state/bab_p26/rank_capacity.json — committed artifact.
* research_state/bab_p26/rank_capacity.md — rendered companion.
* Sweeps gross caps [1.0, 2.0, 3.0, 4.0] x rebalance freqs
  [daily, weekly, monthly] on identical causal folds from P25 WP0 fixture
  read-only (train 180 / test 40, rank_min_leg_beta=0.20,
  rank_max_gross=<cell cap>); per-cell OOS Sharpe/turnover/wealth/capacity
  break-even for rank vs equal; summary verdict; byte-identical
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
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "bab_rank_capacity.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p26"
JSON_ARTIFACT = ARTIFACT_DIR / "rank_capacity.json"
MD_ARTIFACT = ARTIFACT_DIR / "rank_capacity.md"

SEED = 20261120
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
TRAIN_WINDOW = 180
TEST_WINDOW = 40
N_FOLDS = 5
LONG_QUANTILE = 0.3
SHORT_QUANTILE = 0.3
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS_DEFAULT = 4.0
TRANSACTION_COSTS = 0.001
GROSS_CAPS = (1.0, 2.0, 3.0, 4.0)
REBALANCE_FREQS = ("daily", "weekly", "monthly")
DECIMALS = 6
WEIGHTINGS = ("equal", "rank")
BETA_NEUTRAL_TOL = 1e-2
EXPECTED_RETURN_ROWS = 398
EXPECTED_PRICE_ROWS = 399
WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
# P25 WP2 default-cell (gross_cap=4.0, daily) reference values, reproduced to 6 dp.
DEFAULT_RANK_SHARPE = 0.437311
DEFAULT_EQUAL_SHARPE = 0.170267
DEFAULT_DELTA_SHARPE = 0.267044


def _load_json() -> dict:
    return json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))


def _import_harness():
    spec = importlib.util.spec_from_file_location("bab_rank_capacity", HARNESS_SCRIPT)
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
    assert callable(getattr(mod, "run_capacity_sweep", None))
    assert callable(getattr(mod, "build_capacity_sweep", None))


def test_run_capacity_sweep_returns_dict():
    mod = _import_harness()
    payload = mod.run_capacity_sweep()
    assert isinstance(payload, dict)
    assert "aggregate" in payload
    assert "cells" in payload
    assert "provenance" in payload


# --- Schema & chartered metadata ----------------------------------------------

def test_schema_field():
    d = _load_json()
    assert d["schema"] == "bab_p26.rank_capacity/1"


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
    assert d["transaction_costs"] == TRANSACTION_COSTS
    assert d["synthetic"] is True
    assert d["weightings"] == list(WEIGHTINGS)
    assert isinstance(d["gross_caps"], list) and list(d["gross_caps"]) == list(GROSS_CAPS)
    assert isinstance(d["rebalance_freqs"], list)
    assert list(d["rebalance_freqs"]) == list(REBALANCE_FREQS)
    prov = d["provenance"]
    assert isinstance(prov, dict)
    assert isinstance(prov.get("provenance"), str) and len(prov["provenance"]) > 0
    assert isinstance(prov.get("gross_cap_sweep"), str) and len(prov["gross_cap_sweep"]) > 0
    assert isinstance(prov.get("rebalance_sweep"), str) and len(prov["rebalance_sweep"]) > 0
    cbe = prov.get("capacity_break_even_model")
    assert isinstance(cbe, str) and len(cbe) > 0
    assert isinstance(prov.get("verdict_rule"), str) and len(prov["verdict_rule"]) > 0


# --- Fixture provenance --------------------------------------------------------

def test_fixture_sha256_matches_wp0():
    d = _load_json()
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    assert d["fixture_sha256"] == actual
    assert d["fixture_sha256"] == WP0_FIXTURE_SHA256
    assert d["fixture_sha256"] == meta["fixture_sha256"]
    assert d["provenance"]["fixture_sha256"] == actual


# --- Cell structure ------------------------------------------------------------

def test_cells_count_matches_sweep():
    d = _load_json()
    assert len(d["aggregate"]["cells"]) == len(GROSS_CAPS) * len(REBALANCE_FREQS)


def test_aggregate_counts():
    d = _load_json()
    agg = d["aggregate"]
    assert agg["cells_evaluated"] == len(GROSS_CAPS) * len(REBALANCE_FREQS)
    assert agg["candidates_evaluated"] == (
        len(GROSS_CAPS) * len(REBALANCE_FREQS) * len(WEIGHTINGS) * N_FOLDS
    )


def test_each_cell_chartered_fields():
    d = _load_json()
    cell_fields = (
        "cell", "gross_cap", "rebalance_freq", "rank_max_gross", "weightings",
        "results", "delta", "capacity_break_even",
    )
    for cell in d["aggregate"]["cells"]:
        for field in cell_fields:
            assert field in cell, f"missing cell field {field}"
        assert cell["gross_cap"] in GROSS_CAPS
        assert cell["rebalance_freq"] in REBALANCE_FREQS
        assert cell["rank_max_gross"] == cell["gross_cap"]
        assert set(cell["results"].keys()) == set(WEIGHTINGS)
        assert set(cell["capacity_break_even"].keys()) == set(WEIGHTINGS)


def test_each_cell_results_fields():
    d = _load_json()
    for cell in d["aggregate"]["cells"]:
        for w in WEIGHTINGS:
            r = cell["results"][w]
            for field in ("mean_oos_sharpe", "mean_oos_turnover", "mean_oos_wealth",
                          "mean_portfolio_beta", "mean_nonflat_rows", "per_fold"):
                assert field in r, f"missing {field} in cell {cell['cell']}/{w}"
            assert len(r["per_fold"]) == N_FOLDS


def test_each_cell_delta_fields():
    d = _load_json()
    for cell in d["aggregate"]["cells"]:
        dlt = cell["delta"]
        for field in ("delta_oos_sharpe", "delta_oos_turnover", "delta_oos_wealth"):
            assert field in dlt, f"missing delta field {field} in cell {cell['cell']}"


def test_turnover_finite_per_cell():
    d = _load_json()
    for cell in d["aggregate"]["cells"]:
        for w in WEIGHTINGS:
            t = cell["results"][w]["mean_oos_turnover"]
            assert t is None or (math.isfinite(t) and t >= 0.0), (
                f"cell {cell['cell']}/{w} turnover non-finite or negative: {t}"
            )


def test_break_even_finite_or_none():
    d = _load_json()
    for cell in d["aggregate"]["cells"]:
        for w in WEIGHTINGS:
            be = cell["capacity_break_even"][w]
            assert be is None or math.isfinite(be), (
                f"cell {cell['cell']}/{w} break-even non-finite: {be}"
            )
            if be is not None:
                assert be > 0.0, f"cell {cell['cell']}/{w} break-even not positive: {be}"


def test_nonflat_rows_positive_per_fold():
    d = _load_json()
    for cell in d["aggregate"]["cells"]:
        for w in WEIGHTINGS:
            for f in cell["results"][w]["per_fold"]:
                assert f["nonflat_rows"] > 0, (
                    f"cell {cell['cell']}/{w} fold {f['fold']} has zero nonflat rows"
                )


def test_portfolio_beta_neutral_per_cell_per_fold():
    d = _load_json()
    for cell in d["aggregate"]["cells"]:
        for w in WEIGHTINGS:
            pb = cell["results"][w]["mean_portfolio_beta"]
            assert pb is None or abs(pb) < BETA_NEUTRAL_TOL, (
                f"cell {cell['cell']}/{w} mean portfolio_beta={pb} not beta-neutral"
            )
            for f in cell["results"][w]["per_fold"]:
                fpb = f["portfolio_beta"]
                assert fpb is None or abs(fpb) < BETA_NEUTRAL_TOL, (
                    f"cell {cell['cell']}/{w} fold {f['fold']} "
                    f"portfolio_beta={fpb} not beta-neutral"
                )


# --- Default cell reproduces P25 WP2 -------------------------------------------

def test_default_cell_matches_p25_wp2():
    d = _load_json()
    default = next(
        c for c in d["aggregate"]["cells"]
        if c["gross_cap"] == RANK_MAX_GROSS_DEFAULT and c["rebalance_freq"] == "daily"
    )
    rank = default["results"]["rank"]["mean_oos_sharpe"]
    equal = default["results"]["equal"]["mean_oos_sharpe"]
    assert rank is not None and abs(rank - DEFAULT_RANK_SHARPE) < 1e-6, (
        f"default cell rank sharpe {rank} != {DEFAULT_RANK_SHARPE}"
    )
    assert equal is not None and abs(equal - DEFAULT_EQUAL_SHARPE) < 1e-6, (
        f"default cell equal sharpe {equal} != {DEFAULT_EQUAL_SHARPE}"
    )
    dsharpe = default["delta"]["delta_oos_sharpe"]
    assert dsharpe is not None and abs(dsharpe - DEFAULT_DELTA_SHARPE) < 1e-6, (
        f"default cell delta sharpe {dsharpe} != {DEFAULT_DELTA_SHARPE}"
    )


# --- Verdict correctness (data-driven, never forced) --------------------------

def test_verdict_structure():
    d = _load_json()
    agg = d["aggregate"]
    for key in ("verdict", "rank_survives_capacity", "rank_beats_equal_default_cell",
                "default_cell_gross_cap", "default_cell_rebalance_freq"):
        assert key in agg, f"missing aggregate field {key}"
    assert agg["verdict"] in ("rank survives capacity", "rank does not survive capacity")
    assert isinstance(agg["rank_survives_capacity"], bool)
    assert isinstance(agg["rank_beats_equal_default_cell"], bool)
    assert agg["default_cell_gross_cap"] == RANK_MAX_GROSS_DEFAULT
    assert agg["default_cell_rebalance_freq"] == "daily"


def test_verdict_matches_default_cell_data():
    d = _load_json()
    agg = d["aggregate"]
    default = next(
        c for c in d["aggregate"]["cells"]
        if c["gross_cap"] == RANK_MAX_GROSS_DEFAULT and c["rebalance_freq"] == "daily"
    )
    rank = default["results"]["rank"]["mean_oos_sharpe"]
    equal = default["results"]["equal"]["mean_oos_sharpe"]
    expected = rank is not None and equal is not None and rank > equal
    assert agg["rank_beats_equal_default_cell"] == expected, (
        f"rank_beats_equal={agg['rank_beats_equal_default_cell']} != expected {expected}"
    )
    assert agg["rank_survives_capacity"] == expected, (
        f"rank_survives={agg['rank_survives_capacity']} != expected {expected}"
    )
    expected_verdict = "rank survives capacity" if expected else "rank does not survive capacity"
    assert agg["verdict"] == expected_verdict, (
        f"verdict={agg['verdict']} != expected {expected_verdict}"
    )


# --- Rank safety valve unchanged ----------------------------------------------

def test_rank_min_leg_beta_unchanged():
    d = _load_json()
    assert d["rank_min_leg_beta"] == RANK_MIN_LEG_BETA
    assert d["aggregate"]["rank_min_leg_beta"] == RANK_MIN_LEG_BETA


# --- Determinism ---------------------------------------------------------------

def test_build_deterministic_byte_identical():
    mod = _import_harness()
    p1 = json.dumps(mod.build_capacity_sweep(), sort_keys=True).encode("utf-8")
    p2 = json.dumps(mod.build_capacity_sweep(), sort_keys=True).encode("utf-8")
    assert p1 == p2, "capacity sweep must be byte-identical across reruns"


def test_cli_rerun_byte_identical():
    out1 = subprocess.run(
        [sys.executable, str(HARNESS_SCRIPT)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert out1.returncode == 0, f"CLI failed: {out1.stderr}"
    json_before = JSON_ARTIFACT.read_bytes()
    out2 = subprocess.run(
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
            rank_min_leg_beta=RANK_MIN_LEG_BETA, rank_max_gross=RANK_MAX_GROSS_DEFAULT,
            rebalance_freq="daily",
        ).run(returns_df=returns.iloc[:t + 2])
        w_trunc = BABStrategy(
            benchmark="BTC", beta_window=BETA_WINDOW, min_observations=MIN_OBSERVATIONS,
            long_quantile=LONG_QUANTILE, short_quantile=SHORT_QUANTILE,
            transaction_costs=TRANSACTION_COSTS, beta_neutral=True, weighting="rank",
            rank_min_leg_beta=RANK_MIN_LEG_BETA, rank_max_gross=RANK_MAX_GROSS_DEFAULT,
            rebalance_freq="daily",
        ).run(returns_df=returns.iloc[:t + 1])
        pd.testing.assert_series_equal(w_full.weights.iloc[t], w_trunc.weights.iloc[t])


# --- Loader compatibility ------------------------------------------------------

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
