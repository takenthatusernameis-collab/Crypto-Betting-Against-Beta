#!/usr/bin/env python3
"""End-to-end BAB backtest report."""

from __future__ import annotations

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta import metrics


def main():
    strategy = BABStrategy()
    result = strategy.run()

    returns = result.backtest['returns']
    weights = result.weights
    benchmark_returns = result.returns[strategy.config.benchmark]

    summary = metrics.summary(returns, weights_df=weights, benchmark_returns=benchmark_returns)

    print("=" * 60)
    print("BAB STRATEGY BACKTEST REPORT (Synthetic Data)")
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
    print("=" * 60)


if __name__ == '__main__':
    main()
