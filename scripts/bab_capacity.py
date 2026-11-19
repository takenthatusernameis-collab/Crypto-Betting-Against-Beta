#!/usr/bin/env python3
"""P22 WP3 — capacity / break-even via fixed-iteration bisection on the
committed WP2 impact surface.

Loads ``research_state/bab_p22/impact_surface.json`` read-only and for each
book computes the participation-rate break-even (the impact coefficient at
which the costed Sharpe crosses zero) by fixed-iteration bisection on the
discrete impact-coefficient grid.

For every book that exhibits a zero crossing (costed Sharpe positive at
coefficient=0 and negative at some higher coefficient), the bisection proves
each bracket provably halves every iteration. Books without a crossing are
censored with a documented reason (never a midpoint). A per-row zero-crossing
sign test is pinned for every active book.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_capacity.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SCHEMA = "bab_p22.capacity/1"
OUTPUT_DIR = "research_state/bab_p22"
IMPACT_SURFACE_PATH = "research_state/bab_p22/impact_surface.json"
IMPACT_COMPONENT = "market_impact"
DECIMALS = 6
DEGENERATE_TOL = 1e-12

# Bisection settings: fixed iterations, never adaptive.
BISECTION_ITERATIONS = 50
BISECTION_TOL = 1e-12


def _clean(value: float) -> float:
    return round(float(value), DECIMALS)


def _clean_history(history: list[dict]) -> list[dict]:
    """Clean a bracket history for JSON output."""
    return [
        {
            "iteration": h["iteration"],
            "lo": _clean(h["lo"]),
            "hi": _clean(h["hi"]),
            "mid": _clean(h["mid"]),
            "costed_sharpe_at_mid": (
                _clean(h["costed_sharpe_at_mid"])
                if h["costed_sharpe_at_mid"] is not None
                else None
            ),
            "bracket_width": _clean(h["bracket_width"]),
        }
        for h in history
    ]


def _clean_book(book: dict) -> dict:
    """Clean a book dict for JSON output."""
    cleaned = {k: _clean(v) if isinstance(v, float) else v for k, v in book.items()}
    if cleaned["bracket_history"] is not None:
        cleaned["bracket_history"] = _clean_history(cleaned["bracket_history"])
    cleaned["sign_test"] = [
        {
            "coefficient": _clean(e["coefficient"]),
            "costed_sharpe": _clean(e["costed_sharpe"]) if e["costed_sharpe"] is not None else None,
            "sign": e["sign"],
        }
        for e in book["sign_test"]
    ]
    return cleaned


def _load_json(path: str) -> dict:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


def _panel_sha(panel) -> str:
    blob = json.dumps(panel, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _interpolate_sharpe_at_coefficient(
    impact_surface: dict, coefficient: float, variant: str, weighting: str
) -> float | None:
    """Interpolate costed Sharpe at an arbitrary coefficient for a specific book.

    The impact surface provides costed_sharpe at discrete coefficient levels.
    We linearly interpolate between the two adjacent grid points that bracket
    the requested coefficient. If coefficient is outside the grid, return None.
    """
    grid = impact_surface["provenance"]["impact_coefficient_grid"]
    if coefficient < grid[0] or coefficient > grid[-1]:
        return None
    if coefficient == grid[0]:
        # Find the specific book's first level
        for book in impact_surface["books"]:
            if book["variant"] == variant and book["weighting"] == weighting:
                if not book["censored"] and book["surfaces"] is not None:
                    rows = book["surfaces"][IMPACT_COMPONENT]
                    if rows:
                        return rows[0]["costed_sharpe"]
                break
        return None

    # Find the specific book and get its rows
    book = None
    for b in impact_surface["books"]:
        if b["variant"] == variant and b["weighting"] == weighting:
            book = b
            break

    if book is None or book["censored"] or book["surfaces"] is None:
        return None

    rows = book["surfaces"][IMPACT_COMPONENT]

    # Find the two adjacent grid points
    for i in range(len(grid) - 1):
        if grid[i] <= coefficient <= grid[i + 1]:
            if len(rows) > i + 1:
                lo_sharpe = rows[i]["costed_sharpe"]
                hi_sharpe = rows[i + 1]["costed_sharpe"]
                if lo_sharpe is not None and hi_sharpe is not None:
                    t = (coefficient - grid[i]) / (grid[i + 1] - grid[i])
                    return lo_sharpe + t * (hi_sharpe - lo_sharpe)
            break
    return None


def _book_zero_crossing_test(
    impact_surface: dict, variant: str, weighting: str
) -> dict:
    """Test if a book's costed Sharpe crosses zero and locate the crossing bracket.

    Returns a dict with:
    - has_crossing: bool
    - crossing_bracket: (lo_coeff, hi_coeff) or None
    - sign_test: list of (coefficient, costed_sharpe, sign) for each grid point
    """
    # Find the book
    book = None
    for b in impact_surface["books"]:
        if b["variant"] == variant and b["weighting"] == weighting:
            book = b
            break

    if book is None or book["censored"] or book["surfaces"] is None:
        return {
            "has_crossing": False,
            "crossing_bracket": None,
            "sign_test": [],
            "censor_reason": "book_not_found_or_censored",
        }

    rows = book["surfaces"][IMPACT_COMPONENT]
    grid = impact_surface["provenance"]["impact_coefficient_grid"]

    sign_test = []
    for row in rows:
        coeff = row["level"]
        sharpe = row["costed_sharpe"]
        sign = 1 if sharpe > 0 else (-1 if sharpe < 0 else 0)
        sign_test.append(
            {
                "coefficient": _clean(coeff),
                "costed_sharpe": _clean(sharpe) if sharpe is not None else None,
                "sign": sign,
            }
        )

    # Check for zero crossing: positive at coeff=0, negative at some higher coeff
    # (since Sharpe is non-increasing in coefficient)
    if len(rows) < 2:
        return {
            "has_crossing": False,
            "crossing_bracket": None,
            "sign_test": sign_test,
            "censor_reason": "insufficient_grid_points",
        }

    first_sharpe = rows[0]["costed_sharpe"]
    last_sharpe = rows[-1]["costed_sharpe"]

    if first_sharpe is None or last_sharpe is None:
        return {
            "has_crossing": False,
            "crossing_bracket": None,
            "sign_test": sign_test,
            "censor_reason": "non_finite_sharpe_at_grid_ends",
        }

    if first_sharpe <= 0:
        # Never positive at baseline -> no crossing from positive to negative
        return {
            "has_crossing": False,
            "crossing_bracket": None,
            "sign_test": sign_test,
            "censor_reason": "no_positive_sharpe_at_baseline",
        }

    if last_sharpe >= 0:
        # Never goes negative -> no crossing
        return {
            "has_crossing": False,
            "crossing_bracket": None,
            "sign_test": sign_test,
            "censor_reason": "no_negative_sharpe_at_max_coefficient",
        }

    # Find the bracket where sign changes from + to -
    for i in range(len(rows) - 1):
        if (
            rows[i]["costed_sharpe"] is not None
            and rows[i + 1]["costed_sharpe"] is not None
            and rows[i]["costed_sharpe"] > 0
            and rows[i + 1]["costed_sharpe"] <= 0
        ):
            return {
                "has_crossing": True,
                "crossing_bracket": (_clean(grid[i]), _clean(grid[i + 1])),
                "sign_test": sign_test,
                "censor_reason": None,
            }

    return {
        "has_crossing": False,
        "crossing_bracket": None,
        "sign_test": sign_test,
        "censor_reason": "no_sign_change_detected",
    }


def _bisect_break_even(
    impact_surface: dict, lo: float, hi: float, variant: str, weighting: str
) -> tuple[float, list[dict]]:
    """Fixed-iteration bisection to find the break-even coefficient.

    Returns (break_even_coefficient, bracket_history) where bracket_history
    records each iteration's lo, hi, mid, and costed_sharpe_at_mid.
    """
    history = []
    for iteration in range(BISECTION_ITERATIONS):
        mid = (lo + hi) / 2.0
        mid_sharpe = _interpolate_sharpe_at_coefficient(
            impact_surface, mid, variant, weighting
        )
        bracket_width = hi - lo
        history.append(
            {
                "iteration": iteration,
                "lo": lo,
                "hi": hi,
                "mid": mid,
                "costed_sharpe_at_mid": mid_sharpe,
                "bracket_width": bracket_width,
            }
        )
        if mid_sharpe is None:
            # Should not happen if bracket is valid
            break
        if mid_sharpe > 0:
            lo = mid
        else:
            hi = mid

    break_even = (lo + hi) / 2.0
    return _clean(break_even), history


def _verify_bracket_halving(history: list[dict]) -> bool:
    """Verify each bracket provably halves every iteration."""
    if len(history) < 2:
        return False
    for i in range(1, len(history)):
        prev_width = history[i - 1]["bracket_width"]
        curr_width = history[i]["bracket_width"]
        if curr_width > prev_width * 0.5 + 1e-12:
            return False
    return True


def _censor_book(
    variant: str,
    weighting: str,
    active_rows: int,
    total_rows: int,
    gross_sharpe: float,
    reason: str,
    sign_test: list[dict],
) -> dict:
    return {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "total_rows": total_rows,
        "gross_sharpe": _clean(gross_sharpe),
        "break_even_coefficient": None,
        "break_even_sharpe": None,
        "bracket_history": None,
        "bracket_halving_verified": False,
        "censored": True,
        "censor_reason": reason,
        "sign_test": sign_test,
    }


def _build_book_capacity(impact_surface: dict, variant: str, weighting: str) -> dict:
    """Build the capacity record for one book."""
    # Find the book in the impact surface
    book = None
    for b in impact_surface["books"]:
        if b["variant"] == variant and b["weighting"] == weighting:
            book = b
            break

    if book is None:
        return _censor_book(variant, weighting, 0, 0, 0.0, "book_not_found", [])

    active_rows = book["active_rows"]
    total_rows = book["total_rows"]
    gross_sharpe = book["gross_sharpe"]
    sign_test = _book_zero_crossing_test(impact_surface, variant, weighting)

    if not sign_test["has_crossing"]:
        return _censor_book(
            variant,
            weighting,
            active_rows,
            total_rows,
            gross_sharpe,
            sign_test["censor_reason"] or "no_zero_crossing",
            sign_test["sign_test"],
        )

    # Has crossing - do bisection
    lo, hi = sign_test["crossing_bracket"]
    break_even, history = _bisect_break_even(
        impact_surface, lo, hi, variant, weighting
    )
    halving_verified = _verify_bracket_halving(history)

    # Verify the break-even Sharpe is approximately zero
    break_even_sharpe = _interpolate_sharpe_at_coefficient(
        impact_surface, break_even, variant, weighting
    )

    return {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "total_rows": total_rows,
        "gross_sharpe": _clean(gross_sharpe),
        "break_even_coefficient": break_even,
        "break_even_sharpe": _clean(break_even_sharpe) if break_even_sharpe is not None else None,
        "bracket_history": history,
        "bracket_halving_verified": halving_verified,
        "censored": False,
        "censor_reason": None,
        "sign_test": sign_test["sign_test"],
    }


def build_capacity(impact_surface_payload: dict | None = None) -> dict:
    """Build the capacity payload (pure, no I/O beyond committed JSON)."""
    if impact_surface_payload is None:
        impact_surface_payload = _load_json(IMPACT_SURFACE_PATH)

    impact_prov = impact_surface_payload["provenance"]
    universe_seed = impact_prov.get("universe_seed")
    panel_sha256 = impact_prov.get("panel_sha256", {})

    VARIANTS = ("planted", "null")
    WEIGHTINGS = ("equal", "rank")

    books = [
        _build_book_capacity(impact_surface_payload, variant, weighting)
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    ]

    # Clean books for JSON output (round floats to DECIMALS)
    cleaned_books = [_clean_book(b) for b in books]

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_capacity.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "source_impact_surface": IMPACT_SURFACE_PATH,
            "source_impact_surface_schema": impact_surface_payload["schema"],
            "universe_seed": universe_seed,
            "panel_sha256": panel_sha256,
            "impact_component": IMPACT_COMPONENT,
            "impact_coefficient_grid": [
                _clean(v) for v in impact_prov["impact_coefficient_grid"]
            ],
            "bisection_iterations": BISECTION_ITERATIONS,
            "bisection_tol": BISECTION_TOL,
            "method": (
                "loads the committed P22 WP2 impact_surface.json read-only; "
                "for each book, tests for a zero crossing in costed Sharpe across "
                "the impact-coefficient grid (positive at coefficient=0, negative "
                "at some higher coefficient); if a crossing exists, computes the "
                "break-even coefficient via fixed-iteration bisection (50 "
                "iterations) proving each bracket halves every iteration; books "
                "without a crossing are censored with a documented reason, never a "
                "midpoint; a per-row zero-crossing sign test is pinned for every "
                "active book; never regenerates or imports any P21/P22 WP0-WP2 "
                "harness."
            ),
            "caveat": (
                "Break-even on a planted synthetic universe proves the estimator's "
                "capacity under market impact; it is never market alpha. A "
                "null-universe break-even is undefined (censored). NO-GO for "
                "market deployment until a maintainer supplies a licensed price "
                "series."
            ),
        },
        "books": cleaned_books,
    }


def render_markdown(payload: dict) -> str:
    """Render the capacity summary from the payload; no external numbers."""
    prov = payload["provenance"]
    grid_str = json.dumps(prov["impact_coefficient_grid"], sort_keys=True)
    lines = [
        "# BAB P22 WP3 — capacity / break-even on the WP2 impact surface",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        (
            f"Source: `{prov['source_impact_surface']}` "
            f"({prov['source_impact_surface_schema']}); "
            f"universe seed {prov['universe_seed']}; "
            f"component: `{prov['impact_component']}`; "
            f"impact coefficient grid: {grid_str}; "
            f"bisection iterations: {prov['bisection_iterations']}; "
            f"bracket-halving verified per book."
        ),
        "",
        (
            "| variant | weighting | active_rows | gross_sharpe | "
            "break_even_coefficient | break_even_sharpe | censored | "
            "censor_reason | bracket_halving_verified |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for book in payload["books"]:
        be_coeff = (
            book["break_even_coefficient"]
            if book["break_even_coefficient"] is not None
            else "n/a"
        )
        be_sharpe = (
            book["break_even_sharpe"]
            if book["break_even_sharpe"] is not None
            else "n/a"
        )
        lines.append(
            "| {variant} | {weighting} | {active_rows} | {gross_sharpe} | "
            "{break_even_coefficient} | {break_even_sharpe} | {censored} | "
            "{censor_reason} | {bracket_halving_verified} |".format(
                variant=book["variant"],
                weighting=book["weighting"],
                active_rows=book["active_rows"],
                gross_sharpe=book["gross_sharpe"],
                break_even_coefficient=be_coeff,
                break_even_sharpe=be_sharpe,
                censored=book["censored"],
                censor_reason=book["censor_reason"] or "n/a",
                bracket_halving_verified=book["bracket_halving_verified"],
            )
        )

    # Sign test table
    lines.extend(
        [
            "",
            "## Per-row zero-crossing sign test",
            "",
            "| variant | weighting | coefficient | costed_sharpe | sign |",
            "|---|---|---|---|---|",
        ]
    )
    for book in payload["books"]:
        for entry in book["sign_test"]:
            sharpe_str = (
                f"{entry['costed_sharpe']:.6f}"
                if entry["costed_sharpe"] is not None
                else "n/a"
            )
            lines.append(
                "| {variant} | {weighting} | {coefficient} | {sharpe} | {sign} |".format(
                    variant=book["variant"],
                    weighting=book["weighting"],
                    coefficient=f"{entry['coefficient']:.6f}",
                    sharpe=sharpe_str,
                    sign=entry["sign"],
                )
            )

    # Bracket history for uncensored books
    for book in payload["books"]:
        if not book["censored"] and book["bracket_history"]:
            lines += [
                "",
                f"## Bracket history — {book['variant']} / {book['weighting']}",
                "",
                "| iteration | lo | hi | mid | costed_sharpe_at_mid | bracket_width |",
                "|---|---|---|---|---|---|",
            ]
            for h in book["bracket_history"]:
                sharpe_str = (
                    f"{_clean(h['costed_sharpe_at_mid']):.6f}"
                    if h["costed_sharpe_at_mid"] is not None
                    else "n/a"
                )
                lines.append(
                    "| {iteration} | {lo} | {hi} | {mid} | {sharpe} | {width} |".format(
                        iteration=h["iteration"],
                        lo=f"{_clean(h['lo']):.6f}",
                        hi=f"{_clean(h['hi']):.6f}",
                        mid=f"{_clean(h['mid']):.6f}",
                        sharpe=sharpe_str,
                        width=f"{_clean(h['bracket_width']):.6f}",
                    )
                )

    lines += [
        "",
        f"Method: {prov['method']}",
        "",
        f"Caveat: {prov['caveat']}",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "capacity.json"
    markdown_path = directory / "capacity.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_capacity()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for book in payload["books"]:
        status = (
            "CENSORED (" + str(book["censor_reason"]) + ")"
            if book["censored"]
            else f"break_even={book['break_even_coefficient']:.6f}"
        )
        print(
            f"{book['variant']:7s} {book['weighting']:5s} "
            f"active={book['active_rows']} {status}"
        )
        if not book["censored"] and book["bracket_history"]:
            h = book["bracket_history"][-1]
            print(
                f"  final bracket: lo={_clean(h['lo']):.6f} hi={_clean(h['hi']):.6f} "
                f"width={_clean(h['bracket_width']):.6e}"
            )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
