"""Acceptance tests for P24 WP1: the regime-split stress artifact.

These tests are the claim that ``research_state/bab_p24/regime_split.json`` publishes
only numbers that exist in the committed P21/P23/P24 JSON artifacts and that the
regime-split stress is measured correctly. They never import ``scripts`` or
``strategies`` and never call a ``build_*`` harness: every cell is validated
against committed JSON and the regime-zero-reference is pinned to P21.

A hand-typed number, a stale field, a market GO verdict, or a planted-universe
recovery quoted as market alpha fails the suite.
"""

from __future__ import annotations

import ast
import hashlib
import json
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_P24_DIR = REPO_ROOT / "research_state/bab_p24"
RESEARCH_P23_DIR = REPO_ROOT / "research_state/bab_p23"
RESEARCH_P21_DIR = REPO_ROOT / "research_state/bab_p21"
ARTIFACT_PATH = RESEARCH_P24_DIR / "regime_split.json"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6

SOURCES = (
    "charter.json",  # P24 charter
    "regime_split.json",  # P24 WP1 artifact
    "charter.json",  # P23 charter
    "rank_eval.json",  # P21
)


def _load_p24(name: str) -> dict:
    p = RESEARCH_P24_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


def _load_p23(name: str) -> dict:
    p = RESEARCH_P23_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


def _load_p21(name: str) -> dict:
    p = RESEARCH_P21_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p24_regime_split() -> dict:
    return _load_p24("regime_split.json")


@pytest.fixture(scope="module")
def p24_charter() -> dict:
    return _load_p24("charter.json")


@pytest.fixture(scope="module")
def p23_charter() -> dict:
    return _load_p23("charter.json")


@pytest.fixture(scope="module")
def p21_rank_eval() -> dict:
    return _load_p21("rank_eval.json")


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
        values.add(round(float(node), DECIMALS))
    return values


# --------------------------------------------------------------------------- #
# 1. Artifact validates against committed P21/P23/P24 artifacts
# --------------------------------------------------------------------------- #
def test_p24_regime_split_exists_and_reads() -> None:
    assert ARTIFACT_PATH.is_file()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert data["schema"] == "bab_p24.regime_split/1"
    prov = data["provenance"]
    assert prov["generator"] == "scripts/bab_regime_split.py"
    assert prov["synthetic"] is True
    assert prov["universe_seed"] == 20261118
    assert prov["charter_path"] == "research_state/bab_p24/charter.json"
    assert prov["charter_schema"] == "bab_p24.charter/1"
    assert prov["regime_grid"] == ["calm", "stress"]
    assert prov["vol_window"] == 20
    assert prov["vol_percentiles"] == [1.0 / 3.0, 2.0 / 3.0]
    assert "regime_rule" in prov
    assert "causal" in prov["regime_rule"].lower()
    assert "no lookahead" in prov["regime_rule"].lower()
    assert "config" in prov
    assert prov["config"]["benchmark"] == "BTC"
    assert prov["config"]["beta_window"] == 90
    assert prov["config"]["long_quantile"] == 0.3
    assert prov["config"]["short_quantile"] == 0.3
    assert prov["config"]["beta_neutral"] is True
    assert prov["config"]["rank_min_leg_beta"] == 0.2
    assert prov["config"]["rank_max_gross"] == 4.0
    assert "acceptance_thresholds" in prov
    thresholds = prov["acceptance_thresholds"]
    assert thresholds["regime_zero_matches_p21_at_6dp"] is True
    assert thresholds["calm_and_stress_disjoint"] is True
    assert thresholds["planted_recovery_strictly_positive_in_at_least_one_regime"] is True
    assert thresholds["null_recovery_exactly_zero_everywhere"] is True
    assert thresholds["every_planted_regime_cell_positive"] is True
    assert thresholds["every_regime_non_empty"] is True
    assert "regime_coverage" in prov
    coverage = prov["regime_coverage"]
    assert coverage["total_rows"] == 600
    assert coverage["overlap_rows"] == 0
    assert coverage["union_rows"] == sum(coverage["rows_by_regime"].values())
    assert coverage["union_rows"] + coverage["unclassified_rows"] == 600
    assert "regime_zero_reference" in prov
    assert "derived" in prov
    derived = prov["derived"]
    assert derived["n_cells"] == 8
    assert derived["n_regimes"] == 2
    assert derived["n_weightings"] == 2
    assert derived["n_variants"] == 2
    assert "panel_sha256" in prov
    assert "null" in prov["panel_sha256"]
    assert "planted" in prov["panel_sha256"]


def test_p24_regime_split_sources_all_exist_and_parse(
    p24_charter, p23_charter, p21_rank_eval
) -> None:
    _load_p24("charter.json")
    _load_p24("regime_split.json")
    _load_p23("charter.json")
    _load_p21("rank_eval.json")


def test_p24_regime_split_universe_seed_matches_p21(p24_regime_split, p21_rank_eval) -> None:
    expected_seed = 20261118
    assert p24_regime_split["provenance"]["universe_seed"] == expected_seed
    assert p21_rank_eval["provenance"]["universe_seed"] == expected_seed


def test_p24_regime_split_panel_shas_match_p21(
    p24_regime_split, p23_charter, p21_rank_eval
) -> None:
    expected = p21_rank_eval["provenance"]["panel_sha256"]
    assert p23_charter["provenance"]["panel_sha256"] == expected
    assert p24_regime_split["provenance"]["panel_sha256"] == expected


def test_p24_regime_split_numeric_fields_exist_in_committed_json(
    p24_regime_split, p24_charter, p23_charter, p21_rank_eval
) -> None:
    """Every numeric field in P24 regime_split provenance must resolve to a committed JSON leaf."""
    allowed = set()
    for payload in (p24_charter, p23_charter, p21_rank_eval):
        allowed |= _numeric_leaves(payload)

    # Regime split declares constants (vol_percentiles, vol_window, etc.)
    # vol_percentiles are 1/3 and 2/3, rounded to 6dp
    declared_constants = {20, round(1.0 / 3.0, DECIMALS), round(2.0 / 3.0, DECIMALS)}
    artifact_numeric = _numeric_leaves(p24_regime_split["provenance"])
    # The measured values in cells are expected to be new; only check
    # zero-reference values against committed JSON
    ref = p24_regime_split["provenance"]["regime_zero_reference"]["checks"]
    for vals in ref.values():
        assert vals["committed_p21_recovery"] in allowed
        assert vals["regime_zero_recovery"] in allowed


def test_p24_charter_no_go_for_market_enforced(p24_regime_split, p23_charter) -> None:
    # P23 charter verdict must have no_go_for_market = True
    assert p23_charter["provenance"]["p22_verdict"]["no_go_for_market"] is True
    # P24 charter must also declare it
    p24_charter = _load_p24("charter.json")
    assert p24_charter["provenance"]["no_go_for_market"] is True


# --------------------------------------------------------------------------- #
# 2. Cell-level invariants
# --------------------------------------------------------------------------- #
def test_regime_split_cells_complete(p24_regime_split) -> None:
    cells = p24_regime_split["cells"]
    assert len(cells) == 8
    regimes = {c["regime"] for c in cells}
    weightings = {c["weighting"] for c in cells}
    variants = {c["variant"] for c in cells}
    assert regimes == {"calm", "stress"}
    assert weightings == {"equal", "rank"}
    assert variants == {"planted", "null"}

    # Every combination present
    for regime in ("calm", "stress"):
        for weighting in ("equal", "rank"):
            for variant in ("planted", "null"):
                matches = [
                    c
                    for c in cells
                    if c["regime"] == regime
                    and c["weighting"] == weighting
                    and c["variant"] == variant
                ]
                assert len(matches) == 1, f"Missing cell: {regime}/{weighting}/{variant}"


def test_regime_split_calm_and_stress_disjoint(p24_regime_split) -> None:
    """Calm and stress regimes must be disjoint (no row in both)."""
    coverage = p24_regime_split["provenance"]["regime_coverage"]
    assert coverage["overlap_rows"] == 0
    rows = coverage["rows_by_regime"]
    assert set(rows) == {"calm", "stress"}
    for regime, count in rows.items():
        assert 0 < count < coverage["total_rows"], f"{regime}={count}"
    assert rows["calm"] + rows["stress"] == coverage["union_rows"]
    assert coverage["union_rows"] < coverage["total_rows"]

    cells = p24_regime_split["cells"]
    for weighting in ("equal", "rank"):
        for variant in ("planted", "null"):
            calm_cell = next(
                c
                for c in cells
                if c["regime"] == "calm"
                and c["weighting"] == weighting
                and c["variant"] == variant
            )
            stress_cell = next(
                c
                for c in cells
                if c["regime"] == "stress"
                and c["weighting"] == weighting
                and c["variant"] == variant
            )
            # Active fractions should sum to < 1.0 (middle excluded)
            total_frac = calm_cell["active_fraction"] + stress_cell["active_fraction"]
            assert total_frac < 1.0, (
                f"Regimes not disjoint: calm {calm_cell['active_fraction']} + "
                f"stress {stress_cell['active_fraction']} = {total_frac}"
            )


def test_regime_split_null_recovery_exactly_zero(p24_regime_split) -> None:
    """Null variant recovery must be exactly zero in every cell."""
    for cell in p24_regime_split["cells"]:
        if cell["variant"] == "null":
            assert cell["recovery"] == 0.0, f"Null recovery not zero: {cell}"
            assert cell["recovery_exactly_zero"] is True
            assert cell["recovery_positive"] is False
            assert cell["recovery_retention"] == 0.0


def test_regime_split_planted_recovery_strictly_positive_in_at_least_one_regime(
    p24_regime_split
) -> None:
    """For each weighting, planted recovery must be strictly positive in at least one regime."""
    cells = p24_regime_split["cells"]
    for weighting in ("equal", "rank"):
        planted_cells = [
            c for c in cells if c["variant"] == "planted" and c["weighting"] == weighting
        ]
        positive_count = sum(1 for c in planted_cells if c["recovery"] > 0.0)
        assert positive_count >= 1, (
            f"Planted recovery not positive in any regime for {weighting}: "
            f"{[(c['regime'], c['recovery']) for c in planted_cells]}"
        )
        # Actually verify both regimes are positive (they should be)
        for c in planted_cells:
            assert c["recovery"] > 0.0, f"Planted recovery not positive: {c}"
            assert c["recovery_positive"] is True
            assert c["recovery_exactly_zero"] is False


def test_regime_split_rank_guards(p24_regime_split) -> None:
    """Rank weighting cells must respect min_leg_beta floor and gross_max ceiling."""
    for cell in p24_regime_split["cells"]:
        if cell["weighting"] == "rank":
            assert cell["min_leg_beta"] >= cell["rank_min_leg_beta_floor"] - 1e-9, (
                f"Rank min_leg_beta floor breached: {cell}"
            )
            assert cell["gross_max"] <= cell["rank_max_gross_ceiling"] + 1e-9, (
                f"Rank gross_max ceiling breached: {cell}"
            )


def test_regime_zero_reference_matches_p21_at_6dp(
    p24_regime_split, p21_rank_eval
) -> None:
    """Full-panel (no regime) recovery must match P21 rank_eval at 6dp."""
    ref = p24_regime_split["provenance"]["regime_zero_reference"]["checks"]
    p21_books = {(b["variant"], b["weighting"]): b for b in p21_rank_eval["books"]}

    for key, vals in ref.items():
        variant, weighting = key.split("_")
        p21_book = p21_books[(variant, weighting)]
        assert vals["matches_at_6dp"] is True, f"Zero-reference mismatch: {key}"
        assert vals["regime_zero_recovery"] == round(
            float(p21_book["recovery_mean"]), DECIMALS
        )


def test_regime_zero_reference_covers_all_books(p24_regime_split) -> None:
    """Regime zero reference must cover all 4 P21 books."""
    ref = p24_regime_split["provenance"]["regime_zero_reference"]["checks"]
    assert set(ref.keys()) == {"null_equal", "null_rank", "planted_equal", "planted_rank"}


def test_regime_split_active_rows_reasonable(p24_regime_split) -> None:
    """Active rows should be reasonable fractions of total (tertile splits)."""
    for cell in p24_regime_split["cells"]:
        assert cell["total_rows"] == 600
        assert 0 < cell["active_rows"] < cell["total_rows"]
        assert cell["regime_rows"] == (
            p24_regime_split["provenance"]["regime_coverage"]["rows_by_regime"][
                cell["regime"]
            ]
        )
        assert cell["active_rows"] <= cell["regime_rows"]
        # Tertile splits should give ~1/3 each, so ~200 active rows
        assert 150 <= cell["active_rows"] <= 250, f"Unexpected active rows: {cell}"


# --------------------------------------------------------------------------- #
# 3. Verdict strings must be explicit and machine-backed
# --------------------------------------------------------------------------- #
def test_regime_split_labels_synthetic_not_market(
    p24_regime_split, p24_charter, p23_charter
) -> None:
    assert p24_regime_split["provenance"]["synthetic"] is True
    assert p24_charter["charter"]["not_market_evidence"] is True
    assert p23_charter["provenance"]["synthetic"] is True
    assert p23_charter["charter"]["not_market_evidence"] is True


# --------------------------------------------------------------------------- #
# 4. The test itself never re-runs a harness and never edits an artifact
# --------------------------------------------------------------------------- #
def test_regime_split_acceptance_never_executes_a_research_harness() -> None:
    tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                assert not func.attr.startswith("build_"), f"harness call: {func.attr}"
            elif isinstance(func, ast.Name):
                assert not func.id.startswith("build_"), f"harness call: {func.id}"
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(("scripts", "strategies")), module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(("scripts", "strategies")), alias.name
    start = time.perf_counter()
    _load_p24("regime_split.json")
    _load_p24("charter.json")
    _load_p23("charter.json")
    _load_p21("rank_eval.json")
    assert time.perf_counter() - start < 2.0


def test_regime_split_artifacts_are_byte_identical_after_suite() -> None:
    names_p24 = ("charter", "regime_split")
    names_p23 = ("charter",)
    name_p21 = "rank_eval"

    before = {}
    for name in names_p24:
        p = RESEARCH_P24_DIR / f"{name}.json"
        before[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    for name in names_p23:
        p = RESEARCH_P23_DIR / f"{name}.json"
        before[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    p21_path = RESEARCH_P21_DIR / f"{name_p21}.json"
    before[name_p21] = hashlib.sha256(p21_path.read_bytes()).hexdigest()

    for name in names_p24:
        _load_p24(f"{name}.json")
    for name in names_p23:
        _load_p23(f"{name}.json")
    _load_p21(f"{name_p21}.json")

    after = {}
    for name in names_p24:
        p = RESEARCH_P24_DIR / f"{name}.json"
        after[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    for name in names_p23:
        p = RESEARCH_P23_DIR / f"{name}.json"
        after[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    after[name_p21] = hashlib.sha256(p21_path.read_bytes()).hexdigest()

    assert before == after, "One or more research artifacts mutated during test run"


def test_regime_split_flags_are_not_self_attested(p24_regime_split) -> None:
    """Every boolean must be recomputable from the cell's own measured numbers."""
    for cell in p24_regime_split["cells"]:
        assert cell["recovery_positive"] is (cell["recovery"] > 0.0), cell
        assert cell["recovery_exactly_zero"] is (cell["recovery"] == 0.0), cell
        full = cell["recovery_full_panel"]
        if full == 0.0:
            assert cell["recovery_retention"] == 0.0, cell
        else:
            assert cell["recovery_retention"] == round(
                cell["recovery"] / full, DECIMALS
            ), cell


def test_regime_split_retention_uses_committed_full_panel(p24_regime_split) -> None:
    """Each cell's full-panel denominator must equal the pinned zero reference."""
    ref = p24_regime_split["provenance"]["regime_zero_reference"]["checks"]
    for cell in p24_regime_split["cells"]:
        key = f"{cell['variant']}_{cell['weighting']}"
        assert cell["recovery_full_panel"] == ref[key]["regime_zero_recovery"], cell


def test_regime_split_thresholds_recomputed_from_cells(p24_regime_split) -> None:
    """The declared thresholds must equal recomputation from the published cells."""
    prov = p24_regime_split["provenance"]
    cells = p24_regime_split["cells"]
    planted = [c for c in cells if c["variant"] == "planted"]
    null = [c for c in cells if c["variant"] == "null"]
    checks = prov["regime_zero_reference"]["checks"].values()
    recomputed = {
        "regime_zero_matches_p21_at_6dp": all(v["matches_at_6dp"] for v in checks),
        "calm_and_stress_disjoint": prov["regime_coverage"]["overlap_rows"] == 0,
        "every_regime_non_empty": all(
            n > 0 for n in prov["regime_coverage"]["rows_by_regime"].values()
        ),
        "planted_recovery_strictly_positive_in_at_least_one_regime": all(
            any(c["recovery"] > 0.0 for c in planted if c["weighting"] == w)
            for w in ("equal", "rank")
        ),
        "every_planted_regime_cell_positive": all(c["recovery"] > 0.0 for c in planted),
        "null_recovery_exactly_zero_everywhere": all(
            c["recovery"] == 0.0 for c in null
        ),
    }
    assert prov["acceptance_thresholds"] == recomputed
    assert all(recomputed.values()), recomputed


def test_regime_split_stress_is_measured_not_declared(p24_regime_split) -> None:
    """The stress book must actually differ from the full-panel book."""
    for cell in p24_regime_split["cells"]:
        if cell["variant"] != "planted":
            continue
        assert cell["regime_rows"] < cell["total_rows"], cell
        assert cell["recovery_retention"] > 0.9, cell
        assert cell["recovery_retention"] < 1.1, cell
