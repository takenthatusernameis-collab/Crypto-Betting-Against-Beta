#!/usr/bin/env python3
"""P25 WP1 — deterministic rank-weighted walk-forward (out-of-sample) harness.

Runs an expanding-window walk-forward over the P25 WP0 wide synthetic universe
(fixture ``tests/fixtures/wide_bab_universe.csv``). Each fold fits rolling beta
on the causal history, constructs a Frazzini-Pedersen rank-weighted BAB book
on the untouched test slice (one-day lagged weights, no lookahead), and scores
out-of-sample: Sharpe, volatility, drawdown, turnover, realized beta, portfolio
beta, per-leg beta, and the recovered planted beta spread.

Rank weighting: long the lowest-beta quantile, short the highest-beta quantile,
beta-neutral by construction (``Σ wᵢβᵢ ≈ 0``), with ``rank_min_leg_beta=0.20``
and ``rank_max_gross=4.0`` safety valves. The fixture is deterministic synthetic
data; no figure here is evidence of real market profitability.

Writes two artifacts:

  research_state/bab_p25/walk_forward_rank.json  -- machine-readable folds + aggregate
  research_state/bab_p25/walk_forward_rank.md    -- table rendered from that JSON in memory

Single entry point: ``run_walk_forward_rank()`` returns the results dict and
writes the JSON + markdown artifacts.

Usage:
  python3 scripts/bab_walk_forward_rank.py
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p25.walk_forward_rank/1"
FIXTURE_CSV = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
OUTPUT_DIR = _REPO_ROOT / "research_state" / "bab_p25"
BENCHMARK = "BTC"
SEED = 20261120
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
TRAIN_WINDOW = 180
TEST_WINDOW = 40
N_FOLDS = 5
LONG_QUANTILE = 0.3
SHORT_QUANTILE = 0.3
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
DECIMALS = 6
FLAT = 1e-9

FOLD_FIELDS = (
    "fold",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "n_train",
    "n_test",
    "oos_sharpe",
    "oos_vol",
    "oos_max_drawdown",
    "oos_turnover",
    "oos_realized_beta",
    "portfolio_beta",
    "oos_wealth",
    "beta_spread",
    "long_leg_beta",
    "short_leg_beta",
    "nonflat_rows",
)
AGGREGATE_FIELDS = (
    "mean_oos_sharpe",
    "median_oos_sharpe",
    "fraction_positive_oos_sharpe",
    "total_oos_rows",
    "mean_oos_vol",
    "mean_oos_max_drawdown",
    "mean_oos_turnover",
    "mean_portfolio_beta",
    "mean_beta_spread",
    "mean_nonflat_rows",
    "folds",
    "candidates_evaluated",
)

NULL_FIELD_REASONS = {
    "oos_sharpe": "null when the OOS slice has fewer than two finite returns",
    "oos_vol": "null when the OOS slice has fewer than two finite returns",
    "oos_max_drawdown": "null when the OOS path is empty",
    "oos_turnover": "null when the OOS weight frame is empty",
    "oos_realized_beta": "null when OOS strategy/benchmark variance is degenerate",
    "portfolio_beta": "null when no OOS row has nonzero gross exposure",
    "beta_spread": "null when a fold has no eligible long or short leg",
    "long_leg_beta": "null when a fold has no eligible long leg",
    "short_leg_beta": "null when a fold has no eligible short leg",
    "mean_oos_sharpe": "null when every fold's oos_sharpe is null",
    "median_oos_sharpe": "null when every fold's oos_sharpe is null",
    "fraction_positive_oos_sharpe": "null when no fold has a non-null oos_sharpe",
}


def _clean(value) -> float | None:
    """Round a float to artifact precision, mapping non-finite to None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, DECIMALS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strategy_config() -> dict:
    return dict(
        benchmark=BENCHMARK,
        beta_window=BETA_WINDOW,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=LONG_QUANTILE,
        short_quantile=SHORT_QUANTILE,
        transaction_costs=TRANSACTION_COSTS,
        beta_neutral=True,
        weighting="rank",
        rank_min_leg_beta=RANK_MIN_LEG_BETA,
        rank_max_gross=RANK_MAX_GROSS,
    )


def _leg_betas(signals_df: pd.DataFrame, betas_df: pd.DataFrame, test_start: int, test_end: int):
    """Mean long-leg / short-leg causal beta over non-flat test rows."""
    longs, shorts = [], []
    n_rows = len(signals_df)
    for t in range(test_start, min(test_end, n_rows)):
        sig = signals_df.iloc[t]
        bet = betas_df.iloc[t]
        long_cols = [
            c for c in sig.index
            if sig[c] == 1 and c in bet.index and np.isfinite(bet[c]) and bet[c] > 0.0
        ]
        short_cols = [
            c for c in sig.index
            if sig[c] == -1 and c in bet.index and np.isfinite(bet[c]) and bet[c] > 0.0
        ]
        if long_cols:
            longs.append(float(np.mean([bet[c] for c in long_cols])))
        if short_cols:
            shorts.append(float(np.mean([bet[c] for c in short_cols])))
    long_b = float(np.mean(longs)) if longs else None
    short_b = float(np.mean(shorts)) if shorts else None
    spread = (short_b - long_b) if (long_b is not None and short_b is not None) else None
    return long_b, short_b, spread


def _run_fold(returns: pd.DataFrame, test_start: int, test_end: int) -> dict:
    """Run the rank strategy on causal history [0, test_end) and score [test_start, test_end)."""
    result = BABStrategy(**_strategy_config()).run(returns_df=returns.iloc[:test_end])
    weights = result.weights
    betas = result.betas
    signals = result.signals
    backtest = result.backtest
    oos_returns = backtest["returns"].iloc[test_start:test_end]
    oos_weights = weights.iloc[test_start:test_end]
    oos_betas = betas.iloc[test_start:test_end]
    bench = returns[BENCHMARK].iloc[test_start:test_end]
    cumulative = (1.0 + oos_returns.astype("float64")).cumprod()
    wealth = float(cumulative.iloc[-1]) if len(cumulative) else 1.0
    long_b, short_b, spread = _leg_betas(signals, betas, test_start, test_end)
    return {
        "oos_sharpe": _clean(metrics.sharpe_ratio(oos_returns)),
        "oos_vol": _clean(metrics.annualized_volatility(oos_returns)),
        "oos_max_drawdown": _clean(metrics.max_drawdown(cumulative)),
        "oos_turnover": _clean(metrics.turnover(oos_weights)),
        "oos_realized_beta": _clean(metrics.strategy_beta(oos_returns, bench)),
        "oos_wealth": _clean(wealth),
        "portfolio_beta": _clean(metrics.portfolio_beta(oos_weights, oos_betas)),
        "beta_spread": _clean(spread),
        "long_leg_beta": _clean(long_b),
        "short_leg_beta": _clean(short_b),
        "nonflat_rows": int((oos_weights.abs().sum(axis=1) > FLAT).sum()),
    }


def _provenance(returns: pd.DataFrame, fixture_sha: str, n_rows: int) -> dict:
    return {
        "fixture_path": "tests/fixtures/wide_bab_universe.csv",
        "fixture_sha256": fixture_sha,
        "price_rows": n_rows + 1,
        "return_rows": n_rows,
        "date_first": str(returns.index[0].date()),
        "date_last": str(returns.index[-1].date()),
        "seed": SEED,
        "synthetic": True,
        "universe": "BTC + A001..A040 (DEL all-NaN column dropped by loader)",
        "provenance": (
            "Deterministic synthetic wide universe (P25 WP0 fixture); not real market "
            "data and not evidence of real-market profitability."
        ),
        "no_lookahead": (
            "Each fold runs the strategy over causal history [0, test_end); weights at "
            "row t use the one-day backtest lag and rolling betas computed from returns "
            "through t-1, so the OOS return at row t is never used to weight itself. The "
            "test slice [test_start, test_end) is scored but never read during weight "
            "construction for that row."
        ),
        "rank_rule": (
            "Frazzini-Pedersen rank weighting: long the lowest-beta quantile, short the "
            "highest-beta quantile, beta-neutral by construction, rank_min_leg_beta="
            f"{RANK_MIN_LEG_BETA}, rank_max_gross={RANK_MAX_GROSS}."
        ),
        "null_field_reasons": dict(NULL_FIELD_REASONS),
    }


def build_walk_forward_rank(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the full walk-forward and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")
    returns = load_prices(path, benchmark=BENCHMARK, min_rows=2, quality=False)
    n_rows = len(returns)
    needed = TRAIN_WINDOW + TEST_WINDOW * N_FOLDS
    if n_rows < needed:
        raise ValueError(
            f"fixture has {n_rows} return rows but walk-forward needs {needed}"
        )
    fixture_sha = _sha256(path)
    folds = []
    for k in range(N_FOLDS):
        train_end = TRAIN_WINDOW + TEST_WINDOW * k
        test_start = train_end
        test_end = test_start + TEST_WINDOW
        oos = _run_fold(returns, test_start, test_end)
        folds.append(
            {
                "fold": k,
                "train_start": 0,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "n_train": train_end,
                "n_test": test_end - test_start,
                **oos,
            }
        )
    oos_sharpes = [fold["oos_sharpe"] for fold in folds if fold["oos_sharpe"] is not None]
    if oos_sharpes:
        mean_oos_sharpe = _clean(sum(oos_sharpes) / len(oos_sharpes))
        median_oos_sharpe = _clean(statistics.median(oos_sharpes))
        fraction_positive = _clean(
            sum(1 for s in oos_sharpes if s > 0) / len(oos_sharpes)
        )
    else:
        mean_oos_sharpe = None
        median_oos_sharpe = None
        fraction_positive = None

    def _mean(field):
        vals = [fold[field] for fold in folds if fold[field] is not None]
        return _clean(sum(vals) / len(vals)) if vals else None

    aggregate = {
        "mean_oos_sharpe": mean_oos_sharpe,
        "median_oos_sharpe": median_oos_sharpe,
        "fraction_positive_oos_sharpe": fraction_positive,
        "total_oos_rows": sum(fold["n_test"] for fold in folds),
        "mean_oos_vol": _mean("oos_vol"),
        "mean_oos_max_drawdown": _mean("oos_max_drawdown"),
        "mean_oos_turnover": _mean("oos_turnover"),
        "mean_portfolio_beta": _mean("portfolio_beta"),
        "mean_beta_spread": _mean("beta_spread"),
        "mean_nonflat_rows": _mean("nonflat_rows"),
        "folds": folds,
        "candidates_evaluated": N_FOLDS,
    }

    return {
        "schema": SCHEMA,
        "seed": SEED,
        "n_folds": N_FOLDS,
        "train_window": TRAIN_WINDOW,
        "test_window": TEST_WINDOW,
        "beta_window": BETA_WINDOW,
        "long_quantile": LONG_QUANTILE,
        "short_quantile": SHORT_QUANTILE,
        "rank_min_leg_beta": RANK_MIN_LEG_BETA,
        "rank_max_gross": RANK_MAX_GROSS,
        "fixture_sha256": fixture_sha,
        "synthetic": True,
        "provenance": _provenance(returns, fixture_sha, n_rows),
        "aggregate": aggregate,
        "folds": folds,
    }


def run_walk_forward_rank(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the walk-forward, write JSON + markdown artifacts, return the dict."""
    payload = build_walk_forward_rank(fixture_path)
    write_artifacts(payload)
    return payload


def _format(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return value
    return f"{float(value):.{DECIMALS}f}"


def render_markdown(payload: dict) -> str:
    """Render the walk-forward folds and aggregate from the JSON object."""
    lines = [
        "| " + " | ".join(FOLD_FIELDS) + " |",
        "|" + "|".join("---" for _ in FOLD_FIELDS) + "|",
    ]
    for fold in payload["folds"]:
        cells = [_format(fold[field]) for field in FOLD_FIELDS]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("| key | value |")
    lines.append("|---|---|")
    aggregate = payload["aggregate"]
    aggregate_rows = [
        "| " + field + " | " + _format(aggregate[field]) + " |"
        for field in (
            "mean_oos_sharpe",
            "median_oos_sharpe",
            "fraction_positive_oos_sharpe",
            "total_oos_rows",
            "mean_oos_vol",
            "mean_oos_max_drawdown",
            "mean_oos_turnover",
            "mean_portfolio_beta",
            "mean_beta_spread",
            "mean_nonflat_rows",
            "candidates_evaluated",
        )
    ]
    lines.extend(aggregate_rows)
    lines.append("")
    lines.append("| fold_count | " + str(len(payload["folds"])) + " |")
    lines.append("| last_test_index | " + str(payload["folds"][-1]["test_end"] - 1) + " |")
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "walk_forward_rank.json"
    markdown_path = directory / "walk_forward_rank.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_walk_forward_rank()
    print(f"wrote {OUTPUT_DIR / 'walk_forward_rank.json'} ({len(payload['folds'])} folds)")
    print(f"wrote {OUTPUT_DIR / 'walk_forward_rank.md'}")


if __name__ == "__main__":
    main()
