#!/usr/bin/env python3
"""End-to-end BAB backtest report.

Runs the BAB strategy (synthetic data by default, or from a CSV/JSON file or
DataFrame passed via --data-source) and prints a human-readable performance
report. With --json, emits a machine-readable summary.

Examples:
    python3 scripts/bab_backtest_report.py
    python3 scripts/bab_backtest_report.py --data-source returns.csv --benchmark BTC
    python3 scripts/bab_backtest_report.py --data-source returns.csv --json
"""

from __future__ import annotations

import argparse
import json
import sys

from strategies.betting_against_beta import BABConfig, BABStrategy
from strategies.betting_against_beta import metrics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BAB backtest report")
    parser.add_argument(
        "--data-source",
        default=None,
        help="Path to a CSV/JSON returns file, or 'synthetic' (default).",
    )
    parser.add_argument(
        "--returns-csv",
        default=None,
        dest="returns_csv",
        help="Alias for --data-source pointing at a CSV returns file.",
    )
    parser.add_argument("--benchmark", default="BTC", help="Benchmark asset column name.")
    parser.add_argument("--beta-window", type=int, default=90)
    parser.add_argument("--min-observations", type=int, default=60)
    parser.add_argument("--long-quantile", type=float, default=0.3)
    parser.add_argument("--short-quantile", type=float, default=0.3)
    parser.add_argument("--transaction-costs", type=float, default=0.0)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # --returns-csv is an explicit alias for the CSV data path; it wins over
    # --data-source so callers can pass either flag interchangeably.
    data_source = args.returns_csv or args.data_source
    data_source = None if data_source in (None, "", "synthetic") else data_source
    cfg = BABConfig(
        benchmark=args.benchmark,
        beta_window=args.beta_window,
        min_observations=args.min_observations,
        long_quantile=args.long_quantile,
        short_quantile=args.short_quantile,
        transaction_costs=args.transaction_costs,
        data_source=data_source,
    )
    strategy = BABStrategy(cfg)
    result = strategy.run()

    returns = result.backtest["returns"]
    weights = result.weights
    benchmark_returns = result.returns[strategy.config.benchmark]

    summary = metrics.summary(
        returns,
        weights_df=weights,
        benchmark_returns=benchmark_returns,
    )

    if args.json:
        payload = {
            "config": {
                "universe": list(strategy.config.universe),
                "benchmark": strategy.config.benchmark,
                "beta_window": strategy.config.beta_window,
                "min_observations": strategy.config.min_observations,
                "long_quantile": strategy.config.long_quantile,
                "short_quantile": strategy.config.short_quantile,
                "transaction_costs": strategy.config.transaction_costs,
                "data_source": strategy.config.data_source,
            },
            "rebalances": int(len(weights.dropna(how="all"))),
            "metrics": summary,
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0

    print("=" * 60)
    source_desc = "synthetic data" if data_source is None else f"data source: {data_source}"
    print(f"BAB STRATEGY BACKTEST REPORT ({source_desc})")
    print("=" * 60)
    print(f"Universe: {', '.join(strategy.config.universe)}")
    print(f"Benchmark: {strategy.config.benchmark}")
    print(f"Beta window: {strategy.config.beta_window} days (min {strategy.config.min_observations} obs)")
    print(f"Long/Short quantiles: {strategy.config.long_quantile}/{strategy.config.short_quantile}")
    print(f"Rebalances: {len(weights.dropna(how='all'))}")
    print("-" * 60)
    print(f"Final Cumulative: {summary['final_cumulative']:.4f}x ({summary['total_return']:.2%})")
    print(f"Sharpe Ratio (ann.): {summary['sharpe_ratio']:.4f}")
    print(f"Annualized Volatility: {summary['annualized_volatility']:.2%}")
    print(f"Max Drawdown: {summary['max_drawdown']:.2%}")
    print(f"Turnover (avg): {summary['turnover']:.4f}")
    print(f"Strategy Beta vs {strategy.config.benchmark}: {summary['strategy_beta']:.4f}")
    print(f"Observations: {summary['n_observations']}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())