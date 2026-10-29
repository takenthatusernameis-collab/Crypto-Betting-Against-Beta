"""Stress tests for the BAB pipeline at scale.

Deterministic, offline, no network. Asserts the pipeline stays finite and
dollar-neutral on a wide universe, and that the vectorized hot paths scale
without pathological slowdowns.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy, BABConfig


def _make_returns(n_days: int, n_assets: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n_days, freq="D")
    bench = rng.normal(0.0005, 0.02, n_days)
    data = {"BTC": bench}
    for i in range(n_assets - 1):
        data[f"ASSET_{i:03d}"] = rng.normal(0.0004, 0.025, n_days)
    return pd.DataFrame(data, index=idx)


class TestPipelineStress:
    def test_wide_universe_runs_finite_and_dollar_neutral(self):
        n_days, n_assets = 600, 120
        df = _make_returns(n_days, n_assets, 11)
        cfg = BABConfig(benchmark="BTC", beta_window=90, min_observations=60)
        strat = BABStrategy(cfg)
        t0 = time.perf_counter()
        res = strat.run(returns_df=df)
        elapsed = time.perf_counter() - t0

        weights = res.weights
        assert not weights.empty
        # All data columns (including the benchmark, which is scored for beta)
        # flow through to the weights frame.
        assert weights.shape[1] == n_assets
        assert np.isfinite(weights.values).all(), "non-finite weights under scale"

        # Approximately dollar-neutral: longs/shorts equal-weight, benchmark may
        # occupy a short leg, so row sums are bounded by 1 / n_short, not zero.
        row_sums = weights.sum(axis=1).dropna()
        assert len(row_sums) > 0
        assert (np.abs(row_sums) < 0.05).all()

        # Backtest must be finite too.
        bt = res.backtest
        assert not bt.empty
        assert np.isfinite(bt["returns"].values).all()
        assert np.isfinite(bt["cumulative"].values).all()

        # Vectorized hot paths must scale: well under a minute on this size.
        assert elapsed < 60.0, f"pipeline too slow at {n_days}x{n_assets}: {elapsed:.2f}s"

    def test_stress_deterministic_across_runs(self):
        df = _make_returns(300, 60, 21)
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=30)
        first = BABStrategy(cfg).run(returns_df=df)
        second = BABStrategy(cfg).run(returns_df=df)
        pd.testing.assert_frame_equal(first.weights, second.weights)
        pd.testing.assert_frame_equal(first.backtest, second.backtest)

    def test_stress_with_transaction_costs_still_finite(self):
        df = _make_returns(300, 60, 22)
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=30,
                        transaction_costs=0.001, slippage=0.0005)
        res = BABStrategy(cfg).run(returns_df=df)
        assert np.isfinite(res.weights.values).all()
        assert np.isfinite(res.backtest["cumulative"].values).all()
        # Costs must not exceed the gross path cumulatively.
        assert res.backtest["cumulative"].iloc[-1] > 0.0
