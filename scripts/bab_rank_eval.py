#!/usr/bin/env python3
"""P21 WP1 — rank vs equal evaluation on the planted universe.

Loads ``research_state/bab_p21/universe.json`` read-only, runs the shipped
``BABStrategy`` twice per variant (``weighting="equal"`` and
``weighting="rank"``, identical non-weighting config) on both the ``planted``
and ``null`` panels, and publishes per-book recovery, activity, guard
compliance, and neutrality metrics.

The planted variant has alpha strictly decreasing in beta, so a beta-neutral
BAB book recovers positive planted alpha; the null variant has all alphas
zero, so the same book recovers exactly zero. This is the first empirical
measurement of rank weighting on a universe where its guards can actually
clear (P20's 9-asset fixture flattens rank to a zero book).

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_rank_eval.py
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
from strategies.betting_against_beta import BABStrategy  # noqa: E402

SCHEMA = "bab_p21.rank_eval/1"
OUTPUT_DIR = "research_state/bab_p21"
DEGENERATE_TOL = 1e-12
BETA_NEUTRAL_TOL = 0.02
RECOVERY_FLOOR = 1e-5
NULL_RECOVERY_TOL = 1e-15
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0

CONFIG = dict(
    benchmark="BTC",
    beta_window=90,
    min_observations=60,
    long_quantile=0.3,
    short_quantile=0.3,
    transaction_costs=0.0,
    beta_neutral=True,
)


def _clean(value: float) -> float:
    return round(float(value), 6)


def _panel_sha(panel) -> str:
    blob = json.dumps(panel, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _book_metrics(variant: str, weighting: str, payload: dict) -> dict:
    """Run one book and return its metric dict."""
    assets = list(payload["assets"])
    columns = [payload["provenance"]["benchmark"], *assets]
    betas_true = np.concatenate(
        [[1.0], [float(payload["betas"][a]) for a in assets]]
    )

    frame = u.build_returns_frame(variant, payload)
    result = BABStrategy(
        benchmark=payload["provenance"]["benchmark"],
        beta_window=CONFIG["beta_window"],
        min_observations=CONFIG["min_observations"],
        long_quantile=CONFIG["long_quantile"],
        short_quantile=CONFIG["short_quantile"],
        beta_neutral=CONFIG["beta_neutral"],
        transaction_costs=CONFIG["transaction_costs"],
        universe=assets,
        weighting=weighting,
        rank_min_leg_beta=RANK_MIN_LEG_BETA,
        rank_max_gross=RANK_MAX_GROSS,
    ).run(returns_df=frame)

    weights = result.weights.reindex(columns=columns).fillna(0.0).to_numpy(dtype=float)
    gross = np.abs(weights).sum(axis=1)
    active = gross > DEGENERATE_TOL
    active_rows = int(active.sum())
    total_rows = len(weights)

    panel = payload["panels"][variant]["returns"]
    panel_sha256 = _panel_sha(panel)

    if active_rows == 0:
        return {
            "variant": variant,
            "weighting": weighting,
            "active_rows": 0,
            "total_rows": total_rows,
            "gross_mean_active": 0.0,
            "gross_max": 0.0,
            "long_leg_beta_mean": 0.0,
            "short_leg_beta_mean": 0.0,
            "min_leg_beta": 0.0,
            "dollar_imbalance_max": 0.0,
            "beta_exposure_max": 0.0,
            "recovery_mean": 0.0,
            "recovery_frac_positive": 0.0,
            "panel_sha256": panel_sha256,
        }

    w_active = weights[active]
    gross_active = gross[active]

    dollar_imbalance_max = float(np.abs(w_active.sum(axis=1)).max())

    # True-beta portfolio exposure per active row (BTC weight is 0; beta=1).
    beta_exposure = w_active @ betas_true
    beta_exposure_max = float(np.abs(beta_exposure).max())

    # Leg betas per active row from TRUE betas over assets actually held.
    w_assets = w_active[:, 1:]  # drop benchmark column
    beta_assets = betas_true[1:]  # drop benchmark beta (1.0)
    long_mask = w_assets > 0.0
    short_mask = w_assets < 0.0

    long_betas = np.zeros(active_rows, dtype=float)
    short_betas = np.zeros(active_rows, dtype=float)
    min_leg_betas = np.zeros(active_rows, dtype=float)
    for i in range(active_rows):
        lm = long_mask[i]
        sm = short_mask[i]
        lw = w_assets[i][lm]
        sw = np.abs(w_assets[i][sm])
        lb = beta_assets[lm]
        sb = beta_assets[sm]
        long_betas[i] = float(np.dot(lw, lb) / lw.sum()) if lw.sum() > 0 else 0.0
        short_betas[i] = float(np.dot(sw, sb) / sw.sum()) if sw.sum() > 0 else 0.0
        min_leg_betas[i] = min(long_betas[i], short_betas[i])

    # Mean active-row weight vector -> recovery statistic.
    w_bar = w_assets.mean(axis=0)
    recovery_mean = float(w_bar @ beta_assets * 0.0 + w_bar @ np.array(
        [float(payload["alphas"][variant][a]) for a in assets]
    ))

    # Per-row recovery for fraction-positive.
    row_alpha = np.array([float(payload["alphas"][variant][a]) for a in assets])
    row_recovery = w_assets @ row_alpha
    recovery_frac_positive = float((row_recovery > 0.0).mean())

    return {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "total_rows": total_rows,
        "gross_mean_active": float(gross_active.mean()),
        "gross_max": float(gross_active.max()),
        "long_leg_beta_mean": float(long_betas.mean()),
        "short_leg_beta_mean": float(short_betas.mean()),
        "min_leg_beta": float(min_leg_betas.min()),
        "dollar_imbalance_max": dollar_imbalance_max,
        "beta_exposure_max": beta_exposure_max,
        "recovery_mean": _clean(recovery_mean),
        "recovery_frac_positive": _clean(recovery_frac_positive),
        "panel_sha256": panel_sha256,
    }


def build_rank_eval(payload: dict | None = None) -> dict:
    """Build the rank-eval payload (pure, no I/O)."""
    payload = u.build_universe() if payload is None else payload
    prov = payload["provenance"]

    books = [
        _book_metrics(variant, weighting, payload)
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    ]

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_rank_eval.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "universe_seed": prov["seed"],
            "panel_sha256": {
                variant: payload["panels"][variant]["sha256"] for variant in VARIANTS
            },
            "config": {
                **CONFIG,
                "rank_min_leg_beta": RANK_MIN_LEG_BETA,
                "rank_max_gross": RANK_MAX_GROSS,
                "universe": list(payload["assets"]),
            },
            "recovery_estimator": (
                "recovery_mean = sum(w_bar_i * alpha_i) where w_bar is the "
                "mean active-row weight vector over the tradable assets and "
                "alpha_i is the planted (or null) alpha from universe.json."
            ),
            "caveat": (
                "Recovery on a planted synthetic universe proves the estimator "
                "works; it is never market alpha. A null-universe positive "
                "result is a bug, not a finding."
            ),
        },
        "books": books,
    }


def render_markdown(payload: dict) -> str:
    """Render the rank-eval summary from the payload; no external numbers."""
    prov = payload["provenance"]
    lines = [
        "# BAB P21 WP1 — rank vs equal evaluation on the planted universe",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus with known "
        "ground truth: not real market data and not market profitability "
        "evidence.",
        "",
        f"Universe seed {prov['universe_seed']}; variants "
        + ", ".join(sorted(prov["panel_sha256"].keys()))
        + "; config: " + json.dumps(prov["config"], sort_keys=True),
        "",
        "| variant | weighting | active_rows | gross_mean_active | gross_max | "
        "long_leg_beta_mean | short_leg_beta_mean | min_leg_beta | "
        "dollar_imbalance_max | beta_exposure_max | recovery_mean | "
        "recovery_frac_positive | panel_sha256 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        "| {variant} | {weighting} | {active_rows} | {gross_mean_active} | "
        "{gross_max} | {long_leg_beta_mean} | {short_leg_beta_mean} | "
        "{min_leg_beta} | {dollar_imbalance_max} | {beta_exposure_max} | "
        "{recovery_mean} | {recovery_frac_positive} | {panel_sha256} |".format(**book)
        for book in payload["books"]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "rank_eval.json"
    markdown_path = directory / "rank_eval.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_rank_eval()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for book in payload["books"]:
        print(
            f"{book['variant']:7s} {book['weighting']:5s} "
            f"active={book['active_rows']} gross={book['gross_mean_active']:.4f} "
            f"recovery={book['recovery_mean']:.6f} "
            f"min_leg_beta={book['min_leg_beta']:.4f}"
        )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
