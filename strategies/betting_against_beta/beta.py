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
                    y = aligned.iloc[:, 0].to_numpy(dtype=float)
                    x = aligned.iloc[:, 1].to_numpy(dtype=float)
                except Exception:
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
        X = np.column_stack([np.ones(len(x), dtype=float), x.astype(float)])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(X, y.astype(float), rcond=None)
            beta = coeffs[1]
            if not np.isfinite(beta):
                return np.nan
            return float(beta)
        except Exception:
            return np.nan
    except Exception:
        return np.nan


def calculate_rolling_beta(returns_df, benchmark_name, window=90, min_obs=60):
    """Calculate rolling beta for all assets vs benchmark."""
    if returns_df is None:
        raise BABDataError("returns_df is None")
    if not isinstance(returns_df, pd.DataFrame):
        raise BABDataError(f"Expected DataFrame, got {type(returns_df).__name__}")
    if benchmark_name not in returns_df.columns:
        raise BABDataError(f"Benchmark {benchmark_name} not found in returns")

    benchmark_returns = returns_df[benchmark_name]
    # An all-NaN benchmark makes beta estimation impossible; refuse loudly.
    bench_vals = benchmark_returns.to_numpy(dtype=float)
    if not np.isfinite(bench_vals).any():
        raise BABDataError(
            f"Benchmark '{benchmark_name}' has no finite return values; "
            "cannot estimate betas against it"
        )

    n = len(returns_df)
    betas_dict = {}

    # Pre-convert every column to a numpy array ONCE. The previous path sliced
    # pandas Series per window (O(N*W) pandas overhead plus O(N) index
    # bookkeeping per window), which dominated runtime on large universes.
    # Slicing raw ndarrays is dramatically cheaper while producing identical
    # values because calculate_beta_fast already operates on numpy arrays.
    bench_arr = benchmark_returns.to_numpy(dtype=float)
    asset_arrays = {
        col: returns_df[col].to_numpy(dtype=float)
        for col in returns_df.columns
        if col != benchmark_name
    }

    for asset in returns_df.columns:
        if asset == benchmark_name:
            betas_dict[asset] = np.ones(n, dtype=float)
            continue

        a_arr = asset_arrays[asset]
        rolling_betas_arr = np.empty(n, dtype=float)
        rolling_betas_arr[:] = np.nan

        for i in range(n):
            if i < min_obs:
                rolling_betas_arr[i] = np.nan
                continue
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
            except Exception:
                rolling_betas_arr[i] = np.nan
        betas_dict[asset] = rolling_betas_arr

    return pd.DataFrame(betas_dict, index=returns_df.index)


def calculate_beta_fast(a, b, min_obs=None):
    """Fast beta calculation with pre-converted arrays."""
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
    X = np.column_stack([np.ones(len(b_m), dtype=float), b_m.astype(float)])
    try:
        coeffs, _, _, _ = np.linalg.lstsq(X, a_m.astype(float), rcond=None)
        beta = coeffs[1]
        if not np.isfinite(beta):
            return np.nan
        return float(beta)
    except Exception:
        return np.nan
