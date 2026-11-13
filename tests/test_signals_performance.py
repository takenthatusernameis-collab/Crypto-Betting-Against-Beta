"""Performance & regression tests for signal generation.

Guards ``generate_bab_signals`` against silent slowdowns while asserting the
*rank/selection values* never change relative to the original implementation.
The optimized path drops a redundant frame copy, a dead zeros array, and two
impossible finiteness guards, but keeps the exact double-argsort ranking, so
these tests pin bit-identical selection (including NaN/inf/ties) and speed.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.signals import generate_bab_signals
from strategies.betting_against_beta.data import generate_synthetic_returns


def _reference_generate_bab_signals(betas_df, long_quantile=0.3, short_quantile=0.3):
    """Faithful copy of the pre-optimization vectorized algorithm (ground truth).

    Reproduces the historical rank computation and masking exactly (raw double
    argsort primary, masked +inf fallback, per-row quantile counts, overlap
    resolution), so the optimized path can be compared bit-for-bit including its
    NaN/inf/tie handling.
    """
    if betas_df is None:
        return pd.DataFrame()
    if not isinstance(betas_df, pd.DataFrame) or betas_df.empty:
        return pd.DataFrame()

    try:
        if all(pd.api.types.is_numeric_dtype(s) for s in betas_df.dtypes):
            beta_df = betas_df.copy()
        else:
            beta_df = betas_df.apply(pd.to_numeric, errors="coerce")
        beta_arr = beta_df.to_numpy(dtype=float)
    except Exception:
        try:
            beta_df = betas_df.copy()
            beta_df = beta_df.apply(pd.to_numeric, errors="coerce")
            beta_arr = beta_df.to_numpy(dtype=float)
        except Exception:
            return pd.DataFrame(0, index=betas_df.index, columns=betas_df.columns, dtype="int64")

    finite = np.isfinite(beta_arr)
    counts = finite.sum(axis=1)
    n_rows, n_cols = beta_arr.shape
    signals_arr = np.zeros((n_rows, n_cols), dtype=np.int64)

    valid = counts >= 2
    if not np.any(valid):
        return pd.DataFrame(signals_arr, index=betas_df.index, columns=betas_df.columns)

    try:
        rank = np.argsort(np.argsort(beta_arr, axis=1, kind="stable"), axis=1, kind="stable")
    except Exception:
        rank = np.argsort(np.argsort(np.where(finite, beta_arr, np.inf), axis=1), axis=1)

    cnt_valid = counts[valid]
    if long_quantile == 0.0:
        n_long = np.zeros_like(cnt_valid, dtype=np.int64)
    else:
        n_long = np.maximum(1, np.floor(cnt_valid * long_quantile).astype(np.int64))
    if short_quantile == 0.0:
        n_short = np.zeros_like(cnt_valid, dtype=np.int64)
    else:
        n_short = np.maximum(1, np.floor(cnt_valid * short_quantile).astype(np.int64))
    overlap = n_long + n_short > cnt_valid
    n_short[overlap] = np.maximum(0, cnt_valid[overlap] - n_long[overlap])
    n_short = np.where(n_long >= cnt_valid, 0, n_short)

    n_long_full = np.zeros(n_rows, dtype=np.int64)
    n_short_full = np.zeros(n_rows, dtype=np.int64)
    n_long_full[valid] = n_long
    n_short_full[valid] = n_short

    cnt_col = counts.astype(np.int64)[:, None]
    long_mask = finite & (rank < n_long_full[:, None])
    short_mask = finite & (rank >= (cnt_col - n_short_full[:, None]))
    short_mask = short_mask & ~long_mask
    signals_arr = long_mask.astype(np.int64) - short_mask.astype(np.int64)
    return pd.DataFrame(signals_arr, index=betas_df.index, columns=betas_df.columns)


def _time_it(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - start


def _random_betas(rng, n, m):
    arr = rng.normal(0.0, 1.0, size=(n, m))
    if n and m:
        arr[rng.random((n, m)) < 0.1] = np.nan
        arr[rng.random((n, m)) < 0.05] = np.inf
        arr[rng.random((n, m)) < 0.05] = -np.inf
        if n > 2:
            arr[int(rng.integers(0, n))] = 0.0
    cols = [f"c{i}" for i in range(m - 1)] + ["BTC"]
    return pd.DataFrame(arr, columns=cols)


class TestGenerateBabSignalsEquivalence:
    N_DAYS = 2000
    N_ASSETS = 120

    @pytest.fixture(scope="class")
    def betas(self):
        return calculate_rolling_beta(
            generate_synthetic_returns(n_days=self.N_DAYS, n_assets=self.N_ASSETS, seed=1234),
            "BTC",
            window=90,
            min_obs=60,
        )

    def test_large_universe_matches_reference(self, betas):
        for lq, sq in [(0.3, 0.3), (0.5, 0.5), (0.1, 0.9), (1.0, 1.0)]:
            got = generate_bab_signals(betas, long_quantile=lq, short_quantile=sq)
            expected = _reference_generate_bab_signals(betas, long_quantile=lq, short_quantile=sq)
            pd.testing.assert_frame_equal(got, expected)

    def test_randomized_reference_equivalence(self):
        """300 randomized NaN/inf/tie frames must match the original exactly."""
        rng = np.random.default_rng(20261113)
        for _ in range(300):
            n = int(rng.integers(2, 40))
            m = int(rng.integers(2, 15))
            df = _random_betas(rng, n, m)
            lq = float(rng.choice([0.0, 0.1, 0.25, 0.3, 0.5, 0.9, 1.0]))
            sq = float(rng.choice([0.0, 0.1, 0.25, 0.3, 0.5, 0.9, 1.0]))
            got = generate_bab_signals(df, long_quantile=lq, short_quantile=sq)
            expected = _reference_generate_bab_signals(df, long_quantile=lq, short_quantile=sq)
            pd.testing.assert_frame_equal(got, expected)

    def test_all_flat_rows_short_circuit(self):
        df = pd.DataFrame(
            {"A": [np.nan, np.inf, np.nan], "B": [np.nan, np.nan, -np.inf]},
        )
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert (out.to_numpy() == 0).all()

    def test_no_nan_or_inf_in_output(self):
        rng = np.random.default_rng(9)
        out = generate_bab_signals(_random_betas(rng, 50, 10))
        assert np.isfinite(out.to_numpy()).all()
        assert set(np.unique(out.to_numpy())).issubset({-1, 0, 1})


class TestGenerateBabSignalsPerformance:
    N_DAYS = 2000
    N_ASSETS = 120

    @pytest.fixture(scope="class")
    def betas(self):
        return calculate_rolling_beta(
            generate_synthetic_returns(n_days=self.N_DAYS, n_assets=self.N_ASSETS, seed=1234),
            "BTC",
            window=90,
            min_obs=60,
        )

    def test_large_universe_completes_in_reasonable_time(self, betas):
        _, elapsed = _time_it(generate_bab_signals, betas, 0.3, 0.3)
        assert elapsed < 30.0, (
            f"generate_bab_signals took {elapsed:.2f}s for {betas.shape}; "
            "performance regression"
        )

    def test_signals_stage_perf_ceiling(self, betas):
        """Generous, CI-stable ceiling guarding against a catastrophic slowdown."""
        _, elapsed = _time_it(generate_bab_signals, betas, 0.3, 0.3)
        assert elapsed < 1.0, (
            f"generate_bab_signals took {elapsed:.3f}s on {betas.shape}; "
            "signals-stage perf regression"
        )