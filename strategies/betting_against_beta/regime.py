"""Regime detection for Betting Against Beta strategy."""

from __future__ import annotations

from typing import Optional, Union

import numpy as np
import pandas as pd


def calculate_realized_volatility(returns: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Calculate realized volatility (annualized or raw) over rolling window."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    if window < 1:
        raise ValueError("window must be >= 1")
    vol = returns.rolling(window=window, min_periods=max(1, window // 2)).std()
    return vol


def classify_volatility_regimes(
    returns: pd.DataFrame,
    vol_window: int = 20,
    thresholds: Optional[list] = None,
) -> pd.DataFrame:
    """Classify volatility regimes using fixed thresholds."""
    if thresholds is None:
        thresholds = [0.01, 0.02]
    vol = calculate_realized_volatility(returns, window=vol_window)
    # Create regime labels (0=low, 1=medium, 2=high)
    regimes = pd.DataFrame(index=vol.index, columns=vol.columns, dtype=float)
    for col in vol.columns:
        v = vol[col]
        regimes[col] = 0
        # medium if above first threshold
        regimes.loc[v > thresholds[0], col] = 1
        if len(thresholds) > 1:
            regimes.loc[v > thresholds[1], col] = 2
    regimes = regimes.fillna(0)
    return regimes


def classify_volatility_regimes_percentile(
    returns: pd.DataFrame,
    vol_window: int = 20,
    quantiles: Optional[list] = None,
) -> pd.DataFrame:
    """Classify volatility regimes using rolling percentiles."""
    if quantiles is None:
        quantiles = [0.33, 0.67]
    vol = calculate_realized_volatility(returns, window=vol_window)
    regimes = pd.DataFrame(index=vol.index, columns=vol.columns, dtype=float)
    for col in vol.columns:
        v = vol[col]
        regimes[col] = 1  # medium by default
        # Compute expanding/rolling percentiles
        qlow = v.rolling(window=max(vol_window * 2, 50), min_periods=vol_window).quantile(quantiles[0])
        qhigh = v.rolling(window=max(vol_window * 2, 50), min_periods=vol_window).quantile(quantiles[1])
        regimes.loc[v <= qlow, col] = 0  # low
        regimes.loc[v >= qhigh, col] = 2  # high
    regimes = regimes.fillna(1)
    return regimes


def classify_trend_regime(returns: pd.DataFrame, ma_window: int = 20) -> pd.DataFrame:
    """Classify trend regime using moving average."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    # Use cumulative returns or price proxy
    cumret = (1 + returns.fillna(0)).cumprod()
    ma = cumret.rolling(window=ma_window, min_periods=max(1, ma_window // 2)).mean()
    trend = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    trend = ((cumret > ma).astype(float) * 1.0)  # 1 = uptrend
    trend = trend.fillna(0)
    return trend


def mean_reversion_zscore(returns: pd.DataFrame, window: int = 30, z_threshold: float = 1.5) -> pd.DataFrame:
    """Generate mean reversion signals based on z-score."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    roll_mean = returns.rolling(window=window, min_periods=max(1, window // 2)).mean()
    roll_std = returns.rolling(window=window, min_periods=max(1, window // 2)).std()
    zscore = (returns - roll_mean) / (roll_std.replace(0, np.nan))
    signals = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    signals[zscore < -z_threshold] = 1.0  # oversold -> long
    signals[zscore > z_threshold] = -1.0  # overbought -> short
    signals = signals.fillna(0)
    return signals


def get_regime_state(returns: pd.DataFrame, vol_window: int = 20, ma_window: int = 50) -> pd.DataFrame:
    """Get combined regime state aligned to returns index."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    vol_regimes = classify_volatility_regimes_percentile(returns, vol_window=vol_window)
    trend_regimes = classify_trend_regime(returns, ma_window=ma_window)
    # Combine states (simple combination)
    state = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    state = vol_regimes * 0.5 + trend_regimes * 0.5  # combine
    state = state.fillna(1.0)  # neutral default
    return state


def apply_regime_scaling(
    signals: pd.DataFrame,
    returns: Optional[pd.DataFrame] = None,
    scale_low_vol: float = 1.0,
    scale_medium_vol: float = 1.0,
    scale_high_vol: float = 0.5,
) -> pd.DataFrame:
    """Apply regime-based position scaling."""
    if not isinstance(signals, pd.DataFrame):
        raise TypeError("signals must be a DataFrame")
    scaled = signals.copy()
    if returns is not None:
        try:
            vol_regimes = classify_volatility_regimes_percentile(returns)
            for col in scaled.columns:
                if col in vol_regimes.columns:
                    scaled.loc[vol_regimes[col] == 2, col] *= scale_high_vol  # high vol
                    scaled.loc[vol_regimes[col] == 0, col] *= scale_low_vol  # low vol
        except Exception:
            pass  # fail gracefully
    return scaled
