"""Acceptance tests for P34 WP0: multi-seed wide-universe equal-weight robustness study.

These tests verify that the shipped default BAB configuration (weighting="equal",
beta_neutral=True) maintains its core neutrality invariants across multiple
deterministic seeds on the wide synthetic universe (40 assets, betas 0.35-1.90,
idio_vol=0.003).

The study tests a grid of:
  - N_SEEDS >= 8 (base_seed + 1009*i)
  - beta_window in {60, 90, 120}
  - quantile in {0.2, 0.3}
  - transaction_costs = 0.001

Invariants asserted at every grid point and every seed:
  1. max_t |sum_i w_{t,i} * beta_{t,i}| <= 1e-3   (model beta-neutral)
  2. |sum_i w_{t,i}| <= 1e-9                      (dollar-neutral)
  3. |realized beta| <= 0.15                      (strategy beta via OLS vs benchmark)

Results are recorded in research_state/bab_p34/multiseed_summary.json
(schema: bab_p34.multiseed_summary/1) with a --check-multiseed-summary
mode for byte-diff verification in the gate.

Any seed/cell that cannot reproduce the neutrality bounds must be explicitly
allow-listed in this test with a written reason -- never silently skipped,
never hand-waved.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p34" / "multiseed_summary.json"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p34_multiseed_robustness.py"

# Tolerances from HANDOFF.md WP0
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

# Expected grid size
N_SEEDS = 8
BETA_WINDOWS = [60, 90, 120]
QUANTILES = [0.2, 0.3]
EXPECTED_CELLS = N_SEEDS * len(BETA_WINDOWS) * len(QUANTILES)

REQUIRED_CELL_KEYS = (
    "cell_key",
    "seed_index",
    "seed",
    "beta_window",
    "quantile",
    "metrics",
    "neutrality_checks",
    "status",
)

NEUTRALITY_CHECK_NAMES = (
    "model_beta_neutral",
    "dollar_neutral",
    "realized_beta",
)


def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_summary_artifact_exists():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"


def test_summary_schema_version():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["schema"] == "bab_p34.multiseed_summary/1"


def test_summary_has_provenance_block():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    prov = summary["provenance"]
    for key in (
        "fixture_recipe",
        "fixture_sha256",
        "btc_source_sha256",
        "seeds",
        "config_grid",
        "neutrality_tolerances",
    ):
        assert key in prov, f"provenance missing {key}"
    assert prov["seeds"]["base_seed"] == 20261120
    assert prov["seeds"]["increment"] == 1009
    assert prov["seeds"]["n_seeds"] == N_SEEDS
    assert prov["config_grid"]["weighting"] == "equal"
    assert prov["config_grid"]["beta_neutral"] is True
    assert prov["config_grid"]["dollar_neutral"] is True
    assert prov["neutrality_tolerances"]["model_beta_neutral"] == MODEL_BETA_NEUTRAL_TOL
    assert prov["neutrality_tolerances"]["dollar_neutral"] == DOLLAR_NEUTRAL_TOL
    assert prov["neutrality_tolerances"]["realized_beta"] == REALIZED_BETA_TOL


def test_summary_has_expected_cell_count():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    cells = summary["results"]["cells"]
    assert len(cells) == EXPECTED_CELLS, f"expected {EXPECTED_CELLS} cells, got {len(cells)}"


def test_all_cells_have_required_fields():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    for cell in summary["results"]["cells"]:
        for key in REQUIRED_CELL_KEYS:
            assert key in cell, f"cell {cell.get('cell_key', 'unknown')} missing {key}"


def test_all_cells_pass_neutrality_checks():
    """Every cell must pass all three neutrality invariants."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    violations = []
    for cell in summary["results"]["cells"]:
        if cell["status"] != "ok":
            violations.append(
                f"{cell['cell_key']}: status={cell['status']}, "
                f"error={cell.get('error', 'neutrality_violation')}"
            )
            continue
        for check_name in NEUTRALITY_CHECK_NAMES:
            check_result = cell["neutrality_checks"][check_name]
            if not check_result.get("passed", False):
                val = (
                    check_result.get("max_model_beta")
                    or check_result.get("max_dollar_neutral")
                    or check_result.get("realized_beta")
                )
                violations.append(
                    f"{cell['cell_key']}: {check_name} failed -- "
                    f"value={val}, tol={check_result.get('tolerance')}"
                )
    assert not violations, "Neutrality violations found:\n" + "\n".join(violations)


def test_no_cell_has_error_status():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    errors = [c for c in summary["results"]["cells"] if c["status"] == "error"]
    assert not errors, f"Cells with error status: {[e['cell_key'] for e in errors]}"


def test_model_beta_neutrality_bound():
    """max_t |sum_i w_{t,i} * beta_{t,i}| <= 1e-3 at every grid point."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    violations = []
    for cell in summary["results"]["cells"]:
        if cell["status"] != "ok":
            continue
        check = cell["neutrality_checks"]["model_beta_neutral"]
        max_beta = check.get("max_model_beta")
        if max_beta is not None and max_beta > MODEL_BETA_NEUTRAL_TOL:
            violations.append(
                f"{cell['cell_key']}: max_model_beta={max_beta:.6f} > "
                f"{MODEL_BETA_NEUTRAL_TOL}"
            )
    assert not violations, "Model beta neutrality violations:\n" + "\n".join(violations)


def test_dollar_neutrality_bound():
    """|sum_i w_{t,i}| <= 1e-9 at every grid point."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    violations = []
    for cell in summary["results"]["cells"]:
        if cell["status"] != "ok":
            continue
        check = cell["neutrality_checks"]["dollar_neutral"]
        max_dollar = check.get("max_dollar_neutral")
        if max_dollar is not None and max_dollar > DOLLAR_NEUTRAL_TOL:
            violations.append(
                f"{cell['cell_key']}: max_dollar_neutral={max_dollar:.6e} > "
                f"{DOLLAR_NEUTRAL_TOL}"
            )
    assert not violations, "Dollar neutrality violations:\n" + "\n".join(violations)


def test_realized_beta_bound():
    """|realized beta| <= 0.15 at every grid point."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    violations = []
    for cell in summary["results"]["cells"]:
        if cell["status"] != "ok":
            continue
        check = cell["neutrality_checks"]["realized_beta"]
        realized = check.get("realized_beta")
        if realized is not None and abs(realized) > REALIZED_BETA_TOL:
            violations.append(
                f"{cell['cell_key']}: realized_beta={realized:.6f} > "
                f"{REALIZED_BETA_TOL}"
            )
    assert not violations, "Realized beta violations:\n" + "\n".join(violations)


def test_fixture_sha256_matches():
    """The fixture_sha256 in provenance must match the actual fixture file."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    fixture_path = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
    actual_sha = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    assert summary["provenance"]["fixture_sha256"] == actual_sha


def test_btc_source_sha256_matches():
    """The btc_source_sha256 in provenance must match the reference fixture."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    ref_path = REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv"
    ref = pd.read_csv(ref_path, index_col="date", parse_dates=True)
    actual_sha = hashlib.sha256(ref["BTC"].to_numpy(dtype=float).tobytes()).hexdigest()
    assert summary["provenance"]["btc_source_sha256"] == actual_sha


def test_seed_list_deterministic():
    """Seed list must be exactly base_seed + increment * i for i in 0..N_SEEDS-1."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    seeds = summary["provenance"]["seeds"]["seed_list"]
    expected = [20261120 + 1009 * i for i in range(N_SEEDS)]
    assert seeds == expected


def test_config_grid_complete():
    """Every combination of beta_window and quantile must be present for each seed."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    cells = summary["results"]["cells"]
    seen = set()
    for cell in cells:
        key = (cell["seed_index"], cell["beta_window"], cell["quantile"])
        seen.add(key)
    expected = {
        (si, bw, q)
        for si in range(N_SEEDS)
        for bw in BETA_WINDOWS
        for q in QUANTILES
    }
    assert seen == expected, f"Missing cells: {expected - seen}"


def test_check_multiseed_summary_mode():
    """The --check-multiseed-summary mode must pass (byte-identical)."""
    result = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-multiseed-summary"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"--check-multiseed-summary failed: {result.stdout}\n{result.stderr}"
    )


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


def test_metrics_are_finite():
    """All recorded metrics should be finite numbers (not NaN/inf)."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    violations = []
    for cell in summary["results"]["cells"]:
        if cell["status"] != "ok":
            continue
        metrics = cell["metrics"]
        for metric_name, value in metrics.items():
            if value is not None and not math.isfinite(value):
                violations.append(f"{cell['cell_key']}: {metric_name} = {value} (non-finite)")
    assert not violations, "Non-finite metrics:\n" + "\n".join(violations)


def test_all_seeds_have_nonzero_periods():
    """Each cell should have n_periods > 0 (backtest actually ran)."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    violations = []
    for cell in summary["results"]["cells"]:
        if cell["status"] != "ok":
            continue
        n_periods = cell["metrics"].get("n_periods", 0)
        if n_periods <= 0:
            violations.append(f"{cell['cell_key']}: n_periods = {n_periods}")
    assert not violations, "Cells with zero periods:\n" + "\n".join(violations)
