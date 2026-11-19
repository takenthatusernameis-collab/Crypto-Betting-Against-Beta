"""Acceptance tests for P22 WP1: the null battery over the chartered seeds.

These tests are the claim that ``scripts/bab_null_battery.py``:

* consumes the ``research_state/bab_p22/charter.json`` seed list, nominal slack
  and bootstrap thresholds read-only;
* runs the planted/null universe pair for **every** chartered seed (>= 20);
* publishes null recovery that is **exactly zero** for every null book (a
  non-zero null is a bug, not a finding);
* publishes an empirical false-positive rate that is computed as
  ``significant null books / null books`` and stays honest even when it
  exceeds the nominal slack;
* publishes planted recovery that is strictly positive on the documented
  fraction;
* reproduces the committed P21 panel sha256 values at the reference seed,
  proving it drives the same synthetic generator without re-running (or
  editing) any P21 harness;
* is byte-identical across reruns and renders its markdown from JSON only.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import bab_null_battery as b

REPO_ROOT = Path(__file__).resolve().parent.parent
BATTERY_PATH = REPO_ROOT / "research_state/bab_p22/null_battery.json"
BATTERY_MD_PATH = REPO_ROOT / "research_state/bab_p22/null_battery.md"
CHARTER_PATH = REPO_ROOT / "research_state/bab_p22/charter.json"
P21_UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def charter() -> dict:
    return _load(CHARTER_PATH)


@pytest.fixture(scope="module")
def battery() -> dict:
    return b.build_null_battery()


@pytest.fixture(scope="module")
def battery_again(battery: dict) -> dict:
    return b.build_null_battery()


@pytest.fixture(scope="module")
def committed_battery() -> dict:
    return _load(BATTERY_PATH)


@pytest.fixture(scope="module")
def battery_md() -> str:
    return BATTERY_MD_PATH.read_text(encoding="utf-8")


def test_schema_and_provenance(battery: dict) -> None:
    assert battery["schema"] == b.SCHEMA == "bab_p22.null_battery/1"
    prov = battery["provenance"]
    assert prov["generator"] == "scripts/bab_null_battery.py"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert prov["source_charter"] == "research_state/bab_p22/charter.json"
    assert prov["nominal_slack"] == 0.05
    assert prov["reference_universe_seed"] == 20261118


def test_committed_json_matches_fresh_build(
    battery: dict, committed_battery: dict
) -> None:
    assert committed_battery == battery, "committed null_battery.json drifted"


def test_battery_is_hash_deterministic(battery: dict, battery_again: dict) -> None:
    assert battery == battery_again, "null battery is not hash-deterministic"


def test_consumes_charter_seeds_exactly(battery: dict, charter: dict) -> None:
    charter_seeds = charter["provenance"]["p22_null_battery_seeds"]
    prov = battery["provenance"]
    assert prov["seeds"] == charter_seeds
    assert prov["n_seeds"] == len(charter_seeds) == len(battery["seeds"]) >= 20
    assert len(set(prov["seeds"])) == len(prov["seeds"])
    assert [rec["seed"] for rec in battery["seeds"]] == charter_seeds


def test_reference_seed_reproduces_committed_p21_panels(battery: dict) -> None:
    prov = battery["provenance"]
    universe = _load(P21_UNIVERSE_PATH)
    committed = {
        variant: universe["panels"][variant]["sha256"]
        for variant in ("planted", "null")
    }
    assert prov["committed_p21_panel_sha256"] == committed
    assert prov["reference_panel_sha256"] == committed
    assert prov["reference_panel_sha256_matched"] is True


def test_every_seed_is_independent(battery: dict) -> None:
    seeds = [rec["seed"] for rec in battery["seeds"]]
    planted = [rec["panel_sha256"]["planted"] for rec in battery["seeds"]]
    null = [rec["panel_sha256"]["null"] for rec in battery["seeds"]]
    assert len(set(planted)) == len(seeds)
    assert len(set(null)) == len(seeds)
    assert planted != null


def test_null_recovery_is_exactly_zero_for_every_seed(battery: dict) -> None:
    null_books = [
        book
        for rec in battery["seeds"]
        for book in rec["books"]
        if book["variant"] == "null"
    ]
    assert null_books, "battery published no null books"
    assert all(book["recovery_mean"] == 0.0 for book in null_books)
    assert all(book["recovery_frac_positive"] == 0.0 for book in null_books)
    summary = battery["provenance"]["summary"]
    assert summary["null_recovery_max_abs"] == 0.0
    assert summary["null_recovery_zero_books"] == len(null_books)
    assert summary["null_recovery_exactly_zero_every_seed"] is True


def test_false_positive_rate_is_computed_and_published(battery: dict) -> None:
    summary = battery["provenance"]["summary"]
    null_books = [
        book
        for rec in battery["seeds"]
        for book in rec["books"]
        if book["variant"] == "null"
    ]
    measured = sum(1 for book in null_books if book["significant"])
    assert summary["fpr_count"] == measured
    assert summary["fpr_denominator"] == len(null_books)
    assert summary["fpr_rate"] == round(measured / len(null_books), b.DECIMALS)
    assert summary["fpr_expected_count"] == round(
        len(null_books) * battery["provenance"]["nominal_slack"], b.DECIMALS
    )
    assert summary["fpr_within_declared_bound"] is (
        measured <= summary["fpr_max_count_declared"]
    )
    # Each null significance flag must be consistent with its published p-value.
    slack = battery["provenance"]["nominal_slack"]
    for book in null_books:
        assert book["p_value"] is not None
        assert book["significant"] is (book["p_value"] < slack)


def test_planted_recovery_is_strictly_positive_on_documented_fraction(
    battery: dict,
) -> None:
    summary = battery["provenance"]["summary"]
    planted_books = [
        book
        for rec in battery["seeds"]
        for book in rec["books"]
        if book["variant"] == "planted"
    ]
    for weighting in b.WEIGHTINGS:
        books = [book for book in planted_books if book["weighting"] == weighting]
        positive = [book["recovery_mean"] > 0.0 for book in books]
        fraction = round(sum(positive) / len(books), b.DECIMALS)
        assert fraction == summary["planted_recovery_positive_fraction"][weighting]
        assert fraction >= 0.9, f"planted {weighting} recovery fraction {fraction}"
        assert summary["planted_recovery_min"][weighting] > 0.0
    assert summary["planted_recovery_exceeds_null_max"] is True


def test_planted_books_do_not_claim_bootstrap_p_values(battery: dict) -> None:
    planted_books = [
        book
        for rec in battery["seeds"]
        for book in rec["books"]
        if book["variant"] == "planted"
    ]
    assert all(book["p_value"] is None for book in planted_books)
    assert all(book["significant"] is False for book in planted_books)


def test_every_book_is_active_and_complete(battery: dict) -> None:
    for rec in battery["seeds"]:
        assert len(rec["books"]) == 4
        for book in rec["books"]:
            assert book["active_rows"] > 0
            assert book["total_rows"] == b.u.ROWS
            assert book["gross_mean_active"] > 0.0
            assert book["gross_max"] <= b.CONFIG["rank_max_gross"]


def test_bootstrap_respects_chartered_minimums(battery: dict, charter: dict) -> None:
    boot = battery["provenance"]["bootstrap"]
    wp2 = charter["provenance"]["acceptance_thresholds"]["wp2"]
    assert boot["n_resamples"] == b.N_RESAMPLES >= wp2["n_resamples_min"]
    assert boot["block_length"] == b.BLOCK_LENGTH == wp2["block_length"]
    assert boot["applied_to"].startswith("null books")


def test_markdown_matches_renderer(battery: dict, battery_md: str) -> None:
    assert battery_md == b.render_markdown(battery), "null_battery.md drifted"


def test_markdown_numbers_come_from_json(battery: dict, battery_md: str) -> None:
    allowed = set()

    def collect(node) -> None:
        if isinstance(node, dict):
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
        elif isinstance(node, bool):
            return
        elif isinstance(node, (int, float)):
            allowed.add(round(float(node), b.DECIMALS))

    collect(battery)
    for line in battery_md.splitlines():
        if not line.startswith("|"):
            continue
        for cell in line.strip().strip("|").split("|"):
            clean = cell.strip()
            try:
                value = float(clean)
            except ValueError:
                continue
            assert round(value, b.DECIMALS) in allowed, (
                f"markdown cell {clean!r} is not a battery JSON number"
            )


def test_inputs_are_read_only(battery: dict, charter: dict) -> None:
    assert _load(CHARTER_PATH) == charter
    assert _load(P21_UNIVERSE_PATH)["panels"]["planted"]["sha256"] == (
        battery["provenance"]["reference_panel_sha256"]["planted"]
    )


def test_never_executes_a_p21_harness() -> None:
    tree = ast.parse(Path(b.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module != "strategies.betting_against_beta.build_universe"
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                name = func.attr
            elif isinstance(func, ast.Name):
                name = func.id
            else:
                continue
            assert not name.startswith("build_universe_"), name
            assert name != "build_rank_eval"
            assert name != "build_significance"
            assert name != "build_cost_surface"
            assert name != "build_charter"
