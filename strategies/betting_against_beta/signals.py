"""Signal generation for BAB strategy."""

import numpy as np
import pandas as pd


def generate_bab_signals(betas_df, long_quantile=0.3, short_quantile=0.3):
    """Generate long/short signals based on beta ranking."""
    if betas_df is None:
        return pd.DataFrame()
    signals = pd.DataFrame(0, index=betas_df.index, columns=betas_df.columns)

    for idx in betas_df.index:
        try:
            betas = betas_df.loc[idx]
            if isinstance(betas, pd.DataFrame):
                betas = betas.iloc[0]
            if not isinstance(betas, pd.Series):
                continue
            betas = betas.dropna()
            if len(betas) == 0:
                continue
            # Filter out non-finite
            finite_mask = betas.apply(lambda x: isinstance(x, (int, float, np.integer, np.floating)) and np.isfinite(x))
            betas = betas[finite_mask]
            if len(betas) == 0:
                continue
            sorted_betas = betas.sort_values()
            n = len(sorted_betas)
            if n == 0:
                continue
            n_long = max(1, int(n * long_quantile))
            n_short = max(1, int(n * short_quantile))
            if n_long == 0:
                n_long = 1
            if n_short == 0:
                n_short = 1
            long_assets = sorted_betas.index[:n_long]
            short_assets = sorted_betas.index[-n_short:]
            for asset in long_assets:
                signals.at[idx, asset] = 1
            for asset in short_assets:
                signals.at[idx, asset] = -1
        except Exception:
            # Do not swallow in a broad silent bad way - but ensure no crash; zero row is safe
            continue

    return signals
