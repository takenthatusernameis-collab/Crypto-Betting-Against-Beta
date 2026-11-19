"""Acceptance tests for P22 WP2: nonlinear market-impact surface.

These tests are the claim that ``scripts/bab_impact_surface.py``:

* loads the committed WP3 cost surface and WP0 universe **read-only** and
  never regenerates them nor imports any P21 / P22 WP0-WP1 build harness;
* is byte-identical across reruns (hash determinism) and its committed JSON
  and markdown artifacts match a fresh build/render;
* layers a square-root market-impact model (per-period drag =
  ``coefficient * turnover ** 1.5``) on the committed WP3 exposure series;
* proves ``coefficient = 0`` reproduces the linear (zero-cost) baseline
  exactly;
* proves per-book **and** per-period costed Sharpe is non-increasing in the
  impact coefficient;
* reports censoring with a documented reason and ``surfaces=None`` rather
  than a zero tolerance.

They never touch the network, never edit product code, and never regenerate
``research_state/bab_p21/universe.json`` or ``cost_surface.json``.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pytest

from scripts import bab_impact_surface

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p22/impact_surface.json"
MD_PATH = REPO_ROOT / "research_state/bab_p22/impact_surface.md"
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
COST_SURFACE_PATH = REPO_ROOT / "research_state/bab_p21/cost_surface.json"

NUMERIC_TOKEN = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
EPS = 1e-12

_VARIANTS = ("planted", "null")
_WEIGHTINGS = ("equal", "rank")
_COMPONENT = bab_impact_surface.IMPACT_COMPONENT


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def _book(payload: dict, variant: str, weighting: str) -> dict:
    for book in payload["books"]:
        if book["variant"] == variant and book["weighting"] == weighting:
            return book
    raise AssertionError(f"no book for variant={variant!r} weighting={weighting!r}")


def _numeric_values(text: str) -> set[float]:
    return {float(token) for token in NUMERIC_TOKEN.findall(text)}


def test_schema_and_provenance(payload: dict) -> None:
    assert payload["schema"] == bab_impact_surface.SCHEMA == "bab_p22.impact_surface/1"
    prov = payload["provenance"]
    assert prov["generator"] == "scripts/bab_impact_surface.py"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert "never market alpha" in prov["caveat"]
    assert prov["universe_seed"] == 20261118
    assert prov["impact_component"] == _COMPONENT
    assert prov["trading_days"] == 252
    grid = prov["impact_coefficient_grid"]
    assert len(grid) >= 2
    assert grid[0] == 0.0, "impact grid lacks a zero-coefficient baseline"
    assert all(level >= 0.0 for level in grid)
    assert grid == sorted(grid), "impact grid is not ascending"
    cfg = prov["config"]
    assert cfg["benchmark"] == "BTC"
    assert cfg["beta_window"] == 90
    assert cfg["min_observations"] == 60
    assert cfg["long_quantile"] == 0.3
    assert cfg["short_quantile"] == 0.3
    assert cfg["transaction_costs"] == 0.0
    assert cfg["slippage"] == 0.0
    assert cfg["beta_neutral"] is True
    assert cfg["rank_min_leg_beta"] == 0.20
    assert cfg["rank_max_gross"] == 4.0


def test_determinism_two_builds() -> None:
    first = json.dumps(bab_impact_surface.build_impact_surface(), indent=2, sort_keys=True)
    second = json.dumps(bab_impact_surface.build_impact_surface(), indent=2, sort_keys=True)
    assert first == second
    first_sha = hashlib.sha256(first.encode("utf-8")).hexdigest()
    second_sha = hashlib.sha256(second.encode("utf-8")).hexdigest()
    assert first_sha == second_sha
    assert len(first_sha) == 64


def test_committed_json_matches_fresh_build() -> None:
    fresh = (
        json.dumps(bab_impact_surface.build_impact_surface(), indent=2, sort_keys=True) + "\n"
    )
    assert JSON_PATH.read_text(encoding="utf-8") == fresh


def test_committed_markdown_matches_renderer(payload: dict) -> None:
    fresh = bab_impact_surface.render_markdown(payload)
    assert MD_PATH.read_text(encoding="utf-8") == fresh
    assert fresh == bab_impact_surface.render_markdown(
        bab_impact_surface.build_impact_surface()
    )


def test_inputs_are_read_only() -> None:
    universe_before = UNIVERSE_PATH.read_bytes()
    cost_surface_before = COST_SURFACE_PATH.read_bytes()
    bab_impact_surface.build_impact_surface()
    assert UNIVERSE_PATH.read_bytes() == universe_before, "universe.json was mutated"
    assert COST_SURFACE_PATH.read_bytes() == cost_surface_before, "cost_surface.json was mutated"


def test_never_imports_a_p21_harness() -> None:
    import ast

    tree = ast.parse(Path(bab_impact_surface.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module not in (
                "scripts.bab_synthetic_universe",
                "scripts.bab_rank_eval",
                "scripts.bab_significance",
                "scripts.bab_cost_surface",
                "scripts.bab_p22_charter",
                "scripts.bab_null_battery",
            ), module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in (
                    "scripts",
                    "strategies",
                ), alias.name


def test_panel_sha256_matches_universe_and_cost_surface(payload: dict) -> None:
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    cost_surface = json.loads(COST_SURFACE_PATH.read_text(encoding="utf-8"))
    prov = payload["provenance"]
    for variant in _VARIANTS:
        expected = universe["panels"][variant]["sha256"]
        assert prov["panel_sha256"][variant] == expected
        assert cost_surface["provenance"]["panel_sha256"][variant] == expected


def test_coefficient_grid_with_zero_baseline(payload: dict) -> None:
    grid = payload["provenance"]["impact_coefficient_grid"]
    assert grid[0] == 0.0
    for book in payload["books"]:
        rows = book["surfaces"][_COMPONENT]
        levels = [row["level"] for row in rows]
        assert levels == grid, f"{book['variant']}/{book['weighting']} grid mismatch"


def test_all_four_books_active_and_uncensored(payload: dict) -> None:
    seen = set()
    for variant in _VARIANTS:
        for weighting in _WEIGHTINGS:
            book = _book(payload, variant, weighting)
            seen.add((book["variant"], book["weighting"]))
            assert book["censored"] is False, (variant, weighting)
            assert book["censor_reason"] is None, (variant, weighting)
            assert book["active_rows"] == 541, (variant, weighting)
            assert book["total_rows"] == 600, (variant, weighting)
            assert book["gross_sharpe"] is not None, (variant, weighting)
            assert book["impact_exposure_mean"] is not None, (variant, weighting)
            assert _COMPONENT in book["surfaces"], (variant, weighting)
    assert seen == {(v, w) for v in _VARIANTS for w in _WEIGHTINGS}


def test_zero_coefficient_reproduces_gross_baseline(payload: dict) -> None:
    """coefficient == 0 must reproduce the zero-cost (gross) book exactly."""
    for book in payload["books"]:
        rows = book["surfaces"][_COMPONENT]
        zero = rows[0]
        assert zero["level"] == 0.0
        assert zero["costed_sharpe"] == book["gross_sharpe"]
        assert zero["cost_drag_mean"] == 0.0
        assert zero["total_cost"] == 0.0
        assert zero["final_cumulative"] == book["gross_final_cumulative"]


def test_per_book_costed_sharpe_non_increasing_in_coefficient(payload: dict) -> None:
    for book in payload["books"]:
        assert book["censored"] is False
        assert book["monotonicity"][_COMPONENT] is True, (
            f"{book['variant']}/{book['weighting']} not monotone"
        )
        rows = book["surfaces"][_COMPONENT]
        sharpes = [row["costed_sharpe"] for row in rows]
        assert all(value is not None for value in sharpes)
        for previous, current in zip(sharpes, sharpes[1:]):
            assert current <= previous + EPS, (
                f"{book['variant']}/{book['weighting']} Sharpe rose from "
                f"{previous} to {current}"
            )


def test_per_period_costed_returns_non_increasing_in_coefficient(payload: dict) -> None:
    for book in payload["books"]:
        assert book["period_wise_non_increasing"][_COMPONENT] is True, (
            f"{book['variant']}/{book['weighting']} not period-wise non-increasing"
        )


def test_impact_drag_scales_with_participation_1_5() -> None:
    """Per-period drag = coefficient * turnover**1.5, so mean drag is
    linear in the coefficient with slope mean(turnover**1.5)."""
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    for variant in _VARIANTS:
        for weighting in _WEIGHTINGS:
            book = _book(
                json.loads(JSON_PATH.read_text(encoding="utf-8")), variant, weighting
            )
            rows = book["surfaces"][_COMPONENT]
            nonzero = [row for row in rows if row["level"] > 0.0]
            assert nonzero, f"{variant}/{weighting} has no nonzero coefficient"
            slope = book["impact_exposure_mean"]
            assert slope is not None and slope >= 0.0
            for row in nonzero:
                expected_drag = row["level"] * slope
                assert abs(row["cost_drag_mean"] - expected_drag) <= 1e-6 + 1e-9, (
                    f"{variant}/{weighting} level={row['level']} drag "
                    f"{row['cost_drag_mean']} != level * impact_exposure_mean "
                    f"{expected_drag}"
                )


def test_cost_accumulates_with_coefficient(payload: dict) -> None:
    for book in payload["books"]:
        rows = book["surfaces"][_COMPONENT]
        drags = [row["cost_drag_mean"] for row in rows]
        costs = [row["total_cost"] for row in rows]
        cumulatives = [row["final_cumulative"] for row in rows]
        for previous, current in zip(drags, drags[1:]):
            assert current >= previous - EPS
        for previous, current in zip(costs, costs[1:]):
            assert current >= previous - EPS
        for previous, current in zip(cumulatives, cumulatives[1:]):
            assert current <= previous + EPS


def test_censoring_reports_documented_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    import pandas as pd

    index = pd.date_range("2024-01-02", periods=120, freq="B")

    class _ZeroResult:
        def __init__(self) -> None:
            self.weights = pd.DataFrame(0.0, index=index, columns=["BTC", "A001"])
            self.backtest = {"returns": pd.Series(0.0, index=index)}

    class _ZeroStrategy:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def run(self, returns_df: object = None) -> _ZeroResult:
            return _ZeroResult()

    monkeypatch.setattr(bab_impact_surface, "BABStrategy", _ZeroStrategy)
    book = bab_impact_surface._book_surface(
        "planted",
        "equal",
        {
            "assets": ["A001"],
            "provenance": {
                "date_start": "2024-01-02",
                "return_rows": 120,
                "date_freq": "B",
                "benchmark": "BTC",
            },
            "panels": {
                "planted": {"returns": [[0.0]] * 120, "sha256": "x", "shape": [120, 1]},
                "null": {"returns": [[0.0]] * 120, "sha256": "x", "shape": [120, 1]},
            },
            "benchmark": [0.0] * 120,
        },
    )
    assert book["censored"] is True
    assert book["surfaces"] is None
    reason = book["censor_reason"]
    assert isinstance(reason, str) and reason
    assert ":" in reason
    assert "inactive_book" in reason
    assert book["monotonicity"][_COMPONENT] is False
    assert book["period_wise_non_increasing"][_COMPONENT] is False


def test_markdown_numbers_derived_from_json(payload: dict) -> None:
    json_values = _numeric_values(json.dumps(payload, sort_keys=True))
    markdown = MD_PATH.read_text(encoding="utf-8")
    markdown_values = _numeric_values(markdown.replace("|", " "))
    missing = sorted(value for value in markdown_values if value not in json_values)
    assert not missing, f"markdown numbers absent from JSON: {missing[:10]}"


def test_books_schema_keys(payload: dict) -> None:
    expected = {
        "variant",
        "weighting",
        "active_rows",
        "total_rows",
        "gross_sharpe",
        "gross_turnover_mean",
        "impact_exposure_mean",
        "gross_final_cumulative",
        "censored",
        "censor_reason",
        "surfaces",
        "monotonicity",
        "period_wise_non_increasing",
    }
    for book in payload["books"]:
        assert set(book.keys()) == expected
        assert set(book["monotonicity"]) == {_COMPONENT}
        assert set(book["period_wise_non_increasing"]) == {_COMPONENT}
        for row in book["surfaces"][_COMPONENT]:
            assert set(row.keys()) == {
                "level",
                "costed_sharpe",
                "cost_drag_mean",
                "total_cost",
                "final_cumulative",
            }
