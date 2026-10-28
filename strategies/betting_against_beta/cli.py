"""Command-line interface for BAB strategy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import BABConfig
from .strategy import BABStrategy


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Betting Against Beta (BAB) crypto strategy")
    parser.add_argument("--data", type=str, help="Path to returns data (CSV/JSON/Parquet/HDF5/Pickle)")
    parser.add_argument("--benchmark", type=str, default="BTC", help="Benchmark symbol (default: BTC)")
    parser.add_argument("--universe", type=str, nargs="*", help="Universe of assets")
    parser.add_argument("--beta-window", type=int, default=90, help="Beta estimation window")
    parser.add_argument("--long-quantile", type=float, default=0.3, help="Long quantile")
    parser.add_argument("--short-quantile", type=float, default=0.3, help="Short quantile")
    parser.add_argument("--rebalance-freq", type=str, default="daily", help="Rebalance frequency")
    parser.add_argument("--transaction-costs", type=float, default=0.0, help="Transaction costs")
    parser.add_argument("--slippage", type=float, default=0.0, help="Slippage")
    parser.add_argument("--output", type=str, help="Output JSON file for results summary")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic data")

    args = parser.parse_args(argv)

    config = BABConfig(
        universe=args.universe,
        benchmark=args.benchmark,
        beta_window=args.beta_window,
        long_quantile=args.long_quantile,
        short_quantile=args.short_quantile,
        rebalance_freq=args.rebalance_freq,
        transaction_costs=args.transaction_costs,
        slippage=args.slippage,
    )

    strategy = BABStrategy(config)
    if args.synthetic or args.data is None:
        result = strategy.run()
    else:
        result = strategy.run(returns_df=args.data)

    cum = result.backtest["cumulative"].iloc[-1]
    print(f"Final cumulative return: {cum:.6f}")
    print(f"Periods: {len(result.backtest)}")

    if args.output:
        summary = {
            "final_cumulative": float(cum),
            "periods": int(len(result.backtest)),
            "benchmark": config.benchmark,
            "universe": config.universe,
        }
        Path(args.output).write_text(json.dumps(summary, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
