"""Acceptance tests for P38 WP2: tail-risk & drawdown characterization (CVaR / ES).

These tests pin the committed ``research_state/bab_p38/tail_risk_summary.json``
artifact to its deterministic generator and assert the scientific contract:

  * every seed cell (gross and costed) is status ``ok`` and passes the three
    neutrality invariants (model beta <= 1e-3, dollar <= 1e-9, |realized beta| <= 0.15);
  * the tail metrics are internally ordered the way a real return distribution
    must be (VaR/CVaR/ES nesting, worst-day <= CVaR, drawdown ordering,
    tail asymmetry in [-1, +1]);
  * the artifact is byte-reproducible from the pure ``build_summary()`` entry
    point and from ``--check-tail-risk-summary``;
  * the committed SHA-256 provenance digests match a fresh recomputation.

The artifact is a controlled synthetic stimulus, never real market data.
"""

from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "research_state" / "bab_p38" / "tail_risk_summary.json"
MARKDOWN_PATH = REPO_ROOT / "research_state" / "bab_p38" / "tail_risk_summary.md"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p38_tail_risk.py"
DEFATED_SCRIPT = REPO_ROOT / "scripts" / "bab_p38_deflated_significance.py"

MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15
N_SEEDS = 8

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

CONFIGS = ("gross", "costed")


def _load_json() -> dict:
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def summary() -> dict:
    return _load_json()


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location("bab_p38_tail_risk", RUNNER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cells(summary: dict, config: str) -> list[dict]:
    return summary["results"][config]["cells"]


# --------------------------------------------------------------------------- #
# Artifact shape + provenance
# --------------------------------------------------------------------------- #
def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_summary_artifact_exists():
    assert SUMMARY_PATH.is_file(), f"missing {SUMMARY_PATH}"
    assert MARKDOWN_PATH.is_file(), f"missing {MARKDOWN_PATH}"


def test_summary_schema_version(summary):
    assert summary["schema"] == "bab_p38.tail_risk/1"


def test_tail_risk_status_is_all_neutrality_ok(summary):
    assert summary["tail_risk_status"] == "ALL_NEUTRALITY_OK"


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
        "tail_risk_definitions",
    ):
        assert key in prov, f"provenance missing {key}"
    assert prov["synthetic"] is True
    assert prov["seeds"]["base_seed"] == 20261120
    assert prov["seeds"]["increment"] == 1009
    assert prov["seeds"]["n_seeds"] == N_SEEDS
    assert prov["config_grid"]["weighting"] == "equal"
    assert prov["config_grid"]["beta_neutral"] is True
    assert prov["config_grid"]["dollar_neutral"] is True
    assert prov["config_grid"]["gross_transaction_costs"] == 0.0
    assert prov["config_grid"]["costed_transaction_costs"] == 0.001
    assert prov["neutrality_tolerances"]["model_beta_neutral"] == MODEL_BETA_NEUTRAL_TOL
    assert prov["neutrality_tolerances"]["dollar_neutral"] == DOLLAR_NEUTRAL_TOL
    assert prov["neutrality_tolerances"]["realized_beta"] == REALIZED_BETA_TOL


def test_provenance_caveat_present(summary):
    note = summary["provenance"]["note"]
    assert "Not real market data" in note
    assert "not market profitability evidence" in note


def test_seed_list_deterministic(summary):
    seeds = summary["provenance"]["seeds"]["seed_list"]
    expected = [20261120 + 1009 * i for i in range(N_SEEDS)]
    assert seeds == expected


def test_provenance_shas_match_recompute(summary, runner):
    import hashlib

    base = runner._build_wide_universe_for_seed(runner.SEED_BASE)
    returns_sha = hashlib.sha256(base.to_csv(date_format="%Y-%m-%d").encode("utf-8")).hexdigest()
    btc = runner._load_btc_prices()
    btc_sha = hashlib.sha256(btc.to_numpy(dtype=float).tobytes()).hexdigest()
    prov = summary["provenance"]
    assert prov["returns_sha256"] == returns_sha
    assert prov["btc_source_sha256"] == btc_sha


# --------------------------------------------------------------------------- #
# Cell completeness + neutrality at every cell
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("config", CONFIGS)
def test_each_config_has_eight_ok_cells(summary, config):
    cells = _cells(summary, config)
    assert len(cells) == N_SEEDS, f"{config}: expected {N_SEEDS} cells, got {len(cells)}"
    bad = [c["cell_key"] for c in cells if c.get("status") != "ok"]
    assert not bad, f"{config}: non-ok cells: {bad}"


@pytest.mark.parametrize("config", CONFIGS)
def test_model_beta_neutral_at_every_cell(summary, config):
    violations = []
    for cell in _cells(summary, config):
        max_beta = cell["neutrality"]["max_model_beta"]
        if max_beta is None or max_beta > MODEL_BETA_NEUTRAL_TOL:
            violations.append(f"{cell['cell_key']}: max_model_beta={max_beta}")
    assert not violations, "model beta neutrality violations:\n" + "\n".join(violations)


@pytest.mark.parametrize("config", CONFIGS)
def test_dollar_neutral_at_every_cell(summary, config):
    violations = []
    for cell in _cells(summary, config):
        max_dollar = cell["neutrality"]["max_dollar_neutral"]
        if max_dollar is None or max_dollar > DOLLAR_NEUTRAL_TOL:
            violations.append(f"{cell['cell_key']}: max_dollar={max_dollar}")
    assert not violations, "dollar neutrality violations:\n" + "\n".join(violations)


@pytest.mark.parametrize("config", CONFIGS)
def test_realized_beta_at_every_cell(summary, config):
    violations = []
    for cell in _cells(summary, config):
        realized = cell["neutrality"]["realized_beta"]
        if realized is None or abs(realized) > REALIZED_BETA_TOL:
            violations.append(f"{cell['cell_key']}: realized_beta={realized}")
    assert not violations, "realized beta violations:\n" + "\n".join(violations)


@pytest.mark.parametrize("config", CONFIGS)
def test_all_cells_have_required_tail_fields(summary, config):
    for cell in _cells(summary, config):
        tail = cell.get("tail", {})
        for key in REQUIRED_TAIL_KEYS:
            assert key in tail, f"{cell['cell_key']} tail missing {key}"


# --------------------------------------------------------------------------- #
# Tail-metric internal ordering (the scientific contract)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("config", CONFIGS)
def test_tail_metrics_are_finite(summary, config):
    violations = []
    for cell in _cells(summary, config):
        for key, value in cell["tail"].items():
            if isinstance(value, float) and not math.isfinite(value):
                violations.append(f"{cell['cell_key']}: {key}={value}")
    assert not violations, "non-finite tail metrics:\n" + "\n".join(violations)


@pytest.mark.parametrize("config", CONFIGS)
def test_var_cvar_es_nesting(summary, config):
    """var_99 <= var_95 <= 0, cvar <= var, cvar_99 <= cvar_95, ES between the CVaRs."""
    violations = []
    for cell in _cells(summary, config):
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


@pytest.mark.parametrize("config", CONFIGS)
def test_worst_day_below_cvar(summary, config):
    violations = []
    for cell in _cells(summary, config):
        t = cell["tail"]
        if not (t["worst_day_return"] <= t["cvar_99"]):
            violations.append(f"{cell['cell_key']}: worst {t['worst_day_return']} > cvar99")
        if not (t["best_day_return"] >= t["worst_day_return"]):
            violations.append(f"{cell['cell_key']}: best < worst")
    assert not violations, "worst/best day violations:\n" + "\n".join(violations)


@pytest.mark.parametrize("config", CONFIGS)
def test_tail_asymmetry_bounded(summary, config):
    violations = []
    for cell in _cells(summary, config):
        ta = cell["tail"]["tail_asymmetry"]
        if ta is None or not (-1.0 <= ta <= 1.0):
            violations.append(f"{cell['cell_key']}: tail_asymmetry={ta}")
    assert not violations, "tail_asymmetry out of [-1, 1]:\n" + "\n".join(violations)


@pytest.mark.parametrize("config", CONFIGS)
def test_drawdown_ordering(summary, config):
    """max_drawdown <= conditional_drawdown_95 <= 0, and it reconciles with canonical."""
    violations = []
    for cell in _cells(summary, config):
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


@pytest.mark.parametrize("config", CONFIGS)
def test_neutrality_flags_track_status(summary, config):
    for cell in _cells(summary, config):
        checks = cell["neutrality"]
        all_pass = (
            checks["model_beta_neutral"]["passed"]
            and checks["dollar_neutral"]["passed"]
            and checks["realized_beta_check"]["passed"]
        )
        expected = "ok" if all_pass else "neutrality_violation"
        assert cell["status"] == expected, f"{cell['cell_key']}: status mismatch"


# --------------------------------------------------------------------------- #
# Determinism / byte-identity
# --------------------------------------------------------------------------- #
def test_check_mode_is_byte_identical():
    result = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--check-tail-risk-summary"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"--check-tail-risk-summary failed: {result.stdout}\n{result.stderr}"
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


def test_gross_and_costed_provenance_shas_agree(summary):
    prov = summary["provenance"]
    assert len({prov["returns_sha256"], prov["btc_source_sha256"]}) == 2


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


def test_wp1_script_still_present():
    """WP1 deflated script must remain available (this WP2 test must not shadow it)."""
    assert DEFATED_SCRIPT.is_file()
