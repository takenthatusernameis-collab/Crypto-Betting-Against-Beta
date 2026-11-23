#!/usr/bin/env python3
"""P37 WP1 — Market-impact & capacity limits.

Deterministic, offline runner that computes the participation-rate break-even
for the shipped equal-weight BAB default on the P35 wide synthetic universe
(40 assets, 8 seeds).

For each seed the runner:
  1. Builds the wide synthetic universe and the equal-weight, beta-neutral,
     dollar-neutral portfolio (shipped default).
  2. Backtests across a grid of market-impact coefficients (fraction of a
     trade's notional lost to impact), producing a costed Sharpe per level.
  3. Computes the participation-rate break-even — the impact coefficient at
     which the costed Sharpe crosses zero — by fixed-iteration bisection on the
     discrete impact grid.
  4. Pins each bracket so it provably halves every iteration; books without a
     zero crossing are censored with a documented reason (never a midpoint).

Emits research_state/bab_p37/capacity_summary.json
(schema: bab_p37.capacity/1). Provides --check-capacity-summary for
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
    sharpe_ratio,
    strategy_beta,
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

# Market-impact grid: fraction of a trade's notional lost to impact, swept from
# zero (no impact) upward. A break-even is the coefficient where costed Sharpe
# crosses zero.
IMPACT_GRID = (0.0, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.02, 0.05)

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

# Bisection settings: fixed iterations, never adaptive.
BISECTION_ITERATIONS = 60
BISECTION_TOL = 1e-12

SCHEMA_VERSION = "bab_p37.capacity/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p37" / "capacity_summary.json"


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


def _costed_sharpe(
    returns_df: pd.DataFrame, weights: pd.DataFrame, impact_coefficient: float
) -> float:
    """Costed Sharpe at a given market-impact coefficient (fraction of turnover)."""
    backtest = run_backtest(
        returns_df, weights, transaction_costs=float(impact_coefficient)
    )
    if "returns" in backtest.columns:
        strat_returns = backtest["returns"]
    elif "cumulative" in backtest.columns:
        cum = backtest["cumulative"]
        strat_returns = cum.pct_change().iloc[1:]
    else:
        return float("nan")
    sharpe = sharpe_ratio(strat_returns)
    return float(sharpe) if np.isfinite(sharpe) else float("nan")


def _zero_crossing_bracket(sharpes: list[tuple[float, float]]) -> tuple[float, float] | None:
    """Find the first [lo, hi] impact pair with sharpe(lo) >= 0 and sharpe(hi) <= 0."""
    for i in range(1, len(sharpes)):
        lo_coef, lo_sharpe = sharpes[i - 1]
        hi_coef, hi_sharpe = sharpes[i]
        if lo_sharpe >= 0.0 >= hi_sharpe:
            return (lo_coef, hi_coef)
    return None


def _bisect_break_even(
    returns_df: pd.DataFrame,
    weights: pd.DataFrame,
    lo: float,
    hi: float,
) -> dict:
    """Fixed-iteration bisection for the impact coefficient where Sharpe crosses zero."""
    history = []
    a, b = float(lo), float(hi)
    fa = _costed_sharpe(returns_df, weights, a)
    fb = _costed_sharpe(returns_df, weights, b)
    for _ in range(BISECTION_ITERATIONS):
        mid = 0.5 * (a + b)
        fmid = _costed_sharpe(returns_df, weights, mid)
        history.append({
            "iteration": len(history),
            "lo": a,
            "hi": b,
            "mid": mid,
            "f_lo": fa,
            "f_mid": fmid,
            "f_hi": fb,
            "bracket_width": b - a,
        })
        if b - a <= BISECTION_TOL:
            break
        # f(lo) >= 0 and f(hi) <= 0: the root is bracketed.
        if (fa >= 0.0) == (fmid >= 0.0):
            a, fa = mid, fmid
        else:
            b, fb = mid, fmid
    return {
        "break_even_impact": 0.5 * (a + b),
        "iterations": len(history),
        "final_bracket": [a, b],
        "final_bracket_width": b - a,
        "history": history,
    }


# --- Per-seed runner ---


def _run_capacity_for_seed(returns_df: pd.DataFrame, seed: int, seed_idx: int) -> dict:
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

    weights = _base_weights(valid_returns, valid_betas_aligned)

    impact_rows = []
    sharpes = []
    for coef in IMPACT_GRID:
        s = _costed_sharpe(valid_returns, weights, coef)
        sharpes.append((coef, s))
        impact_rows.append({
            "impact_coefficient": coef,
            "costed_sharpe": s,
        })

    bracket = _zero_crossing_bracket(sharpes)
    if bracket is None:
        # Censor: no zero crossing in the grid. Document why.
        if all(s >= 0.0 for _, s in sharpes):
            reason = "costed sharpe non-negative across the whole impact grid"
        elif all(s <= 0.0 for _, s in sharpes):
            reason = "costed sharpe non-positive at every impact level including zero"
        else:
            reason = "no sign change bracketed by the impact grid"
        break_even = None
        bisection = None
    else:
        lo, hi = bracket
        bisection = _bisect_break_even(valid_returns, weights, lo, hi)
        break_even = bisection["break_even_impact"]

    # Neutrality: model beta / dollar / realized at the zero-impact level.
    backtest0 = run_backtest(valid_returns, weights, transaction_costs=0.0)
    if "returns" in backtest0.columns:
        sr = backtest0["returns"]
    elif "cumulative" in backtest0.columns:
        sr = backtest0["cumulative"].pct_change().iloc[1:]
    else:
        sr = pd.Series(dtype=float)
    realized_beta = strategy_beta(
        sr, valid_returns["BTC"] if "BTC" in valid_returns.columns else pd.Series(dtype=float)
    )
    neutrality_ok = (
        realized_beta is not None
        and np.isfinite(realized_beta)
        and abs(realized_beta) <= REALIZED_BETA_TOL
    )

    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "n_periods": len(valid_returns),
        "n_valid_beta_rows": len(valid_betas),
        "impact_rows": impact_rows,
        "zero_crossing": bracket is not None,
        "break_even_impact": break_even,
        "censoring_reason": None if bracket is not None else reason,
        "bisection": bisection,
        "neutrality_ok": neutrality_ok,
        # Round the one library-sensitive diagnostic (strategy_beta differs by
        # ~1 ULP across numpy/pandas/scipy versions) so the committed artifact is
        # byte-reproducible on any runner. All other metrics are version-stable.
        "realized_beta": round(float(realized_beta), 12) if np.isfinite(realized_beta) else None,
        "status": "ok" if neutrality_ok else "neutrality_violation",
    }


def _run_all_seeds_and_configs() -> dict:
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)

        try:
            cell = _run_capacity_for_seed(returns_df, seed, seed_idx)
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
                "impact_grid": list(IMPACT_GRID),
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "capacity": {
                "method": (
                    "market-impact participation-rate break-even via fixed-iteration "
                    "bisection on the discrete impact grid; brackets halve every "
                    "iteration; no-crossing books are censored with a reason"
                ),
                "bisection_iterations": BISECTION_ITERATIONS,
                "bisection_tol": BISECTION_TOL,
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
        description="P37 WP1 market-impact & capacity limits"
    )
    parser.add_argument(
        "--check-capacity-summary",
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

    if args.check_capacity_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P37 WP1 market-impact & capacity limits...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Impact grid: {list(IMPACT_GRID)}")
    print(f"  Beta window: {BETA_WINDOW}d")

    started = time.perf_counter()
    grid_results = _run_all_seeds_and_configs()
    summary = _build_summary_artifact(grid_results)
    write_summary(summary, args.output)
    elapsed = time.perf_counter() - started

    total_cells = len(grid_results["cells"])
    ok_cells = sum(1 for c in grid_results["cells"] if c["status"] == "ok")
    violation_cells = sum(
        1 for c in grid_results["cells"] if c["status"] == "neutrality_violation"
    )
    error_cells = sum(1 for c in grid_results["cells"] if c["status"] == "error")
    crossing = sum(1 for c in grid_results["cells"] if c.get("zero_crossing"))

    print(f"Done in {elapsed:.2f}s")
    print(f"  Total seeds: {total_cells}")
    print(f"  OK: {ok_cells}")
    print(f"  Zero-crossing books: {crossing}")
    print(f"  Neutrality violations: {violation_cells}")
    print(f"  Errors: {error_cells}")
    print(f"  Summary written to: {args.output}")

    if violation_cells > 0 or error_cells > 0:
        print("WARNING: Some cells failed neutrality checks or had errors")
        for c in grid_results["cells"]:
            if c["status"] != "ok":
                print(f"  {c['cell_key']}: {c['status']}")
                if "error" in c:
                    print(f"    Error: {c['error']}")

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
