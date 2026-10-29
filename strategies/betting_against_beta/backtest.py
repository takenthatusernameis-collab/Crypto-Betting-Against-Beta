"""Backtesting for BAB strategy."""

import numpy as np
import pandas as pd

from .costs import TransactionCostModel, compute_transaction_costs


def run_backtest(returns_df, weights_df, transaction_costs=0.0, slippage=0.0,
                 tc=None, slippage_cost=None, cost_model=None,
                 prices_df=None, adv_usd=None):
    """Run simple backtest."""
    # Allow alternative parameter names for flexibility
    if tc is not None and transaction_costs == 0.0:
        transaction_costs = tc
    if slippage_cost is not None and slippage == 0.0:
        slippage = slippage_cost

    if returns_df is None or weights_df is None:
        return pd.DataFrame(columns=["returns", "cumulative"])

    if not isinstance(returns_df, pd.DataFrame):
        try:
            returns_df = pd.DataFrame(returns_df)
        except (TypeError, ValueError):
            return pd.DataFrame(columns=["returns", "cumulative"])
    if not isinstance(weights_df, pd.DataFrame):
        try:
            weights_df = pd.DataFrame(weights_df)
        except (TypeError, ValueError):
            return pd.DataFrame(columns=["returns", "cumulative"])

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
    if len(common_cols) > 0:
        returns = returns[common_cols]
        weights = weights[common_cols]
    else:
        # Try to align by position if same shape
        if returns.shape == weights.shape:
            weights = weights.copy()
            weights.columns = returns.columns
        else:
            pass

    # Clean weights of NaN/inf
    try:
        weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    except (TypeError, ValueError):
        pass

    # Calculate portfolio returns (shift weights by 1 day for no lookahead) - vectorized
    w_shifted = weights.shift(1)
    # Use numpy for efficiency
    try:
        port_ret = (w_shifted.to_numpy(dtype=float) * returns.to_numpy(dtype=float)).sum(axis=1)
        portfolio_returns = pd.Series(port_ret, index=common_idx)
    except Exception:
        portfolio_returns = (w_shifted * returns).sum(axis=1)

    # Compute turnover symmetrically once - vectorized
    try:
        wdiff = weights.to_numpy(dtype=float) - weights.shift(1).fillna(0.0).to_numpy(dtype=float)
        weight_changes = np.abs(wdiff).sum(axis=1)
        weight_changes_s = pd.Series(weight_changes, index=common_idx).fillna(0.0)
    except Exception:
        weight_changes_s = weights.diff().abs().sum(axis=1).fillna(0.0)

    # Apply transaction costs if any
    tc_val = float(transaction_costs) if transaction_costs is not None else 0.0
    if tc_val > 0:
        portfolio_returns = portfolio_returns - weight_changes_s * tc_val

    # Apply slippage cost on turnover if any
    slip_val = float(slippage) if slippage is not None else 0.0
    if slip_val > 0:
        portfolio_returns = portfolio_returns - weight_changes_s * slip_val

    # Apply modeled transaction costs if any
    if cost_model is not None:
        if not isinstance(cost_model, TransactionCostModel):
            raise TypeError("cost_model must be a TransactionCostModel instance")
        weights_prev = weights.shift(1).fillna(0.0)
        period_costs = compute_transaction_costs(
            weights, weights_prev, prices_df, cost_model, adv_usd=adv_usd
        )
        period_costs = period_costs.reindex(portfolio_returns.index).fillna(0.0)
        portfolio_returns = portfolio_returns - period_costs.astype(float)

    # Calculate cumulative returns
    portfolio_returns = portfolio_returns.fillna(0.0)
    portfolio_returns_filled = portfolio_returns.clip(lower=-1.0 + 1e-12)
    log_returns = np.log1p(portfolio_returns_filled.to_numpy(dtype=float))
    cumulative_returns = np.exp(np.cumsum(log_returns))

    results = pd.DataFrame({
        'returns': portfolio_returns,
        'cumulative': cumulative_returns
    }, index=common_idx)

    return results
