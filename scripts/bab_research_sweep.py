#!/usr/bin/env python3
"""Deterministic P20 WP0 research sweep for the BAB strategy.

Builds an 80-configuration in-process grid over the committed synthetic
fixture and writes two artifacts that are the load-bearing evidence for the
campaign:

  research_state/bab_p20/sweep.json  -- machine-readable rows + provenance
  research_state/bab_p20/sweep.md    -- table rendered from that JSON in memory

The sweep is equal-weight only. Rank weighting is intentionally absent: it is
not empirically evaluable on this 9-asset universe (see docs/BAB_FIDELITY.md
section 9.1). The fixture is a deterministic synthetic random walk, never real
market data.

Usage:
  python3 scripts/bab_research_sweep.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p20.sweep/1"
FIXTURE_PATH = "tests/fixtures/real_market_prices.csv"
OUTPUT_DIR = "research_state/bab_p20"
BENCHMARK = "BTC"
MIN_OBSERVATIONS = 60
BETA_WINDOWS = (30, 60, 90, 120, 180)
QUANTILES = (0.2, 0.3)
TRANSACTION_COSTS = (0.0, 0.001, 0.0025, 0.005)
BETA_NEUTRAL = (False, True)
IN_SAMPLE_WINDOWS = (180,)
FIXTURE_SEED = 20261028
KNOWN_GAP = "2021-09-17"
NAN_COLUMNS = ("DEL",)
DECIMALS = 6

ROW_FIELDS = (
    "beta_window",
    "long_quantile",
    "short_quantile",
    "transaction_costs",
    "beta_neutral",
    "weighting",
    "wealth",
    "sharpe",
    "model_beta",
    "realized_beta",
    "gross",
    "turnover",
)


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
        "in_sample_windows": list(IN_SAMPLE_WINDOWS),
        "synthetic_fixture": (
            "This fixture is a deterministic synthetic random walk generated with a "
            "fixed seed; it is not real market data and its returns are not evidence "
            "of real-world profitability."
        ),
        "metric_definitions": {
            "wealth": "final cumulative wealth index of the backtest (1.0 = start)",
            "sharpe": "annualized Sharpe ratio of daily backtest returns",
            "model_beta": "max over rows of |sum_i w_i*beta_i| (the book beta the model targets)",
            "realized_beta": "OLS beta of backtest returns against the BTC benchmark",
            "gross": "max over rows of sum_i |w_i| (gross exposure)",
            "turnover": "mean one-way turnover from weight changes",
        },
        "null_field_reasons": {},
    }


def _grid() -> dict:
    return {
        "beta_window": list(BETA_WINDOWS),
        "long_quantile": list(QUANTILES),
        "short_quantile": list(QUANTILES),
        "transaction_costs": list(TRANSACTION_COSTS),
        "beta_neutral": list(BETA_NEUTRAL),
        "weighting": ["equal"],
        "benchmark": BENCHMARK,
        "min_observations": MIN_OBSERVATIONS,
        "rebalance_freq": "daily",
        "configurations": (
            len(BETA_WINDOWS) * len(QUANTILES) * len(TRANSACTION_COSTS) * len(BETA_NEUTRAL)
        ),
    }


def _run_config(returns: pd.DataFrame, beta_window: int, quantile: float,
                transaction_costs: float, beta_neutral: bool) -> dict:
    result = BABStrategy(
        benchmark=BENCHMARK,
        beta_window=beta_window,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=quantile,
        short_quantile=quantile,
        transaction_costs=transaction_costs,
        beta_neutral=beta_neutral,
    ).run(returns_df=returns)

    weights = result.weights
    betas = result.betas.reindex(columns=weights.columns).fillna(0.0)
    book_beta = (weights * betas).sum(axis=1)
    backtest_returns = result.backtest["returns"]

    return {
        "beta_window": int(beta_window),
        "long_quantile": _clean(quantile),
        "short_quantile": _clean(quantile),
        "transaction_costs": _clean(transaction_costs),
        "beta_neutral": bool(beta_neutral),
        "weighting": "equal",
        "wealth": _clean(result.backtest["cumulative"].iloc[-1]),
        "sharpe": _clean(metrics.sharpe_ratio(backtest_returns)),
        "model_beta": _clean(book_beta.abs().max()),
        "realized_beta": _clean(metrics.strategy_beta(backtest_returns, returns[BENCHMARK])),
        "gross": _clean(weights.abs().sum(axis=1).max()),
        "turnover": _clean(metrics.turnover(weights)),
    }


def build_sweep(fixture_path: str = FIXTURE_PATH) -> dict:
    """Run the full grid and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    prices = pd.read_csv(path)
    returns = load_prices(path, benchmark=BENCHMARK)

    rows = [
        _run_config(returns, beta_window, quantile, transaction_costs, beta_neutral)
        for beta_window in BETA_WINDOWS
        for quantile in QUANTILES
        for transaction_costs in TRANSACTION_COSTS
        for beta_neutral in BETA_NEUTRAL
    ]

    return {
        "schema": SCHEMA,
        "provenance": _provenance(prices, returns),
        "grid": _grid(),
        "rows": rows,
    }


def _format(value) -> str:
    if value is None:
        return "None"
    return f"{float(value):.{DECIMALS}f}"


def render_markdown(sweep: dict) -> str:
    """Render the sweep rows as a markdown table derived from the JSON object."""
    columns = (
        "beta_window",
        "long_quantile",
        "short_quantile",
        "transaction_costs",
        "beta_neutral",
        "weighting",
        "wealth",
        "sharpe",
        "model_beta",
        "realized_beta",
        "gross",
        "turnover",
    )
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in sweep["rows"]:
        cells = []
        for column in columns:
            value = row[column]
            if isinstance(value, bool):
                cells.append(str(value))
            elif isinstance(value, str):
                cells.append(value)
            else:
                cells.append(_format(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write_artifacts(sweep: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "sweep.json"
    markdown_path = directory / "sweep.md"
    json_path.write_text(json.dumps(sweep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(sweep), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    sweep = build_sweep()
    json_path, markdown_path = write_artifacts(sweep)
    print(f"wrote {json_path} ({len(sweep['rows'])} rows)")
    print(f"wrote {markdown_path}")


if __name__ == "__main__":
    main()
