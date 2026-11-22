#!/usr/bin/env python3
"""P35 WP2 — Signal-Stability / Beta-Noise Sensitivity + Anti-Overfit Guard.

Deterministic, offline runner that quantifies selection churn on the P34
wide-universe recipe (8 seeds, 40 assets from tests/fixtures/wide_bab_universe.csv)
under two perturbations:

(a) tiny beta-noise injection: Gaussian epsilon on estimated betas,
    epsilon in a small deterministic ladder
(b) estimator switch: rolling-OLS <-> EWMA <-> shrinkage (reusing beta_estimators.py)

For each perturbation cell records:
- fraction of names flipping long<->short vs the OLS baseline
- long/short set Jaccard overlap vs the OLS baseline

Shows shrinkage/EWMA reduce churn while preserving neutrality
(model beta-neutral <= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15).

Mirrors the P34 WP1 anti-victory guard: a perturbation that reduces churn but
breaks neutrality is a FAIL, not a "finding".

Emits a deterministic summary artifact:
  research_state/bab_p35/signal_stability_summary.json  (schema: bab_p35.signal_stability/1)

Provides --check-signal-stability-summary for byte-diff verification in the gate.
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

BETA_WINDOW = 90
QUANTILE = 0.3
TRANSACTION_COSTS = 0.001

# Noise-injection ladder: std of Gaussian noise added to estimated betas.
NOISE_EPSILONS = [1e-4, 1e-3, 1e-2, 5e-2]

# Estimator-switch configs (reusing beta_estimators.py).
EWMA_HALFLIFES = [20, 40, 60]
SHRINKAGE_INTENSITIES = [0.1, 0.3]
SHRINKAGE_TARGETS = [1.0, "cross_sectional_mean"]

# Neutrality tolerances (per HANDOFF.md WP2).
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

# Weight threshold for long/short set membership.
WEIGHT_THRESHOLD = 1e-10

SCHEMA_VERSION = "bab_p35.signal_stability/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p35" / "signal_stability_summary.json"

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# --- Churn computation ---


def _long_short_sets(weights: pd.DataFrame) -> tuple[set, set]:
    """Return (long_set, short_set) for a single-period weight row."""
    w = weights.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    long_set = set(w[w > WEIGHT_THRESHOLD].index)
    short_set = set(w[w < -WEIGHT_THRESHOLD].index)
    return long_set, short_set


def _churn_vs_baseline(
    perturbed_weights: pd.DataFrame,
    baseline_weights: pd.DataFrame,
) -> tuple[float, float]:
    """Compute flip fraction and Jaccard overlap vs baseline, averaged over periods.

    Returns (mean_flip_fraction, mean_jaccard_overlap).

    flip_fraction per period = names in baseline selected set that change side
    (long<->short) or drop out entirely, divided by baseline selected count.
    Names newly selected in perturbed but flat in baseline are not flips.
    """
    common_idx = perturbed_weights.index.intersection(baseline_weights.index)
    common_cols = perturbed_weights.columns.intersection(baseline_weights.columns)
    if len(common_idx) == 0 or len(common_cols) == 0:
        return np.nan, np.nan

    p = perturbed_weights.loc[common_idx, common_cols]
    b = baseline_weights.loc[common_idx, common_cols]

    flip_fracs = []
    jaccards = []
    for idx in common_idx:
        b_long, b_short = _long_short_sets(b.loc[idx])
        p_long, p_short = _long_short_sets(p.loc[idx])

        b_sel = b_long | b_short
        p_sel = p_long | p_short

        if len(b_sel) == 0:
            # No baseline selection; define churn as 0 if perturbed also flat,
            # otherwise 1.0 (everything is new).
            flip_fracs.append(0.0 if len(p_sel) == 0 else 1.0)
            jaccards.append(1.0 if len(p_sel) == 0 else 0.0)
            continue

        # Names changing side: baseline long -> perturbed short, or vice versa.
        side_changers = (b_long & p_short) | (b_short & p_long)
        # Names dropping out: selected in baseline, flat in perturbed.
        dropouts = b_sel - p_sel

        flipping = side_changers | dropouts
        flip_fracs.append(len(flipping) / len(b_sel))

        inter = len(b_sel & p_sel)
        union = len(b_sel | p_sel)
        jaccards.append(inter / union if union > 0 else 1.0)

    mean_flip = float(np.mean(flip_fracs)) if flip_fracs else np.nan
    mean_jaccard = float(np.mean(jaccards)) if jaccards else np.nan
    return mean_flip, mean_jaccard


# --- Universe / reference (mirrors P35 WP1 bakeoff) ---


def _load_reference_prices() -> pd.DataFrame:
    df = pd.read_csv(REFERENCE_FIXTURE, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"reference fixture missing BTC column: {list(df.columns)}")
    return df


def _build_wide_universe_for_seed(seed: int) -> pd.DataFrame:
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


# --- Strategy pipeline (mirrors WP1 _run_strategy_with_betas) ---


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


def _compute_metrics(
    weights: pd.DataFrame,
    betas: pd.DataFrame,
    returns_df: pd.DataFrame,
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

    bench_returns = returns_df["BTC"] if "BTC" in returns_df.columns else pd.Series(dtype=float)

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


# --- Per-seed runner ---


def _inject_beta_noise(
    betas: pd.DataFrame,
    epsilon: float,
    seed: int,
) -> pd.DataFrame:
    """Add iid Gaussian noise N(0, epsilon) to asset betas (benchmark stays 1.0)."""
    asset_cols = [c for c in betas.columns if c != "BTC"]
    noisy = betas.copy()
    rng = np.random.default_rng(seed)
    for c in asset_cols:
        noise = rng.normal(loc=0.0, scale=epsilon, size=len(betas))
        noisy[c] = betas[c] + noise
        # Preserve NaN where OLS was NaN.
        noisy[c] = noisy[c].where(betas[c].notna(), np.nan)
    return noisy


def _run_all_perturbations_for_seed(
    returns_df: pd.DataFrame,
    seed: int,
) -> dict:
    """Run baseline OLS + all perturbations for one seed.

    Returns dict with baseline and every perturbed cell, keyed by cell key.
    """
    results = {}

    # 1. Baseline: rolling-OLS window=90, no noise.
    ols_betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
    )
    ols_weights, _, ols_backtest = _run_strategy_with_betas(returns_df, ols_betas)
    baseline_key = "rolling_ols_w90_no_noise"
    results[baseline_key] = {
        "perturbation": "baseline",
        "param": None,
        "betas": ols_betas,
        "weights": ols_weights,
        "backtest": ols_backtest,
        "metrics": _compute_metrics(ols_weights, ols_betas, returns_df, ols_backtest),
    }

    # 2. Beta-noise injection on OLS betas.
    for epsilon in NOISE_EPSILONS:
        key = f"noise_e{epsilon}"
        noisy_betas = _inject_beta_noise(ols_betas, epsilon, seed)
        noisy_weights, _, noisy_backtest = _run_strategy_with_betas(
            returns_df, noisy_betas
        )
        results[key] = {
            "perturbation": "noise",
            "param": epsilon,
            "betas": noisy_betas,
            "weights": noisy_weights,
            "backtest": noisy_backtest,
            "metrics": _compute_metrics(
                noisy_weights, noisy_betas, returns_df, noisy_backtest
            ),
        }

    # 3. Estimator switch: EWMA.
    for halflife in EWMA_HALFLIFES:
        key = f"ewma_h{halflife}"
        ewma_betas = estimate_ewma_beta(
            returns_df, "BTC", halflife=halflife, min_obs=60
        )
        ewma_weights, _, ewma_backtest = _run_strategy_with_betas(
            returns_df, ewma_betas
        )
        results[key] = {
            "perturbation": "estimator",
            "param": {"estimator": "ewma", "halflife": halflife},
            "betas": ewma_betas,
            "weights": ewma_weights,
            "backtest": ewma_backtest,
            "metrics": _compute_metrics(
                ewma_weights, ewma_betas, returns_df, ewma_backtest
            ),
        }

    # 4. Estimator switch: shrinkage.
    for intensity in SHRINKAGE_INTENSITIES:
        for target in SHRINKAGE_TARGETS:
            target_str = "csm" if target == "cross_sectional_mean" else f"t{target}"
            key = f"shrinkage_i{intensity}_{target_str}"
            shrink_betas = estimate_shrinkage_beta(
                returns_df,
                "BTC",
                window=BETA_WINDOW,
                shrink_target=target,
                shrink_intensity=intensity,
                min_obs=60,
            )
            shrink_weights, _, shrink_backtest = _run_strategy_with_betas(
                returns_df, shrink_betas
            )
            results[key] = {
                "perturbation": "estimator",
                "param": {
                    "estimator": "shrinkage",
                    "intensity": intensity,
                    "target": target,
                },
                "betas": shrink_betas,
                "weights": shrink_weights,
                "backtest": shrink_backtest,
                "metrics": _compute_metrics(
                    shrink_weights, shrink_betas, returns_df, shrink_backtest
                ),
            }

    return results, ols_weights


def _run_all_seeds_and_configs() -> dict:
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        prices = _build_wide_universe_for_seed(seed)
        returns_df = prices.pct_change().iloc[1:][["BTC", *ASSET_COLUMNS]]

        cell_key_base = f"seed_{seed_idx}"

        try:
            perturbed_results, ols_weights = _run_all_perturbations_for_seed(
                returns_df, seed
            )

            for cell_key, cell_result in perturbed_results.items():
                metrics = cell_result["metrics"]

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

                # Churn vs OLS baseline (baseline vs itself = 0 flip, 1.0 Jaccard).
                if cell_key == "rolling_ols_w90_no_noise":
                    flip_fraction = 0.0
                    jaccard_overlap = 1.0
                else:
                    flip_fraction, jaccard_overlap = _churn_vs_baseline(
                        cell_result["weights"], ols_weights
                    )

                cell_result_entry = {
                    "cell_key": f"{cell_key_base}_{cell_key}",
                    "seed_index": seed_idx,
                    "seed": seed,
                    "perturbation": cell_result["perturbation"],
                    "param": cell_result["param"],
                    "metrics": metrics,
                    "churn": {
                        "flip_fraction": float(flip_fraction)
                        if np.isfinite(flip_fraction)
                        else None,
                        "jaccard_overlap": float(jaccard_overlap)
                        if np.isfinite(jaccard_overlap)
                        else None,
                    },
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

                all_cells.append(cell_result_entry)

        except Exception as e:
            cell_result_entry = {
                "cell_key": f"{cell_key_base}_error",
                "seed_index": seed_idx,
                "seed": seed,
                "perturbation": "error",
                "param": {},
                "metrics": {},
                "churn": {"flip_fraction": None, "jaccard_overlap": None},
                "neutrality_checks": {},
                "status": "error",
                "error": str(e),
            }
            all_cells.append(cell_result_entry)

    return {"cells": all_cells}


# --- Summary artifact ---


def _build_summary_artifact(grid_results: dict) -> dict:
    base_prices = _build_wide_universe_for_seed(SEED_BASE)
    fixture_bytes = base_prices.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    fixture_sha256 = hashlib.sha256(fixture_bytes).hexdigest()

    ref = _load_reference_prices()
    btc_sha256 = hashlib.sha256(
        ref["BTC"].to_numpy(dtype=float).tobytes()
    ).hexdigest()

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "fixture_recipe": (
                f"Deterministic synthetic wide universe (P34 recipe). "
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
                "beta_window": BETA_WINDOW,
                "quantile": QUANTILE,
                "transaction_costs": TRANSACTION_COSTS,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
                "noise_epsilons": NOISE_EPSILONS,
                "estimator_families": {
                    "ewma": {"halflifes": EWMA_HALFLIFES},
                    "shrinkage": {
                        "intensities": SHRINKAGE_INTENSITIES,
                        "targets": [str(t) for t in SHRINKAGE_TARGETS],
                        "base_window": BETA_WINDOW,
                    },
                },
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "churn_definition": {
                "flip_fraction": (
                    "Per-period fraction of names in the baseline long/short book "
                    "that change side (long<->short) or drop out entirely, "
                    "averaged over all periods. Baseline-vs-baseline = 0.0."
                ),
                "jaccard_overlap": (
                    "Per-period Jaccard overlap of baseline vs perturbed "
                    "long/short selected sets, averaged over all periods. "
                    "Baseline-vs-baseline = 1.0."
                ),
                "weight_threshold": WEIGHT_THRESHOLD,
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
    `research_state/bab_p35/signal_stability_summary.json` against a fresh
    in-memory rebuild.
    """
    grid_results = _run_all_seeds_and_configs()
    return _build_summary_artifact(grid_results)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P35 WP2 signal-stability / beta-noise sensitivity study"
    )
    parser.add_argument(
        "--check-signal-stability-summary",
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

    if args.check_signal_stability_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P35 WP2 signal-stability / beta-noise sensitivity study...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Beta window: {BETA_WINDOW}")
    print(f"  Noise epsilons: {NOISE_EPSILONS}")
    print(f"  EWMA halflifes: {EWMA_HALFLIFES}")
    print(f"  Shrinkage intensities: {SHRINKAGE_INTENSITIES}")
    print(f"  Shrinkage targets: {SHRINKAGE_TARGETS}")

    n_perts_per_seed = (
        1  # baseline
        + len(NOISE_EPSILONS)
        + len(EWMA_HALFLIFES)
        + len(SHRINKAGE_INTENSITIES) * len(SHRINKAGE_TARGETS)
    )
    total_cells = N_SEEDS * n_perts_per_seed
    print(f"  Perturbations per seed: {n_perts_per_seed}")
    print(f"  Total cells: {total_cells}")

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

    # Churn report: noise ladder monotonicity + estimator vs baseline.
    print("\nChurn summary (flip_fraction vs OLS baseline, averaged over seeds):")
    for epsilon in NOISE_EPSILONS:
        flips = [
            c["churn"]["flip_fraction"]
            for c in grid_results["cells"]
            if (
                c["perturbation"] == "noise"
                and c["param"] == epsilon
                and c["churn"]["flip_fraction"] is not None
            )
        ]
        if flips:
            print(f"  noise eps={epsilon}: mean flip_fraction={np.mean(flips):.6f}")

    for hl in EWMA_HALFLIFES:
        flips = [
            c["churn"]["flip_fraction"]
            for c in grid_results["cells"]
            if (
                c["perturbation"] == "estimator"
                and isinstance(c["param"], dict)
                and c["param"].get("estimator") == "ewma"
                and c["param"].get("halflife") == hl
                and c["churn"]["flip_fraction"] is not None
            )
        ]
        if flips:
            print(f"  ewma halflife={hl}: mean flip_fraction={np.mean(flips):.6f}")

    for intensity in SHRINKAGE_INTENSITIES:
        for target in SHRINKAGE_TARGETS:
            flips = [
                c["churn"]["flip_fraction"]
                for c in grid_results["cells"]
                if (
                    c["perturbation"] == "estimator"
                    and isinstance(c["param"], dict)
                    and c["param"].get("estimator") == "shrinkage"
                    and c["param"].get("intensity") == intensity
                    and c["param"].get("target") == target
                    and c["churn"]["flip_fraction"] is not None
                )
            ]
            if flips:
                t_str = "csm" if target == "cross_sectional_mean" else str(target)
                print(
                    f"  shrinkage intensity={intensity} target={t_str}: "
                    f"mean flip_fraction={np.mean(flips):.6f}"
                )

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
