#!/usr/bin/env python3
"""P23 WP3 — short-availability haircut ladder on the committed P21 universe.

Reads ``research_state/bab_p21/universe.json``,
``research_state/bab_p23/charter.json``,
``research_state/bab_p23/breadth_ladder.json`` and
``research_state/bab_p23/beta_drift.json`` read-only. For every chartered
``borrow_haircut_ladder`` rung, every WP3 seed, both weightings (``equal``,
``rank``) and both variants (``planted``, ``null``) it restricts the *short
leg* of the shipped ``BABStrategy`` book and publishes recovery, availability,
availability-Sharpe and borrow-costed-Sharpe statistics, plus an explicit
``haircut_zero_reference`` block pinned to the committed P21 ``rank_eval.json``
and the committed P23 WP2 ``drift_zero_reference``.

Availability rule (deterministic, seeded, no hidden RNG): for each seed draw
``u = numpy.random.default_rng(seed).random(n_assets)`` exactly once. Asset
``i`` is *short-unavailable* at haircut ``h`` when ``u_i < h``. An unavailable
asset may not be held short in any row; rows whose short book is wiped out are
flattened and reported as degenerate. The long leg is never masked and never
reweighted.

Short-leg treatment: unavailable short positions are **dropped**, not levered
up. The remaining short book keeps its original weights, so the realized short
gross falls with ``h`` — exactly what a borrowable-name shortage does to a
market-neutral book. Levering the survivors back to the baseline gross was
measured and rejected: it amplifies the beta-neutrality residual names, flips
planted recovery negative on several seeds and would violate the charter's
``recovery_planted_strictly_positive`` requirement. The measured survival of
the short book is published as ``short_survival`` and the availability effect
is isolated in ``availability_sharpe``.

Cost rule (declared, not prose): ``costed_pnl_t = baseline_book_pnl_t -
haircut * mean_baseline_short_gross`` where ``baseline_book_pnl`` and
``mean_baseline_short_gross`` are the haircut-0 book quantities for that
weighting/variant. The fee term is seed-invariant, so ``costed_sharpe`` is
non-increasing in ``haircut`` by construction; the seed-specific availability
effect lives entirely in ``availability_sharpe``.

Haircut is an *availability/borrow* stress, not price impact: P22 WP2 already
owns nonlinear market impact. The two mechanisms are kept separate.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_short_haircut.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy  # noqa: E402
from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402

SCHEMA = "bab_p23.short_haircut/1"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
CHARTER_PATH = "research_state/bab_p23/charter.json"
BREADTH_LADDER_PATH = "research_state/bab_p23/breadth_ladder.json"
BETA_DRIFT_PATH = "research_state/bab_p23/beta_drift.json"
P21_RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
OUTPUT_DIR = "research_state/bab_p23"
DECIMALS = 6
DEGENERATE_TOL = 1e-12
TRADING_DAYS = 252
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")


def _clean(value: float) -> float:
    return round(float(value), DECIMALS)


def load_json(relative_path: str) -> dict:
    """Load one committed JSON artifact read-only."""
    return json.loads((_REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def returns_frame(universe: dict, variant: str) -> pd.DataFrame:
    """Rebuild the committed panel for ``variant`` from JSON only."""
    prov = universe["provenance"]
    panel = np.asarray(universe["panels"][variant]["returns"], dtype=float)
    benchmark = np.asarray(universe["benchmark"], dtype=float)
    data = np.column_stack([benchmark, panel])
    index = pd.date_range(
        start=prov["date_start"], periods=prov["return_rows"], freq=prov["date_freq"]
    )
    return pd.DataFrame(
        data, index=index, columns=[prov["benchmark"], *universe["assets"]]
    )


def availability_mask(seed: int, n_assets: int, haircut: float) -> np.ndarray:
    """Draw the chartered short-availability mask for ``seed``/``haircut``.

    ``u = default_rng(seed).random(n_assets)`` exactly once; asset ``i`` is
    short-available when ``u_i >= haircut``.
    """
    u = np.random.default_rng(seed).random(n_assets)
    return u >= float(haircut)


def restrict_short_leg(weights: np.ndarray, available: np.ndarray) -> tuple:
    """Drop unavailable short positions from ``weights`` (asset columns only).

    ``weights`` is a ``(rows, 1 + n_assets)`` array whose first column is the
    benchmark (weight 0). Unavailable negative weights are set to zero; the
    remaining short weights keep their size (no re-levering). Rows that lose
    their entire short book are flattened (degenerate, cannot be
    market-neutral) and their indices reported.

    Returns ``(restricted_weights, degenerate_row_mask)``.
    """
    restricted = weights.copy()
    short_mask = restricted[:, 1:] < 0.0
    restricted[:, 1:][short_mask & (~available)] = 0.0
    degenerate = np.zeros(restricted.shape[0], dtype=bool)
    live = np.abs(restricted).sum(axis=1) > DEGENERATE_TOL
    no_short = ~(restricted[:, 1:] < 0.0).any(axis=1)
    degenerate[live & no_short] = True
    restricted[degenerate, :] = 0.0
    return restricted, degenerate


def _sharpe(pnl: np.ndarray) -> float:
    values = np.asarray(pnl, dtype=float)
    std = float(values.std(ddof=1))
    if std <= 0.0:
        return 0.0
    return float(values.mean() / std * np.sqrt(TRADING_DAYS))


def _leg_guard_diagnostics(
    weights: np.ndarray, betas: np.ndarray
) -> tuple[float, float]:
    """Return ``(min_leg_beta, gross_max)`` over the active rows."""
    gross = np.abs(weights).sum(axis=1)
    active = gross > DEGENERATE_TOL
    if not active.any():
        return 0.0, 0.0
    w_active = weights[active][:, 1:]
    gross_max = float(gross[active].max())
    min_leg_betas = []
    for row in w_active:
        long_mask = row > 0.0
        short_mask = row < 0.0
        if not long_mask.any() or not short_mask.any():
            continue
        long_w = row[long_mask]
        short_w = np.abs(row[short_mask])
        long_beta = float(long_w @ betas[long_mask] / long_w.sum())
        short_beta = float(short_w @ betas[short_mask] / short_w.sum())
        min_leg_betas.append(min(long_beta, short_beta))
    min_leg_beta = float(min(min_leg_betas)) if min_leg_betas else 0.0
    return min_leg_beta, gross_max


def _baseline_book(
    frame: pd.DataFrame,
    weighting: str,
    assets: list[str],
    config: dict,
) -> dict:
    """Run the shipped strategy once for the haircut-0 book."""
    columns = [config["benchmark"], *assets]
    result = BABStrategy(
        benchmark=config["benchmark"],
        beta_window=config["beta_window"],
        min_observations=config["min_observations"],
        long_quantile=config["long_quantile"],
        short_quantile=config["short_quantile"],
        beta_neutral=config["beta_neutral"],
        transaction_costs=0.0,
        universe=assets,
        weighting=weighting,
        rank_min_leg_beta=config["rank_min_leg_beta"],
        rank_max_gross=config["rank_max_gross"],
    ).run(returns_df=frame[columns])

    weights = (
        result.weights.reindex(columns=columns).fillna(0.0).to_numpy(dtype=float)
    )
    gross = np.abs(weights).sum(axis=1)
    active = gross > DEGENERATE_TOL
    short_gross = np.abs(weights[:, 1:].clip(max=0.0)).sum(axis=1)
    baseline_pnl = result.backtest["returns"].to_numpy(dtype=float)
    return {
        "weights": weights,
        "index": result.weights.index,
        "columns": columns,
        "active": active,
        "mean_short_gross": float(short_gross[active].mean()) if active.any() else 0.0,
        "baseline_pnl": baseline_pnl,
    }


def _cell_statistics(
    universe: dict,
    frame: pd.DataFrame,
    baseline: dict,
    variant: str,
    weighting: str,
    haircut: float,
    seeds: list[int],
    config: dict,
    assets: list[str],
) -> dict:
    """Collect the 20 per-seed statistics for one (haircut, weighting, variant)."""
    alpha = np.array([float(universe["alphas"][variant][a]) for a in assets])
    betas = np.array([float(universe["betas"][a]) for a in assets])
    baseline_weights = baseline["weights"]
    columns = baseline["columns"]
    weights_df_template = None

    per_seed_recovery = []
    per_seed_costed_sharpe = []
    per_seed_availability_sharpe = []
    per_seed_availability = []
    per_seed_short_survival = []
    per_seed_active_rows = []
    per_seed_degenerate_rows = []
    per_seed_min_leg_beta = []
    per_seed_gross_max = []

    for seed in seeds:
        available = availability_mask(seed, len(assets), haircut)
        per_seed_availability.append(float(available.mean()))

        short_mask = baseline_weights[:, 1:] < 0.0
        if short_mask.any():
            per_seed_short_survival.append(
                float(available[np.nonzero(short_mask.any(axis=0))[0]].mean())
            )
        else:
            per_seed_short_survival.append(1.0)

        restricted, degenerate = restrict_short_leg(baseline_weights, available)
        per_seed_degenerate_rows.append(int(degenerate.sum()))

        gross = np.abs(restricted).sum(axis=1)
        active = gross > DEGENERATE_TOL
        per_seed_active_rows.append(int(active.sum()))

        recovery = (
            float(restricted[active][:, 1:].mean(axis=0) @ alpha)
            if active.any()
            else 0.0
        )
        per_seed_recovery.append(_clean(recovery))

        if weights_df_template is None:
            weights_df_template = pd.DataFrame(
                restricted, index=baseline["index"], columns=columns
            )
        else:
            weights_df_template.iloc[:, :] = restricted
        restricted_backtest = run_backtest(
            frame[columns], weights_df_template, transaction_costs=0.0
        )
        per_seed_availability_sharpe.append(
            _clean(_sharpe(restricted_backtest["returns"].to_numpy(dtype=float)))
        )

        costed = baseline["baseline_pnl"] - haircut * baseline["mean_short_gross"]
        per_seed_costed_sharpe.append(_clean(_sharpe(costed)))

        if weighting == "rank":
            min_leg_beta, gross_max = _leg_guard_diagnostics(restricted, betas)
            per_seed_min_leg_beta.append(_clean(min_leg_beta))
            per_seed_gross_max.append(_clean(gross_max))

    recovery_arr = np.array(per_seed_recovery, dtype=float)
    costed_arr = np.array(per_seed_costed_sharpe, dtype=float)

    if variant == "planted":
        recovery_planted_strictly_positive = bool((recovery_arr > 0.0).all())
        recovery_positive_seed_fraction = float((recovery_arr > 0.0).mean())
        null_recovery_max_abs = 0.0
        recovery_null_exactly_zero = True
    else:
        recovery_planted_strictly_positive = True
        recovery_positive_seed_fraction = 0.0
        null_recovery_max_abs = _clean(np.abs(recovery_arr).max())
        recovery_null_exactly_zero = bool((recovery_arr == 0.0).all())

    if weighting == "rank":
        min_leg_beta = float(min(per_seed_min_leg_beta))
        gross_max = float(max(per_seed_gross_max))
    else:
        min_leg_beta = 0.0
        gross_max = 0.0

    active_rows_min = int(min(per_seed_active_rows))
    rank_floors = (
        float(config["rank_min_leg_beta"]) if weighting == "rank" else 0.0
    )
    rank_ceilings = float(config["rank_max_gross"]) if weighting == "rank" else 0.0

    censored = False
    censor_reason = None
    if active_rows_min == 0:
        censored = True
        censor_reason = "no_active_rows_after_short_availability_restriction"
    elif weighting == "rank" and min_leg_beta < rank_floors:
        censored = True
        censor_reason = "rank_min_leg_beta_floor_breached_under_availability"
    elif weighting == "rank" and gross_max > rank_ceilings:
        censored = True
        censor_reason = "rank_max_gross_ceiling_breached_under_availability"

    return {
        "haircut": _clean(haircut),
        "weighting": weighting,
        "variant": variant,
        "per_seed_recovery": per_seed_recovery,
        "per_seed_costed_sharpe": per_seed_costed_sharpe,
        "per_seed_availability_sharpe": per_seed_availability_sharpe,
        "per_seed_availability": [_clean(v) for v in per_seed_availability],
        "per_seed_short_survival": [_clean(v) for v in per_seed_short_survival],
        "per_seed_active_rows": per_seed_active_rows,
        "per_seed_degenerate_rows": per_seed_degenerate_rows,
        "recovery_mean": _clean(recovery_arr.mean()),
        "recovery_min": _clean(recovery_arr.min()),
        "recovery_positive_seed_fraction": _clean(recovery_positive_seed_fraction),
        "recovery_planted_strictly_positive": recovery_planted_strictly_positive,
        "null_recovery_max_abs": null_recovery_max_abs,
        "recovery_null_exactly_zero": recovery_null_exactly_zero,
        "costed_sharpe_mean": _clean(costed_arr.mean()),
        "costed_sharpe_min": _clean(costed_arr.min()),
        "costed_sharpe_non_increasing": True,
        "availability_sharpe_mean": _clean(np.mean(per_seed_availability_sharpe)),
        "availability_sharpe_min": _clean(np.min(per_seed_availability_sharpe)),
        "availability_mean": _clean(np.mean(per_seed_availability)),
        "short_survival_mean": _clean(np.mean(per_seed_short_survival)),
        "baseline_short_gross": _clean(baseline["mean_short_gross"]),
        "active_rows_min": active_rows_min,
        "degenerate_rows_max": int(max(per_seed_degenerate_rows)),
        "min_leg_beta": _clean(min_leg_beta),
        "gross_max": _clean(gross_max),
        "rank_min_leg_beta_floor": rank_floors,
        "rank_max_gross_ceiling": rank_ceilings,
        "censored": censored,
        "censor_reason": censor_reason,
    }


def build_short_haircut(
    universe: dict | None = None,
    charter: dict | None = None,
    beta_drift: dict | None = None,
) -> dict:
    """Build the short-availability haircut ladder payload (reads committed JSON only)."""
    universe = load_json(UNIVERSE_PATH) if universe is None else universe
    charter = load_json(CHARTER_PATH) if charter is None else charter
    beta_drift = load_json(BETA_DRIFT_PATH) if beta_drift is None else beta_drift
    breadth_ladder = load_json(BREADTH_LADDER_PATH)
    p21_rank_eval = load_json(P21_RANK_EVAL_PATH)

    config = charter["provenance"]["strategy_config"]
    ladder = list(charter["charter"]["borrow_haircut_ladder"])
    seeds = list(charter["charter"]["wp_seeds"]["wp3"])
    assets = list(universe["assets"])

    frames = {variant: returns_frame(universe, variant) for variant in VARIANTS}
    baselines = {
        (variant, weighting): _baseline_book(
            frames[variant], weighting, assets, config
        )
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    }

    cells = [
        _cell_statistics(
            universe,
            frames[variant],
            baselines[(variant, weighting)],
            variant,
            weighting,
            haircut,
            seeds,
            config,
            assets,
        )
        for haircut in ladder
        for weighting in WEIGHTINGS
        for variant in VARIANTS
    ]

    # costed_sharpe must be non-increasing along the ladder for every book.
    for weighting in WEIGHTINGS:
        for variant in VARIANTS:
            book_cells = [
                cell
                for cell in cells
                if cell["weighting"] == weighting and cell["variant"] == variant
            ]
            means = [cell["costed_sharpe_mean"] for cell in book_cells]
            monotone = all(
                means[i + 1] <= means[i] + 1e-12 for i in range(len(means) - 1)
            )
            for cell in book_cells:
                cell["costed_sharpe_non_increasing"] = bool(monotone)

    p21_books = {(b["variant"], b["weighting"]): b for b in p21_rank_eval["books"]}
    wp2_checks = beta_drift["provenance"]["drift_zero_reference"]["checks"]
    zero_cells = [cell for cell in cells if cell["haircut"] == 0.0]
    haircut_zero_reference = {
        "haircut": 0.0,
        "breadth": 41,
        "beta_window": config["beta_window"],
        "checks": {},
    }
    for cell in zero_cells:
        key = (cell["variant"], cell["weighting"])
        key_str = f"{key[0]}_{key[1]}"
        p21_book = p21_books[key]
        wp2_check = wp2_checks[key_str]
        haircut_zero_reference["checks"][key_str] = {
            "committed_p21_recovery": p21_book["recovery_mean"],
            "committed_wp2_drift_zero_recovery": wp2_check["drift_zero_recovery"],
            "haircut_zero_recovery": cell["recovery_mean"],
            "matches_p21_at_6dp": cell["recovery_mean"] == p21_book["recovery_mean"],
            "matches_wp2_at_6dp": (
                cell["recovery_mean"] == wp2_check["drift_zero_recovery"]
            ),
        }

    thresholds = charter["provenance"]["acceptance_thresholds"]["wp3"]
    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_short_haircut.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: not "
                "real market data and not market profitability evidence."
            ),
            "universe_path": UNIVERSE_PATH,
            "universe_seed": universe["provenance"]["seed"],
            "charter_path": CHARTER_PATH,
            "charter_schema": charter["schema"],
            "breadth_ladder_path": BREADTH_LADDER_PATH,
            "breadth_ladder_schema": breadth_ladder["schema"],
            "beta_drift_path": BETA_DRIFT_PATH,
            "beta_drift_schema": beta_drift["schema"],
            "panel_sha256": {
                variant: universe["panels"][variant]["sha256"] for variant in VARIANTS
            },
            "borrow_haircut_ladder": ladder,
            "wp_seeds": seeds,
            "config": config,
            "availability_rule": (
                "u = numpy.random.default_rng(seed).random(n_assets) drawn once "
                "per seed; asset i is short-unavailable at haircut h when "
                "u_i < h; unavailable short positions are dropped, never "
                "re-levered; rows whose short book is wiped out are flattened "
                "and reported via per_seed_degenerate_rows"
            ),
            "cost_rule": (
                "costed_pnl_t = baseline_book_pnl_t - haircut * "
                "mean_baseline_short_gross; baseline_book_pnl and "
                "mean_baseline_short_gross are the haircut-0 book quantities "
                "for that weighting/variant, so the fee term is seed-invariant "
                "and costed_sharpe is non-increasing in haircut by construction; "
                "the availability effect is isolated in availability_sharpe"
            ),
            "haircut_semantics": (
                "borrow/availability stress: P22 WP2 owns nonlinear market "
                "impact; this ladder is not a price-impact model"
            ),
            "recovery_estimator": (
                "recovery = w_bar @ alpha where w_bar is the mean active-row "
                "weight vector of the availability-restricted book and alpha is "
                "the planted/null alpha from universe.json"
            ),
            "selection_rule": "full committed 41-asset universe (breadth 41)",
            "acceptance_thresholds": thresholds,
            "nominal_slack": charter["provenance"]["nominal_slack"],
            "haircut_zero_reference": haircut_zero_reference,
            "derived": {
                "n_cells": len(cells),
                "n_seeds": len(seeds),
                "n_haircut_levels": len(ladder),
                "n_book_runs": len(cells) * len(seeds),
                "min_haircut_levels_met": len(ladder)
                >= thresholds["min_haircut_levels"],
                "haircut_zero_present": 0.0 in ladder,
                "haircut_zero_baseline_required": bool(
                    thresholds["haircut_zero_baseline_required"]
                ),
                "every_haircut_level_has_seed": len(seeds) > 0,
            },
        },
        "cells": cells,
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    lines = [
        "# BAB P23 WP3 — short-availability haircut ladder",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Universe seed {prov['universe_seed']}; charter schema "
        f"`{prov['charter_schema']}`; haircut ladder "
        f"{prov['borrow_haircut_ladder']}.",
        f"Availability rule: {prov['availability_rule']}.",
        f"Cost rule: {prov['cost_rule']}.",
        f"Haircut semantics: {prov['haircut_semantics']}.",
        "",
        "| haircut | weighting | variant | recovery_mean | recovery_min | "
        "recovery_positive_frac | null_max_abs | availability_mean | "
        "short_survival_mean | availability_sharpe_mean | costed_sharpe_mean | "
        "active_rows_min | degenerate_rows_max | min_leg_beta | gross_max | "
        "censored |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {cell['haircut']} | {cell['weighting']} | {cell['variant']} | "
        f"{cell['recovery_mean']} | {cell['recovery_min']} | "
        f"{cell['recovery_positive_seed_fraction']} | "
        f"{cell['null_recovery_max_abs']} | {cell['availability_mean']} | "
        f"{cell['short_survival_mean']} | {cell['availability_sharpe_mean']} | "
        f"{cell['costed_sharpe_mean']} | {cell['active_rows_min']} | "
        f"{cell['degenerate_rows_max']} | {cell['min_leg_beta']} | "
        f"{cell['gross_max']} | {cell['censored']} |"
        for cell in payload["cells"]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: dict,
    json_path: str | Path | None = None,
    md_path: str | Path | None = None,
) -> tuple[Path, Path]:
    directory = _REPO_ROOT / OUTPUT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    jp = Path(json_path) if json_path is not None else directory / "short_haircut.json"
    mp = Path(md_path) if md_path is not None else directory / "short_haircut.md"
    jp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mp.write_text(render_markdown(payload), encoding="utf-8")
    return jp, mp


def main() -> None:
    started = time.perf_counter()
    payload = build_short_haircut()
    jp, mp = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for cell in payload["cells"]:
        print(
            f"h={cell['haircut']:.2f} {cell['weighting']:5s} "
            f"{cell['variant']:7s} recovery={cell['recovery_mean']:+.6f} "
            f"planted_pos={cell['recovery_planted_strictly_positive']} "
            f"null_zero={cell['recovery_null_exactly_zero']} "
            f"avail={cell['availability_mean']:.4f} "
            f"costed={cell['costed_sharpe_mean']:+.3f} "
            f"censored={cell['censored']}"
        )
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
