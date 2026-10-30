"""Offline tests for BAB backtest alignment and fallback paths."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.backtest import run_backtest


class NoNumpyFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return NoNumpyFrame

    def to_numpy(self, *args, **kwargs):
        raise TypeError("forced pandas fallback")


class NoReplaceFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return NoReplaceFrame

    def replace(self, *args, **kwargs):
        raise TypeError("forced replace fallback")


def test_no_common_columns_uses_positional_alignment_when_shapes_match():
    index = pd.date_range("2026-01-01", periods=3, freq="D")
    returns = pd.DataFrame({"ASSET": [0.01, 0.02, 0.03]}, index=index)
    weights = pd.DataFrame({"LONG": [1.0, 0.0, 0.0]}, index=index)

    result = run_backtest(returns, weights)

    assert result.loc[index[0], "returns"] == 0.0
    assert result.loc[index[1], "returns"] == 0.02


def test_no_common_columns_with_different_shapes_returns_empty_result():
    index = pd.date_range("2026-01-01", periods=3, freq="D")
    returns = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03], "ETH": [0.02, 0.03, 0.04]},
        index=index,
    )
    weights = pd.DataFrame({"X": [1.0, 1.0, 1.0]}, index=index)

    result = run_backtest(returns, weights)

    assert result.empty


def test_dataframe_numpy_conversion_fallback_preserves_results():
    index = pd.date_range("2026-01-01", periods=3, freq="D")
    returns = NoNumpyFrame({"BTC": [0.01, 0.02, 0.03]}, index=index)
    weights = NoNumpyFrame({"BTC": [1.0, 0.0, 1.0]}, index=index)

    result = run_backtest(returns, weights)

    assert result.loc[index[1], "gross_return"] == 0.02
    assert result.loc[index[2], "gross_return"] == 0.0
    assert result["cumulative"].notna().all()


def test_weight_replace_fallback_still_runs_on_finite_weights():
    index = pd.date_range("2026-01-01", periods=3, freq="D")
    returns = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=index)
    weights = NoReplaceFrame({"BTC": [1.0, 0.0, 1.0]}, index=index)

    result = run_backtest(returns, weights)

    assert result.loc[index[1], "returns"] == 0.02
    assert result["cumulative"].notna().all()


def test_none_inputs_return_empty_results():
    assert run_backtest(None, pd.DataFrame()).empty
    assert run_backtest(pd.DataFrame(), None).empty
