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
    """Compute rolling beta series for a single asset."""
    n = len(bench_arr)
    rolling_betas_arr = np.empty(n, dtype=float)
    rolling_betas_arr[:] = np.nan
    for i in range(n):
        start_idx = max(0, i - window + 1)
        end_idx = i + 1
        window_len = end_idx - start_idx
        if window_len < min_obs:
            rolling_betas_arr[i] = np.nan
            continue
        try:
            window_asset = a_arr[start_idx:end_idx]
            window_bench = bench_arr[start_idx:end_idx]
            beta = calculate_beta_fast(window_asset, window_bench, min_obs=min_obs)
            if beta is None or not np.isfinite(beta):
                rolling_betas_arr[i] = np.nan
            else:
                rolling_betas_arr[i] = float(beta)
        except (TypeError, ValueError, AttributeError):
            rolling_betas_arr[i] = np.nan
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
