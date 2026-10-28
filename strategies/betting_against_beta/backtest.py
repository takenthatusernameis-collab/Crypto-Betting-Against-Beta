"""Backtesting for BAB strategy."""

import numpy as np
import pandas as pd


def run_backtest(returns_df, weights_df, transaction_costs=0.0, slippage=0.0,
                 tc=None, slippage_cost=None):
    """Run simple backtest."""
    # Allow alternative parameter names for flexibility
    if tc is not None and transaction_costs == 0.0:
        transaction_costs = tc
    if slippage_cost is not None and slippage == 0.0:
        slippage = slippage_cost

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
    # Align columns where possible
    common_cols = returns.columns.intersection(weights.columns)
    if len(common_cols) == 0:
        # Try to proceed if structures match
        pass
    else:
        returns = returns[common_cols]
        weights = weights[common_cols]

    # Calculate portfolio returns (shift weights by 1 day for no lookahead)
    portfolio_returns = (weights.shift(1) * returns).sum(axis=1)

    # Compute turnover symmetrically once
    weight_changes = weights.diff().abs().sum(axis=1).fillna(0.0)

    # Apply transaction costs if any
    tc_val = float(transaction_costs) if transaction_costs is not None else 0.0
    if tc_val != 0.0:  # apply even if small negative? but spec says fraction; be defensive
        if tc_val > 0:
            costs = weight_changes * tc_val
            portfolio_returns = portfolio_returns - costs

    # Apply slippage cost on turnover if any
    slip_val = float(slippage) if slippage is not None else 0.0
    if slip_val != 0.0:
        if slip_val > 0:
            slippage_costs = weight_changes * slip_val
            portfolio_returns = portfolio_returns - slippage_costs

    # Calculate cumulative returns in log space to avoid overflow/underflow
    portfolio_returns_filled = portfolio_returns.fillna(0).clip(lower=-1.0 + 1e-12)
    log_returns = np.log1p(portfolio_returns_filled)
    cumulative_returns = np.exp(np.cumsum(log_returns.to_numpy()))

    results = pd.DataFrame({
        'returns': portfolio_returns,
        'cumulative': cumulative_returns
    }, index=common_idx)

    return results
