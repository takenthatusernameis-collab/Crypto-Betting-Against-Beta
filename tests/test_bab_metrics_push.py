"""Targeted coverage push for strategies/betting_against_beta/metrics.py.

Targets the currently-missing statements:
  - 25:  _to_series single-column DataFrame branch
  - 42:  sharpe_ratio ``abs(mean_excess) < EPS`` -> nan (std tiny, mean tiny)
  - 97:  turnover ``pd.isna(turnover_mean)`` -> 0.0
  - 114: strategy_beta ``pd.isna(beta)`` -> nan
  - 126: total_return ``pd.isna(val)`` -> nan
  - 138: final_cumulative ``pd.isna(val)`` -> nan
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import metrics


def test_to_series_single_column_dataframe():
    # metrics.py:25 single-column DataFrame collapses to its series.
    df = pd.DataFrame({"A": [1.0, 2.0, 3.0]})
    s = metrics._to_series(df)
    assert isinstance(s, pd.Series)
    assert list(s) == [1.0, 2.0, 3.0]


def test_sharpe_std_and_mean_both_tiny_returns_nan():
    # metrics.py:40-42: std_excess < EPS and abs(mean_excess) < EPS -> nan.
    res = metrics.sharpe_ratio(pd.Series([0.0, 0.0, 0.0]))
    assert np.isnan(res)


def test_turnover_single_row_mean_nan_returns_zero():
    # metrics.py:96-97: diff of a single row is all-NaN -> mean NaN -> 0.0.
    df = pd.DataFrame({"A": [0.5], "B": [0.3]})
    assert metrics.turnover(df) == 0.0


def test_strategy_beta_beta_nan_returns_nan():
    # metrics.py:112-114: beta NaN -> nan.
    # cov/var with a degenerate-but-not-guarded benchmark can yield NaN.
    strat = pd.Series([0.01, 0.02])
    bench = pd.Series([0.01, 0.01])
    res = metrics.strategy_beta(strat, bench)
    assert np.isnan(res)


def test_total_return_nan_value_returns_nan():
    # metrics.py:123-126: cumprod can yield NaN (0 * inf) -> val NaN -> nan.
    res = metrics.total_return(pd.Series([-1.0, np.inf]))
    assert np.isnan(res)


def test_final_cumulative_nan_value_returns_nan():
    # metrics.py:135-138: cumprod NaN -> val NaN -> nan.
    res = metrics.final_cumulative(pd.Series([-1.0, np.inf]))
    assert np.isnan(res)
