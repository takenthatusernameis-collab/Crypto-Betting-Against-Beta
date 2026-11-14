"""Trade attribution for BAB backtests.

Splits per-period performance into gross return, transaction-cost drag, and
slippage drag so a caller can attribute P&L to alpha versus execution costs.
All functions are defensive: None / empty inputs yield empty frames or zeros
rather than raising.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ATTRIBUTION_COLUMNS = ["gross_return", "cost_drag", "slippage_drag", "net_return"]


def _finite_series(values, index) -> pd.Series:
    """Return ``values`` as a finite ``float64`` Series aligned to ``index``.

    Every non-finite entry (NaN, +inf, -inf) becomes ``0.0``.  This is
    provably identical to the previous
    ``pd.Series(values, index=index).astype("float64")
    .replace([inf,-inf], nan).fillna(0.0)`` (finite values are untouched;
    NaN/inf/-inf all collapse to 0.0) but avoids the per-series pandas
    ``astype``/``replace_list``/``fillna`` block-manager passes: a single
    ``to_numpy`` + ``np.where`` repair, with a C-level ``isfinite`` fast path
    that skips the repair entirely when the input is already finite.
    """
    series = pd.Series(values, index=index)
    try:
        arr = series.to_numpy(dtype=float, copy=False)
        if not np.all(np.isfinite(arr)):
            arr = np.where(np.isfinite(arr), arr, 0.0)
        return pd.Series(arr, index=index)
    except Exception:
        # Defensive fallback: preserve the original replace+fillna semantics if
        # the numeric conversion or fast-path repair fails for any reason.
        return (
            series.astype("float64")
            .replace([float("inf"), float("-inf")], float("nan"))
            .fillna(0.0)
        )


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
    frame["gross_return"] = _finite_series(gross, idx)
    frame["cost_drag"] = _finite_series(cost, idx)
    frame["slippage_drag"] = _finite_series(slip, idx)

    if "returns" in backtest.columns:
        frame["net_return"] = _finite_series(backtest["returns"], idx)
    else:
        frame["net_return"] = (
            frame["gross_return"] - frame["cost_drag"] - frame["slippage_drag"]
        )
        frame["net_return"] = _finite_series(frame["net_return"], idx)

    return frame[ATTRIBUTION_COLUMNS]


def _finite_sum(values) -> float:
    """Sum a series after repairing non-finite entries to ``0.0``.

    Equivalent to the previous
    ``pd.Series(values).replace([inf,-inf], nan).fillna(0.0).sum()``: a
    single ``to_numpy`` + ``np.where`` finite repair, then a vectorized sum.
    """
    try:
        arr = pd.Series(values).to_numpy(dtype=float, copy=False)
        if not np.all(np.isfinite(arr)):
            arr = np.where(np.isfinite(arr), arr, 0.0)
        return float(arr.sum())
    except Exception:
        # Defensive fallback: preserve the original replace+fillna semantics if
        # the numeric conversion or fast-path repair fails for any reason.
        return float(
            pd.Series(values)
            .astype("float64")
            .replace([float("inf"), float("-inf")], float("nan"))
            .fillna(0.0)
            .sum()
        )


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
    gross = _finite_sum(df["gross_return"]) if "gross_return" in df.columns else 0.0
    cost = _finite_sum(df["cost_drag"]) if "cost_drag" in df.columns else 0.0
    slip = _finite_sum(df["slippage_drag"]) if "slippage_drag" in df.columns else 0.0
    net = _finite_sum(df["net_return"]) if "net_return" in df.columns else gross - cost - slip
    denom = abs(gross)
    if denom == 0 or denom != denom:  # NaN check
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
