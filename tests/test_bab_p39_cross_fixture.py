"""Acceptance tests for P39 WP2: cross-fixture replication (second synthetic universe).

These tests pin the committed ``research_state/bab_p39/cross_fixture_summary.json``
artifact to its deterministic generator and assert the scientific contract:

  * every seed cell is status ``ok`` or ``error``; every ``ok`` cell passes the
    three neutrality invariants (model beta <= 1e-3, dollar <= 1e-9,
    |realized beta| <= 0.15);
  * DSR/PSR + tail metrics (CVaR / expected shortfall / drawdown / skew /
    kurtosis) are computed per seed cell, deflated over n_trials_total read-only
    from P38 WP1;
  * tail metrics are internally ordered (VaR/CVaR/ES nesting, worst-day <= CVaR,
    drawdown ordering, tail asymmetry in [-1, +1]);
  * the artifact is byte-reproducible from the pure ``build_summary()`` entry
    point and from ``--check-cross-fixture-summary``;
  * the committed SHA-256 provenance digests match a fresh recomputation;
  * the campaign verdict is explicit: ``REPLICATES`` or ``DOES_NOT_REPLICATE``
    (honest, may be negative — pinned to determinism, not to a positive result).

The artifact is a controlled synthetic stimulus, never real market data. The
verdict is honest; these tests pin determinism and internal consistency, not a
positive replication.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p39" / "cross_fixture_summary.json"
MARKDOWN_PATH = REPO_ROOT / "research_state" / "bab_p39" / "cross_fixture_summary.md"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p39_cross_fixture.py"
P38_DEFLATED_PATH = REPO_ROOT / "research_state" / "bab_p38" / "deflated_summary.json"

MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15
N_SEEDS = 8
DSR_SURVIVE_THRESHOLD = 0.50

REQUIRED_TAIL_KEYS = (
    "n_observations",
    "mean_return",
    "std_return",
    "var_95",
    "cvar_95",
    "n_tail_obs_95",
    "var_99",
    "cvar_99",
    "n_tail_obs_99",
    "expected_shortfall_975",
    "worst_day_return",
    "best_day_return",
    "skew",
    "excess_kurtosis",
    "left_tail_mean",
    "right_tail_mean",
    "tail_asymmetry",
    "drawdown_var_95",
    "conditional_drawdown_95",
    "max_drawdown",
    "max_drawdown_canonical",
    "sharpe",
)


def _load_json() -> dict:
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def summary() -> dict:
    return _load_json()


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location("bab_p39_cross_fixture", RUNNER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _p38_n_trials_total() -> int:
    return int(
        json.loads(P38_DEFLATED_PATH.read_text(encoding="utf-8"))[
            "trial_enumeration"
        ]["n_trials_total"]
    )


def _cells(summary: dict) -> list[dict]:
    return summary["results"]["cells"]


# --------------------------------------------------------------------------- #
# Artifact shape + provenance
# --------------------------------------------------------------------------- #
def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_summary_artifact_exists():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"
    assert MARKDOWN_PATH.is_file(), f"missing {MARKDOWN_PATH}"


def test_summary_schema_version(summary):
    assert summary["schema"] == "bab_p39.cross_fixture/1"


def test_campaign_verdict_is_explicit(summary):
    verdict = summary["campaign_verdict"]
    assert verdict in ("REPLICATES", "DOES_NOT_REPLICATE"), verdict


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
        "seeds",
        "config_grid",
        "neutrality_tolerances",
        "bootstrap",
        "dsr_survive_threshold",
        "deflation",
    ):
        assert key in prov, f"provenance missing {key}"
    assert prov["synthetic"] is True
    assert prov["seeds"]["base_seed"] == 20270101
    assert prov["seeds"]["increment"] == 9973
    assert prov["seeds"]["n_seeds"] == N_SEEDS
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


def test_seed_list_deterministic(summary):
    seeds = summary["provenance"]["seeds"]["seed_list"]
    expected = [20270101 + 9973 * i for i in range(N_SEEDS)]
    assert seeds == expected


def test_config_grid_is_second_parameterization(summary):
    cg = summary["provenance"]["config_grid"]
    assert cg["idio_vol"] == 0.006
    assert cg["beta_min"] == 0.20
    assert cg["beta_max"] == 2.40
    assert cg["n_assets"] == 32


def test_deflation_uses_p38_n_trials_total_read_only(summary, runner):
    assert summary["trial_enumeration"]["n_trials_total"] == _p38_n_trials_total()
    assert summary["provenance"]["deflation"]["n_trials_total"] == _p38_n_trials_total()
    assert "P38 deflated_summary.json" in summary["provenance"]["deflation"]["source"]


def test_provenance_shas_match_recompute(summary, runner):
    base = runner._build_wide_universe_for_seed(runner.SEED_BASE)
    returns_sha = hashlib.sha256(base.to_csv(date_format="%Y-%m-%d").encode("utf-8")).hexdigest()
    btc = runner._load_btc_prices()
    btc_sha = hashlib.sha256(btc.to_numpy(dtype=float).tobytes()).hexdigest()
    prov = summary["provenance"]
    assert prov["returns_sha256"] == returns_sha
    assert prov["btc_source_sha256"] == btc_sha


# --------------------------------------------------------------------------- #
# Per-seed cell completeness + neutrality at every ok cell
# --------------------------------------------------------------------------- #
def test_each_seed_has_a_cell(summary):
    cells = _cells(summary)
    assert len(cells) == N_SEEDS, f"expected {N_SEEDS} cells, got {len(cells)}"


def test_cell_status_is_valid(summary):
    for cell in _cells(summary):
        assert cell.get("status") in (
            "ok",
            "error",
        ), f"{cell.get('cell_key')}: bad status {cell.get('status')}"


def test_model_beta_neutral_at_every_ok_cell(summary):
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        max_beta = cell["neutrality"]["max_model_beta"]
        if max_beta is None or max_beta > MODEL_BETA_NEUTRAL_TOL:
            violations.append(f"{cell['cell_key']}: max_model_beta={max_beta}")
    assert not violations, "model beta neutrality violations:\n" + "\n".join(violations)


def test_dollar_neutral_at_every_ok_cell(summary):
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        max_dollar = cell["neutrality"]["max_dollar_neutral"]
        if max_dollar is None or max_dollar > DOLLAR_NEUTRAL_TOL:
            violations.append(f"{cell['cell_key']}: max_dollar={max_dollar}")
    assert not violations, "dollar neutrality violations:\n" + "\n".join(violations)


def test_realized_beta_at_every_ok_cell(summary):
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        realized = cell["neutrality"]["realized_beta"]
        if realized is None or abs(realized) > REALIZED_BETA_TOL:
            violations.append(f"{cell['cell_key']}: realized_beta={realized}")
    assert not violations, "realized beta violations:\n" + "\n".join(violations)


def test_all_ok_cells_have_required_tail_fields(summary):
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        tail = cell.get("tail", {})
        for key in REQUIRED_TAIL_KEYS:
            assert key in tail, f"{cell['cell_key']} tail missing {key}"


# --------------------------------------------------------------------------- #
# Tail-metric internal ordering (the scientific contract)
# --------------------------------------------------------------------------- #
def test_tail_metrics_are_finite(summary):
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        for key, value in cell["tail"].items():
            if isinstance(value, float) and not math.isfinite(value):
                violations.append(f"{cell['cell_key']}: {key}={value}")
    assert not violations, "non-finite tail metrics:\n" + "\n".join(violations)


def test_var_cvar_es_nesting(summary):
    """var_99 <= var_95 <= 0, cvar <= var, cvar_99 <= cvar_95, ES between the CVaRs."""
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        t = cell["tail"]
        var95, var99 = t["var_95"], t["var_99"]
        cvar95, cvar99 = t["cvar_95"], t["cvar_99"]
        es = t["expected_shortfall_975"]
        if not (var99 <= var95 <= 0.0):
            violations.append(f"{cell['cell_key']}: var ordering {var99} / {var95}")
        if not (cvar95 <= var95 and cvar99 <= var99):
            violations.append(f"{cell['cell_key']}: cvar below var violated")
        if not (cvar99 <= cvar95):
            violations.append(f"{cell['cell_key']}: cvar_99 {cvar99} > cvar_95 {cvar95}")
        if not (cvar99 <= es <= cvar95):
            violations.append(f"{cell['cell_key']}: ES {es} outside [{cvar99}, {cvar95}]")
    assert not violations, "tail nesting violations:\n" + "\n".join(violations)


def test_worst_day_below_cvar(summary):
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        t = cell["tail"]
        if not (t["worst_day_return"] <= t["cvar_99"]):
            violations.append(
                f"{cell['cell_key']}: worst {t['worst_day_return']} > cvar99"
            )
        if not (t["best_day_return"] >= t["worst_day_return"]):
            violations.append(f"{cell['cell_key']}: best < worst")
    assert not violations, "worst/best day violations:\n" + "\n".join(violations)


def test_tail_asymmetry_bounded(summary):
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        ta = cell["tail"]["tail_asymmetry"]
        if ta is None or not (-1.0 <= ta <= 1.0):
            violations.append(f"{cell['cell_key']}: tail_asymmetry={ta}")
    assert not violations, "tail_asymmetry out of [-1, 1]:\n" + "\n".join(violations)


def test_drawdown_ordering(summary):
    """max_drawdown <= conditional_drawdown_95 <= 0, reconciles with canonical."""
    violations = []
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        t = cell["tail"]
        dd = t["max_drawdown"]
        cdd = t["conditional_drawdown_95"]
        canon = t["max_drawdown_canonical"]
        if not (dd <= 0.0 and cdd <= 0.0):
            violations.append(f"{cell['cell_key']}: drawdown positive dd={dd} cdd={cdd}")
        if not (dd <= cdd):
            violations.append(f"{cell['cell_key']}: max_dd {dd} > c_dar {cdd}")
        if abs(canon - dd) > 1e-9:
            violations.append(f"{cell['cell_key']}: canonical {canon} != series {dd}")
    assert not violations, "drawdown ordering violations:\n" + "\n".join(violations)


def test_neutrality_flags_track_status(summary):
    for cell in _cells(summary):
        if cell.get("status") != "ok":
            continue
        checks = cell["neutrality"]
        all_pass = (
            checks["model_beta_neutral"]["passed"]
            and checks["dollar_neutral"]["passed"]
            and checks["realized_beta_check"]["passed"]
        )
        assert all_pass is True, f"{cell['cell_key']}: neutrality flag mismatch"


# --------------------------------------------------------------------------- #
# DSR/PSR sanity at every ok cell
# --------------------------------------------------------------------------- #
def test_dsr_and_psr_bounded_at_every_ok_cell(summary):
    for cell in _cells(summary):
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
def test_aggregate_has_required_keys(summary):
    agg = summary["results"]["aggregate"]
    for key in (
        "n_cells",
        "n_ok_cells",
        "n_error_cells",
        "n_neutrality_violations",
        "all_neutrality_ok",
        "all_survive",
        "any_survive",
        "n_survive",
        "dsr",
        "psr",
        "sharpe",
        "tail_metric_aggregates",
        "neutrality",
    ):
        assert key in agg, f"aggregate missing {key}"


# --------------------------------------------------------------------------- #
# Determinism / byte-identity
# --------------------------------------------------------------------------- #
def test_check_mode_is_byte_identical():
    result = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-cross-fixture-summary"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"--check-cross-fixture-summary failed: {result.stdout}\n{result.stderr}"
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
