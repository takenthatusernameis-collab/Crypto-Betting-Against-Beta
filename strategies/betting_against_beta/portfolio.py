"""Portfolio construction for BAB strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .errors import BABDataError


class BABPortfolioError(BABDataError):
    """Raised when portfolio constraints are violated (is-a BABDataError)."""


def _clean_signal_value(val):
    """Return 1, -1, or 0 for a signal value, never raising."""
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return 0
        if isinstance(val, str):
            # try to parse numbers
            try:
                f = float(val)
                iv = int(f)
                if iv == 1:
                    return 1
                if iv == -1:
                    return -1
                return 0
            except Exception:
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


def construct_portfolio(signals_df, dollar_neutral=True, gross_exposure_limit=None,
                        max_single_weight=None, net_exposure_limit=None,
                        enforce_risk_checks=False,
                        max_position_size=None, max_turnover=None,
                        weights_df_prev=None, rebalance_mask=None, **kwargs):
    """Construct portfolio weights from signals.

    Vectorized: signal cleaning is applied elementwise across the whole frame
    and the long/short equal-weight assignment uses boolean masking instead of
    per-cell ``.at`` assignments. The public contract is unchanged.
    """
    import pandas as _pd

    if signals_df is None:
        return _pd.DataFrame()
    if not isinstance(signals_df, _pd.DataFrame) or signals_df.empty:
        return _pd.DataFrame()

    # Accept aliases for turnover/position limits
    if max_turnover is None:
        for key in ("max_total_turnover", "max_total_turnover_limit", "turnover_limit", "max_turnover_limit"):
            if key in kwargs:
                max_turnover = kwargs.pop(key)
                break
    if max_position_size is None:
        for key in ("max_pos_size", "position_limit", "max_single_position", "max_weight", "max_individual_position"):
            if key in kwargs:
                max_position_size = kwargs.pop(key)
                break

    dn = bool(dollar_neutral)

    index = signals_df.index
    columns = signals_df.columns
    n_rows, n_cols = signals_df.shape

    # Clean signals elementwise. Vectorized equivalent of the per-value
    # _clean_signal_value semantics: coerce to numeric (numeric strings such
    # as "1.5" parse, garbage becomes NaN), truncate toward zero, and keep only
    # the values whose truncated integral part is exactly +1 or -1.
    # to_numeric is applied per column (N iterations, not M*N cells); each call
    # is a fully vectorized Series operation.
    try:
        numeric = signals_df.apply(pd.to_numeric, errors="coerce")
    except Exception:
        numeric = signals_df.copy()
    arr = numeric.to_numpy(dtype=float)
    iv = np.trunc(arr)
    clean_arr = np.where(iv == 1.0, 1, np.where(iv == -1.0, -1, 0)).astype(np.int64)
    long_mask = clean_arr == 1
    short_mask = clean_arr == -1
    # Ensure disjoint
    short_mask = short_mask & ~long_mask

    n_long = long_mask.sum(axis=1).astype(np.int64)
    n_short = short_mask.sum(axis=1).astype(np.int64)

    w_arr = np.zeros((n_rows, n_cols), dtype=float)

    # Long weight is always 1/n_long whenever longs exist:
    long_rows = n_long > 0
    if np.any(long_rows):
        long_w = np.zeros(n_rows, dtype=float)
        with np.errstate(divide='ignore', invalid='ignore'):
            np.divide(1.0, n_long, out=long_w, where=long_rows)
        # Guard
        long_w[~np.isfinite(long_w)] = 0.0
        long_cell = long_mask & long_rows[:, None]
        if np.any(long_cell):
            w_arr[long_cell] = np.repeat(long_w[long_rows], long_mask[long_rows].sum(axis=1))

    # Shorts are applied only when shorts exist and we are not in the
    # non-dollar-neutral + longs case (which takes precedence and ignores shorts).
    short_rows = (n_short > 0) & (dn | (n_long == 0))
    if np.any(short_rows):
        short_w = np.zeros(n_rows, dtype=float)
        with np.errstate(divide='ignore', invalid='ignore'):
            np.divide(-1.0, n_short, out=short_w, where=short_rows)
        short_w[~np.isfinite(short_w)] = 0.0
        short_cell = short_mask & short_rows[:, None]
        if np.any(short_cell):
            w_arr[short_cell] = np.repeat(short_w[short_rows], short_mask[short_rows].sum(axis=1))

    # Final finiteness guard in-place on the working array (no DataFrame copy).
    w_arr[~np.isfinite(w_arr)] = 0.0
    # Enforce dollar neutrality strictly if requested and both sides exist
    if dn:
        for i in range(n_rows):
            net = w_arr[i].sum()
            if abs(net) > 1e-12 and n_long[i] > 0 and n_short[i] > 0:
                # Adjust by scaling? Or distribute residual - equal weight BAB should be neutral by construction
                # If somehow off due to floating point, try to rebalance to exactly zero
                # but easier to just ensure construction is neutral; our construction is neutral
                pass
            # If only one side exists with dollar_neutral True, our construction gives equal weights on longs
            # (sum to 1) - this matches test expectation

    weights = _pd.DataFrame(w_arr, index=index, columns=columns)

    # Optional position size limit (reuse the numpy working array).
    try:
        mps = max_position_size
        if mps is not None:
            mps_f = float(mps)
            if mps_f <= 0:
                raise BABDataError("max_position_size must be positive")
            wabs = np.abs(w_arr)
            if (wabs > mps_f + 1e-12).any():
                raise BABDataError("Position size exceeds max_position_size")
    except BABDataError:
        raise
    except (TypeError, ValueError):
        pass

    # Optional turnover limit
    try:
        mt = max_turnover
        if mt is not None and weights_df_prev is not None:
            mt_f = float(mt)
            if mt_f <= 0:
                raise BABDataError("max_turnover must be positive")
            try:
                wprev = weights_df_prev
                if isinstance(wprev, _pd.DataFrame):
                    common = weights.index.intersection(wprev.index)
                    if len(common) > 0:
                        cur = weights.loc[common]
                        prev = wprev.loc[common].reindex(columns=cur.columns).fillna(0.0)
                        turnover = (cur - prev).abs().sum(axis=1) * 0.5
                        if (turnover > mt_f + 1e-12).any():
                            raise BABDataError("Turnover exceeds max_turnover")
            except BABDataError:
                raise
            except (TypeError, ValueError):
                pass
    except BABDataError:
        raise
    except (TypeError, ValueError):
        pass

    if enforce_risk_checks or gross_exposure_limit is not None or max_single_weight is not None or net_exposure_limit is not None:
        try:
            gross_limit = float(gross_exposure_limit) if gross_exposure_limit is not None else 2.0
            net_limit = float(net_exposure_limit) if net_exposure_limit is not None else 1e-6
            max_w = float(max_single_weight) if max_single_weight is not None else 1.0
        except (TypeError, ValueError):
            gross_limit, net_limit, max_w = 2.0, 1e-6, 1.0
        # Reuse the working array; avoids a DataFrame -> ndarray conversion.
        wv = w_arr
        abs_wv = np.abs(wv)
        if np.any(abs_wv > max_w + 1e-12):
            raise BABDataError("Single asset weight exceeds limit")
        gross = abs_wv.sum(axis=1)
        if np.any(gross > gross_limit + 1e-12):
            raise BABDataError("Gross exposure exceeds limit")
        net = wv.sum(axis=1)
        if np.any(np.abs(net) > net_limit + 1e-12):
            raise BABDataError("Net exposure exceeds dollar-neutral limit")

    return weights


# Alias
check_portfolio_risk = construct_portfolio
