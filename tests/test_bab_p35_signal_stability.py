"""Acceptance tests for P35 WP2: signal-stability / beta-noise sensitivity + anti-overfit guard.

These tests verify the P35 WP2 artifact contract:

  - the committed summary exists with schema ``bab_p35.signal_stability/1``
  - every estimator/perturbation cell satisfies the neutrality invariants
    (model beta-neutral <= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15)
  - baseline (OLS vs itself) has flip_fraction=0.0 and Jaccard=1.0
  - flip_fraction is monotonic non-decreasing in the noise-injection epsilon
  - the summary is reproducible byte-for-byte via ``--check-signal-stability-summary``

All data is deterministic synthetic data (the P34 wide-universe recipe); no result
is evidence of real-market profitability.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p35" / "signal_stability_summary.json"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p35_signal_stability.py"

SCHEMA = "bab_p35.signal_stability/1"
N_SEEDS = 8
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

NOISE_EPSILONS = [1e-4, 1e-3, 1e-2, 5e-2]
EWMA_HALFLIFES = [20, 40, 60]
SHRINKAGE_INTENSITIES = [0.1, 0.3]
SHRINKAGE_TARGETS = [1.0, "cross_sectional_mean"]

# Perturbations per seed: 1 baseline + len(noise) + len(ewma) + len(shrink)*len(targets)
N_PERTS_PER_SEED = (
    1
    + len(NOISE_EPSILONS)
    + len(EWMA_HALFLIFES)
    + len(SHRINKAGE_INTENSITIES) * len(SHRINKAGE_TARGETS)
)
EXPECTED_CELLS = N_SEEDS * N_PERTS_PER_SEED


@pytest.fixture(scope="module")
def summary():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cells(summary):
    return summary["results"]["cells"]


def _by_seed(cells):
    grouped = defaultdict(list)
    for cell in cells:
        grouped[cell["seed_index"]].append(cell)
    return grouped


def _noise_cells(cells):
    return [c for c in cells if c["perturbation"] == "noise"]


def _estimator_cells(cells):
    return [c for c in cells if c["perturbation"] == "estimator"]


def _baseline_cells(cells):
    return [c for c in cells if c["perturbation"] == "baseline"]


def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_schema_and_synthetic_provenance(summary):
    assert summary["schema"] == SCHEMA
    provenance = summary["provenance"]
    assert "synthetic" in provenance["fixture_recipe"].lower()
    assert "not real market data" in provenance["fixture_recipe"].lower()
    assert provenance["seeds"]["n_seeds"] == N_SEEDS
    assert provenance["config_grid"]["weighting"] == "equal"
    assert provenance["config_grid"]["beta_neutral"] is True
    assert provenance["config_grid"]["dollar_neutral"] is True
    assert provenance["config_grid"]["transaction_costs"] == 0.001
    assert provenance["config_grid"]["beta_window"] == 90
    assert provenance["config_grid"]["noise_epsilons"] == NOISE_EPSILONS
    assert provenance["neutrality_tolerances"] == {
        "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
        "dollar_neutral": DOLLAR_NEUTRAL_TOL,
        "realized_beta": REALIZED_BETA_TOL,
    }
    # Churn definition documented.
    assert "flip_fraction" in provenance["churn_definition"]
    assert "jaccard_overlap" in provenance["churn_definition"]


def test_expected_grid_shape(cells):
    assert len(cells) == EXPECTED_CELLS, f"expected {EXPECTED_CELLS} cells, got {len(cells)}"
    per_seed = defaultdict(int)
    for cell in cells:
        per_seed[cell["seed_index"]] += 1
        assert cell["status"] == "ok", f"non-ok cell: {cell['cell_key']}"
    assert sorted(per_seed) == list(range(N_SEEDS))
    assert all(n == N_PERTS_PER_SEED for n in per_seed.values())


def test_baseline_churn_zero_jaccard_one(cells):
    baselines = _baseline_cells(cells)
    assert len(baselines) == N_SEEDS
    for cell in baselines:
        churn = cell["churn"]
        assert churn["flip_fraction"] == 0.0, (
            f"{cell['cell_key']}: baseline flip_fraction must be 0.0"
        )
        assert churn["jaccard_overlap"] == 1.0, (
            f"{cell['cell_key']}: baseline Jaccard must be 1.0"
        )


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


def test_noise_flip_fraction_monotonic_in_epsilon(cells):
    """flip_fraction must be non-decreasing as noise epsilon increases."""
    grouped = _by_seed(cells)
    for seed_idx in range(N_SEEDS):
        seed_cells = grouped[seed_idx]
        noise_map = {}
        for c in seed_cells:
            if c["perturbation"] == "noise":
                noise_map[c["param"]] = c["churn"]["flip_fraction"]
        # All epsilons must be present.
        assert set(noise_map) == set(NOISE_EPSILONS), f"seed {seed_idx}: missing noise cells"
        prev = None
        prev_eps = None
        for eps in sorted(NOISE_EPSILONS):
            val = noise_map[eps]
            assert val is not None, f"seed {seed_idx} eps={eps}: flip_fraction is None"
            if prev is not None:
                assert val >= prev - 1e-12, (
                    f"seed {seed_idx}: flip_fraction not monotonic in epsilon: "
                    f"eps={prev_eps} -> {prev}, eps={eps} -> {val}"
                )
            prev = val
            prev_eps = eps

def test_estimator_churn_finite_and_nonnegative(cells):
    for cell in _estimator_cells(cells):
        churn = cell["churn"]
        assert churn["flip_fraction"] is not None, f"{cell['cell_key']}: flip_fraction is None"
        assert churn["flip_fraction"] >= 0.0, f"{cell['cell_key']}: negative flip_fraction"
        assert churn["flip_fraction"] <= 1.0, f"{cell['cell_key']}: flip_fraction > 1.0"
        assert churn["jaccard_overlap"] is not None, f"{cell['cell_key']}: Jaccard is None"
        assert 0.0 <= churn["jaccard_overlap"] <= 1.0, f"{cell['cell_key']}: Jaccard out of range"


def test_anti_victory_guard(cells):
    """No cell may claim reduced churn while violating neutrality.

    A neutrality violation is an automatic FAIL regardless of churn metrics.
    """
    for cell in cells:
        if cell["status"] != "ok":
            continue
        checks = cell["neutrality_checks"]
        for check_name, check_result in checks.items():
            max_val = (
                check_result.get("max_model_beta")
                or check_result.get("max_dollar_neutral")
                or check_result.get("realized_beta")
            )
            assert check_result["passed"] is True, (
                f"{cell['cell_key']}: anti-victory — {check_name} failed "
                f"(max={max_val}, tol={check_result.get('tolerance')})"
            )

def test_synthetic_provenance_guard(cells):
    """No result may be presented as real-market evidence."""
    provenance = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))["provenance"]
    assert "not real market data" in provenance["fixture_recipe"].lower()
    assert "not market profitability evidence" in provenance["fixture_recipe"].lower()
    for cell in cells:
        assert cell["status"] == "ok", f"{cell['cell_key']}: not ok"


def test_required_metrics_present(cells):
    for cell in cells:
        metrics = cell["metrics"]
        for key in (
            "turnover",
            "max_model_beta",
            "max_dollar_neutral",
            "realized_beta",
            "n_periods",
        ):
            assert key in metrics, f"{cell['cell_key']} missing {key}"
            assert metrics[key] is not None, f"{cell['cell_key']} null {key}"
        assert metrics["n_periods"] > 0


def test_summary_byte_determinism():
    proc = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-signal-stability-summary"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    assert "PASS (byte-identical)" in proc.stdout
