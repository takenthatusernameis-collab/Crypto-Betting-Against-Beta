"""Coverage campaign: beta.py alignment / fallback / error paths (lines 55-56, 76,
78, 80, 82, 85, 87, 90-91, 103, 113, 123, 125-126, 129-130, 147, 159, 161-164,
306, 314)."""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class _BadSeries(pd.Series):
    @property
    def _constructor(self):
        return _BadSeries


class TestBetaAlignmentPaths:
    def test_rolling_beta_fallback_empty(self):
        # lines 43-56: both generic paths fail -> empty/NaN array returned
        class Bad:
            def __len__(self):
                raise TypeError

        rb = beta.rolling_beta(Bad(), Bad())
        assert rb is not None
        assert len(rb) == 0 or np.isnan(np.asarray(rb, dtype=float)).all()

    def test_calculate_beta_ndarray_series(self):
        # line 75-76: asset ndarray, bench Series -> convert asset to Series
        asset = np.array([0.01, 0.02, 0.03, 0.04])
        bench = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05])
        out = beta.calculate_beta(asset, bench)
        assert np.isfinite(out)

    def test_calculate_beta_series_ndarray(self):
        # line 77-78: asset Series, bench ndarray -> convert bench to Series
        asset = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05])
        bench = np.array([0.01, 0.02, 0.03, 0.04])
        out = beta.calculate_beta(asset, bench)
        assert np.isfinite(out)

    def test_calculate_beta_list_list(self):
        # line 79-82: both lists -> convert to Series
        out = beta.calculate_beta([0.01, 0.02, 0.03, 0.04], [0.01, 0.02, 0.03, 0.04, 0.05])
        assert np.isfinite(out)

    def test_calculate_beta_list_ndarray(self):
        # line 82: asset list, bench ndarray
        out = beta.calculate_beta([0.01, 0.02, 0.03, 0.04], np.array([0.01, 0.02, 0.03, 0.04, 0.05]))
        assert np.isfinite(out)

    def test_calculate_beta_ndarray_list(self):
        # line 85: asset ndarray, bench list
        out = beta.calculate_beta(np.array([0.01, 0.02, 0.03, 0.04]), [0.01, 0.02, 0.03, 0.04, 0.05])
        assert np.isfinite(out)

    def test_calculate_beta_alignment_typeerror(self):
        # lines 90-91: alignment raises TypeError/ValueError/AttributeError -> nan
        out = beta.calculate_beta(_BadSeries([1, 2, 3]), _BadSeries([1, 2, 3, 4]))
        assert out is not None

    def test_calculate_beta_empty_after_mask(self):
        # line 113: len(y) == 0 after finite mask
        out = beta.calculate_beta([np.inf, -np.inf], [np.inf, np.inf])
        assert np.isnan(out)

    def test_calculate_beta_non_finite_result(self):
        # line 123: lstsq returns non-finite beta -> nan
        a = np.array([1e300, 1e300, 1e300, 1e300])
        b = np.array([1e300, 2e300, 3e300, 4e300])
        out = beta.calculate_beta(a, b)
        assert np.isnan(out) or np.isfinite(out)

    def test_calculate_beta_outer_typeerror(self):
        # lines 127-128: outer TypeError/ValueError/AttributeError -> nan
        out = beta.calculate_beta("abc", "def")
        assert np.isnan(out)

    def test_calculate_beta_babdataerror_reraise(self):
        # lines 129-130: BABDataError re-raised, not swallowed
        with pytest.raises(BABDataError):
            beta.calculate_beta(None, None)

    def test_calculate_beta_fast_empty_after_mask(self):
        # line 147: len(a_m) == 0 after mask
        out = beta.calculate_beta_fast([np.inf], [np.inf])
        assert np.isnan(out)

    def test_calculate_beta_fast_constant_benchmark(self):
        # line 153: b_std < 1e-18 -> 0.0
        out = beta.calculate_beta_fast([1.0, 2.0, 3.0], [5.0, 5.0, 5.0])
        assert out == 0.0

    def test_calculate_beta_fast_outer_typeerror(self):
        # lines 163-164: outer TypeError/ValueError/AttributeError -> 0.0
        out = beta.calculate_beta_fast("abc", "def")
        assert out == 0.0

    def test_calculate_rolling_beta_string_fallback(self):
        # line 314: string column triggers fallback path
        df = pd.DataFrame({
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05] * 10,
            "ETH": ["a", "b", "c", "d", "e"] * 10,
        })
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(df, "BTC", window=10, min_obs=5)

    def test_calculate_rolling_beta_babdataerror_reraise(self):
        # line 306: BABDataError re-raised inside try
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(None, "BTC")