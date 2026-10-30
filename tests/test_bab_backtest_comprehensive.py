import numpy as np
import pandas as pd

from strategies.betting_against_beta import backtest
from strategies.betting_against_beta.data import generate_synthetic_returns


class TestRunBacktest:
    def test_basic_backtest(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=42)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[-1, 0] = 1.0  # BTC long
        res = backtest.run_backtest(df, weights)
        assert "returns" in res.columns
        assert "cumulative" in res.columns
        assert len(res) == len(df)

    def test_backtest_with_costs(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=42)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[10, 1] = 0.5
        weights.iloc[50, 1] = 0.0
        weights.iloc[50, 2] = -0.5
        res = backtest.run_backtest(df, weights, transaction_costs=0.001)
        assert "returns" in res.columns

    def test_backtest_with_slippage(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=42)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[10, 1] = 0.3
        weights.iloc[20, 1] = -0.3
        res = backtest.run_backtest(df, weights, slippage=0.0005)
        assert isinstance(res, pd.DataFrame)

    def test_one_day_lag(self):
        df = generate_synthetic_returns(n_days=50, n_assets=3, seed=10)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        # Set weight at t=0 - should apply to return at t+1
        weights.iloc[0, 0] = 1.0
        res = backtest.run_backtest(df, weights)
        assert np.isclose(res["returns"].iloc[0], 0.0)  # lagged
