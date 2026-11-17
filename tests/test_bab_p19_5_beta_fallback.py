"""Tests for beta.py fallback path (P19-5/P19-6 residue line coverage)."""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.data_loader import BABDataError


class _OuterFallbackDF(pd.DataFrame):
    @property
    def _constructor(self):
        return _OuterFallbackDF

    def __getitem__(self, key):
        if isinstance(key, list):
            class BadSlice:
                def to_numpy(self, dtype=float):
                    raise AttributeError("force outer fallback")

            return BadSlice()
        return super().__getitem__(key)


class _BadToNumpyGoodArray:
    def __init__(self, values):
        self.values = np.asarray(values, dtype=float)

    def to_numpy(self, dtype=float, copy=False):
        raise ValueError("to_numpy unavailable")

    def __array__(self, dtype=None):
        return np.asarray(self.values, dtype=dtype)

    def __len__(self):
        return len(self.values)


class _NoArrayNoToNumpy:
    def __init__(self, n):
        self.n = n

    def to_numpy(self, dtype=float, copy=False):
        raise ValueError("to_numpy unavailable")

    def __array__(self, dtype=None):
        raise TypeError("array unavailable")

    def __len__(self):
        return self.n


class _OuterFallbackAssetDF(_OuterFallbackDF):
    def __init__(self, *args, eth_obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._eth_obj = eth_obj

    @property
    def _constructor(self):
        return _OuterFallbackAssetDF

    def __getitem__(self, key):
        if key == "ETH" and self._eth_obj is not None:
            return self._eth_obj
        return super().__getitem__(key)


def test_beta_uncoercible_asset_column_raises_babdataerror():
    """calculate_rolling_beta raises BABDataError for uncoercible asset columns.

    Covers beta.py:544-548 where:
    1. returns_df[asset].to_numpy(dtype=float, copy=False) raises TypeError
    2. np.asarray(returns_df[asset], dtype=float) also raises TypeError
    3. BABDataError is raised with the error message
    """
    df = pd.DataFrame({
        "BTC": [0.01, 0.02, 0.01, -0.01, 0.02, 0.01, 0.03, -0.02, 0.01, 0.02],
        "ETH": [object(), object(), object(), object(), object(), object(),
                object(), object(), object(), object()],
        "SOL": [0.02, 0.01, 0.03, 0.01, 0.02, 0.03, 0.01, 0.02, 0.01, 0.03],
    })
    df.index = pd.date_range("2020-01-01", periods=10, freq="D")

    with pytest.raises(BABDataError,
                       match=r"float\(\) argument must be a string or a real number, not 'object'"):
        calculate_rolling_beta(df, "BTC", window=5, min_obs=3)


def test_beta_uncoercible_asset_column_with_valid_benchmark():
    """Benchmark works while an uncoercible asset column raises BABDataError."""
    df = pd.DataFrame({
        "BTC": [0.01, 0.02, 0.01, -0.01, 0.02, 0.01, 0.03, -0.02, 0.01, 0.02],
        "BAD_ASSET": ["not_a_number", "also_bad", "still_bad", "nope", "fail",
                      "bad", "worse", "terrible", "awful", "horrible"],
    })
    df.index = pd.date_range("2020-01-01", periods=10, freq="D")

    with pytest.raises(BABDataError, match=r"could not convert string to float"):
        calculate_rolling_beta(df, "BTC", window=5, min_obs=3)


def test_beta_benchmark_with_objects_raises():
    """An uncoercible benchmark column raises BABDataError."""
    df = pd.DataFrame({
        "BAD_BENCH": [object(), object(), object(), object(), object()],
        "ETH": [0.02, 0.01, 0.03, 0.01, 0.02],
        "SOL": [0.01, 0.03, 0.02, 0.01, 0.03],
    })
    df.index = pd.date_range("2020-01-01", periods=5, freq="D")

    with pytest.raises(BABDataError,
                       match=r"float\(\) argument must be a string or a real number, not 'object'"):
        calculate_rolling_beta(df, "BAD_BENCH", window=3, min_obs=2)


def test_beta_outer_fallback_asset_to_numpy_fails_but_asarray_succeeds():
    """Outer AttributeError fallback should recover via np.asarray for assets."""
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    base = _OuterFallbackDF(
        {
            "BTC": np.linspace(0.01, 0.1, 10),
            "ETH": np.linspace(0.02, 0.08, 10),
            "SOL": np.linspace(0.03, 0.07, 10),
        },
        index=idx,
    )
    df = _OuterFallbackAssetDF(base, eth_obj=_BadToNumpyGoodArray(base["ETH"].values))

    res = calculate_rolling_beta(df, "BTC", window=5, min_obs=3)

    assert list(res.columns) == ["BTC", "ETH", "SOL"]
    assert res["BTC"].to_numpy(dtype=float).tolist() == [1.0] * 10
    assert res["ETH"].notna().sum() == 8
    assert res["SOL"].notna().sum() == 8
    assert np.isclose(res.iloc[-1]["ETH"], 0.6666666666666685)
    assert np.isclose(res.iloc[-1]["SOL"], 0.4444444444444549)


def test_beta_outer_fallback_asset_conversions_raise_babdataerror():
    """Outer fallback must raise BABDataError when per-asset coercion fully fails."""
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    base = _OuterFallbackDF(
        {
            "BTC": np.linspace(0.01, 0.1, 10),
            "ETH": np.linspace(0.02, 0.08, 10),
        },
        index=idx,
    )
    df = _OuterFallbackAssetDF(base, eth_obj=_NoArrayNoToNumpy(10))

    with pytest.raises(BABDataError, match=r"array unavailable"):
        calculate_rolling_beta(df, "BTC", window=5, min_obs=3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
