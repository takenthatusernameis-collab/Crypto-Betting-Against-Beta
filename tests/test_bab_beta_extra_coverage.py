"""Extra BAB coverage tests for beta module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.beta import (
    _calc_rolling_beta_series,
    calculate_beta,
    calculate_beta_fast,
    calculate_rolling_beta,
    estimate_betas,
    rolling_beta,
)
from strategies.betting_against_beta.data_loader import BABDataError


def test_rolling_beta_fallback_bad_objects():
    class Bad:
        def __len__(self):
            raise TypeError()

    res = rolling_beta(Bad(), Bad())
    assert isinstance(res, np.ndarray)
    res = rolling_beta([], [])
    assert isinstance(res, np.ndarray)
    res = rolling_beta(np.array([0.01, 0.02]), np.array([0.01, 0.01]), window=1)
    assert res is not None


def test_rolling_beta_min_periods_alias():
    a = pd.Series([0.01, 0.02, -0.01, 0.03])
    b = pd.Series([0.005, 0.01, -0.005, 0.015])
    res = rolling_beta(a, b, window=4, min_periods=2)
    assert len(res) == 4


def test_calculate_beta_truncated():
    res = calculate_beta(np.array([0.01, 0.02, 0.03, 0.04]), np.array([0.01, 0.02]))
    assert res is not None


def test_calculate_beta_all_nonfinite():
    assert np.isnan(calculate_beta([np.nan, np.inf], [1.0, 2.0]))


def test_calculate_beta_filtered():
    res = calculate_beta([0.01, np.nan, 0.03], [0.005, 0.01, 0.015])
    assert res is not None


def test_calculate_beta_empty_after():
    assert np.isnan(calculate_beta([np.nan], [np.nan]))


def test_calculate_beta_min_obs_big():
    assert np.isnan(calculate_beta([0.01, 0.02], [0.01, 0.02], min_obs=100))


def test_calculate_beta_none_raises():
    with pytest.raises(BABDataError):
        calculate_beta(None, [0.01])


def test_calculate_beta_fast_paths():
    assert calculate_beta_fast(None, None) is not None
    assert np.isnan(calculate_beta_fast([np.nan, np.inf], [np.nan, np.inf]))
    res = calculate_beta_fast([0.01, np.nan, 0.03], [0.005, 0.01, 0.015])
    assert res is not None
    assert np.isnan(calculate_beta_fast([np.nan], [5.0]))
    assert np.isnan(calculate_beta_fast([0.01, 0.02], [0.01, 0.02], min_obs=100))
    assert calculate_beta_fast([0.01, 0.02, 0.03], [0.01, 0.01, 0.01]) == 0.0


def test_calc_rolling_beta_series_paths():
    res = _calc_rolling_beta_series([], [], 5, 3)
    assert len(res) == 0
    bench = np.array([0.01] * 5)
    asset = np.array([0.02] * 5)
    res = _calc_rolling_beta_series(bench, asset, window=3, min_obs=5)
    assert res is not None


def test_calculate_rolling_beta_paths():
    df = pd.DataFrame({"BTC": [np.nan, np.inf, np.nan], "ETH": [0.01, 0.02, 0.03]})
    with pytest.raises(BABDataError):
        calculate_rolling_beta(df, "BTC")

    df2 = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04, 0.05], "ETH": [0.02, np.nan, 0.01, 0.03, np.nan]})
    res = calculate_rolling_beta(df2, "BTC", window=3, min_obs=2)
    assert "ETH" in res.columns


def test_estimate_betas_more():
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.01, 0.03], "ETH": [0.02, 0.01, 0.02, 0.04]})
    res = estimate_betas(df, benchmark="BTC", window=4, min_observations=3)
    assert res is not None
    res = estimate_betas(df, benchmark="BTC", window=3, min_obs=10)
    assert res is not None
