#!/usr/bin/env python3
"""P23 WP1 — breadth ladder on the committed P21 universe."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import bab_synthetic_universe as u
from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta import metrics as m

SCHEMA = "bab_p23.breadth_ladder/1"
OUTPUT_DIR = "research_state/bab_p23"
DECIMALS = 6
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
DEGENERATE_TOL = 1e-12
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0


def _clean(value):
    return round(float(value), DECIMALS)


def _book_metrics(variant, weighting, universe, b, charter):
    cfg = charter["provenance"]["strategy_config"]
    assets = list(universe["assets"])[:b]
    columns = [universe["provenance"]["benchmark"], *assets]
    betas_true = np.concatenate(
        [[1.0], [float(universe["betas"][a]) for a in assets]]
    )

    frame = u.build_returns_frame(variant, universe)[
        [universe["provenance"]["benchmark"], *assets]
    ]
    result = BABStrategy(
        benchmark=cfg["benchmark"],
        beta_window=cfg["beta_window"],
        min_observations=cfg["min_observations"],
        long_quantile=cfg["long_quantile"],
        short_quantile=cfg["short_quantile"],
        beta_neutral=cfg["beta_neutral"],
        transaction_costs=0.0,
        universe=assets,
        weighting=weighting,
        rank_min_leg_beta=cfg["rank_min_leg_beta"],
        rank_max_gross=cfg["rank_max_gross"],
    ).run(returns_df=frame)

    weights = result.weights.reindex(columns=columns).fillna(0.0).to_numpy(
        dtype=float
    )
    gross = np.abs(weights).sum(axis=1)
    active = gross > DEGENERATE_TOL
    active_rows = int(active.sum())

    min_leg_beta = 0.0
    gross_max = 0.0
    if active_rows > 0:
        w_active = weights[active]
        gross_active = gross[active]
        gross_max = float(gross_active.max())
        w_assets = w_active[:, 1:]
        beta_assets = betas_true[1:]
        long_mask = w_assets > 0.0
        short_mask = w_assets < 0.0
        min_leg_betas = []
        for i in range(active_rows):
            lm = long_mask[i]
            sm = short_mask[i]
            lw = w_assets[i][lm]
            sw = np.abs(w_assets[i][sm])
            lb = beta_assets[lm]
            sb = beta_assets[sm]
            long_b = (
                float(np.dot(lw, lb) / lw.sum()) if lw.sum() > 0 else 0.0
            )
            short_b = (
                float(np.dot(sw, sb) / sw.sum()) if sw.sum() > 0 else 0.0
            )
            min_leg_betas.append(min(long_b, short_b))
        min_leg_beta = float(np.min(min_leg_betas)) if min_leg_betas else 0.0

    row_alpha = np.array(
        [float(universe["alphas"][variant][a]) for a in assets]
    )
    if active_rows > 0 and variant != "null":
        w_assets_all = weights[active, 1:]
        row_recovery = w_assets_all @ row_alpha
        recovery_frac_positive = float((row_recovery > 0.0).mean())
        w_bar = weights[active, 1:].mean(axis=0)
        recovery_mean = float(w_bar @ row_alpha)
    else:
        recovery_frac_positive = 0.0
        recovery_mean = 0.0

    wealth = (
        float(result.backtest["cumulative"].iloc[-1])
        if len(result.backtest)
        else 0.0
    )
    try:
        gross_sharpe = float(m.sharpe_ratio(result.backtest["returns"]))
    except Exception:
        gross_sharpe = 0.0
    if not np.isfinite(gross_sharpe):
        gross_sharpe = 0.0

    return {
        "variant": variant,
        "weighting": weighting,
        "breadth": len(assets),
        "active_rows": active_rows,
        "recovery_mean": _clean(recovery_mean),
        "recovery_frac_positive": _clean(recovery_frac_positive),
        "gross_sharpe": _clean(gross_sharpe),
        "wealth": _clean(wealth),
        "min_leg_beta": _clean(min_leg_beta) if active_rows > 0 else 0.0,
        "gross_max": _clean(gross_max) if active_rows > 0 else 0.0,
    }


def build_breadth_ladder(planted_panel=None, null_panel=None, charter_json=None):
    if charter_json is None:
        charter_json = json.loads(
            (_REPO_ROOT / "research_state/bab_p23/charter.json").read_text(
                encoding="utf-8"
            )
        )
    if planted_panel is None:
        planted_panel = u.build_universe()
    universe = planted_panel

    ladder = []
    for b in charter_json["charter"]["breadth_ladder"]:
        books = []
        for variant in VARIANTS:
            for weighting in WEIGHTINGS:
                bm = _book_metrics(variant, weighting, universe, b, charter_json)
                books.append(bm)
        ladder.append({"breadth": b, "books": books})

    provenance = {
        "generator": "scripts/bab_breadth_ladder.py",
        "synthetic": True,
        "universe_seed": universe["provenance"]["seed"],
        "panel_sha256": {
            v: universe["panels"][v]["sha256"] for v in VARIANTS
        },
        "charter_schema": charter_json["schema"],
        "config": charter_json["provenance"]["strategy_config"],
    }
    return {
        "schema": SCHEMA,
        "provenance": provenance,
        "ladder": ladder,
    }


def render_markdown(payload):
    lines = [
        "# BAB P23 WP1 — breadth ladder",
        "",
        f"Schema `{payload['schema']}`.",
        "",
    ]
    for rung in payload["ladder"]:
        lines.append(f"## Breadth {rung['breadth']}")
        for book in rung["books"]:
            lines.append(
                "- "
                + f"{book['variant']} {book['weighting']}: "
                + f"active={book['active_rows']} "
                + f"recovery={book['recovery_mean']} "
                + f"gross_sharpe={book['gross_sharpe']} "
                + f"wealth={book['wealth']}"
            )
    return "\n".join(lines) + "\n"


def write_artifacts(payload, json_path=None, md_path=None):
    out = _REPO_ROOT / OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    jp = out / "breadth_ladder.json"
    mp = out / "breadth_ladder.md"
    jp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mp.write_text(render_markdown(payload), encoding="utf-8")
    return jp, mp


def main():
    started = time.perf_counter()
    charter = json.loads(
        (_REPO_ROOT / "research_state/bab_p23/charter.json").read_text(
            encoding="utf-8"
        )
    )
    universe = u.build_universe()
    payload = build_breadth_ladder(universe, universe, charter)
    jp, mp = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
