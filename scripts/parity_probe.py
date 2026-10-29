#!/usr/bin/env python3
"""Parity probe: compare the cumsum vectorized path vs the pandas rolling path
for all-finite data, so we can route the fast path through the vectorized one
without changing numerics.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.beta import _calc_rolling_beta_series


def pandas_path(bench_arr, a_arr, window, min_obs):
    n = len(bench_arr)
    x_s = pd.Series(bench_arr)
    y_s = pd.Series(a_arr)
    xy_s = x_s * y_s
    xx_s = x_s * x_s
    ones_s = pd.Series(np.ones(n, dtype=float))
    cnt = ones_s.rolling(window=window, min_periods=min_obs).sum()
    x_sum = x_s.rolling(window=window, min_periods=min_obs).sum()
    y_sum = y_s.rolling(window=window, min_periods=min_obs).sum()
    xy_sum = xy_s.rolling(window=window, min_periods=min_obs).sum()
    xx_sum = xx_s.rolling(window=window, min_periods=min_obs).sum()
    cnt_f = cnt.to_numpy(dtype=float, copy=False)
    denom = cnt * xx_sum - x_sum * x_sum
    num = cnt * xy_sum - x_sum * y_sum
    beta = num / denom
    beta_arr = beta.to_numpy(dtype=float).copy()
    denom_f = denom.to_numpy(dtype=float, copy=False)
    degenerate = (~np.isfinite(denom_f)) | (np.abs(denom_f) < 1e-18)
    beta_arr[degenerate] = 0.0
    beta_arr[~np.isfinite(beta_arr) & ~np.isnan(beta_arr)] = 0.0
    beta_arr[(cnt_f < min_obs) | np.isnan(cnt_f)] = np.nan
    return beta_arr


def main():
    rng = np.random.default_rng(42)
    n = 150
    bench = rng.normal(0, 0.01, n)
    worst = 0.0
    worst_mask_diff = 0
    for trial in range(200):
        a = rng.normal(0, 0.01, n)
        p = pandas_path(bench, a, 90, 60)
        v = _calc_rolling_beta_series(bench, a, 90, 60)
        mask_diff = np.isnan(p) != np.isnan(v)
        worst_mask_diff += int(mask_diff.sum())
        both = np.isfinite(p) & np.isfinite(v)
        if both.any():
            worst = max(worst, float(np.max(np.abs(p[both] - v[both]))))
    print(f"trials=200 max_abs_diff={worst:.3e} nan_mask_mismatches={worst_mask_diff}")

    # Constant asset edge case
    a = np.zeros(n)
    p = pandas_path(bench, a, 90, 60)
    v = _calc_rolling_beta_series(bench, a, 90, 60)
    print("constant asset: nan-mask match =", np.array_equal(np.isnan(p), np.isnan(v)),
          "max abs diff =", float(np.max(np.abs(np.nan_to_num(p) - np.nan_to_num(v)))))

    # Constant benchmark edge case
    a = rng.normal(0, 0.01, n)
    bench_c = np.full(n, 0.001)
    p = pandas_path(bench_c, a, 90, 60)
    v = _calc_rolling_beta_series(bench_c, a, 90, 60)
    print("constant bench: nan-mask match =", np.array_equal(np.isnan(p), np.isnan(v)),
          "max abs diff =", float(np.max(np.nan_to_num(p) - np.nan_to_num(v))))


if __name__ == "__main__":
    main()