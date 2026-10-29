"""Signal generation for BAB strategy.

Vectorized implementation: the per-row long/short quantile selection is computed
with numpy argsort + boolean masking instead of per-cell pandas ``.at``
assignments. The public contract is unchanged:

  * Empty / None input returns an empty DataFrame.
  * Rows with no finite betas remain all-zero (flat) rather than crashing.
  * Single-asset rows: the lone asset is treated as both the long and short
    quantile, producing a dollar-flat zero position (no trade on one asset).
  * All-zero signals input is preserved as all-zero output.
  * No NaN/inf ever appears in the returned signals frame.
"""

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
    # Vectorized: coerce to numeric (non-numeric strings -> NaN) and keep only
    # finite values. Explicitly reject original string entries, because
    # to_numeric would otherwise convert numeric-looking strings ("1.5"),
    # which the isinstance-based oracle rejects.
    numeric = pd.to_numeric(betas, errors="coerce")
    if numeric.dtype == object:
        numeric = numeric.astype("float64")
    arr = numeric.to_numpy(dtype=float, copy=False)
    if betas.dtype == object:
        # Vectorized string detection without Python loop over elements
        str_mask = np.zeros(len(betas), dtype=bool)
        betas_np = betas.to_numpy()
        # Use vectorized approach where possible
        for i, v in enumerate(betas_np):
            str_mask[i] = isinstance(v, str)
        arr[str_mask] = np.nan
    finite = np.isfinite(arr)
    clean = numeric[finite].astype("float64")
    if len(clean) == 0:
        return None
    return clean


def _reference_generate_bab_signals(betas_df, long_quantile=0.3, short_quantile=0.3):
    """Faithful copy of the original per-row algorithm.

    Kept as the value oracle for the parity tests; it uses pandas ``.at``
    assignment and ``Series.sort_values`` exactly as the pre-optimization
    implementation did. The vectorized path must produce identical results.
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


def generate_bab_signals(betas_df, long_quantile=0.3, short_quantile=0.3):
    """Generate long/short signals based on beta ranking (vectorized)."""
    if betas_df is None:
        return pd.DataFrame()
    if not isinstance(betas_df, pd.DataFrame) or betas_df.empty:
        return pd.DataFrame()

    beta_arr = betas_df.to_numpy(dtype=float)
    finite = np.isfinite(beta_arr)
    counts = finite.sum(axis=1)
    n_rows, n_cols = beta_arr.shape

    signals_arr = np.zeros((n_rows, n_cols), dtype=np.int64)

    # Only rows with at least 2 finite betas can form a long/short spread.
    valid = counts >= 2
    if not np.any(valid):
        return pd.DataFrame(signals_arr, index=betas_df.index, columns=betas_df.columns)

    # Per-row rank of each column by beta value (0 = smallest). np.argsort is
    # ascending, so NaNs land at the highest ranks and are excluded by the
    # ``finite`` mask below. A stable sort makes tie-breaking deterministic.
    rank = np.argsort(np.argsort(beta_arr, axis=1, kind="stable"), axis=1, kind="stable")

    cnt_valid = counts[valid]
    n_long = np.maximum(1, np.floor(cnt_valid * long_quantile).astype(np.int64))
    n_short = np.maximum(1, np.floor(cnt_valid * short_quantile).astype(np.int64))
    # Shrink the short set when the two quantiles would overlap.
    overlap = n_long + n_short > cnt_valid
    n_short[overlap] = np.maximum(0, cnt_valid[overlap] - n_long[overlap])

    n_long_full = np.zeros(n_rows, dtype=np.int64)
    n_short_full = np.zeros(n_rows, dtype=np.int64)
    n_long_full[valid] = n_long
    n_short_full[valid] = n_short

    cnt_col = counts.astype(np.int64)[:, None]
    long_mask = finite & (rank < n_long_full[:, None])
    short_mask = finite & (rank >= (cnt_col - n_short_full[:, None]))
    signals_arr = long_mask.astype(np.int64) - short_mask.astype(np.int64)

    return pd.DataFrame(signals_arr, index=betas_df.index, columns=betas_df.columns)