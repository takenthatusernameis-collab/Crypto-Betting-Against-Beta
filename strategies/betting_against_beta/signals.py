"""Signal generation for BAB strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _finite_beta_series(betas) -> pd.Series | None:
    """Return a clean numeric Series of finite betas, or None if none remain."""
    if betas is None:
        return None
    if isinstance(betas, pd.DataFrame):
        if betas.shape[0] != 1:
            return None
        betas = betas.iloc[0]
    if not isinstance(betas, pd.Series):
        return None
    finite = betas.apply(
        lambda x: isinstance(x, (int, float, np.integer, np.floating))
        and np.isfinite(float(x))
    )
    clean = betas[finite].astype("float64")
    if len(clean) == 0:
        return None
    return clean


def generate_bab_signals(betas_df, long_quantile=0.3, short_quantile=0.3):
    """Generate long/short signals based on beta ranking.

    Robustness guarantees:
      * Empty / None input returns an empty DataFrame.
      * Rows with no finite betas remain all-zero (flat) rather than crashing.
      * Single-asset rows: the lone asset is treated as both the long and short
        quantile, producing a dollar-flat zero position (no trade on one asset).
      * All-zero signals input is preserved as all-zero output.
      * No NaN/inf ever appears in the returned signals frame.
    """
    if betas_df is None:
        return pd.DataFrame()
    if not isinstance(betas_df, pd.DataFrame) or betas_df.empty:
        return pd.DataFrame()

    signals = pd.DataFrame(0, index=betas_df.index, columns=betas_df.columns)

    for idx in betas_df.index:
        clean = _finite_beta_series(betas_df.loc[idx])
        if clean is None:
            continue
        sorted_betas = clean.sort_values()
        n = len(sorted_betas)
        if n == 0:
            continue

        # A single asset cannot form a long/short spread; keep the row flat.
        if n < 2:
            continue

        n_long = max(1, int(n * long_quantile))
        n_short = max(1, int(n * short_quantile))
        # Never let the long and short sets overlap; shrink the short set
        # (possibly to zero) so the two quantiles stay disjoint.
        if n_long + n_short > n:
            n_short = max(0, n - n_long)

        long_assets = list(sorted_betas.index[:n_long])
        short_assets = list(sorted_betas.index[n - n_short:]) if n_short else []
        for asset in long_assets:
            signals.at[idx, asset] = 1
        for asset in short_assets:
            signals.at[idx, asset] = -1

    # Final finiteness guard: coerce any stray non-finite to 0.
    signals = signals.replace([np.inf, -np.inf], 0).fillna(0).astype("int64")
    return signals
