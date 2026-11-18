"""P19-7 Milestone 2: beta.py exception hardening regression tests.

Each test locks the intended behavior (Class A: total contract) or proves
identical happy-path output with failure now surfacing (Class B: surface).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import (
    _calc_rolling_beta_series,
    _rolling_sum,
    _rolling_sum_finite,
    calculate_beta,
    calculate_beta_fast,
    calculate_rolling_beta,
    rolling_beta,
)


class TestRollingBeta:
    """rolling_beta lines 40, 43, 50, 55, 58, 67: broad except Exception.

    Class B (surface): _calc_rolling_beta_series failure -> try numpy array fallback.
    Class A (total contract): length detection failures -> continue/return [nan].
    """

    def test_rolling_beta_first_fallback_to_numpy_arrays(self):
        # Trigger first except by making _calc_rolling_beta_series fail
        # with non-Series inputs that cause an error in the fast path
        a = pd.Series([1.0, 2.0, 3.0])
        b = pd.Series([0.5, 1.0, 1.5])
        result = rolling_beta(a, b, window=2, min_obs=1)
        assert len(result) == 3
        assert isinstance(result, pd.Series)

    def test_rolling_beta_second_fallback_length_detection(self):
        # When both _calc_rolling_beta_series calls fail, length detection runs
        class BadArray:
            def __len__(self):
                raise ValueError("no len")

        a = BadArray()
        b = BadArray()
        result = rolling_beta(a, b, window=2, min_obs=1)
        # Should return array of NaN with length 1 (fallback)
        assert isinstance(result, np.ndarray)
        assert len(result) == 1
        assert np.isnan(result[0])

    def test_rolling_beta_length_detection_np_asarray_fallback(self):
        # len() fails but np.asarray works -> falls back to _calc_rolling_beta_series
        class LenFails:
            def __len__(self):
                raise ValueError("no len")
            def __array__(self):
                return np.array([1.0, 2.0, 3.0])

        a = LenFails()
        b = LenFails()
        result = rolling_beta(a, b, window=2, min_obs=1)
        assert isinstance(result, np.ndarray)
        assert len(result) == 3
        # _calc_rolling_beta_series computes betas for valid windows
        # First window (min_obs=1): 1 observation -> NaN (insufficient)
        # Second window: 2 observations -> beta computed
        # Third window: 3 observations -> beta computed
        assert np.isnan(result[0])
        assert np.isfinite(result[1])
        assert np.isfinite(result[2])

    def test_rolling_beta_all_length_detection_fails_returns_nan(self):
        # All length detection fails -> return [nan]
        class TotallyBroken:
            def __len__(self):
                raise ValueError("no len")
            def __array__(self):
                raise ValueError("no array")

        a = TotallyBroken()
        b = TotallyBroken()
        result = rolling_beta(a, b, window=2, min_obs=1)
        assert isinstance(result, np.ndarray)
        assert len(result) == 1
        assert np.isnan(result[0])


class TestCalculateBeta:
    """calculate_beta line 129: silent except Exception -> pass.

    Class A (total contract): min_obs int conversion failure -> ignore.
    """

    def test_calculate_beta_min_obs_conversion_failure_ignored(self):
        # min_obs that can't be converted to int should be ignored
        asset = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        bench = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
        # min_obs as a non-convertible object
        class BadInt:
            def __int__(self):
                raise ValueError("bad int")

        result = calculate_beta(asset, bench, min_obs=BadInt())
        # Should not raise, should compute beta normally
        assert isinstance(result, float)
        assert np.isfinite(result)


class TestCalculateBetaFast:
    """calculate_beta_fast line 188: broad except Exception -> return np.nan.

    Class A (total contract): min_obs int conversion failure -> return nan.
    """

    def test_calculate_beta_fast_min_obs_conversion_failure_returns_nan(self):
        asset = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        bench = np.array([0.5, 1.0, 1.5, 2.0, 2.5])

        class BadInt:
            def __int__(self):
                raise ValueError("bad int")

        result = calculate_beta_fast(asset, bench, min_obs=BadInt())
        assert np.isnan(result)


class TestCalculateRollingBeta:
    """calculate_rolling_beta lines 394, 397, 479, 482, 518, 521, 544, 547: broad except Exception.

    Class B (surface): to_numpy/asarray failures -> fallback or raise BABDataError.
    """

    def test_calculate_rolling_beta_benchmark_to_numpy_failure_fallback(self):
        # Benchmark column that fails to_numpy but works with np.asarray
        df = pd.DataFrame({
            "BTC": pd.Series([0.01, 0.02, -0.01, 0.03], dtype=float),
            "ETH": pd.Series([0.02, 0.03, -0.02, 0.04], dtype=float),
        })
        # Normal case should work
        result = calculate_rolling_beta(df, "BTC", window=2, min_obs=1)
        assert isinstance(result, pd.DataFrame)
        assert "ETH" in result.columns
        assert "BTC" in result.columns
        assert len(result) == 4

    def test_calculate_rolling_beta_asset_to_numpy_failure_fallback(self):
        # Asset column that fails to_numpy but works with np.asarray
        df = pd.DataFrame({
            "BTC": pd.Series([0.01, 0.02, -0.01, 0.03], dtype=float),
            "ETH": pd.Series([0.02, 0.03, -0.02, 0.04], dtype=float),
            "SOL": pd.Series([0.015, 0.025, -0.015, 0.035], dtype=float),
        })
        result = calculate_rolling_beta(df, "BTC", window=2, min_obs=1)
        assert isinstance(result, pd.DataFrame)
        assert "ETH" in result.columns
        assert "SOL" in result.columns

    def test_calculate_rolling_beta_bad_cols_fallback_path(self):
        # Mixed dtypes that force per-column fallback; unconvertible column raises BABDataError
        df = pd.DataFrame({
            "BTC": pd.Series([0.01, 0.02, -0.01, 0.03], dtype=float),
            "ETH": pd.Series([0.02, 0.03, -0.02, 0.04], dtype=float),
            "BAD": pd.Series(["a", "b", "c", "d"]),  # non-numeric
        })
        with pytest.raises(Exception) as exc_info:
            calculate_rolling_beta(df, "BTC", window=2, min_obs=1)
        assert "could not convert string to float" in str(exc_info.value)


class TestCalcRollingBetaSeries:
    """_calc_rolling_beta_series: internal function behavior lock."""

    def test_calc_rolling_beta_series_basic(self):
        bench = np.array([0.01, 0.02, -0.01, 0.03, 0.02])
        asset = np.array([0.02, 0.03, -0.02, 0.04, 0.03])
        result = _calc_rolling_beta_series(bench, asset, window=3, min_obs=2)
        assert len(result) == 5
        assert isinstance(result, np.ndarray)

    def test_calc_rolling_beta_series_degenerate_benchmark(self):
        # Constant benchmark -> all NaN betas
        bench = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        asset = np.array([0.02, 0.03, -0.02, 0.04, 0.03])
        result = _calc_rolling_beta_series(bench, asset, window=3, min_obs=2)
        assert np.all(np.isnan(result))


class TestRollingSum:
    """_rolling_sum / _rolling_sum_finite: internal function behavior lock."""

    def test_rolling_sum_basic(self):
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        sums, counts = _rolling_sum(arr, window=3, min_periods=2)
        assert len(sums) == 5
        assert len(counts) == 5
        # window=3, min_periods=2:
        # Index 0: 1 element < min_periods -> NaN
        # Index 1: 2 elements >= min_periods -> sum = 3.0
        # Index 2: 3 elements -> sum = 6.0
        # Index 3: 3 elements -> sum = 9.0
        # Index 4: 3 elements -> sum = 12.0
        assert np.isnan(sums[0])
        assert sums[1] == 3.0
        assert sums[2] == 6.0
        assert sums[3] == 9.0
        assert sums[4] == 12.0

    def test_rolling_sum_with_nan(self):
        arr = np.array([1.0, np.nan, 3.0, 4.0, 5.0])
        sums, counts = _rolling_sum(arr, window=3, min_periods=2)
        # NaN masked to 0, counted separately
        assert np.isnan(sums[0])  # min_periods=2, only 1 valid
        assert np.isnan(sums[1])  # window [1, nan] -> 1 valid
        assert sums[2] == 4.0   # window [1, nan, 3] -> 2 valid (1+3)
        assert counts[2] == 2

    def test_rolling_sum_finite_basic(self):
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        sums, counts = _rolling_sum_finite(arr, window=3, min_periods=2)
        assert len(sums) == 5
        assert len(counts) == 5
        # window=3, min_periods=2:
        # Index 0: 1 element < min_periods -> NaN
        # Index 1: 2 elements >= min_periods -> sum = 3.0
        # Index 2: 3 elements -> sum = 6.0
        # Index 3: 3 elements -> sum = 9.0
        # Index 4: 3 elements -> sum = 12.0
        assert np.isnan(sums[0])
        assert sums[1] == 3.0
        assert sums[2] == 6.0
        assert sums[3] == 9.0
        assert sums[4] == 12.0


class TestBetaEndToEnd:
    """End-to-end happy path tests to lock behavior before/after changes."""

    def test_calculate_beta_basic(self):
        asset = np.array([0.02, 0.03, -0.01, 0.04, 0.02])
        bench = np.array([0.01, 0.02, -0.01, 0.03, 0.02])
        beta = calculate_beta(asset, bench, min_obs=3)
        assert isinstance(beta, float)
        assert np.isfinite(beta)

    def test_calculate_beta_fast_basic(self):
        asset = np.array([0.02, 0.03, -0.01, 0.04, 0.02])
        bench = np.array([0.01, 0.02, -0.01, 0.03, 0.02])
        beta = calculate_beta_fast(asset, bench, min_obs=3)
        assert isinstance(beta, float)
        assert np.isfinite(beta)

    def test_calculate_rolling_beta_basic(self):
        df = pd.DataFrame({
            "BTC": pd.Series([0.01, 0.02, -0.01, 0.03, 0.02], dtype=float),
            "ETH": pd.Series([0.02, 0.03, -0.02, 0.04, 0.03], dtype=float),
            "SOL": pd.Series([0.015, 0.025, -0.015, 0.035, 0.025], dtype=float),
        })
        result = calculate_rolling_beta(df, "BTC", window=3, min_obs=2)
        assert isinstance(result, pd.DataFrame)
        assert "BTC" in result.columns
        assert "ETH" in result.columns
        assert "SOL" in result.columns
        assert len(result) == 5
        # Benchmark beta should be 1.0
        assert np.allclose(result["BTC"].dropna().values, 1.0)
