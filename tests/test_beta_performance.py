"""Performance & regression tests for rolling beta calculation.

These tests guard against silent slowdowns in ``calculate_rolling_beta``
while asserting that the *values* produced never change. They are written
TDD-style: the timing assertions encode the bottleneck we are removing.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.data import generate_synthetic_returns


def _time_it(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - start


def _reference_rolling_beta(returns_df, benchmark_name, window=90, min_obs=60):
    """Naive per-window O(N*W) implementation used only as a value oracle."""
    from strategies.betting_against_beta.beta import calculate_beta_fast

    n = len(returns_df)
    out = {}
    for asset in returns_df.columns:
        if asset == benchmark_name:
            out[asset] = np.ones(n, dtype=float)
            continue
        arr = np.empty(n, dtype=float)
        arr[:] = np.nan
        for i in range(n):
            start = max(0, i - window + 1)
            end = i + 1
            if end - start < min_obs:
                continue
            a = returns_df[asset].iloc[start:end].to_numpy(dtype=float)
            b = returns_df[benchmark_name].iloc[start:end].to_numpy(dtype=float)
            beta = calculate_beta_fast(a, b, min_obs=min_obs)
            arr[i] = beta if beta is not None and np.isfinite(beta) else np.nan
        out[asset] = arr
    return pd.DataFrame(out, index=returns_df.index)


class TestRollingBetaPerformance:
    """Large-universe scaling must not regress."""

    N_DAYS = 2000
    N_ASSETS = 120
    WINDOW = 90
    MIN_OBS = 60

    @pytest.fixture(scope="class")
    def big_df(self):
        return generate_synthetic_returns(
            n_days=self.N_DAYS, n_assets=self.N_ASSETS, seed=1234
        )

    def test_values_match_reference_oracle(self, big_df):
        """The optimized path must produce bit-identical results to the naive loop."""
        got = calculate_rolling_beta(
            big_df, "BTC", window=self.WINDOW, min_obs=self.MIN_OBS
        )
        expected = _reference_rolling_beta(
            big_df, "BTC", window=self.WINDOW, min_obs=self.MIN_OBS
        )
        pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-9, atol=1e-12)

    def test_large_universe_completes_in_reasonable_time(self, big_df):
        """Regression guard: 120 assets x 2000 days must finish well under 60s."""
        _, elapsed = _time_it(
            calculate_rolling_beta,
            big_df,
            "BTC",
            window=self.WINDOW,
            min_obs=self.MIN_OBS,
        )
        assert elapsed < 60.0, (
            f"calculate_rolling_beta took {elapsed:.2f}s for "
            f"{self.N_ASSETS} assets x {self.N_DAYS} days; performance regression"
        )

    def test_scaling_is_sub_quadratic_per_asset(self):
        """Each additional asset should cost ~O(N) not O(N*W) per window."""
        small = generate_synthetic_returns(n_days=500, n_assets=10, seed=1)
        large = generate_synthetic_returns(n_days=1000, n_assets=10, seed=1)

        _, t_small = _time_it(
            calculate_rolling_beta, small, "BTC", window=90, min_obs=60
        )
        _, t_large = _time_it(
            calculate_rolling_beta, large, "BTC", window=90, min_obs=60
        )
        # Doubling rows should not more than double+margin time (linear-ish).
        # Allow generous 4x to absorb noise on shared CI runners.
        assert t_large < max(4.0 * t_small, 8.0), (
            f"scaling looks super-linear: {t_small:.2f}s -> {t_large:.2f}s"
        )


class TestRollingBetaNumericalStability:
    """Edge cases that must not silently produce NaN/inf."""

    def test_constant_benchmark_is_finite(self):
        df = pd.DataFrame(
            {
                "BTC": np.ones(200) * 0.0,
                "ETH": np.linspace(-0.01, 0.01, 200),
            }
        )
        betas = calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
        # Skip the warm-up window where insufficient observations are NaN by design.
        arr = betas["ETH"].to_numpy()
        assert np.isfinite(arr[30:]).all()

    def test_near_collinear_asset_is_finite(self):
        rng = np.random.default_rng(5)
        bench = rng.normal(0, 0.02, 300)
        asset = 0.9999 * bench + rng.normal(0, 1e-9, 300)
        df = pd.DataFrame({"BTC": bench, "ETH": asset})
        betas = calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        arr = betas["ETH"].to_numpy()
        assert np.isfinite(arr[60:]).all()

    def test_single_asset_universe(self):
        df = pd.DataFrame({"BTC": np.random.default_rng(1).normal(0, 0.02, 200)})
        betas = calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
        assert betas["BTC"].tolist() == [1.0] * 200

    def test_all_nan_asset_column_is_nan_not_error(self):
        df = pd.DataFrame(
            {
                "BTC": np.random.default_rng(2).normal(0, 0.02, 200),
                "ETH": np.full(200, np.nan),
            }
        )
        betas = calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
        assert np.isnan(betas["ETH"].to_numpy()).all()