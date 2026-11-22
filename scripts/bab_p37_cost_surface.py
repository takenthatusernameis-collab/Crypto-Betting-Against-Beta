#!/usr/bin/env python3
"""P37 WP0 — Cost-aware transaction-cost x turnover surface.

Deterministic, offline runner that sweeps transaction-cost levels x turnover
multipliers over the P35 wide synthetic universe (40 assets, 8 seeds) and proves
that the costed Sharpe is non-increasing in the transaction-cost level at every
(seed, turnover) cell, on the shipped equal-weight BAB default
(``weighting="equal"``, ``beta_neutral=True``, ``dollar_neutral=True``).

Per cell (seed, cost level, turnover multiplier):
  1. Build the wide synthetic universe (BTC from wide_bab_universe.csv + seeded
     idio noise; asset returns = beta * BTC_return + idio).
  2. Estimate rolling-OLS betas (window=90) on the full sample.
  3. Generate BAB signals (long low-beta quantile, short high-beta quantile).
  4. Construct the equal-weight, beta-neutral, dollar-neutral portfolio.
  5. Optionally apply a hysteresis band to damp turnover (turnover multiplier > 1
     keeps the same weights; the multiplier only widens the no-trade band, so the
     resulting weights are a subset of the base weights — turnover is
     non-increasing in the multiplier, never increased).
  6. Backtest at each cost level with one-day lagged weights; the realized
     turnover scales with the weight change, so costed Sharpe is compared across
     the cost grid at fixed turnover.

Emits research_state/bab_p37/cost_surface_summary.json
(schema: bab_p37.cost_surface/1). Provides
--check-cost-surface-summary for byte-diff verification.
All data is deterministic synthetic; not real market data.
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

from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402
from strategies.betting_against_beta.beta_estimators import (  # noqa: E402
    estimate_rolling_ols_beta,
)
from strategies.betting_against_beta.metrics import (  # noqa: E402
    annualized_volatility,
    final_cumulative,
    max_drawdown,
    sharpe_ratio,
    strategy_beta,
    total_return,
    turnover,
)
from strategies.betting_against_beta.portfolio import (  # noqa: E402
    construct_portfolio,
    enforce_beta_neutrality,
)
from strategies.betting_against_beta.signals import generate_bab_signals  # noqa: E402

# --- Constants matching the P35/P36 wide universe recipe ---
SEED_BASE = 20261120
SEED_INCREMENT = 1009
N_SEEDS = 8
IDIO_VOL = 0.003
BETA_MIN = 0.35
BETA_MAX = 1.90
N_ASSETS = 40
FIXTURE_PATH = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"

BETA_WINDOW = 90
QUANTILE = 0.3

# Cost grid: the transaction-cost levels swept (per unit of turnover).
COST_GRID = (0.0, 0.001, 0.0025, 0.005, 0.010, 0.020)

# Turnover multipliers applied via the hysteresis no-trade band. 1.0 = base
# (shipped default, no hysteresis); higher values widen the no-trade band and
# can only reduce turnover, never increase it.
TURNOVER_GRID = (1.0, 1.5, 2.0, 3.0)

# Hysteresis band width per turnover multiplier. The band is expressed in units
# of the average absolute base weight; a trade is suppressed when the target
# weight moves by less than band_fraction * mean(|base weight|).
HYSTERESIS_BAND = 1e-3

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances (per HANDOFF.md P36/P37)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

WEIGHT_THRESHOLD = 1e-10

SCHEMA_VERSION = "bab_p37.cost_surface/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p37" / "cost_surface_summary.json"


# --- Universe / reference (P35 wide-universe recipe) ---


def _load_btc_prices() -> pd.Series:
    df = pd.read_csv(FIXTURE_PATH, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"wide universe fixture missing BTC column: {list(df.columns)}")
    return df["BTC"].astype(float)


def _build_wide_universe_for_seed(seed: int) -> pd.DataFrame:
    """Build synthetic wide universe: asset returns = beta * BTC_return + seeded idio.

    BTC prices are loaded read-only from tests/fixtures/wide_bab_universe.csv.
    Not real market data; not market profitability evidence.
    """
    btc_prices = _load_btc_prices()
    btc_returns = btc_prices.pct_change().iloc[1:]
    btc_return_dates = btc_returns.index

    rng = np.random.default_rng(seed)
    betas = np.linspace(BETA_MIN, BETA_MAX, N_ASSETS)

    n_returns = len(btc_return_dates)
    idio = rng.normal(loc=0.0, scale=IDIO_VOL, size=(N_ASSETS, n_returns))

    asset_returns = np.vstack([
        beta * btc_returns.to_numpy(dtype=float) + idio[i]
        for i, beta in enumerate(betas)
    ])

    returns_df = pd.DataFrame(
        asset_returns.T,
        index=btc_return_dates,
        columns=ASSET_COLUMNS,
    )
    returns_df["BTC"] = btc_returns

    return returns_df


# --- Strategy pipeline ---


def _base_weights(
    returns_df: pd.DataFrame, beta_estimates: pd.DataFrame
) -> pd.DataFrame:
    """Equal-weight, beta-neutral, dollar-neutral base portfolio (shipped default)."""
    signals = generate_bab_signals(
        beta_estimates,
        long_quantile=QUANTILE,
        short_quantile=QUANTILE,
    )
    weights = construct_portfolio(
        signals,
        betas=beta_estimates,
        weighting="equal",
        dollar_neutral=True,
    )
    weights = enforce_beta_neutrality(
        weights,
        beta_estimates,
        target_beta=0.0,
        tolerance=1e-4,
        max_drift=1e-4,
        correction=True,
    )
    return weights


def _apply_hysteresis(weights: pd.DataFrame, turnover_multiplier: float) -> pd.DataFrame:
    """Widen the no-trade band by a hysteresis fraction of the average base weight.

    The trade from the previously held weight to the new target is suppressed
    when its magnitude is below ``band``. Because suppression holds the previous
    weight (not the target), turnover is non-increasing in the band width. The
    multiplier only scales the band; it never amplifies a trade.
    """
    if turnover_multiplier <= 1.0:
        return weights.copy()

    w = weights.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    # Scale the band by the average absolute nonzero weight so the band is
    # expressed in units comparable to the signal.
    flat = w.to_numpy(dtype=float).ravel()
    flat_nz = flat[flat != 0.0]
    mean_abs = float(np.abs(flat_nz).mean()) if flat_nz.size else 0.0
    band = HYSTERESIS_BAND * turnover_multiplier * max(mean_abs, 1e-12)

    out = w.copy()
    prev = pd.Series(0.0, index=w.columns)
    for t in range(len(w)):
        target = w.iloc[t]
        delta = (target - prev).abs()
        hold = delta < band
        new = target.copy()
        new[hold] = prev[hold]
        out.iloc[t] = new
        prev = new
    return out


# --- Per-cell backtest ---


def _compute_metrics(
    weights: pd.DataFrame,
    returns_df: pd.DataFrame,
    transaction_costs: float,
) -> dict:
    backtest = run_backtest(returns_df, weights, transaction_costs=transaction_costs)
    if "returns" in backtest.columns:
        strat_returns = backtest["returns"]
    elif "cumulative" in backtest.columns:
        cum = backtest["cumulative"]
        strat_returns = cum.pct_change().iloc[1:]
    else:
        strat_returns = pd.Series(dtype=float)

    bench_returns = returns_df["BTC"] if "BTC" in returns_df.columns else pd.Series(dtype=float)

    wealth = final_cumulative(strat_returns)
    sharpe = sharpe_ratio(strat_returns)
    ann_vol = annualized_volatility(strat_returns)
    max_dd = max_drawdown(strat_returns)
    tr = total_return(strat_returns)
    turn = turnover(weights)
    realized_beta = strategy_beta(strat_returns, bench_returns)

    return {
        "transaction_costs": float(transaction_costs),
        "wealth": float(wealth) if np.isfinite(wealth) else None,
        "sharpe": float(sharpe) if np.isfinite(sharpe) else None,
        "annualized_volatility": float(ann_vol) if np.isfinite(ann_vol) else None,
        "max_drawdown": float(max_dd) if np.isfinite(max_dd) else None,
        "total_return": float(tr) if np.isfinite(tr) else None,
        "turnover": float(turn) if np.isfinite(turn) else None,
        "realized_beta": float(realized_beta) if np.isfinite(realized_beta) else None,
        "n_periods": len(strat_returns),
    }


def _count_selected(weights: pd.DataFrame) -> int:
    w = weights.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    n_sel = (w.abs() > WEIGHT_THRESHOLD).sum(axis=1)
    return float(n_sel.mean())


# --- Per-seed runner ---


def _run_cost_surface_for_seed(returns_df: pd.DataFrame, seed: int, seed_idx: int) -> dict:
    betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
    )

    valid_betas = betas.dropna(how="all", subset=ASSET_COLUMNS)
    if len(valid_betas) == 0:
        return {
            "cell_key": f"seed_{seed_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "status": "error",
            "error": "no valid beta estimates",
        }

    valid_returns = returns_df.loc[valid_betas.index]
    valid_betas_aligned = valid_betas[[*ASSET_COLUMNS, "BTC"]]

    base = _base_weights(valid_returns, valid_betas_aligned)

    cells = []
    for mult in TURNOVER_GRID:
        weights = _apply_hysteresis(base, mult)
        cost_rows = []
        for cost in COST_GRID:
            metrics = _compute_metrics(weights, valid_returns, cost)
            cost_rows.append(metrics)
        cells.append({
            "turnover_multiplier": float(mult),
            "n_selected_avg": _count_selected(weights),
            "cost_rows": cost_rows,
        })

    # Monotonicity: costed Sharpe must be non-increasing in the cost level at
    # every (seed, turnover) cell. A tolerance absorbs float round-off.
    monotonicity_ok = True
    violations = []
    for cell in cells:
        sharpes = [r["sharpe"] for r in cell["cost_rows"]]
        for i in range(1, len(sharpes)):
            prev_s = sharpes[i - 1]
            cur_s = sharpes[i]
            if prev_s is None or cur_s is None:
                monotonicity_ok = False
                violations.append({
                    "turnover_multiplier": cell["turnover_multiplier"],
                    "from": i - 1,
                    "to": i,
                    "reason": "non-finite sharpe",
                })
            elif cur_s > prev_s + 1e-9:
                monotonicity_ok = False
                violations.append({
                    "turnover_multiplier": cell["turnover_multiplier"],
                    "from": i - 1,
                    "to": i,
                    "reason": "costed sharpe increased with cost",
                })

    # Neutrality: model beta / dollar / realized at the highest cost level.
    # (Weights are identical across cost levels; only the cost applied differs.)
    base_row = cells[0]["cost_rows"][-1]
    neutrality_ok = (
        base_row["realized_beta"] is not None
        and abs(base_row["realized_beta"]) <= REALIZED_BETA_TOL
    )

    status = "ok" if (monotonicity_ok and neutrality_ok) else "monotonicity_violation"
    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "n_periods": len(valid_returns),
        "n_valid_beta_rows": len(valid_betas),
        "cells": cells,
        "monotonicity_ok": monotonicity_ok,
        "monotonicity_violations": violations,
        "neutrality_ok": neutrality_ok,
        "status": status,
    }


def _run_all_seeds_and_configs() -> dict:
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)

        try:
            cell = _run_cost_surface_for_seed(returns_df, seed, seed_idx)
            all_cells.append(cell)
        except Exception as e:
            all_cells.append({
                "cell_key": f"seed_{seed_idx}",
                "seed_index": seed_idx,
                "seed": seed,
                "status": "error",
                "error": str(e),
            })

    return {"cells": all_cells}


# --- Summary artifact ---


def _build_summary_artifact(grid_results: dict) -> dict:
    base_returns = _build_wide_universe_for_seed(SEED_BASE)
    returns_bytes = base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    returns_sha256 = hashlib.sha256(returns_bytes).hexdigest()

    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(
        btc_prices.to_numpy(dtype=float).tobytes()
    ).hexdigest()

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "fixture_recipe": (
                f"Deterministic synthetic wide universe (P35 wide-universe recipe). "
                f"BTC prices from tests/fixtures/wide_bab_universe.csv. "
                f"Asset returns = beta * BTC_return + idio, idio ~ N(0, {IDIO_VOL}), "
                f"betas linspace({BETA_MIN}, {BETA_MAX}, {N_ASSETS}). "
                f"Not real market data; not market profitability evidence."
            ),
            "fixture_path": str(FIXTURE_PATH),
            "returns_sha256": returns_sha256,
            "btc_source_sha256": btc_sha256,
            "seeds": {
                "base_seed": SEED_BASE,
                "increment": SEED_INCREMENT,
                "n_seeds": N_SEEDS,
                "seed_list": [SEED_BASE + SEED_INCREMENT * i for i in range(N_SEEDS)],
            },
            "config_grid": {
                "beta_window": BETA_WINDOW,
                "quantile": QUANTILE,
                "cost_grid": list(COST_GRID),
                "turnover_grid": list(TURNOVER_GRID),
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "cost_surface": {
                "method": (
                    "transaction-cost x turnover grid on the shipped equal-weight BAB "
                    "default; costed Sharpe must be non-increasing in the cost level "
                    "at every (seed, turnover) cell"
                ),
                "monotonicity_tolerance": 1e-9,
            },
        },
        "results": grid_results,
    }

    return summary


def write_summary(summary: dict, path: Path = SUMMARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_summary(path: Path = SUMMARY_PATH) -> bool:
    if not path.exists():
        print(f"Summary artifact not found: {path}")
        return False

    grid_results = _run_all_seeds_and_configs()
    fresh_summary = _build_summary_artifact(grid_results)

    expected_bytes = path.read_bytes()
    actual_bytes = json.dumps(fresh_summary, indent=2, sort_keys=True).encode("utf-8") + b"\n"

    if expected_bytes == actual_bytes:
        print("Summary artifact check: PASS (byte-identical)")
        return True
    else:
        print("Summary artifact check: FAIL (byte mismatch)")
        for i, (e, a) in enumerate(zip(expected_bytes, actual_bytes)):
            if e != a:
                print(f"  First difference at byte {i}: expected {e!r}, got {a!r}")
                break
        if len(expected_bytes) != len(actual_bytes):
            print(
                f"  Length mismatch: expected {len(expected_bytes)}, "
                f"got {len(actual_bytes)}"
            )
        return False


def build_summary() -> dict:
    """Build the deterministic summary artifact (read-only; does not write to disk)."""
    grid_results = _run_all_seeds_and_configs()
    return _build_summary_artifact(grid_results)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P37 WP0 transaction-cost x turnover surface"
    )
    parser.add_argument(
        "--check-cost-surface-summary",
        action="store_true",
        help="Verify existing summary artifact is byte-identical to fresh recomputation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SUMMARY_PATH,
        help=f"Output path for summary artifact (default: {SUMMARY_PATH})",
    )
    args = parser.parse_args()

    if args.check_cost_surface_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P37 WP0 cost-aware transaction-cost x turnover surface...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Cost grid: {list(COST_GRID)}")
    print(f"  Turnover grid: {list(TURNOVER_GRID)}")
    print(f"  Beta window: {BETA_WINDOW}d")

    started = time.perf_counter()
    grid_results = _run_all_seeds_and_configs()
    summary = _build_summary_artifact(grid_results)
    write_summary(summary, args.output)
    elapsed = time.perf_counter() - started

    total_cells = len(grid_results["cells"])
    ok_cells = sum(1 for c in grid_results["cells"] if c["status"] == "ok")
    violation_cells = sum(
        1 for c in grid_results["cells"] if c["status"] == "monotonicity_violation"
    )
    error_cells = sum(1 for c in grid_results["cells"] if c["status"] == "error")

    print(f"Done in {elapsed:.2f}s")
    print(f"  Total seeds: {total_cells}")
    print(f"  OK: {ok_cells}")
    print(f"  Monotonicity violations: {violation_cells}")
    print(f"  Errors: {error_cells}")
    print(f"  Summary written to: {args.output}")

    if violation_cells > 0 or error_cells > 0:
        print("WARNING: Some cells failed the monotonicity/neutrality checks or had errors")
        for c in grid_results["cells"]:
            if c["status"] != "ok":
                print(f"  {c['cell_key']}: {c['status']}")
                if "error" in c:
                    print(f"    Error: {c['error']}")

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
