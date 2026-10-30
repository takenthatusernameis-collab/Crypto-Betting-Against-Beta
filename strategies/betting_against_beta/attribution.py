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
    """Return a per-period trade-attribution frame aligned to ``backtest``."""
    if backtest is None or not isinstance(backtest, pd.DataFrame) or backtest.empty:
        return pd.DataFrame(columns=ATTRIBUTION_COLUMNS)

    idx = backtest.index
    zero = pd.Series(0.0, index=idx)

    gross = backtest.get("gross_return", zero)
    cost = backtest.get("cost_drag", zero)
    slip = backtest.get("slippage_drag", zero)

    frame = pd.DataFrame(index=idx)
    frame["gross_return"] = pd.Series(gross, index=idx).astype("float64").replace([float("inf"), float("-inf")], float("nan")).fillna(0.0)
    frame["cost_drag"] = pd.Series(cost, index=idx).astype("float64").replace([float("inf"), float("-inf")], float("nan")).fillna(0.0)
    frame["slippage_drag"] = pd.Series(slip, index=idx).astype("float64").replace([float("inf"), float("-inf")], float("nan")).fillna(0.0)

    if "returns" in backtest.columns:
        frame["net_return"] = pd.Series(backtest["returns"], index=idx).astype("float64").replace([float("inf"), float("-inf")], float("nan")).fillna(0.0)
    else:
        frame["net_return"] = (
            frame["gross_return"] - frame["cost_drag"] - frame["slippage_drag"]
        )
    frame["net_return"] = frame["net_return"].replace([float("inf"), float("-inf")], float("nan")).fillna(0.0)

    return frame[ATTRIBUTION_COLUMNS]


def attribution_totals(attribution_df: pd.DataFrame) -> dict:
    """Aggregate an attribution frame into scalar totals."""
    if attribution_df is None or not isinstance(attribution_df, pd.DataFrame) or attribution_df.empty:
        return {
            "gross_return": 0.0,
            "cost_drag": 0.0,
            "slippage_drag": 0.0,
            "net_return": 0.0,
            "cost_share": 0.0,
            "slippage_share": 0.0,
        }
    df = attribution_df
    gross = float(pd.Series(df["gross_return"]).replace([float("inf"), float("-inf")], float("nan")).fillna(0.0).sum()) if "gross_return" in df.columns else 0.0
    cost = float(pd.Series(df["cost_drag"]).replace([float("inf"), float("-inf")], float("nan")).fillna(0.0).sum()) if "cost_drag" in df.columns else 0.0
    slip = float(pd.Series(df["slippage_drag"]).replace([float("inf"), float("-inf")], float("nan")).fillna(0.0).sum()) if "slippage_drag" in df.columns else 0.0
    if "net_return" in df.columns:
        net = float(pd.Series(df["net_return"]).replace([float("inf"), float("-inf")], float("nan")).fillna(0.0).sum())
    else:
        net = gross - cost - slip
    denom = abs(gross)
    if denom == 0 or not (denom == denom):  # NaN check
        cost_share = 0.0
        slip_share = 0.0
    else:
        cost_share = float(cost / denom)
        slip_share = float(slip / denom)
    return {
        "gross_return": float(gross),
        "cost_drag": float(cost),
        "slippage_drag": float(slip),
        "net_return": float(net),
        "cost_share": float(cost_share),
        "slippage_share": float(slip_share),
    }
