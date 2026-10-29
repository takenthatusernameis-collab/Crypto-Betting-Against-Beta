#!/usr/bin/env python3
"""Micro-benchmark for BAB strategy hot paths.

Measures wall time and allocation pressure for the pipeline stages so that
optimizations can be justified with numbers rather than intuition.
"""
from __future__ import annotations

import gc
import time

import numpy as np
import pandas as pd

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.signals import generate_bab_signals
from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.backtest import run_backtest


def _make_returns(n_days=720, n_assets=12, seed=7):
    rng = np.random.default_rng(seed)
    data = rng.normal(0.0005, 0.02, size=(n_days, n_assets))
    cols = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT",
            "DOGE", "LINK", "MATIC", "ARB"][:n_assets]
    idx = pd.bdate_range("2022-01-03", periods=n_days)
    return pd.DataFrame(data, index=idx, columns=cols)


def _time(fn, repeats=5):
    gc.collect()
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    times.sort()
    return times[len(times) // 2]


def main():
    returns = _make_returns()
    print(f"shape={returns.shape}")

    # Warm up once so lazy imports/compilation are excluded.
    calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)
    generate_bab_signals(calculate_rolling_beta(returns, "BTC", window=90, min_obs=60))
    construct_portfolio(generate_bab_signals(
        calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)))
    run_backtest(returns, construct_portfolio(generate_bab_signals(
        calculate_rolling_beta(returns, "BTC", window=90, min_obs=60))))

    def stage_beta():
        return calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)

    def stage_full():
        return BABStrategy().run(returns_df=returns)

    beta_t = _time(stage_beta)
    full_t = _time(stage_full)
    print(f"calculate_rolling_beta  median: {beta_t * 1000:8.2f} ms")
    print(f"full BABStrategy.run   median: {full_t * 1000:8.2f} ms")

    # Allocation proxy: count live Python objects before/after a run.
    import tracemalloc
    tracemalloc.start()
    stage_full()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"tracemalloc peak during one run: {peak / 1e6:8.2f} MB")


if __name__ == "__main__":
    main()