#!/usr/bin/env python3
"""Example: load real price/return data and run BABStrategy.

This is the canonical real-data contract for the BAB strategy. It documents
the expected schema and shows how to swap a ``returns_df`` into
``BABStrategy.run()``.

## Schema contract (what the validator enforces)

A returns DataFrame must have:

* a ``DatetimeIndex`` (timezone-aware values are converted to naive UTC),
  sorted ascending, with no duplicate timestamps;
* one column per asset plus the benchmark, each with a stripped string name;
* every cell coercible to ``float64`` (commas as thousand separators, ``%``
  suffixes, and the NA markers ``na``/``n/a``/``nan``/``none``/``null``/
  ``#n/a``/``#na``/``missing`` are all handled);
* no ``inf`` values;
* at least ``min_rows`` rows and at least ``min_rows`` finite observations per
  asset (including the benchmark);
* a benchmark column with at least one finite value;
* at least one non-benchmark asset column.

## Price vs returns

Pass **prices** (e.g. closing prices) and the loader computes simple returns via
``pct_change``; pass **returns** directly and they are validated as-is. The
fixture at ``tests/fixtures/real_market_prices.csv`` exercises the price path
and includes a deliberate date gap and an all-NaN delisted column.

## Defaults remain synthetic

Do not remove the synthetic defaults; they keep smoke runs reproducible.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices, load_returns

# Default fixture shipped with the repo; replace with your own real data.
DEFAULT_PRICES_CSV = Path("tests/fixtures/real_market_prices.csv")


def example_with_returns_csv(csv_path: str | Path, benchmark: str = "BTC"):
    """Load returns from CSV and run strategy."""
    returns_df = load_returns(csv_path, benchmark=benchmark, min_rows=60)
    strategy = BABStrategy()
    result = strategy.run(returns_df=returns_df)
    return result


def example_with_prices_csv(csv_path: str | Path, benchmark: str = "BTC"):
    """Load prices from CSV, convert to returns, then run strategy."""
    returns_df = load_prices(csv_path, benchmark=benchmark, min_rows=60)
    strategy = BABStrategy()
    result = strategy.run(returns_df=returns_df)
    return result


def example_in_memory():
    """Build a minimal in-memory returns DataFrame (daily returns).

    The values here are illustrative only; in practice substitute real
    returns. The schema is what matters: DatetimeIndex + numeric columns.
    """
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    df = pd.DataFrame(
        {
            "BTC": 0.001 * (pd.Series(range(150)) % 5 - 2).values,
            "ETH": 0.001 * (pd.Series(range(150)) % 7 - 3).values,
            "SOL": 0.002 * (pd.Series(range(150)) % 3 - 1).values,
        },
        index=dates,
    )
    returns_df = load_returns(df, benchmark="BTC", min_rows=60)
    strategy = BABStrategy()
    return strategy.run(returns_df=returns_df)


def example_with_real_fixture(benchmark: str = "BTC"):
    """Run the strategy on the shipped real-market price fixture.

    Demonstrates the full contract: prices -> returns -> strategy. The
    fixture contains a date gap and an all-NaN delisted column that the
    loader must tolerate.
    """
    returns_df = load_prices(DEFAULT_PRICES_CSV, benchmark=benchmark, min_rows=60)
    strategy = BABStrategy()
    result = strategy.run(returns_df=returns_df)
    return result


if __name__ == "__main__":
    # Replace with your real data paths:
    # res = example_with_returns_csv("your_returns.csv", benchmark="BTC")
    # res = example_with_prices_csv("your_prices.csv", benchmark="BTC")
    res = example_with_real_fixture()
    print(float(res.backtest["cumulative"].iloc[-1]))