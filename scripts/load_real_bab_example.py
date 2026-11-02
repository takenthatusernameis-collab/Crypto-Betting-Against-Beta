#!/usr/bin/env python3
"""
Example: Load real returns data and run BABStrategy.

This script shows the concrete contract for swapping in real data:
- CSV/JSON/JSONL/Parquet/HDF5/Pickle with datetime index/column and numeric return columns per asset
- Use load_returns() for validation/coercion/normalization (tz-aware -> UTC naive, dedup, drop all-NaN, numeric coercion)
- Pass returns_df to BABStrategy.run(returns_df=...)
- Also demonstrates price->returns via load_prices() if needed
"""

from __future__ import annotations

import argparse
from pathlib import Path

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import BABDataError, load_prices, load_returns


def main() -> int:
    parser = argparse.ArgumentParser(description="Load real returns/price data and run BAB")
    parser.add_argument("data_path", type=str, help="Path to data file (CSV/JSON/JSONL/Parquet/HDF5/Pickle). For prices use --from-prices")
    parser.add_argument("--benchmark", type=str, default="BTC", help="Benchmark symbol column name")
    parser.add_argument("--min-rows", type=int, default=30, help="Minimum rows/finite history")
    parser.add_argument("--lookback", type=int, default=252, help="Rolling beta lookback")
    parser.add_argument("--quantile", type=float, default=0.3, help="Quantile for long/short")
    parser.add_argument("--transaction-cost", type=float, default=0.001, help="Transaction cost per unit turnover")
    parser.add_argument("--from-prices", action="store_true", help="Treat input as prices and convert to returns via load_prices()")
    parser.add_argument("--universe", type=str, nargs="*", help="Optional universe override (must intersect data)")
    args = parser.parse_args()

    data_path = Path(args.data_path)
    if not data_path.exists():
        raise SystemExit(f"File not found: {data_path}")

    try:
        if args.from_prices:
            returns_df = load_prices(data_path, benchmark=args.benchmark, min_rows=args.min_rows)
        else:
            returns_df = load_returns(data_path, benchmark=args.benchmark, min_rows=args.min_rows)
    except BABDataError as exc:
        raise SystemExit(f"Data load/validation failed: {exc}") from exc

    strat = BABStrategy(
        benchmark=args.benchmark,
        universe=args.universe,
        beta_window=args.lookback,
        long_quantile=args.quantile,
        short_quantile=args.quantile,
        transaction_costs=args.transaction_cost,
    )
    result = strat.run(returns_df=returns_df)
    cum = result.backtest["cumulative"].iloc[-1]
    print(f"cumulative_return={float(cum):.6f}")
    print(f"periods={len(result.backtest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
