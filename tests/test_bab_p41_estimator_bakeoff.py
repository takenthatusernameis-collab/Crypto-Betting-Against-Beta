"""Acceptance tests for P41 WP1: estimator bakeoff under non-Gaussian idio.

These tests pin the committed ``research_state/bab_p41/estimator_bakeoff.json``
artifact to its deterministic generator and assert the scientific contract:

  * five DGPs present (GAUSSIAN_IID, STUDENT_T, REGIME_SWITCH, JUMP_DIFFUSION,
    STOCHASTIC_VOL), 8 seeds each, 4 estimators each = 160 cells (32 per DGP);
  * every cell is status ``ok`` / ``error`` / ``neutrality_violation``; every
    ``ok`` cell passes the three neutrality invariants (model beta <= 1e-3,
    dollar <= 1e-9, |realized beta| <= 0.15);
  * DSR/PSR + tail metrics computed per seed cell, deflated over
    n_trials_total read-only from P38 WP1;
  * the artifact is byte-reproducible from the pure ``build_summary()`` entry
    point and from ``--check-estimator-bakeoff``;
  * the committed SHA-256 provenance digests match a fresh recomputation;
  * the bakeoff verdict is explicit and honest (may be negative).

The artifact is a controlled synthetic stimulus, never real market data. The
verdict is honest; these tests pin determinism and internal consistency, not a
positive ranking.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p41" / "estimator_bakeoff.json"
MARKDOWN_PATH = REPO_ROOT / "research_state" / "bab_p41" / "estimator_bakeoff.md"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p41_stress.py"
P38_DEFLATED_PATH = REPO_ROOT / "research_state" / "bab_p38" / "deflated_summary.json"

MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15
N_SEEDS = 8
N_ESTIMATORS = 4
N_DGPS = 5
DSR_SURVIVE_THRESHOLD = 0.50
N_TOTAL_CELLS = N_DGPS * N_SEEDS * N_ESTIMATORS  # 160
N_CELLS_PER_DGP = N_SEEDS * N_ESTIMATORS  # 32

EXPECTED_DGP_IDS = [
    "GAUSSIAN_IID",
    "STUDENT_T",
    "REGIME_SWITCH",
    "JUMP_DIFFUSION",
    "STOCHASTIC_VOL",
]

EXPECTED_ESTIMATOR_KEYS = [
    "rolling_ols_w90",
    "ewma_h40",
    "shrinkage_i0.3_t1.0",
    "shrinkage_i0.3_csm",
]


def _load_json() -> dict:
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def summary() -> dict:
    return _load_json()


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location("bab_p41_stress", RUNNER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _p38_n_trials_total() -> int:
    return int(
        json.loads(P38_DEFLATED_PATH.read_text(encoding="utf-8"))[
            "trial_enumeration"
        ]["n_trials_total"]
    )


def _collect_cells(summary: dict) -> list[dict]:
    cells = []
    for did in summary["results"]["dgps"]:
        cells.extend(summary["results"]["dgps"][did]["cells"])
    return cells


# --------------------------------------------------------------------------- #
# Artifact shape + provenance
# --------------------------------------------------------------------------- #
def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_summary_artifact_exists():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"
    assert MARKDOWN_PATH.is_file(), f"missing {MARKDOWN_PATH}"


def test_summary_schema_version(summary):
    assert summary["schema"] == "bab_p41.estimator_bakeoff/1"


def test_bakeoff_verdict_is_explicit(summary):
    verdict = summary["bakeoff_verdict"]
    assert "_LEAST_BROKEN" in verdict, verdict


def test_summary_has_provenance_block(summary):
    prov = summary["provenance"]
    for key in (
        "generator",
        "campaign",
        "wp",
        "synthetic",
        "note",
        "fixture_path",
        "returns_sha256",
        "btc_source_sha256",
        "n_dgps",
        "n_seeds_per_dgp",
        "n_estimators",
        "n_total_cells",
        "seeds",
        "dgps",
        "config_grid",
        "neutrality_tolerances",
        "bootstrap",
        "dsr_survive_threshold",
        "deflation",
    ):
        assert key in prov, f"provenance missing {key}"
    assert prov["synthetic"] is True
    assert prov["n_dgps"] == N_DGPS
    assert prov["n_seeds_per_dgp"] == N_SEEDS
    assert prov["n_estimators"] == N_ESTIMATORS
    assert prov["n_total_cells"] == N_TOTAL_CELLS
    assert prov["config_grid"]["weighting"] == "equal"
    assert prov["config_grid"]["beta_neutral"] is True
    assert prov["config_grid"]["dollar_neutral"] is True
    assert prov["neutrality_tolerances"]["model_beta_neutral"] == MODEL_BETA_NEUTRAL_TOL
    assert prov["neutrality_tolerances"]["dollar_neutral"] == DOLLAR_NEUTRAL_TOL
    assert prov["neutrality_tolerances"]["realized_beta"] == REALIZED_BETA_TOL
    assert prov["dsr_survive_threshold"] == DSR_SURVIVE_THRESHOLD


def test_provenance_caveat_present(summary):
    note = summary["provenance"]["note"]
    assert "Not real market data" in note
    assert "not market profitability evidence" in note


def test_five_dgps_present(summary):
    prov = summary["provenance"]
    dgp_ids = [d["id"] for d in prov["dgps"]]
    assert dgp_ids == EXPECTED_DGP_IDS, f"expected {EXPECTED_DGP_IDS}, got {dgp_ids}"


def test_deflation_uses_p38_n_trials_total_read_only(summary, runner):
    assert summary["trial_enumeration"]["n_trials_total"] == _p38_n_trials_total()
    assert summary["provenance"]["deflation"]["n_trials_total"] == _p38_n_trials_total()
    assert "P38 deflated_summary.json" in summary["provenance"]["deflation"]["source"]


def test_provenance_shas_match_recompute(summary, runner):
    base = runner._build_universe_for_dgp(runner.DGPs[0], runner.DGPs[0]["base_seed"])
    returns_sha = hashlib.sha256(base.to_csv(date_format="%Y-%m-%d").encode("utf-8")).hexdigest()
    btc = runner._load_btc_prices()
    btc_sha = hashlib.sha256(btc.to_numpy(dtype=float).tobytes()).hexdigest()
    prov = summary["provenance"]
    assert prov["returns_sha256"] == returns_sha
    assert prov["btc_source_sha256"] == btc_sha


# --------------------------------------------------------------------------- #
# Per-cell completeness + neutrality at every ok cell
# --------------------------------------------------------------------------- #
def test_each_dgp_has_thirtytwo_cells(summary):
    for did in summary["results"]["dgps"]:
        cells = summary["results"]["dgps"][did]["cells"]
        assert (
            len(cells) == N_CELLS_PER_DGP
        ), f"{did}: expected {N_CELLS_PER_DGP} cells, got {len(cells)}"


def test_total_cell_count(summary):
    assert len(_collect_cells(summary)) == N_TOTAL_CELLS


def test_cell_status_is_valid(summary):
    for cell in _collect_cells(summary):
        assert cell.get("status") in (
            "ok",
            "error",
            "neutrality_violation",
        ), f"{cell.get('cell_key')}: bad status {cell.get('status')}"


def test_model_beta_neutral_at_every_ok_cell(summary):
    violations = []
    for cell in _collect_cells(summary):
        if cell.get("status") != "ok":
            continue
        max_beta = cell["neutrality"]["max_model_beta"]
        if max_beta is None or max_beta > MODEL_BETA_NEUTRAL_TOL:
            violations.append(f"{cell['cell_key']}: max_model_beta={max_beta}")
    assert not violations, "model beta neutrality violations:\n" + "\n".join(violations)


def test_dollar_neutral_at_every_ok_cell(summary):
    violations = []
    for cell in _collect_cells(summary):
        if cell.get("status") != "ok":
            continue
        max_dollar = cell["neutrality"]["max_dollar_neutral"]
        if max_dollar is None or max_dollar > DOLLAR_NEUTRAL_TOL:
            violations.append(f"{cell['cell_key']}: max_dollar={max_dollar}")
    assert not violations, "dollar neutrality violations:\n" + "\n".join(violations)


def test_realized_beta_at_every_ok_cell(summary):
    violations = []
    for cell in _collect_cells(summary):
        if cell.get("status") != "ok":
            continue
        realized = cell["neutrality"]["realized_beta"]
        if realized is None or abs(realized) > REALIZED_BETA_TOL:
            violations.append(f"{cell['cell_key']}: realized_beta={realized}")
    assert not violations, "realized beta violations:\n" + "\n".join(violations)


def test_all_ok_cells_have_required_tail_fields(summary):
    for cell in _collect_cells(summary):
        if cell.get("status") != "ok":
            continue
        tail = cell.get("tail", {})
        for key in (
            "cvar_95",
            "cvar_99",
            "expected_shortfall_975",
            "worst_day_return",
            "skew",
            "excess_kurtosis",
            "max_drawdown",
            "sharpe",
        ):
            assert key in tail, f"{cell['cell_key']} tail missing {key}"


def test_dsr_and_psr_bounded_at_every_ok_cell(summary):
    for cell in _collect_cells(summary):
        if cell.get("status") != "ok":
            continue
        assert cell["dsr"] is not None
        assert 0.0 <= cell["dsr"] <= 1.0, f"{cell['cell_key']}: dsr={cell['dsr']}"
        assert cell["psr"] is not None
        assert 0.0 <= cell["psr"] <= 1.0, (
            f"{cell['cell_key']}: psr={cell['psr']}"
        )
        assert cell["verdict"] in ("SURVIVES_DEFLATION", "DOES_NOT_SURVIVE_DEFLATION")
        expected = (
            "SURVIVES_DEFLATION"
            if cell["dsr"] >= DSR_SURVIVE_THRESHOLD
            else "DOES_NOT_SURVIVE_DEFLATION"
        )
        assert cell["verdict"] == expected, f"{cell['cell_key']}: verdict mismatch"


# --------------------------------------------------------------------------- #
# Aggregate sanity
# --------------------------------------------------------------------------- #
def test_cross_dgp_aggregates(summary):
    cross = summary["results"]["cross_dgp"]
    for key in (
        "n_dgps", "n_seeds_per_dgp", "n_estimators", "n_total_cells",
        "n_total_ok_cells", "n_total_error_cells", "n_total_survive",
        "n_dgps_replicating", "all_dgps_neutrality_ok", "all_dgps_survive",
    ):
        assert key in cross, f"cross_dgp aggregate missing {key}"
    assert cross["n_dgps"] == N_DGPS
    assert cross["n_total_cells"] == N_TOTAL_CELLS


def test_estimator_comparison_present(summary):
    comp = summary["results"]["estimator_comparison"]
    assert "least_broken_estimator" in comp
    assert comp["least_broken_estimator"] in EXPECTED_ESTIMATOR_KEYS
    assert "by_estimator" in comp
    for key in EXPECTED_ESTIMATOR_KEYS:
        assert key in comp["by_estimator"], f"estimator_comparison missing {key}"


# --------------------------------------------------------------------------- #
# Determinism / byte-identity
# --------------------------------------------------------------------------- #
def test_check_mode_is_byte_identical():
    result = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-estimator-bakeoff"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"--check-estimator-bakeoff failed: {result.stdout}\n{result.stderr}"
    )
    assert "PASS (byte-identical)" in result.stdout


def test_build_summary_matches_committed_bytes(runner):
    fresh = runner.build_summary()
    expected = json.dumps(fresh, indent=2, sort_keys=True) + "\n"
    assert SUMMARY_PATH.read_text(encoding="utf-8") == expected


def test_build_summary_is_deterministic(runner):
    first = json.dumps(runner.build_summary(), indent=2, sort_keys=True)
    second = json.dumps(runner.build_summary(), indent=2, sort_keys=True)
    assert first == second


# --------------------------------------------------------------------------- #
# Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(RUNNER_SCRIPT), str(__file__)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"ruff must pass on new files: {result.stdout} {result.stderr}"
    )
