#!/usr/bin/env python3
"""P23 WP1 — breadth ladder on the committed P21 universe.

Reads ``research_state/bab_p21/universe.json`` and
``research_state/bab_p23/charter.json`` read-only. For every chartered breadth
``b`` it builds a sub-universe of ``b`` assets drawn evenly across the
beta-ordered asset list (so the full beta spread survives concentration), runs
the shipped ``BABStrategy`` with the chartered config for both weightings
(``equal``, ``rank``) and both variants (``planted``, ``null``), and publishes
active-row count, recovery, positive-recovery fraction, gross Sharpe, wealth
and the rank-guard diagnostics.

Ground truth: the planted panel carries a strictly beta-decreasing convex
alpha; the null panel carries zero alpha. A correct estimator therefore shows
strictly positive recovery on every planted rung and exactly zero recovery on
every null rung. This is a controlled synthetic stimulus, never market data.

Usage:
  python3 scripts/bab_breadth_ladder.py
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

SCHEMA = "bab_p23.breadth_ladder/1"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
CHARTER_PATH = "research_state/bab_p23/charter.json"
OUTPUT_DIR = "research_state/bab_p23"
DECIMALS = 6
DEGENERATE_TOL = 1e-12
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")


def _clean(value: float) -> float:
    return round(float(value), DECIMALS)


def load_json(relative_path: str) -> dict:
    """Load one committed JSON artifact read-only."""
    return json.loads((_REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def returns_frame(universe: dict, variant: str) -> pd.DataFrame:
    """Rebuild the committed panel for ``variant`` from JSON only.

    The benchmark column is prepended exactly as the P21 readers do; the panel
    is read from ``universe['panels'][variant]['returns']`` and is never
    regenerated.
    """
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


def breadth_assets(universe: dict, breadth: int) -> list[str]:
    """Pick ``breadth`` assets evenly across the beta-ordered asset list.

    The committed list ``A001..A041`` is beta-ordered by construction, so
    even spacing preserves the full beta spread while shrinking the name
    count. Endpoints are always included.
    """
    assets = list(universe["assets"])
    if breadth < 2 or breadth > len(assets):
        raise ValueError(
            f"breadth must be in [2, {len(assets)}], got {breadth!r}"
        )
    positions = np.unique(
        np.round(np.linspace(0, len(assets) - 1, breadth)).astype(int)
    )
    if len(positions) != breadth:
        raise ValueError(f"breadth {breadth!r} is not representable")
    return [assets[i] for i in positions]


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
    breadth: int,
    assets: list[str],
    config: dict,
) -> dict:
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

    alpha = np.array(
        [float(universe["alphas"][variant][a]) for a in assets]
    )
    if active_rows > 0:
        w_assets = weights[active][:, 1:]
        w_bar = w_assets.mean(axis=0)
        recovery_mean = float(w_bar @ alpha)
        row_recovery = w_assets @ alpha
        recovery_frac_positive = float((row_recovery > 0.0).mean())
    else:
        recovery_mean = 0.0
        recovery_frac_positive = 0.0

    returns = result.backtest["returns"] if len(result.backtest) else None
    if returns is None or len(returns) == 0:
        gross_sharpe = 0.0
        wealth = 0.0
    else:
        std = float(np.std(returns.to_numpy(dtype=float), ddof=1))
        mean = float(np.mean(returns.to_numpy(dtype=float)))
        gross_sharpe = mean / std * np.sqrt(252.0) if std > 0.0 else 0.0
        if not np.isfinite(gross_sharpe):
            gross_sharpe = 0.0
        wealth = float(result.backtest["cumulative"].iloc[-1])

    return {
        "variant": variant,
        "weighting": weighting,
        "breadth": breadth,
        "assets": list(assets),
        "active_rows": active_rows,
        "recovery_mean": _clean(recovery_mean),
        "recovery_frac_positive": _clean(recovery_frac_positive),
        "gross_sharpe": _clean(gross_sharpe),
        "wealth": _clean(wealth),
        "min_leg_beta": _clean(min_leg_beta),
        "gross_max": _clean(gross_max),
        "rank_min_leg_beta_floor": float(config["rank_min_leg_beta"]),
        "rank_max_gross_ceiling": float(config["rank_max_gross"]),
    }


def build_breadth_ladder(
    universe: dict | None = None, charter: dict | None = None
) -> dict:
    """Build the breadth-ladder payload (pure: reads committed JSON only)."""
    universe = load_json(UNIVERSE_PATH) if universe is None else universe
    charter = load_json(CHARTER_PATH) if charter is None else charter
    config = charter["provenance"]["strategy_config"]

    frames = {variant: returns_frame(universe, variant) for variant in VARIANTS}
    ladder = []
    for breadth in charter["charter"]["breadth_ladder"]:
        assets = breadth_assets(universe, breadth)
        books = [
            _book_metrics(
                universe, frames[variant], variant, weighting,
                breadth, assets, config,
            )
            for variant in VARIANTS
            for weighting in WEIGHTINGS
        ]
        assorted = sorted(
            books, key=lambda book: (VARIANTS.index(book["variant"]),
                                     WEIGHTINGS.index(book["weighting"])),
        )
        ladder.append({"breadth": breadth, "books": assorted})

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_breadth_ladder.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: not "
                "real market data and not market profitability evidence."
            ),
            "universe_path": UNIVERSE_PATH,
            "universe_seed": universe["provenance"]["seed"],
            "charter_path": CHARTER_PATH,
            "charter_schema": charter["schema"],
            "panel_sha256": {
                variant: universe["panels"][variant]["sha256"]
                for variant in VARIANTS
            },
            "breadth_ladder": list(charter["charter"]["breadth_ladder"]),
            "selection_rule": (
                "evenly spaced indices over the beta-ordered committed asset "
                "list, endpoints included"
            ),
            "config": config,
            "recovery_estimator": (
                "recovery_mean = mean over active rows of sum_i w_i alpha_i, "
                "computed as w_bar @ alpha with alpha from universe.json"
            ),
            "acceptance_thresholds": charter["provenance"][
                "acceptance_thresholds"
            ]["wp1"],
            "derived": {
                "rungs": len(ladder),
                "ladder_min_rungs_met": len(ladder)
                >= charter["provenance"]["acceptance_thresholds"]["wp1"][
                    "ladder_min_rungs"
                ],
            },
        },
        "ladder": ladder,
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    lines = [
        "# BAB P23 WP1 — breadth ladder",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Universe seed {prov['universe_seed']}; charter schema "
        f"`{prov['charter_schema']}`; selection: {prov['selection_rule']}.",
        "",
        "| breadth | variant | weighting | active_rows | recovery_mean | "
        "recovery_frac_positive | gross_sharpe | wealth | min_leg_beta | "
        "gross_max |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {book['breadth']} | {book['variant']} | "
        f"{book['weighting']} | {book['active_rows']} | "
        f"{book['recovery_mean']} | "
        f"{book['recovery_frac_positive']} | "
        f"{book['gross_sharpe']} | {book['wealth']} | "
        f"{book['min_leg_beta']} | {book['gross_max']} |"
        for rung in payload["ladder"]
        for book in rung["books"]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: dict, json_path: str | Path | None = None,
    md_path: str | Path | None = None,
) -> tuple[Path, Path]:
    directory = _REPO_ROOT / OUTPUT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    jp = Path(json_path) if json_path is not None else directory / "breadth_ladder.json"
    mp = Path(md_path) if md_path is not None else directory / "breadth_ladder.md"
    jp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mp.write_text(render_markdown(payload), encoding="utf-8")
    return jp, mp


def main() -> None:
    started = time.perf_counter()
    payload = build_breadth_ladder()
    jp, mp = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for rung in payload["ladder"]:
        for book in rung["books"]:
            print(
                f"b={book['breadth']:2d} {book['variant']:7s} "
                f"{book['weighting']:5s} active={book['active_rows']} "
                f"recovery={book['recovery_mean']:+.6f} "
                f"min_leg_beta={book['min_leg_beta']:.4f}"
            )
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
