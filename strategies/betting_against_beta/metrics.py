"""Performance metrics for BAB strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sharpe_ratio(returns, risk_free: float = 0.0, periods_per_year: int = 252):
    """Calculate annualized Sharpe ratio."""
    if returns is None:
        return np.nan
    r = pd.Series(returns).dropna()
    if len(r) == 0:
        return np.nan
    excess = r - risk_free / periods_per_year
    mean_excess = excess.mean()
    std_excess = excess.std(ddof=1)
    if std_excess == 0 or np.isnan(std_excess) or std_excess < 1e-18:
        if abs(mean_excess) < 1e-18:
            return np.nan
        elif mean_excess > 0:
            return np.inf
        else:
            return -np.inf
    return float((mean_excess / std_excess) * np.sqrt(periods_per_year))


def max_drawdown(cumulative_or_returns):
    """Calculate maximum drawdown."""
    if cumulative_or_returns is None:
        return np.nan
    s = pd.Series(cumulative_or_returns).dropna()
    if len(s) == 0:
        return np.nan
    if s.iloc[0] > 0.5 and s.iloc[0] < 5 and all(x >= 0 for x in s.iloc[:min(5, len(s))]):
        cumulative = s
    else:
        cumulative = (1 + s).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()
    return float(max_dd) if not pd.isna(max_dd) else np.nan


def annualized_volatility(returns, periods_per_year: int = 252):
    """Calculate annualized volatility."""
    if returns is None:
        return np.nan
    r = pd.Series(returns).dropna()
    if len(r) == 0:
        return np.nan
    vol = r.std(ddof=1) * np.sqrt(periods_per_year)
    if vol < 1e-18 or np.isnan(vol):
        return 0.0
    return float(vol)


def turnover(weights_df):
    """Calculate mean turnover."""
    if weights_df is None or len(weights_df) == 0:
        return np.nan
    w = weights_df.copy()
    weight_changes = w.diff().abs().sum(axis=1)
    turnover_mean = weight_changes.dropna().mean()
    if pd.isna(turnover_mean):
        return 0.0
    return float(turnover_mean)


def strategy_beta(strategy_returns, benchmark_returns, periods_per_year: int = 252):
    """Calculate OLS beta of strategy vs benchmark."""
    if strategy_returns is None or benchmark_returns is None:
        return np.nan
    strat = pd.Series(strategy_returns)
    bench = pd.Series(benchmark_returns)
    df = pd.DataFrame({'strat': strat, 'bench': bench}).dropna()
    if len(df) < 2:
        return np.nan
    cov = df['strat'].cov(df['bench'])
    var_bench = df['bench'].var(ddof=1)
    if var_bench == 0 or np.isnan(var_bench):
        return np.nan
    beta = cov / var_bench
    return float(beta)


def summary(returns, weights_df=None, benchmark_returns=None, risk_free: float = 0.0, periods_per_year: int = 252):
    """Generate summary of all metrics."""
    result = {}
    r = pd.Series(returns) if returns is not None else pd.Series([])

    result['sharpe_ratio'] = sharpe_ratio(r, risk_free=risk_free, periods_per_year=periods_per_year)
    result['annualized_volatility'] = annualized_volatility(r, periods_per_year=periods_per_year)
    result['max_drawdown'] = max_drawdown(r)

    if weights_df is not None:
        result['turnover'] = turnover(weights_df)
    else:
        result['turnover'] = np.nan

    if benchmark_returns is not None:
        result['strategy_beta'] = strategy_beta(r, benchmark_returns, periods_per_year=periods_per_year)
    else:
        result['strategy_beta'] = np.nan

    if len(r.dropna()) > 0:
        cum = (1 + r.fillna(0)).cumprod()
        result['total_return'] = float(cum.iloc[-1] - 1)
        result['final_cumulative'] = float(cum.iloc[-1])
    else:
        result['total_return'] = np.nan
        result['final_cumulative'] = np.nan

    return result
