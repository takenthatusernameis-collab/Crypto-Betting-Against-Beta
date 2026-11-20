#!/usr/bin/env python3
"""P24 WP1 — regime-split stress on the committed P21 universe.

Reads ``research_state/bab_p21/universe.json``,
``research_state/bab_p23/charter.json`` and
``research_state/bab_p21/rank_eval.json`` read-only. For each chartered
``regime_grid`` entry (``calm``, ``stress``) it splits the panel using the
volatility-percentile regime classifier (causal, no lookahead), runs the
shipped ``BABStrategy`` on the regime-restricted rows, and publishes recovery,
Sharpe and beta-exposure statistics. A ``regime_zero_reference`` block pins
the full-panel recovery to the committed P21 ``rank_eval.json``.

Regime rule (deterministic, causal): realised volatility is computed with a
20-day rolling window on the benchmark (BTC). The ``calm`` regime is the
bottom tertile of rolling volatility; the ``stress`` regime is the top tertile.
Rows in the middle tertile are excluded from both regimes so the two books are
disjoint. The regime at date ``t`` uses only data up to and including ``t``,
so applying it to weights at ``t`` (which are applied to returns at ``t+1`` by
the backtest) introduces no lookahead.

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
from strategies.betting_against_beta.regime import calculate_realized_volatility  # noqa: E402

SCHEMA = "bab_p24.regime_split/1"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
CHARTER_PATH = "research_state/bab_p24/charter.json"
P21_RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
OUTPUT_DIR = "research_state/bab_p24"
DECIMALS = 6
DEGENERATE_TOL = 1e-12
TRADING_DAYS = 252
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
REGIMES = ("calm", "stress")
VOL_WINDOW = 20
VOL_PERCENTILES = (1.0 / 3.0, 2.0 / 3.0)


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


def regime_mask(
    returns: pd.DataFrame,
    benchmark: str,
    regime: str,
    vol_window: int = VOL_WINDOW,
    percentiles: tuple = VOL_PERCENTILES,
) -> pd.Series:
    """Return a boolean mask for ``regime`` using rolling benchmark volatility.

    The regime at date ``t`` uses only data up to and including ``t`` (causal).
    ``calm`` = bottom tertile, ``stress`` = top tertile. Middle tertile is
    excluded (returns False).
    """
    if benchmark not in returns.columns:
        raise ValueError(f"Benchmark {benchmark!r} not in returns columns")
    bench_ret = returns[benchmark]
    vol = calculate_realized_volatility(
        bench_ret.to_frame(), window=vol_window, use_ewma=False
    )[benchmark]
    vol = vol.ffill().fillna(0.0)

    q_low = vol.rolling(window=max(vol_window * 2, 50), min_periods=vol_window).quantile(
        percentiles[0]
    )
    q_high = vol.rolling(window=max(vol_window * 2, 50), min_periods=vol_window).quantile(
        percentiles[1]
    )

    if regime == "calm":
        mask = vol <= q_low
    elif regime == "stress":
        mask = vol >= q_high
    else:
        raise ValueError(f"Unknown regime: {regime!r}")
    mask = mask.fillna(False)
    mask.name = f"regime_{regime}"
    return mask


def _baseline_book(
    frame: pd.DataFrame,
    weighting: str,
    assets: list[str],
    config: dict,
) -> dict:
    """Run the shipped strategy once for the full-panel book (regime=none)."""
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
    baseline_pnl = result.backtest["returns"].to_numpy(dtype=float)
    return {
        "weights": weights,
        "index": result.weights.index,
        "columns": columns,
        "active": active,
        "baseline_pnl": baseline_pnl,
    }


def _cell_statistics(
    universe: dict,
    frame: pd.DataFrame,
    baseline: dict,
    variant: str,
    weighting: str,
    regime: str,
    regime_mask_series: pd.Series,
    config: dict,
    assets: list[str],
    full_recovery: float,
) -> dict:
    """Collect statistics for one (regime, weighting, variant).

    Every boolean field is recomputed from this cell's own measured numbers;
    none is asserted by hand. ``recovery_retention`` is the regime-restricted
    recovery over the same book's full-panel recovery, i.e. the measured
    regime degradation.
    """
    alpha = np.array([float(universe["alphas"][variant][a]) for a in assets])
    betas = np.array([float(universe["betas"][a]) for a in assets])
    baseline_weights = baseline["weights"]
    columns = baseline["columns"]

    # Align regime mask to the weights index
    aligned_mask = regime_mask_series.reindex(baseline["index"]).fillna(False)

    # Restrict weights to regime rows
    restricted = baseline_weights.copy()
    restricted[~aligned_mask.to_numpy(), :] = 0.0

    gross = np.abs(restricted).sum(axis=1)
    active = gross > DEGENERATE_TOL
    n_active = int(active.sum())
    n_total = len(restricted)

    # Recovery: w_bar @ alpha over active rows
    if active.any():
        w_bar = restricted[active][:, 1:].mean(axis=0)
        recovery = float(w_bar @ alpha)
    else:
        recovery = 0.0

    # Sharpe on regime-restricted book
    from strategies.betting_against_beta.backtest import run_backtest
    weights_df = pd.DataFrame(restricted, index=baseline["index"], columns=columns)
    restricted_backtest = run_backtest(
        frame[columns], weights_df, transaction_costs=0.0
    )
    regime_pnl = restricted_backtest["returns"].to_numpy(dtype=float)
    sharpe = 0.0
    std = float(regime_pnl.std(ddof=1))
    if std > 0.0:
        sharpe = float(regime_pnl.mean() / std * np.sqrt(TRADING_DAYS))

    # Beta exposure of the regime-restricted book
    beta_exposure = 0.0
    if active.any():
        w_active = restricted[active][:, 1:]
        beta_exposure = float(np.abs(w_active @ betas).mean())

    # Min leg beta and gross max (for rank)
    min_leg_beta = 0.0
    gross_max = 0.0
    if weighting == "rank" and active.any():
        w_active = restricted[active][:, 1:]
        gross_max = float(np.abs(w_active).sum(axis=1).max())
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

    recovery_positive = recovery > 0.0
    # Retention is derived from the *published* 6 dp numbers so any reader can
    # recompute it from the artifact alone.
    recovery_retention = 0.0
    if _clean(full_recovery) != 0.0:
        recovery_retention = _clean(recovery) / _clean(full_recovery)

    return {
        "regime": regime,
        "weighting": weighting,
        "variant": variant,
        "recovery": _clean(recovery),
        "recovery_full_panel": _clean(full_recovery),
        "recovery_retention": _clean(recovery_retention),
        "recovery_positive": recovery_positive,
        "recovery_exactly_zero": recovery == 0.0,
        "sharpe": _clean(sharpe),
        "beta_exposure": _clean(beta_exposure),
        "regime_rows": int(aligned_mask.sum()),
        "active_rows": n_active,
        "total_rows": n_total,
        "active_fraction": _clean(n_active / n_total if n_total > 0 else 0.0),
        "min_leg_beta": _clean(min_leg_beta),
        "gross_max": _clean(gross_max),
        "rank_min_leg_beta_floor": _clean(
            config["rank_min_leg_beta"] if weighting == "rank" else 0.0
        ),
        "rank_max_gross_ceiling": _clean(
            config["rank_max_gross"] if weighting == "rank" else 0.0
        ),
    }


def build_regime_split(
    universe: dict | None = None,
    charter_p24: dict | None = None,
    charter_p23: dict | None = None,
) -> dict:
    """Build the regime-split stress payload (reads committed JSON only)."""
    universe = load_json(UNIVERSE_PATH) if universe is None else universe
    charter_p24 = load_json(CHARTER_PATH) if charter_p24 is None else charter_p24
    if charter_p23 is None:
        charter_p23 = load_json("research_state/bab_p23/charter.json")
    p21_rank_eval = load_json(P21_RANK_EVAL_PATH)

    config = charter_p23["provenance"]["strategy_config"]
    assets = list(universe["assets"])
    regimes = list(charter_p24["charter"]["regime_grid"])

    frames = {variant: returns_frame(universe, variant) for variant in VARIANTS}
    baselines = {
        (variant, weighting): _baseline_book(
            frames[variant], weighting, assets, config
        )
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    }

    # Full-panel recovery per book: the regime zero reference and the
    # denominator of every cell's measured retention.
    full_recoveries = {}
    for variant in VARIANTS:
        alpha = np.array([float(universe["alphas"][variant][a]) for a in assets])
        for weighting in WEIGHTINGS:
            baseline = baselines[(variant, weighting)]
            active = baseline["active"]
            if active.any():
                w_bar = baseline["weights"][active][:, 1:].mean(axis=0)
                full_recoveries[(variant, weighting)] = float(w_bar @ alpha)
            else:
                full_recoveries[(variant, weighting)] = 0.0

    benchmark = config["benchmark"]
    masks = {regime: regime_mask(frames["planted"], benchmark, regime) for regime in regimes}
    for variant in VARIANTS:
        for regime in regimes:
            assert masks[regime].equals(
                regime_mask(frames[variant], benchmark, regime)
            ), "regime mask must not depend on the alpha variant"
    reference_index = baselines[("planted", "rank")]["index"]
    aligned = {r: masks[r].reindex(reference_index).fillna(False) for r in regimes}
    total_rows = len(reference_index)
    rows_by_regime = {r: int(aligned[r].sum()) for r in regimes}
    overlap_rows = int((aligned[regimes[0]] & aligned[regimes[1]]).sum())
    union_rows = int((aligned[regimes[0]] | aligned[regimes[1]]).sum())

    cells = []
    for variant in VARIANTS:
        frame = frames[variant]
        for regime in regimes:
            mask = masks[regime]
            for weighting in WEIGHTINGS:
                baseline = baselines[(variant, weighting)]
                cells.append(
                    _cell_statistics(
                        universe,
                        frame,
                        baseline,
                        variant,
                        weighting,
                        regime,
                        mask,
                        config,
                        assets,
                        full_recoveries[(variant, weighting)],
                    )
                )

    # Zero-reference: full-panel recovery matches P21 rank_eval at 6dp
    p21_books = {(b["variant"], b["weighting"]): b for b in p21_rank_eval["books"]}
    regime_zero_reference = {"checks": {}}
    for variant in VARIANTS:
        for weighting in WEIGHTINGS:
            key_str = f"{variant}_{weighting}"
            committed = _clean(p21_books[(variant, weighting)]["recovery_mean"])
            measured = _clean(full_recoveries[(variant, weighting)])
            regime_zero_reference["checks"][key_str] = {
                "committed_p21_recovery": committed,
                "regime_zero_recovery": measured,
                "matches_at_6dp": measured == committed,
            }

    # Every acceptance threshold is computed from the measured artifact, never
    # asserted by hand.
    zero_checks = regime_zero_reference["checks"].values()
    planted_cells = [c for c in cells if c["variant"] == "planted"]
    null_cells = [c for c in cells if c["variant"] == "null"]
    acceptance_thresholds = {
        "regime_zero_matches_p21_at_6dp": all(v["matches_at_6dp"] for v in zero_checks),
        "calm_and_stress_disjoint": overlap_rows == 0,
        "every_regime_non_empty": all(rows_by_regime[r] > 0 for r in regimes),
        "planted_recovery_strictly_positive_in_at_least_one_regime": all(
            any(
                c["recovery_positive"]
                for c in planted_cells
                if c["weighting"] == weighting
            )
            for weighting in WEIGHTINGS
        ),
        "every_planted_regime_cell_positive": all(
            c["recovery_positive"] for c in planted_cells
        ),
        "null_recovery_exactly_zero_everywhere": all(
            c["recovery_exactly_zero"] for c in null_cells
        ),
    }

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
            "charter_path": CHARTER_PATH,
            "charter_schema": charter_p24["schema"],
            "panel_sha256": {
                variant: universe["panels"][variant]["sha256"] for variant in VARIANTS
            },
            "regime_grid": regimes,
            "vol_window": VOL_WINDOW,
            "vol_percentiles": list(VOL_PERCENTILES),
            "regime_rule": (
                f"benchmark rolling vol (window={VOL_WINDOW}) percentile split; "
                f"calm <= {VOL_PERCENTILES[0]:.3f} quantile, "
                f"stress >= {VOL_PERCENTILES[1]:.3f} quantile; "
                f"middle excluded; causal (no lookahead)"
            ),
            "config": config,
            "regime_coverage": {
                "total_rows": total_rows,
                "rows_by_regime": rows_by_regime,
                "overlap_rows": overlap_rows,
                "union_rows": union_rows,
                "unclassified_rows": total_rows - union_rows,
            },
            "acceptance_thresholds": acceptance_thresholds,
            "regime_zero_reference": regime_zero_reference,
            "derived": {
                "n_cells": len(cells),
                "n_regimes": len(regimes),
                "n_weightings": len(WEIGHTINGS),
                "n_variants": len(VARIANTS),
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
        f"Universe seed {prov['universe_seed']}; charter schema "
        f"`{prov['charter_schema']}`; regimes {prov['regime_grid']}.",
        f"Regime rule: {prov['regime_rule']}.",
        "",
        "| regime | weighting | variant | recovery | full_panel | retention | "
        "sharpe | beta_exposure | regime_rows | active_rows | total_rows | "
        "active_frac | min_leg_beta | gross_max |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {cell['regime']} | {cell['weighting']} | {cell['variant']} | "
        f"{cell['recovery']} | {cell['recovery_full_panel']} | "
        f"{cell['recovery_retention']} | "
        f"{cell['sharpe']} | {cell['beta_exposure']} | "
        f"{cell['regime_rows']} | {cell['active_rows']} | {cell['total_rows']} | "
        f"{cell['active_fraction']} | {cell['min_leg_beta']} | {cell['gross_max']} |"
        for cell in payload["cells"]
    )
    lines.append("")
    coverage = prov["regime_coverage"]
    lines.append(
        f"Regime coverage: {coverage['total_rows']} rows; "
        f"{coverage['rows_by_regime']} classified; "
        f"{coverage['overlap_rows']} overlapping; "
        f"{coverage['unclassified_rows']} middle/unclassified."
    )
    lines.append("")
    lines.append("## Regime zero-reference (full panel, matches P21 at 6 dp)")
    lines.append("")
    header = (
        "| variant | weighting | committed_p21_recovery | "
        "regime_zero_recovery | matches_at_6dp |"
    )
    lines.append(header)
    lines.append("|---|---|---|---|---|")
    for key, vals in prov["regime_zero_reference"]["checks"].items():
        variant, weighting = key.split("_")
        lines.append(
            f"| {variant} | {weighting} | "
            f"{vals['committed_p21_recovery']} | {vals['regime_zero_recovery']} | "
            f"{vals['matches_at_6dp']} |"
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
            f"regime={cell['regime']:5s} {cell['weighting']:5s} "
            f"{cell['variant']:7s} recovery={cell['recovery']:+.6f} "
            f"sharpe={cell['sharpe']:+.3f} "
            f"active={cell['active_rows']}/{cell['total_rows']} "
            f"beta_exp={cell['beta_exposure']:.4f}"
        )
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
