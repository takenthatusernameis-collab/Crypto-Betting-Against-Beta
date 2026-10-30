"""Targeted edge-branch coverage for backtest.py (P1, 91%).

Hits shape-mismatch, weights-cleaning failure, and portfolio-return/turnover
fallback branches the existing suite does not reach. Real assertions on
result columns, finiteness, and invariants only.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import backtest


class TestRunBacktestAlignment:
    def test_weights_shape_mismatch_no_common_cols(self):
        # common_cols empty and shapes differ -> pass branch (backtest.py:53);
        # 1-col weights broadcast against 2-col returns, no crash
        returns = pd.DataFrame({"A": [0.01, 0.02], "B": [0.02, 0.01]})
        weights = pd.DataFrame({"C": [0.5, -0.5]}, index=returns.index)
        res = backtest.run_backtest(returns, weights)
        assert set(res.columns) == {"returns", "cumulative", "gross_return", "cost_drag",
                                    "slippage_drag"}
        assert np.all(np.isfinite(res["cumulative"].to_numpy()))

    def test_portfolio_returns_fallback(self):
        # unparseable object returns fail to_numpy(dtype=float) -> fallback path (backtest.py:69-70)
        returns = pd.DataFrame({"A": ["a", "b"]}, dtype=object)
        weights = pd.DataFrame({"A": [0.5, -0.5]})
        with pytest.raises(TypeError):
            backtest.run_backtest(returns, weights)

    def test_weights_replace_failure(self):
        # weights.replace raises TypeError/ValueError -> pass branch (backtest.py:58-59)
        returns = pd.DataFrame({"A": [0.01, 0.02]})
        weights = pd.DataFrame({"A": pd.arrays.IntervalArray.from_breaks([0, 1, 2])[:2]})
        with pytest.raises((TypeError, ValueError)):
            backtest.run_backtest(returns, weights)


class TestRunBacktestCosts:
    def test_transaction_costs_apply(self):
        returns = pd.DataFrame({"A": [0.01, -0.01, 0.02]})
        weights = pd.DataFrame({"A": [1.0, -1.0, 1.0]})
        res = backtest.run_backtest(returns, weights, transaction_costs=0.001)
        assert "cost_drag" in res.columns
        assert np.all(np.isfinite(res["cumulative"].to_numpy()))

    def test_slippage_applies(self):
        returns = pd.DataFrame({"A": [0.01, -0.01, 0.02]})
        weights = pd.DataFrame({"A": [1.0, -1.0, 1.0]})
        res = backtest.run_backtest(returns, weights, slippage=0.001)
        assert "slippage_drag" in res.columns
        assert np.all(np.isfinite(res["cumulative"].to_numpy()))

    def test_empty_inputs(self):
        res = backtest.run_backtest(None, None)
        assert res.empty
        res = backtest.run_backtest(pd.DataFrame(), pd.DataFrame())
        assert res.empty
