"""TDD test: rolling beta must pre-convert columns to numpy arrays once.

The naive path re-slices pandas Series per window (O(N*W) pandas overhead
plus O(N) per window for index bookkeeping). Pre-converting every column to a
numpy array once and slicing the raw ndarray is dramatically faster while
producing bit-identical beta values because calculate_beta_fast already works
on numpy arrays.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.data import generate_synthetic_returns


def _reference_rolling_beta(returns_df, benchmark_name, window=90, min_obs=60):
    from strategies.betting_against_beta.beta import calculate_beta

    n = len(returns_df)
    out = {}
    for asset in returns_df.columns:
        if asset == benchmark_name:
            out[asset] = np.ones(n, dtype=float)
            continue
        arr = np.empty(n, dtype=float)
        arr[:] = np.nan
        for i in range(n):
            if i < min_obs:
                continue
            start = max(0, i - window + 1)
            end = i + 1
            if end - start < min_obs:
                continue
            a = returns_df[asset].iloc[start:end].to_numpy(dtype=float)
            b = returns_df[benchmark_name].iloc[start:end].to_numpy(dtype=float)
            beta = calculate_beta(a, b, min_obs=min_obs)
            arr[i] = beta if beta is not None and np.isfinite(beta) else np.nan
        out[asset] = arr
    return pd.DataFrame(out, index=returns_df.index)


class TestRollingBetaNumpyCache:
    N_DAYS = 2000
    N_ASSETS = 120
    WINDOW = 90
    MIN_OBS = 60

    @pytest.fixture(scope="class")
    def big_df(self):
        return generate_synthetic_returns(
            n_days=self.N_DAYS, n_assets=self.N_ASSETS, seed=1234
        )

    def test_values_identical_to_oracle(self, big_df):
        got = calculate_rolling_beta(
            big_df, "BTC", window=self.WINDOW, min_obs=self.MIN_OBS
        )
        expected = _reference_rolling_beta(
            big_df, "BTC", window=self.WINDOW, min_obs=self.MIN_OBS
        )
        pd.testing.assert_frame_equal(
            got, expected, check_exact=False, rtol=1e-9, atol=1e-12
        )

    def test_fast_enough_with_numpy_cache(self, big_df):
        start = time.perf_counter()
        calculate_rolling_beta(
            big_df, "BTC", window=self.WINDOW, min_obs=self.MIN_OBS
        )
        elapsed = time.perf_counter() - start
        assert elapsed < 15.0, (
            f"calculate_rolling_beta took {elapsed:.2f}s for "
            f"{self.N_ASSETS} assets x {self.N_DAYS} days; numpy caching missing"
        )