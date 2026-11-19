"""Acceptance tests for P21 WP3: multi-component cost surface.

These tests are the claim that ``scripts/bab_cost_surface.py``:

* loads the committed WP0 universe and WP1 rank evaluation **read-only** and
  never regenerates them,
* is byte-identical across reruns (hash determinism) and its committed JSON
  and markdown artifacts match a fresh build/render,
* covers **three** cost components (linear transaction cost, borrow/funding,
  notional slippage) with a zero-cost baseline,
* proves per-book **and** per-period costed performance is non-increasing in
  every component level, and that cost drag / total cost are non-decreasing,
* reports censoring with a documented reason and ``surfaces=None`` rather than
  a zero tolerance.

They never touch the network, never edit product code, and never regenerate
``research_state/bab_p21/universe.json`` or ``rank_eval.json``.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import bab_cost_surface, bab_rank_eval, bab_synthetic_universe

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p21/cost_surface.json"
MD_PATH = REPO_ROOT / "research_state/bab_p21/cost_surface.md"
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
RANK_EVAL_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.json"

NUMERIC_TOKEN = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
EPS = 1e-12

_VARIANTS = ("planted", "null")
_WEIGHTINGS = ("equal", "rank")
_COMPONENTS = ("borrow_funding", "linear_transaction_cost", "notional_slippage")


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
    assert payload["schema"] == bab_cost_surface.SCHEMA == "bab_p21.cost_surface/1"
    prov = payload["provenance"]
    assert prov["generator"] == "scripts/bab_cost_surface.py"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert "never market alpha" in prov["caveat"]
    assert prov["universe_seed"] == 20261118
    assert prov["trading_days"] == 252
    assert set(prov["component_grids"]) == set(_COMPONENTS)
    assert len(prov["component_grids"]) >= 3
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
    first = json.dumps(bab_cost_surface.build_cost_surface(), indent=2, sort_keys=True)
    second = json.dumps(bab_cost_surface.build_cost_surface(), indent=2, sort_keys=True)
    assert first == second
    first_sha = hashlib.sha256(first.encode("utf-8")).hexdigest()
    second_sha = hashlib.sha256(second.encode("utf-8")).hexdigest()
    assert first_sha == second_sha
    assert len(first_sha) == 64


def test_committed_json_matches_fresh_build() -> None:
    fresh = (
        json.dumps(bab_cost_surface.build_cost_surface(), indent=2, sort_keys=True) + "\n"
    )
    assert JSON_PATH.read_text(encoding="utf-8") == fresh


def test_committed_markdown_matches_renderer(payload: dict) -> None:
    fresh = bab_cost_surface.render_markdown(payload)
    assert MD_PATH.read_text(encoding="utf-8") == fresh
    assert fresh == bab_cost_surface.render_markdown(
        bab_cost_surface.build_cost_surface()
    )


def test_inputs_are_read_only() -> None:
    universe_before = UNIVERSE_PATH.read_bytes()
    rank_eval_before = RANK_EVAL_PATH.read_bytes()
    bab_cost_surface.build_cost_surface()
    assert UNIVERSE_PATH.read_bytes() == universe_before, "universe.json was mutated"
    assert RANK_EVAL_PATH.read_bytes() == rank_eval_before, "rank_eval.json was mutated"

    fresh_universe = (
        json.dumps(bab_synthetic_universe.build_universe(), indent=2, sort_keys=True) + "\n"
    )
    assert UNIVERSE_PATH.read_text(encoding="utf-8") == fresh_universe
    fresh_rank_eval = (
        json.dumps(bab_rank_eval.build_rank_eval(), indent=2, sort_keys=True) + "\n"
    )
    assert RANK_EVAL_PATH.read_text(encoding="utf-8") == fresh_rank_eval


def test_panel_sha256_matches_universe_and_rank_eval(payload: dict) -> None:
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    rank_eval = json.loads(RANK_EVAL_PATH.read_text(encoding="utf-8"))
    prov = payload["provenance"]
    for variant in _VARIANTS:
        expected = universe["panels"][variant]["sha256"]
        assert prov["panel_sha256"][variant] == expected
        assert rank_eval["provenance"]["panel_sha256"][variant] == expected


def test_three_components_with_zero_baseline(payload: dict) -> None:
    grids = payload["provenance"]["component_grids"]
    assert set(grids) == set(_COMPONENTS)
    for component, grid in grids.items():
        assert len(grid) >= 2, component
        assert grid[0] == 0.0, f"{component} lacks a zero-cost baseline"
        assert all(level >= 0.0 for level in grid), component
        assert grid == sorted(grid), f"{component} grid is not ascending"
        assert len({float(level) for level in grid}) == len(grid), component


def test_all_four_books_active_and_uncensored(payload: dict) -> None:
    seen = set()
    for variant in _VARIANTS:
        for weighting in _WEIGHTINGS:
            book = _book(payload, variant, weighting)
            seen.add((book["variant"], book["weighting"]))
            assert book["censored"] is False
            assert book["censor_reason"] is None
            assert book["active_rows"] == 541, (variant, weighting)
            assert book["total_rows"] == 600
            assert book["gross_sharpe"] is not None
            assert set(book["surfaces"]) == set(_COMPONENTS)
    assert seen == {(v, w) for v in _VARIANTS for w in _WEIGHTINGS}


def test_per_book_costed_sharpe_non_increasing(payload: dict) -> None:
    for book in payload["books"]:
        assert book["censored"] is False
        for component in _COMPONENTS:
            assert book["monotonicity"][component] is True, (
                f"{book['variant']}/{book['weighting']}/{component} not monotone"
            )
            rows = book["surfaces"][component]
            sharpes = [row["costed_sharpe"] for row in rows]
            assert all(value is not None for value in sharpes)
            for previous, current in zip(sharpes, sharpes[1:]):
                assert current <= previous + EPS, (
                    f"{book['variant']}/{book['weighting']}/{component} "
                    f"Sharpe rose from {previous} to {current}"
                )


def test_per_period_costed_returns_non_increasing(payload: dict) -> None:
    for book in payload["books"]:
        for component in _COMPONENTS:
            assert book["period_wise_non_increasing"][component] is True, (
                f"{book['variant']}/{book['weighting']}/{component} not "
                "period-wise non-increasing"
            )


def test_zero_level_reproduces_gross_book(payload: dict) -> None:
    for book in payload["books"]:
        for component in _COMPONENTS:
            row = book["surfaces"][component][0]
            assert row["level"] == 0.0
            assert row["costed_sharpe"] == book["gross_sharpe"]
            assert row["cost_drag_mean"] == 0.0
            assert row["total_cost"] == 0.0
            assert row["final_cumulative"] == book["gross_final_cumulative"]


def test_cost_accumulates_with_level(payload: dict) -> None:
    for book in payload["books"]:
        for component in _COMPONENTS:
            rows = book["surfaces"][component]
            drags = [row["cost_drag_mean"] for row in rows]
            costs = [row["total_cost"] for row in rows]
            cumulatives = [row["final_cumulative"] for row in rows]
            for previous, current in zip(drags, drags[1:]):
                assert current >= previous - EPS
            for previous, current in zip(costs, costs[1:]):
                assert current >= previous - EPS
            for previous, current in zip(cumulatives, cumulatives[1:]):
                assert current <= previous + EPS


def test_total_cost_is_linear_in_level(payload: dict) -> None:
    for book in payload["books"]:
        for component in _COMPONENTS:
            rows = [row for row in book["surfaces"][component] if row["level"] > 0.0]
            ratios = [row["total_cost"] / row["level"] for row in rows]
            assert ratios
            # Use the largest level as the reference: its 6-dp rounding error
            # is smallest relative to the level, so the tolerance only has to
            # absorb the current row's rounding.
            reference = ratios[-1]
            for row, ratio in zip(rows, ratios):
                tolerance = 1e-6 + 5.1e-7 / row["level"] + 2.6e-6
                assert abs(ratio - reference) <= tolerance, (
                    f"{book['variant']}/{book['weighting']}/{component} total "
                    "cost is not linear in the component level"
                )


def test_cost_drag_mean_matches_total_cost(payload: dict) -> None:
    for book in payload["books"]:
        for component in _COMPONENTS:
            for row in book["surfaces"][component]:
                expected = row["total_cost"] / book["total_rows"]
                assert abs(row["cost_drag_mean"] - expected) <= 1e-3, (
                    f"{book['variant']}/{book['weighting']}/{component} mean "
                    "drag inconsistent with total cost"
                )


def test_exposure_series_is_non_negative() -> None:
    weights = np.array([[1.0, -1.0], [0.5, -0.5], [0.0, 0.0]])
    turnover, short_notional = bab_cost_surface._exposure_series(weights)
    assert np.array_equal(turnover, np.array([2.0, 1.0, 1.0]))
    assert np.array_equal(short_notional, np.array([1.0, 0.5, 0.0]))
    assert bool((turnover >= 0.0).all())
    assert bool((short_notional >= 0.0).all())


def test_censoring_reports_documented_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    index = pd.date_range("2024-01-02", periods=120, freq="B")

    class _ZeroResult:
        def __init__(self) -> None:
            self.weights = pd.DataFrame(
                0.0, index=index, columns=["BTC", "A001"]
            )
            self.backtest = {"returns": pd.Series(0.0, index=index)}

    class _ZeroStrategy:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def run(self, returns_df: object = None) -> _ZeroResult:
            return _ZeroResult()

    monkeypatch.setattr(bab_cost_surface, "BABStrategy", _ZeroStrategy)
    monkeypatch.setattr(
        bab_cost_surface.u,
        "build_returns_frame",
        lambda variant, payload: pd.DataFrame(
            0.0, index=index, columns=["BTC", "A001"]
        ),
    )
    book = bab_cost_surface._book_surface(
        "planted", "equal", {"assets": ["A001"], "provenance": {"benchmark": "BTC"}}
    )
    assert book["censored"] is True
    assert book["surfaces"] is None
    reason = book["censor_reason"]
    assert isinstance(reason, str) and reason
    assert ":" in reason
    assert "inactive_book" in reason
    assert all(book["monotonicity"][c] is False for c in _COMPONENTS)
    assert all(book["period_wise_non_increasing"][c] is False for c in _COMPONENTS)


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
        "gross_turnover_max",
        "short_notional_mean",
        "gross_final_cumulative",
        "censored",
        "censor_reason",
        "surfaces",
        "monotonicity",
        "period_wise_non_increasing",
    }
    for book in payload["books"]:
        assert set(book.keys()) == expected
        for component in _COMPONENTS:
            assert set(book["monotonicity"]) == set(_COMPONENTS)
            assert set(book["period_wise_non_increasing"]) == set(_COMPONENTS)
            for row in book["surfaces"][component]:
                assert set(row.keys()) == {
                    "level",
                    "costed_sharpe",
                    "cost_drag_mean",
                    "total_cost",
                    "final_cumulative",
                }
