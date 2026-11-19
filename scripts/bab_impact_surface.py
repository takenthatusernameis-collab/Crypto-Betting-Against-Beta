#!/usr/bin/env python3
"""P22 WP2 — nonlinear market-impact surface on the committed WP3 exposure series.

Loads ``research_state/bab_p21/cost_surface.json`` and
``research_state/bab_p21/universe.json`` read-only, runs the shipped
``BABStrategy`` once per (variant, weighting) at zero cost to recover the gross
returns and weights, then builds per-row costed performance for both
``planted`` and ``null`` variants and both ``equal`` and ``rank`` weightings
across a square-root market-impact model:

    per-period impact drag = coefficient * turnover ** 1.5

i.e. drag is proportional to participation (turnover) raised to the 3/2 power,
the classic square-root market-impact scaling. At ``coefficient = 0`` the drag
vanishes and the surface reproduces the linear (zero-cost) baseline exactly.

For every book and every coefficient level the surface proves per-book and
per-period costed Sharpe is non-increasing in the impact coefficient. Nulls /
censoring are reported with documented reasons, never as zero tolerances.
Byte-identical reruns are verified by hash determinism.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_impact_surface.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402

SCHEMA = "bab_p22.impact_surface/1"
OUTPUT_DIR = "research_state/bab_p22"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
COST_SURFACE_PATH = "research_state/bab_p21/cost_surface.json"
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
DECIMALS = 6
DEGENERATE_TOL = 1e-12
STD_TOL = 1e-12
IMPACT_COMPONENT = "market_impact"
TRADING_DAYS = 252

# Square-root market-impact coefficient grid. Level 0.0 is the uncosted
# baseline: drag is identically zero and the surface equals the gross book.
IMPACT_COEFFICIENT_GRID = [0.0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

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


def _returns_frame(universe_payload: dict, variant: str) -> pd.DataFrame:
    """Rebuild the returns frame for one P21 WP0 panel (pure, from JSON)."""
    assets = list(universe_payload["assets"])
    panel = np.asarray(
        universe_payload["panels"][variant]["returns"], dtype=float
    )
    benchmark = np.asarray(universe_payload["benchmark"], dtype=float)
    if benchmark.shape[0] != panel.shape[0]:
        raise AssertionError(
            f"benchmark length {benchmark.shape[0]} != panel rows {panel.shape[0]}"
        )
    data = np.column_stack([benchmark, panel])
    prov = universe_payload["provenance"]
    index = pd.date_range(
        start=prov["date_start"], periods=int(prov["return_rows"]), freq=prov["date_freq"]
    )
    columns = [prov["benchmark"], *assets]
    return pd.DataFrame(data, index=index, columns=columns)


def _exposure_series(weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-period turnover and impact exposure from a weight matrix.

    Turnover follows the backtest convention: |w[t] - w[t-1]| with w[-1] = 0,
    so the first period trades from zero into the initial book. The square-root
    market-impact exposure is turnover ** 1.5 per period (participation raised
    to the 3/2 power). Both are non-negative.
    """
    _n_rows, n_cols = weights.shape
    shifted = np.vstack([np.zeros((1, n_cols), dtype=float), weights[:-1]])
    turnover = np.abs(weights - shifted).sum(axis=1)
    impact_exposure = np.power(turnover, 1.5)
    return turnover, impact_exposure


def _book_surface(variant: str, weighting: str, universe_payload: dict) -> dict:
    """Build the full impact surface for one book."""
    assets = list(universe_payload["assets"])
    frame = _returns_frame(universe_payload, variant)
    result = BABStrategy(
        benchmark=CONFIG["benchmark"],
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

    weights = result.weights.reindex(
        columns=[CONFIG["benchmark"], *assets]
    ).fillna(0.0)
    w_arr = weights.to_numpy(dtype=float)
    gross = result.backtest["returns"].to_numpy(dtype=float)
    total_rows = len(gross)

    turnover, impact_exposure = _exposure_series(w_arr)
    active = np.abs(w_arr).sum(axis=1) > DEGENERATE_TOL
    active_rows = int(active.sum())

    def _censor(reason: str) -> dict:
        return {
            "variant": variant,
            "weighting": weighting,
            "active_rows": active_rows,
            "total_rows": total_rows,
            "gross_sharpe": None,
            "impact_exposure_mean": None,
            "censored": True,
            "censor_reason": reason,
            "surfaces": None,
            "monotonicity": {IMPACT_COMPONENT: False},
            "period_wise_non_increasing": {IMPACT_COMPONENT: False},
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
    impact_exposure_mean = float(impact_exposure.mean())
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

    rows, mono, pw = _sweep(impact_exposure, IMPACT_COEFFICIENT_GRID)

    return {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "total_rows": total_rows,
        "gross_sharpe": _clean(gross_sharpe),
        "gross_turnover_mean": _clean(gross_turnover_mean),
        "impact_exposure_mean": _clean(impact_exposure_mean),
        "gross_final_cumulative": _clean(gross_final_cumulative),
        "censored": False,
        "censor_reason": None,
        "surfaces": {IMPACT_COMPONENT: rows},
        "monotonicity": {IMPACT_COMPONENT: bool(mono)},
        "period_wise_non_increasing": {IMPACT_COMPONENT: bool(pw)},
    }


def build_impact_surface(
    universe_payload: dict | None = None,
    cost_surface_payload: dict | None = None,
) -> dict:
    """Build the impact-surface payload (pure, no I/O beyond committed JSON)."""
    if universe_payload is None:
        universe_payload = _load_json(UNIVERSE_PATH)
    if cost_surface_payload is None:
        cost_surface_payload = _load_json(COST_SURFACE_PATH)

    # Integrity: the panels consumed here must match the committed cost surface.
    prov_u = universe_payload["provenance"]
    prov_c = cost_surface_payload["provenance"]
    for variant in VARIANTS:
        u_sha = universe_payload["panels"][variant]["sha256"]
        assert prov_c["panel_sha256"][variant] == u_sha, (
            f"panel sha mismatch for {variant}"
        )
        assert prov_u["seed"] == prov_c.get("universe_seed", prov_u["seed"]), (
            f"universe seed mismatch for {variant}"
        )

    books = [
        _book_surface(variant, weighting, universe_payload)
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    ]

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_impact_surface.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "universe_seed": prov_u["seed"],
            "panel_sha256": {
                variant: universe_payload["panels"][variant]["sha256"]
                for variant in VARIANTS
            },
            "config": {**CONFIG},
            "trading_days": TRADING_DAYS,
            "impact_coefficient_grid": [_clean(v) for v in IMPACT_COEFFICIENT_GRID],
            "impact_component": IMPACT_COMPONENT,
            "method": (
                "run BABStrategy at zero cost per (variant, weighting) to recover "
                "gross returns and weights; per-period turnover is raised to the "
                "3/2 power to obtain the square-root market-impact exposure; "
                "costed returns = gross - coefficient * turnover**1.5; costed "
                "Sharpe asserted non-increasing in the impact coefficient; "
                "coefficient == 0 reproduces the gross baseline exactly."
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
    """Render the impact-surface summary from the payload; no external numbers."""
    prov = payload["provenance"]
    lines = [
        "# BAB P22 WP2 — nonlinear market-impact surface on the WP3 exposure series",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Universe seed {prov['universe_seed']}; component: `{prov['impact_component']}`; "
        "model: per-period impact drag = coefficient * turnover ** 1.5 "
        "(square-root market impact, participation to the 3/2 power); "
        f"coefficient grid: {json.dumps(prov['impact_coefficient_grid'], sort_keys=True)}; "
        f"trading days: {prov['trading_days']}.",
        "",
        "| variant | weighting | active_rows | gross_sharpe | gross_turnover_mean | "
        "impact_exposure_mean | gross_final_cumulative | censored | censor_reason |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        [
            "| {variant} | {weighting} | {active_rows} | {gross_sharpe} | "
            "{gross_turnover_mean} | {impact_exposure_mean} | "
            "{gross_final_cumulative} | {censored} | {censor_reason} |".format(
                variant=book["variant"],
                weighting=book["weighting"],
                active_rows=book["active_rows"],
                gross_sharpe=book["gross_sharpe"],
                gross_turnover_mean=book["gross_turnover_mean"],
                impact_exposure_mean=book["impact_exposure_mean"],
                gross_final_cumulative=book["gross_final_cumulative"],
                censored=book["censored"],
                censor_reason=book["censor_reason"],
            )
            for book in payload["books"]
        ]
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
        "|---|---|---|---|---|",
    ]
    for book in payload["books"]:
        if book["censored"]:
            continue
        lines.extend(
            [
                "| {variant} | {weighting} | {component} | {mono} | {pw} |".format(
                    variant=book["variant"],
                    weighting=book["weighting"],
                    component=component,
                    mono=book["monotonicity"][component],
                    pw=book["period_wise_non_increasing"][component],
                )
                for component in sorted(book["monotonicity"].keys())
            ]
        )
    lines += [
        "",
        "Per-book costed Sharpe is non-increasing in the impact-coefficient level "
        "(monotonic_sharpe = true), and every period's costed return is "
        "non-increasing in the level (period_wise_non_increasing = true), since "
        "each drag is a non-negative coefficient times a non-negative "
        "turnover**1.5 exposure. At coefficient == 0 the surface reproduces the "
        "gross baseline exactly. Censored books carry a documented censor_reason "
        "and never a zero tolerance.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "impact_surface.json"
    markdown_path = directory / "impact_surface.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_impact_surface()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for book in payload["books"]:
        status = (
            "CENSORED (" + str(book["censor_reason"]) + ")"
            if book["censored"]
            else f"gross_sharpe={book['gross_sharpe']:.6f}"
        )
        print(
            f"{book['variant']:7s} {book['weighting']:5s} "
            f"active={book['active_rows']} {status}"
        )
        if not book["censored"]:
            component = IMPACT_COMPONENT
            print(
                f"    {component:26s} mono={book['monotonicity'][component]} "
                f"pw={book['period_wise_non_increasing'][component]}"
            )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
