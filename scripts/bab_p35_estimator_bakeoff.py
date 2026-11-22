#!/usr/bin/env python3
"""P35 WP1 — Estimator Bake-off on the Wide Universe.

Deterministic, offline runner that exercises the shipped default BAB configuration
(weighting="equal", beta_neutral=True, transaction_costs=0.001) across the P34
wide-universe recipe (8 seeds, 40 assets from tests/fixtures/wide_bab_universe.csv)
across estimator families:

- Rolling-OLS: window ∈ {60, 90, 120}
- EWMA: halflife ∈ {20, 40, 60}
- Shrinkage: intensity ∈ {0.1, 0.3} (target = 1.0 and cross_sectional_mean)

Per cell records: realized beta, model beta-neutrality (≤1e-3), dollar-neutrality
(≤1e-9), beta rank-stability (Spearman corr of betas vs OLS baseline + long/short
set Jaccard overlap), turnover, net-of-cost Sharpe, ann vol, max-DD.

Emits a deterministic summary artifact:
  research_state/bab_p35/estimator_bakeoff_summary.json  (schema: bab_p35.estimator_bakeoff/1)

Provides --check-estimator-bakeoff-summary for byte-diff verification in the gate.
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
    estimate_ewma_beta,
    estimate_rolling_ols_beta,
    estimate_shrinkage_beta,
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

# --- Constants matching P34 wide universe recipe ---
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
EWMA_HALFLIFES = [20, 40, 60]
SHRINKAGE_INTENSITIES = [0.1, 0.3]
SHRINKAGE_TARGETS = [1.0, "cross_sectional_mean"]
QUANTILE = 0.3
TRANSACTION_COSTS = 0.001

# Neutrality tolerances (per HANDOFF.md WP1)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

SCHEMA_VERSION = "bab_p35.estimator_bakeoff/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p35" / "estimator_bakeoff_summary.json"

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


def _run_strategy_with_betas(
    returns_df: pd.DataFrame,
    beta_estimates: pd.DataFrame,
    quantile: float = QUANTILE,
    transaction_costs: float = TRANSACTION_COSTS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the BAB pipeline using precomputed beta estimates.

    Mirrors BABStrategy's shipped default path (equal-weight, dollar-neutral,
    beta-neutral) without recomputing rolling-OLS betas, so alternative
    estimator families can be evaluated on the same causal footing.

    Returns (weights, returns_df_used, backtest_df)
    """
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
    # BABStrategy enforces beta neutrality after portfolio construction when
    # beta_neutral=True (the shipped default). The bake-off bypasses
    # BABStrategy.run, so the same minimum-norm correction must be applied
    # here; without it every cell would (correctly) fail model beta-neutrality.
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
    """Compute per-period model portfolio beta: sum_i w_i * beta_i (gross-exposure weighted)."""
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


def _compute_rank_stability(
    estimator_betas: pd.DataFrame,
    ols_betas: pd.DataFrame,
    weights: pd.DataFrame,
    ols_weights: pd.DataFrame,
) -> tuple[float, float]:
    """Compute beta rank-stability metrics vs OLS baseline.

    Returns (spearman_corr, jaccard_overlap)
    - Spearman correlation of cross-sectional beta rankings (averaged over time)
    - Jaccard overlap of long/short sets (averaged over time)
    """
    common_idx = estimator_betas.index.intersection(ols_betas.index)
    common_cols = estimator_betas.columns.intersection(ols_betas.columns)

    if len(common_idx) == 0 or len(common_cols) == 0:
        return np.nan, np.nan

    est = estimator_betas.loc[common_idx, common_cols].astype(float)
    ols = ols_betas.loc[common_idx, common_cols].astype(float)

    # Spearman correlation per period, then average
    spearman_vals = []
    for idx in common_idx:
        est_row = est.loc[idx].dropna()
        ols_row = ols.loc[idx].dropna()
        common_names = est_row.index.intersection(ols_row.index)
        if len(common_names) >= 4:  # need at least 4 for meaningful rank corr
            rho, _ = spearmanr(est_row[common_names], ols_row[common_names])
            if np.isfinite(rho):
                spearman_vals.append(rho)

    avg_spearman = float(np.mean(spearman_vals)) if spearman_vals else np.nan

    # Jaccard overlap of long/short sets per period
    if ols_weights is not None and weights is not None:
        common_w_idx = weights.index.intersection(ols_weights.index)
        common_w_cols = weights.columns.intersection(ols_weights.columns)
        if len(common_w_idx) > 0 and len(common_w_cols) > 0:
            jaccard_vals = []
            for idx in common_w_idx:
                w_row = weights.loc[idx, common_w_cols]
                ols_w_row = ols_weights.loc[idx, common_w_cols]

                est_long = set(w_row[w_row > 1e-10].index)
                est_short = set(w_row[w_row < -1e-10].index)
                ols_long = set(ols_w_row[ols_w_row > 1e-10].index)
                ols_short = set(ols_w_row[ols_w_row < -1e-10].index)

                est_set = est_long.union(est_short)
                ols_set = ols_long.union(ols_short)

                if len(est_set) > 0 or len(ols_set) > 0:
                    inter = len(est_set.intersection(ols_set))
                    union = len(est_set.union(ols_set))
                    jaccard_vals.append(inter / union if union > 0 else 1.0)

            avg_jaccard = float(np.mean(jaccard_vals)) if jaccard_vals else np.nan
        else:
            avg_jaccard = np.nan
    else:
        avg_jaccard = np.nan

    return avg_spearman, avg_jaccard


def _compute_metrics(
    weights: pd.DataFrame,
    betas: pd.DataFrame,
    returns_df: pd.DataFrame,
    backtest: pd.DataFrame,
    ols_betas: pd.DataFrame | None = None,
    ols_weights: pd.DataFrame | None = None,
) -> dict:
    """Compute all metrics for a single run."""
    if "returns" in backtest.columns:
        strat_returns = backtest["returns"]
    else:
        if "cumulative" in backtest.columns:
            cum = backtest["cumulative"]
            strat_returns = cum.pct_change().iloc[1:]
        else:
            strat_returns = pd.Series(dtype=float)

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

    # Rank stability vs OLS baseline
    spearman_corr, jaccard_overlap = _compute_rank_stability(
        betas, ols_betas if ols_betas is not None else betas,
        weights, ols_weights
    )

    # Signal-stability diagnostics: period-to-period beta roughness (mean
    # absolute change of the cross-sectional beta vector) and cross-sectional
    # beta dispersion (mean per-period std). Both are estimator-intrinsic and
    # do not depend on the portfolio run.
    beta_cols = [c for c in betas.columns if c != "BTC"]
    if beta_cols:
        beta_noise = float(betas[beta_cols].diff().abs().mean(axis=1).mean())
        beta_dispersion = float(betas[beta_cols].std(axis=1).mean())
    else:
        beta_noise = None
        beta_dispersion = None

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
        "spearman_vs_ols": float(spearman_corr) if np.isfinite(spearman_corr) else None,
        "jaccard_vs_ols": float(jaccard_overlap) if np.isfinite(jaccard_overlap) else None,
        "beta_noise": beta_noise,
        "beta_dispersion": beta_dispersion,
        "n_periods": len(strat_returns),
    }


def _run_all_estimators_for_seed(
    returns_df: pd.DataFrame,
    shrink_window: int = 90,
) -> dict:
    """Run all estimator families once for a given seed.

    Rolling-OLS is evaluated at every window in ``BETA_WINDOWS``; EWMA is
    evaluated at every halflife in ``EWMA_HALFLIFES``; shrinkage is evaluated
    at every ``SHRINKAGE_INTENSITIES`` x ``SHRINKAGE_TARGETS`` combination
    using ``shrink_window`` (the shipped default window). Each estimator is
    computed exactly once per seed -- the earlier per-window outer loop
    recomputed the same OLS/EWMA cells three times and tripled both runtime
    and artifact size.

    Returns dict with all estimator results keyed by estimator name.
    """
    results = {}

    # 1. Rolling-OLS (baseline)
    for window in BETA_WINDOWS:
        key = f"rolling_ols_w{window}"
        ols_betas = estimate_rolling_ols_beta(
            returns_df, "BTC", window=window, min_obs=min(60, window)
        )
        weights, _, backtest = _run_strategy_with_betas(returns_df, ols_betas)
        results[key] = {
            "estimator": "rolling_ols",
            "params": {"window": window},
            "betas": ols_betas,
            "weights": weights,
            "backtest": backtest,
            "metrics": _compute_metrics(weights, ols_betas, returns_df, backtest),
        }

    # Store OLS baseline for rank stability comparison (use window=90 as reference)
    ols_baseline_key = "rolling_ols_w90"
    ols_baseline_betas = results[ols_baseline_key]["betas"]
    ols_baseline_weights = results[ols_baseline_key]["weights"]

    # 2. EWMA
    for halflife in EWMA_HALFLIFES:
        key = f"ewma_h{halflife}"
        ewma_betas = estimate_ewma_beta(returns_df, "BTC", halflife=halflife, min_obs=60)
        weights, _, backtest = _run_strategy_with_betas(returns_df, ewma_betas)
        results[key] = {
            "estimator": "ewma",
            "params": {"halflife": halflife},
            "betas": ewma_betas,
            "weights": weights,
            "backtest": backtest,
            "metrics": _compute_metrics(
                weights, ewma_betas, returns_df, backtest,
                ols_betas=ols_baseline_betas, ols_weights=ols_baseline_weights
            ),
        }

    # 3. Shrinkage
    for intensity in SHRINKAGE_INTENSITIES:
        for target in SHRINKAGE_TARGETS:
            target_str = "csm" if target == "cross_sectional_mean" else f"t{target}"
            key = f"shrinkage_i{intensity}_{target_str}"
            shrink_betas = estimate_shrinkage_beta(
                returns_df, "BTC",
                window=shrink_window,
                shrink_target=target,
                shrink_intensity=intensity,
                min_obs=60,
            )
            weights, _, backtest = _run_strategy_with_betas(returns_df, shrink_betas)
            results[key] = {
                "estimator": "shrinkage",
                "params": {"window": shrink_window, "intensity": intensity, "target": target},
                "betas": shrink_betas,
                "weights": weights,
                "backtest": backtest,
                "metrics": _compute_metrics(
                    weights, shrink_betas, returns_df, backtest,
                    ols_betas=ols_baseline_betas, ols_weights=ols_baseline_weights
                ),
            }

    return results


def _run_all_seeds_and_configs() -> dict:
    """Run the full multi-seed, multi-estimator grid and collect results.

    Grid size: N_SEEDS x (len(BETA_WINDOWS) + len(EWMA_HALFLIFES)
    + len(SHRINKAGE_INTENSITIES) * len(SHRINKAGE_TARGETS)) = 8 x 10 = 80 cells.
    """
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        prices = _build_wide_universe_for_seed(seed)

        # Convert to returns for strategy
        returns_df = prices.pct_change().iloc[1:][["BTC", *ASSET_COLUMNS]]

        cell_key_base = f"seed_{seed_idx}"

        try:
            estimator_results = _run_all_estimators_for_seed(returns_df)

            for est_key, est_result in estimator_results.items():
                cell_key = f"{cell_key_base}_{est_key}"
                metrics = est_result["metrics"]

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
                    "beta_window": est_result["params"].get("window"),
                    "estimator": est_result["estimator"],
                    "params": est_result["params"],
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

                all_cells.append(cell_result)

        except Exception as e:
            cell_result = {
                "cell_key": f"{cell_key_base}_error",
                "seed_index": seed_idx,
                "seed": seed,
                "beta_window": None,
                "estimator": "error",
                "params": {},
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
                "quantile": QUANTILE,
                "transaction_costs": TRANSACTION_COSTS,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
                "estimator_families": {
                    "rolling_ols": {"windows": BETA_WINDOWS},
                    "ewma": {"halflifes": EWMA_HALFLIFES},
                    "shrinkage": {
                        "intensities": SHRINKAGE_INTENSITIES,
                        "targets": [str(t) for t in SHRINKAGE_TARGETS],
                        "base_window": BETA_WINDOWS[1],  # 90
                    },
                },
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

    parser = argparse.ArgumentParser(description="P35 WP1 estimator bake-off on wide universe")
    parser.add_argument(
        "--check-estimator-bakeoff-summary",
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

    if args.check_estimator_bakeoff_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P35 WP1 estimator bake-off on wide universe...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Beta windows: {BETA_WINDOWS}")
    print(f"  EWMA halflifes: {EWMA_HALFLIFES}")
    print(f"  Shrinkage intensities: {SHRINKAGE_INTENSITIES}")
    print(f"  Shrinkage targets: {SHRINKAGE_TARGETS}")
    n_estimators = (
        len(BETA_WINDOWS)
        + len(EWMA_HALFLIFES)
        + len(SHRINKAGE_INTENSITIES) * len(SHRINKAGE_TARGETS)
    )
    total_cells = N_SEEDS * n_estimators
    print(f"  Total estimator configs per seed: {n_estimators}")
    print(f"  Total cells: {total_cells}")

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
