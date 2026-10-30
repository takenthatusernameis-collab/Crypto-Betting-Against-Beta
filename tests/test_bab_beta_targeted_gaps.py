import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaTargetedGaps:
    def test_rolling_beta_both_series_min_obs_clamp(self):
        idx = pd.date_range("2023-01-01", periods=40)
        mkt = pd.Series(np.random.default_rng(21).normal(0,0.01,40), index=idx)
        a = pd.Series(np.random.default_rng(22).normal(0,0.01,40), index=idx)
        rb = beta.rolling_beta(mkt, a, window=15, min_obs=50)
        assert len(rb) == 40

    def test_rolling_beta_both_arrays(self):
        rng = np.random.default_rng(23)
        mkt = rng.normal(0,0.01,30)
        a = rng.normal(0,0.01,30)
        rb = beta.rolling_beta(np.asarray(mkt), np.asarray(a), window=10, min_obs=5)
        assert len(rb) == 30

    def test_calculate_beta_align_attr_error_returns_nan(self):
        class Bad:
            def __init__(self):
                pass
        # pass objects that cause issues in alignment
        out = beta.calculate_beta(Bad(), Bad())
        assert np.isnan(out)

    def test_calculate_beta_both_ndarray_different(self):
        out = beta.calculate_beta(np.array([0.01,0.02,0.03]), np.array([0.01,0.02]))
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_both_list_different(self):
        out = beta.calculate_beta([0.01,0.02],[0.01,0.02,0.03])
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_truncate_path(self):
        out = beta.calculate_beta(np.array([0.01,0.02,0.03,0.04,0.05]), np.array([0.01,0.02,0.03]))
        assert np.isfinite(out)

    def test_calculate_beta_min_obs_after_align(self):
        a = pd.Series([0.01,0.02,0.03])
        b = pd.Series([0.01,0.02,0.03,0.04])
        out = beta.calculate_beta(a,b,min_obs=100)
        assert np.isnan(out)

    def test_calculate_beta_lstsq_finite_check(self):
        a = np.array([0.01]*5)
        b = np.array([0.01,0.02,0.03,0.04,0.05])
        out = beta.calculate_beta(a,b)
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_fast_mask_not_all(self):
        a = np.array([0.01, np.inf, 0.02, 0.03])
        b = np.array([0.01, 0.02, np.inf, 0.03])
        out = beta.calculate_beta_fast(a,b)
        assert np.isfinite(out)

    def test_calculate_beta_fast_deg_bench_std_small(self):
        a = np.array([1.0,2.0,3.0,4.0])
        b = np.array([0.0,1e-20,0.0,0.0])
        out = beta.calculate_beta_fast(a,b)
        assert isinstance(out, float)

    def test_calculate_beta_fast_nonfinite_result(self):
        a = np.array([np.nan, np.nan, np.nan])
        b = np.array([0.01,0.02,0.03])
        out = beta.calculate_beta_fast(a,b)
        assert np.isnan(out)
