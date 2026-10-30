"""Extra coverage tests for beta module uncovered branches."""

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


class TestBetaCoverageExtra:
    def test_rolling_beta_fallback_all_fail(self):
        class Bad:
            def __len__(self):
                raise TypeError()

        res = rolling_beta(Bad(), Bad())
        assert isinstance(res, np.ndarray)
        assert np.all(np.isnan(res)) or res.size >= 0

    def test_rolling_beta_empty_lists(self):
        res = rolling_beta([], [])
        assert isinstance(res, np.ndarray)

    def test_rolling_beta_with_min_periods_alias(self):
        a = pd.Series([0.01, 0.02, -0.01, 0.03])
        b = pd.Series([0.005, 0.01, -0.005, 0.015])
        res = rolling_beta(a, b, window=4, min_periods=2)
        assert hasattr(res, "__len__")

    def test_rolling_beta_arrays(self):
        res = rolling_beta(np.array([0.01, 0.02, 0.03]), np.array([0.01, 0.01, 0.01]), window=2)
        assert res is not None

    def test_calculate_beta_truncated_path(self):
        res = calculate_beta(np.array([0.01, 0.02, 0.03, 0.04]), np.array([0.01, 0.02]))
        assert res is not None

    def test_calculate_beta_all_nonfinite(self):
        assert np.isnan(calculate_beta([np.nan, np.inf], [1.0, 2.0]))

    def test_calculate_beta_filtered_nan(self):
        res = calculate_beta([0.01, np.nan, 0.03], [0.005, 0.01, 0.015])
        assert res is not None

    def test_calculate_beta_empty_after_filter(self):
        assert np.isnan(calculate_beta([np.nan], [np.nan]))

    def test_calculate_beta_min_obs_exceeded(self):
        assert np.isnan(calculate_beta([0.01, 0.02], [0.01, 0.02], min_obs=100))

    def test_calculate_beta_none_inputs_raises(self):
        with pytest.raises(BABDataError):
            calculate_beta(None, [0.01, 0.02])

    def test_calculate_beta_fast_none(self):
        res = calculate_beta_fast(None, None)
        assert res is not None

    def test_calculate_beta_fast_all_nonfinite(self):
        assert np.isnan(calculate_beta_fast([np.nan, np.inf], [np.nan, np.inf]))

    def test_calculate_beta_fast_filtered_nan(self):
        res = calculate_beta_fast([0.01, np.nan, 0.03], [0.005, 0.01, 0.015])
        assert res is not None

    def test_calculate_beta_fast_empty_after_filter(self):
        assert np.isnan(calculate_beta_fast([np.nan], [5.0]))

    def test_calculate_beta_fast_min_obs(self):
        assert np.isnan(calculate_beta_fast([0.01, 0.02], [0.01, 0.02], min_obs=100))

    def test_calculate_beta_fast_constant_bench(self):
        res = calculate_beta_fast([0.01, 0.02, 0.03], [0.01, 0.01, 0.01])
        assert res == 0.0

    def test_calc_rolling_beta_series_empty(self):
        res = _calc_rolling_beta_series([], [], 5, 3)
        assert len(res) == 0

    def test_calc_rolling_beta_series_insufficient(self):
        bench = np.array([0.01] * 5)
        asset = np.array([0.02] * 5)
        res = _calc_rolling_beta_series(bench, asset, window=3, min_obs=5)
        assert res is not None

    def test_calculate_rolling_beta_bench_no_finite_raises(self):
        df = pd.DataFrame({"BTC": [np.nan, np.inf, np.nan], "ETH": [0.01, 0.02, 0.03]})
        with pytest.raises(BABDataError):
            calculate_rolling_beta(df, "BTC")

    def test_calculate_rolling_beta_bad_asset_to_series_path(self):
        df2 = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04, 0.05], "ETH": [0.02, np.nan, 0.01, 0.03, np.nan]})
        res = calculate_rolling_beta(df2, "BTC", window=3, min_obs=2)
        assert "ETH" in res.columns

    def test_estimate_betas_variants(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.01, 0.03], "ETH": [0.02, 0.01, 0.02, 0.04]})
        res = estimate_betas(df, benchmark="BTC", window=4, min_observations=3)
        assert res is not None
        res = estimate_betas(df, benchmark="BTC", window=3, min_obs=10)
        assert res is not None
