"""Backtesting for BAB strategy."""

import numpy as np
import pandas as pd


def run_backtest(returns_df, weights_df, transaction_costs=0.0):
    """Run simple backtest."""
    # Align indices
    common_idx = returns_df.index.intersection(weights_df.index)
    returns = returns_df.loc[common_idx]
    weights = weights_df.loc[common_idx]

    # Calculate portfolio returns (shift weights by 1 day for no lookahead)
    portfolio_returns = (weights.shift(1) * returns).sum(axis=1)

    # Apply transaction costs if any
    if transaction_costs > 0:
        weight_changes = weights.diff().abs().sum(axis=1)
        costs = weight_changes * transaction_costs
        portfolio_returns = portfolio_returns - costs

    # Calculate cumulative returns
    cumulative_returns = (1 + portfolio_returns.fillna(0)).cumprod()

    results = pd.DataFrame({
        'returns': portfolio_returns,
        'cumulative': cumulative_returns
    }, index=common_idx)

    return results
