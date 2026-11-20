#!/usr/bin/env python3
"""P24 WP1 — regime-split stress on the committed P21 universe.

Reads ``research_state/bab_p21/universe.json``,
``research_state/bab_p23/charter.json`` and
``research_state/bab_p24/charter.json`` read-only. For every chartered
``regime`` in ``regime_grid`` (``calm``, ``stress``), every ``hysteresis``
in ``hysteresis_band_grid``, both weightings (``equal``, ``rank``) and both
variants (``planted``, ``null``) it runs the shipped ``BABStrategy`` with
regime-conditional parameters and publishes aggregated recovery statistics,
per-seed recovery lists and an explicit ``regime_zero_reference`` block
pinned to the committed P21 ``rank_eval.json`` and the P23 WP1 breadth-41
baseline.

Regime-conditional parameter grid (charter constants):
  * ``calm``: beta_window=120, long_quantile=0.25, short_quantile=0.25
  * ``stress``: beta_window=60, long_quantile=0.35, short_quantile=0.35

The regime detector uses ``classify_volatility_regimes_percentile`` with the
chartered ``vol_hysteresis`` from ``hysteresis_band_grid``. When
``regime_filter=True`` the strategy applies a single causal scalar scale
factor per date (most conservative across assets) via
``regime_scale_scalar``, preserving dollar-neutrality exactly.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_regime_split.py
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

SCHEMA = "bab_p24.regime_split/1"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
P23_CHARTER_PATH = "research_state/bab_p23/charter.json"
P24_CHARTER_PATH = "research_state/bab_p24/charter.json"
P21_RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
OUTPUT_DIR = "research_state/bab_p24"
DECIMALS = 6
DEGENERATE_TOL = 1e-12
TRADING_DAYS = 252
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")

# Regime-conditional parameter grid (charter constants)
REGIME_CONFIGS = {
    "calm": {
        "beta_window": 120,
        "long_quantile": 0.25,
        "short_quantile": 0.25,
    },
    "stress": {
        "beta_window": 60,
        "long_quantile": 0.35,
        "short_quantile": 0.35,
    },
}

# WP1 seeds (deterministic, separate from P23 seeds)
WP1_SEEDS = [
    20270101, 20270102, 20270103, 20270104, 20270105,
    20270106, 20270107, 20270108, 20270109, 20270110,
    20270111, 20270112, 20270113, 20270114, 20270115,
    20270116, 20270117, 20270118, 20270119, 20270120,
]


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


def _sharpe(pnl: np.ndarray) -> float:
    values = np.asarray(pnl, dtype=float)
    std = float(values.std(ddof=1))
    if std <= 0.0:
        return 0.0
    return float(values.mean() / std * np.sqrt(TRADING_DAYS))


def _book_metrics(
    universe: dict,
    frame: pd.DataFrame,
    variant: str,
    weighting: str,
    regime: str,
    hysteresis: float,
    assets: list[str],
    config: dict,
) -> dict:
    """Run BABStrategy with regime-conditional config and return metrics."""
    regime_cfg = REGIME_CONFIGS[regime]

    # Merge base config with regime-specific overrides
    strategy_config = {
        **config,
        "beta_window": regime_cfg["beta_window"],
        "long_quantile": regime_cfg["long_quantile"],
        "short_quantile": regime_cfg["short_quantile"],
        "regime_filter": True,
        "vol_hysteresis": hysteresis,
    }

    result = BABStrategy(**strategy_config).run(returns_df=frame[[config["benchmark"], *assets]])

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
        row_recovery = w_assets @ alpha
        recovery_frac_positive = float((row_recovery > 0.0).mean())
    else:
        recovery = 0.0
        recovery_frac_positive = 0.0

    returns_pnl = (
        result.backtest["returns"].to_numpy(dtype=float)
        if len(result.backtest)
        else np.array([])
    )
    gross_sharpe = _sharpe(returns_pnl)
    wealth = float(result.backtest["cumulative"].iloc[-1]) if len(result.backtest) else 0.0

    return {
        "variant": variant,
        "weighting": weighting,
        "regime": regime,
        "hysteresis": _clean(hysteresis),
        "active_rows": active_rows,
        "recovery": _clean(recovery),
        "recovery_frac_positive": _clean(recovery_frac_positive),
        "gross_sharpe": _clean(gross_sharpe),
        "wealth": _clean(wealth),
        "min_leg_beta": _clean(min_leg_beta),
        "gross_max": _clean(gross_max),
        "rank_min_leg_beta_floor": float(config["rank_min_leg_beta"]),
        "rank_max_gross_ceiling": float(config["rank_max_gross"]),
        "beta_window": regime_cfg["beta_window"],
        "long_quantile": regime_cfg["long_quantile"],
        "short_quantile": regime_cfg["short_quantile"],
    }


def build_regime_split(
    universe: dict | None = None,
    p23_charter: dict | None = None,
    p24_charter: dict | None = None,
) -> dict:
    """Build the regime-split stress payload (pure: reads committed JSON only)."""
    universe = load_json(UNIVERSE_PATH) if universe is None else universe
    p23_charter = load_json(P23_CHARTER_PATH) if p23_charter is None else p23_charter
    p24_charter = load_json(P24_CHARTER_PATH) if p24_charter is None else p24_charter

    config = p23_charter["provenance"]["strategy_config"]
    regime_grid = list(p24_charter["charter"]["regime_grid"])
    hysteresis_band_grid = list(p24_charter["charter"]["hysteresis_band_grid"])
    assets = list(universe["assets"])
    p21_rank_eval = load_json(P21_RANK_EVAL_PATH)

    frames = {variant: returns_frame(universe, variant) for variant in VARIANTS}

    cells = []
    for regime in regime_grid:
        for hysteresis in hysteresis_band_grid:
            for weighting in WEIGHTINGS:
                for variant in VARIANTS:
                    per_seed_recovery = []
                    per_seed_active_rows = []
                    per_seed_min_leg_beta = []
                    per_seed_gross_max = []
                    per_seed_gross_sharpe = []
                    per_seed_wealth = []

                    for seed in WP1_SEEDS:
                        # Set seed for reproducibility of any internal RNG
                        np.random.seed(seed)

                        book = _book_metrics(
                            universe,
                            frames[variant],
                            variant,
                            weighting,
                            regime,
                            hysteresis,
                            assets,
                            config,
                        )
                        per_seed_recovery.append(book["recovery"])
                        per_seed_active_rows.append(book["active_rows"])
                        if weighting == "rank":
                            per_seed_min_leg_beta.append(book["min_leg_beta"])
                            per_seed_gross_max.append(book["gross_max"])
                        per_seed_gross_sharpe.append(book["gross_sharpe"])
                        per_seed_wealth.append(book["wealth"])

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
                            "regime": regime,
                            "hysteresis": _clean(hysteresis),
                            "weighting": weighting,
                            "variant": variant,
                            "per_seed_recovery": [_clean(v) for v in per_seed_recovery],
                            "per_seed_active_rows": per_seed_active_rows,
                            "per_seed_gross_sharpe": [_clean(v) for v in per_seed_gross_sharpe],
                            "per_seed_wealth": [_clean(v) for v in per_seed_wealth],
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
                            "gross_sharpe_mean": _clean(float(np.mean(per_seed_gross_sharpe))),
                            "wealth_mean": _clean(float(np.mean(per_seed_wealth))),
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
                            "beta_window": REGIME_CONFIGS[regime]["beta_window"],
                            "long_quantile": REGIME_CONFIGS[regime]["long_quantile"],
                            "short_quantile": REGIME_CONFIGS[regime]["short_quantile"],
                            "censored": False,
                            "censor_reason": None,
                        }
                    )

    # regime_zero_reference: baseline (no regime filter) at breadth 41
    ref_cells = []
    for weighting in WEIGHTINGS:
        for variant in VARIANTS:
            per_seed_recovery = []
            for seed in WP1_SEEDS:
                np.random.seed(seed)
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
                ).run(returns_df=frames[variant][[config["benchmark"], *assets]])

                columns = [config["benchmark"], *assets]
                weights = (
                    result.weights.reindex(columns=columns).fillna(0.0).to_numpy(dtype=float)
                )
                gross = np.abs(weights).sum(axis=1)
                active = gross > DEGENERATE_TOL
                alpha = np.array([float(universe["alphas"][variant][a]) for a in assets])
                if active.any():
                    w_assets = weights[active][:, 1:]
                    w_bar = w_assets.mean(axis=0)
                    recovery = float(w_bar @ alpha)
                else:
                    recovery = 0.0
                per_seed_recovery.append(_clean(recovery))

            recovery_arr = np.array(per_seed_recovery)
            ref_cells.append(
                {
                    "regime": "baseline",
                    "weighting": weighting,
                    "variant": variant,
                    "recovery_mean": _clean(float(recovery_arr.mean())),
                    "per_seed_recovery": [_clean(v) for v in per_seed_recovery],
                }
            )

    p21_books = {(b["variant"], b["weighting"]): b for b in p21_rank_eval["books"]}
    regime_zero_reference = {
        "regime": "baseline",
        "breadth": 41,
        "beta_window": config["beta_window"],
        "checks": {},
    }
    for ref in ref_cells:
        key = (ref["variant"], ref["weighting"])
        p21_book = p21_books[key]
        regime_zero_reference["checks"][f"{key[0]}_{key[1]}"] = {
            "committed_p21_recovery": p21_book["recovery_mean"],
            "regime_zero_recovery": ref["recovery_mean"],
            "matches_at_6dp": ref["recovery_mean"] == p21_book["recovery_mean"],
        }

    # P23 WP1 breadth-41 baseline cross-check
    p23_breadth = load_json("research_state/bab_p23/breadth_ladder.json")
    breadth_41_books = {
        (b["variant"], b["weighting"]): b
        for rung in p23_breadth["ladder"]
        if rung["breadth"] == 41
        for b in rung["books"]
    }
    breadth_41_checks = {}
    for key, book in breadth_41_books.items():
        breadth_41_checks[f"{key[0]}_{key[1]}"] = {
            "p23_breadth_41_recovery": book["recovery_mean"],
            "p23_breadth_41_active_rows": book["active_rows"],
        }

    thresholds = p24_charter["provenance"].get("acceptance_thresholds", {}).get("wp1", {
        "regime_grid_min": 2,
        "hysteresis_band_grid_min": 3,
        "recovery_null_exactly_zero": 0.0,
        "recovery_planted_strictly_positive": True,
    })

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_regime_split.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: not "
                "real market data and not market profitability evidence."
            ),
            "universe_path": UNIVERSE_PATH,
            "universe_seed": universe["provenance"]["seed"],
            "p23_charter_path": P23_CHARTER_PATH,
            "p23_charter_schema": p23_charter["schema"],
            "p24_charter_path": P24_CHARTER_PATH,
            "p24_charter_schema": p24_charter["schema"],
            "panel_sha256": {
                variant: universe["panels"][variant]["sha256"] for variant in VARIANTS
            },
            "regime_grid": regime_grid,
            "hysteresis_band_grid": hysteresis_band_grid,
            "regime_configs": REGIME_CONFIGS,
            "wp_seeds": WP1_SEEDS,
            "config": config,
            "regime_model": (
                "Volatility regime detection via classify_volatility_regimes_percentile "
                "with vol_hysteresis from hysteresis_band_grid; regime_filter applies "
                "a single causal scalar scale factor per date (minimum across assets) "
                "via regime_scale_scalar, preserving dollar-neutrality exactly. "
                "Calm regime uses beta_window=120, quantiles=0.25; stress regime uses "
                "beta_window=60, quantiles=0.35."
            ),
            "selection_rule": "full committed 41-asset universe (breadth 41)",
            "recovery_estimator": (
                "recovery = w_bar @ alpha where w_bar is the mean active-row "
                "weight vector and alpha is the planted/null alpha from universe.json"
            ),
            "acceptance_thresholds": thresholds,
            "regime_zero_reference": regime_zero_reference,
            "breadth_41_cross_check": breadth_41_checks,
            "derived": {
                "n_cells": len(cells),
                "n_seeds": len(WP1_SEEDS),
                "n_regimes": len(regime_grid),
                "n_hysteresis_levels": len(hysteresis_band_grid),
                "n_book_runs": len(cells) * len(WP1_SEEDS),
                "regime_grid_min_met": len(regime_grid)
                >= thresholds["regime_grid_min"],
                "hysteresis_band_grid_min_met": len(hysteresis_band_grid)
                >= thresholds["hysteresis_band_grid_min"],
            },
        },
        "cells": cells,
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    lines = [
        "# BAB P24 WP1 — regime-split stress",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Universe seed {prov['universe_seed']}; P23 charter schema "
        f"`{prov['p23_charter_schema']}`; P24 charter schema "
        f"`{prov['p24_charter_schema']}`.",
        f"Regime model: {prov['regime_model']}.",
        "",
        "| regime | hysteresis | weighting | variant | recovery_mean | recovery_min | "
        "recovery_positive_frac | null_max_abs | active_rows_min | min_leg_beta | "
        "gross_max | gross_sharpe_mean | wealth_mean | beta_window | "
        "long_quantile | short_quantile |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {cell['regime']} | {cell['hysteresis']} | {cell['weighting']} | "
        f"{cell['variant']} | {cell['recovery_mean']} | {cell['recovery_min']} | "
        f"{cell['recovery_positive_seed_fraction']} | {cell['null_recovery_max_abs']} | "
        f"{cell['active_rows_min']} | {cell['min_leg_beta']} | {cell['gross_max']} | "
        f"{cell['gross_sharpe_mean']} | {cell['wealth_mean']} | {cell['beta_window']} | "
        f"{cell['long_quantile']} | {cell['short_quantile']} |"
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
    jp = Path(json_path) if json_path is not None else directory / "regime_split.json"
    mp = Path(md_path) if md_path is not None else directory / "regime_split.md"
    jp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mp.write_text(render_markdown(payload), encoding="utf-8")
    return jp, mp


def main() -> None:
    started = time.perf_counter()
    payload = build_regime_split()
    jp, mp = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for cell in payload["cells"]:
        print(
            f"regime={cell['regime']:5s} h={cell['hysteresis']:.2f} "
            f"{cell['weighting']:5s} {cell['variant']:7s} "
            f"recovery={cell['recovery_mean']:+.6f} "
            f"planted_pos={cell['recovery_planted_strictly_positive']} "
            f"null_zero={cell['recovery_null_exactly_zero']} "
            f"active_min={cell['active_rows_min']} "
            f"sharpe={cell['gross_sharpe_mean']:+.3f}"
        )
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
