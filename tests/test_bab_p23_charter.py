"""Acceptance tests for P23 WP0: the machine-readable campaign charter.

These tests are the claim that ``scripts/bab_p23_charter.py`` produces a
deterministic, sha-pinned charter (``research_state/bab_p23/charter.json``) that
**restates the closed P22 verdict from the committed P22 JSON only** (no
hand-typed numbers), pins the P23 breadth ladder, beta-window/drift grid,
short-availability haircut ladder, per-work-package seeds (>= 20 each), the
nominal slack, and the exact acceptance thresholds consumed by P23 WP1-WP4;
that committed JSON equals a fresh build; and that the markdown is derived from
JSON only.

They never re-run or import any P21/P22 harness: ``build_charter`` reads the
committed P22 JSON artifacts and never writes them.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

import pytest

from scripts import bab_p23_charter as c

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTER_PATH = REPO_ROOT / "research_state/bab_p23/charter.json"
CHARTER_MD_PATH = REPO_ROOT / "research_state/bab_p23/charter.md"
KICKOFF_PATH = REPO_ROOT / "docs/BAB_P23_KICKOFF.md"
P22_SOURCES = (
    REPO_ROOT / "research_state/bab_p22/charter.json",
    REPO_ROOT / "research_state/bab_p22/null_battery.json",
    REPO_ROOT / "research_state/bab_p22/impact_surface.json",
    REPO_ROOT / "research_state/bab_p22/capacity.json",
)

NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def p22_payloads() -> dict:
    return {p.stem: _load(p) for p in P22_SOURCES}


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


def _book(books: list, variant: str, weighting: str) -> dict:
    return next(
        b
        for b in books
        if b["variant"] == variant and b["weighting"] == weighting
    )


def test_schema_and_provenance(charter: dict) -> None:
    assert charter["schema"] == c.SCHEMA == "bab_p23.charter/1"
    prov = charter["provenance"]
    assert prov["generator"] == "scripts/bab_p23_charter.py"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert prov["p22_source_schema"] == "bab_p22.charter/1"
    assert prov["universe_seed"] == 20261118
    assert set(prov["panel_sha256"]) == {"planted", "null"}


def test_charter_matches_fresh_build(charter: dict, committed_charter: dict) -> None:
    assert committed_charter == charter, "committed charter.json drifted from fresh build"


def test_charter_is_deterministic(charter: dict) -> None:
    assert c.build_charter() == charter, "charter build is not hash-deterministic"


def test_markdown_matches_renderer(charter: dict, charter_md: str) -> None:
    assert charter_md == c.render_markdown(charter), "charter.md drifted from its renderer"


def test_kickoff_equals_charter_markdown(charter_md: str) -> None:
    assert KICKOFF_PATH.read_text(encoding="utf-8") == charter_md


def test_p22_verdict_restated_from_committed_json(
    charter: dict, p22_payloads: dict
) -> None:
    verdict = charter["provenance"]["p22_verdict"]
    p22_charter = p22_payloads["charter"]["provenance"]
    nb = p22_payloads["null_battery"]["provenance"]["summary"]

    assert "NO-GO for market deployment" in p22_charter["p21_verdict"]["verdict"]
    assert verdict["no_go_for_market"] is True
    assert verdict["verdict"] == "NO-GO for market deployment"
    assert verdict["p22_charter_verdict"] == p22_charter["p21_verdict"]["verdict"]
    assert verdict["nominal_slack"] == p22_charter["nominal_slack"] == 0.05

    assert verdict["signal_on_planted"] is True
    assert verdict["noise_on_null"] is True
    restated = verdict["null_battery"]
    assert restated["n_seeds"] == nb["n_seeds"]
    assert restated["n_null_books"] == nb["n_null_books"]
    assert restated["n_planted_books"] == nb["n_planted_books"]
    assert restated["null_recovery_max_abs"] == nb["null_recovery_max_abs"] == 0.0
    assert (
        restated["null_recovery_exactly_zero_every_seed"]
        is nb["null_recovery_exactly_zero_every_seed"]
    )
    assert restated["fpr_count"] == nb["fpr_count"]
    assert restated["fpr_denominator"] == nb["fpr_denominator"]
    assert restated["fpr_rate"] == nb["fpr_rate"]
    assert restated["fpr_within_declared_bound"] is True
    assert restated["planted_recovery_min"] == nb["planted_recovery_min"]
    assert (
        restated["planted_recovery_positive_fraction"]
        == nb["planted_recovery_positive_fraction"]
    )
    assert restated["null_sharpe_max"] == nb["null_sharpe_max"]
    assert restated["planted_sharpe_min"] == nb["planted_sharpe_min"]

    for variant in ("planted", "null"):
        for weighting in ("equal", "rank"):
            key = f"{variant}_{weighting}"
            impact = _book(p22_payloads["impact_surface"]["books"], variant, weighting)
            capacity = _book(p22_payloads["capacity"]["books"], variant, weighting)
            assert verdict["impact"][key]["monotone"] is True
            assert verdict["impact"][key]["gross_sharpe"] == impact["gross_sharpe"]
            assert verdict["capacity"][key]["gross_sharpe"] == capacity["gross_sharpe"]
            assert (
                verdict["capacity"][key]["break_even_coefficient"]
                == capacity["break_even_coefficient"]
            )
            assert verdict["capacity"][key]["censored"] is capacity["censored"]
            assert (
                verdict["capacity"][key]["bracket_halving_verified"]
                is capacity["bracket_halving_verified"]
            )


def test_p23_grids_pinned(charter: dict) -> None:
    block = charter["charter"]
    assert block["breadth_ladder"] == c.P23_BREADTH_LADDER == [9, 17, 25, 33, 41]
    assert block["beta_window_grid"] == c.P23_BETA_WINDOW_GRID == [60, 90, 120, 180]
    assert block["drift_threshold_grid"] == c.P23_DRIFT_THRESHOLD_GRID
    assert block["borrow_haircut_ladder"] == c.P23_BORROW_HAIRCUT_LADDER
    assert block["breadth_ladder"][0] < block["breadth_ladder"][-1]
    assert block["borrow_haircut_ladder"][0] == 0.0
    assert block["borrow_haircut_ladder"] == sorted(block["borrow_haircut_ladder"])
    assert len(block["beta_window_grid"]) >= c.P23_MIN_RUNGS
    assert len(block["drift_threshold_grid"]) >= c.P23_MIN_RUNGS
    assert len(block["borrow_haircut_ladder"]) >= c.P23_MIN_RUNGS
    assert block["breadth_ladder"][-1] == 41  # P21/P22 universe width


def test_per_wp_seeds_pinned_and_disjoint(charter: dict, p22_payloads: dict) -> None:
    block = charter["charter"]
    p22_seeds = set(p22_payloads["charter"]["provenance"]["p22_null_battery_seeds"])
    all_seeds: list = []
    for wp, seeds in block["wp_seeds"].items():
        assert len(seeds) >= c.P23_MIN_SEEDS, f"{wp} needs >= 20 seeds"
        assert block["wp_seed_counts"][wp] == len(seeds)
        assert all(isinstance(s, int) for s in seeds)
        assert len(set(seeds)) == len(seeds), f"{wp} seed list has duplicates"
        assert not (set(seeds) & p22_seeds), f"{wp} reuses a P22 seed"
        all_seeds.extend(seeds)
    assert len(all_seeds) == len(set(all_seeds)), "WP seed lists overlap"
    assert set(block["wp_seeds"]) == {"wp1", "wp2", "wp3"}


def test_acceptance_thresholds_present(charter: dict, p22_payloads: dict) -> None:
    thresholds = charter["provenance"]["acceptance_thresholds"]
    for wp in ("wp1", "wp2", "wp3", "wp4"):
        assert wp in thresholds, f"missing acceptance thresholds for {wp}"
    assert thresholds["nominal_slack"] == 0.05

    config = p22_payloads["impact_surface"]["provenance"]["config"]
    assert thresholds["wp1"]["rank_min_leg_beta"] == config["rank_min_leg_beta"]
    assert thresholds["wp1"]["rank_max_gross"] == config["rank_max_gross"]
    assert thresholds["wp1"]["rank_guards_never_relaxed"] is True
    assert thresholds["wp1"]["recovery_null_exactly_zero"] == 0.0
    assert thresholds["wp2"]["beta_window_default_preserved"] == config["beta_window"]
    assert thresholds["wp2"]["min_beta_windows"] >= 3
    assert thresholds["wp2"]["min_drift_thresholds"] >= 3
    assert thresholds["wp2"]["recovery_null_exactly_zero"] == 0.0
    assert thresholds["wp3"]["min_haircut_levels"] >= 3
    assert thresholds["wp3"]["costed_sharpe_non_increasing_in_haircut"] is True
    assert thresholds["wp4"]["numbers_matched_min"] >= 100
    assert thresholds["wp4"]["zero_unmatched_cells"] == 0
    assert thresholds["wp4"]["no_harness_re_run"] is True
    assert thresholds["wp4"]["no_go_for_market"] is True

    strategy = charter["provenance"]["strategy_config"]
    assert strategy["rank_min_leg_beta"] == config["rank_min_leg_beta"]
    assert strategy["rank_max_gross"] == config["rank_max_gross"]
    assert strategy["beta_window"] == config["beta_window"]


def test_charter_framing(charter: dict) -> None:
    block = charter["charter"]
    assert block["campaign"] == "P23"
    assert block["title"] == "Breadth and instability stress"
    assert block["artifact_gated"] is True
    assert block["not_market_evidence"] is True
    assert block["licensed_data_required"] is True
    assert block["wps_in_order"][0] == "P23 WP0 — charter"
    assert block["wps_in_order"][-1].startswith("P23 WP4")
    assert "NO-GO" in block["wps_in_order"][-1]


def test_all_charter_numbers_are_backed(charter: dict, p22_payloads: dict, charter_md: str) -> None:
    allowed = set()
    for payload in p22_payloads.values():
        allowed |= _numeric_leaves(payload)
    # Charter-declared constants: grids, ladders, seeds and thresholds.
    allowed |= _numeric_leaves(charter["charter"])
    allowed |= _numeric_leaves(charter["provenance"]["acceptance_thresholds"])
    allowed |= {0.0}

    def check_node(node, where: str) -> None:
        for value in _numeric_leaves(node):
            assert value in allowed, f"{where}: unbacked number {value}"

    check_node(charter, "fresh build")
    check_node(_load(CHARTER_PATH), "charter.json")

    tables = list(ANCHOR.finditer(charter_md))
    assert len(tables) >= 6, "expected at least six JSON-derived tables"
    for body in tables:
        rows = body.group("body").splitlines()[2:]
        assert rows, f"table {body.group('name')} has no data rows"
        for line in rows:
            for cell in line.strip().strip("|").split("|"):
                clean = cell.strip()
                if NUMERIC_CELL.match(clean):
                    assert round(float(clean), 6) in allowed, (
                        f"markdown cell {clean!r} not backed by a JSON field "
                        f"or a declared constant"
                    )


def test_p22_artifacts_are_read_only(charter: dict) -> None:
    before = {p.name: _sha256(p) for p in P22_SOURCES}
    c.render_markdown(charter)
    c.build_charter()
    after = {p.name: _sha256(p) for p in P22_SOURCES}
    assert before == after, "charter build wrote to a committed P22 artifact"


def test_charter_never_executes_a_harness() -> None:
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
                ), f"harness call: {func.attr}"
            elif isinstance(func, ast.Name):
                assert not (
                    func.id.startswith("build_") and func.id != "build_charter"
                ), f"harness call: {func.id}"
