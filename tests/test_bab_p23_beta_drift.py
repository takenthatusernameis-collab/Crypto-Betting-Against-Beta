"""Acceptance tests for P23 WP2: the beta-window/drift grid.

These tests are the claim that ``scripts/bab_beta_drift.py`` produces a
deterministic, chartered beta-window/drift grid
(``research_state/bab_p23/beta_drift.json``) from the committed P21 universe,
the committed P23 charter and the committed P23 breadth ladder, all read-only.
They prove the mechanical contract the charter declares:

* all 4 beta windows x 3 drift thresholds x 2 weightings x 2 variants =
  48 cells are present, each carrying 20 per-seed recovery values;
* planted recovery is strictly positive on every seed in every cell for both
  weightings;
* null recovery is exactly ``0.0`` on every seed in every cell for both
  weightings;
* rank-leg guards (``min_leg_beta >= 0.2``, ``gross_max <= 4.0``) hold on
  every active rank row and are never relaxed;
* the ``drift_zero_reference`` at ``delta=0, beta_window=90`` equals the
  committed P21 ``rank_eval.json`` values at 6 dp;
* committed JSON equals a fresh build; markdown equals the renderer output;
* a second build is byte-identical;
* the inputs are byte-identical before and after ``main()``;
* the harness never imports or calls a P21/P22/P23 build function.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from scripts import bab_beta_drift as b

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
CHARTER_PATH = REPO_ROOT / "research_state/bab_p23/charter.json"
BREADTH_LADDER_PATH = REPO_ROOT / "research_state/bab_p23/breadth_ladder.json"
P21_RANK_EVAL_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.json"
JSON_PATH = REPO_ROOT / "research_state/bab_p23/beta_drift.json"
MD_PATH = REPO_ROOT / "research_state/bab_p23/beta_drift.md"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_beta_drift.py"

FORBIDDEN_BUILDERS = (
    "build_universe",
    "build_rank_eval",
    "build_null_battery",
    "build_impact_surface",
    "build_capacity",
    "build_significance",
    "build_synthetic_universe",
    "build_breadth_ladder",
    "build_charter",
    "build_beta_drift",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


@pytest.fixture(scope="module")
def charter() -> dict:
    return json.loads(CHARTER_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def breadth_ladder() -> dict:
    return json.loads(BREADTH_LADDER_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def payload() -> dict:
    return b.build_beta_drift()


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def test_schema_is_pinned(payload: dict) -> None:
    assert payload["schema"] == "bab_p23.beta_drift/1"


def test_committed_json_matches_fresh_build(payload: dict, committed: dict) -> None:
    assert _canonical(payload) == _canonical(committed)
    assert _canonical(payload) == JSON_PATH.read_text(encoding="utf-8")


def test_second_build_is_byte_identical(payload: dict) -> None:
    again = b.build_beta_drift()
    assert _canonical(again) == _canonical(payload)
    assert _sha(JSON_PATH) == hashlib.sha256(
        _canonical(again).encode("utf-8")
    ).hexdigest()


def test_committed_markdown_matches_renderer(payload: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == b.render_markdown(payload)


def test_main_is_read_only_on_inputs() -> None:
    input_shas = {
        path: _sha(path)
        for path in (UNIVERSE_PATH, CHARTER_PATH, BREADTH_LADDER_PATH)
    }
    committed_bytes = JSON_PATH.read_bytes()
    committed_md = MD_PATH.read_bytes()

    b.main()

    assert {path: _sha(path) for path in input_shas} == input_shas
    assert JSON_PATH.read_bytes() == committed_bytes
    assert MD_PATH.read_bytes() == committed_md


def test_all_chartered_cells_present(payload: dict, charter: dict) -> None:
    beta_windows = charter["charter"]["beta_window_grid"]
    drift_thresholds = charter["charter"]["drift_threshold_grid"]
    expected = 4 * 3 * 2 * 2
    assert len(payload["cells"]) == expected, len(payload["cells"])
    seen = {
        (cell["beta_window"], cell["drift_threshold"], cell["weighting"], cell["variant"])
        for cell in payload["cells"]
    }
    expected_set = {
        (bw, dt, w, v)
        for bw in beta_windows
        for dt in drift_thresholds
        for w in ("equal", "rank")
        for v in ("planted", "null")
    }
    assert seen == expected_set


def test_every_cell_carries_20_per_seed_values(payload: dict, charter: dict) -> None:
    n_seeds = len(charter["charter"]["wp_seeds"]["wp2"])
    for cell in payload["cells"]:
        assert len(cell["per_seed_recovery"]) == n_seeds, cell


def test_beta_window_default_preserved(payload: dict, charter: dict) -> None:
    windows = {cell["beta_window"] for cell in payload["cells"]}
    assert 90 in windows
    assert payload["provenance"]["derived"]["beta_window_default_preserved"] is True


def test_min_beta_windows_and_drift_thresholds(payload: dict, charter: dict) -> None:
    thresholds = charter["provenance"]["acceptance_thresholds"]["wp2"]
    assert len({cell["beta_window"] for cell in payload["cells"]}) >= thresholds[
        "min_beta_windows"
    ]
    assert len({cell["drift_threshold"] for cell in payload["cells"]}) >= thresholds[
        "min_drift_thresholds"
    ]
    assert payload["provenance"]["derived"]["min_beta_windows_met"] is True
    assert payload["provenance"]["derived"]["min_drift_thresholds_met"] is True


def test_planted_recovery_strictly_positive(payload: dict) -> None:
    planted = [cell for cell in payload["cells"] if cell["variant"] == "planted"]
    assert len(planted) == 24, len(planted)
    for cell in planted:
        assert cell["recovery_planted_strictly_positive"] is True, cell
        assert cell["recovery_mean"] > 0.0, cell
        assert cell["recovery_min"] > 0.0, cell
        for value in cell["per_seed_recovery"]:
            assert value > 0.0, cell


def test_null_recovery_exactly_zero(payload: dict) -> None:
    nulls = [cell for cell in payload["cells"] if cell["variant"] == "null"]
    assert len(nulls) == 24, len(nulls)
    for cell in nulls:
        assert cell["recovery_null_exactly_zero"] is True, cell
        assert cell["recovery_mean"] == 0.0, cell
        assert cell["null_recovery_max_abs"] == 0.0, cell
        for value in cell["per_seed_recovery"]:
            assert value == 0.0, cell


def test_rank_guards_never_relaxed(payload: dict, charter: dict) -> None:
    floor = charter["provenance"]["acceptance_thresholds"]["wp2"][
        "rank_min_leg_beta"
    ] if "rank_min_leg_beta" in charter["provenance"]["acceptance_thresholds"]["wp2"] else charter["provenance"]["strategy_config"]["rank_min_leg_beta"]
    ceiling = charter["provenance"]["strategy_config"]["rank_max_gross"]
    assert floor == charter["provenance"]["strategy_config"]["rank_min_leg_beta"]
    assert ceiling == charter["provenance"]["strategy_config"]["rank_max_gross"]
    for cell in [c for c in payload["cells"] if c["weighting"] == "rank"]:
        assert cell["rank_min_leg_beta_floor"] == floor, cell
        assert cell["rank_max_gross_ceiling"] == ceiling, cell
        assert cell["min_leg_beta"] >= floor, cell
        assert cell["gross_max"] <= ceiling, cell


def test_drift_zero_reference_matches_p21_rank_eval(payload: dict) -> None:
    p21 = json.loads(P21_RANK_EVAL_PATH.read_text(encoding="utf-8"))
    p21_books = {(b["variant"], b["weighting"]): b for b in p21["books"]}
    ref = payload["provenance"]["drift_zero_reference"]
    assert ref["beta_window"] == 90
    assert ref["drift_threshold"] == 0.0
    assert ref["breadth"] == 41
    for key_str, check in ref["checks"].items():
        variant, weighting = key_str.split("_")
        p21_book = p21_books[(variant, weighting)]
        assert check["committed_p21_recovery"] == p21_book["recovery_mean"], key_str
        assert check["drift_zero_recovery"] == p21_book["recovery_mean"], key_str
        assert check["matches_at_6dp"] is True, key_str


def test_provenance_is_complete(payload: dict, charter: dict) -> None:
    prov = payload["provenance"]
    assert prov["universe_seed"] == 20261118
    assert prov["charter_schema"] == charter["schema"]
    assert prov["panel_sha256"] == charter["provenance"]["panel_sha256"]
    assert prov["config"] == charter["provenance"]["strategy_config"]
    assert prov["beta_window_grid"] == charter["charter"]["beta_window_grid"]
    assert prov["drift_threshold_grid"] == charter["charter"]["drift_threshold_grid"]
    assert prov["wp_seeds"] == charter["charter"]["wp_seeds"]["wp2"]
    assert prov["acceptance_thresholds"] == charter["provenance"][
        "acceptance_thresholds"
    ]["wp2"]
    assert prov["selection_rule"]
    assert prov["recovery_estimator"]
    assert prov["drift_model"]
    assert prov["drift_zero_reference"]["beta_window"] == 90
    assert prov["drift_zero_reference"]["breadth"] == 41
    assert prov["synthetic"] is True


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
        if line.startswith("| ") and not line.startswith("| beta_window")
    ]
    assert len(rows) == len(payload["cells"]), (len(rows), len(payload["cells"]))
    for cell in payload["cells"]:
        assert any(
            f"| {cell['beta_window']} | {cell['drift_threshold']} | {cell['weighting']} | {cell['variant']} |"
            in row
            for row in rows
        )
