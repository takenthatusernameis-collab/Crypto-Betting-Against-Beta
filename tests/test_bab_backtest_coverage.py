"""Coverage-focused tests for backtest.py edge and error paths."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.backtest import run_backtest
from strategies.betting_against_beta.costs import TransactionCostModel


def _make_inputs(periods=40):
    idx = pd.date_range("2023-01-01", periods=periods, freq="D")
    rng = np.random.default_rng(7)
    returns = pd.DataFrame({
        "A": rng.normal(0.0005, 0.01, periods),
        "B": rng.normal(0.0008, 0.015, periods),
    }, index=idx)
    weights = pd.DataFrame({
        "A": [0.5] * periods,
        "B": [-0.5] * periods,
    }, index=idx)
    return returns, weights


def test_none_inputs_return_empty_frame():
    res = run_backtest(None, None)
    assert list(res.columns) == ["returns", "cumulative"]
    assert len(res) == 0


def test_non_dataframe_returns_that_convert_fail_return_empty():
    res = run_backtest(lambda x: x, pd.DataFrame({"A": [0.1, 0.2]}))
    assert list(res.columns) == ["returns", "cumulative"]
    res = run_backtest(pd.DataFrame({"A": [0.1, 0.2]}), lambda x: x)
    assert list(res.columns) == ["returns", "cumulative"]


def test_align_by_position_when_columns_disjoint():
    idx = pd.date_range("2023-01-01", periods=10, freq="D")
    returns = pd.DataFrame({"A": [0.001] * 10, "B": [0.002] * 10}, index=idx)
    weights = pd.DataFrame({"X": [0.5] * 10, "Y": [-0.5] * 10}, index=idx)
    res = run_backtest(returns, weights)
    assert list(res.columns) == ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]
    assert np.isfinite(res["cumulative"].values).all()


def test_transaction_costs_and_slippage():
    returns, weights = _make_inputs()
    res = run_backtest(returns, weights, transaction_costs=0.001, slippage=0.0005)
    assert np.isfinite(res["cumulative"].values).all()
    assert (res["cost_drag"] >= 0).all()
    assert (res["slippage_drag"] >= 0).all()


def test_cost_model_must_be_transaction_cost_model():
    returns, weights = _make_inputs()
    with pytest.raises(TypeError):
        run_backtest(returns, weights, cost_model="not-a-model")


def test_realistic_run_matches_lagged_weights():
    returns, weights = _make_inputs()
    res = run_backtest(returns, weights)
    expected = (weights.shift(1).fillna(0.0) * returns).sum(axis=1)
    assert np.allclose(res["gross_return"].values, expected.values, atol=1e-12)
