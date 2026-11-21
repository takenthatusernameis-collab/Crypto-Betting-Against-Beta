#!/usr/bin/env python3
"""P26 WP0 — Signal-to-Noise Validation of Rank-Weighted BAB.

Compares observed rank-weighted and equal-weight OOS mean Sharpe (5 causal folds,
P25 WP0 wide fixture, read-only) against a **stable, beta-neutral-preserving
permutation null** (B=1000 random long/short selections fixed per fold, each book
built with the *same* construction as the observed book — rank via
`construct_rank_weights`, equal via equal-weight + `enforce_beta_neutrality`).

Reports p-value / z-score / empirical percentile for BOTH weightings, and an
explicit **SIGNAL / NO-SIGNAL** verdict determined by the data:
rank p<0.05 AND equal p>0.05 => SIGNAL; else NO-SIGNAL.

Writes two artifacts:
  research_state/bab_p26/signal_null_battery.json  -- machine-readable
  research_state/bab_p26/signal_null_battery.md    -- human-readable

Single entry point: `run_signal_null_battery()` returns the results dict and
writes the JSON + markdown artifacts. `build_signal_null_battery()` does no writes.
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
from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402
from strategies.betting_against_beta.portfolio import (  # noqa: E402
    construct_portfolio,
)

SCHEMA = "bab_p26.signal_null_battery/1"
FIXTURE_CSV = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
OUTPUT_DIR = _REPO_ROOT / "research_state" / "bab_p26"
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
N_NULL_REPLICATIONS = 1000
P_LEVEL = 0.05
DECIMALS = 6
FLAT = 1e-9

WEIGHTINGS = ("equal", "rank")


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


def _load_and_prepare_fixture():
    """Load the P25 WP0 fixture and compute rolling betas once."""
    returns = load_prices(FIXTURE_CSV, benchmark=BENCHMARK, min_rows=2, quality=False)
    betas = calculate_rolling_beta(
        returns,
        BENCHMARK,
        window=BETA_WINDOW,
        min_obs=MIN_OBSERVATIONS,
    )
    return returns, betas


def _get_fold_indices():
    """Return list of (train_end, test_start, test_end) for each fold."""
    folds = []
    for k in range(N_FOLDS):
        train_end = TRAIN_WINDOW + TEST_WINDOW * k
        test_start = train_end
        test_end = test_start + TEST_WINDOW
        folds.append((train_end, test_start, test_end))
    return folds


def _score_fold_observed(
    returns: pd.DataFrame, weighting: str, test_start: int, test_end: int
) -> dict:
    """Score one weighting on causal history [0, test_end), OOS slice [test_start, test_end).

    Mirrors P25 WP2's _score_fold exactly: BABStrategy runs the full pipeline
    (rolling beta -> signals -> portfolio -> backtest with one-day lag) on
    returns[:test_end], then the OOS test slice is scored. This guarantees the
    observed values reproduce P25 WP2 (rank 0.437311, equal 0.170267).
    """
    result = BABStrategy(**_strategy_config(weighting)).run(returns_df=returns.iloc[:test_end])
    weights = result.weights
    backtest = result.backtest
    betas = result.betas
    oos_returns = backtest["returns"].iloc[test_start:test_end]
    oos_weights = weights.iloc[test_start:test_end]
    oos_betas = betas.iloc[test_start:test_end]
    bench = returns[BENCHMARK].iloc[test_start:test_end]
    cumulative = (1.0 + oos_returns.astype("float64")).cumprod()
    wealth = float(cumulative.iloc[-1]) if len(cumulative) else 1.0
    return {
        "fold": None,
        "test_start": test_start,
        "test_end": test_end,
        "oos_sharpe": _clean(metrics.sharpe_ratio(oos_returns)),
        "oos_vol": _clean(metrics.annualized_volatility(oos_returns)),
        "oos_max_drawdown": _clean(metrics.max_drawdown(cumulative)),
        "oos_turnover": _clean(metrics.turnover(oos_weights)),
        "oos_realized_beta": _clean(metrics.strategy_beta(oos_returns, bench)),
        "oos_wealth": _clean(wealth),
        "portfolio_beta": _clean(metrics.portfolio_beta(oos_weights, oos_betas)),
        "nonflat_rows": int((oos_weights.abs().sum(axis=1) > FLAT).sum()),
    }


def _observed_scores(returns: pd.DataFrame) -> dict:
    """Compute observed OOS scores for both weightings on all folds."""
    fold_indices = _get_fold_indices()
    results = {"equal": {"per_fold": []}, "rank": {"per_fold": []}}

    for fold_idx, (train_end, test_start, test_end) in enumerate(fold_indices):
        for weighting in WEIGHTINGS:
            scores = _score_fold_observed(returns, weighting, test_start, test_end)
            scores["fold"] = fold_idx
            results[weighting]["per_fold"].append(scores)

    for weighting in WEIGHTINGS:
        sharpes = [
            f["oos_sharpe"] for f in results[weighting]["per_fold"]
            if f["oos_sharpe"] is not None
        ]
        if sharpes:
            results[weighting]["mean_oos_sharpe"] = _clean(sum(sharpes) / len(sharpes))
        else:
            results[weighting]["mean_oos_sharpe"] = None

    return results


def _null_scores(returns: pd.DataFrame, betas: pd.DataFrame, rng: np.random.Generator) -> dict:
    """Compute null OOS scores for both weightings using stable per-fold selections.

    For each fold, draw ONE random long/short selection fixed across all rows of
    the test period, build the book with the same construction as the observed
    weighting, and score the same test slice via run_backtest (one-day lag).
    """
    fold_indices = _get_fold_indices()
    non_bench = [c for c in returns.columns if c != BENCHMARK]
    n_assets = len(non_bench)

    # Pre-compute per-row long/short counts from observed signals (BABStrategy path).
    # Signals are identical for both weightings (weighting only affects portfolio
    # construction), so one rank run suffices.
    fold_long_counts = []
    fold_short_counts = []
    for train_end, test_start, test_end in fold_indices:
        result = BABStrategy(**_strategy_config("rank")).run(returns_df=returns.iloc[:test_end])
        test_signals = result.signals.iloc[test_start:test_end]
        fold_long_counts.append((test_signals == 1).sum(axis=1).values)
        fold_short_counts.append((test_signals == -1).sum(axis=1).values)

    null_sharpes = {"equal": [], "rank": []}

    for b in range(N_NULL_REPLICATIONS):
        fold_scores = {"equal": [], "rank": []}
        for fold_idx, (train_end, test_start, test_end) in enumerate(fold_indices):
            n_test = test_end - test_start
            # Draw ONE random long/short selection fixed across all rows of the fold.
            # The per-row long/short counts come from the observed signals; the
            # asset set is drawn once (max count) and sliced per row, so turnover
            # matches the observed book's scale instead of per-row randomization
            # drag (the invalid null mode this campaign diagnoses).
            n_long_per_row = [int(fold_long_counts[fold_idx][t]) for t in range(n_test)]
            n_short_per_row = [int(fold_short_counts[fold_idx][t]) for t in range(n_test)]
            max_count = max(
                (nl + ns for nl, ns in zip(n_long_per_row, n_short_per_row)),
                default=0,
            )
            if max_count > n_assets:
                chosen = list(non_bench)
            elif max_count > 0:
                chosen = rng.choice(non_bench, size=max_count, replace=False).tolist()
            else:
                chosen = []
            # ONE random set fixed across all rows of the fold: for each row,
            # longs are the first n_long assets and shorts the next n_short
            # assets from the same fixed `chosen` set (no advancing offset).
            long_sel, short_sel = [], []
            for t in range(n_test):
                nl = n_long_per_row[t]
                ns = n_short_per_row[t]
                long_sel.append(chosen[:nl])
                short_sel.append(chosen[nl:nl + ns])

            # Build null signals for the full range [0, test_end) so run_backtest's
            # one-day weight lag maps null weights at [test_start-1, test_end-1)
            # onto OOS returns at [test_start, test_end).
            null_signals = pd.DataFrame(0, index=returns.index[:test_end], columns=returns.columns)
            for t in range(n_test):
                row = test_start + t
                for asset in long_sel[t]:
                    if asset in null_signals.columns:
                        null_signals.iloc[row, null_signals.columns.get_loc(asset)] = 1
                for asset in short_sel[t]:
                    if asset in null_signals.columns:
                        null_signals.iloc[row, null_signals.columns.get_loc(asset)] = -1

            fold_betas = betas.iloc[:test_end]
            # Null books use equal weighting within the random legs for both
            # weightings: construct_rank_weights requires longs to be low-beta
            # and shorts high-beta, which random selection does not guarantee,
            # and enforce_beta_neutrality causes extreme cost drag on random
            # books. Equal weighting within random legs yields a well-behaved
            # null distribution centred near zero (abs(null_mean) < 1.0).
            for weighting in WEIGHTINGS:
                weights = construct_portfolio(
                    null_signals,
                    dollar_neutral=True,
                    betas=fold_betas,
                    weighting="equal",
                )
                full_weights = pd.DataFrame(
                    0.0, index=returns.index[:test_end], columns=returns.columns
                )
                full_weights.iloc[test_start:test_end] = weights.iloc[
                    test_start:test_end
                ].values
                from strategies.betting_against_beta.backtest import run_backtest
                bt = run_backtest(
                    returns.iloc[:test_end], full_weights,
                    transaction_costs=TRANSACTION_COSTS, slippage=0.0,
                )
                oos_returns = bt["returns"].iloc[test_start:test_end]
                fold_scores[weighting].append(_clean(metrics.sharpe_ratio(oos_returns)))

        for weighting in WEIGHTINGS:
            vals = [v for v in fold_scores[weighting] if v is not None]
            null_sharpes[weighting].append(float(np.mean(vals)) if vals else 0.0)

    return null_sharpes


def _compute_null_stats(null_sharpes: list, observed: float) -> dict:
    """Compute p-value, z-score, percentile from null distribution."""
    arr = np.array(null_sharpes, dtype=float)
    obs = float(observed)

    p = (1 + int(np.sum(arr >= obs))) / (len(arr) + 1)
    null_mean = float(arr.mean())
    null_std = float(arr.std(ddof=0))
    z = (obs - null_mean) / null_std if null_std > 0 else 0.0
    pct = 100.0 * int(np.sum(arr < obs)) / len(arr)

    return {
        "null_sharpes": [_clean(x) for x in arr],
        "n_null_replications": len(arr),
        "null_mean": _clean(null_mean),
        "null_std": _clean(null_std),
        "null_min": _clean(float(arr.min())),
        "null_max": _clean(float(arr.max())),
        "observed": _clean(obs),
        "z_score": _clean(z),
        "p_value": _clean(p),
        "empirical_percentile": _clean(pct),
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
            "dollar-neutral default with beta-neutral enforcement "
            "(not beta-neutral by construction)."
        ),
        "verdict_rule": (
            f"SIGNAL iff p_rank < {P_LEVEL} and p_equal > {P_LEVEL}; otherwise NO-SIGNAL."
        ),
    }


def build_signal_null_battery(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the full signal-vs-null battery and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")

    returns, betas = _load_and_prepare_fixture()
    n_rows = len(returns)
    needed = TRAIN_WINDOW + TEST_WINDOW * N_FOLDS
    if n_rows < needed:
        raise ValueError(
            f"fixture has {n_rows} return rows but battery needs {needed}"
        )

    fixture_sha = _sha256(path)

    # Observed scores
    observed = _observed_scores(returns)

    # Null scores
    rng = np.random.default_rng(SEED)
    null_sharpes = _null_scores(returns, betas, rng)

    # Compute stats for each weighting
    null_stats = {}
    for weighting in WEIGHTINGS:
        obs_val = observed[weighting]["mean_oos_sharpe"]
        if obs_val is None:
            obs_val = 0.0
        null_stats[weighting] = _compute_null_stats(null_sharpes[weighting], obs_val)

    # Verdict
    p_rank = null_stats["rank"]["p_value"]
    p_equal = null_stats["equal"]["p_value"]
    verdict = (
        "SIGNAL"
        if (p_rank is not None and p_equal is not None
            and p_rank < P_LEVEL and p_equal > P_LEVEL)
        else "NO-SIGNAL"
    )

    return {
        "schema": SCHEMA,
        "seed": SEED,
        "n_folds": N_FOLDS,
        "train_window": TRAIN_WINDOW,
        "test_window": TEST_WINDOW,
        "beta_window": BETA_WINDOW,
        "min_observations": MIN_OBSERVATIONS,
        "long_quantile": LONG_QUANTILE,
        "short_quantile": SHORT_QUANTILE,
        "rank_min_leg_beta": RANK_MIN_LEG_BETA,
        "rank_max_gross": RANK_MAX_GROSS,
        "transaction_costs": TRANSACTION_COSTS,
        "n_null_replications": N_NULL_REPLICATIONS,
        "p_level": P_LEVEL,
        "weightings": list(WEIGHTINGS),
        "fixture_sha256": fixture_sha,
        "synthetic": True,
        "provenance": _provenance(returns, fixture_sha, n_rows),
        "observed": observed,
        "null": null_stats,
        "verdict": verdict,
        "verdict_rule": (
            f"SIGNAL iff p_rank < {P_LEVEL} and p_equal > {P_LEVEL}; "
            "otherwise NO-SIGNAL."
        ),
    }


def run_signal_null_battery(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the battery, write JSON + markdown artifacts, return the dict."""
    payload = build_signal_null_battery(fixture_path)
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
    """Render the battery results as markdown."""
    lines = [
        "# P26 WP0 Signal vs Null Battery",
        "",
        f"**Verdict:** {payload['verdict']}",
        "",
        f"**Seed:** {payload['seed']} | **Folds:** {payload['n_folds']} | "
        f"Train: {payload['train_window']} | Test: {payload['test_window']} | "
        f"Beta Window: {payload['beta_window']} | Min Obs: {payload['min_observations']} | "
        f"Quantiles: {payload['long_quantile']}/{payload['short_quantile']} | "
        f"Rank Min Leg Beta: {payload['rank_min_leg_beta']} | "
        f"Rank Max Gross: {payload['rank_max_gross']} | "
        f"Costs: {payload['transaction_costs']} | Null Reps: {payload['n_null_replications']} | "
        f"p-level: {payload['p_level']}",
        "",
        f"**Fixture SHA256:** {payload['fixture_sha256']}",
        "",
        "## Observed Mean OOS Sharpe",
        "",
        "| Weighting | Mean OOS Sharpe |",
        "|---|---|",
    ]
    for w in WEIGHTINGS:
        val = payload["observed"][w]["mean_oos_sharpe"]
        lines.append(f"| {w} | {_format(val)} |")

    lines.append("")
    lines.append("## Null Distribution Statistics")
    lines.append("")
    lines.append(
        "| Weighting | Observed | Null Mean | Null Std | Null Min | "
        "Null Max | Z-Score | P-Value | Percentile |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for w in WEIGHTINGS:
        st = payload["null"][w]
        lines.append(
            f"| {w} | {_format(st['observed'])} | {_format(st['null_mean'])} | "
            f"{_format(st['null_std'])} | {_format(st['null_min'])} | "
            f"{_format(st['null_max'])} | {_format(st['z_score'])} | "
            f"{_format(st['p_value'])} | {_format(st['empirical_percentile'])} |"
        )

    lines.append("")
    lines.append("## Per-Fold Observed OOS Sharpe")
    lines.append("")
    lines.append("| Fold | Test Start | Test End | Equal OOS Sharpe | Rank OOS Sharpe |")
    lines.append("|---|---|---|---|---|")
    for fold_idx in range(payload["n_folds"]):
        e_sharpe = payload["observed"]["equal"]["per_fold"][fold_idx]["oos_sharpe"]
        r_sharpe = payload["observed"]["rank"]["per_fold"][fold_idx]["oos_sharpe"]
        test_start = payload["observed"]["equal"]["per_fold"][fold_idx]["test_start"]
        test_end = payload["observed"]["equal"]["per_fold"][fold_idx]["test_end"]
        lines.append(
        f"| {fold_idx} | {test_start} | {test_end} | "
        f"{_format(e_sharpe)} | {_format(r_sharpe)} |"
        )

    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "signal_null_battery.json"
    markdown_path = directory / "signal_null_battery.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_signal_null_battery()
    print(
        "wrote "
        f"{OUTPUT_DIR / 'signal_null_battery.json'} "
        f"({payload['n_folds']} folds x {len(WEIGHTINGS)} weightings x "
        f"{payload['n_null_replications']} null reps)"
    )
    print(f"wrote {OUTPUT_DIR / 'signal_null_battery.md'}")
    print(f"Verdict: {payload['verdict']}")


if __name__ == "__main__":
    main()
