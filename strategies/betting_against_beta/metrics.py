"""Performance metrics for BAB strategy.

All functions are defensive: they accept None, empty, or single-element inputs
and return ``np.nan`` (or 0.0) rather than raising, so the report path and
downstream callers never crash on degenerate data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Tolerance used when comparing floats to zero; keeps tiny negative vols
# (from floating point error) from being treated as real signal.
EPS = 1e-18


def _to_series(x) -> pd.Series:
    """Coerce arbitrary input to a numeric Series, dropping NaNs."""
    if x is None:
        return pd.Series(dtype="float64")
    if isinstance(x, pd.DataFrame):
        # Collapse a single-column DataFrame to its series.
        if x.shape[1] == 1:
            return pd.Series(x.iloc[:, 0], dtype="float64")
        return pd.Series(np.nan)
    return pd.Series(x, dtype="float64").dropna()


def sharpe_ratio(returns, risk_free: float = 0.0, periods_per_year: int = 252):
    """Calculate annualized Sharpe ratio."""
    r = _to_series(returns)
    if len(r) < 2:
        return np.nan
    periods = max(int(periods_per_year), 1)
    rf_per_period = risk_free / periods
    excess = r - rf_per_period
    mean_excess = excess.mean()
    std_excess = excess.std(ddof=1)
    if std_excess is None or np.isnan(std_excess) or std_excess < EPS:
        if abs(mean_excess) < EPS:
            return np.nan
        return np.inf if mean_excess > 0 else -np.inf
    return float((mean_excess / std_excess) * np.sqrt(periods))


def max_drawdown(cumulative_or_returns):
    """Calculate maximum drawdown (a non-positive fraction).

    Accepts either a cumulative equity path or a returns series; the heuristic
    detects cumulative paths by checking that the first value is near 1.0 and
    the early path is non-negative.
    """
    s = _to_series(cumulative_or_returns)
    if len(s) == 0:
        return np.nan
    first = s.iloc[0]
    looks_cumulative = (
        abs(first - 1.0) < 0.5
        and 0.5 < first < 5.0
        and bool((s.iloc[: min(5, len(s))] >= 0).all())
    )
    if looks_cumulative:
        cumulative = s
    else:
        cumulative = (1.0 + s).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()
    if pd.isna(max_dd):
        return np.nan
    return float(min(max_dd, 0.0))


def annualized_volatility(returns, periods_per_year: int = 252):
    """Calculate annualized volatility."""
    r = _to_series(returns)
    if len(r) < 2:
        return np.nan
    periods = max(int(periods_per_year), 1)
    vol = r.std(ddof=1) * np.sqrt(periods)
    if np.isnan(vol) or vol < EPS:
        return 0.0
    return float(vol)


def turnover(weights_df):
    """Calculate mean one-way turnover from weight changes."""
    if weights_df is None:
        return np.nan
    if not isinstance(weights_df, pd.DataFrame) or weights_df.empty:
        return np.nan
    w = weights_df.astype("float64").copy()
    weight_changes = w.diff().abs().sum(axis=1)
    turnover_mean = weight_changes.dropna().mean()
    if pd.isna(turnover_mean):
        return 0.0
    return float(turnover_mean)


def strategy_beta(strategy_returns, benchmark_returns, periods_per_year: int = 252):
    """Calculate OLS beta of strategy vs benchmark (no annualization needed)."""
    strat = _to_series(strategy_returns)
    bench = _to_series(benchmark_returns)
    df = pd.DataFrame({"strat": strat, "bench": bench}).dropna()
    if len(df) < 2:
        return np.nan
    cov = df["strat"].cov(df["bench"])
    var_bench = df["bench"].var(ddof=1)
    if var_bench is None or np.isnan(var_bench) or var_bench < EPS:
        return np.nan
    beta = cov / var_bench
    if pd.isna(beta):
        return np.nan
    return float(beta)


def total_return(returns):
    """Cumulative total return (fraction) of a returns series."""
    r = _to_series(returns)
    if len(r) == 0:
        return np.nan
    cum = (1.0 + r.fillna(0.0)).cumprod()
    val = cum.iloc[-1] - 1.0
    if pd.isna(val):
        return np.nan
    return float(val)


def final_cumulative(returns):
    """Final cumulative equity value (starting from 1.0)."""
    r = _to_series(returns)
    if len(r) == 0:
        return np.nan
    cum = (1.0 + r.fillna(0.0)).cumprod()
    val = cum.iloc[-1]
    if pd.isna(val):
        return np.nan
    return float(val)


def summary(returns, weights_df=None, benchmark_returns=None, risk_free: float = 0.0, periods_per_year: int = 252):
    """Generate summary of all metrics."""
    result: dict = {}
    r = _to_series(returns)

    result["sharpe_ratio"] = sharpe_ratio(r, risk_free=risk_free, periods_per_year=periods_per_year)
    result["annualized_volatility"] = annualized_volatility(r, periods_per_year=periods_per_year)
    result["max_drawdown"] = max_drawdown(r)
    result["turnover"] = turnover(weights_df) if weights_df is not None else np.nan
    result["strategy_beta"] = (
        strategy_beta(r, benchmark_returns, periods_per_year=periods_per_year)
        if benchmark_returns is not None
        else np.nan
    )
    result["total_return"] = total_return(r)
    result["final_cumulative"] = final_cumulative(r)
    result["n_observations"] = int(len(r))
    return result