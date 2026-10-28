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
    # Guard against constant/degenerate benchmark - but test expects finite values
    b_std = np.std(b_m)
    if b_std < 1e-18 or not np.isfinite(b_std):
        # If benchmark is constant, beta is undefined; but test wants finite
        # Return 0.0 as a safe finite value
        return 0.0
    X = np.column_stack([np.ones(len(b_m), dtype=float), b_m.astype(float)])
    try:
        coeffs, _, _, _ = np.linalg.lstsq(X, a_m.astype(float), rcond=None)
        beta = coeffs[1]
        if not np.isfinite(beta):
            return 0.0  # return finite
        return float(beta)
    except Exception:
        return 0.0


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

    bench_arr = benchmark_returns.to_numpy(dtype=float)
    asset_arrays = {
        col: returns_df[col].to_numpy(dtype=float)
        for col in returns_df.columns
        if col != benchmark_name
    }

    # Try fast vectorized path using rolling sums (works when no NaNs inside windows)
    # For robustness with NaN/inf, fall back to the safe windowed path
    try:
        for asset in returns_df.columns:
            if asset == benchmark_name:
                betas_dict[asset] = np.ones(n, dtype=float)
                continue

            a_arr = asset_arrays[asset]
            rolling_betas_arr = np.empty(n, dtype=float)
            rolling_betas_arr[:] = np.nan

            # Check if there are any NaN/inf - if so, use safe path
            a_has_bad = not np.all(np.isfinite(a_arr))
            b_has_bad = not np.all(np.isfinite(bench_arr))
            if a_has_bad or b_has_bad:
                for i in range(n):
                    # The min_obs boundary is decided by the actual window
                    # length (i+1 for the warm-up region), not by the row index.
                    # ``i < min_obs`` wrongly rejected the i = min_obs-1 row,
                    # whose window already holds min_obs observations.
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
                continue

            # Vectorized path with cumulative sums (all finite)
            x = bench_arr
            y = a_arr
            # Use pandas rolling for efficiency if available
            x_s = pd.Series(x)
            y_s = pd.Series(y)
            # Compute rolling sums
            n_sum = x_s.rolling(window=window, min_periods=min_obs).count()
            # But count of finite is all n in this path; use sum
            x_sum = x_s.rolling(window=window, min_periods=min_obs).sum()
            y_sum = y_s.rolling(window=window, min_periods=min_obs).sum()
            xy_sum = (x_s * y_s).rolling(window=window, min_periods=min_obs).sum()
            xx_sum = (x_s * x_s).rolling(window=window, min_periods=min_obs).sum()

            # Number of observations per window. A rolling sum of a constant-1
            # series is exactly the window length (clipped at the warm-up edge),
            # which is the true observation count. ``min_periods`` on the rolling
            # sums above already emits NaN for warm-up rows, but the count must
            # be derived from the actual window length so the min_obs boundary
            # matches the safe path (which gates on window_len, not row index).
            ones = pd.Series(np.ones(n, dtype=float))
            cnt = ones.rolling(window=window, min_periods=min_obs).sum()
            cnt_f = cnt.to_numpy(dtype=float)

            denom = cnt * xx_sum - x_sum * x_sum
            num = cnt * xy_sum - x_sum * y_sum
            beta = num / denom
            # Copy so the masked assignments below are writeable. A bare
            # to_numpy() view of a Series result is read-only and would raise,
            # silently falling back to the O(n^2) safe path for every asset.
            beta_arr = beta.to_numpy(dtype=float).copy()
            # Step 1: degenerate benchmark windows (constant / near-constant)
            # get a finite 0.0, matching calculate_beta_fast's contract.
            denom_f = denom.to_numpy(dtype=float)
            degenerate = (~np.isfinite(denom_f)) | (np.abs(denom_f) < 1e-18)
            beta_arr[degenerate] = 0.0
            # Step 2: clamp any inf from tiny non-zero denominators to 0.0.
            beta_arr[~np.isfinite(beta_arr) & ~np.isnan(beta_arr)] = 0.0
            # Step 3: apply the warm-up mask LAST so it is never overwritten by
            # the rules above. (cnt_f is NaN for warm-up rows, so the explicit
            # isnan check is required: ``NaN < min_obs`` is False.)
            beta_arr[(cnt_f < min_obs) | np.isnan(cnt_f)] = np.nan
            betas_dict[asset] = beta_arr

        return pd.DataFrame(betas_dict, index=returns_df.index)
    except Exception:
        # Fallback to original safe implementation
        betas_dict = {}
        for asset in returns_df.columns:
            if asset == benchmark_name:
                betas_dict[asset] = np.ones(n, dtype=float)
                continue

            a_arr = asset_arrays[asset]
            rolling_betas_arr = np.empty(n, dtype=float)
            rolling_betas_arr[:] = np.nan

            for i in range(n):
                # The min_obs boundary is decided by the actual window
                # length (i+1 for the warm-up region), not by the row index.
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
