"""Acceptance tests for P22 WP0: the machine-readable campaign charter.

These tests are the claim that ``scripts/bab_p22_charter.py`` produces a
deterministic, sha-pinned charter (``research_state/bab_p22/charter.json``)
that **restates the P21 verdict from the committed P21 JSON only** (no
hand-typed numbers), pins the P22 null-battery seed list (>= 20 seeds), the
nominal slack, and the exact acceptance thresholds consumed by P21 WP1-WP4;
that committed JSON equals a fresh build; and that the markdown is derived
from JSON only.

They never re-run any P21 harness: ``build_charter`` reads the committed JSON
artifacts and never imports or calls a P21 ``build_*`` function.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from scripts import bab_p22_charter as c

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTER_PATH = REPO_ROOT / "research_state/bab_p22/charter.json"
CHARTER_MD_PATH = REPO_ROOT / "research_state/bab_p22/charter.md"
P21_SOURCES = (
    REPO_ROOT / "research_state/bab_p21/universe.json",
    REPO_ROOT / "research_state/bab_p21/significance.json",
    REPO_ROOT / "research_state/bab_p21/rank_eval.json",
    REPO_ROOT / "research_state/bab_p21/cost_surface.json",
)

NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p21_payloads() -> dict:
    return {p.stem: _load(p) for p in P21_SOURCES}


@pytest.fixture(scope="module")
def charter() -> dict:
    return c.build_charter()


@pytest.fixture(scope="module")
def committed_charter() -> dict:
    return _load(CHARTER_PATH)


@pytest.fixture(scope="module")
def charter_md() -> str:
    return CHARTER_MD_PATH.read_text(encoding="utf-8")


def _numeric_leaves(node) -> set:
    values = set()
    if isinstance(node, dict):
        for value in node.values():
            values |= _numeric_leaves(value)
    elif isinstance(node, list):
        for value in node:
            values |= _numeric_leaves(value)
    elif isinstance(node, bool):
        return values
    elif isinstance(node, (int, float)):
        values.add(round(float(node), 6))
    return values


def test_schema_and_provenance(charter: dict) -> None:
    assert charter["schema"] == c.SCHEMA == "bab_p22.charter/1"
    prov = charter["provenance"]
    assert prov["generator"] == "scripts/bab_p22_charter.py"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert prov["universe_seed"] == 20261118
    assert prov["p21_significance_seed"] == 20261119
    assert "planted" in prov["panel_sha256"] and "null" in prov["panel_sha256"]


def test_charter_matches_fresh_build(charter: dict, committed_charter: dict) -> None:
    assert committed_charter == charter, "committed charter.json drifted from fresh build"


def test_charter_is_deterministic(charter: dict) -> None:
    again = c.build_charter()
    assert again == charter, "charter build is not hash-deterministic"


def test_null_battery_seeds_pinned(charter: dict) -> None:
    prov = charter["provenance"]
    seeds = prov["p22_null_battery_seeds"]
    assert prov["p22_null_battery_n_seeds"] == len(seeds)
    assert len(seeds) >= 20, "P22 null battery requires >= 20 seeds"
    assert all(isinstance(s, int) for s in seeds)
    assert len(set(seeds)) == len(seeds), "seed list must not contain duplicates"


def test_verdict_restated_from_p21_json(
    charter: dict, p21_payloads: dict
) -> None:
    prov = charter["provenance"]
    verdict = prov["p21_verdict"]
    sig = p21_payloads["significance"]["provenance"]
    assert verdict["null_calibrated"] is sig["null_calibrated"] is True
    assert verdict["planted_detected"] is sig["planted_detected"] is True
    assert verdict["null_max_p_value"] == sig["null_max_p_value"]
    assert verdict["nominal_slack"] == 0.05
    assert "SIGNAL" in verdict["verdict"] and "NOISE" in verdict["verdict"]
    assert "NO-GO" in verdict["verdict"]
    for key, book in verdict["books"].items():
        variant, weighting = key.split("_")
        sig_book = next(
            b
            for b in p21_payloads["significance"]["books"]
            if b["variant"] == variant and b["weighting"] == weighting
        )
        rank_book = next(
            b
            for b in p21_payloads["rank_eval"]["books"]
            if b["variant"] == variant and b["weighting"] == weighting
        )
        cost_book = next(
            b
            for b in p21_payloads["cost_surface"]["books"]
            if b["variant"] == variant and b["weighting"] == weighting
        )
        assert book["p_value"] == sig_book["p_value"]
        assert book["significant"] is sig_book["significant"]
        assert book["ci_excludes_zero"] is sig_book["ci_excludes_zero"]
        assert book["oos_sharpe"] == sig_book["oos_sharpe"]
        assert book["dsr"] == sig_book["dsr"]
        assert book["recovery_mean"] == rank_book["recovery_mean"]
        assert book["active_rows"] == rank_book["active_rows"]
        assert book["gross_sharpe"] == cost_book["gross_sharpe"]
        assert book["censored"] is cost_book["censored"]
        for component in book["monotonicity"]:
            assert book["monotonicity"][component] is cost_book["monotonicity"][component]


def test_acceptance_thresholds_present(charter: dict) -> None:
    thresholds = charter["provenance"]["acceptance_thresholds"]
    for wp in ("wp1", "wp2", "wp3", "wp4"):
        assert wp in thresholds, f"missing acceptance thresholds for {wp}"
    assert thresholds["nominal_slack"] == 0.05
    assert thresholds["wp1"]["rank_min_leg_beta"] == 0.20
    assert thresholds["wp1"]["rank_max_gross"] == 4.0
    assert thresholds["wp1"]["beta_exposure_max"] == 0.05
    assert thresholds["wp2"]["n_resamples_min"] >= 2000
    assert thresholds["wp3"]["min_components"] >= 3
    assert thresholds["wp4"]["numbers_matched_min"] >= 100
    assert thresholds["wp4"]["zero_unmatched_cells"] == 0
    assert thresholds["wp4"]["no_harness_re_run"] is True
    assert thresholds["wp4"]["no_go_for_market"] is True


def test_charter_framing(charter: dict) -> None:
    charter_block = charter["charter"]
    assert charter_block["campaign"] == "P22"
    assert charter_block["binding_row"] == "P22 WP0"
    assert charter_block["artifact_gated"] is True
    assert charter_block["not_market_evidence"] is True
    assert charter_block["licensed_data_required"] is True
    assert charter_block["wps_in_order"][0] == "P22 WP0 — charter"


def test_markdown_matches_renderer(charter: dict, charter_md: str) -> None:
    assert charter_md == c.render_markdown(charter), "charter.md drifted from its renderer"


def test_all_charter_numbers_from_p21_json_or_declared_constants(
    charter: dict, committed_charter: dict, p21_payloads: dict, charter_md: str
) -> None:
    allowed = set()
    for payload in p21_payloads.values():
        allowed |= _numeric_leaves(payload)
    # Charter-declared constants (not derived from P21 JSON).
    allowed |= _numeric_leaves(charter["provenance"]["p22_null_battery_seeds"])
    allowed |= _numeric_leaves(
        charter["provenance"]["acceptance_thresholds"]
    )
    allowed.add(0.0)  # recovery_null_exactly_zero / null p_value baseline

    def check_node(node, where: str) -> None:
        for value in _numeric_leaves(node):
            assert value in allowed, f"{where}: unbacked number {value}"

    check_node(committed_charter, "charter.json")
    check_node(charter, "fresh build")

    # Every numeric table cell in the markdown must be allowed.
    for body in ANCHOR.finditer(charter_md):
        for line in body.group("body").splitlines()[2:]:
            for cell in line.strip().strip("|").split("|"):
                clean = cell.strip()
                if NUMERIC_CELL.match(clean):
                    assert round(float(clean), 6) in allowed, (
                        f"markdown cell {clean!r} not in P21 JSON or declared constants"
                    )


def test_charter_never_executes_a_p21_harness() -> None:
    tree = ast.parse(Path(c.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module not in ("scripts", "strategies"), module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in ("scripts", "strategies"), alias.name
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                assert not (
                    func.attr.startswith("build_") and func.attr != "build_charter"
                ), f"P21 harness call: {func.attr}"
            elif isinstance(func, ast.Name):
                assert not (
                    func.id.startswith("build_") and func.id != "build_charter"
                ), f"P22 harness call: {func.id}"
