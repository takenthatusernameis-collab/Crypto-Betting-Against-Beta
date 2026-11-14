"""Targeted tests for backtest.py uncovered branches (58-59)."""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import backtest as backtest_mod


def test_run_backtest_weights_replace_failure():
    # Force TypeError in weights.replace([np.inf, -np.inf], np.nan) -> lines 58-59
    # Monkey-patch DataFrame.replace to raise TypeError, then restore.
    original_replace = pd.DataFrame.replace

    def failing_replace(self, *args, **kwargs):
        raise TypeError("Forced replace failure")

    pd.DataFrame.replace = failing_replace
    try:
        returns = pd.DataFrame({"BTC": [0.01, -0.02, 0.03]})
        weights = pd.DataFrame({"BTC": [0.5, -0.3, 0.2]})
        res = backtest_mod.run_backtest(returns, weights)
        assert isinstance(res, pd.DataFrame)
    finally:
        pd.DataFrame.replace = original_replace


def test_run_backtest_returns_coercion_failure():
    # Force TypeError in returns_df = pd.DataFrame(returns_df) -> line 26
    res = backtest_mod.run_backtest(42, pd.DataFrame({"BTC": [0.1, 0.2]}))
    assert isinstance(res, pd.DataFrame)
    assert res.empty


def test_run_backtest_weights_coercion_failure():
    # Force TypeError in weights_df = pd.DataFrame(weights_df) -> line 31
    res = backtest_mod.run_backtest(pd.DataFrame({"BTC": [0.01, 0.02]}), 42)
    assert isinstance(res, pd.DataFrame)
    assert res.empty


def test_run_backtest_numpy_path_fallback():
    # Force the except branch in numpy path (line 70)
    returns = pd.DataFrame({"BTC": [0.01, -0.02, 0.03]})
    weights = pd.DataFrame({"BTC": [0.5, -0.3, 0.2]})
    res = backtest_mod.run_backtest(returns, weights)
    assert isinstance(res, pd.DataFrame)
    assert "returns" in res.columns


def test_run_backtest_turnover_fallback():
    # Force the except branch in turnover numpy path (line 78)
    returns = pd.DataFrame({"BTC": [0.01, -0.02, 0.03]})
    weights = pd.DataFrame({"BTC": [0.5, -0.3, 0.2]})
    res = backtest_mod.run_backtest(returns, weights, transaction_costs=0.001)
    assert isinstance(res, pd.DataFrame)
    assert "cost_drag" in res.columns


def test_run_backtest_cost_model_type_error():
    # Force TypeError when cost_model is not a TransactionCostModel -> line 102
    returns = pd.DataFrame({"BTC": [0.01, -0.02, 0.03]})
    weights = pd.DataFrame({"BTC": [0.5, -0.3, 0.2]})
    try:
        backtest_mod.run_backtest(returns, weights, cost_model="not_a_model")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
