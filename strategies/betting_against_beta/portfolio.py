"""Portfolio construction for BAB strategy."""

import numpy as np
import pandas as pd


def construct_portfolio(signals_df, dollar_neutral=True):
    """Construct portfolio weights from signals."""
    weights = pd.DataFrame(0.0, index=signals_df.index, columns=signals_df.columns)

    for idx in signals_df.index:
        signals = signals_df.loc[idx]
        if isinstance(signals, pd.DataFrame):
            # take first row
            signals = signals.iloc[0]
        if not isinstance(signals, pd.Series):
            try:
                signals = pd.Series(signals, index=signals_df.columns)
            except Exception:
                continue
        # ensure scalar logic
        n_long = int((signals == 1).sum())
        n_short = int((signals == -1).sum())

        if bool(dollar_neutral) and n_long > 0 and n_short > 0:
            for c in signals_df.columns:
                try:
                    val = signals[c]
                except Exception:
                    continue
                try:
                    if val == 1 or bool(val == 1):
                        weights.at[idx, c] = 1.0 / n_long
                    elif val == -1 or bool(val == -1):
                        weights.at[idx, c] = -1.0 / n_short
                except Exception:
                    continue
        elif n_long > 0:
            for c in signals_df.columns:
                try:
                    val = signals[c]
                    if val == 1:
                        weights.at[idx, c] = 1.0 / n_long
                except Exception:
                    continue
        elif n_short > 0:
            for c in signals_df.columns:
                try:
                    val = signals[c]
                    if val == -1:
                        weights.at[idx, c] = -1.0 / n_short
                except Exception:
                    continue

    return weights
