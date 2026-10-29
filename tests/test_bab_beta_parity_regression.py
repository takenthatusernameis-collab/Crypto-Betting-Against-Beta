"""Regression/parity tests for vectorized rolling beta vs slow reference."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.beta import calculate_rolling_beta


def _slow_rolling_beta_match_impl(returns_df: pd.DataFrame, benchmark_name: str, window: int = 90, min_obs: int = 60) -> pd.DataFrame:
    """Reference matching implementation semantics."""
    bench_arr = returns_df[benchmark_name].to_numpy(dtype=float)
    n = len(returns_df)
    ones_s = pd.Series(np.ones(n, dtype=float))
    x_s = pd.Series(bench_arr)
    xx_s = x_s * x_s
    cnt_s = ones_s.rolling(window=window, min_periods=min_obs).sum()
    x_sum_s = x_s.rolling(window=window, min_periods=min_obs).sum()
    xx_sum_s = xx_s.rolling(window=window, min_periods=min_obs).sum()
    cnt_f = cnt_s.to_numpy(dtype=float)
    x_sum_f = x_sum_s.to_numpy(dtype=float)
    xx_sum_f = xx_sum_s.to_numpy(dtype=float)
    denom_shared = cnt_f[:, None] * xx_sum_f[:, None] - x_sum_f[:, None] * x_sum_f[:, None]
    obs_short = (cnt_f < min_obs) | np.isnan(cnt_f)

    def _finalize(beta_arr):
        beta_arr = np.asarray(beta_arr, dtype=float)
        degenerate = (~np.isfinite(denom_shared)) | (np.abs(denom_shared) < 1e-18)
        beta_arr = np.where(degenerate, 0.0, beta_arr)
        beta_arr = np.where(~np.isfinite(beta_arr) & ~np.isnan(beta_arr), 0.0, beta_arr)
        beta_arr = np.where(obs_short[:, None], np.nan, beta_arr)
        return beta_arr

    out = {}
    for c in returns_df.columns:
        if c == benchmark_name:
            out[c] = np.ones(n, dtype=float)
            continue
        a_arr = returns_df[c].to_numpy(dtype=float)
        # For all-finite case like fast path
        if np.all(np.isfinite(a_arr)) and np.all(np.isfinite(bench_arr)):
            y_s = pd.Series(a_arr)
            xy_s = pd.Series(a_arr * bench_arr)
            y_sum_f = y_s.rolling(window=window, min_periods=min_obs).sum().to_numpy(dtype=float)
            xy_sum_f = xy_s.rolling(window=window, min_periods=min_obs).sum().to_numpy(dtype=float)
            num = cnt_f * xy_sum_f - x_sum_f * y_sum_f
            beta = num / denom_shared[:, 0]
            beta = _finalize(beta.reshape(-1, 1))[:, 0]
            out[c] = beta
        else:
            # fall back to series path behavior
            from strategies.betting_against_beta.beta import _calc_rolling_beta_series
            out[c] = _calc_rolling_beta_series(bench_arr, a_arr, window, min_obs)
    return pd.DataFrame(out, index=returns_df.index)


def test_rolling_beta_parity_synthetic_seeds():
    rng = np.random.RandomState(12345)
    dates = pd.date_range("2023-01-01", periods=400)
    assets = ["BTC", "ETH", "SOL", "BNB"]
    bench = rng.normal(0, 0.02, len(dates))
    rets = {a: rng.normal(0, 0.03, len(dates)) + 0.8 * bench + rng.normal(0, 0.01, len(dates)) for a in assets}
    rets["BTC"] = bench
    df = pd.DataFrame(rets, index=dates)
    window = 90
    fast = calculate_rolling_beta(df, benchmark_name="BTC", window=window, min_obs=60)
    slow = _slow_rolling_beta_match_impl(df, benchmark_name="BTC", window=window, min_obs=60)
    common = fast.notna() & slow.notna()
    assert common.sum().sum() > 0
    diff = (fast - slow).abs()
    assert diff[common].max().max() < 1e-10


def test_rolling_beta_parity_with_nans():
    rng = np.random.RandomState(54321)
    dates = pd.date_range("2023-01-01", periods=200)
    df = pd.DataFrame({
        "BTC": rng.normal(0, 0.02, len(dates)),
        "ETH": rng.normal(0, 0.03, len(dates)),
        "SOL": rng.normal(0, 0.04, len(dates)),
    }, index=dates)
    df.iloc[10:15, 1] = np.nan
    df.iloc[50, 2] = np.nan
    df.iloc[120:125, 0] = np.nan
    window = 60
    fast = calculate_rolling_beta(df, benchmark_name="BTC", window=window, min_obs=30)
    slow = _slow_rolling_beta_match_impl(df, benchmark_name="BTC", window=window, min_obs=30)
    common = fast.notna() & slow.notna()
    assert common.values.sum() > 0
    diff = (fast - slow).abs()
    assert diff[common].max().max() < 1e-10


def test_rolling_beta_parity_with_infs():
    rng = np.random.RandomState(999)
    dates = pd.date_range("2023-01-01", periods=150)
    df = pd.DataFrame({
        "BTC": rng.normal(0, 0.02, len(dates)),
        "ETH": rng.normal(0, 0.03, len(dates)),
    }, index=dates)
    df.iloc[5, 1] = np.inf
    df.iloc[80, 0] = -np.inf
    window = 45
    fast = calculate_rolling_beta(df, benchmark_name="BTC", window=window, min_obs=30)
    slow = _slow_rolling_beta_match_impl(df, benchmark_name="BTC", window=window, min_obs=30)
    common = fast.notna() & slow.notna()
    assert common.values.sum() > 0
    diff = (fast - slow).abs()
    assert diff[common].max().max() < 1e-10
