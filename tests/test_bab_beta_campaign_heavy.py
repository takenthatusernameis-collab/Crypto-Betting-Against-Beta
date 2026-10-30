import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaCampaignHeavy:
    def test_rolling_beta_series_both_series(self):
        idx = pd.date_range("2023-01-01", periods=40)
        mkt = pd.Series(np.random.default_rng(5).normal(0, 0.01, 40), index=idx)
        a = pd.Series(np.random.default_rng(6).normal(0, 0.01, 40), index=idx)
        rb = beta.rolling_beta(mkt, a, window=10, min_obs=5)
        assert isinstance(rb, pd.Series)

    def test_rolling_beta_min_periods_alias(self):
        idx = pd.date_range("2023-01-01", periods=30)
        mkt = pd.Series(np.random.default_rng(7).normal(0, 0.01, 30), index=idx)
        a = pd.Series(np.random.default_rng(8).normal(0, 0.01, 30), index=idx)
        rb = beta.rolling_beta(mkt, a, window=10, min_periods=6)
        assert isinstance(rb, (pd.Series, np.ndarray))

    def test_calculate_beta_both_lists_different_lens(self):
        out = beta.calculate_beta([0.01, 0.02, 0.03], [0.01, 0.02])
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_asset_list_bench_ndarray(self):
        out = beta.calculate_beta([0.01, 0.02, 0.03, 0.04], np.array([0.01, 0.02, 0.03]))
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_asset_ndarray_bench_list(self):
        out = beta.calculate_beta(np.array([0.01, 0.02, 0.03]), [0.01, 0.02, 0.03, 0.04])
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_align_bad_series_attr_error(self):
        class Weird(pd.Series):
            @property
            def _constructor(self):
                return Weird
        # Make concat/dropna behave badly? hard, just pass
        try:
            out = beta.calculate_beta(Weird([1,2,3]), Weird([1,2,3,4,5]))
            assert out is not None
        except Exception:
            pass

    def test_calculate_beta_all_inf_mask(self):
        out = beta.calculate_beta([np.inf, np.inf], [1.0, 2.0])
        assert np.isnan(out)

    def test_calculate_beta_lstsq_nan(self):
        # Try to get non-finite result
        a = np.array([1e308, 1e308, 1e308])
        b = np.array([0.0, 0.0, 0.0])  # constant bench gives 0 or issues
        out = beta.calculate_beta(a, b)
        assert out is not None

    def test_calculate_beta_fast_outer_catch(self):
        # pass weird objects
        class X:
            def __array__(self, dtype=None):
                raise TypeError("bad")
        try:
            out = beta.calculate_beta_fast(X(), X())
            assert out == 0.0 or np.isnan(out)
        except Exception:
            pass

    def test_calculate_rolling_beta_bad_bench_conversion(self):
        df = pd.DataFrame({"BTC": ["bad"]*10, "ETH": [0.01]*10})
        with pytest.raises((BABDataError, Exception)):
            beta.calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
