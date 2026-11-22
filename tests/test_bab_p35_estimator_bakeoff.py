"""Acceptance tests for P35 WP1: estimator bake-off on the wide universe.

These tests verify the P35 WP1 artifact contract:

  - the committed summary exists with schema ``bab_p35.estimator_bakeoff/1``
  - every estimator at every cell satisfies the neutrality invariants
    (model beta-neutral <= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15)
  - EWMA and shrinkage measurably reduce signal instability versus the shipped
    default rolling-OLS window=90 without breaking neutrality
  - the summary is reproducible byte-for-byte via
    ``--check-estimator-bakeoff-summary``

All data is deterministic synthetic data (the P34 wide-universe recipe and the
synthetic P25 reference fixture); no result is evidence of real-market
profitability.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p35" / "estimator_bakeoff_summary.json"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p35_estimator_bakeoff.py"

SCHEMA = "bab_p35.estimator_bakeoff/1"
N_SEEDS = 8
EXPECTED_PER_SEED = 10
EXPECTED_CELLS = N_SEEDS * EXPECTED_PER_SEED
ESTIMATOR_COUNTS = {"rolling_ols": 24, "ewma": 24, "shrinkage": 32}

MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

REQUIRED_METRIC_KEYS = (
    "turnover",
    "beta_noise",
    "beta_dispersion",
    "spearman_vs_ols",
    "max_model_beta",
    "max_dollar_neutral",
    "realized_beta",
)


@pytest.fixture(scope="module")
def summary():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cells(summary):
    return summary["results"]["cells"]


def _estimator_key(cell):
    params = cell["params"]
    if cell["estimator"] == "rolling_ols":
        return f"ols{params['window']}"
    if cell["estimator"] == "ewma":
        return f"ewma{params['halflife']}"
    target = "csm" if params["target"] == "cross_sectional_mean" else params["target"]
    return f"shrink_{params['intensity']}_{target}"


def _by_seed(cells):
    grouped = defaultdict(dict)
    for cell in cells:
        grouped[cell["seed_index"]][_estimator_key(cell)] = cell
    return grouped


def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_schema_and_synthetic_provenance(summary):
    assert summary["schema"] == SCHEMA
    provenance = summary["provenance"]
    assert "synthetic" in provenance["fixture_recipe"].lower()
    assert "not real market data" in provenance["fixture_recipe"].lower()
    assert provenance["seeds"]["n_seeds"] == N_SEEDS
    assert provenance["seeds"]["seed_list"] == [
        provenance["seeds"]["base_seed"] + provenance["seeds"]["increment"] * i
        for i in range(N_SEEDS)
    ]
    assert provenance["config_grid"]["weighting"] == "equal"
    assert provenance["config_grid"]["beta_neutral"] is True
    assert provenance["config_grid"]["dollar_neutral"] is True
    assert provenance["config_grid"]["transaction_costs"] == 0.001
    assert provenance["neutrality_tolerances"] == {
        "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
        "dollar_neutral": DOLLAR_NEUTRAL_TOL,
        "realized_beta": REALIZED_BETA_TOL,
    }


def test_expected_grid_shape(cells):
    assert len(cells) == EXPECTED_CELLS
    counts = defaultdict(int)
    per_seed = defaultdict(int)
    for cell in cells:
        counts[cell["estimator"]] += 1
        per_seed[cell["seed_index"]] += 1
        assert cell["status"] == "ok", f"non-ok cell: {cell['cell_key']}"
    assert dict(counts) == ESTIMATOR_COUNTS
    assert sorted(per_seed) == list(range(N_SEEDS))
    assert all(n == EXPECTED_PER_SEED for n in per_seed.values())


def test_neutrality_invariants_hold_for_every_cell(cells):
    for cell in cells:
        checks = cell["neutrality_checks"]
        assert set(checks) == {
            "model_beta_neutral",
            "dollar_neutral",
            "realized_beta",
        }
        for check in checks.values():
            assert check["passed"] is True, f"{cell['cell_key']}: {check}"
        metrics = cell["metrics"]
        assert metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL
        assert metrics["max_dollar_neutral"] <= DOLLAR_NEUTRAL_TOL
        assert abs(metrics["realized_beta"]) <= REALIZED_BETA_TOL


def test_required_metrics_present(cells):
    for cell in cells:
        metrics = cell["metrics"]
        for key in REQUIRED_METRIC_KEYS:
            assert key in metrics, f"{cell['cell_key']} missing {key}"
            assert metrics[key] is not None, f"{cell['cell_key']} null {key}"
        assert metrics["n_periods"] > 0


def test_ewma_reduces_instability_vs_default_ols(cells):
    grouped = _by_seed(cells)
    ewma_turnover = []
    ewma_noise = []
    ols_turnover = []
    ols_noise = []
    for seed_idx in range(N_SEEDS):
        seed_cells = grouped[seed_idx]
        ols = seed_cells["ols90"]["metrics"]
        ols_turnover.append(ols["turnover"])
        ols_noise.append(ols["beta_noise"])
        ewma_cells = [c for k, c in seed_cells.items() if k.startswith("ewma")]
        assert len(ewma_cells) == 3
        ewma_turnover.append(min(c["metrics"]["turnover"] for c in ewma_cells))
        ewma_noise.append(min(c["metrics"]["beta_noise"] for c in ewma_cells))

    mean = lambda xs: sum(xs) / len(xs)  # noqa: E731
    assert mean(ewma_turnover) < mean(ols_turnover)
    assert mean(ewma_noise) < mean(ols_noise)

    for cell in cells:
        if cell["estimator"] == "ewma":
            assert cell["metrics"]["spearman_vs_ols"] >= 0.99
            assert cell["metrics"]["jaccard_vs_ols"] == 1.0


def test_shrinkage_reduces_dispersion_and_noise(cells):
    grouped = _by_seed(cells)
    for seed_idx in range(N_SEEDS):
        seed_cells = grouped[seed_idx]
        ols = seed_cells["ols90"]["metrics"]
        shrink_cells = [c for k, c in seed_cells.items() if k.startswith("shrink")]
        assert len(shrink_cells) == 4
        assert min(c["metrics"]["beta_noise"] for c in shrink_cells) < ols["beta_noise"]
        assert (
            min(c["metrics"]["beta_dispersion"] for c in shrink_cells)
            < ols["beta_dispersion"]
        )
        # Shrinkage is a per-row monotone transform of the OLS ranking, so the
        # long/short sets and turnover must be unchanged versus the OLS default.
        for cell in shrink_cells:
            assert cell["metrics"]["turnover"] == pytest.approx(
                ols["turnover"], abs=5e-5
            )
            assert cell["metrics"]["spearman_vs_ols"] >= 0.99
            assert cell["metrics"]["jaccard_vs_ols"] == 1.0


def test_summary_byte_determinism():
    proc = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-estimator-bakeoff-summary"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    assert "PASS (byte-identical)" in proc.stdout
