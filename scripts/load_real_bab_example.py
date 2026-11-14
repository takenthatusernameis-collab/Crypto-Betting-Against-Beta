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
import json
import sys
from pathlib import Path

__version__ = "0.1.0"

# Ensure the repository root is importable when this script is executed
# directly (``python scripts/load_real_bab_example.py``) rather than as a
# module. Without this, ``from strategies.betting_against_beta import ...``
# fails with ModuleNotFoundError because Python prepends the script's own
# directory (``scripts/``) to sys.path, not the repository root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import BABDataError, load_prices, load_returns


def main() -> int:
    parser = argparse.ArgumentParser(description="Load real returns/price data and run BAB")
    parser.add_argument("data_path", nargs="?", default=None, type=str, help="Path to data file (CSV/JSON/JSONL/Parquet/HDF5/Pickle). For prices use --from-prices")
    parser.add_argument("--benchmark", type=str, default="BTC", help="Benchmark symbol column name")
    parser.add_argument("--min-rows", type=int, default=30, help="Minimum rows/finite history")
    parser.add_argument("--lookback", type=int, default=252, help="Rolling beta lookback")
    parser.add_argument("--quantile", type=float, default=0.3, help="Quantile for long/short")
    parser.add_argument("--transaction-cost", type=float, default=0.001, help="Transaction cost per unit turnover")
    parser.add_argument("--from-prices", action="store_true", help="Treat input as prices and convert to returns via load_prices()")
    parser.add_argument("--universe", type=str, nargs="*", help="Optional universe override (must intersect data)")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--output", type=str, help="Output JSON file for results summary")
    args = parser.parse_args()

    if args.version:
        print(f"bab {__version__}")
        return 0

    if args.data_path is None:
        parser.error("the following arguments are required: data_path")

    data_path = Path(args.data_path)
    if not data_path.exists():
        raise SystemExit(f"File not found: {data_path}")
    if data_path.is_dir():
        raise SystemExit(f"Path is a directory, not a file: {data_path}")

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
    # Extract the final cumulative defensively: a degenerate backtest frame
    # (empty, or lacking a cumulative column) must surface as a clean
    # non-finite/zero value rather than crashing the console script.
    import math

    cum = None
    bt = getattr(result, "backtest", None)
    if bt is not None and hasattr(bt, "__len__") and len(bt) > 0:
        if "cumulative" in getattr(bt, "columns", []):
            try:
                cum = bt["cumulative"].iloc[-1]
            except Exception:
                cum = None
        else:
            for col in bt.columns:
                if "cum" in str(col).lower():
                    try:
                        cum = bt[col].iloc[-1]
                        break
                    except Exception:
                        continue
    if cum is None or not math.isfinite(float(cum)):
        cum = 0.0
    print(f"cumulative_return={float(cum):.6f}")
    print(f"periods={len(bt) if bt is not None and hasattr(bt, '__len__') else 0}")

    if args.output:
        out_path = Path(args.output)
        parent = out_path.parent
        if str(parent) and str(parent) != ".":
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                print(f"Error creating parent directory for --output {out_path}: {exc}", file=sys.stderr)
                return 1
        universe = args.universe if args.universe else []
        summary = {
            "final_cumulative": float(cum),
            "periods": len(bt) if bt is not None and hasattr(bt, "__len__") else 0,
            "benchmark": args.benchmark,
            "universe": [str(u) for u in universe],
        }
        try:
            out_path.write_text(json.dumps(summary, indent=2, allow_nan=False))
        except OSError as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
