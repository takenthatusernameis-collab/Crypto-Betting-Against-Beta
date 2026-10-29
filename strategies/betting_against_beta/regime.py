"""Regime detection for Betting Against Beta strategy."""

from __future__ import annotations

from typing import Optional, Union

import numpy as np
import pandas as pd


def calculate_realized_volatility(returns: pd.DataFrame, window: int = 20, use_ewma: bool = False) -> pd.DataFrame:
    """Calculate realized volatility (raw or EWMA) over rolling window."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    if window < 1:
        raise ValueError("window must be >= 1")
    if use_ewma:
        vol = returns.ewm(span=window, min_periods=max(1, window // 2), adjust=False).std()
    else:
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
        # Apply high first so that degenerate bands (qlow == qhigh, e.g. constant
        # zero vol) resolve to the low regime rather than the high regime.
        regimes.loc[v >= qhigh, col] = 2  # high
        regimes.loc[v <= qlow, col] = 0   # low wins ties
    regimes = regimes.fillna(1)
    return regimes


def classify_trend_regime(returns: pd.DataFrame, ma_window: int = 20, z_window: Optional[int] = None) -> pd.DataFrame:
    """Classify trend regime using a moving average or a z-score.

    When ``z_window`` is set, the regime is uptrend (1) where the z-score of
    returns over the z-score window is positive, else downtrend (0).  Otherwise
    the regime is uptrend (1) where cumulative returns exceed their moving
    average, else downtrend (0).  All values are causal (no lookahead).
    """
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    if z_window is not None and int(z_window) >= 1:
        z_win = int(z_window)
        roll_mean = returns.rolling(window=z_win, min_periods=max(1, z_win // 2)).mean()
        roll_std = returns.rolling(window=z_win, min_periods=max(1, z_win // 2)).std()
        zscore = (returns - roll_mean) / (roll_std.replace(0, np.nan))
        trend = (zscore > 0).astype(float)
    else:
        cumret = (1 + returns.fillna(0)).cumprod()
        ma = cumret.rolling(window=ma_window, min_periods=max(1, ma_window // 2)).mean()
        trend = ((cumret > ma).astype(float) * 1.0)
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


def _apply_vol_hysteresis(
    vol: pd.DataFrame,
    regimes: pd.DataFrame,
    low_thr,
    high_thr,
    hysteresis: float,
) -> pd.DataFrame:
    """Apply causal hysteresis so regime flips require crossing a margin.

    ``low_thr``/``high_thr`` may be scalars or DataFrames (time-varying bands,
    e.g. rolling percentiles).  The state machine only uses data up to the
    current row, so it introduces no lookahead.
    """
    if hysteresis <= 0:
        return regimes
    out = regimes.copy()
    for col in out.columns:
        v = vol[col]
        r = out[col]
        lt = low_thr[col] if isinstance(low_thr, pd.DataFrame) else low_thr
        ht = high_thr[col] if isinstance(high_thr, pd.DataFrame) else high_thr
        prev = None
        for i in range(len(r)):
            vi = v.iloc[i]
            if not np.isfinite(vi):
                if prev is not None:
                    r.iloc[i] = prev
                continue
            lti = lt.iloc[i] if hasattr(lt, "iloc") else lt
            hti = ht.iloc[i] if hasattr(ht, "iloc") else ht
            if not np.isfinite(lti) or not np.isfinite(hti):
                if prev is not None:
                    r.iloc[i] = prev
                continue
            if prev is None:
                prev = int(r.iloc[i]) if np.isfinite(r.iloc[i]) else 1
            elif prev == 2:
                if vi < hti - hysteresis * max(hti - lti, 0.0):
                    prev = 0 if vi < lti - hysteresis * max(hti - lti, 0.0) else 1
            elif prev == 0:
                if vi > lti + hysteresis * max(hti - lti, 0.0):
                    prev = 2 if vi > hti + hysteresis * max(hti - lti, 0.0) else 1
            else:
                if vi > hti + hysteresis * max(hti - lti, 0.0):
                    prev = 2
                elif vi < lti - hysteresis * max(hti - lti, 0.0):
                    prev = 0
            r.iloc[i] = prev
        out[col] = r
    return out


def regime_scale_factors(returns: pd.DataFrame, cfg) -> pd.DataFrame:
    """Return per-column regime scale factors aligned to ``returns``.

    The benchmark column is excluded (it is not traded).  Every factor is
    causal: it uses only data up to and including that date, so applying it to
    weights at date ``t`` introduces no lookahead.  Output is neutral (1.0)
    wherever the regime cannot be determined.

    Regime -> scale mapping (default scale_high=0.5, scale_low=1.0):
      * vol: low-vol regime -> scale_low, medium -> 1.0, high-vol -> scale_high
      * trend: uptrend -> scale_low, downtrend -> scale_high
      * combined: element-wise minimum (most conservative) of vol and trend
    """
    import pandas as pd

    if not isinstance(returns, pd.DataFrame) or returns.empty:
        return pd.DataFrame()

    benchmark = getattr(cfg, "benchmark", None)
    universe = [c for c in returns.columns if c != benchmark]
    if not universe:
        universe = list(returns.columns)

    method = str(getattr(cfg, "regime_method", "vol") or "vol")
    if method not in ("vol", "trend", "combined"):
        method = "vol"
    vol_window = int(getattr(cfg, "vol_window", 20) or 20)
    vol_use_ewma = bool(getattr(cfg, "vol_use_ewma", False))
    vol_hysteresis = float(getattr(cfg, "vol_hysteresis", 0.0) or 0.0)
    vol_thresholds = getattr(cfg, "vol_thresholds", None)
    vol_percentiles = getattr(cfg, "vol_percentiles", None)
    if vol_percentiles is None:
        vol_percentiles = (0.33, 0.66)
    trend_ma_window = int(getattr(cfg, "trend_ma_window", 50) or 50)
    trend_z_window = getattr(cfg, "trend_z_window", None)
    scale_high = float(getattr(cfg, "regime_scale_high", 0.5) or 0.5)
    scale_low = float(getattr(cfg, "regime_scale_low", 1.0) or 1.0)

    sub = returns[universe]
    vol = calculate_realized_volatility(sub, window=vol_window, use_ewma=vol_use_ewma)

    scale = pd.DataFrame(1.0, index=returns.index, columns=universe, dtype=float)

    vol_regime = None
    low_thr = high_thr = None
    if method in ("vol", "combined"):
        if vol_thresholds is not None and len(vol_thresholds) >= 1:
            thr = [float(t) for t in vol_thresholds]
            low_thr = thr[0]
            high_thr = thr[1] if len(thr) >= 2 else thr[0]
            vol_regime = classify_volatility_regimes(sub, vol_window=vol_window, thresholds=thr)
        else:
            qlow, qhigh = float(vol_percentiles[0]), float(vol_percentiles[1])
            low_thr = vol.rolling(window=max(vol_window * 2, 50), min_periods=vol_window).quantile(qlow)
            high_thr = vol.rolling(window=max(vol_window * 2, 50), min_periods=vol_window).quantile(qhigh)
            vol_regime = classify_volatility_regimes_percentile(
                sub, vol_window=vol_window, quantiles=[qlow, qhigh]
            )
        if vol_hysteresis > 0:
            vol_regime = _apply_vol_hysteresis(vol, vol_regime, low_thr, high_thr, vol_hysteresis)

    trend_regime = None
    if method in ("trend", "combined"):
        trend_regime = classify_trend_regime(sub, ma_window=trend_ma_window, z_window=trend_z_window)

    vol_scale = pd.DataFrame(1.0, index=returns.index, columns=universe, dtype=float)
    trend_scale = pd.DataFrame(1.0, index=returns.index, columns=universe, dtype=float)

    if vol_regime is not None:
        for col in universe:
            if col in vol_regime.columns:
                vol_scale[col] = vol_regime[col].map({0: scale_low, 1: 1.0, 2: scale_high}).fillna(1.0)
    if trend_regime is not None:
        for col in universe:
            if col in trend_regime.columns:
                trend_scale[col] = trend_regime[col].map({1: scale_low, 0: scale_high}).fillna(1.0)

    if method == "vol":
        combined = vol_scale
    elif method == "trend":
        combined = trend_scale
    else:
        import numpy as _np

        combined = vol_scale.copy()
        for col in universe:
            combined[col] = _np.minimum(vol_scale[col].to_numpy(), trend_scale[col].to_numpy())

    return combined.fillna(1.0)
