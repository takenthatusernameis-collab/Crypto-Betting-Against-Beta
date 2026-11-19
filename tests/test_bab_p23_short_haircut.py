"""Acceptance tests for P23 WP3: the short-availability haircut ladder.

These tests are the claim that ``scripts/bab_short_haircut.py`` produces a
deterministic, chartered short-availability haircut ladder
(``research_state/bab_p23/short_haircut.json``) from the committed P21
universe, the committed P23 charter, the committed P23 breadth ladder and the
committed P23 WP2 beta-drift artifact, all read-only. They prove the
mechanical contract the charter declares:

* all 5 haircuts x 2 weightings x 2 variants = 20 cells are present, each
  carrying 20 per-seed recovery, costed-Sharpe and availability values;
* planted recovery is strictly positive on every seed in every non-censored
  planted cell (censored cells stay visible with a machine-readable reason and
  only their fully-degenerate seeds read zero);
* null recovery is exactly ``0.0`` on every seed in every cell;
* ``costed_sharpe`` is non-increasing along ``[0.0, 0.1, 0.25, 0.5, 0.75]``
  for every book and is seed-invariant by construction (fee-only);
* availability tracks ``1 - haircut`` within the chartered nominal slack and
  short survival never exceeds raw availability;
* the ``haircut_zero_reference`` equals the committed P21 ``rank_eval.json``
  and the committed WP2 ``drift_zero_reference`` at 6 dp;
* rank-leg guards (``min_leg_beta >= 0.2``, ``gross_max <= 4.0``) hold on every
  non-censored rank cell and are never relaxed;
* committed JSON equals a fresh build; markdown equals the renderer output;
* a second build is byte-identical;
* the four inputs are byte-identical before and after ``main()``;
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

from scripts import bab_short_haircut as b

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
CHARTER_PATH = REPO_ROOT / "research_state/bab_p23/charter.json"
BREADTH_LADDER_PATH = REPO_ROOT / "research_state/bab_p23/breadth_ladder.json"
BETA_DRIFT_PATH = REPO_ROOT / "research_state/bab_p23/beta_drift.json"
P21_RANK_EVAL_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.json"
JSON_PATH = REPO_ROOT / "research_state/bab_p23/short_haircut.json"
MD_PATH = REPO_ROOT / "research_state/bab_p23/short_haircut.md"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_short_haircut.py"

INPUT_PATHS = (UNIVERSE_PATH, CHARTER_PATH, BREADTH_LADDER_PATH, BETA_DRIFT_PATH)

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
    "build_charter",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


@pytest.fixture(scope="module")
def charter() -> dict:
    return json.loads(CHARTER_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def payload() -> dict:
    return b.build_short_haircut()


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def test_schema_is_pinned(payload: dict) -> None:
    assert payload["schema"] == "bab_p23.short_haircut/1"


def test_committed_json_matches_fresh_build(payload: dict, committed: dict) -> None:
    assert _canonical(payload) == _canonical(committed)
    assert _canonical(payload) == JSON_PATH.read_text(encoding="utf-8")


def test_second_build_is_byte_identical(payload: dict) -> None:
    again = b.build_short_haircut()
    assert _canonical(again) == _canonical(payload)
    assert _sha(JSON_PATH) == hashlib.sha256(
        _canonical(again).encode("utf-8")
    ).hexdigest()


def test_committed_markdown_matches_renderer(payload: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == b.render_markdown(payload)


def test_main_is_read_only_on_inputs() -> None:
    input_shas = {path: _sha(path) for path in INPUT_PATHS}
    committed_bytes = JSON_PATH.read_bytes()
    committed_md = MD_PATH.read_bytes()

    b.main()

    assert {path: _sha(path) for path in input_shas} == input_shas
    assert JSON_PATH.read_bytes() == committed_bytes
    assert MD_PATH.read_bytes() == committed_md


def test_all_chartered_cells_present(payload: dict, charter: dict) -> None:
    ladder = charter["charter"]["borrow_haircut_ladder"]
    expected_set = {
        (float(h), w, v)
        for h in ladder
        for w in ("equal", "rank")
        for v in ("planted", "null")
    }
    seen = {(cell["haircut"], cell["weighting"], cell["variant"]) for cell in payload["cells"]}
    assert len(payload["cells"]) == len(expected_set)
    assert seen == expected_set
    assert payload["provenance"]["derived"]["n_cells"] == len(expected_set)


def test_every_cell_carries_20_per_seed_values(payload: dict, charter: dict) -> None:
    n_seeds = len(charter["charter"]["wp_seeds"]["wp3"])
    for cell in payload["cells"]:
        for key in (
            "per_seed_recovery",
            "per_seed_costed_sharpe",
            "per_seed_availability_sharpe",
            "per_seed_availability",
            "per_seed_short_survival",
            "per_seed_active_rows",
            "per_seed_degenerate_rows",
        ):
            assert len(cell[key]) == n_seeds, (key, cell)


def test_haircut_ladder_minimums(payload: dict, charter: dict) -> None:
    thresholds = charter["provenance"]["acceptance_thresholds"]["wp3"]
    levels = {cell["haircut"] for cell in payload["cells"]}
    assert 0.0 in levels
    assert len(levels) >= thresholds["min_haircut_levels"]
    assert payload["provenance"]["derived"]["min_haircut_levels_met"] is True
    assert payload["provenance"]["derived"]["haircut_zero_present"] is True
    assert payload["provenance"]["derived"]["n_book_runs"] == len(payload["cells"]) * 20


def test_planted_recovery_strictly_positive_unless_censored(payload: dict) -> None:
    planted = [cell for cell in payload["cells"] if cell["variant"] == "planted"]
    assert len(planted) == 10, len(planted)
    for cell in planted:
        if cell["censored"]:
            assert cell["censor_reason"], cell
            zero_seeds = [
                seed
                for seed, value, degen in zip(
                    payload["provenance"]["wp_seeds"],
                    cell["per_seed_recovery"],
                    cell["per_seed_degenerate_rows"],
                )
                if value == 0.0
            ]
            assert zero_seeds, cell
            for value, degen in zip(
                cell["per_seed_recovery"], cell["per_seed_degenerate_rows"]
            ):
                if value == 0.0:
                    assert degen > 0, cell
            assert cell["recovery_planted_strictly_positive"] is False
            continue
        assert cell["recovery_planted_strictly_positive"] is True, cell
        assert cell["censor_reason"] is None, cell
        assert cell["recovery_mean"] > 0.0, cell
        assert cell["recovery_min"] > 0.0, cell
        assert cell["recovery_positive_seed_fraction"] == 1.0, cell
        for value in cell["per_seed_recovery"]:
            assert value > 0.0, cell


def test_null_recovery_exactly_zero(payload: dict) -> None:
    nulls = [cell for cell in payload["cells"] if cell["variant"] == "null"]
    assert len(nulls) == 10, len(nulls)
    for cell in nulls:
        assert cell["recovery_null_exactly_zero"] is True, cell
        assert cell["recovery_mean"] == 0.0, cell
        assert cell["null_recovery_max_abs"] == 0.0, cell
        for value in cell["per_seed_recovery"]:
            assert value == 0.0, cell


def test_costed_sharpe_non_increasing_along_ladder(payload: dict) -> None:
    ladder = payload["provenance"]["borrow_haircut_ladder"]
    for weighting in ("equal", "rank"):
        for variant in ("planted", "null"):
            book = [
                cell
                for cell in payload["cells"]
                if cell["weighting"] == weighting and cell["variant"] == variant
            ]
            book = sorted(book, key=lambda c: c["haircut"])
            assert [c["haircut"] for c in book] == [float(h) for h in ladder]
            means = [c["costed_sharpe_mean"] for c in book]
            for i in range(len(means) - 1):
                assert means[i + 1] <= means[i] + 1e-12, (weighting, variant, means)
            for cell in book:
                assert cell["costed_sharpe_non_increasing"] is True, cell
                assert cell["costed_sharpe_min"] <= cell["costed_sharpe_mean"] + 1e-12
                for value in cell["per_seed_costed_sharpe"]:
                    assert value == cell["per_seed_costed_sharpe"][0], cell


def test_censored_cells_are_visible_with_reason(payload: dict) -> None:
    for cell in payload["cells"]:
        if cell["censored"]:
            assert isinstance(cell["censor_reason"], str) and cell["censor_reason"]
            assert cell["active_rows_min"] == 0, cell
        else:
            assert cell["censor_reason"] is None, cell
            assert cell["active_rows_min"] > 0, cell


def test_availability_matches_haircut_within_slack(payload: dict) -> None:
    slack = payload["provenance"]["nominal_slack"]
    assert slack == 0.05
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    n_assets = len(universe["assets"])
    seeds = payload["provenance"]["wp_seeds"]
    for cell in payload["cells"]:
        assert abs(cell["availability_mean"] - (1.0 - cell["haircut"])) <= slack, cell
        expected = [
            round(
                float(b.availability_mask(seed, n_assets, cell["haircut"]).mean()), 6
            )
            for seed in seeds
        ]
        assert cell["per_seed_availability"] == expected, cell
        assert cell["short_survival_mean"] <= cell["availability_mean"] + 1e-6, cell


def test_rank_guards_never_relaxed(payload: dict, charter: dict) -> None:
    config = charter["provenance"]["strategy_config"]
    floor = config["rank_min_leg_beta"]
    ceiling = config["rank_max_gross"]
    rank_cells = [c for c in payload["cells"] if c["weighting"] == "rank"]
    assert len(rank_cells) == 10
    for cell in rank_cells:
        assert cell["rank_min_leg_beta_floor"] == floor, cell
        assert cell["rank_max_gross_ceiling"] == ceiling, cell
        if cell["censored"]:
            continue
        assert cell["min_leg_beta"] >= floor, cell
        assert cell["gross_max"] <= ceiling, cell


def test_haircut_zero_reference_matches_p21_and_wp2(payload: dict) -> None:
    p21 = json.loads(P21_RANK_EVAL_PATH.read_text(encoding="utf-8"))
    p21_books = {(b["variant"], b["weighting"]): b for b in p21["books"]}
    wp2 = json.loads(BETA_DRIFT_PATH.read_text(encoding="utf-8"))
    wp2_checks = wp2["provenance"]["drift_zero_reference"]["checks"]

    ref = payload["provenance"]["haircut_zero_reference"]
    assert ref["haircut"] == 0.0
    assert ref["breadth"] == 41
    assert len(ref["checks"]) == 4
    for key_str, check in ref["checks"].items():
        variant, weighting = key_str.split("_")
        p21_book = p21_books[(variant, weighting)]
        assert check["committed_p21_recovery"] == p21_book["recovery_mean"], key_str
        assert (
            check["committed_wp2_drift_zero_recovery"]
            == wp2_checks[key_str]["drift_zero_recovery"]
        ), key_str
        assert check["haircut_zero_recovery"] == p21_book["recovery_mean"], key_str
        assert check["haircut_zero_recovery"] == wp2_checks[key_str]["drift_zero_recovery"], key_str
        assert check["matches_p21_at_6dp"] is True, key_str
        assert check["matches_wp2_at_6dp"] is True, key_str


def test_provenance_is_complete(payload: dict, charter: dict) -> None:
    prov = payload["provenance"]
    assert prov["universe_seed"] == 20261118
    assert prov["charter_schema"] == charter["schema"]
    assert prov["panel_sha256"] == charter["provenance"]["panel_sha256"]
    assert prov["config"] == charter["provenance"]["strategy_config"]
    assert prov["borrow_haircut_ladder"] == charter["charter"]["borrow_haircut_ladder"]
    assert prov["wp_seeds"] == charter["charter"]["wp_seeds"]["wp3"]
    assert prov["acceptance_thresholds"] == charter["provenance"][
        "acceptance_thresholds"
    ]["wp3"]
    assert prov["availability_rule"]
    assert prov["cost_rule"]
    assert prov["haircut_semantics"]
    assert prov["recovery_estimator"]
    assert prov["selection_rule"]
    assert prov["beta_drift_schema"]
    assert prov["synthetic"] is True


def test_no_upstream_build_harness_is_imported_or_called() -> None:
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
        if line.startswith("| ") and not line.startswith("| haircut")
    ]
    assert len(rows) == len(payload["cells"]), (len(rows), len(payload["cells"]))
    for cell in payload["cells"]:
        prefix = (
            f"| {cell['haircut']} | {cell['weighting']} | {cell['variant']} |"
        )
        assert any(prefix in row for row in rows)
