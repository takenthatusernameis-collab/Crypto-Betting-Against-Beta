"""Beta calculation for BAB strategy."""

import numpy as np
import pandas as pd

from .data_loader import BABDataError


def calculate_beta(asset_returns, benchmark_returns, min_obs=None):
    """Calculate beta of asset vs benchmark using OLS regression."""
    try:
        # Align and drop NaN
        aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
        if len(aligned) == 0:
            return np.nan
        if min_obs is not None and len(aligned) < min_obs:
            return np.nan

        y = aligned.iloc[:, 0].values
        x = aligned.iloc[:, 1].values

        # Add intercept
        X = np.column_stack([np.ones(len(x)), x])
        try:
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
            beta = coeffs[1]
            if beta is None or (isinstance(beta, float) and (np.isnan(beta) or np.isinf(beta))):
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
    if not np.isfinite(benchmark_returns.to_numpy()).any():
        raise BABDataError(
            f"Benchmark '{benchmark_name}' has no finite return values; "
            "cannot estimate betas against it"
        )

    betas = {}

    for asset in returns_df.columns:
        if asset == benchmark_name:
            betas[asset] = 1.0  # beta of benchmark vs itself
            continue
        rolling_betas = []
        for i in range(len(returns_df)):
            if i < min_obs:
                rolling_betas.append(np.nan)
                continue
            start_idx = max(0, i - window + 1)
            end_idx = i + 1
            try:
                window_asset = returns_df[asset].iloc[start_idx:end_idx]
                window_bench = benchmark_returns.iloc[start_idx:end_idx]
                beta = calculate_beta(window_asset, window_bench, min_obs=min_obs)
                # Degenerate cases -> NaN cleanly
                if beta is None or (isinstance(beta, float) and (np.isnan(beta) or np.isinf(beta))):
                    rolling_betas.append(np.nan)
                else:
                    rolling_betas.append(beta)
            except Exception:
                rolling_betas.append(np.nan)
        betas[asset] = rolling_betas

    return pd.DataFrame(betas, index=returns_df.index)
