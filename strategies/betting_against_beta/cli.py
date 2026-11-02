"""Command-line interface for BAB strategy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import BABConfig
from .strategy import BABStrategy

__version__ = "0.1.0"


def _print_resolved_config(config: BABConfig) -> None:
    """Print the resolved CLI configuration in a stable, human-readable form."""
    print("Resolved BAB configuration:")
    print(f"  version:          {__version__}")
    print(f"  benchmark:        {config.benchmark}")
    print(f"  universe:         {list(config.universe) if config.universe else []}")
    print(f"  beta_window:      {config.beta_window}")
    print(f"  long_quantile:    {config.long_quantile}")
    print(f"  short_quantile:   {config.short_quantile}")
    print(f"  rebalance_freq:   {config.rebalance_freq}")
    print(f"  transaction_costs:{config.transaction_costs}")
    print(f"  slippage:         {config.slippage}")
    print(f"  min_rows:         {config.min_rows}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Betting Against Beta (BAB) crypto strategy")
    parser.add_argument("--version", action="version", version=f"bab {__version__}")
    parser.add_argument("--data", type=str, help="Path to returns data (CSV/JSON/Parquet/HDF5/Pickle). Use --from-prices to treat this as a price series instead.")
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
    parser.add_argument(
        "--from-prices",
        action="store_true",
        help="Treat --data as a price series and convert to returns via load_prices()",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print resolved config without running the backtest",
    )

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

    if args.dry_run:
        _print_resolved_config(config)
        if args.data is not None:
            from .data_loader import load_returns

            try:
                load_returns(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
                print(f"data:             {args.data} (valid, --from-prices={args.from_prices})")
            except Exception as exc:
                print(f"data:             {args.data} (INVALID: {exc})")
                return 1
        else:
            print("data:             synthetic (default)")
        return 0

    strategy = BABStrategy(config)
    if args.synthetic or args.data is None:
        result = strategy.run()
    else:
        from .data_loader import load_prices, load_returns

        try:
            if args.from_prices:
                returns_df = load_prices(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
            else:
                returns_df = load_returns(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
        except Exception as exc:
            print(f"Error loading data: {exc}")
            return 1
        result = strategy.run(returns_df=returns_df)

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
