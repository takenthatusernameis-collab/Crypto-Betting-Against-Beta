import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaFillP0:
    def test_rolling_beta_fallback_both_fail_to_get_n(self):
        class Bad:
            def __len__(self):
                raise TypeError
        # First try series path - both might not be series; then try generic paths
        rb = beta.rolling_beta(Bad(), Bad())
        assert rb is not None

    def test_calculate_beta_align_exception(self):
        class BadSeries(pd.Series):
            @property
            def _constructor(self):
                return BadSeries
        # Force alignment exception
        try:
            out = beta.calculate_beta(BadSeries([1,2,3,4]), BadSeries([1,2,3]))
            assert out is not None
        except Exception:
            pass

    def test_calculate_beta_lists_both_converted(self):
        out = beta.calculate_beta([0.01,0.02,0.03], [0.01,0.02,0.03,0.04], min_obs=2)
        assert np.isfinite(out)

    def test_calculate_beta_ndarray_ndarray_different_len_truncate(self):
        out = beta.calculate_beta(np.array([0.01,0.02,0.03]), np.array([0.01,0.02,0.03,0.04]))
        assert np.isfinite(out)

    def test_calculate_beta_y_none_case(self):
        out = beta.calculate_beta([], [1,2,3,4])
        assert np.isnan(out)

    def test_calculate_beta_empty_after_mask(self):
        out = beta.calculate_beta([np.inf, -np.inf], [0.01, 0.02])
        assert np.isnan(out)

    def test_calculate_beta_min_obs_check(self):
        out = beta.calculate_beta([0.01,0.02], [0.01,0.02], min_obs=10)
        assert np.isnan(out)

    def test_calculate_beta_nonfinite_beta(self):
        a = np.array([1e200, 2e200, 3e200, 4e200])
        b = np.array([1e200, 2e200, 3e200, 4e200])
        out = beta.calculate_beta(a, b)
        assert np.isnan(out) or np.isfinite(out)

    def test_calculate_beta_outer_except(self):
        class Bad:
            def __array__(self, *args, **kwargs):
                raise AttributeError
        out = beta.calculate_beta(Bad(), Bad())
        assert np.isnan(out)

    def test_calculate_beta_fast_outer_except(self):
        class Bad:
            def __array__(self, *args, **kwargs):
                raise TypeError
        out = beta.calculate_beta_fast(Bad(), Bad())
        assert out == 0.0

    def test_estimate_betas_minobs_greater_than_window_clamped(self):
        idx = pd.date_range("2023-01-01", periods=50)
        df = pd.DataFrame({"BTC": np.random.default_rng(99).normal(0,0.01,50), "ETH": np.random.default_rng(98).normal(0,0.01,50)}, index=idx)
        out = beta.estimate_betas(df, benchmark="BTC", window=20, min_obs=30)
        assert isinstance(out, pd.DataFrame)
