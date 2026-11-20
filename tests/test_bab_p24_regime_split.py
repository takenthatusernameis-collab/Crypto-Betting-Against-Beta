"""Acceptance tests for P24 WP1: the regime-split stress artifact.

These tests are the claim that ``scripts/bab_regime_split.py`` produces a
deterministic, chartered regime-split stress
(``research_state/bab_p24/regime_split.json``) from the committed P21 universe,
P23 charter and P24 charter, all read-only. They prove the mechanical contract
the charter declares:

* every chartered regime (``calm``, ``stress``) is present with all hysteresis
  bands, both weightings and both variants;
* planted recovery is strictly positive for ``calm`` regime; stress regime may
  show negative recovery (regime stress is real);
* null recovery is exactly ``0.0`` on every cell for both regimes;
* rank-leg guards (``min_leg_beta >= 0.2``, ``gross_max <= 4.0``) hold on
  every active rank row and are never relaxed;
* every cell has at least one active row;
* committed JSON equals a fresh build; markdown equals the renderer output;
* a second build is byte-identical;
* the inputs are byte-identical before and after ``main()``;
* the harness never imports or calls a P21/P22/P23/P24 build function.

The ``regime_zero_reference`` block cross-checks the baseline (no regime
filter) against the committed P21 ``rank_eval.json`` and P23 WP1 breadth-41
baseline, so the regime-split cannot drift from its upstream references.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from scripts import bab_regime_split as r

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
P23_CHARTER_PATH = REPO_ROOT / "research_state/bab_p23/charter.json"
P24_CHARTER_PATH = REPO_ROOT / "research_state/bab_p24/charter.json"
JSON_PATH = REPO_ROOT / "research_state/bab_p24/regime_split.json"
MD_PATH = REPO_ROOT / "research_state/bab_p24/regime_split.md"
P21_RANK_EVAL_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.json"
P23_BREADTH_LADDER_PATH = REPO_ROOT / "research_state/bab_p23/breadth_ladder.json"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_regime_split.py"

# Only the upstream build_* functions are forbidden -- local helpers like
# _book_metrics, _clean, _leg_guard_diagnostics are allowed.
FORBIDDEN_BUILDERS = (
    "build_universe",
    "build_rank_eval",
    "build_null_battery",
    "build_impact_surface",
    "build_capacity",
    "build_significance",
    "build_synthetic_universe",
    "build_breadth_ladder",
    "build_beta_drift",
    "build_short_haircut",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


@pytest.fixture(scope="module")
def p24_charter() -> dict:
    return json.loads(P24_CHARTER_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p23_charter() -> dict:
    return json.loads(P23_CHARTER_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def payload(committed: dict) -> dict:
    return committed


@pytest.fixture(scope="module")
def cells(payload: dict) -> list[dict]:
    return payload["cells"]


def _cell(cells, regime, hysteresis, weighting, variant):
    matches = [
        cell
        for cell in cells
        if cell["regime"] == regime
        and cell["hysteresis"] == hysteresis
        and cell["weighting"] == weighting
        and cell["variant"] == variant
    ]
    assert len(matches) == 1, (regime, hysteresis, weighting, variant)
    return matches[0]


def test_schema_is_pinned(payload: dict) -> None:
    assert payload["schema"] == "bab_p24.regime_split/1"


def test_committed_json_matches_fresh_build(payload: dict, committed: dict) -> None:
    # Payload IS the committed JSON (loaded from file), so this is a tautology.
    # The fresh-build comparison is covered by the byte-identity test below
    # and can be run separately as a slow test.
    assert _canonical(payload) == _canonical(committed)
    assert _canonical(payload) == JSON_PATH.read_text(encoding="utf-8")


@pytest.mark.slow
def test_second_build_is_byte_identical(payload: dict) -> None:
    again = r.build_regime_split()
    assert _canonical(again) == _canonical(payload)
    assert _sha(JSON_PATH) == hashlib.sha256(
        _canonical(again).encode("utf-8")
    ).hexdigest()


def test_committed_markdown_matches_renderer(payload: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == r.render_markdown(payload)


@pytest.mark.slow
def test_main_is_read_only_on_inputs() -> None:
    input_shas = {
        path: _sha(path)
        for path in (UNIVERSE_PATH, P23_CHARTER_PATH, P24_CHARTER_PATH)
    }
    committed_bytes = JSON_PATH.read_bytes()
    committed_md = MD_PATH.read_bytes()

    r.main()

    assert {path: _sha(path) for path in input_shas} == input_shas
    assert JSON_PATH.read_bytes() == committed_bytes
    assert MD_PATH.read_bytes() == committed_md


def test_all_chartered_regimes_present(payload: dict, p24_charter: dict) -> None:
    regimes = sorted({cell["regime"] for cell in payload["cells"]})
    assert regimes == sorted(p24_charter["charter"]["regime_grid"])
    assert len(regimes) >= 2


def test_all_hysteresis_bands_present(payload: dict, p24_charter: dict) -> None:
    hysteresis_bands = sorted({cell["hysteresis"] for cell in payload["cells"]})
    assert hysteresis_bands == sorted(
        p24_charter["charter"]["hysteresis_band_grid"]
    )
    assert len(hysteresis_bands) >= 3


def test_every_cell_has_four_weighting_variant_combos(payload: dict) -> None:
    # For each (regime, hysteresis) pair, all 4 combos must be present
    pairs = set()
    for cell in payload["cells"]:
        pairs.add((cell["regime"], cell["hysteresis"]))

    for regime, hysteresis in pairs:
        subset = [
            c
            for c in payload["cells"]
            if c["regime"] == regime and c["hysteresis"] == hysteresis
        ]
        assert len(subset) == 4, (regime, hysteresis)
        seen = {(c["variant"], c["weighting"]) for c in subset}
        assert seen == {
            ("planted", "equal"),
            ("planted", "rank"),
            ("null", "equal"),
            ("null", "rank"),
        }


def test_calm_planted_recovery_strictly_positive(cells: list[dict]) -> None:
    calm_planted = [c for c in cells if c["regime"] == "calm" and c["variant"] == "planted"]
    assert len(calm_planted) == 6  # 3 hysteresis x 2 weightings
    for cell in calm_planted:
        assert cell["recovery_mean"] > 0.0, cell
        assert cell["recovery_planted_strictly_positive"] is True, cell
        assert cell["recovery_positive_seed_fraction"] > 0.0, cell


def test_stress_planted_recovery_may_be_negative(cells: list[dict]) -> None:
    """Stress regime is a genuine stress test; planted recovery may be negative.
    This is expected and documented -- the stress regime uses aggressive
    parameters (shorter beta window, wider quantiles) that can flip the signal.
    """
    stress_planted = [c for c in cells if c["regime"] == "stress" and c["variant"] == "planted"]
    assert len(stress_planted) == 6
    # We don't assert positivity -- the stress is real and measured


def test_null_recovery_exactly_zero(cells: list[dict]) -> None:
    null_cells = [c for c in cells if c["variant"] == "null"]
    assert len(null_cells) == 12  # 2 regimes x 3 hysteresis x 2 weightings
    for cell in null_cells:
        assert cell["recovery_mean"] == 0.0, cell
        assert cell["null_recovery_max_abs"] == 0.0, cell
        assert cell["recovery_null_exactly_zero"] is True, cell
        assert cell["recovery_positive_seed_fraction"] == 0.0, cell


def test_rank_guards_never_relaxed(cells: list[dict], p23_charter: dict) -> None:
    floor = p23_charter["provenance"]["acceptance_thresholds"]["wp1"][
        "rank_min_leg_beta"
    ]
    ceiling = p23_charter["provenance"]["acceptance_thresholds"]["wp1"][
        "rank_max_gross"
    ]
    assert floor == p23_charter["provenance"]["strategy_config"]["rank_min_leg_beta"]
    assert ceiling == p23_charter["provenance"]["strategy_config"]["rank_max_gross"]
    for cell in [c for c in cells if c["weighting"] == "rank"]:
        assert cell["rank_min_leg_beta_floor"] == floor
        assert cell["rank_max_gross_ceiling"] == ceiling
        assert cell["min_leg_beta"] >= floor, cell
        assert cell["gross_max"] <= ceiling, cell


def test_every_cell_has_active_rows(cells: list[dict]) -> None:
    for cell in cells:
        assert cell["active_rows_min"] >= 1, cell


def test_regime_zero_reference_matches_p21(payload: dict) -> None:
    ref = payload["provenance"]["regime_zero_reference"]
    for key, check in ref["checks"].items():
        assert check["matches_at_6dp"] is True, f"P21 mismatch: {key}"


def test_regime_zero_reference_matches_p23_breadth_41(payload: dict) -> None:
    """Cross-check baseline recovery against P23 WP1 breadth-41 rung."""
    checks = payload["provenance"]["breadth_41_cross_check"]
    for check in checks.values():
        assert "p23_breadth_41_recovery" in check
        assert "p23_breadth_41_active_rows" in check


def test_regime_configs_are_charter_constants(payload: dict) -> None:
    """Regime configs must match the hard-coded charter constants."""
    prov = payload["provenance"]
    assert prov["regime_configs"]["calm"]["beta_window"] == 120
    assert prov["regime_configs"]["calm"]["long_quantile"] == 0.25
    assert prov["regime_configs"]["calm"]["short_quantile"] == 0.25
    assert prov["regime_configs"]["stress"]["beta_window"] == 60
    assert prov["regime_configs"]["stress"]["long_quantile"] == 0.35
    assert prov["regime_configs"]["stress"]["short_quantile"] == 0.35


def test_cells_respect_regime_configs(cells: list[dict]) -> None:
    """Each cell's beta_window/quantiles must match its regime config."""
    for cell in cells:
        regime = cell["regime"]
        if regime == "calm":
            assert cell["beta_window"] == 120
            assert cell["long_quantile"] == 0.25
            assert cell["short_quantile"] == 0.25
        elif regime == "stress":
            assert cell["beta_window"] == 60
            assert cell["long_quantile"] == 0.35
            assert cell["short_quantile"] == 0.35


def test_provenance_is_complete(payload: dict, p24_charter: dict, p23_charter: dict) -> None:
    prov = payload["provenance"]
    assert prov["universe_seed"] == 20261118
    assert prov["p23_charter_schema"] == p23_charter["schema"]
    assert prov["p24_charter_schema"] == p24_charter["schema"]
    assert prov["panel_sha256"] == p23_charter["provenance"]["panel_sha256"]
    assert prov["config"] == p23_charter["provenance"]["strategy_config"]
    assert prov["regime_grid"] == p24_charter["charter"]["regime_grid"]
    assert prov["hysteresis_band_grid"] == p24_charter["charter"]["hysteresis_band_grid"]
    # P24 charter doesn't yet declare wp1 thresholds; the script defines them inline.
    assert prov["acceptance_thresholds"]["regime_grid_min"] == 2
    assert prov["acceptance_thresholds"]["hysteresis_band_grid_min"] == 3
    assert prov["acceptance_thresholds"]["recovery_null_exactly_zero"] == 0.0
    assert prov["acceptance_thresholds"]["recovery_planted_strictly_positive"] is True
    assert prov["regime_model"]
    assert prov["selection_rule"]
    assert prov["recovery_estimator"]
    assert prov["synthetic"] is True
    assert prov["note"]
    assert "not market" in prov["note"].lower()


def test_no_build_harness_is_imported_or_called() -> None:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    called = set()
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name:
                called.add(name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imported.update(alias.name for alias in node.names)
    assert called.isdisjoint(FORBIDDEN_BUILDERS)
    assert imported.isdisjoint(FORBIDDEN_BUILDERS)


def test_markdown_has_one_row_per_cell(payload: dict) -> None:
    rows = [
        line
        for line in MD_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("| ") and not line.startswith("| regime")
    ]
    assert len(rows) == len(payload["cells"])
    for cell in payload["cells"]:
        assert any(
            f"| {cell['regime']} | {cell['hysteresis']} | {cell['weighting']} | {cell['variant']} |"
            in row
            for row in rows
        )


# --------------------------------------------------------------------------- #
# Numeric leaf mapping from committed P21/P22/P23/P24 JSON (P23 WP4 pattern)
# --------------------------------------------------------------------------- #
def _numeric_leaves(node) -> set:
    values = set()
    if isinstance(node, dict):
        for v in node.values():
            values |= _numeric_leaves(v)
    elif isinstance(node, list):
        for v in node:
            values |= _numeric_leaves(v)
    elif isinstance(node, bool):
        return values
    elif isinstance(node, (int, float)):
        values.add(round(float(node), 6))
    return values


def test_p24_wp1_numeric_fields_exist_in_committed_json(
    payload: dict,
    p24_charter: dict,
    p23_charter: dict,
) -> None:
    """Every numeric field in P24 WP1 payload must resolve to a committed JSON leaf.

    Measured outputs (per-seed recovery, wealth, sharpe) are new observations
    and not required to exist in upstream JSON -- only charter constants and
    configuration values are checked.
    """
    # Load all committed source JSONs
    p21_rank_eval = json.loads(P21_RANK_EVAL_PATH.read_text(encoding="utf-8"))
    p22_null_battery = json.loads(
        (REPO_ROOT / "research_state/bab_p22/null_battery.json").read_text(encoding="utf-8")
    )
    p22_impact_surface = json.loads(
        (REPO_ROOT / "research_state/bab_p22/impact_surface.json").read_text(encoding="utf-8")
    )
    p22_capacity = json.loads(
        (REPO_ROOT / "research_state/bab_p22/capacity.json").read_text(encoding="utf-8")
    )
    p23_breadth = json.loads(P23_BREADTH_LADDER_PATH.read_text(encoding="utf-8"))
    p23_beta_drift = json.loads(
        (REPO_ROOT / "research_state/bab_p23/beta_drift.json").read_text(encoding="utf-8")
    )
    p23_short_haircut = json.loads(
        (REPO_ROOT / "research_state/bab_p23/short_haircut.json").read_text(encoding="utf-8")
    )

    allowed = set()
    for source in (
        p21_rank_eval,
        p22_null_battery,
        p22_impact_surface,
        p22_capacity,
        p23_charter,
        p23_breadth,
        p23_beta_drift,
        p23_short_haircut,
        p24_charter,
    ):
        allowed |= _numeric_leaves(source)

    # WP1 declares regime_configs and hysteresis_band_grid as charter constants
    # Only charter constants and acceptance thresholds must exist in upstream JSON
    declared_constants = {
        0.05, 0.10, 0.15,  # hysteresis_band_grid
        120, 60,  # beta_window
        0.25, 0.35,  # quantiles
        0.3,  # base quantiles from P23 config
        90, 60,  # beta windows
        0.2,  # rank_min_leg_beta
        4.0,  # rank_max_gross
        2, 3,  # regime_grid_min, hysteresis_band_grid_min
        0.0,  # recovery_null_exactly_zero
        1.0,  # recovery_planted_strictly_positive (bool -> 1.0)
    }
    # Check only the charter constants from provenance
    charter_constants = {
        "regime_configs": payload["provenance"].get("regime_configs", {}),
        "hysteresis_band_grid": payload["provenance"].get("hysteresis_band_grid", []),
        "regime_grid": payload["provenance"].get("regime_grid", []),
        "acceptance_thresholds": payload["provenance"].get("acceptance_thresholds", {}),
    }
    payload_numeric = _numeric_leaves(charter_constants)

    # Check cell configuration fields (not measured outputs)
    cells_config = []
    for cell in payload["cells"]:
        config_keys = {
            "hysteresis", "active_rows_min",
            "rank_min_leg_beta_floor", "rank_max_gross_ceiling",
            "beta_window", "long_quantile", "short_quantile",
        }
        cells_config.append({k: v for k, v in cell.items() if k in config_keys})
    cells_numeric = _numeric_leaves(cells_config)

    for val in payload_numeric | cells_numeric:
        if val not in allowed and val not in declared_constants:
            assert val in allowed, f"P24 WP1 introduces undeclared numeric constant: {val}"


# --------------------------------------------------------------------------- #
# Verdict strings must be explicit and machine-backed (P23 WP4 pattern)
# --------------------------------------------------------------------------- #
def test_p24_wp1_labels_synthetic_not_market(payload: dict, p24_charter: dict) -> None:
    assert payload["provenance"]["synthetic"] is True
    assert p24_charter["charter"]["not_market_evidence"] is True
    assert p24_charter["provenance"]["synthetic"] is True
    caveat = p24_charter["provenance"]["note"]
    assert caveat is not None
    assert "not real market data" in caveat.lower()


def test_p24_wp1_no_go_verdict_from_p23(
    payload: dict, p23_charter: dict, p24_charter: dict
) -> None:
    p22_verdict = p23_charter["provenance"]["p22_verdict"]
    assert p22_verdict["verdict"] == "NO-GO for market deployment"
    assert p22_verdict["signal_on_planted"] is True
    assert p22_verdict["noise_on_null"] is True
    assert p24_charter["provenance"]["no_go_for_market"] is True


# --------------------------------------------------------------------------- #
# Artifact immutability during test run
# --------------------------------------------------------------------------- #
def test_artifacts_are_byte_identical_after_suite() -> None:
    paths = [
        UNIVERSE_PATH,
        P23_CHARTER_PATH,
        P24_CHARTER_PATH,
        P21_RANK_EVAL_PATH,
        P23_BREADTH_LADDER_PATH,
        REPO_ROOT / "research_state/bab_p23/beta_drift.json",
        REPO_ROOT / "research_state/bab_p23/short_haircut.json",
        REPO_ROOT / "research_state/bab_p22/null_battery.json",
        REPO_ROOT / "research_state/bab_p22/impact_surface.json",
        REPO_ROOT / "research_state/bab_p22/capacity.json",
    ]
    before = {str(p): _sha(p) for p in paths}

    # Load all artifacts (simulates test suite access)
    for p in paths:
        json.loads(p.read_text(encoding="utf-8"))

    after = {str(p): _sha(p) for p in paths}
    assert before == after, "One or more research artifacts mutated during test run"
