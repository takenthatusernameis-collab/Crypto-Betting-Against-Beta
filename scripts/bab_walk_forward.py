#!/usr/bin/env python3
"""Deterministic P20 WP3 walk-forward (out-of-sample) harness for the BAB strategy.

Runs a fixed 5-fold expanding walk-forward over the committed synthetic fixture:
each fold selects a config on train rows only, then scores that config on the
untouched test slice. Nothing here is in-sample cherry-picking; the test slice
is never read during selection.

Writes two artifacts that are the load-bearing evidence for the campaign:

  research_state/bab_p20/walk_forward.json  -- machine-readable folds + aggregate
  research_state/bab_p20/walk_forward.md    -- table rendered from that JSON in memory

Equal-weight only (`weighting="equal"`). Rank weighting is intentionally absent:
it is not empirically evaluable on this 9-asset universe (see docs/BAB_FIDELITY.md
section 9.1). The fixture is a deterministic synthetic random walk, never real
market data, and no figure here is evidence of real profitability.

Usage:
  python3 scripts/bab_walk_forward.py
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p20.walk_forward/1"
FIXTURE_PATH = "tests/fixtures/real_market_prices.csv"
OUTPUT_DIR = "research_state/bab_p20"
BENCHMARK = "BTC"
MIN_OBSERVATIONS = 60
TRAIN_ROWS = 180
TEST_ROWS = 40
N_FOLDS = 5
BETA_WINDOWS = (30, 60, 90, 120)
QUANTILES = (0.2, 0.3)
TRANSACTION_COSTS = 0.001
BETA_NEUTRAL = True
WEIGHTING = "equal"
REBALANCE_FREQ = "daily"
FIXTURE_SEED = 20261028
KNOWN_GAP = "2021-09-17"
NAN_COLUMNS = ("DEL",)
DECIMALS = 6

LAST_TEST_INDEX = TRAIN_ROWS + TEST_ROWS * N_FOLDS - 1  # 379

FOLD_FIELDS = (
    "fold",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "n_train",
    "n_test",
    "selected_beta_window",
    "selected_long_quantile",
    "selected_short_quantile",
    "train_sharpe",
    "oos_sharpe",
    "oos_vol",
    "oos_max_drawdown",
    "oos_turnover",
    "oos_realized_beta",
    "oos_wealth",
)

AGGREGATE_FIELDS = (
    "mean_oos_sharpe",
    "median_oos_sharpe",
    "fraction_positive_oos_sharpe",
    "total_oos_rows",
    "folds",
    "candidates_evaluated",
)

NULL_FIELD_REASONS = {
    "train_sharpe": "undefined when train-slice returns have zero variance",
    "oos_sharpe": "undefined when OOS returns have zero variance",
    "oos_vol": "zero (never null) when fewer than two OOS returns exist",
    "oos_max_drawdown": "undefined when the OOS path is empty",
    "oos_turnover": "undefined when the OOS weight frame is empty",
    "oos_realized_beta": "undefined when the OOS benchmark has zero variance",
    "oos_wealth": "always finite (wealth index starts at 1.0)",
    "mean_oos_sharpe": "null when every fold's oos_sharpe is null",
    "median_oos_sharpe": "null when every fold's oos_sharpe is null",
    "fraction_positive_oos_sharpe": "null when no fold has a non-null oos_sharpe",
}


def _clean(value):
    """Round a float to the artifact precision, mapping non-finite to None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, DECIMALS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _provenance(prices: pd.DataFrame, returns: pd.DataFrame) -> dict:
    wanted_nan = [c for c in NAN_COLUMNS if c in prices.columns and prices[c].isna().all()]
    return {
        "fixture_path": FIXTURE_PATH,
        "fixture_sha256": _sha256(_REPO_ROOT / FIXTURE_PATH),
        "price_rows": len(prices),
        "return_rows": len(returns),
        "date_first": str(prices["date"].iloc[0]),
        "date_last": str(prices["date"].iloc[-1]),
        "synthetic": True,
        "seed": FIXTURE_SEED,
        "known_gap": KNOWN_GAP,
        "nan_columns": wanted_nan,
        "synthetic_fixture": (
            "This fixture is a deterministic synthetic random walk generated with a "
            "fixed seed; it is not real market data and its returns are not evidence "
            "of real-world profitability."
        ),
        "selection_rule": (
            "For each fold, the candidate grid (beta_window x {30, 60, 90, 120} x "
            "quantile x {0.2, 0.3}, beta_neutral=True, transaction_costs=0.001, "
            "weighting='equal') is scored exclusively on train rows [0, train_end); "
            "the configuration with the highest train-slice Sharpe wins, ties broken "
            "by smaller beta_window then smaller quantile. The test slice is never "
            "read during selection."
        ),
        "no_lookahead": (
            "Fold k trains on rows [0, 180 + 40k) and tests on rows "
            "[180 + 40k, 220 + 40k), so max(train_index) < min(test_index) for every "
            "fold. Weights at row t depend on data through t-1 only (one-day lag), "
            "and the evaluation run over history [0, test_end) is scored only on "
            "rows [test_start, test_end). No test label ever influences selection."
        ),
        "null_field_reasons": dict(NULL_FIELD_REASONS),
    }


def _fold_bounds(k: int) -> tuple[int, int, int, int]:
    """Return (train_start, train_end, test_start, test_end) row positions for fold k."""
    train_start = 0
    train_end = TRAIN_ROWS + TEST_ROWS * k
    test_start = train_end
    test_end = test_start + TEST_ROWS
    return train_start, train_end, test_start, test_end


def _run_config(returns: pd.DataFrame, end: int, beta_window: int, quantile: float):
    """Run one config over history rows [0, end) and return the BABResult."""
    return BABStrategy(
        benchmark=BENCHMARK,
        beta_window=beta_window,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=quantile,
        short_quantile=quantile,
        transaction_costs=TRANSACTION_COSTS,
        beta_neutral=BETA_NEUTRAL,
        weighting=WEIGHTING,
    ).run(returns_df=returns.iloc[:end])


def _train_sharpe(
    returns: pd.DataFrame, train_end: int, beta_window: int, quantile: float
) -> float:
    result = _run_config(returns, train_end, beta_window, quantile)
    return metrics.sharpe_ratio(result.backtest["returns"])


def assert_train_before_test(train_index, test_index) -> None:
    """Reject any train/test index split that is not strictly train-before-test.

    Raises ``ValueError`` when ``max(train_index) >= min(test_index)``, i.e. when
    a selection or evaluation could have seen a test row.
    """
    train = [int(i) for i in train_index]
    test = [int(i) for i in test_index]
    if not train or not test:
        raise ValueError("train and test index sets must be non-empty")
    if max(train) >= min(test):
        raise ValueError(
            f"lookahead violation: train reaches row {max(train)} but test starts "
            f"at row {min(test)}"
        )


def select_on_train(returns: pd.DataFrame, train_end: int) -> tuple[int, float, float]:
    """Select the best config on train rows [0, train_end) only.

    Maximizes train-slice Sharpe; ties break by smaller beta_window, then smaller
    quantile. Iteration order is sorted and replacement is strict, so the first
    (smallest) config wins every tie. Returns (beta_window, quantile, train_sharpe).
    """
    best_key = None
    best = None
    for beta_window in BETA_WINDOWS:
        for quantile in QUANTILES:
            sharpe = _train_sharpe(returns, train_end, beta_window, quantile)
            sharpe_key = sharpe if (sharpe is not None and math.isfinite(sharpe)) else -math.inf
            key = (-sharpe_key, int(beta_window), float(quantile))
            if best_key is None or key < best_key:
                best_key = key
                best = (
                    int(beta_window),
                    float(quantile),
                    float(sharpe) if sharpe is not None else None,
                )
    return best


def _oos_metrics(
    returns: pd.DataFrame, test_start: int, test_end: int, beta_window: int, quantile: float
) -> dict:
    """Evaluate the selected config on OOS rows [test_start, test_end) only.

    The strategy runs over history [0, test_end) (weights at t use data <= t-1)
    and only rows [test_start, test_end) are scored.
    """
    result = _run_config(returns, test_end, beta_window, quantile)
    rets = result.backtest["returns"].iloc[test_start:test_end]
    bench = returns[BENCHMARK].iloc[test_start:test_end]
    cumulative = (1.0 + rets.astype("float64")).cumprod()
    wealth = float(cumulative.iloc[-1]) if len(cumulative) else 1.0
    return {
        "oos_sharpe": _clean(metrics.sharpe_ratio(rets)),
        "oos_vol": _clean(metrics.annualized_volatility(rets)),
        "oos_max_drawdown": _clean(metrics.max_drawdown(cumulative)),
        "oos_turnover": _clean(metrics.turnover(result.weights.iloc[test_start:test_end])),
        "oos_realized_beta": _clean(metrics.strategy_beta(rets, bench)),
        "oos_wealth": _clean(wealth),
    }


def build_walk_forward(fixture_path: str = FIXTURE_PATH) -> dict:
    """Run the full walk-forward and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    prices = pd.read_csv(path)
    returns = load_prices(path, benchmark=BENCHMARK)
    n_rows = len(returns)
    if n_rows <= LAST_TEST_INDEX:
        raise ValueError(
            f"fixture has {n_rows} return rows but walk-forward needs through row {LAST_TEST_INDEX}"
        )

    folds = []
    for k in range(N_FOLDS):
        train_start, train_end, test_start, test_end = _fold_bounds(k)
        assert_train_before_test(range(train_start, train_end), range(test_start, test_end))
        beta_window, quantile, train_sharpe = select_on_train(returns, train_end)
        oos = _oos_metrics(returns, test_start, test_end, beta_window, quantile)
        folds.append(
            {
                "fold": k,
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "n_train": train_end - train_start,
                "n_test": test_end - test_start,
                "selected_beta_window": beta_window,
                "selected_long_quantile": _clean(quantile),
                "selected_short_quantile": _clean(quantile),
                "train_sharpe": _clean(train_sharpe),
                **oos,
            }
        )

    oos_sharpes = [fold["oos_sharpe"] for fold in folds if fold["oos_sharpe"] is not None]
    if oos_sharpes:
        mean_oos_sharpe = _clean(sum(oos_sharpes) / len(oos_sharpes))
        median_oos_sharpe = _clean(statistics.median(oos_sharpes))
        fraction_positive = _clean(sum(1 for s in oos_sharpes if s > 0) / len(oos_sharpes))
    else:
        mean_oos_sharpe = None
        median_oos_sharpe = None
        fraction_positive = None

    aggregate = {
        "mean_oos_sharpe": mean_oos_sharpe,
        "median_oos_sharpe": median_oos_sharpe,
        "fraction_positive_oos_sharpe": fraction_positive,
        "total_oos_rows": sum(fold["n_test"] for fold in folds),
        "folds": folds,
        "candidates_evaluated": len(BETA_WINDOWS) * len(QUANTILES) * N_FOLDS,
    }

    return {
        "schema": SCHEMA,
        "provenance": _provenance(prices, returns),
        "aggregate": aggregate,
        "folds": folds,
    }


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
            "candidates_evaluated",
        )
    ]
    lines.extend(aggregate_rows)
    lines.append("")
    lines.append("| fold_count | " + str(len(payload["folds"])) + " |")
    lines.append("| last_test_index | " + str(LAST_TEST_INDEX) + " |")
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "walk_forward.json"
    markdown_path = directory / "walk_forward.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = build_walk_forward()
    json_path, markdown_path = write_artifacts(payload)
    print(f"wrote {json_path} ({len(payload['folds'])} folds)")
    print(f"wrote {markdown_path}")


if __name__ == "__main__":
    main()
