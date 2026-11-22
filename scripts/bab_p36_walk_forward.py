#!/usr/bin/env python3
"""P36 WP0 — Walk-Forward / Out-of-Sample Validation on the P35 Wide-Universe Fixture.

Deterministic, offline walk-forward harness that validates whether the BAB
beta signal persists out of sample.

Per cell (seed × rebalance window):
  1. Train: estimate rolling-OLS betas on the IS window (90 days).
  2. Construct equal-weight, beta-neutral, dollar-neutral portfolio from IS betas.
  3. Test: apply lagged weights to the OOS test window (30 days).
  4. Record: OOS Sharpe, OOS realized beta, OOS turnover, OOS wealth,
     neutrality invariants, walk-forward stability (Spearman of IS vs OOS beta ranks).

Rolling rebalance windows: default 90-day train, 30-day test, step 30.
One-day lagged weights (no lookahead) via run_backtest. Optional transaction costs.

Emits research_state/bab_p36/walk_forward_summary.json (schema: bab_p36.walk_forward/1).
Provides --check-walk-forward-summary for byte-diff verification.
All data is deterministic synthetic (P35 wide-universe recipe); not real market data.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

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

# --- Constants matching P34/P35 wide universe recipe ---
SEED_BASE = 20261120
SEED_INCREMENT = 1009
N_SEEDS = 8
IDIO_VOL = 0.003
BETA_MIN = 0.35
BETA_MAX = 1.90
N_ASSETS = 40
NAN_COLUMN = "DEL"
FIXTURE_PATH = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"

# Walk-forward window config
TRAIN_WINDOW = 90
TEST_WINDOW = 30
STEP = 30
BETA_WINDOW = 90
QUANTILE = 0.3
TRANSACTION_COSTS = 0.001

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances (per HANDOFF.md P36)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

WEIGHT_THRESHOLD = 1e-10

SCHEMA_VERSION = "bab_p36.walk_forward/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p36" / "walk_forward_summary.json"


# --- Window generation ---


def _walk_forward_windows(n_periods: int, train_window: int, test_window: int, step: int) -> list[tuple[int, int, int, int]]:
    """Yield (train_start, train_end, test_start, test_end) integer-location tuples."""
    windows = []
    start = 0
    while start + train_window + test_window <= n_periods:
        windows.append((start, start + train_window, start + train_window, start + train_window + test_window))
        start += step
    return windows


# --- Universe / reference (P35 wide-universe recipe, BTC from wide_bab_universe.csv) ---


def _load_btc_prices() -> pd.Series:
    df = pd.read_csv(FIXTURE_PATH, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"wide universe fixture missing BTC column: {list(df.columns)}")
    return df["BTC"].astype(float)


def _build_wide_universe_for_seed(seed: int) -> pd.DataFrame:
    """Build synthetic wide universe: asset returns = beta * BTC_return + seeded idio.

    BTC prices are loaded read-only from tests/fixtures/wide_bab_universe.csv.
    Asset returns are synthetic: beta * BTC_return + idio, idio ~ N(0, IDIO_VOL).
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


# --- Strategy pipeline (mirrors P35 _run_strategy_with_betas) ---


def _run_strategy_with_betas(
    returns_df: pd.DataFrame,
    beta_estimates: pd.DataFrame,
    quantile: float = QUANTILE,
    transaction_costs: float = TRANSACTION_COSTS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    signals = generate_bab_signals(
        beta_estimates,
        long_quantile=quantile,
        short_quantile=quantile,
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
    backtest = run_backtest(
        returns_df,
        weights,
        transaction_costs=transaction_costs,
    )
    return weights, returns_df, backtest


def _compute_model_beta_neutrality(weights: pd.DataFrame, betas: pd.DataFrame) -> pd.Series:
    common_idx = weights.index.intersection(betas.index)
    common_cols = weights.columns.intersection(betas.columns)
    if len(common_idx) == 0 or len(common_cols) == 0:
        return pd.Series(index=weights.index, dtype=float)

    w = weights.loc[common_idx, common_cols].astype(float).replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0)
    b = betas.loc[common_idx, common_cols].astype(float).replace(
        [np.inf, -np.inf], np.nan
    )

    wv = w.to_numpy(dtype=float)
    bv = b.to_numpy(dtype=float)
    finite = np.isfinite(bv)
    wv = np.where(finite, wv, 0.0)
    bv = np.where(finite, bv, 0.0)

    gross = np.abs(wv).sum(axis=1)
    pb = np.full(len(common_idx), np.nan)
    mask = gross > 1e-18
    if mask.any():
        pb[mask] = (wv[mask] * bv[mask]).sum(axis=1) / gross[mask]

    return pd.Series(pb, index=common_idx).reindex(weights.index)


def _compute_dollar_neutrality(weights: pd.DataFrame) -> pd.Series:
    return weights.sum(axis=1)


def _compute_oos_metrics(
    weights: pd.DataFrame,
    betas: pd.DataFrame,
    oos_returns: pd.DataFrame,
    backtest: pd.DataFrame,
) -> dict:
    if "returns" in backtest.columns:
        strat_returns = backtest["returns"]
    else:
        if "cumulative" in backtest.columns:
            cum = backtest["cumulative"]
            strat_returns = cum.pct_change().iloc[1:]
        else:
            strat_returns = pd.Series(dtype=float)

    bench_returns = oos_returns["BTC"] if "BTC" in oos_returns.columns else pd.Series(dtype=float)

    model_beta_series = _compute_model_beta_neutrality(weights, betas)
    max_model_beta = (
        float(model_beta_series.abs().max()) if len(model_beta_series) > 0 else np.nan
    )

    dollar_neutral_series = _compute_dollar_neutrality(weights)
    max_dollar_neutral = (
        float(dollar_neutral_series.abs().max()) if len(dollar_neutral_series) > 0 else np.nan
    )

    realized_beta = strategy_beta(strat_returns, bench_returns)

    wealth = final_cumulative(strat_returns)
    sharpe = sharpe_ratio(strat_returns)
    ann_vol = annualized_volatility(strat_returns)
    max_dd = max_drawdown(strat_returns)
    tr = total_return(strat_returns)
    turn = turnover(weights)

    return {
        "wealth": float(wealth) if np.isfinite(wealth) else None,
        "sharpe": float(sharpe) if np.isfinite(sharpe) else None,
        "annualized_volatility": float(ann_vol) if np.isfinite(ann_vol) else None,
        "max_drawdown": float(max_dd) if np.isfinite(max_dd) else None,
        "total_return": float(tr) if np.isfinite(tr) else None,
        "turnover": float(turn) if np.isfinite(turn) else None,
        "max_model_beta": float(max_model_beta) if np.isfinite(max_model_beta) else None,
        "max_dollar_neutral": (
            float(max_dollar_neutral) if np.isfinite(max_dollar_neutral) else None
        ),
        "realized_beta": float(realized_beta) if np.isfinite(realized_beta) else None,
        "n_periods": len(strat_returns),
    }


def _ols_beta_per_asset(oos_returns: pd.DataFrame, bench_col: str = "BTC") -> pd.Series:
    """Simple OLS beta of each asset vs benchmark over the full OOS period."""
    bench = oos_returns[bench_col] if bench_col in oos_returns.columns else pd.Series(dtype=float)
    betas_out = {}
    for col in oos_returns.columns:
        if col == bench_col or col == NAN_COLUMN:
            continue
        df = pd.DataFrame({"asset": oos_returns[col], "bench": bench}).dropna()
        if len(df) < 2:
            betas_out[col] = np.nan
            continue
        cov = df["asset"].cov(df["bench"])
        var_bench = df["bench"].var(ddof=1)
        if var_bench is None or np.isnan(var_bench) or var_bench < 1e-18:
            betas_out[col] = np.nan
            continue
        betas_out[col] = float(cov / var_bench)
    return pd.Series(betas_out)


# --- Per-seed walk-forward runner ---


def _run_walk_forward_for_seed(returns_df: pd.DataFrame, seed: int, seed_idx: int) -> list[dict]:
    """Run walk-forward windows for one seed.

    Returns a list of cell dicts, one per (train, test) window pair.
    """
    cells = []
    n_periods = len(returns_df)
    windows = _walk_forward_windows(n_periods, TRAIN_WINDOW, TEST_WINDOW, STEP)

    for w_idx, (train_start, train_end, test_start, test_end) in enumerate(windows):
        is_returns = returns_df.iloc[train_start:train_end]
        oos_returns = returns_df.iloc[test_start:test_end]

        # 1. Estimate rolling-OLS betas on the IS window.
        is_betas = estimate_rolling_ols_beta(
            is_returns, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
        )

        # Use the last available IS beta estimate for portfolio construction.
        last_betas = is_betas.iloc[[-1]]

        # 2. Generate signals and construct portfolio from IS betas.
        weights, _, _ = _run_strategy_with_betas(is_returns, last_betas)

        # 3. Backtest OOS: repeat the IS-constructed weights for each OOS date,
        #    prepending the boundary row so run_backtest's one-day lag uses IS
        #    weights on the first OOS date (no lookahead).
        oos_weights = pd.DataFrame(
            np.tile(weights.values, (len(oos_returns), 1)),
            index=oos_returns.index,
            columns=weights.columns,
        )
        boundary_weights = pd.DataFrame(
            weights.values,
            index=is_returns.index[[-1]],
            columns=weights.columns,
        )
        full_weights = pd.concat([boundary_weights, oos_weights])

        backtest = run_backtest(
            oos_returns,
            full_weights,
            transaction_costs=TRANSACTION_COSTS,
        )

        # 4. OOS metrics.
        oos_metrics = _compute_oos_metrics(weights, last_betas, oos_returns, backtest)

        # 5. Walk-forward stability: Spearman of IS beta ranks vs OOS realized beta ranks.
        oos_betas = _ols_beta_per_asset(oos_returns)
        is_beta_vals = last_betas.iloc[0]
        common = is_beta_vals.index.intersection(oos_betas.index)
        if len(common) > 1:
            is_ranks = is_beta_vals[common].rank(method="average")
            oos_ranks = oos_betas[common].rank(method="average")
            spearman_corr = float(spearmanr(is_ranks, oos_ranks).correlation)
        else:
            spearman_corr = np.nan

        # Neutrality checks.
        model_beta_ok = (
            oos_metrics["max_model_beta"] is not None
            and oos_metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL
        )
        dollar_neutral_ok = (
            oos_metrics["max_dollar_neutral"] is not None
            and oos_metrics["max_dollar_neutral"] <= DOLLAR_NEUTRAL_TOL
        )
        realized_beta_ok = (
            oos_metrics["realized_beta"] is not None
            and abs(oos_metrics["realized_beta"]) <= REALIZED_BETA_TOL
        )

        cell = {
            "cell_key": f"seed_{seed_idx}_win_{w_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "window_index": w_idx,
            "train_start": str(is_returns.index[0].date()),
            "train_end": str(is_returns.index[-1].date()),
            "test_start": str(oos_returns.index[0].date()),
            "test_end": str(oos_returns.index[-1].date()),
            "n_train": len(is_returns),
            "n_test": len(oos_returns),
            "metrics": oos_metrics,
            "walk_forward_stability": {
                "spearman_is_oos_beta": (
                    float(spearman_corr) if np.isfinite(spearman_corr) else None
                ),
                "n_common_assets": int(len(common)),
            },
            "neutrality_checks": {
                "model_beta_neutral": {
                    "passed": bool(model_beta_ok),
                    "max_model_beta": oos_metrics["max_model_beta"],
                    "tolerance": MODEL_BETA_NEUTRAL_TOL,
                },
                "dollar_neutral": {
                    "passed": bool(dollar_neutral_ok),
                    "max_dollar_neutral": oos_metrics["max_dollar_neutral"],
                    "tolerance": DOLLAR_NEUTRAL_TOL,
                },
                "realized_beta": {
                    "passed": bool(realized_beta_ok),
                    "realized_beta": oos_metrics["realized_beta"],
                    "tolerance": REALIZED_BETA_TOL,
                },
            },
            "status": "ok"
            if (model_beta_ok and dollar_neutral_ok and realized_beta_ok)
            else "neutrality_violation",
        }
        cells.append(cell)

    return cells


def _run_all_seeds_and_configs() -> dict:
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)

        try:
            cells = _run_walk_forward_for_seed(returns_df, seed, seed_idx)
            all_cells.extend(cells)
        except Exception as e:
            all_cells.append({
                "cell_key": f"seed_{seed_idx}_error",
                "seed_index": seed_idx,
                "seed": seed,
                "window_index": -1,
                "train_start": None,
                "train_end": None,
                "test_start": None,
                "test_end": None,
                "n_train": 0,
                "n_test": 0,
                "metrics": {},
                "walk_forward_stability": {"spearman_is_oos_beta": None, "n_common_assets": 0},
                "neutrality_checks": {},
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
                f"Walk-forward: train={TRAIN_WINDOW}d, test={TEST_WINDOW}d, step={STEP}d. "
                f"Not real market data; not market profitability evidence."
            ),
            "fixture_path": str(FIXTURE_PATH),
            "returns_sha256": returns_sha256,
            "btc_source_sha256": btc_sha256,
            "seeds": {
                "base_seed": SEED_BASE,
                "increment": SEED_INCREMENT,
                "n_seeds": N_SEEDS,
                "seed_list": [
                    SEED_BASE + SEED_INCREMENT * i for i in range(N_SEEDS)
                ],
            },
            "config_grid": {
                "train_window": TRAIN_WINDOW,
                "test_window": TEST_WINDOW,
                "step": STEP,
                "beta_window": BETA_WINDOW,
                "quantile": QUANTILE,
                "transaction_costs": TRANSACTION_COSTS,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "walk_forward_stability": {
                "metric": "spearman_is_oos_beta",
                "description": (
                    "Spearman rank correlation between in-sample beta ranks "
                    "(rolling-OLS at the rebalance point) and out-of-sample realized "
                    "beta ranks (simple OLS over the test window). Measures whether "
                    "the beta signal persists out of sample."
                ),
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
    """Build the deterministic summary artifact (read-only; does not write to disk).

    Returns the same summary dict that ``write_summary`` persists. Used by the
    replay gate (``scripts/bab_replay_full.py``) to byte-diff the committed
    `research_state/bab_p36/walk_forward_summary.json` against a fresh
    in-memory rebuild.
    """
    grid_results = _run_all_seeds_and_configs()
    return _build_summary_artifact(grid_results)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P36 WP0 walk-forward / out-of-sample validation harness"
    )
    parser.add_argument(
        "--check-walk-forward-summary",
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

    if args.check_walk_forward_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P36 WP0 walk-forward / out-of-sample validation...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Train window: {TRAIN_WINDOW}d, test window: {TEST_WINDOW}d, step: {STEP}d")
    print(f"  Beta window: {BETA_WINDOW}d")
    print(f"  Transaction costs: {TRANSACTION_COSTS}")

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

    print(f"Done in {elapsed:.2f}s")
    print(f"  Total cells: {total_cells}")
    print(f"  OK: {ok_cells}")
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
                else:
                    for check_name, check_result in c.get(
                        "neutrality_checks", {}
                    ).items():
                        if not check_result.get("passed", True):
                            val = (
                                check_result.get("max_model_beta")
                                or check_result.get("max_dollar_neutral")
                                or check_result.get("realized_beta")
                            )
                            print(
                                f"    {check_name}: max={val} "
                                f"tol={check_result.get('tolerance')}"
                            )

    # Walk-forward stability report.
    print("\nWalk-forward stability (Spearman IS vs OOS beta ranks, by window):")
    by_window = {}
    for c in grid_results["cells"]:
        if c["status"] != "ok":
            continue
        widx = c["window_index"]
        val = c["walk_forward_stability"]["spearman_is_oos_beta"]
        if val is not None:
            by_window.setdefault(widx, []).append(val)
    for widx in sorted(by_window):
        vals = by_window[widx]
        print(f"  window {widx}: mean spearman={np.mean(vals):.4f} (n={len(vals)})")

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
