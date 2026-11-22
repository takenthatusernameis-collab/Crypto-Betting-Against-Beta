#!/usr/bin/env python3
"""P34 WP0 — Multi-seed wide-universe equal-weight robustness study.

Deterministic, offline runner that exercises the shipped default BAB configuration
(weighting="equal", beta_neutral=True) across N>=8 seeds on the wide synthetic
universe recipe (beta * BTC_return + idio, idio ~ N(0, idio_vol), betas
linspace 0.35-1.9, 40 assets + 1 all-NaN column).

For each seed and each config cell (beta_window in {60,90,120}, quantile in {0.2,0.3}):
  - Runs BABStrategy with transaction_costs=0.001
  - Asserts systematic invariants:
      max_t |sum_i w_{t,i} * beta_{t,i}| <= 1e-3   (model beta-neutral)
      |sum_i w_{t,i}| <= 1e-9                      (dollar-neutral)
      |realized beta| <= 0.15                      (strategy beta via OLS)
  - Records wealth, Sharpe, ann-vol, max-DD, realized beta, model beta, turnover

Emits a deterministic summary artifact:
  research_state/bab_p34/multiseed_summary.json  (schema: bab_p34.multiseed_summary/1)

Provides --check-multiseed-summary for byte-diff verification in the gate.
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

from strategies.betting_against_beta import BABStrategy  # noqa: E402
from strategies.betting_against_beta.metrics import (  # noqa: E402
    annualized_volatility,
    final_cumulative,
    max_drawdown,
    sharpe_ratio,
    strategy_beta,
    total_return,
    turnover,
)

# --- Constants matching P25 wide universe recipe ---
SEED_BASE = 20261120
SEED_INCREMENT = 1009
N_SEEDS = 8
IDIO_VOL = 0.003
BETA_MIN = 0.35
BETA_MAX = 1.90
N_ASSETS = 40
NAN_COLUMN = "DEL"
REFERENCE_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv"

BETA_WINDOWS = [60, 90, 120]
QUANTILES = [0.2, 0.3]
TRANSACTION_COSTS = 0.001

# Neutrality tolerances (per HANDOFF.md WP0)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

SCHEMA_VERSION = "bab_p34.multiseed_summary/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p34" / "multiseed_summary.json"

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]


def _load_reference_prices() -> pd.DataFrame:
    """Load reference BTC prices from the P25 fixture."""
    df = pd.read_csv(REFERENCE_FIXTURE, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"reference fixture missing BTC column: {list(df.columns)}")
    return df


def _build_wide_universe_for_seed(seed: int) -> pd.DataFrame:
    """Build wide synthetic universe for a specific seed (returns price DataFrame)."""
    ref = _load_reference_prices()
    btc_prices = ref["BTC"].astype(float)
    dates = ref.index

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

    # Reconstruct prices from returns
    btc_first_price = float(btc_prices.iloc[0])
    btc_price_series = btc_first_price * (1.0 + btc_returns).cumprod()
    btc_price_full = pd.concat([
        pd.Series({dates[0]: btc_first_price}),
        btc_price_series,
    ])

    asset_price_series = {}
    for i, col in enumerate(ASSET_COLUMNS):
        asset_prices = 100.0 * (1.0 + returns_df[col]).cumprod()
        asset_price_series[col] = asset_prices

    prices = pd.DataFrame({"BTC": btc_price_full, **asset_price_series}, index=dates)
    prices[NAN_COLUMN] = np.nan
    prices = prices[["BTC", *ASSET_COLUMNS, NAN_COLUMN]]

    return prices


def _run_strategy_for_config(
    returns_df: pd.DataFrame,
    beta_window: int,
    quantile: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run BABStrategy with shipped default config for given parameters.

    Returns (weights, betas, returns, backtest_df)
    """
    # synthetic_seed must be an int per config validation, even though we pass returns_df
    strategy = BABStrategy(
        benchmark="BTC",
        beta_window=beta_window,
        min_observations=min(60, beta_window),
        long_quantile=quantile,
        short_quantile=quantile,
        transaction_costs=TRANSACTION_COSTS,
        beta_neutral=True,
        weighting="equal",
        dollar_neutral=True,
        synthetic_seed=42,  # dummy value; not used when returns_df is passed
    )
    result = strategy.run(returns_df=returns_df)
    return result.weights, result.betas, result.returns, result.backtest


def _compute_model_beta_neutrality(weights: pd.DataFrame, betas: pd.DataFrame) -> pd.Series:
    """Compute per-period model portfolio beta: sum_i w_i * beta_i (gross-exposure weighted).

    Returns a Series aligned to weights.index.
    """
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
    """Compute per-period net exposure: sum_i w_i."""
    return weights.sum(axis=1)


def _compute_metrics(
    weights: pd.DataFrame,
    betas: pd.DataFrame,
    returns_df: pd.DataFrame,
    backtest: pd.DataFrame,
) -> dict:
    """Compute all metrics for a single run."""
    # Strategy returns from backtest
    if "returns" in backtest.columns:
        strat_returns = backtest["returns"]
    else:
        # Fallback: compute from cumulative
        if "cumulative" in backtest.columns:
            cum = backtest["cumulative"]
            strat_returns = cum.pct_change().iloc[1:]
        else:
            strat_returns = pd.Series(dtype=float)

    # Benchmark returns
    bench_returns = returns_df["BTC"] if "BTC" in returns_df.columns else pd.Series(dtype=float)

    # Model beta neutrality (per-period portfolio beta)
    model_beta_series = _compute_model_beta_neutrality(weights, betas)
    max_model_beta = (
        float(model_beta_series.abs().max()) if len(model_beta_series) > 0 else np.nan
    )

    # Dollar neutrality
    dollar_neutral_series = _compute_dollar_neutrality(weights)
    max_dollar_neutral = (
        float(dollar_neutral_series.abs().max()) if len(dollar_neutral_series) > 0 else np.nan
    )

    # Realized beta (OLS)
    realized_beta = strategy_beta(strat_returns, bench_returns)

    # Performance metrics
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


def _run_all_seeds_and_configs() -> dict:
    """Run the full multi-seed, multi-config grid and collect results."""
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        prices = _build_wide_universe_for_seed(seed)

        # Convert to returns for strategy (drop BTC column for returns, but keep for benchmark)
        returns_df = prices.pct_change().iloc[1:][["BTC", *ASSET_COLUMNS]]

        for beta_window in BETA_WINDOWS:
            for quantile in QUANTILES:
                cell_key = f"seed_{seed_idx}_bw{beta_window}_q{quantile}"

                try:
                    weights, betas, ret_df, backtest = _run_strategy_for_config(
                        returns_df, beta_window, quantile
                    )
                    metrics = _compute_metrics(weights, betas, ret_df, backtest)

                    # Neutrality checks
                    model_beta_ok = (
                        metrics["max_model_beta"] is not None
                        and metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL
                    )
                    dollar_neutral_ok = (
                        metrics["max_dollar_neutral"] is not None
                        and metrics["max_dollar_neutral"] <= DOLLAR_NEUTRAL_TOL
                    )
                    realized_beta_ok = (
                        metrics["realized_beta"] is not None
                        and abs(metrics["realized_beta"]) <= REALIZED_BETA_TOL
                    )

                    cell_result = {
                        "cell_key": cell_key,
                        "seed_index": seed_idx,
                        "seed": seed,
                        "beta_window": beta_window,
                        "quantile": quantile,
                        "metrics": metrics,
                        "neutrality_checks": {
                            "model_beta_neutral": {
                                "passed": bool(model_beta_ok),
                                "max_model_beta": metrics["max_model_beta"],
                                "tolerance": MODEL_BETA_NEUTRAL_TOL,
                            },
                            "dollar_neutral": {
                                "passed": bool(dollar_neutral_ok),
                                "max_dollar_neutral": metrics["max_dollar_neutral"],
                                "tolerance": DOLLAR_NEUTRAL_TOL,
                            },
                            "realized_beta": {
                                "passed": bool(realized_beta_ok),
                                "realized_beta": metrics["realized_beta"],
                                "tolerance": REALIZED_BETA_TOL,
                            },
                        },
                        "status": "ok"
                        if (model_beta_ok and dollar_neutral_ok and realized_beta_ok)
                        else "neutrality_violation",
                    }

                except Exception as e:
                    cell_result = {
                        "cell_key": cell_key,
                        "seed_index": seed_idx,
                        "seed": seed,
                        "beta_window": beta_window,
                        "quantile": quantile,
                        "metrics": {},
                        "neutrality_checks": {},
                        "status": "error",
                        "error": str(e),
                    }

                all_cells.append(cell_result)

    return {"cells": all_cells}


def _build_summary_artifact(grid_results: dict) -> dict:
    """Build the deterministic summary artifact with provenance."""
    # Compute fixture SHA256 for provenance (using the base seed fixture as reference)
    base_prices = _build_wide_universe_for_seed(SEED_BASE)
    fixture_bytes = base_prices.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    fixture_sha256 = hashlib.sha256(fixture_bytes).hexdigest()

    # Reference BTC SHA256
    ref = _load_reference_prices()
    btc_sha256 = hashlib.sha256(
        ref["BTC"].to_numpy(dtype=float).tobytes()
    ).hexdigest()

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "fixture_recipe": (
                f"Deterministic synthetic wide universe (P25 recipe). "
                f"BTC prices from tests/fixtures/real_market_prices.csv. "
                f"Asset returns = beta * BTC_return + idio, idio ~ N(0, {IDIO_VOL}), "
                f"betas linspace({BETA_MIN}, {BETA_MAX}, {N_ASSETS}). "
                f"One all-NaN {NAN_COLUMN} column for loader robustness. "
                f"Not real market data; not market profitability evidence."
            ),
            "fixture_sha256": fixture_sha256,
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
                "beta_windows": BETA_WINDOWS,
                "quantiles": QUANTILES,
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
        },
        "results": grid_results,
    }

    return summary


def write_summary(summary: dict, path: Path = SUMMARY_PATH) -> None:
    """Write summary artifact with deterministic JSON formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_summary(path: Path = SUMMARY_PATH) -> bool:
    """Verify that the summary artifact matches a fresh recomputation (byte-identical)."""
    if not path.exists():
        print(f"Summary artifact not found: {path}")
        return False

    # Recompute
    grid_results = _run_all_seeds_and_configs()
    fresh_summary = _build_summary_artifact(grid_results)

    # Compare byte-identical
    expected_bytes = path.read_bytes()
    actual_bytes = json.dumps(fresh_summary, indent=2, sort_keys=True).encode("utf-8") + b"\n"

    if expected_bytes == actual_bytes:
        print("Summary artifact check: PASS (byte-identical)")
        return True
    else:
        print("Summary artifact check: FAIL (byte mismatch)")
        # Find first difference
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


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="P34 WP0 multi-seed robustness study")
    parser.add_argument(
        "--check-multiseed-summary",
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

    if args.check_multiseed_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P34 WP0 multi-seed robustness study...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Beta windows: {BETA_WINDOWS}")
    print(f"  Quantiles: {QUANTILES}")
    print(f"  Total cells: {N_SEEDS * len(BETA_WINDOWS) * len(QUANTILES)}")

    started = time.perf_counter()
    grid_results = _run_all_seeds_and_configs()
    summary = _build_summary_artifact(grid_results)
    write_summary(summary, args.output)
    elapsed = time.perf_counter() - started

    # Report summary
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

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
