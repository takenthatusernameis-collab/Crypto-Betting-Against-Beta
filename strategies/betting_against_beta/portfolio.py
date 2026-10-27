"""Portfolio construction for BAB strategy."""

import numpy as np
import pandas as pd


def construct_portfolio(signals_df, dollar_neutral=True):
    """Construct portfolio weights from signals."""
    weights = pd.DataFrame(0.0, index=signals_df.index, columns=signals_df.columns)

    for idx in signals_df.index:
        signals = signals_df.loc[idx]
        long_mask = signals == 1
        short_mask = signals == -1

        n_long = long_mask.sum()
        n_short = short_mask.sum()

        if dollar_neutral and n_long > 0 and n_short > 0:
            # Equal weight, dollar neutral
            weights.loc[idx, long_mask] = 1.0 / n_long  # +1.0 total long
            weights.loc[idx, short_mask] = -1.0 / n_short  # -1.0 total short
        elif n_long > 0:
            weights.loc[idx, long_mask] = 1.0 / n_long
        elif n_short > 0:
            weights.loc[idx, short_mask] = -1.0 / n_short

    return weights
