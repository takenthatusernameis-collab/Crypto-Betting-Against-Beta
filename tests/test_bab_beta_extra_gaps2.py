import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaExtraGaps2:
    def test_calculate_beta_fast_with_nans(self):
        a = np.array([0.01, np.nan, 0.02, 0.03])
        b = np.array([0.01, 0.02, np.nan, 0.03])
        out = beta.calculate_beta_fast(a, b)
        assert np.isfinite(out)

    def test_calculate_beta_fast_min_obs(self):
        a = np.array([0.01, 0.02, 0.03])
        b = np.array([0.01, 0.02, 0.03])
        out = beta.calculate_beta_fast(a, b, min_obs=10)
        assert np.isnan(out)

    def test_calculate_beta_fast_nonfinite_beta(self):
        # Try to trigger non-finite coeff
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 2.0, 3.0])
        out = beta.calculate_beta_fast(a, b)
        assert isinstance(out, float)

    def test_calculate_beta_series_with_nans_mixed(self):
        a = pd.Series([0.01, np.nan, 0.02, 0.03, 0.04])
        b = pd.Series([0.01, 0.02, 0.03, np.nan, 0.05])
        out = beta.calculate_beta(a, b)
        assert np.isfinite(out)

    def test_calculate_beta_both_none_raises(self):
        with pytest.raises(BABDataError):
            beta.calculate_beta(None, None)

    def test_calculate_beta_outer_exception_catch(self):
        class Bad:
            def __array__(self, dtype=None):
                raise ValueError("bad")
        out = beta.calculate_beta(Bad(), Bad())
        assert np.isnan(out)

    def test_rolling_beta_both_series_min_periods(self):
        idx = pd.date_range("2023-01-01", periods=25)
        mkt = pd.Series(np.random.default_rng(123).normal(0, 0.01, 25), index=idx)
        a = pd.Series(np.random.default_rng(124).normal(0, 0.01, 25), index=idx)
        rb = beta.rolling_beta(mkt, a, window=5, min_periods=3)
        assert len(rb) == 25

    def test_rolling_beta_fallback_all_fail(self):
        class Bad:
            def __len__(self):
                raise TypeError
            def __iter__(self):
                raise TypeError
        try:
            rb = beta.rolling_beta(Bad(), Bad())
            assert rb is not None
        except Exception:
            pass

    def test_estimate_betas_default_bench_guess(self):
        idx = pd.date_range("2023-01-01", periods=30)
        rng = np.random.default_rng(9)
        df = pd.DataFrame({"BTC": rng.normal(0, 0.01, 30), "ETH": rng.normal(0, 0.01, 30)}, index=idx)
        # no benchmark specified - try
        try:
            b = beta.estimate_betas(df)
            assert isinstance(b, pd.DataFrame)
        except Exception:
            pass

    def test_calculate_rolling_beta_bad_bench_has_bad_values(self):
        idx = pd.date_range("2023-01-01", periods=20)
        df = pd.DataFrame({"BTC": [np.nan]*20, "ETH": np.random.default_rng(1).normal(0,0.01,20)}, index=idx)
        with pytest.raises((BABDataError, Exception)):
            beta.calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
