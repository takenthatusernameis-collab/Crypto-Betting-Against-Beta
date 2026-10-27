"""Unit tests for BAB strategy metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import metrics


class TestSharpeRatio:
    def test_sharpe_of_positive_excess(self):
        rng = np.random.default_rng(123)
        returns = pd.Series(rng.normal(0.001, 0.01, 252))
        sr = metrics.sharpe_ratio(returns)
        assert isinstance(sr, float)
        assert not np.isnan(sr)

    def test_sharpe_zero_vol(self):
        returns = pd.Series([0.001] * 100)
        sr = metrics.sharpe_ratio(returns)
        assert sr == np.inf or np.isnan(sr)

    def test_empty_returns_nan(self):
        assert np.isnan(metrics.sharpe_ratio(pd.Series([])))


class TestMaxDrawdown:
    def test_drawdown_known_path(self):
        # Cumulative path: 1.0, 1.1, 0.99 (10% dd from peak)
        cum = pd.Series([1.0, 1.1, 0.99])
        mdd = metrics.max_drawdown(cum)
        assert abs(mdd - (-0.1)) < 1e-6

    def test_no_drawdown_zero(self):
        cum = pd.Series([1.0, 1.01, 1.02])
        mdd = metrics.max_drawdown(cum)
        assert mdd <= 0
        assert abs(mdd) < 1e-6 or mdd == 0


class TestTurnover:
    def test_constant_weights_zero_turnover(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        weights = pd.DataFrame({"A": [0.5, 0.5, 0.5, 0.5, 0.5], "B": [-0.5, -0.5, -0.5, -0.5, -0.5]}, index=idx)
        t = metrics.turnover(weights)
        assert abs(t) < 1e-9


class TestStrategyBeta:
    def test_strategy_beta_one(self):
        rng = np.random.default_rng(42)
        bench = pd.Series(rng.normal(0, 0.01, 100))
        strat = bench.copy()
        b = metrics.strategy_beta(strat, bench)
        assert abs(b - 1.0) < 1e-6


class TestSummary:
    def test_summary_has_keys(self):
        rng = np.random.default_rng(7)
        returns = pd.Series(rng.normal(0.0005, 0.01, 200))
        bench = pd.Series(rng.normal(0.0003, 0.01, 200))
        idx = returns.index
        weights = pd.DataFrame({"A": [0.3]*200, "B": [-0.3]*200}, index=idx)
        s = metrics.summary(returns, weights_df=weights, benchmark_returns=bench)
        for k in ['sharpe_ratio', 'annualized_volatility', 'max_drawdown', 'turnover', 'strategy_beta']:
            assert k in s
