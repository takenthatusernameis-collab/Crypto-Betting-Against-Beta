#!/usr/bin/env python3
"""P36 WP1 — Frazzini-Pedersen Rank-Weighted / Beta-Scaled Construction.

Deterministic, offline runner that compares the Frazzini-Pedersen rank-weighted
/ beta-scaled construction (opt-in via construct_rank_weights) against the
shipped equal-weight default on the 40-asset wide synthetic universe (P35 recipe).

Per cell (seed):
  1. Build the wide synthetic universe (BTC from wide_bab_universe.csv +
     seeded idio noise; asset returns = beta * BTC_return + idio).
  2. Estimate rolling-OLS betas (window=90) on the full sample.
  3. Generate BAB signals (long low-beta quantile, short high-beta quantile).
  4. Construct equal-weight portfolio (weighting="equal", beta_neutral=True,
     dollar_neutral=True) — the shipped default.
  5. Construct rank-weighted portfolio (weighting="rank") — Frazzini-Pedersen
     rank weights with per-leg beta scaling to achieve beta-neutrality.
  6. Backtest both on the full sample with one-day lagged weights.
  7. Compare: turnover, neutrality (model beta, dollar neutral, realized beta),
     Sharpe, wealth.

Emits research_state/bab_p36/rank_weighted_summary.json (schema: bab_p36.rank_weighted/1).
Provides --check-rank-weighted-summary for byte-diff verification.
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
    construct_rank_weights,
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

BETA_WINDOW = 90
QUANTILE = 0.3
TRANSACTION_COSTS = 0.001

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances (per HANDOFF.md P36)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

# Rank-mode safety valves (never weakened; see HANDOFF.md forbidden list)
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0

WEIGHT_THRESHOLD = 1e-10

SCHEMA_VERSION = "bab_p36.rank_weighted/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p36" / "rank_weighted_summary.json"


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


def _run_strategy_with_betas(
    returns_df: pd.DataFrame,
    beta_estimates: pd.DataFrame,
    weighting: str = "equal",
    quantile: float = QUANTILE,
    transaction_costs: float = TRANSACTION_COSTS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    signals = generate_bab_signals(
        beta_estimates,
        long_quantile=quantile,
        short_quantile=quantile,
    )
    if weighting == "rank":
        weights = construct_rank_weights(
            signals,
            beta_estimates,
            min_leg_beta=RANK_MIN_LEG_BETA,
            max_gross=RANK_MAX_GROSS,
        )
    else:
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
        # Round floats to 12 decimals so the summary is byte-reproducible across
        # numpy/pandas/scipy versions (raw values differ by ~1 ULP otherwise).
        "wealth": round(float(wealth), 12) if np.isfinite(wealth) else None,
        "sharpe": round(float(sharpe), 12) if np.isfinite(sharpe) else None,
        "annualized_volatility": round(float(ann_vol), 12) if np.isfinite(ann_vol) else None,
        "max_drawdown": round(float(max_dd), 12) if np.isfinite(max_dd) else None,
        "total_return": round(float(tr), 12) if np.isfinite(tr) else None,
        "turnover": round(float(turn), 12) if np.isfinite(turn) else None,
        "max_model_beta": round(float(max_model_beta), 12) if np.isfinite(max_model_beta) else None,
        "max_dollar_neutral": (
            round(float(max_dollar_neutral), 12) if np.isfinite(max_dollar_neutral) else None
        ),
        "realized_beta": round(float(realized_beta), 12) if np.isfinite(realized_beta) else None,
        "n_periods": len(strat_returns),
    }


def _count_selected(weights: pd.DataFrame) -> int:
    """Number of assets with nonzero weight, averaged over periods."""
    w = weights.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    n_sel = (w.abs() > WEIGHT_THRESHOLD).sum(axis=1)
    return float(n_sel.mean())


# --- Per-seed runner ---


def _run_rank_weighted_for_seed(returns_df: pd.DataFrame, seed: int, seed_idx: int) -> dict:
    """Run equal-weight vs rank-weighted comparison for one seed."""
    # Estimate rolling-OLS betas on the full sample.
    betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
    )

    # Drop leading NaN rows (insufficient observations for rolling OLS).
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
    valid_betas_aligned = valid_betas[ASSET_COLUMNS + ["BTC"]]

    # Equal-weight (shipped default).
    eq_weights, _, eq_backtest = _run_strategy_with_betas(
        valid_returns, valid_betas_aligned, weighting="equal"
    )
    eq_metrics = _compute_metrics(
        eq_weights, valid_betas_aligned, valid_returns, eq_backtest
    )
    eq_n_selected = _count_selected(eq_weights)

    # Rank-weighted (Frazzini-Pedersen).
    rw_weights, _, rw_backtest = _run_strategy_with_betas(
        valid_returns, valid_betas_aligned, weighting="rank"
    )
    rw_metrics = _compute_metrics(
        rw_weights, valid_betas_aligned, valid_returns, rw_backtest
    )
    rw_n_selected = _count_selected(rw_weights)

    # Neutrality checks.
    # Equal-weight (shipped default): all three neutrality invariants.
    # Rank-weighted: model beta-neutral + realized-beta only; dollar-neutral is
    # intentionally relaxed because rank weighting achieves beta-neutrality
    # (not dollar-neutrality) by construction — see HANDOFF.md P36 WP1.
    def _eq_neutrality_ok(metrics):
        return (
            metrics["max_model_beta"] is not None
            and metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL
            and metrics["max_dollar_neutral"] is not None
            and metrics["max_dollar_neutral"] <= DOLLAR_NEUTRAL_TOL
            and metrics["realized_beta"] is not None
            and abs(metrics["realized_beta"]) <= REALIZED_BETA_TOL
        )

    def _rw_neutrality_ok(metrics):
        return (
            metrics["max_model_beta"] is not None
            and metrics["max_model_beta"] <= MODEL_BETA_NEUTRAL_TOL
            and metrics["realized_beta"] is not None
            and abs(metrics["realized_beta"]) <= REALIZED_BETA_TOL
        )

    eq_neutrality_ok = _eq_neutrality_ok(eq_metrics)
    rw_neutrality_ok = _rw_neutrality_ok(rw_metrics)

    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "n_periods": len(valid_returns),
        "n_valid_beta_rows": len(valid_betas),
        "equal_weight": {
            "metrics": eq_metrics,
            "n_selected_avg": eq_n_selected,
            "neutrality_ok": eq_neutrality_ok,
        },
        "rank_weighted": {
            "metrics": rw_metrics,
            "n_selected_avg": rw_n_selected,
            "neutrality_ok": rw_neutrality_ok,
        },
        "comparison": {
            "turnover_reduction": (
                (eq_metrics["turnover"] - rw_metrics["turnover"])
                if (eq_metrics["turnover"] is not None
                    and rw_metrics["turnover"] is not None)
                else None
            ),
            "sharpe_difference": (
                (rw_metrics["sharpe"] - eq_metrics["sharpe"])
                if (rw_metrics["sharpe"] is not None
                    and eq_metrics["sharpe"] is not None)
                else None
            ),
            "wealth_difference": (
                (rw_metrics["wealth"] - eq_metrics["wealth"])
                if (rw_metrics["wealth"] is not None
                    and eq_metrics["wealth"] is not None)
                else None
            ),
            "realized_beta_difference": (
                (rw_metrics["realized_beta"] - eq_metrics["realized_beta"])
                if (rw_metrics["realized_beta"] is not None
                    and eq_metrics["realized_beta"] is not None)
                else None
            ),
        },
        "status": "ok"
        if (eq_neutrality_ok and rw_neutrality_ok)
        else "neutrality_violation",
    }


def _run_all_seeds_and_configs() -> dict:
    all_cells = []

    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)

        try:
            cell = _run_rank_weighted_for_seed(returns_df, seed, seed_idx)
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
                "seed_list": [
                    SEED_BASE + SEED_INCREMENT * i for i in range(N_SEEDS)
                ],
            },
            "config_grid": {
                "beta_window": BETA_WINDOW,
                "quantile": QUANTILE,
                "transaction_costs": TRANSACTION_COSTS,
                "weighting_equal": "equal",
                "weighting_rank": "rank",
                "beta_neutral": True,
                "dollar_neutral": True,
                "rank_min_leg_beta": RANK_MIN_LEG_BETA,
                "rank_max_gross": RANK_MAX_GROSS,
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "rank_construction": {
                "method": "Frazzini-Pedersen rank weighting with per-leg beta scaling",
                "description": (
                    "Rank eligible betas ascending; long lowest quantile, short "
                    "highest quantile; dollar-normalize each leg; scale by inverse "
                    "leg beta to achieve beta-neutrality (not dollar-neutrality). "
                    "Flat row if leg beta < min_leg_beta or gross > max_gross."
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
    `research_state/bab_p36/rank_weighted_summary.json` against a fresh
    in-memory rebuild.
    """
    grid_results = _run_all_seeds_and_configs()
    return _build_summary_artifact(grid_results)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P36 WP1 Frazzini-Pedersen rank-weighted / beta-scaled construction"
    )
    parser.add_argument(
        "--check-rank-weighted-summary",
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

    if args.check_rank_weighted_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P36 WP1 rank-weighted / beta-scaled construction...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Beta window: {BETA_WINDOW}d")
    print(f"  Quantile: {QUANTILE}")
    print(f"  Transaction costs: {TRANSACTION_COSTS}")
    print(f"  Rank min leg beta: {RANK_MIN_LEG_BETA}")
    print(f"  Rank max gross: {RANK_MAX_GROSS}")

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

    # Comparison report.
    print("\nEqual-weight vs rank-weighted (averaged over seeds):")
    eq_turnovers = []
    rw_turnovers = []
    eq_sharpes = []
    rw_sharpes = []
    eq_realized = []
    rw_realized = []
    for c in grid_results["cells"]:
        if c["status"] != "ok":
            continue
        eq = c["equal_weight"]["metrics"]
        rw = c["rank_weighted"]["metrics"]
        if eq["turnover"] is not None:
            eq_turnovers.append(eq["turnover"])
        if rw["turnover"] is not None:
            rw_turnovers.append(rw["turnover"])
        if eq["sharpe"] is not None:
            eq_sharpes.append(eq["sharpe"])
        if rw["sharpe"] is not None:
            rw_sharpes.append(rw["sharpe"])
        if eq["realized_beta"] is not None:
            eq_realized.append(eq["realized_beta"])
        if rw["realized_beta"] is not None:
            rw_realized.append(rw["realized_beta"])

    if eq_turnovers and rw_turnovers:
        print(f"  Equal-weight avg turnover: {np.mean(eq_turnovers):.6f}")
        print(f"  Rank-weighted avg turnover: {np.mean(rw_turnovers):.6f}")
        print(f"  Turnover reduction: {np.mean(eq_turnovers) - np.mean(rw_turnovers):.6f}")
    if eq_sharpes and rw_sharpes:
        print(f"  Equal-weight avg Sharpe: {np.mean(eq_sharpes):.4f}")
        print(f"  Rank-weighted avg Sharpe: {np.mean(rw_sharpes):.4f}")
    if eq_realized and rw_realized:
        print(f"  Equal-weight avg realized beta: {np.mean(eq_realized):.6f}")
        print(f"  Rank-weighted avg realized beta: {np.mean(rw_realized):.6f}")

    return 0 if (violation_cells == 0 and error_cells == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
