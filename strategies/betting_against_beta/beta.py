"""Beta calculation for BAB strategy."""

import numpy as np
import pandas as pd

from .data_loader import BABDataError


def calculate_beta(asset_returns, benchmark_returns, min_obs=None):
    """Calculate beta of asset vs benchmark using OLS regression."""
    try:
        # Fast path with numpy
        a = np.asarray(asset_returns, dtype=float).ravel()
        b = np.asarray(benchmark_returns, dtype=float).ravel()
        if len(a) != len(b):
            # Try to align as Series if different lengths
            if isinstance(asset_returns, (pd.Series,)) or isinstance(benchmark_returns, (pd.Series,)):
                try:
                    if isinstance(asset_returns, np.ndarray):
                        asset_returns = pd.Series(asset_returns)
                    if isinstance(benchmark_returns, np.ndarray):
                        benchmark_returns = pd.Series(benchmark_returns)
                    if isinstance(asset_returns, list):
                        asset_returns = pd.Series(asset_returns)
                    if isinstance(benchmark_returns, list):
                        benchmark_returns = pd.Series(benchmark_returns)
                    aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
                    if len(aligned) == 0:
                        return np.nan
                    if min_obs is not None and len(aligned) < min_obs:
                        return np.nan
                    y = aligned.iloc[:, 0].to_numpy(dtype=float, copy=False)
                    x = aligned.iloc[:, 1].to_numpy(dtype=float, copy=False)
                except (TypeError, ValueError, AttributeError):
                    return np.nan
            else:
                # Truncate to common length
                n = min(len(a), len(b))
                a = a[:n]
                b = b[:n]
        else:
            y = a
            x = b

        # Check for finite values
        mask = np.isfinite(y) & np.isfinite(x)
        if not np.any(mask):
            return np.nan
        if not np.all(mask):
            y = y[mask]
            x = x[mask]
        if len(y) == 0:
            return np.nan
        if min_obs is not None and len(y) < min_obs:
            return np.nan

        # Add intercept and solve via lstsq (efficient)
        X = np.column_stack([np.ones(len(x), dtype=float), x])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
            beta = coeffs[1]
            if not np.isfinite(beta):
                return np.nan
            return float(beta)
        except np.linalg.LinAlgError:
            return np.nan
    except (TypeError, ValueError, AttributeError):
        return np.nan
    except BABDataError:
        raise


def calculate_beta_fast(a, b, min_obs=None):
    """Fast beta calculation with pre-converted arrays."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    if not np.any(mask):
        return np.nan
    if not np.all(mask):
        a_m = a[mask]
        b_m = b[mask]
    else:
        a_m = a
        b_m = b
    if len(a_m) == 0:
        return np.nan
    if min_obs is not None and len(a_m) < min_obs:
        return np.nan
    # Guard against constant/degenerate benchmark
    b_std = np.std(b_m)
    if b_std < 1e-18 or not np.isfinite(b_std):
        return 0.0
    X = np.column_stack([np.ones(len(b_m), dtype=float), b_m])
    try:
        coeffs, _, _, _ = np.linalg.lstsq(X, a_m, rcond=None)
        beta = coeffs[1]
        if not np.isfinite(beta):
            return 0.0
        return float(beta)
    except np.linalg.LinAlgError:
        return 0.0
    except (TypeError, ValueError, AttributeError):
        return 0.0


def _calc_rolling_beta_series(bench_arr, a_arr, window, min_obs):
    """Compute rolling beta series for a single asset (fully vectorized).

    Same numerics as the previous per-row loop: OLS slope per window derived
    from cumulative sums, with degenerate windows -> 0.0 and insufficient /
    non-finite windows -> NaN.
    """
    n = len(bench_arr)
    rolling_betas_arr = np.empty(n, dtype=float)
    rolling_betas_arr[:] = np.nan
    if n == 0:
        return rolling_betas_arr
    bench_arr_f = np.asarray(bench_arr, dtype=float)
    a_arr_f = np.asarray(a_arr, dtype=float)
    # Precompute products
    xy = a_arr_f * bench_arr_f
    xx = bench_arr_f * bench_arr_f
    ones = np.ones(n, dtype=float)
    # Cumulative sums (NaN propagates, matching the legacy per-row semantics)
    csum1 = np.concatenate(([0.0], np.cumsum(ones)))
    csumx = np.concatenate(([0.0], np.cumsum(bench_arr_f)))
    csumy = np.concatenate(([0.0], np.cumsum(a_arr_f)))
    csumxy = np.concatenate(([0.0], np.cumsum(xy)))
    csumxx = np.concatenate(([0.0], np.cumsum(xx)))

    idx = np.arange(n)
    starts = np.maximum(0, idx - window + 1)
    ends = idx + 1
    window_len = ends - starts

    cnt = csum1[ends] - csum1[starts]
    x_sum = csumx[ends] - csumx[starts]
    y_sum = csumy[ends] - csumy[starts]
    xy_sum = csumxy[ends] - csumxy[starts]
    xx_sum = csumxx[ends] - csumxx[starts]

    with np.errstate(invalid="ignore", divide="ignore"):
        denom = cnt * xx_sum - x_sum * x_sum
        num = cnt * xy_sum - x_sum * y_sum
        beta = np.divide(num, denom)

    degenerate = (~np.isfinite(denom)) | (np.abs(denom) < 1e-18)
    enough = window_len >= min_obs

    rolling_betas_arr[:] = np.nan
    rolling_betas_arr[enough & degenerate] = 0.0
    valid = enough & ~degenerate & np.isfinite(beta)
    rolling_betas_arr[valid] = beta[valid]
    return rolling_betas_arr


def calculate_rolling_beta(returns_df, benchmark_name, window=90, min_obs=60):
    """Calculate rolling beta for all assets vs benchmark."""
    if returns_df is None:
        raise BABDataError("returns_df is None")
    if not isinstance(returns_df, pd.DataFrame):
        raise BABDataError(f"Expected DataFrame, got {type(returns_df).__name__}")
    if benchmark_name not in returns_df.columns:
        raise BABDataError(f"Benchmark {benchmark_name} not found in returns")

    benchmark_returns = returns_df[benchmark_name]
    bench_vals = benchmark_returns.to_numpy(dtype=float)
    if not np.isfinite(bench_vals).any():
        raise BABDataError(
            f"Benchmark '{benchmark_name}' has no finite return values; "
            "cannot estimate betas against it"
        )

    n = len(returns_df)
    betas_dict = {}

    bench_arr = benchmark_returns.to_numpy(dtype=float, copy=False)
    asset_arrays = {
        col: returns_df[col].to_numpy(dtype=float, copy=False)
        for col in returns_df.columns
        if col != benchmark_name
    }

    try:
        for asset in returns_df.columns:
            if asset == benchmark_name:
                betas_dict[asset] = np.ones(n, dtype=float)
                continue

            a_arr = asset_arrays[asset]

            a_has_bad = not np.all(np.isfinite(a_arr))
            b_has_bad = not np.all(np.isfinite(bench_arr))
            if a_has_bad or b_has_bad:
                betas_dict[asset] = _calc_rolling_beta_series(bench_arr, a_arr, window, min_obs)
                continue

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
            betas_dict[asset] = beta_arr

        return pd.DataFrame(betas_dict, index=returns_df.index)
    except BABDataError:
        raise
    except (TypeError, ValueError, AttributeError):
        betas_dict = {}
        for asset in returns_df.columns:
            if asset == benchmark_name:
                betas_dict[asset] = np.ones(n, dtype=float)
                continue
            betas_dict[asset] = _calc_rolling_beta_series(bench_arr, asset_arrays[asset], window, min_obs)
        return pd.DataFrame(betas_dict, index=returns_df.index)
