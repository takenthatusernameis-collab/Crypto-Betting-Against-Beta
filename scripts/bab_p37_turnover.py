#!/usr/bin/env python3
"""P37 WP2 — Turnover reduction / hysteresis guard.

Deterministic, offline runner that validates turnover reduction from a
hysteresis no-trade band against the shipped equal-weight BAB default on the
P35 wide synthetic universe (40 assets, 8 seeds).

Per seed the runner:
  1. Builds the wide synthetic universe and the equal-weight, beta-neutral,
     dollar-neutral base portfolio (shipped default, no hysteresis).
  2. Builds a hysteresis variant that suppresses trades smaller than a band
     expressed as a fraction of the average base weight. Suppression holds the
     previous weight, so turnover is non-increasing in the band width.
  3. Backtests both at a fixed transaction-cost level and compares turnover,
     costed Sharpe, and neutrality.

Emits research_state/bab_p37/turnover_summary.json
(schema: bab_p37.turnover/1). Provides --check-turnover-summary for
byte-diff verification. All data is deterministic synthetic; not real market data.
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

# Fixed transaction cost for the turnover comparison.
TRANSACTION_COSTS = 0.001

# Hysteresis band grid, expressed as a multiple of the average absolute base
# weight. 0.0 = no hysteresis (the shipped equal-weight default).
HYSTERESIS_GRID = (0.0, 1.0, 2.0, 5.0, 10.0)
HYSTERESIS_BASE_FRACTION = 1e-3

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

WEIGHT_THRESHOLD = 1e-10

SCHEMA_VERSION = "bab_p37.turnover/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p37" / "turnover_summary.json"


# --- Universe / reference (P35 wide-universe recipe) ---


def _load_btc_prices() -> pd.Series:
    df = pd.read_csv(FIXTURE_PATH, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"wide universe fixture missing BTC column: {list(df.columns)}")
    return df["BTC"].astype(float)


def _build_wide_universe_for_seed(seed: int) -> pd.DataFrame:
    """Build synthetic wide universe: asset returns = beta * BTC_return + seeded idio."""
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


def _apply_hysteresis(weights: pd.DataFrame, band_multiplier: float) -> pd.DataFrame:
    """Suppress trades smaller than a band scaled by the average base weight.

    A trade from the previously held weight to the new target is suppressed when
    its magnitude is below ``band``. Holding the previous weight (rather than
    the target) makes turnover non-increasing in the band width. The multiplier
    never amplifies a trade; band_multiplier=0.0 reproduces the base weights.
    """
    if band_multiplier <= 0.0:
        return weights.copy()

    w = weights.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    flat = w.to_numpy(dtype=float).ravel()
    flat_nz = flat[flat != 0.0]
    mean_abs = float(np.abs(flat_nz).mean()) if flat_nz.size else 0.0
    band = HYSTERESIS_BASE_FRACTION * band_multiplier * max(mean_abs, 1e-12)

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
        "wealth": float(wealth) if np.isfinite(wealth) else None,
        "sharpe": float(sharpe) if np.isfinite(sharpe) else None,
        "annualized_volatility": float(ann_vol) if np.isfinite(ann_vol) else None,
        "max_drawdown": float(max_dd) if np.isfinite(max_dd) else None,
        "total_return": float(tr) if np.isfinite(tr) else None,
        "turnover": float(turn) if np.isfinite(turn) else None,
        # Round the one library-sensitive diagnostic (strategy_beta differs by
        # ~1 ULP across numpy/pandas/scipy versions) so the committed artifact is
        # byte-reproducible on any runner. All other metrics are version-stable.
        "realized_beta": round(float(realized_beta), 12) if np.isfinite(realized_beta) else None,
        "n_periods": len(strat_returns),
    }


def _count_selected(weights: pd.DataFrame) -> int:
    w = weights.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    n_sel = (w.abs() > WEIGHT_THRESHOLD).sum(axis=1)
    return float(n_sel.mean())


# --- Per-seed runner ---


def _run_turnover_for_seed(returns_df: pd.DataFrame, seed: int, seed_idx: int) -> dict:
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

    rows = []
    for band in HYSTERESIS_GRID:
        weights = _apply_hysteresis(base, band)
        metrics = _compute_metrics(weights, valid_returns, TRANSACTION_COSTS)
        rows.append({
            "band_multiplier": float(band),
            "n_selected_avg": _count_selected(weights),
            "metrics": metrics,
        })

    # Monotonicity: turnover must be non-increasing in the band width.
    turnover_monotonic = True
    turnover_violations = []
    for i in range(1, len(rows)):
        prev_t = rows[i - 1]["metrics"]["turnover"]
        cur_t = rows[i]["metrics"]["turnover"]
        if prev_t is None or cur_t is None:
            turnover_monotonic = False
            turnover_violations.append({
                "from": rows[i - 1]["band_multiplier"],
                "to": rows[i]["band_multiplier"],
                "reason": "non-finite turnover",
            })
        elif cur_t > prev_t + 1e-12:
            turnover_monotonic = False
            turnover_violations.append({
                "from": rows[i - 1]["band_multiplier"],
                "to": rows[i]["band_multiplier"],
                "reason": "turnover increased with band width",
            })

    # Neutrality at the widest band.
    widest = rows[-1]["metrics"]
    neutrality_ok = (
        widest["realized_beta"] is not None
        and abs(widest["realized_beta"]) <= REALIZED_BETA_TOL
    )

    base_row = rows[0]["metrics"]
    reduction = None
    if base_row["turnover"] is not None and widest["turnover"] is not None:
        reduction = base_row["turnover"] - widest["turnover"]

    status = "ok" if (turnover_monotonic and neutrality_ok) else "turnover_violation"
    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "n_periods": len(valid_returns),
        "n_valid_beta_rows": len(valid_betas),
        "rows": rows,
        "turnover_monotonic": turnover_monotonic,
        "turnover_violations": turnover_violations,
        "turnover_reduction": reduction,
        "neutrality_ok": neutrality_ok,
        "status": status,
    }


def _run_all_seeds_and_configs() -> dict:
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)

        try:
            cell = _run_turnover_for_seed(returns_df, seed, seed_idx)
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
                "transaction_costs": TRANSACTION_COSTS,
                "hysteresis_grid": list(HYSTERESIS_GRID),
                "hysteresis_base_fraction": HYSTERESIS_BASE_FRACTION,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "turnover_guard": {
                "method": (
                    "hysteresis no-trade band vs the shipped equal-weight default; "
                    "turnover must be non-increasing in the band width and the "
                    "widest band must preserve neutrality"
                ),
                "monotonicity_tolerance": 1e-12,
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
        description="P37 WP2 turnover reduction / hysteresis guard"
    )
    parser.add_argument(
        "--check-turnover-summary",
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

    if args.check_turnover_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P37 WP2 turnover reduction / hysteresis guard...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Hysteresis grid: {list(HYSTERESIS_GRID)}")
    print(f"  Transaction costs: {TRANSACTION_COSTS}")
    print(f"  Beta window: {BETA_WINDOW}d")

    started = time.perf_counter()
    grid_results = _run_all_seeds_and_configs()
    summary = _build_summary_artifact(grid_results)
    write_summary(summary, args.output)
    elapsed = time.perf_counter() - started

    total_cells = len(grid_results["cells"])
    ok_cells = sum(1 for c in grid_results["cells"] if c["status"] == "ok")
    violation_cells = sum(
        1 for c in grid_results["cells"] if c["status"] == "turnover_violation"
    )
    error_cells = sum(1 for c in grid_results["cells"] if c["status"] == "error")

    print(f"Done in {elapsed:.2f}s")
    print(f"  Total seeds: {total_cells}")
    print(f"  OK: {ok_cells}")
    print(f"  Turnover violations: {violation_cells}")
    print(f"  Errors: {error_cells}")
    print(f"  Summary written to: {args.output}")

    if violation_cells > 0 or error_cells > 0:
        print("WARNING: Some cells failed turnover/neutrality checks or had errors")
        for c in grid_results["cells"]:
            if c["status"] != "ok":
                print(f"  {c['cell_key']}: {c['status']}")
                if "error" in c:
                    print(f"    Error: {c['error']}")

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
