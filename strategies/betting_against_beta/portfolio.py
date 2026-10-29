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

    # Clean signals elementwise (exact per-value semantics preserved), then work
    # with numpy arrays for the hot weight-assignment path.
    cleaned = signals_df.map(_clean_signal_value)
    n_rows, n_cols = cleaned.shape
    index = cleaned.index
    columns = cleaned.columns

    clean_arr = cleaned.to_numpy(dtype=np.int64, copy=False)
    long_mask = clean_arr == 1
    short_mask = clean_arr == -1

    n_long = long_mask.sum(axis=1).astype(np.int64)
    n_short = short_mask.sum(axis=1).astype(np.int64)

    w_arr = np.zeros((n_rows, n_cols), dtype=float)

    # Long weight is always 1/n_long whenever longs exist:
    #   - dollar_neutral + both sides: long_w = 1/n_long
    #   - dollar_neutral + longs only: long_w = 1/n_long
    #   - non-dollar-neutral + longs: long_w = 1/n_long
    long_rows = n_long > 0
    if np.any(long_rows):
        long_w = np.zeros(n_rows, dtype=float)
        np.divide(1.0, n_long, out=long_w, where=long_rows)
        long_cell = long_mask & long_rows[:, None]
        w_arr[long_cell] = np.repeat(long_w[long_rows], long_mask[long_rows].sum(axis=1))

    # Shorts are applied only when shorts exist and we are not in the
    # non-dollar-neutral + longs case (which takes precedence and ignores shorts).
    short_rows = (n_short > 0) & (dn | (n_long == 0))
    if np.any(short_rows):
        short_w = np.zeros(n_rows, dtype=float)
        np.divide(-1.0, n_short, out=short_w, where=short_rows)
        short_cell = short_mask & short_rows[:, None]
        w_arr[short_cell] = np.repeat(short_w[short_rows], short_mask[short_rows].sum(axis=1))

    weights = _pd.DataFrame(w_arr, index=index, columns=columns)

    # Final finiteness guard
    weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # Optional position size limit
    try:
        mps = max_position_size
        if mps is not None:
            mps_f = float(mps)
            if mps_f <= 0:
                raise BABDataError("max_position_size must be positive")
            wabs = weights.abs()
            if (wabs > mps_f + 1e-12).any().any():
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
        wv = weights.to_numpy(dtype=float)
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
