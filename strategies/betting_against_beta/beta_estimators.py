"""Beta estimators for the Betting Against Beta strategy.

Estimator families beyond the shipped rolling OLS: exponentially-weighted
moving average (EWMA) beta and shrinkage (James-Stein / Bayesian) beta.

All estimators share a common contract:

* Input: asset x date ``DataFrame`` of returns including a benchmark column.
* Output: ``DataFrame`` with the same columns and index; the benchmark
  column is always ``1.0``; asset columns hold the per-row beta estimate.
* Causal: row ``t`` uses only data at or before ``t`` (no lookahead).
* NaN before ``min_obs``: rows with fewer than ``min_obs`` usable observations
  are ``NaN``.
* Deterministic: no randomness, no dependence on execution order.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .beta import calculate_rolling_beta


def _validate_returns_frame(returns_df, benchmark):
    if returns_df is None:
        raise ValueError("returns_df must not be None")
    if not isinstance(returns_df, pd.DataFrame):
        raise ValueError(f"Expected DataFrame, got {type(returns_df).__name__}")
    if benchmark not in returns_df.columns:
        raise ValueError(f"Benchmark '{benchmark}' not found in returns")


def _out_frame(returns_df, benchmark):
    out = pd.DataFrame(
        np.nan, index=returns_df.index, columns=returns_df.columns, dtype=float
    )
    out[benchmark] = 1.0
    return out


def estimate_rolling_ols_beta(returns_df, benchmark, window=90, min_obs=60):
    """Rolling-OLS beta; thin parity wrapper over ``calculate_rolling_beta``."""
    _validate_returns_frame(returns_df, benchmark)
    if window is None or window < 1:
        raise ValueError("window must be >= 1")
    if min_obs is None:
        min_obs = 60
    if len(returns_df) == 0:
        return _out_frame(returns_df, benchmark)
    return calculate_rolling_beta(returns_df, benchmark, window=int(window), min_obs=int(min_obs))


def estimate_ewma_beta(returns_df, benchmark, halflife=40, min_obs=60):
    """Exponentially-weighted covariance/variance beta, causal, no lookahead.

    beta(t) = EwmaCov(r_asset, r_bench)(t) / EwmaVar(r_bench)(t), computed with
    the recursive adjust=False EWMA so row ``t`` depends only on data <= t.
    """
    _validate_returns_frame(returns_df, benchmark)
    if halflife is None or not np.isfinite(float(halflife)) or float(halflife) <= 0:
        raise ValueError("halflife must be a positive finite number")
    if min_obs is None:
        min_obs = 60
    halflife = float(halflife)
    min_obs = int(min_obs)

    asset_cols = [c for c in returns_df.columns if c != benchmark]
    out = _out_frame(returns_df, benchmark)
    bench = returns_df[benchmark].astype(float)

    for c in asset_cols:
        a = returns_df[c].astype(float)
        pair_finite = a.notna() & bench.notna()
        obs_count = pair_finite.astype(float).cumsum()

        mean_a = a.ewm(halflife=halflife, min_periods=min_obs, adjust=False).mean()
        mean_b = bench.ewm(halflife=halflife, min_periods=min_obs, adjust=False).mean()
        e_ab = (a * bench).ewm(halflife=halflife, min_periods=min_obs, adjust=False).mean()
        e_b2 = (bench * bench).ewm(halflife=halflife, min_periods=min_obs, adjust=False).mean()

        cov = e_ab - mean_a * mean_b
        var = e_b2 - mean_b * mean_b
        beta = cov / var
        beta = beta.where(var > 1e-18, np.nan)
        beta = beta.where(obs_count >= min_obs, np.nan)
        out[c] = beta.reindex(returns_df.index)

    return out


def estimate_shrinkage_beta(
    returns_df,
    benchmark,
    window=90,
    shrink_target=1.0,
    shrink_intensity=0.0,
    min_obs=60,
):
    """Rolling-OLS beta shrunk toward ``shrink_target``.

    beta_shrink(t) = (1 - intensity) * beta_ols(t) + intensity * target(t).

    intensity == 0 returns the OLS baseline exactly; intensity in [0, 1].
    ``shrink_target`` may be a finite float (default 1.0) or the string
    ``"cross_sectional_mean"`` for the per-row cross-sectional mean of OLS betas.
    """
    _validate_returns_frame(returns_df, benchmark)
    if window is None or window < 1:
        raise ValueError("window must be >= 1")
    intensity = float(shrink_intensity)
    if not np.isfinite(intensity) or not 0.0 <= intensity <= 1.0:
        raise ValueError("shrink_intensity must be in [0, 1]")
    if min_obs is None:
        min_obs = 60
    min_obs = int(min_obs)

    ols = estimate_rolling_ols_beta(returns_df, benchmark, window=window, min_obs=min_obs)
    if intensity == 0.0:
        return ols

    asset_cols = [c for c in returns_df.columns if c != benchmark]
    out = _out_frame(returns_df, benchmark)

    if shrink_target == "cross_sectional_mean":
        target = ols[asset_cols].mean(axis=1)
    else:
        target_value = float(shrink_target)
        if not np.isfinite(target_value):
            raise ValueError("shrink_target must be finite or 'cross_sectional_mean'")
        target = pd.Series(target_value, index=returns_df.index)

    for c in asset_cols:
        out[c] = (1.0 - intensity) * ols[c] + intensity * target.reindex(returns_df.index)

    return out
