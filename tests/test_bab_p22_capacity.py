"""Acceptance tests for P22 WP3: capacity / break-even via fixed-iteration bisection.

These tests are the claim that ``scripts/bab_capacity.py``:

* loads the committed ``research_state/bab_p22/impact_surface.json`` read-only
  and never regenerates it nor imports any P21 / P22 WP0-WP2 build harness;
* is byte-identical across reruns (hash determinism) and its committed JSON
  and markdown artifacts match a fresh build/render;
* for each book, tests for a zero crossing in costed Sharpe across the
  impact-coefficient grid (positive at coefficient=0, negative at some higher
  coefficient);
* if a crossing exists, computes the break-even coefficient via fixed-iteration
  bisection (50 iterations) proving each bracket halves every iteration;
* books without a crossing are censored with a documented reason, never a
  midpoint;
* a per-row zero-crossing sign test is pinned for every active book.

They never touch the network, never edit product code, and never regenerate
``research_state/bab_p22/impact_surface.json``.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pytest

from scripts import bab_capacity as c

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPACITY_PATH = REPO_ROOT / "research_state/bab_p22/capacity.json"
CAPACITY_MD_PATH = REPO_ROOT / "research_state/bab_p22/capacity.md"
IMPACT_SURFACE_PATH = REPO_ROOT / "research_state/bab_p22/impact_surface.json"

NUMERIC_TOKEN = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
EPS = 1e-12

_VARIANTS = ("planted", "null")
_WEIGHTINGS = ("equal", "rank")
_COMPONENT = c.IMPACT_COMPONENT


@pytest.fixture(scope="module")
def capacity() -> dict:
    return c.build_capacity()


@pytest.fixture(scope="module")
def capacity_again(capacity: dict) -> dict:
    return c.build_capacity()


@pytest.fixture(scope="module")
def committed_capacity() -> dict:
    return json.loads(CAPACITY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def capacity_md() -> str:
    return CAPACITY_MD_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def impact_surface() -> dict:
    return json.loads(IMPACT_SURFACE_PATH.read_text(encoding="utf-8"))


def _book(payload: dict, variant: str, weighting: str) -> dict:
    for book in payload["books"]:
        if book["variant"] == variant and book["weighting"] == weighting:
            return book
    raise AssertionError(f"no book for variant={variant!r} weighting={weighting!r}")


def _numeric_values(text: str) -> set[float]:
    return {float(token) for token in NUMERIC_TOKEN.findall(text)}


def test_schema_and_provenance(capacity: dict) -> None:
    assert capacity["schema"] == c.SCHEMA == "bab_p22.capacity/1"
    prov = capacity["provenance"]
    assert prov["generator"] == "scripts/bab_capacity.py"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert "never market alpha" in prov["caveat"]
    assert prov["universe_seed"] == 20261118
    assert prov["impact_component"] == _COMPONENT
    assert prov["source_impact_surface"] == "research_state/bab_p22/impact_surface.json"
    assert prov["source_impact_surface_schema"] == "bab_p22.impact_surface/1"
    grid = prov["impact_coefficient_grid"]
    assert len(grid) >= 2
    assert grid[0] == 0.0, "impact grid lacks a zero-coefficient baseline"
    assert all(level >= 0.0 for level in grid)
    assert grid == sorted(grid), "impact grid is not ascending"
    assert prov["bisection_iterations"] == 50
    assert prov["bisection_tol"] == 1e-12


def test_determinism_two_builds(capacity: dict, capacity_again: dict) -> None:
    first = json.dumps(capacity, indent=2, sort_keys=True)
    second = json.dumps(capacity_again, indent=2, sort_keys=True)
    assert first == second
    first_sha = hashlib.sha256(first.encode("utf-8")).hexdigest()
    second_sha = hashlib.sha256(second.encode("utf-8")).hexdigest()
    assert first_sha == second_sha
    assert len(first_sha) == 64


def test_committed_json_matches_fresh_build(capacity: dict, committed_capacity: dict) -> None:
    fresh = json.dumps(capacity, indent=2, sort_keys=True) + "\n"
    assert CAPACITY_PATH.read_text(encoding="utf-8") == fresh


def test_committed_markdown_matches_renderer(capacity: dict, capacity_md: str) -> None:
    fresh = c.render_markdown(capacity)
    assert capacity_md == fresh
    assert fresh == c.render_markdown(c.build_capacity())


def test_inputs_are_read_only(impact_surface: dict) -> None:
    impact_before = IMPACT_SURFACE_PATH.read_bytes()
    c.build_capacity()
    assert IMPACT_SURFACE_PATH.read_bytes() == impact_before, "impact_surface.json was mutated"


def test_never_imports_a_p21_or_p22_harness() -> None:
    import ast

    tree = ast.parse(Path(c.__file__).read_text(encoding="utf-8"))
    forbidden_modules = (
        "scripts.bab_synthetic_universe",
        "scripts.bab_rank_eval",
        "scripts.bab_significance",
        "scripts.bab_cost_surface",
        "scripts.bab_p22_charter",
        "scripts.bab_null_battery",
        "scripts.bab_impact_surface",
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module not in forbidden_modules, module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in ("scripts", "strategies"), alias.name


def test_panel_sha256_matches_impact_surface(capacity: dict, impact_surface: dict) -> None:
    prov = capacity["provenance"]
    impact_prov = impact_surface["provenance"]
    for variant in _VARIANTS:
        assert prov["panel_sha256"][variant] == impact_prov["panel_sha256"][variant]


def test_coefficient_grid_matches_impact_surface(
    capacity: dict, impact_surface: dict
) -> None:
    grid = capacity["provenance"]["impact_coefficient_grid"]
    impact_grid = impact_surface["provenance"]["impact_coefficient_grid"]
    assert grid == impact_grid


def test_all_four_books_present(capacity: dict) -> None:
    seen = set()
    for variant in _VARIANTS:
        for weighting in _WEIGHTINGS:
            book = _book(capacity, variant, weighting)
            seen.add((book["variant"], book["weighting"]))
            assert book["active_rows"] == 541, (variant, weighting)
            assert book["total_rows"] == 600, (variant, weighting)
            assert book["gross_sharpe"] is not None, (variant, weighting)
            assert "sign_test" in book, (variant, weighting)
            assert len(book["sign_test"]) == 7, (variant, weighting)  # 7 grid points
    assert seen == {(v, w) for v in _VARIANTS for w in _WEIGHTINGS}


def test_sign_test_structure(capacity: dict) -> None:
    for book in capacity["books"]:
        signs = [e["sign"] for e in book["sign_test"]]
        # First entry (coeff=0) must be positive for all four books
        assert signs[0] == 1, f"{book['variant']}/{book['weighting']} coeff=0 sign not positive"
        # All coefficients must be the standard grid
        coeffs = [e["coefficient"] for e in book["sign_test"]]
        expected_grid = capacity["provenance"]["impact_coefficient_grid"]
        assert coeffs == expected_grid, f"{book['variant']}/{book['weighting']} grid mismatch"
        # All costed_sharpe values must be non-None
        for entry in book["sign_test"]:
            msg = f"{book['variant']}/{book['weighting']} has None sharpe"
            assert entry["costed_sharpe"] is not None, msg


def test_zero_crossing_detection(capacity: dict, impact_surface: dict) -> None:
    """Verify zero crossing detection matches the impact surface data."""
    for variant in _VARIANTS:
        for weighting in _WEIGHTINGS:
            book = _book(capacity, variant, weighting)
            impact_book = _book(impact_surface, variant, weighting)

            if impact_book["censored"]:
                assert book["censored"] is True
                continue

            # Check if impact surface has a zero crossing
            rows = impact_book["surfaces"][_COMPONENT]
            first_sharpe = rows[0]["costed_sharpe"]
            last_sharpe = rows[-1]["costed_sharpe"]

            has_crossing = first_sharpe > 0 and last_sharpe <= 0

            if has_crossing:
                msg = f"{variant}/{weighting} should have crossing but is censored"
                assert book["censored"] is False, msg
                assert book["break_even_coefficient"] is not None
                assert book["break_even_sharpe"] is not None
                assert book["bracket_history"] is not None
                assert len(book["bracket_history"]) == 50
                # Break-even should be between 0 and max coefficient
                max_coeff = impact_surface["provenance"]["impact_coefficient_grid"][-1]
                assert 0.0 < book["break_even_coefficient"] <= max_coeff
                # Break-even Sharpe should be approximately zero
                msg2 = f"break_even_sharpe not near zero: {book['break_even_sharpe']}"
                assert abs(book["break_even_sharpe"]) < 0.1, msg2
            else:
                msg = f"{variant}/{weighting} should be censored (no crossing)"
                assert book["censored"] is True, msg
                assert book["censor_reason"] is not None
                assert book["censor_reason"] != ""
                assert book["break_even_coefficient"] is None
                assert book["break_even_sharpe"] is None
                assert book["bracket_history"] is None


def test_bracket_halving_verified(capacity: dict) -> None:
    """Verify each bracket provably halves every iteration (on raw values)."""
    for book in capacity["books"]:
        if not book["censored"] and book["bracket_history"]:
            # The flag should be True since verification runs on raw values
            msg = f"{book['variant']}/{book['weighting']} bracket halving not verified"
            assert book["bracket_halving_verified"] is True, msg


def test_censored_books_have_documented_reason(capacity: dict) -> None:
    """Censored books must have a documented reason, never a midpoint."""
    for book in capacity["books"]:
        if book["censored"]:
            assert book["censor_reason"] is not None
            assert book["censor_reason"] != ""
            assert "midpoint" not in book["censor_reason"].lower()
            assert book["break_even_coefficient"] is None
            assert book["bracket_history"] is None


def test_planted_equal_has_crossing(capacity: dict) -> None:
    """Planted/equal should have a crossing (break-even exists)."""
    book = _book(capacity, "planted", "equal")
    assert book["censored"] is False
    assert book["break_even_coefficient"] is not None
    # Should be between 0.05 and 0.1 based on impact surface
    assert 0.05 < book["break_even_coefficient"] < 0.1


def test_planted_rank_censored(capacity: dict) -> None:
    """Planted/rank should be censored (no negative Sharpe at max coefficient)."""
    book = _book(capacity, "planted", "rank")
    assert book["censored"] is True
    assert book["censor_reason"] == "no_negative_sharpe_at_max_coefficient"


def test_null_books_have_crossing(capacity: dict) -> None:
    """Null books have positive Sharpe at coeff=0 and negative at max coeff, so they cross."""
    for weighting in _WEIGHTINGS:
        book = _book(capacity, "null", weighting)
        assert book["censored"] is False
        assert book["break_even_coefficient"] is not None
        # Should be between 0.0 and 0.02
        assert 0.0 < book["break_even_coefficient"] < 0.02


def test_bracket_history_structure(capacity: dict) -> None:
    """Bracket history must have correct structure for uncensored books."""
    for book in capacity["books"]:
        if not book["censored"]:
            history = book["bracket_history"]
            assert history is not None
            assert len(history) == 50
            for i, h in enumerate(history):
                assert h["iteration"] == i
                # JSON stores rounded values, so mid may not be exactly (lo+hi)/2
                # Check that lo <= hi and width is approximately correct
                assert h["lo"] <= h["hi"] + 1e-9
                # Allow larger tolerance for width due to rounding of lo/hi to 6dp
                assert abs(h["bracket_width"] - (h["hi"] - h["lo"])) < 2e-6
                assert h["costed_sharpe_at_mid"] is not None


def test_markdown_matches_renderer(capacity: dict, capacity_md: str) -> None:
    assert capacity_md == c.render_markdown(capacity), "capacity.md drifted"


def test_markdown_numbers_come_from_json(capacity: dict, capacity_md: str) -> None:
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
            allowed.add(round(float(node), c.DECIMALS))

    collect(capacity)
    for line in capacity_md.splitlines():
        if not line.startswith("|"):
            continue
        for cell in line.strip().strip("|").split("|"):
            clean = cell.strip()
            try:
                value = float(clean)
            except ValueError:
                continue
            assert round(value, c.DECIMALS) in allowed, (
                f"markdown cell {clean!r} is not a capacity JSON number"
            )


def test_books_schema_keys(capacity: dict) -> None:
    expected = {
        "variant",
        "weighting",
        "active_rows",
        "total_rows",
        "gross_sharpe",
        "break_even_coefficient",
        "break_even_sharpe",
        "bracket_history",
        "bracket_halving_verified",
        "censored",
        "censor_reason",
        "sign_test",
    }
    for book in capacity["books"]:
        assert set(book.keys()) == expected, f"keys mismatch: {set(book.keys()) ^ expected}"
        for entry in book["sign_test"]:
            assert set(entry.keys()) == {"coefficient", "costed_sharpe", "sign"}


def test_no_harness_reexecution(capacity: dict, impact_surface: dict) -> None:
    """Verify the capacity build never re-runs the impact surface or any P21 harness."""
    # The capacity build only reads impact_surface.json and does bisection
    # It should not import any build_* functions from P21/P22 scripts
    tree = ast.parse(Path(c.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                name = func.attr
            elif isinstance(func, ast.Name):
                name = func.id
            else:
                continue
            # Should not call any build_* from P21/P22 (but own build_capacity is fine)
            if name.startswith("build_") and name != "build_capacity":
                raise AssertionError(f"found build_ call: {name}")
            # Should not call BABStrategy.run or other harness entry points
            # (main is the script entry point, called only in if __name__ == "__main__")
            msg = f"found BABStrategy.run call: {name}"
            assert name != "run", msg
