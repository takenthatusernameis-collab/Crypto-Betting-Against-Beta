#!/usr/bin/env python3
"""P23 WP2 — beta-window/drift grid on the committed P21 universe.

Reads ``research_state/bab_p21/universe.json``,
``research_state/bab_p23/charter.json`` and
``research_state/bab_p23/breadth_ladder.json`` read-only. For every chartered
``(beta_window, drift_threshold)`` cell it builds 20 seeded drift-stressed
panel pairs from committed data only, runs the shipped ``BABStrategy`` for both
weightings (``equal``, ``rank``) and both variants (``planted``, ``null``), and
publishes aggregated recovery statistics, rank-guard diagnostics, per-seed
recovery lists and an explicit ``drift_zero_reference`` block pinned to the
committed P21 ``rank_eval.json``.

The drift model: ``beta_true_{i,t} = beta_i * (1 + DRIFT_SCALE * delta * t * u_i)``
where ``u_i`` is a per-asset drift direction from
``numpy.random.default_rng(seed)`` and ``t`` is the row index. Drift is a
*per-row relative* beta drift accumulated across the sample, so the chartered
``delta`` grid stresses the estimator instead of being lost in the beta level.
``DRIFT_SCALE = 0.1`` calibrates the chartered grid to a survivable but
degrading stress: relative beta displacement reaches ``+/-6%`` at
``delta = 1e-3``, which measurably lowers planted recovery while keeping it
strictly positive on every seed. The stressed returns are
``R'_{i,t} = R_{i,t} + DRIFT_SCALE * delta * t * u_i * beta_i * B_t``, reusing
the committed benchmark and residuals row-for-row.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_beta_drift.py
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

SCHEMA = "bab_p23.beta_drift/1"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
CHARTER_PATH = "research_state/bab_p23/charter.json"
BREADTH_LADDER_PATH = "research_state/bab_p23/breadth_ladder.json"
P21_RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
OUTPUT_DIR = "research_state/bab_p23"
DECIMALS = 6
DEGENERATE_TOL = 1e-12
DRIFT_SCALE = 0.1
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
        start=prov["date_start"],
        periods=prov["return_rows"],
        freq=prov["date_freq"],
    )
    return pd.DataFrame(
        data, index=index, columns=[prov["benchmark"], *universe["assets"]]
    )


def build_drift_stressed_panel(
    universe: dict, variant: str, seed: int, drift_threshold: float
) -> pd.DataFrame:
    """Build a drift-stressed panel from committed data only.

    ``beta_true_{i,t} = beta_i * (1 + DRIFT_SCALE * delta * t * u_i)`` with
    ``u_i ~ default_rng(seed).uniform(-1, 1)`` and ``t`` the row index;
    stressed returns are
    ``R'_{i,t} = R_{i,t} + DRIFT_SCALE * delta * t * u_i * beta_i * B_t``.
    """
    prov = universe["provenance"]
    n_assets = len(universe["assets"])
    rows = prov["return_rows"]

    benchmark = np.asarray(universe["benchmark"], dtype=float)
    panel = np.asarray(universe["panels"][variant]["returns"], dtype=float)
    betas = np.array([float(universe["betas"][a]) for a in universe["assets"]])

    rng = np.random.default_rng(seed)
    u = rng.uniform(-1.0, 1.0, n_assets)

    t_index = np.arange(rows, dtype=float)
    drift = DRIFT_SCALE * drift_threshold * np.outer(t_index, u * betas) * benchmark[:, None]

    stressed = panel + drift
    benchmark_col = benchmark[:, None]
    data = np.column_stack([benchmark_col, stressed])
    data_rounded = [[_clean(v) for v in row] for row in data.tolist()]

    index = pd.date_range(
        start=prov["date_start"], periods=rows, freq=prov["date_freq"]
    )
    return pd.DataFrame(
        data_rounded, index=index, columns=[prov["benchmark"], *universe["assets"]]
    )


def _leg_guard_diagnostics(weights: np.ndarray, betas: np.ndarray) -> tuple:
    """Return (min_leg_beta, gross_max) over the active rows."""
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


def _book_metrics(
    universe: dict,
    frame: pd.DataFrame,
    variant: str,
    weighting: str,
    assets: list[str],
    config: dict,
    beta_window: int,
) -> dict:
    result = BABStrategy(
        benchmark=config["benchmark"],
        beta_window=beta_window,
        min_observations=config["min_observations"],
        long_quantile=config["long_quantile"],
        short_quantile=config["short_quantile"],
        beta_neutral=config["beta_neutral"],
        transaction_costs=0.0,
        universe=assets,
        weighting=weighting,
        rank_min_leg_beta=config["rank_min_leg_beta"],
        rank_max_gross=config["rank_max_gross"],
    ).run(returns_df=frame[[config["benchmark"], *assets]])

    columns = [config["benchmark"], *assets]
    weights = (
        result.weights.reindex(columns=columns).fillna(0.0).to_numpy(dtype=float)
    )
    gross = np.abs(weights).sum(axis=1)
    active = gross > DEGENERATE_TOL
    active_rows = int(active.sum())

    betas = np.array([float(universe["betas"][a]) for a in assets])
    min_leg_beta, gross_max = _leg_guard_diagnostics(weights, betas)

    alpha = np.array([float(universe["alphas"][variant][a]) for a in assets])
    if active_rows > 0:
        w_assets = weights[active][:, 1:]
        w_bar = w_assets.mean(axis=0)
        recovery = float(w_bar @ alpha)
    else:
        recovery = 0.0

    return {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "recovery": _clean(recovery),
        "min_leg_beta": _clean(min_leg_beta),
        "gross_max": _clean(gross_max),
    }


def build_beta_drift(
    universe: dict | None = None,
    charter: dict | None = None,
    breadth_ladder: dict | None = None,
) -> dict:
    """Build the beta-window/drift grid payload (pure: reads committed JSON only)."""
    universe = load_json(UNIVERSE_PATH) if universe is None else universe
    charter = load_json(CHARTER_PATH) if charter is None else charter
    breadth_ladder = load_json(BREADTH_LADDER_PATH) if breadth_ladder is None else breadth_ladder

    config = charter["provenance"]["strategy_config"]
    beta_window_grid = list(charter["charter"]["beta_window_grid"])
    drift_threshold_grid = list(charter["charter"]["drift_threshold_grid"])
    wp_seeds = list(charter["charter"]["wp_seeds"]["wp2"])
    assets = list(universe["assets"])
    p21_rank_eval = load_json(P21_RANK_EVAL_PATH)

    committed_frames = {variant: returns_frame(universe, variant) for variant in VARIANTS}

    cells = []
    for beta_window in beta_window_grid:
        for drift_threshold in drift_threshold_grid:
            for weighting in WEIGHTINGS:
                for variant in VARIANTS:
                    per_seed_recovery = []
                    per_seed_active_rows = []
                    per_seed_min_leg_beta = []
                    per_seed_gross_max = []

                    for seed in wp_seeds:
                        frame = build_drift_stressed_panel(
                            universe, variant, seed, drift_threshold
                        )
                        book = _book_metrics(
                            universe, frame, variant, weighting, assets, config, beta_window
                        )
                        per_seed_recovery.append(book["recovery"])
                        per_seed_active_rows.append(book["active_rows"])
                        if weighting == "rank":
                            per_seed_min_leg_beta.append(book["min_leg_beta"])
                            per_seed_gross_max.append(book["gross_max"])

                    recovery_arr = np.array(per_seed_recovery)
                    recovery_mean = float(recovery_arr.mean())
                    recovery_min = float(recovery_arr.min())

                    if variant == "planted":
                        recovery_positive_seed_fraction = float(
                            (recovery_arr > 0.0).mean()
                        )
                        recovery_planted_strictly_positive = bool(
                            (recovery_arr > 0.0).all()
                        )
                        null_recovery_max_abs = 0.0
                        recovery_null_exactly_zero = True
                    else:
                        recovery_positive_seed_fraction = 0.0
                        recovery_planted_strictly_positive = True
                        null_recovery_max_abs = float(np.abs(recovery_arr).max())
                        recovery_null_exactly_zero = bool(
                            (recovery_arr == 0.0).all()
                        )

                    if weighting == "rank":
                        min_leg_beta = (
                            float(min(per_seed_min_leg_beta))
                            if per_seed_min_leg_beta
                            else 0.0
                        )
                        gross_max = (
                            float(max(per_seed_gross_max))
                            if per_seed_gross_max
                            else 0.0
                        )
                    else:
                        min_leg_beta = 0.0
                        gross_max = 0.0

                    cells.append(
                        {
                            "beta_window": beta_window,
                            "drift_threshold": _clean(drift_threshold),
                            "weighting": weighting,
                            "variant": variant,
                            "per_seed_recovery": [_clean(v) for v in per_seed_recovery],
                            "recovery_mean": _clean(recovery_mean),
                            "recovery_min": _clean(recovery_min),
                            "recovery_positive_seed_fraction": _clean(
                                recovery_positive_seed_fraction
                            ),
                            "null_recovery_max_abs": _clean(null_recovery_max_abs),
                            "recovery_planted_strictly_positive": (
                                recovery_planted_strictly_positive
                            ),
                            "recovery_null_exactly_zero": recovery_null_exactly_zero,
                            "active_rows_min": int(min(per_seed_active_rows)),
                            "min_leg_beta": _clean(min_leg_beta),
                            "gross_max": _clean(gross_max),
                            "rank_min_leg_beta_floor": float(
                                config["rank_min_leg_beta"]
                            )
                            if weighting == "rank"
                            else 0.0,
                            "rank_max_gross_ceiling": float(
                                config["rank_max_gross"]
                            )
                            if weighting == "rank"
                            else 0.0,
                            "censored": False,
                            "censor_reason": None,
                        }
                    )

    # drift_zero_reference at delta=0, beta_window=90, breadth 41
    ref_cells = []
    for weighting in WEIGHTINGS:
        for variant in VARIANTS:
            per_seed_recovery = []
            for seed in wp_seeds:
                frame = committed_frames[variant]
                book = _book_metrics(
                    universe, frame, variant, weighting, assets, config, 90
                )
                per_seed_recovery.append(book["recovery"])
            recovery_arr = np.array(per_seed_recovery)
            ref_cells.append(
                {
                    "beta_window": 90,
                    "drift_threshold": 0.0,
                    "weighting": weighting,
                    "variant": variant,
                    "recovery_mean": _clean(float(recovery_arr.mean())),
                    "per_seed_recovery": [_clean(v) for v in per_seed_recovery],
                }
            )

    p21_books = {(b["variant"], b["weighting"]): b for b in p21_rank_eval["books"]}
    drift_zero_reference = {
        "beta_window": 90,
        "drift_threshold": 0.0,
        "breadth": 41,
        "checks": {},
    }
    for ref in ref_cells:
        key = (ref["variant"], ref["weighting"])
        p21_book = p21_books[key]
        drift_zero_reference["checks"][f"{key[0]}_{key[1]}"] = {
            "committed_p21_recovery": p21_book["recovery_mean"],
            "drift_zero_recovery": ref["recovery_mean"],
            "matches_at_6dp": ref["recovery_mean"] == p21_book["recovery_mean"],
        }

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_beta_drift.py",
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
            "panel_sha256": {
                variant: universe["panels"][variant]["sha256"]
                for variant in VARIANTS
            },
            "beta_window_grid": beta_window_grid,
            "drift_threshold_grid": drift_threshold_grid,
            "wp_seeds": wp_seeds,
            "config": config,
            "drift_model": (
                "beta_true_{i,t} = beta_i * (1 + drift_scale * delta * t * u_i); "
                "R'_{i,t} = R_{i,t} + drift_scale * delta * t * u_i * beta_i * B_t; "
                "t = row index 0..rows-1; drift_scale = 0.1 (relative beta "
                "displacement up to +/-6% at delta = 1e-3); "
                "u_i ~ default_rng(seed).uniform(-1, 1); committed benchmark and "
                "residuals reused row-for-row"
            ),
            "drift_scale": DRIFT_SCALE,
            "selection_rule": "full committed 41-asset universe (breadth 41)",
            "recovery_estimator": (
                "recovery = w_bar @ alpha where w_bar is the mean active-row "
                "weight vector and alpha is the planted/null alpha from universe.json"
            ),
            "acceptance_thresholds": charter["provenance"][
                "acceptance_thresholds"
            ]["wp2"],
            "drift_zero_reference": drift_zero_reference,
            "derived": {
                "n_cells": len(cells),
                "n_seeds": len(wp_seeds),
                "n_book_runs": len(cells) * len(wp_seeds),
                "beta_window_default_preserved": 90 in beta_window_grid,
                "min_beta_windows_met": len(beta_window_grid)
                >= charter["provenance"]["acceptance_thresholds"]["wp2"][
                    "min_beta_windows"
                ],
                "min_drift_thresholds_met": len(drift_threshold_grid)
                >= charter["provenance"]["acceptance_thresholds"]["wp2"][
                    "min_drift_thresholds"
                ],
            },
        },
        "cells": cells,
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    lines = [
        "# BAB P23 WP2 — beta-window/drift grid",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Universe seed {prov['universe_seed']}; charter schema "
        f"`{prov['charter_schema']}`.",
        f"Drift model: {prov['drift_model']}.",
        "",
        "| beta_window | drift_threshold | weighting | variant | recovery_mean | recovery_min | "
        "recovery_positive_frac | null_max_abs | active_rows_min | min_leg_beta | gross_max |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {cell['beta_window']} | {cell['drift_threshold']} | "
        f"{cell['weighting']} | {cell['variant']} | "
        f"{cell['recovery_mean']} | {cell['recovery_min']} | "
        f"{cell['recovery_positive_seed_fraction']} | "
        f"{cell['null_recovery_max_abs']} | {cell['active_rows_min']} | "
        f"{cell['min_leg_beta']} | {cell['gross_max']} |"
        for cell in payload["cells"]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: dict, json_path: str | Path | None = None,
    md_path: str | Path | None = None,
) -> tuple[Path, Path]:
    directory = _REPO_ROOT / OUTPUT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    jp = Path(json_path) if json_path is not None else directory / "beta_drift.json"
    mp = Path(md_path) if md_path is not None else directory / "beta_drift.md"
    jp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mp.write_text(render_markdown(payload), encoding="utf-8")
    return jp, mp


def main() -> None:
    started = time.perf_counter()
    payload = build_beta_drift()
    jp, mp = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for cell in payload["cells"]:
        print(
            f"w={cell['beta_window']} d={cell['drift_threshold']} "
            f"{cell['weighting']:5s} {cell['variant']:7s} "
            f"recovery={cell['recovery_mean']:+.6f} "
            f"planted_pos={cell['recovery_planted_strictly_positive']} "
            f"null_zero={cell['recovery_null_exactly_zero']}"
        )
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
