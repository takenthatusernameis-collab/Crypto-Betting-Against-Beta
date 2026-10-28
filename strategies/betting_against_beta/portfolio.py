"""Portfolio construction for BAB strategy."""

import numpy as np
import pandas as pd


def construct_portfolio(signals_df, dollar_neutral=True):
    """Construct portfolio weights from signals."""
    if signals_df is None:
        return pd.DataFrame()
    weights = pd.DataFrame(0.0, index=signals_df.index, columns=signals_df.columns)

    for idx in signals_df.index:
        try:
            signals = signals_df.loc[idx]
            if isinstance(signals, pd.DataFrame):
                signals = signals.iloc[0]
            if not isinstance(signals, pd.Series):
                try:
                    signals = pd.Series(signals, index=signals_df.columns)
                except Exception:
                    continue
            n_long = int((signals == 1).sum())
            n_short = int((signals == -1).sum())

            if bool(dollar_neutral) and n_long > 0 and n_short > 0:
                for c in signals_df.columns:
                    try:
                        val = signals[c]
                        # handle
                        is_long = False
                        is_short = False
                        try:
                            if val == 1 or bool(val == 1):
                                is_long = True
                        except Exception:
                            pass
                        try:
                            if val == -1 or bool(val == -1):
                                is_short = True
                        except Exception:
                            pass
                        if is_long:
                            w = 1.0 / n_long
                            if np.isfinite(w):
                                weights.at[idx, c] = w
                        elif is_short:
                            w = -1.0 / n_short
                            if np.isfinite(w):
                                weights.at[idx, c] = w
                    except Exception:
                        continue
            elif n_long > 0:
                for c in signals_df.columns:
                    try:
                        val = signals[c]
                        if val == 1:
                            w = 1.0 / n_long
                            if np.isfinite(w):
                                weights.at[idx, c] = w
                    except Exception:
                        continue
            elif n_short > 0:
                for c in signals_df.columns:
                    try:
                        val = signals[c]
                        if val == -1:
                            w = -1.0 / n_short
                            if np.isfinite(w):
                                weights.at[idx, c] = w
                    except Exception:
                        continue
            # ensure finite
            row = weights.loc[idx]
            # if any non-finite, zero
            for c in weights.columns:
                try:
                    v = weights.at[idx, c]
                    if not np.isfinite(v):
                        weights.at[idx, c] = 0.0
                except Exception:
                    weights.at[idx, c] = 0.0
        except Exception:
            continue

    # Final finiteness guard
    try:
        weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    except Exception:
        pass
    return weights
