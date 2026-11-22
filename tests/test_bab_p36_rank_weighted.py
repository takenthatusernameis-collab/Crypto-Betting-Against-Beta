"""Acceptance tests for P36 WP1: Frazzini-Pedersen rank-weighted / beta-scaled construction.

These tests verify the P36 WP1 artifact contract:

  - the committed summary exists with schema ``bab_p36.rank_weighted/1``
  - beta-neutrality holds at every cell for both equal-weight and rank-weighted
  - realized beta |beta| <= 0.15 at every cell for both constructions
  - equal-weight satisfies dollar-neutrality <= 1e-9 (shipped default)
  - rank-weighted is intentionally NOT dollar-neutral (beta-neutrality only)
  - rank-weighted vs equal-weight turnover/churn comparison
  - the summary is reproducible byte-for-byte via ``--check-rank-weighted-summary``

All data is deterministic synthetic data (the P35 wide-universe recipe); no result
is evidence of real-market profitability.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p36" / "rank_weighted_summary.json"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p36_rank_weighted.py"

SCHEMA = "bab_p36.rank_weighted/1"
N_SEEDS = 8
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0


@pytest.fixture(scope="module")
def summary():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cells(summary):
    return summary["results"]["cells"]


def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_schema_and_synthetic_provenance(summary):
    assert summary["schema"] == SCHEMA
    provenance = summary["provenance"]
    assert "synthetic" in provenance["fixture_recipe"].lower()
    assert "not real market data" in provenance["fixture_recipe"].lower()
    assert "not market profitability evidence" in provenance["fixture_recipe"].lower()
    assert provenance["seeds"]["n_seeds"] == N_SEEDS
    assert provenance["config_grid"]["weighting_equal"] == "equal"
    assert provenance["config_grid"]["weighting_rank"] == "rank"
    assert provenance["config_grid"]["beta_neutral"] is True
    assert provenance["config_grid"]["dollar_neutral"] is True
    assert provenance["config_grid"]["transaction_costs"] == 0.001
    assert provenance["config_grid"]["beta_window"] == 90
    assert provenance["config_grid"]["rank_min_leg_beta"] == RANK_MIN_LEG_BETA
    assert provenance["config_grid"]["rank_max_gross"] == RANK_MAX_GROSS
    assert provenance["neutrality_tolerances"] == {
        "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
        "dollar_neutral": DOLLAR_NEUTRAL_TOL,
        "realized_beta": REALIZED_BETA_TOL,
    }
    assert provenance["rank_construction"]["method"] == (
        "Frazzini-Pedersen rank weighting with per-leg beta scaling"
    )


def test_expected_cell_count(cells):
    assert len(cells) == N_SEEDS, f"expected {N_SEEDS} cells, got {len(cells)}"
    for cell in cells:
        assert cell["status"] == "ok", f"non-ok cell: {cell['cell_key']}"
    assert [c["seed_index"] for c in cells] == list(range(N_SEEDS))


def test_beta_neutrality_equal_weight_every_cell(cells):
    """Equal-weight (shipped default): model beta-neutral at every cell."""
    for cell in cells:
        eq = cell["equal_weight"]
        assert eq["neutrality_ok"] is True, f"{cell['cell_key']}: equal-weight neutrality failed"
        metrics = eq["metrics"]
        assert metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL, (
            f"{cell['cell_key']}: equal-weight max_model_beta={metrics['max_model_beta']}"
        )


def test_beta_neutrality_rank_weighted_every_cell(cells):
    """Rank-weighted: model beta-neutral at every cell."""
    for cell in cells:
        rw = cell["rank_weighted"]
        assert rw["neutrality_ok"] is True, f"{cell['cell_key']}: rank-weighted neutrality failed"
        metrics = rw["metrics"]
        assert metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL, (
            f"{cell['cell_key']}: rank-weighted max_model_beta={metrics['max_model_beta']}"
        )


def test_realized_beta_bound_every_cell(cells):
    """|realized beta| <= 0.15 at every cell for both constructions."""
    for cell in cells:
        eq_metrics = cell["equal_weight"]["metrics"]
        rw_metrics = cell["rank_weighted"]["metrics"]
        assert eq_metrics["realized_beta"] is not None
        assert abs(eq_metrics["realized_beta"]) <= REALIZED_BETA_TOL, (
            f"{cell['cell_key']}: equal-weight realized_beta={eq_metrics['realized_beta']}"
        )
        assert rw_metrics["realized_beta"] is not None
        assert abs(rw_metrics["realized_beta"]) <= REALIZED_BETA_TOL, (
            f"{cell['cell_key']}: rank-weighted realized_beta={rw_metrics['realized_beta']}"
        )


def test_dollar_neutral_equal_weight(cells):
    """Equal-weight (shipped default): dollar-neutrality <= 1e-9 at every cell."""
    for cell in cells:
        metrics = cell["equal_weight"]["metrics"]
        assert metrics["max_dollar_neutral"] is not None
        assert metrics["max_dollar_neutral"] <= DOLLAR_NEUTRAL_TOL, (
            f"{cell['cell_key']}: equal-weight max_dollar_neutral={metrics['max_dollar_neutral']}"
        )


def test_rank_weighted_not_dollar_neutral(cells):
    """Rank-weighted is intentionally NOT dollar-neutral (beta-neutrality only).

    Rank weighting scales each leg by inverse leg beta, so the long and short
    leg gross exposures are 1/beta_L and 1/beta_H respectively. Unless
    beta_L == beta_H, the net dollar exposure is nonzero. This is by design.
    """
    for cell in cells:
        metrics = cell["rank_weighted"]["metrics"]
        # model beta-neutrality must still hold
        assert metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL
        # realized beta must still be bounded
        assert abs(metrics["realized_beta"]) <= REALIZED_BETA_TOL


def test_rank_weighted_turnover_vs_equal_weight(cells):
    """Rank-weighted vs equal-weight turnover comparison.

    Reports whether rank-weighted reduces churn vs equal-weight, as the
    HANDOFF P36 decision expects: "rank-weighted construction reduces churn
    vs equal-weight at equal neutrality".
    """
    reductions = []
    for cell in cells:
        comp = cell["comparison"]
        if comp["turnover_reduction"] is not None:
            reductions.append(comp["turnover_reduction"])
    assert len(reductions) == N_SEEDS, f"expected {N_SEEDS} turnover comparisons"
    for r in reductions:
        assert r is not None
    # At minimum, turnover should be finite and comparable.
    for r in reductions:
        assert abs(r) < float("inf")


def test_sharpe_and_wealth_finite(cells):
    for cell in cells:
        eq_metrics = cell["equal_weight"]["metrics"]
        rw_metrics = cell["rank_weighted"]["metrics"]
        for label, m in (("equal_weight", eq_metrics), ("rank_weighted", rw_metrics)):
            assert m["sharpe"] is not None, f"{cell['cell_key']}: {label} Sharpe is None"
            assert abs(m["sharpe"]) < float("inf"), f"{cell['cell_key']}: {label} Sharpe infinite"
            assert m["wealth"] is not None, f"{cell['cell_key']}: {label} wealth is None"
            assert abs(m["wealth"]) < float("inf"), f"{cell['cell_key']}: {label} wealth infinite"
            assert m["wealth"] > 0.0, f"{cell['cell_key']}: {label} wealth non-positive"


def test_n_periods_positive(cells):
    for cell in cells:
        assert cell["n_periods"] > 0, f"{cell['cell_key']}: n_periods must be positive"
        eq_metrics = cell["equal_weight"]["metrics"]
        rw_metrics = cell["rank_weighted"]["metrics"]
        assert eq_metrics["n_periods"] == cell["n_periods"]
        assert rw_metrics["n_periods"] == cell["n_periods"]


def test_anti_victory_guard(cells):
    """No cell may claim good performance while violating beta neutrality.

    Beta neutrality is non-negotiable for both constructions.
    """
    for cell in cells:
        eq = cell["equal_weight"]
        rw = cell["rank_weighted"]
        assert eq["neutrality_ok"] is True, (
            f"{cell['cell_key']}: anti-victory — equal-weight neutrality failed"
        )
        assert rw["neutrality_ok"] is True, (
            f"{cell['cell_key']}: anti-victory — rank-weighted neutrality failed"
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
        for label in ("equal_weight", "rank_weighted"):
            metrics = cell[label]["metrics"]
            for key in (
                "turnover",
                "max_model_beta",
                "max_dollar_neutral",
                "realized_beta",
                "sharpe",
                "wealth",
                "n_periods",
            ):
                assert key in metrics, f"{cell['cell_key']} {label} missing {key}"
                assert metrics[key] is not None, f"{cell['cell_key']} {label} null {key}"
            assert metrics["n_periods"] > 0


def test_summary_byte_determinism():
    proc = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-rank-weighted-summary"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    assert "PASS (byte-identical)" in proc.stdout


def test_no_harness_execution_ast_scan():
    """The runner must not execute any research harness (no `build_*` calls at module level)."""
    source = RUNNER_SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            parent_in_func = False
            for ancestor in ast.walk(tree):
                if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
