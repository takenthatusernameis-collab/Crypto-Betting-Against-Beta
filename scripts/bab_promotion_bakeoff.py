#!/usr/bin/env python3
"""P25 WP2 — deterministic equal-vs-rank out-of-sample bake-off.

Runs the equal-weight default and the Frazzini-Pedersen rank-weighted BAB book
on identical causal walk-forward folds of the P25 WP0 wide synthetic universe
(fixture ``tests/fixtures/wide_bab_universe.csv``), so rank weighting can be
compared to the equal-weight default and the evidence for the WP3
promote/no-promote decision is produced.

Each fold fits rolling beta on causal history [0, train_end), constructs the
book on the untouched test slice [test_start, test_end) with one-day lagged
weights (no lookahead), and scores out-of-sample: Sharpe, vol, max drawdown,
turnover, realized beta, portfolio beta, beta spread, and wealth — per fold,
per weighting. A per-fold delta (rank minus equal) and aggregate means + delta
Sharpe summarize the bake-off.

Writes two artifacts:

  research_state/bab_p25/promotion_bakeoff.json  -- machine-readable folds + aggregate + delta
  research_state/bab_p25/promotion_bakeoff.md    -- table rendered from that JSON in memory

Single entry point: ``run_promotion_bakeoff()`` returns the results dict and
writes the JSON + markdown artifacts.

Usage:
  python3 scripts/bab_promotion_bakeoff.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p25.promotion_bakeoff/1"
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

WEIGHTINGS = ("equal", "rank")

FOLD_FIELDS = (
    "fold",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "n_train",
    "n_test",
    "equal_oos_sharpe",
    "rank_oos_sharpe",
    "delta_oos_sharpe",
    "equal_oos_wealth",
    "rank_oos_wealth",
    "delta_oos_wealth",
    "equal_portfolio_beta",
    "rank_portfolio_beta",
    "delta_portfolio_beta",
    "equal_oos_turnover",
    "rank_oos_turnover",
    "delta_oos_turnover",
    "equal_nonflat_rows",
    "rank_nonflat_rows",
    "equal_beta_spread",
    "rank_beta_spread",
)
AGGREGATE_FIELDS = (
    "equal_mean_oos_sharpe",
    "rank_mean_oos_sharpe",
    "delta_mean_oos_sharpe",
    "equal_mean_oos_wealth",
    "rank_mean_oos_wealth",
    "delta_mean_oos_wealth",
    "equal_mean_portfolio_beta",
    "rank_mean_portfolio_beta",
    "delta_mean_portfolio_beta",
    "equal_mean_oos_turnover",
    "rank_mean_oos_turnover",
    "delta_mean_oos_turnover",
    "equal_mean_nonflat_rows",
    "rank_mean_nonflat_rows",
    "equal_mean_beta_spread",
    "rank_mean_beta_spread",
    "rank_beta_neutral_folds",
    "total_oos_rows",
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


def _strategy_config(weighting: str) -> dict:
    return dict(
        benchmark=BENCHMARK,
        beta_window=BETA_WINDOW,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=LONG_QUANTILE,
        short_quantile=SHORT_QUANTILE,
        transaction_costs=TRANSACTION_COSTS,
        beta_neutral=True,
        weighting=weighting,
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


def _score_fold(returns: pd.DataFrame, weighting: str, test_start: int, test_end: int) -> dict:
    """Run one weighting on causal history [0, test_end) and score [test_start, test_end)."""
    result = BABStrategy(**_strategy_config(weighting)).run(returns_df=returns.iloc[:test_end])
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
            "Each fold runs both weightings over causal history [0, test_end); weights at "
            "row t use the one-day backtest lag and rolling betas computed from returns "
            "through t-1, so the OOS return at row t is never used to weight itself. The "
            "test slice [test_start, test_end) is scored but never read during weight "
            "construction for that row. Equal and rank are run on identical folds."
        ),
        "weightings": list(WEIGHTINGS),
        "rank_rule": (
            "Frazzini-Pedersen rank weighting: long the lowest-beta quantile, short the "
            "highest-beta quantile, beta-neutral by construction, rank_min_leg_beta="
            f"{RANK_MIN_LEG_BETA}, rank_max_gross={RANK_MAX_GROSS}. Equal weighting is the "
            "dollar-neutral default (not beta-neutral)."
        ),
        "null_field_reasons": dict(NULL_FIELD_REASONS),
    }


def build_promotion_bakeoff(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the full equal-vs-rank bake-off and return the artifact dict. No file writes."""
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
            f"fixture has {n_rows} return rows but bake-off needs {needed}"
        )
    fixture_sha = _sha256(path)
    folds = []
    for k in range(N_FOLDS):
        train_end = TRAIN_WINDOW + TEST_WINDOW * k
        test_start = train_end
        test_end = test_start + TEST_WINDOW
        equal = _score_fold(returns, "equal", test_start, test_end)
        rank = _score_fold(returns, "rank", test_start, test_end)
        folds.append(
            {
                "fold": k,
                "train_start": 0,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "n_train": train_end,
                "n_test": test_end - test_start,
                "equal": equal,
                "rank": rank,
                "delta": {
                    key: _clean((rank.get(key) if rank.get(key) is not None else 0.0)
                                - (equal.get(key) if equal.get(key) is not None else 0.0))
                    if rank.get(key) is not None and equal.get(key) is not None
                    else None
                    for key in (
                        "oos_sharpe", "oos_wealth", "portfolio_beta",
                        "oos_turnover", "beta_spread",
                    )
                },
            }
        )

    def _mean(folds, weighting, field):
        vals = [fold[weighting][field] for fold in folds if fold[weighting].get(field) is not None]
        return _clean(sum(vals) / len(vals)) if vals else None

    equal_sharpes = [
        fold["equal"]["oos_sharpe"]
        for fold in folds
        if fold["equal"]["oos_sharpe"] is not None
    ]
    rank_sharpes = [
        fold["rank"]["oos_sharpe"]
        for fold in folds
        if fold["rank"]["oos_sharpe"] is not None
    ]
    delta_sharpe = None
    if equal_sharpes and rank_sharpes:
        delta_sharpe = _clean(
            sum(rank_sharpes) / len(rank_sharpes)
            - sum(equal_sharpes) / len(equal_sharpes)
        )

    rank_neutral_folds = sum(
        1 for fold in folds
        if fold["rank"]["portfolio_beta"] is not None and abs(fold["rank"]["portfolio_beta"]) < 1e-2
    )

    aggregate = {
        "weightings": list(WEIGHTINGS),
        "equal": {
            "mean_oos_sharpe": _mean(folds, "equal", "oos_sharpe"),
            "mean_oos_vol": _mean(folds, "equal", "oos_vol"),
            "mean_oos_max_drawdown": _mean(folds, "equal", "oos_max_drawdown"),
            "mean_oos_turnover": _mean(folds, "equal", "oos_turnover"),
            "mean_oos_realized_beta": _mean(folds, "equal", "oos_realized_beta"),
            "mean_oos_wealth": _mean(folds, "equal", "oos_wealth"),
            "mean_portfolio_beta": _mean(folds, "equal", "portfolio_beta"),
            "mean_beta_spread": _mean(folds, "equal", "beta_spread"),
            "mean_long_leg_beta": _mean(folds, "equal", "long_leg_beta"),
            "mean_short_leg_beta": _mean(folds, "equal", "short_leg_beta"),
            "mean_nonflat_rows": _mean(folds, "equal", "nonflat_rows"),
        },
        "rank": {
            "mean_oos_sharpe": _mean(folds, "rank", "oos_sharpe"),
            "mean_oos_vol": _mean(folds, "rank", "oos_vol"),
            "mean_oos_max_drawdown": _mean(folds, "rank", "oos_max_drawdown"),
            "mean_oos_turnover": _mean(folds, "rank", "oos_turnover"),
            "mean_oos_realized_beta": _mean(folds, "rank", "oos_realized_beta"),
            "mean_oos_wealth": _mean(folds, "rank", "oos_wealth"),
            "mean_portfolio_beta": _mean(folds, "rank", "portfolio_beta"),
            "mean_beta_spread": _mean(folds, "rank", "beta_spread"),
            "mean_long_leg_beta": _mean(folds, "rank", "long_leg_beta"),
            "mean_short_leg_beta": _mean(folds, "rank", "short_leg_beta"),
            "mean_nonflat_rows": _mean(folds, "rank", "nonflat_rows"),
        },
        "delta_mean_oos_sharpe": delta_sharpe,
        "rank_beta_neutral_folds": rank_neutral_folds,
        "total_oos_rows": sum(fold["n_test"] for fold in folds),
        "folds": folds,
        "candidates_evaluated": N_FOLDS * len(WEIGHTINGS),
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
        "weightings": list(WEIGHTINGS),
        "fixture_sha256": fixture_sha,
        "synthetic": True,
        "provenance": _provenance(returns, fixture_sha, n_rows),
        "aggregate": aggregate,
        "folds": folds,
    }


def run_promotion_bakeoff(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the bake-off, write JSON + markdown artifacts, return the dict."""
    payload = build_promotion_bakeoff(fixture_path)
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
    """Render the bake-off folds and aggregate from the JSON object."""
    lines = [
        "| " + " | ".join(FOLD_FIELDS) + " |",
        "|" + "|".join("---" for _ in FOLD_FIELDS) + "|",
    ]
    for fold in payload["folds"]:
        e = fold["equal"]
        r = fold["rank"]
        d = fold["delta"]
        cells = [
            _format(fold[field]) if field not in (
                "equal_oos_sharpe", "rank_oos_sharpe", "delta_oos_sharpe",
                "equal_oos_wealth", "rank_oos_wealth", "delta_oos_wealth",
                "equal_portfolio_beta", "rank_portfolio_beta", "delta_portfolio_beta",
                "equal_oos_turnover", "rank_oos_turnover", "delta_oos_turnover",
                "equal_nonflat_rows", "rank_nonflat_rows",
                "equal_beta_spread", "rank_beta_spread",
            ) else _format({
                "equal_oos_sharpe": e["oos_sharpe"],
                "rank_oos_sharpe": r["oos_sharpe"],
                "delta_oos_sharpe": d["oos_sharpe"],
                "equal_oos_wealth": e["oos_wealth"],
                "rank_oos_wealth": r["oos_wealth"],
                "delta_oos_wealth": d["oos_wealth"],
                "equal_portfolio_beta": e["portfolio_beta"],
                "rank_portfolio_beta": r["portfolio_beta"],
                "delta_portfolio_beta": d["portfolio_beta"],
                "equal_oos_turnover": e["oos_turnover"],
                "rank_oos_turnover": r["oos_turnover"],
                "delta_oos_turnover": d["oos_turnover"],
                "equal_nonflat_rows": e["nonflat_rows"],
                "rank_nonflat_rows": r["nonflat_rows"],
                "equal_beta_spread": e["beta_spread"],
                "rank_beta_spread": r["beta_spread"],
            }[field])
            for field in FOLD_FIELDS
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("| key | value |")
    lines.append("|---|---|")
    aggregate = payload["aggregate"]
    for field in AGGREGATE_FIELDS:
        if field in ("equal", "rank", "folds"):
            continue
        value = aggregate.get(field)
        lines.append("| " + field + " | " + _format(value) + " |")
    lines.append("")
    lines.append("| fold_count | " + str(len(payload["folds"])) + " |")
    lines.append("| last_test_index | " + str(payload["folds"][-1]["test_end"] - 1) + " |")
    lines.append("| delta_rule | rank_mean_oos_sharpe - equal_mean_oos_sharpe |")
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "promotion_bakeoff.json"
    markdown_path = directory / "promotion_bakeoff.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_promotion_bakeoff()
    print(
        "wrote "
        f"{OUTPUT_DIR / 'promotion_bakeoff.json'} "
        f"({len(payload['folds'])} folds x {len(WEIGHTINGS)} weightings)"
    )
    print(f"wrote {OUTPUT_DIR / 'promotion_bakeoff.md'}")


if __name__ == "__main__":
    main()
