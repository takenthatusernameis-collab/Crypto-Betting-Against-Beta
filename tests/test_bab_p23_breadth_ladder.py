"""Acceptance tests for P23 WP1: the breadth ladder.

These tests are the claim that ``scripts/bab_breadth_ladder.py`` produces a
deterministic, chartered breadth ladder (``research_state/bab_p23/
breadth_ladder.json``) from the committed P21 universe and the committed P23
charter, both read-only. They prove the mechanical contract the charter
declares:

* every chartered rung is present with all four certified books;
* planted recovery is strictly positive on every rung for both weightings;
* null recovery is exactly ``0.0`` on every rung for both weightings;
* rank-leg guards (``min_leg_beta >= 0.2``, ``gross_max <= 4.0``) hold on
  every active rank row and are never relaxed;
* every rung has at least one active row;
* committed JSON equals a fresh build; markdown equals the renderer output;
* a second build is byte-identical;
* the inputs are byte-identical before and after ``main()``;
* the harness never imports or calls a P21/P22/P23 build function.

The breadth-41 rung is cross-checked against the committed P21 rank-eval
artifact, so the ladder cannot drift from its upstream reference.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from scripts import bab_breadth_ladder as b

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
CHARTER_PATH = REPO_ROOT / "research_state/bab_p23/charter.json"
JSON_PATH = REPO_ROOT / "research_state/bab_p23/breadth_ladder.json"
MD_PATH = REPO_ROOT / "research_state/bab_p23/breadth_ladder.md"
P21_RANK_EVAL_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.json"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_breadth_ladder.py"

FORBIDDEN_BUILDERS = (
    "build_universe",
    "build_rank_eval",
    "build_null_battery",
    "build_impact_surface",
    "build_capacity",
    "build_significance",
    "build_synthetic_universe",
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
    return b.build_breadth_ladder()


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def books(payload: dict) -> list[dict]:
    return [book for rung in payload["ladder"] for book in rung["books"]]


def _book(books, variant, weighting, breadth=None):
    matches = [
        book
        for book in books
        if book["variant"] == variant
        and book["weighting"] == weighting
        and (breadth is None or book["breadth"] == breadth)
    ]
    assert len(matches) == 1, (variant, weighting, breadth)
    return matches[0]


def test_schema_is_pinned(payload: dict) -> None:
    assert payload["schema"] == "bab_p23.breadth_ladder/1"


def test_committed_json_matches_fresh_build(payload: dict, committed: dict) -> None:
    assert _canonical(payload) == _canonical(committed)
    assert _canonical(payload) == JSON_PATH.read_text(encoding="utf-8")


def test_second_build_is_byte_identical(payload: dict) -> None:
    again = b.build_breadth_ladder()
    assert _canonical(again) == _canonical(payload)
    assert _sha(JSON_PATH) == hashlib.sha256(
        _canonical(again).encode("utf-8")
    ).hexdigest()


def test_committed_markdown_matches_renderer(payload: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == b.render_markdown(payload)


def test_main_is_read_only_on_inputs() -> None:
    input_shas = {path: _sha(path) for path in (UNIVERSE_PATH, CHARTER_PATH)}
    committed_bytes = JSON_PATH.read_bytes()
    committed_md = MD_PATH.read_bytes()

    b.main()

    assert {path: _sha(path) for path in input_shas} == input_shas
    assert JSON_PATH.read_bytes() == committed_bytes
    assert MD_PATH.read_bytes() == committed_md


def test_all_chartered_rungs_present(payload: dict, charter: dict) -> None:
    ladder = [rung["breadth"] for rung in payload["ladder"]]
    assert ladder == list(charter["charter"]["breadth_ladder"])
    assert len(ladder) >= charter["provenance"]["acceptance_thresholds"]["wp1"][
        "ladder_min_rungs"
    ]
    assert payload["provenance"]["derived"]["ladder_min_rungs_met"] is True


def test_every_rung_has_four_books(payload: dict) -> None:
    for rung in payload["ladder"]:
        assert len(rung["books"]) == 4
        seen = {(book["variant"], book["weighting"]) for book in rung["books"]}
        assert seen == {
            ("planted", "equal"),
            ("planted", "rank"),
            ("null", "equal"),
            ("null", "rank"),
        }


def test_rung_assets_preserve_beta_span(payload: dict, charter: dict) -> None:
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    betas = universe["betas"]
    for rung in payload["ladder"]:
        assets = rung["books"][0]["assets"]
        assert len(assets) == rung["breadth"]
        assert assets == sorted(set(assets))
        span = [betas[a] for a in assets]
        assert span[0] == min(span) and span[-1] == max(span)
        assert span[0] == pytest.approx(
            universe["provenance"]["beta_min"], abs=1e-9
        )
        assert span[-1] == pytest.approx(
            universe["provenance"]["beta_max"], abs=1e-9
        )


def test_planted_recovery_strictly_positive(books: list[dict]) -> None:
    planted = [book for book in books if book["variant"] == "planted"]
    assert len(planted) == 10
    for book in planted:
        assert book["recovery_mean"] > 0.0, book
        assert book["recovery_frac_positive"] > 0.0, book


def test_null_recovery_exactly_zero(books: list[dict]) -> None:
    null_books = [book for book in books if book["variant"] == "null"]
    assert len(null_books) == 10
    for book in null_books:
        assert book["recovery_mean"] == 0.0, book
        assert book["recovery_frac_positive"] == 0.0, book


def test_rank_guards_never_relaxed(books: list[dict], charter: dict) -> None:
    floor = charter["provenance"]["acceptance_thresholds"]["wp1"][
        "rank_min_leg_beta"
    ]
    ceiling = charter["provenance"]["acceptance_thresholds"]["wp1"][
        "rank_max_gross"
    ]
    assert floor == charter["provenance"]["strategy_config"]["rank_min_leg_beta"]
    assert ceiling == charter["provenance"]["strategy_config"]["rank_max_gross"]
    for book in [item for item in books if item["weighting"] == "rank"]:
        assert book["rank_min_leg_beta_floor"] == floor
        assert book["rank_max_gross_ceiling"] == ceiling
        assert book["min_leg_beta"] >= floor, book
        assert book["gross_max"] <= ceiling, book


def test_every_rung_has_active_rows(books: list[dict], charter: dict) -> None:
    minimum = charter["provenance"]["acceptance_thresholds"]["wp1"][
        "min_active_rows"
    ]
    for book in books:
        assert book["active_rows"] >= minimum, book


def test_breadth_41_matches_committed_p21_rank_eval(books: list[dict]) -> None:
    p21 = json.loads(P21_RANK_EVAL_PATH.read_text(encoding="utf-8"))
    for reference in p21["books"]:
        book = _book(
            books, reference["variant"], reference["weighting"], breadth=41
        )
        assert book["active_rows"] == reference["active_rows"]
        assert book["recovery_mean"] == reference["recovery_mean"]
        assert book["min_leg_beta"] == round(reference["min_leg_beta"], 6)


def test_provenance_is_complete(payload: dict, charter: dict) -> None:
    prov = payload["provenance"]
    assert prov["universe_seed"] == 20261118
    assert prov["charter_schema"] == charter["schema"]
    assert prov["panel_sha256"] == charter["provenance"]["panel_sha256"]
    assert prov["config"] == charter["provenance"]["strategy_config"]
    assert prov["breadth_ladder"] == charter["charter"]["breadth_ladder"]
    assert prov["acceptance_thresholds"] == charter["provenance"][
        "acceptance_thresholds"
    ]["wp1"]
    assert prov["selection_rule"]
    assert prov["recovery_estimator"]
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


def test_markdown_has_one_row_per_book(payload: dict) -> None:
    rows = [
        line
        for line in MD_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("| ") and not line.startswith("| breadth")
    ]
    assert len(rows) == 20
    for rung in payload["ladder"]:
        for book in rung["books"]:
            assert any(
                f"| {book['breadth']} | {book['variant']} | {book['weighting']} |"
                in row
                for row in rows
            )
