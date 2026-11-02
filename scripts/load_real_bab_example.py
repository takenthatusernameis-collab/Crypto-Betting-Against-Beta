#!/usr/bin/env python3
"""Example script for loading real data into BAB strategy.

Demonstrates how to swap real price/returns data into BABStrategy.run().
Keep synthetic defaults intact - this just shows the contract.
"""
from __future__ import annotations

from pathlib import Path

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import (
    load_prices,
    load_returns,
    validate_returns_dataframe,
)


def example_with_returns_csv(csv_path: str | Path, benchmark: str = "BTC"):
    """Load pre-computed daily returns from CSV."""
    returns_df = load_returns(csv_path, benchmark=benchmark, min_rows=60)
    strategy = BABStrategy()
    result = strategy.run(returns_df=returns_df)
    print(f"Cumulative return: {result.backtest['cumulative'].iloc[-1]:.4f}")
    return result


def example_with_prices_csv(csv_path: str | Path, benchmark: str = "BTC"):
    """Load daily prices from CSV and convert to returns."""
    returns_df = load_prices(csv_path, benchmark=benchmark, min_rows=2)
    strategy = BABStrategy()
    result = strategy.run(returns_df=returns_df)
    print(f"Cumulative return: {result.backtest['cumulative'].iloc[-1]:.4f}")
    return result


if __name__ == "__main__":
    # Example usage (replace paths with your real data):
    # example_with_prices_csv("data/prices.csv", benchmark="BTC")
    # example_with_returns_csv("data/returns.csv", benchmark="BTC")
    print("Edit this script to point to your real price/returns files.")
