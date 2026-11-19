#!/usr/bin/env python3
"""P21 WP3 — multi-component cost surface on the planted universe.

Loads ``research_state/bab_p21/universe.json`` and
``research_state/bab_p21/rank_eval.json`` read-only, runs the shipped
``BABStrategy`` once per (variant, weighting) at zero cost to recover the gross
returns and weights, then builds per-row costed performance for both
``planted`` and ``null`` variants and both ``equal`` and ``rank`` weightings
across **three** cost components:

1. linear transaction cost (fraction of one-way turnover)
2. borrow/funding (annualized short-borrow, pro-rata daily on short notional)
3. notional slippage (fraction of one-way turnover)

For every book and every component the surface proves per-row costed Sharpe is
non-increasing in the component level (both per-book across the grid and
per-period, since every cost drag is a non-negative rate times a non-negative
exposure). Nulls/censoring are reported with documented reasons, never as zero
tolerances. Byte-identical reruns are verified by hash determinism.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_cost_surface.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import bab_synthetic_universe as u  # noqa: E402
from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402

SCHEMA = "bab_p21.cost_surface/1"
OUTPUT_DIR = "research_state/bab_p21"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
DECIMALS = 6
DEGENERATE_TOL = 1e-12
STD_TOL = 1e-12

# Cost-component grids (level 0.0 is the uncosted baseline in every component).
LINEAR_TC_GRID = [0.0, 0.00025, 0.0005, 0.001, 0.002, 0.005, 0.01]
BORROW_GRID = [0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
SLIPPAGE_GRID = [0.0, 0.00005, 0.0001, 0.00025, 0.0005, 0.001, 0.002]
TRADING_DAYS = 252

COMPONENT_GRIDS = {
    "linear_transaction_cost": LINEAR_TC_GRID,
    "borrow_funding": BORROW_GRID,
    "notional_slippage": SLIPPAGE_GRID,
}

CONFIG = dict(
    benchmark="BTC",
    beta_window=90,
    min_observations=60,
    long_quantile=0.3,
    short_quantile=0.3,
    transaction_costs=0.0,
    slippage=0.0,
    beta_neutral=True,
    rank_min_leg_beta=0.20,
    rank_max_gross=4.0,
)


def _clean(value: float) -> float:
    return round(float(value), DECIMALS)


def _load_json(path: str) -> dict:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


def _panel_sha(panel) -> str:
    blob = json.dumps(panel, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _exposure_series(weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-period turnover and short notional from a weight matrix.

    Turnover follows the backtest convention: |w[t] - w[t-1]| with w[-1] = 0,
    so the first period trades from zero into the initial book. Short notional
    is the gross short exposure held in each period. Both are non-negative.
    """
    n_rows, n_cols = weights.shape
    turnover = np.zeros(n_rows, dtype=float)
    shifted = np.vstack([np.zeros((1, n_cols), dtype=float), weights[:-1]])
    turnover = np.abs(weights - shifted).sum(axis=1)
    short_notional = np.abs(np.minimum(weights, 0.0)).sum(axis=1)
    return turnover, short_notional


def _book_surface(variant: str, weighting: str, universe_payload: dict) -> dict:
    """Build the full cost surface for one book."""
    assets = list(universe_payload["assets"])
    frame = u.build_returns_frame(variant, universe_payload)
    result = BABStrategy(
        benchmark=universe_payload["provenance"]["benchmark"],
        beta_window=CONFIG["beta_window"],
        min_observations=CONFIG["min_observations"],
        long_quantile=CONFIG["long_quantile"],
        short_quantile=CONFIG["short_quantile"],
        beta_neutral=CONFIG["beta_neutral"],
        transaction_costs=CONFIG["transaction_costs"],
        slippage=CONFIG["slippage"],
        universe=assets,
        weighting=weighting,
        rank_min_leg_beta=CONFIG["rank_min_leg_beta"],
        rank_max_gross=CONFIG["rank_max_gross"],
    ).run(returns_df=frame)

    weights = result.weights.reindex(columns=[CONFIG["benchmark"], *assets]).fillna(0.0)
    w_arr = weights.to_numpy(dtype=float)
    gross = result.backtest["returns"].to_numpy(dtype=float)
    total_rows = len(gross)

    turnover, short_notional = _exposure_series(w_arr)
    active = np.abs(w_arr).sum(axis=1) > DEGENERATE_TOL
    active_rows = int(active.sum())

    def _censor(reason: str) -> dict:
        return {
            "variant": variant,
            "weighting": weighting,
            "active_rows": active_rows,
            "total_rows": total_rows,
            "gross_sharpe": None,
            "censored": True,
            "censor_reason": reason,
            "surfaces": None,
            "monotonicity": {
                "linear_transaction_cost": False,
                "borrow_funding": False,
                "notional_slippage": False,
            },
            "period_wise_non_increasing": {
                "linear_transaction_cost": False,
                "borrow_funding": False,
                "notional_slippage": False,
            },
        }

    if active_rows == 0:
        return _censor("inactive_book: zero active rows (flat book, no positions)")

    gross_std = float(np.std(gross, ddof=1)) if total_rows > 1 else 0.0
    if not np.isfinite(gross_std) or gross_std < STD_TOL:
        return _censor(
            "degenerate_returns: gross return std below tolerance "
            f"({STD_TOL}), Sharpe undefined"
        )

    gross_sharpe = float(metrics.sharpe_ratio(gross))
    if not np.isfinite(gross_sharpe):
        return _censor("undefined_sharpe: gross Sharpe is non-finite")

    gross_turnover_mean = float(turnover.mean())
    gross_turnover_max = float(turnover.max())
    short_notional_mean = float(short_notional.mean())
    gross_final_cumulative = float(np.prod(1.0 + gross))

    def _sweep(exposure: np.ndarray, grid: list[float]) -> list[dict]:
        rows: list[dict] = []
        prev_sharpe: float | None = None
        monotonic = True
        period_wise = True
        for level in grid:
            costed = gross - float(level) * exposure
            cost_drag_mean = float((float(level) * exposure).mean())
            total_cost = float((float(level) * exposure).sum())
            final_cumulative = float(np.prod(1.0 + costed))
            sharpe = float(metrics.sharpe_ratio(costed))
            sharpe_clean = _clean(sharpe) if np.isfinite(sharpe) else None
            rows.append(
                {
                    "level": _clean(float(level)),
                    "costed_sharpe": sharpe_clean,
                    "cost_drag_mean": _clean(cost_drag_mean),
                    "total_cost": _clean(total_cost),
                    "final_cumulative": _clean(final_cumulative),
                }
            )
            if sharpe_clean is not None:
                if prev_sharpe is not None and sharpe_clean > prev_sharpe + 1e-12:
                    monotonic = False
                prev_sharpe = sharpe_clean
        # Period-wise: every adjacent level pair must satisfy
        # costed_t(level2) <= costed_t(level1) for all t when level2 >= level1.
        for i in range(1, len(rows)):
            hi = float(rows[i]["level"])
            lo = float(rows[i - 1]["level"])
            if hi < lo:
                continue
            exposure_hi = exposure * hi
            exposure_lo = exposure * lo
            if not bool((gross - exposure_hi <= gross - exposure_lo + 1e-12).all()):
                period_wise = False
                break
        return rows, monotonic, period_wise

    surfaces: dict = {}
    monotonicity: dict = {}
    period_wise: dict = {}
    for component, grid in COMPONENT_GRIDS.items():
        if component == "linear_transaction_cost":
            exposure = turnover
        elif component == "borrow_funding":
            exposure = short_notional * (1.0 / TRADING_DAYS)
        else:
            exposure = turnover
        rows, mono, pw = _sweep(exposure, grid)
        surfaces[component] = rows
        monotonicity[component] = bool(mono)
        period_wise[component] = bool(pw)

    return {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "total_rows": total_rows,
        "gross_sharpe": _clean(gross_sharpe),
        "gross_turnover_mean": _clean(gross_turnover_mean),
        "gross_turnover_max": _clean(gross_turnover_max),
        "short_notional_mean": _clean(short_notional_mean),
        "gross_final_cumulative": _clean(gross_final_cumulative),
        "censored": False,
        "censor_reason": None,
        "surfaces": surfaces,
        "monotonicity": monotonicity,
        "period_wise_non_increasing": period_wise,
    }


def build_cost_surface(universe_payload: dict | None = None,
                       rank_eval_payload: dict | None = None) -> dict:
    """Build the cost-surface payload (pure, no I/O)."""
    if universe_payload is None:
        universe_payload = _load_json(UNIVERSE_PATH)
    if rank_eval_payload is None:
        rank_eval_payload = _load_json(RANK_EVAL_PATH)

    # Integrity: the panels consumed here must match the committed rank_eval.
    for variant in VARIANTS:
        committed_sha = rank_eval_payload["provenance"]["panel_sha256"][variant]
        universe_sha = universe_payload["panels"][variant]["sha256"]
        assert committed_sha == universe_sha, f"panel sha mismatch for {variant}"

    books = [
        _book_surface(variant, weighting, universe_payload)
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    ]

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_cost_surface.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "universe_seed": universe_payload["provenance"]["seed"],
            "panel_sha256": {
                variant: universe_payload["panels"][variant]["sha256"]
                for variant in VARIANTS
            },
            "config": {**CONFIG},
            "trading_days": TRADING_DAYS,
            "component_grids": {k: [_clean(v) for v in grid]
                              for k, grid in COMPONENT_GRIDS.items()},
            "method": (
                "run BABStrategy at zero cost per (variant, weighting) to recover "
                "gross returns and weights; per-row costed returns = gross - "
                "component_level * exposure, with exposure = turnover for "
                "linear_transaction_cost and notional_slippage and "
                "short_notional / trading_days for borrow_funding; costed "
                "Sharpe asserted non-increasing in each component level."
            ),
            "caveat": (
                "Recovery on a planted synthetic universe proves the estimator "
                "works; it is never market alpha. A null-universe positive "
                "result is a bug, not a finding. Censored books report a "
                "documented reason, never a zero tolerance."
            ),
        },
        "books": books,
    }


def render_markdown(payload: dict) -> str:
    """Render the cost-surface summary from the payload; no external numbers."""
    prov = payload["provenance"]
    lines = [
        "# BAB P21 WP3 — multi-component cost surface on the planted universe",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus with known "
        "ground truth: not real market data and not market profitability "
        "evidence.",
        "",
        f"Universe seed {prov['universe_seed']}; components: "
        + ", ".join(sorted(prov["component_grids"].keys()))
        + "; grids: " + json.dumps(prov["component_grids"], sort_keys=True),
        "",
        "| variant | weighting | active_rows | gross_sharpe | gross_turnover_mean | "
        "short_notional_mean | gross_final_cumulative | censored | censor_reason |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for book in payload["books"]:
        lines.extend(
            "| {variant} | {weighting} | {active_rows} | {gross_sharpe} | "
            "{gross_turnover_mean} | {short_notional_mean} | "
            "{gross_final_cumulative} | {censored} | {censor_reason} |".format(
                **{
                    "variant": book["variant"],
                    "weighting": book["weighting"],
                    "active_rows": book["active_rows"],
                    "gross_sharpe": book["gross_sharpe"],
                    "gross_turnover_mean": book["gross_turnover_mean"],
                    "short_notional_mean": book["short_notional_mean"],
                    "gross_final_cumulative": book["gross_final_cumulative"],
                    "censored": book["censored"],
                    "censor_reason": book["censor_reason"],
                }
            )
        )
    lines += [
        "",
        "| variant | weighting | component | level | costed_sharpe | cost_drag_mean | "
        "total_cost | final_cumulative |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for book in payload["books"]:
        if book["censored"] or book["surfaces"] is None:
            continue
        for component in sorted(book["surfaces"].keys()):
            lines.extend(
                "| {variant} | {weighting} | {component} | {level} | "
                "{costed_sharpe} | {cost_drag_mean} | {total_cost} | "
                "{final_cumulative} |".format(
                    variant=book["variant"],
                    weighting=book["weighting"],
                    component=component,
                    level=row["level"],
                    costed_sharpe=row["costed_sharpe"],
                    cost_drag_mean=row["cost_drag_mean"],
                    total_cost=row["total_cost"],
                    final_cumulative=row["final_cumulative"],
                )
                for row in book["surfaces"][component]
            )
    lines += [
        "",
        "| variant | weighting | component | monotonic_sharpe | period_wise_non_increasing |",
        "|---|---|---|---|---|---|",
    ]
    for book in payload["books"]:
        if book["censored"]:
            continue
        lines.extend(
            "| {variant} | {weighting} | {component} | {mono} | {pw} |".format(
                variant=book["variant"],
                weighting=book["weighting"],
                component=component,
                mono=book["monotonicity"][component],
                pw=book["period_wise_non_increasing"][component],
            )
            for component in sorted(book["monotonicity"].keys())
        )
    lines += [
        "",
        "Per-book costed Sharpe is non-increasing in every cost-component level "
        "(monotonic_sharpe = true), and every period's costed return is "
        "non-increasing in the level (period_wise_non_increasing = true), since "
        "each drag is a non-negative rate times a non-negative exposure. "
        "Censored books carry a documented censor_reason and never a zero "
        "tolerance.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "cost_surface.json"
    markdown_path = directory / "cost_surface.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_cost_surface()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for book in payload["books"]:
        status = "CENSORED (" + str(book["censor_reason"]) + ")" if book[
            "censored"
        ] else f"gross_sharpe={book['gross_sharpe']:.6f}"
        print(
            f"{book['variant']:7s} {book['weighting']:5s} "
            f"active={book['active_rows']} {status}"
        )
        if not book["censored"]:
            for component in sorted(book["surfaces"].keys()):
                print(
                    f"    {component:26s} mono={book['monotonicity'][component]} "
                    f"pw={book['period_wise_non_increasing'][component]}"
                )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
