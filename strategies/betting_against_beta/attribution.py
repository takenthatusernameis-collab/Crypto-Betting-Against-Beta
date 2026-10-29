"""Trade attribution for BAB backtests.

Splits per-period performance into gross return, transaction-cost drag, and
slippage drag so a caller can attribute P&L to alpha versus execution costs.
All functions are defensive: None / empty inputs yield empty frames or zeros
rather than raising.
"""

from __future__ import annotations

import pandas as pd

ATTRIBUTION_COLUMNS = ["gross_return", "cost_drag", "slippage_drag", "net_return"]


def trade_attribution(backtest: pd.DataFrame) -> pd.DataFrame:
    """Return a per-period trade-attribution frame aligned to ``backtest``.

    Columns:
        ``gross_return``   return before any costs (weights x asset returns)
        ``cost_drag``      transaction-cost drag per period (turnover x tc)
        ``slippage_drag``  slippage drag per period (turnover x slippage)
        ``net_return``     gross_return - cost_drag - slippage_drag

    Missing cost/drag columns are treated as zero. A ``net_return`` column is
    always present; if ``backtest`` already carries a ``returns`` column it is
    used as the authoritative net return.
    """
    if backtest is None or not isinstance(backtest, pd.DataFrame) or backtest.empty:
        return pd.DataFrame(columns=ATTRIBUTION_COLUMNS)

    idx = backtest.index
    zero = pd.Series(0.0, index=idx)

    gross = backtest.get("gross_return", zero)
    cost = backtest.get("cost_drag", zero)
    slip = backtest.get("slippage_drag", zero)

    frame = pd.DataFrame(index=idx)
    frame["gross_return"] = pd.Series(gross, index=idx).astype("float64").fillna(0.0)
    frame["cost_drag"] = pd.Series(cost, index=idx).astype("float64").fillna(0.0)
    frame["slippage_drag"] = pd.Series(slip, index=idx).astype("float64").fillna(0.0)

    if "returns" in backtest.columns:
        frame["net_return"] = pd.Series(backtest["returns"], index=idx).astype("float64").fillna(0.0)
    else:
        frame["net_return"] = (
            frame["gross_return"] - frame["cost_drag"] - frame["slippage_drag"]
        ).fillna(0.0)

    return frame[ATTRIBUTION_COLUMNS]


def attribution_totals(attribution: pd.DataFrame) -> dict:
    """Aggregate an attribution frame into scalar totals.

    Returns gross, cost drag, slippage drag, net, and the cost/slippage share
    of gross return (guarded against a zero gross denominator).
    """
    if attribution is None or not isinstance(attribution, pd.DataFrame) or attribution.empty:
        return {
            "gross_return": 0.0,
            "cost_drag": 0.0,
            "slippage_drag": 0.0,
            "net_return": 0.0,
            "cost_share": 0.0,
            "slippage_share": 0.0,
        }
    gross = float(attribution["gross_return"].sum()) if "gross_return" in attribution.columns else 0.0
    cost = float(attribution["cost_drag"].sum()) if "cost_drag" in attribution.columns else 0.0
    slip = float(attribution["slippage_drag"].sum()) if "slippage_drag" in attribution.columns else 0.0
    net = float(attribution["net_return"].sum()) if "net_return" in attribution.columns else gross - cost - slip
    denom = abs(gross)
    cost_share = cost / denom if denom > 0 else 0.0
    slip_share = slip / denom if denom > 0 else 0.0
    return {
        "gross_return": gross,
        "cost_drag": cost,
        "slippage_drag": slip,
        "net_return": net,
        "cost_share": float(cost_share),
        "slippage_share": float(slip_share),
    }
