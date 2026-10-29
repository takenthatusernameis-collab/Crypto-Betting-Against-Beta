"""Coverage-focused tests for signals.py internals and quantile clamping."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.signals import (
    _finite_beta_series,
    _reference_generate_bab_signals,
    generate_bab_signals,
)


class TestFiniteBetaSeries:
    def test_none_returns_none(self):
        assert _finite_beta_series(None) is None

    def test_dataframe_not_single_row_returns_none(self):
        assert _finite_beta_series(pd.DataFrame({"a": [1.0, 2.0]})) is None

    def test_non_series_returns_none(self):
        assert _finite_beta_series([1.0, 2.0]) is None

    def test_string_entries_zeroed(self):
        s = pd.Series(["1.5", "garbage", 2.0], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert list(out.index) == [2]
        assert abs(out.iloc[0] - 2.0) < 1e-12

    def test_all_non_finite_returns_none(self):
        assert _finite_beta_series(pd.Series([np.inf, -np.inf, np.nan])) is None


class TestReferenceImplementation:
    def test_none_and_empty(self):
        assert _reference_generate_bab_signals(None).empty
        assert _reference_generate_bab_signals(pd.DataFrame()).empty

    def test_single_asset_row_stays_flat(self):
        df = pd.DataFrame({"BTC": [0.5, 0.6, 0.7]}, index=range(3))
        out = _reference_generate_bab_signals(df)
        assert (out.values == 0).all()

    def test_overlap_shrink(self):
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]}, index=range(2))
        out = _reference_generate_bab_signals(df, long_quantile=0.9, short_quantile=0.9)
        assert out.shape == df.shape
        assert np.isfinite(out.values).all()

    def test_matches_vectorized(self):
        rng = np.random.default_rng(5)
        df = pd.DataFrame(rng.normal(1.0, 0.5, size=(20, 6)))
        a = _reference_generate_bab_signals(df)
        b = generate_bab_signals(df)
        assert a.equals(b)


class TestQuantileClampCoverage:
    def _df(self):
        return pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4]}, index=range(2))

    def test_non_numeric_long_quantile_defaults(self):
        out = generate_bab_signals(self._df(), long_quantile="abc")
        assert out.shape == (2, 2)
        assert np.isfinite(out.values).all()

    def test_non_numeric_short_quantile_defaults(self):
        out = generate_bab_signals(self._df(), short_quantile=None)
        assert out.shape == (2, 2)
        assert np.isfinite(out.values).all()

    def test_non_finite_long_quantile_defaults(self):
        out = generate_bab_signals(self._df(), long_quantile=float("nan"))
        assert out.shape == (2, 2)
        assert np.isfinite(out.values).all()

    def test_non_finite_short_quantile_defaults(self):
        out = generate_bab_signals(self._df(), short_quantile=float("inf"))
        assert out.shape == (2, 2)
        assert np.isfinite(out.values).all()
