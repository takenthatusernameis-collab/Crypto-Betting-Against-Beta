#!/usr/bin/env python3
"""Example: load real price/return data and run BABStrategy.

This shows the expected schema for real data:
- DataFrame with a DatetimeIndex (date/time)
- Numeric columns for assets and benchmark (e.g., BTC, ETH, ...)
- Either returns (daily/simple returns) or prices (converted via pct_change)

Defaults remain synthetic if you don't pass returns_df. Do not remove synthetic defaults.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices, load_returns


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
    """Build a minimal in-memory returns DataFrame (daily returns)."""
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    df = pd.DataFrame(
        {
            "BTC": 0.001 * (pd.Series(range(150)) % 5 - 2).values,
            "ETH": 0.001 * (pd.Series(range(150)) % 7 - 3).values,
            "SOL": 0.002 * (pd.Series(range(150)) % 3 - 1).values,
        },
        index=dates,
    )
    # df here is just example structure - in practice use real returns
    returns_df = load_returns(df, benchmark="BTC", min_rows=60)
    strategy = BABStrategy()
    return strategy.run(returns_df=returns_df)


if __name__ == "__main__":
    # Replace with your real data paths
    # res = example_with_returns_csv("your_returns.csv", benchmark="BTC")
    # res = example_with_prices_csv("your_prices.csv", benchmark="BTC")
    res = example_in_memory()
    print(float(res.backtest["cumulative"].iloc[-1]))
