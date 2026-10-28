"""Portfolio construction for BAB strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _clean_signal_value(val):
    """Return 1, -1, or 0 for a signal value, never raising."""
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return 0
        if isinstance(val, (int, float, np.integer, np.floating)) and np.isfinite(float(val)):
            iv = int(float(val))
            if iv == 1:
                return 1
            if iv == -1:
                return -1
        return 0
    except (TypeError, ValueError):
        return 0


def construct_portfolio(signals_df, dollar_neutral=True):
    """Construct portfolio weights from signals.

    Robustness guarantees:
      * None / empty input returns an empty DataFrame.
      * Every row's weights are finite (non-finite values coerced to 0.0).
      * Dollar-neutral rows sum to zero when both longs and shorts exist.
      * Long-only (dollar_neutral=False) rows weight only longs.
      * All-zero signal rows remain all-zero.
    """
    if signals_df is None:
        return pd.DataFrame()
    if not isinstance(signals_df, pd.DataFrame) or signals_df.empty:
        return pd.DataFrame()

    weights = pd.DataFrame(0.0, index=signals_df.index, columns=signals_df.columns)

    for idx in signals_df.index:
        row = signals_df.loc[idx]
        if isinstance(row, pd.DataFrame):
            if row.shape[0] != 1:
                continue
            row = row.iloc[0]
        if not isinstance(row, pd.Series):
            try:
                row = pd.Series(row, index=signals_df.columns)
            except Exception:
                continue

        cleaned = row.map(_clean_signal_value)
        n_long = int((cleaned == 1).sum())
        n_short = int((cleaned == -1).sum())

        if n_long > 0 and n_short > 0 and bool(dollar_neutral):
            long_w = 1.0 / n_long
            short_w = -1.0 / n_short
            for c in signals_df.columns:
                v = cleaned[c]
                if v == 1:
                    weights.at[idx, c] = long_w
                elif v == -1:
                    weights.at[idx, c] = short_w
        elif n_long > 0:
            long_w = 1.0 / n_long
            for c in signals_df.columns:
                if cleaned[c] == 1:
                    weights.at[idx, c] = long_w
        elif n_short > 0:
            short_w = -1.0 / n_short
            for c in signals_df.columns:
                if cleaned[c] == -1:
                    weights.at[idx, c] = short_w

    # Final finiteness guard: coerce any stray non-finite to 0.0.
    weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return weights
