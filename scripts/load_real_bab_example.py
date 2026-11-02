#!/usr/bin/env python3
"""
Example: Load real returns data and run BABStrategy.

This script shows the concrete contract for swapping in real data:
- CSV with datetime index/column and numeric return columns per asset
- Use load_returns() for validation/coercion/normalization
- Pass returns_df to BABStrategy.run(returns_df=...)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import BABDataError, load_returns


def main() -> int:
    parser = argparse.ArgumentParser(description="Load real returns CSV and run BAB")
    parser.add_argument("csv_path", type=str, help="Path to CSV of returns (datetime index or column)")
    parser.add_argument("--benchmark", type=str, default="BTC", help="Benchmark symbol column name")
    parser.add_argument("--min-rows", type=int, default=30, help="Minimum rows/finite history")
    parser.add_argument("--lookback", type=int, default=252, help="Rolling beta lookback")
    parser.add_argument("--quantile", type=float, default=0.3, help="Quantile for long/short")
    parser.add_argument("--transaction-cost", type=float, default=0.001, help="Transaction cost per unit turnover")
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise SystemExit(f"File not found: {csv_path}")

    # Load and validate real data using the hardened loader contract
    returns_df = load_returns(csv_path, benchmark=args.benchmark, min_rows=args.min_rows)

    # Run strategy with validated real data
    strat = BABStrategy(
        benchmark=args.benchmark,
        lookback=args.lookback,
        quantile=args.quantile,
        transaction_cost=args.transaction_cost,
    )
    result = strat.run(returns_df=returns_df)
    cum = result.backtest["cumulative"].iloc[-1]
    print(f"cumulative_return={float(cum):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
