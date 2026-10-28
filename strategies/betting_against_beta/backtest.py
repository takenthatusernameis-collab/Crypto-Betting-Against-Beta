"""Backtesting for BAB strategy."""

import numpy as np
import pandas as pd


def run_backtest(returns_df, weights_df, transaction_costs=0.0, slippage=0.0):
    """Run simple backtest."""
    if returns_df is None or weights_df is None:
        return pd.DataFrame(columns=["returns", "cumulative"])

    if not isinstance(returns_df, pd.DataFrame) or not isinstance(weights_df, pd.DataFrame):
        try:
            returns_df = pd.DataFrame(returns_df)
        except Exception:
            pass
        try:
            weights_df = pd.DataFrame(weights_df)
        except Exception:
            pass

    if returns_df.empty or weights_df.empty:
        common_idx = returns_df.index.intersection(weights_df.index)
        results = pd.DataFrame({"returns": [], "cumulative": []}, index=common_idx)
        return results

    # Align indices
    common_idx = returns_df.index.intersection(weights_df.index)
    returns = returns_df.loc[common_idx]
    weights = weights_df.loc[common_idx]

    # Calculate portfolio returns (shift weights by 1 day for no lookahead)
    portfolio_returns = (weights.shift(1) * returns).sum(axis=1)

    # Apply transaction costs if any
    if transaction_costs and float(transaction_costs) > 0:
        weight_changes = weights.diff().abs().sum(axis=1)
        costs = weight_changes * float(transaction_costs)
        portfolio_returns = portfolio_returns - costs

    # Apply slippage cost on turnover if any
    if slippage and float(slippage) > 0:
        weight_changes = weights.diff().abs().sum(axis=1)
        slippage_costs = weight_changes * float(slippage)
        portfolio_returns = portfolio_returns - slippage_costs

    # Calculate cumulative returns in log space to avoid overflow/underflow
    # on real-market data with large multi-day moves. exp(cumsum(log(1+r)))
    # is mathematically identical to cumprod(1+r) but numerically stable.
    # Clip at -1 + epsilon so log1p cannot hit its singularity (a -100%
    # single-day return wipes the portfolio to zero; that is the floor).
    portfolio_returns_filled = portfolio_returns.fillna(0).clip(lower=-1.0 + 1e-12)
    log_returns = np.log1p(portfolio_returns_filled)
    cumulative_returns = np.exp(np.cumsum(log_returns.to_numpy()))

    results = pd.DataFrame({
        'returns': portfolio_returns,
        'cumulative': cumulative_returns
    }, index=common_idx)

    return results
