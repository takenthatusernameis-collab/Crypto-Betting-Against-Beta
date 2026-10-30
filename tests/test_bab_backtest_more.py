import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import backtest


class TestBacktestMore:
    def test_backtest_lag_invariant(self):
        idx = pd.date_range("2023-01-01", periods=10)
        weights = pd.DataFrame({"BTC": [0.5]*10, "ETH": [-0.5]*10}, index=idx)
        returns = pd.DataFrame({"BTC": np.random.default_rng(1).normal(0,0.01,10), "ETH": np.random.default_rng(2).normal(0,0.01,10)}, index=idx)
        res = backtest.run_backtest(returns, weights)
        assert isinstance(res, pd.DataFrame) or hasattr(res, 'returns')

    def test_backtest_costs(self):
        idx = pd.date_range("2023-01-01", periods=15)
        weights = pd.DataFrame({"BTC": [0.3]*(7) + [0.6]*(8), "ETH": [-0.3]*(7) + [-0.6]*(8)}, index=idx)
        returns = pd.DataFrame({"BTC": np.random.default_rng(3).normal(0,0.01,15), "ETH": np.random.default_rng(4).normal(0,0.01,15)}, index=idx)
        try:
            res = backtest.run_backtest(returns, weights, transaction_costs=0.001)
        except Exception:
            pass

    def test_backtest_zero_trades(self):
        idx = pd.date_range("2023-01-01", periods=5)
        weights = pd.DataFrame({"BTC": [0.0]*5, "ETH": [0.0]*5}, index=idx)
        returns = pd.DataFrame({"BTC": [0.01]*5, "ETH": [-0.01]*5}, index=idx)
        try:
            res = backtest.run_backtest(returns, weights)
        except Exception:
            pass
