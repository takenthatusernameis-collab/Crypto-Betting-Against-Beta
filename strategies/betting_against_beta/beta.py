"""Beta calculation for BAB strategy."""

import numpy as np
import pandas as pd

from .data_loader import BABDataError


def estimate_betas(returns_df, benchmark=None, window=90, min_obs=None, min_observations=None):
    if benchmark is None and hasattr(returns_df, "columns"):
        # try to guess - not common; fall back
        pass
    if min_observations is not None and min_obs is None:
        min_obs = min_observations
    if min_obs is not None and window is not None and min_obs > window:
        min_obs = window
    if min_obs is None:
        min_obs = min(window, 60) if window is not None else 60
    return calculate_rolling_beta(returns_df, benchmark, window=window, min_obs=min_obs)


def rolling_beta(a, b, window=90, min_periods=None, min_obs=None):
    import pandas as pd
    if min_periods is not None and min_obs is None:
        min_obs = min_periods
    if min_obs is not None and window is not None and min_obs > window:
        min_obs = window
    if min_obs is None:
        min_obs = min(window, 60) if window is not None else 60
    # Accept series
    if isinstance(a, pd.Series) and isinstance(b, pd.Series):
        df = pd.concat([b, a], axis=1)
        df.columns = ["benchmark", "asset"]
        res = calculate_rolling_beta(df, "benchmark", window=window, min_obs=min_obs)
        return res["asset"]
    # try generic
    try:
        return _calc_rolling_beta_series(b, a, window, min_obs)
    except Exception:
        try:
            return _calc_rolling_beta_series(np.asarray(b), np.asarray(a), window, min_obs)
        except Exception:
            # Return empty/NaN series-like array if possible
            n = 0
            for cand in (a, b):
                try:
                    n = len(cand)
                    break
                except Exception:
                    continue
            if n == 0:
                try:
                    n = len(np.asarray(a))
                except Exception:
                    try:
                        n = len(np.asarray(b))
                    except Exception:
                        n = 0
            try:
                if n == 0:
                    res = np.array([np.nan])
                    return res
                res = np.empty(n)
                res[:] = np.nan
                return res
            except Exception:
                return np.array([np.nan])




def calculate_beta(asset_returns, benchmark_returns, min_obs=None):
    """Calculate beta of asset vs benchmark using OLS regression."""
    if asset_returns is None or benchmark_returns is None:
        raise BABDataError("asset_returns and benchmark_returns must not be None")
    try:
        # Fast path with numpy
        a = np.asarray(asset_returns, dtype=float).ravel()
        b = np.asarray(benchmark_returns, dtype=float).ravel()
        y = None
        x = None
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
                y = a
                x = b
        else:
            y = a
            x = b
        if y is None or x is None:
            return np.nan

        # Check for finite values
        mask = np.isfinite(y) & np.isfinite(x)
        if not np.any(mask):
            return np.nan
        if not np.all(mask):
            y = y[mask]
            x = x[mask]
        if len(y) == 0:
            return np.nan
        if min_obs is not None:
            try:
                mo = int(min_obs)
                if mo > 0 and len(y) < mo:
                    return np.nan
            except Exception:
                pass
        # Guard against constant/degenerate benchmark
        x_std = np.std(x)
        if x_std < 1e-12 or not np.isfinite(x_std):
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
    try:
        try:
            a = np.asarray(a, dtype=float)
            b = np.asarray(b, dtype=float)
        except (TypeError, ValueError, AttributeError):
            return np.nan
        if a is None or b is None:
            return np.nan
        if getattr(a, "ndim", 0) != 1 or getattr(b, "ndim", 0) != 1:
            return np.nan
        # Flatten
        try:
            a = np.array(a).ravel()
            b = np.array(b).ravel()
        except Exception:
            return np.nan
        if len(a) == 0 or len(b) == 0:
            return np.nan
        # If lengths differ, align
        if len(a) != len(b):
            n = min(len(a), len(b))
            a = a[:n]
            b = b[:n]
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
        if min_obs is not None:
            try:
                mo = int(min_obs)
                if mo > 0 and len(a_m) < mo:
                    return np.nan
            except Exception:
                return np.nan
        # Guard against constant/degenerate benchmark.  A zero-variance
        # benchmark carries no information, so beta is undefined.  Return NaN
        # to match calculate_beta() and metrics.strategy_beta() rather than a
        # synthetic 0.0 that would silently corrupt downstream ranking.
        b_std = np.std(b_m)
        if b_std < 1e-12 or not np.isfinite(b_std):
            return np.nan
        X = np.column_stack([np.ones(len(b_m), dtype=float), b_m])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(X, a_m, rcond=None)
            beta = coeffs[1]
            if (not np.isscalar(beta)) or not np.isfinite(beta):
                # Undefined beta (singular fit) is NaN, never a synthetic 0.0
                # that would be ranked as a valid low-beta signal.
                return np.nan
            return float(beta)
        except np.linalg.LinAlgError:
            # Singular design matrix -> beta is undefined, not zero.
            return np.nan
        except (TypeError, ValueError, AttributeError):
            return np.nan
    except (TypeError, ValueError, AttributeError):
        return np.nan


def _calc_rolling_beta_series(bench_arr, a_arr, window, min_obs):
    """Compute rolling beta series for a single asset (fully vectorized).

    Same numerics as the previous per-row loop: OLS slope per window derived
    from cumulative sums, with degenerate windows -> 0.0 and insufficient /
    non-finite windows -> NaN.

    NaN-safe: non-finite observations are masked to 0.0 before the cumulative
    sums so a single NaN in the benchmark or asset series does not poison every
    subsequent window (the old ``np.cumsum`` path propagated NaN forward).
    """
    n = len(bench_arr)
    rolling_betas_arr = np.empty(n, dtype=float)
    rolling_betas_arr[:] = np.nan
    if n == 0:
        return rolling_betas_arr
    bench_arr_f = np.asarray(bench_arr, dtype=float)
    a_arr_f = np.asarray(a_arr, dtype=float)
    # Mask non-finite entries so cumulative sums stay finite.  The valid-observation
    # count is tracked separately via ``ones`` (1.0 only where both inputs are finite).
    finite_mask = np.isfinite(bench_arr_f) & np.isfinite(a_arr_f)
    b_safe = np.where(finite_mask, bench_arr_f, 0.0)
    a_safe = np.where(finite_mask, a_arr_f, 0.0)
    ones = np.where(finite_mask, 1.0, 0.0)

    xy = a_safe * b_safe
    xx = b_safe * b_safe
    # Cumulative sums over the NaN-safe arrays; ``cnt`` is the real number of
    # valid observations per window, not the window length.
    csum1 = np.concatenate(([0.0], np.cumsum(ones)))
    csumx = np.concatenate(([0.0], np.cumsum(b_safe)))
    csumy = np.concatenate(([0.0], np.cumsum(a_safe)))
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

    # Degeneracy is PER-WINDOW, not whole-series. ``denom`` is exactly
    # cnt*xx - x^2, which is zero (or non-finite) exactly when the benchmark
    # has zero variance *within that window*. A single NaN in the benchmark
    # must not poison every window: non-finite entries are masked to 0.0 and
    # counted separately via ``cnt``, so a window with one bad observation
    # still has the correct count and sums for the remaining valid ones.
    # A whole-series np.std(bench_arr) check would collapse the entire series
    # to NaN on any benchmark NaN -- that is undefined-beta poisoning, not
    # undefined beta, and it silently flattens real signals.
    degenerate = (~np.isfinite(denom)) | (np.abs(denom) < 1e-12)
    # Enough valid observations to estimate a beta (not just window length).
    enough = cnt >= min_obs

    rolling_betas_arr[:] = np.nan
    rolling_betas_arr[enough & degenerate] = np.nan
    valid = enough & ~degenerate & np.isfinite(beta)
    rolling_betas_arr[valid] = beta[valid]
    return rolling_betas_arr


def _rolling_sum(arr, window, min_periods):
    """NaN-safe rolling window sum matching pandas ``.rolling(window, min_periods).sum()``.

    Non-finite entries are masked to 0.0 before the cumulative sum and counted
    separately via ``ones`` so a single NaN does not poison the window sum.
    Windows with fewer than ``min_periods`` valid observations emit NaN.
    """
    arr = np.asarray(arr, dtype=float)
    if arr.ndim == 1:
        n = arr.shape[0]
        finite = np.isfinite(arr)
        safe = np.where(finite, arr, 0.0)
        ones = np.where(finite, 1.0, 0.0)
        csum = np.concatenate(([0.0], np.cumsum(safe)))
        cones = np.concatenate(([0.0], np.cumsum(ones)))
        idx = np.arange(n)
        starts = np.maximum(0, idx - window + 1)
        ends = idx + 1
        sums = csum[ends] - csum[starts]
        counts = cones[ends] - cones[starts]
        too_short = counts < min_periods
        sums = np.where(too_short, np.nan, sums)
        return sums, counts
    n, k = arr.shape[0], arr.shape[1]
    finite = np.isfinite(arr)
    safe = np.where(finite, arr, 0.0)
    ones = np.where(finite, 1.0, 0.0)
    csum = np.concatenate((np.zeros((1, k)), np.cumsum(safe, axis=0)), axis=0)
    cones = np.concatenate((np.zeros((1, k)), np.cumsum(ones, axis=0)), axis=0)
    idx = np.arange(n)
    starts = np.maximum(0, idx - window + 1)
    ends = idx + 1
    sums = csum[ends] - csum[starts]
    counts = cones[ends] - cones[starts]
    too_short = counts < min_periods
    sums = np.where(too_short, np.nan, sums)
    return sums, counts


def _rolling_sum_finite(arr, window, min_periods):
    """Rolling window sum for an **all-finite** array (1-D or 2-D).

    Semantically identical to :func:`_rolling_sum` on all-finite input, but
    skips the ``isfinite``/``where``/``ones`` masks and the ``cones`` cumulative
    sum. Because every entry is finite, the per-window valid count is simply
    ``min(i + 1, window)`` and is identical across columns, so ``counts`` is
    returned as a 1-D array. Callers must guarantee finiteness (the rolling
    fast path only routes finite asset columns here); otherwise the NaN
    propagation semantics of ``_rolling_sum`` are lost.
    """
    arr = np.asarray(arr, dtype=float)
    idx = np.arange(arr.shape[0])
    starts = np.maximum(0, idx - window + 1)
    ends = idx + 1
    if arr.ndim == 1:
        csum = np.concatenate(([0.0], np.cumsum(arr)))
        sums = csum[ends] - csum[starts]
    else:
        n, k = arr.shape
        csum = np.empty((n + 1, k), dtype=float)
        csum[0] = 0.0
        np.cumsum(arr, axis=0, out=csum[1:])
        sums = csum[ends] - csum[starts]
    counts = np.minimum(idx + 1, window).astype(np.int64)
    too_short = counts < min_periods
    if arr.ndim == 1:
        sums = np.where(too_short, np.nan, sums)
    else:
        sums = np.where(too_short[:, None], np.nan, sums)
    return sums, counts


def calculate_rolling_beta(returns_df, benchmark_name, window=90, min_obs=60):
    """Calculate rolling beta for all assets vs benchmark."""
    if returns_df is None:
        raise BABDataError("returns_df is None")
    if not isinstance(returns_df, pd.DataFrame):
        raise BABDataError(f"Expected DataFrame, got {type(returns_df).__name__}")
    if benchmark_name not in returns_df.columns:
        raise BABDataError(f"Benchmark {benchmark_name} not found in returns")

    benchmark_returns = returns_df[benchmark_name]
    try:
        bench_vals = benchmark_returns.to_numpy(dtype=float)
    except Exception:
        try:
            bench_vals = np.asarray(benchmark_returns, dtype=float)
        except Exception as e:
            raise BABDataError(str(e))
    if not np.isfinite(bench_vals).any():
        raise BABDataError(
            f"Benchmark '{benchmark_name}' has no finite return values; "
            "cannot estimate betas against it"
        )

    n = len(returns_df)
    betas_dict = {}

    bench_arr = bench_vals
    b_has_bad = not np.all(np.isfinite(bench_arr))

    # Benchmark rolling sums are asset-independent; hoist them out so every
    # asset reuses the same cnt / x_sum / xx_sum instead of recomputing them.
    # CRITICAL: ``ones`` is the benchmark's *finite* mask, not a constant 1.0.
    # pandas rolling .sum() skips NaN, so x_sum / xx_sum already sum only the
    # finite benchmark observations per window. ``cnt`` MUST match that: it is
    # the number of valid benchmark observations in each window, used both for
    # the OLS denominator (cnt*xx - x^2) and the min_obs gate. Counting window
    # length instead would let a single NaN in the benchmark inflate ``cnt``,
    # loosen the min_obs gate, and corrupt the shared denominator -- producing
    # a finite beta from one valid observation in an otherwise-NaN window.
    if b_has_bad:
        x_sum_f, cnt_f = _rolling_sum(bench_arr, window, min_obs)
        xx_sum_f, _ = _rolling_sum(bench_arr * bench_arr, window, min_obs)
    else:
        x_sum_f, cnt_f = _rolling_sum_finite(bench_arr, window, min_obs)
        xx_sum_f, _ = _rolling_sum_finite(bench_arr * bench_arr, window, min_obs)
    # Shared denominator component across all assets: cnt*xx - x^2, shape (n, 1).
    denom_shared = cnt_f[:, None] * xx_sum_f[:, None] - x_sum_f[:, None] * x_sum_f[:, None]
    obs_short = (cnt_f < min_obs) | np.isnan(cnt_f)  # shape (n,)

    def _finalize_betas(beta_arr):
        """Apply degenerate / insufficient-observation masks to a (n,) beta array."""
        beta_arr = np.asarray(beta_arr, dtype=float).copy()
        # Degeneracy is PER-ROW (per-window), derived from the shared denominator
        # cnt*xx - x^2. It is zero exactly when the benchmark has zero variance
        # within that window. A whole-series np.std(bench_arr) check would
        # collapse the entire beta series to NaN on any benchmark NaN, which is
        # undefined-beta poisoning rather than undefined beta -- it silently
        # flattens real signals in windows with plenty of valid observations.
        degenerate = (~np.isfinite(denom_shared)) | (np.abs(denom_shared) < 1e-12)
        if beta_arr.ndim == 1:
            beta_arr = np.where(degenerate.ravel(), np.nan, beta_arr)
            beta_arr = np.where(~np.isfinite(beta_arr), np.nan, beta_arr)
            beta_arr = np.where(obs_short, np.nan, beta_arr)
            return beta_arr
        else:
            deg = degenerate.reshape(-1)
            beta_arr = np.where(deg[:, None], np.nan, beta_arr)
            beta_arr = np.where(~np.isfinite(beta_arr), np.nan, beta_arr)
            beta_arr = np.where(obs_short[:, None], np.nan, beta_arr)
            return beta_arr

    asset_cols = [c for c in returns_df.columns if c != benchmark_name]

    try:
        # Fast path: all-finite assets are computed at once from a single 2-D
        # conversion plus lean (mask-free) cumulative-sum rolling windows. This
        # removes the per-asset Python loop and the redundant pandas
        # DataFrame/mul/to_numpy round-trips. Assets that contain any
        # non-finite value fall back to the per-series safe path.
        finite_cols = []
        bad_cols = []
        for c in asset_cols:
            try:
                a_arr = returns_df[c].to_numpy(dtype=float, copy=False)
            except Exception:
                try:
                    a_arr = np.asarray(returns_df[c], dtype=float)
                except Exception:
                    bad_cols.append(c)
                    continue
            (finite_cols if np.all(np.isfinite(a_arr)) else bad_cols).append(c)

        # The vectorized finite path derives the OLS y-sum over *all* asset
        # observations, but the benchmark-derived cnt/x-sum/xy-sum only cover
        # the finite-benchmark observations. When the benchmark itself has
        # non-finite entries those sets differ, so the paired y-sum would be
        # inflated and betas wrong. In that case fall back to the per-series
        # path, which masks on the *pairwise* finite mask (benchmark & asset)
        # and therefore matches the naive per-window OLS oracle exactly.
        if b_has_bad:
            bad_cols = list(asset_cols)
            finite_cols = []

        asset_betas = {}

        if finite_cols:
            # All columns here are finite (b_has_bad was handled above), so a
            # single 2-D conversion and mask-free rolling sums are exact.
            y_arr = returns_df[finite_cols].to_numpy(dtype=float)
            xy_arr = y_arr * bench_arr[:, None]
            y_sum_f, _ = _rolling_sum_finite(y_arr, window, min_obs)
            xy_sum_f, _ = _rolling_sum_finite(xy_arr, window, min_obs)
            num = cnt_f[:, None] * xy_sum_f - x_sum_f[:, None] * y_sum_f
            with np.errstate(invalid="ignore", divide="ignore"):
                beta = _finalize_betas(num / denom_shared)
            for j, c in enumerate(finite_cols):
                asset_betas[c] = beta[:, j]

        for c in bad_cols:
            try:
                a_arr = returns_df[c].to_numpy(dtype=float, copy=False)
            except Exception:
                try:
                    a_arr = np.asarray(returns_df[c], dtype=float)
                except Exception as e:
                    raise BABDataError(str(e))
            asset_betas[c] = _calc_rolling_beta_series(bench_arr, a_arr, window, min_obs)

        # Re-emit columns in the original frame order (benchmark keeps its
        # position) so positional comparisons against the slow reference line up.
        betas_dict = {}
        for c in returns_df.columns:
            if c == benchmark_name:
                betas_dict[c] = np.ones(n, dtype=float)
            else:
                betas_dict[c] = asset_betas[c]
        return pd.DataFrame(betas_dict, index=returns_df.index)
    except BABDataError:
        raise
    except (TypeError, ValueError, AttributeError):
        betas_dict = {}
        for asset in returns_df.columns:
            if asset == benchmark_name:
                betas_dict[asset] = np.ones(n, dtype=float)
                continue
            try:
                a_arr = returns_df[asset].to_numpy(dtype=float, copy=False)
            except Exception:
                try:
                    a_arr = np.asarray(returns_df[asset], dtype=float)
                except Exception as e:
                    raise BABDataError(str(e))
            betas_dict[asset] = _calc_rolling_beta_series(bench_arr, a_arr, window, min_obs)
        return pd.DataFrame(betas_dict, index=returns_df.index)
