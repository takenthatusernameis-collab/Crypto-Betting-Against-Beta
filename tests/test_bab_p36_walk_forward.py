"""Acceptance tests for P36 WP0: walk-forward / out-of-sample validation harness.

These tests verify the P36 WP0 artifact contract:

  - the committed summary exists with schema ``bab_p36.walk_forward/1``
  - every walk-forward cell satisfies the neutrality invariants
    (model beta-neutral <= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15)
  - OOS Sharpe is finite and non-NaN at every cell
  - walk-forward stability (Spearman of IS vs OOS beta ranks) is finite and near 1
  - the summary is reproducible byte-for-byte via ``--check-walk-forward-summary``

All data is deterministic synthetic data (the P35 wide-universe recipe); no result
is evidence of real-market profitability.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p36" / "walk_forward_summary.json"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p36_walk_forward.py"

SCHEMA = "bab_p36.walk_forward/1"
N_SEEDS = 8
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

TRAIN_WINDOW = 90
TEST_WINDOW = 30
STEP = 30


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


def _by_window(cells):
    grouped = defaultdict(list)
    for cell in cells:
        grouped[cell["window_index"]].append(cell)
    return grouped


def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_schema_and_synthetic_provenance(summary):
    assert summary["schema"] == SCHEMA
    provenance = summary["provenance"]
    assert "synthetic" in provenance["fixture_recipe"].lower()
    assert "not real market data" in provenance["fixture_recipe"].lower()
    assert "not market profitability evidence" in provenance["fixture_recipe"].lower()
    assert provenance["seeds"]["n_seeds"] == N_SEEDS
    assert provenance["config_grid"]["weighting"] == "equal"
    assert provenance["config_grid"]["beta_neutral"] is True
    assert provenance["config_grid"]["dollar_neutral"] is True
    assert provenance["config_grid"]["transaction_costs"] == 0.001
    assert provenance["config_grid"]["train_window"] == TRAIN_WINDOW
    assert provenance["config_grid"]["test_window"] == TEST_WINDOW
    assert provenance["config_grid"]["step"] == STEP
    assert provenance["config_grid"]["beta_window"] == 90
    assert provenance["neutrality_tolerances"] == {
        "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
        "dollar_neutral": DOLLAR_NEUTRAL_TOL,
        "realized_beta": REALIZED_BETA_TOL,
    }
    assert provenance["walk_forward_stability"]["metric"] == "spearman_is_oos_beta"
    assert "fixture_path" in provenance


def test_expected_cell_count(cells):
    """8 seeds x 10 walk-forward windows = 80 cells."""
    expected_windows = 0
    n_periods = 400  # wide_bab_universe.csv has 400 rows
    start = 0
    while start + TRAIN_WINDOW + TEST_WINDOW <= n_periods:
        expected_windows += 1
        start += STEP
    expected_cells = N_SEEDS * expected_windows
    assert len(cells) == expected_cells, f"expected {expected_cells} cells, got {len(cells)}"
    per_seed = defaultdict(int)
    for cell in cells:
        per_seed[cell["seed_index"]] += 1
        assert cell["status"] == "ok", f"non-ok cell: {cell['cell_key']}"
    assert sorted(per_seed) == list(range(N_SEEDS))
    assert all(n == expected_windows for n in per_seed.values())


def test_train_test_window_sizes(cells):
    for cell in cells:
        assert cell["n_train"] == TRAIN_WINDOW, f"{cell['cell_key']}: n_train={cell['n_train']}"
        assert cell["n_test"] == TEST_WINDOW, f"{cell['cell_key']}: n_test={cell['n_test']}"


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


def test_oos_sharpe_finite_non_nan(cells):
    """OOS Sharpe must be finite and non-NaN at every cell."""
    for cell in cells:
        metrics = cell["metrics"]
        sharpe = metrics["sharpe"]
        assert sharpe is not None, f"{cell['cell_key']}: OOS Sharpe is None"
        assert abs(sharpe) < float("inf"), f"{cell['cell_key']}: OOS Sharpe is infinite"


def test_oos_wealth_finite(cells):
    for cell in cells:
        metrics = cell["metrics"]
        wealth = metrics["wealth"]
        assert wealth is not None, f"{cell['cell_key']}: OOS wealth is None"
        assert abs(wealth) < float("inf"), f"{cell['cell_key']}: OOS wealth is infinite"
        assert wealth > 0.0, f"{cell['cell_key']}: OOS wealth non-positive: {wealth}"


def test_walk_forward_stability_finite_and_near_one(cells):
    """Spearman IS vs OOS beta ranks should be finite and strongly positive."""
    for cell in cells:
        wf = cell["walk_forward_stability"]
        spearman = wf["spearman_is_oos_beta"]
        assert spearman is not None, f"{cell['cell_key']}: Spearman is None"
        assert abs(spearman) < float("inf"), f"{cell['cell_key']}: Spearman is infinite"
        assert spearman > 0.5, (
            f"{cell['cell_key']}: walk-forward stability too low: spearman={spearman}"
        )
        assert wf["n_common_assets"] == 40, (
            f"{cell['cell_key']}: expected 40 common assets, got {wf['n_common_assets']}"
        )


def test_walk_forward_stability_monotonic_in_training_window(cells):
    """Walk-forward stability should not degrade as training window grows.

    Since all windows use the same 90-day train window, we verify the
    per-window mean Spearman is consistently high across all window positions.
    """
    grouped = _by_window(cells)
    window_spearmans = {}
    for widx in sorted(grouped):
        vals = [
            c["walk_forward_stability"]["spearman_is_oos_beta"]
            for c in grouped[widx]
            if c["walk_forward_stability"]["spearman_is_oos_beta"] is not None
        ]
        assert len(vals) == N_SEEDS, f"window {widx}: expected {N_SEEDS} values"
        window_spearmans[widx] = sum(vals) / len(vals)

    # All window positions should have high stability (no decay signal).
    for widx, mean_spearman in window_spearmans.items():
        assert mean_spearman > 0.9, (
            f"window {widx}: mean Spearman decayed: {mean_spearman:.4f}"
        )


def test_anti_victory_guard(cells):
    """No cell may claim good OOS performance while violating neutrality.

    A neutrality violation is an automatic FAIL regardless of OOS Sharpe.
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
            "sharpe",
            "wealth",
            "n_periods",
        ):
            assert key in metrics, f"{cell['cell_key']} missing {key}"
            assert metrics[key] is not None, f"{cell['cell_key']} null {key}"
        assert metrics["n_periods"] > 0


def test_summary_byte_determinism():
    proc = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-walk-forward-summary"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    assert "PASS (byte-identical)" in proc.stdout


def test_no_harness_execution_ast_scan():
    """The runner must not execute any research harness (no `build_*` calls at module level).

    The script must be importable / runnable via --check-* without running the
    full walk-forward grid. Only ``build_summary()`` may be called at module
    level (and only lazily via the check flag).
    """
    source = RUNNER_SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Find top-level calls (not inside functions/classes).
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Only allow calls inside function/method definitions.
            parent_in_func = False
            for ancestor in ast.walk(tree):
                if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if node is within this function's body (rough check via line range)
                    if ancestor.lineno <= node.lineno <= ancestor.end_lineno:
                        parent_in_func = True
                        break
            if not parent_in_func:
                if isinstance(node.func, ast.Attribute):
                    assert not node.func.attr.startswith("build_"), (
                        f"top-level build_* call found: {node.func.attr}"
                    )
                elif isinstance(node.func, ast.Name):
                    assert not node.func.id.startswith("build_"), (
                        f"top-level build_* call found: {node.func.id}"
                    )
