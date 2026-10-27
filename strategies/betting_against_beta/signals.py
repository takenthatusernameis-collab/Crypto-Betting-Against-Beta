"""Signal generation for BAB strategy."""

import numpy as np
import pandas as pd


def generate_bab_signals(betas_df, long_quantile=0.3, short_quantile=0.3):
    """Generate long/short signals based on beta ranking."""
    signals = pd.DataFrame(0, index=betas_df.index, columns=betas_df.columns)

    for idx in betas_df.index:
        betas = betas_df.loc[idx].dropna()
        if len(betas) == 0:
            continue

        # Sort by beta ascending (low beta first)
        sorted_betas = betas.sort_values()
        n = len(sorted_betas)

        n_long = max(1, int(n * long_quantile))
        n_short = max(1, int(n * short_quantile))

        # Long low beta, short high beta
        long_assets = sorted_betas.index[:n_long]
        short_assets = sorted_betas.index[-n_short:]

        for asset in long_assets:
            signals.at[idx, asset] = 1  # long
        for asset in short_assets:
            signals.at[idx, asset] = -1  # short

    return signals
