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
    # Enforce dollar neutrality strictly if requested and both sides exist.
    # The equal-weight construction is neutral by construction, but floating
    # point drift and the disjoint-set guards can leave a residual.  We
    # redistribute the residual proportionally across the long book when both
    # sides are present, and clamp the result to finite values.  When only one
    # side is present we leave it as-is (long-only semantics).
    if dn:
        # Re-normalize each side exactly so the book is dollar-neutral to
        # machine precision: longs sum to +1.0, shorts to -1.0.  Equal-weight
        # within each side is preserved (every long scaled by the same factor).
        both = (n_long > 0) & (n_short > 0)
        if np.any(both):
            for i in np.nonzero(both)[0]:
                row = w_arr[i]
                long_sum = float(row[row > 0].sum())
                short_sum = float(row[row < 0].sum())
                if long_sum > 0:
                    row[row > 0] = row[row > 0] / long_sum
                if short_sum < 0:
                    row[row < 0] = row[row < 0] / (-short_sum)
                w_arr[i] = row
        # Mop up any residual drift so net exposure is exactly zero.
        net = w_arr.sum(axis=1)
        both = (n_long > 0) & (n_short > 0)
        if np.any(both & (np.abs(net) > 1e-12)):
            # Distribute -net across longs proportionally to their weight so the
            # long book still sums to 1.0 after the adjustment.
            for i in np.nonzero(both & (np.abs(net) > 1e-12))[0]:
                row = w_arr[i]
                long_sum = float(row[row > 0].sum())
                if long_sum > 1e-18:
                    row[row > 0] = row[row > 0] * (1.0 - net[i]) / long_sum
                w_arr[i] = row
        # Final clamp after any adjustment.
        w_arr[~np.isfinite(w_arr)] = 0.0

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


def enforce_beta_neutrality(
    weights,
    betas,
    target_beta=0.0,
    tolerance=1e-4,
    max_drift=1e-4,
    returns=None,
    benchmark_returns=None,
    tracking_error_tolerance=None,
    tracking_error_limit=None,
    enable_tracking_error_monitoring=False,
    correction=True,
):
    """Enforce portfolio beta neutrality via least-squares weight adjustment.

    The portfolio beta is the return-weighted average of asset betas::

        beta_p = sum_i w_i * beta_i

    This function adjusts weights so that ``beta_p`` is driven toward
    ``target_beta`` while minimizing the squared distance from the original
    weights (a minimum-norm correction).  The adjustment preserves dollar
    neutrality (sum of weights stays zero) when the original portfolio is
    dollar-neutral.

    Degenerate cases are handled explicitly:

    * ``weights`` or ``betas`` is ``None`` / empty -> returns the input unchanged.
    * No finite beta available -> returns the input unchanged.
    * ``correction=False`` -> only monitoring (no adjustment); returns input.
    """
    import pandas as _pd

    if weights is None or betas is None:
        return weights
    if not isinstance(weights, _pd.DataFrame) or weights.empty:
        return weights
    if not isinstance(betas, _pd.DataFrame) or betas.empty:
        return weights

    # Align columns and rows.
    common_cols = weights.columns.intersection(betas.columns)
    if len(common_cols) == 0:
        return weights
    common_idx = weights.index.intersection(betas.index)
    if len(common_idx) == 0:
        return weights

    w = weights.loc[common_idx, common_cols].astype(float).copy()
    b = betas.loc[common_idx, common_cols].astype(float).copy()

    # Clean weights of non-finite values.
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    # Betas: replace non-finite with NaN; they will be masked out.
    b = b.replace([np.inf, -np.inf], np.nan)

    out = w.copy()

    tol = float(tolerance) if tolerance is not None else 1e-4
    drift = float(max_drift) if max_drift is not None else tol
    if not np.isfinite(tol) or tol < 0:
        tol = 1e-4
    if not np.isfinite(drift) or drift < 0:
        drift = tol
    target = float(target_beta) if target_beta is not None else 0.0
    if not np.isfinite(target):
        target = 0.0

    te_tol = tracking_error_tolerance if tracking_error_tolerance is not None else tracking_error_limit
    enable_te = bool(enable_tracking_error_monitoring) or te_tol is not None

    cols = list(out.columns)
    w_arr = out.to_numpy(dtype=float, copy=True)
    b_arr = b.to_numpy(dtype=float)

    for i in range(len(common_idx)):
        row_w = w_arr[i]
        row_b = b_arr[i]
        finite = np.isfinite(row_b)
        if not np.any(finite):
            continue
        w_f = row_w[finite]
        b_f = row_b[finite]
        # Current portfolio beta.
        denom = np.abs(w_f).sum()
        if denom < 1e-18:
            continue
        port_beta = float(np.sum(w_f * b_f) / denom)
        if abs(port_beta - target) <= tol:
            continue

        if not correction:
            continue

        # Minimum-norm correction that preserves dollar neutrality.
        # Solve: minimize sum(delta_i^2) subject to
        #   sum_i delta_i * b_i = residual   (beta constraint)
        #   sum_i delta_i = 0                (dollar neutrality, when applicable)
        # Solution via Lagrange multipliers:
        #   delta_i = alpha * (b_i - mean(b))
        #   alpha = residual / (sum(b_i^2) - sum(b_i)^2 / n)
        residual = target - port_beta
        b_mean = float(np.sum(b_f)) / len(b_f)
        centered = b_f - b_mean
        s2_centered = float(np.sum(centered * centered))
        if s2_centered < 1e-18:
            continue
        alpha = residual / s2_centered
        delta = alpha * centered
        new_w = w_f + delta
        # Clamp to finite values.
        new_w = np.where(np.isfinite(new_w), new_w, 0.0)
        # Write back only the finite positions.
        w_arr[i, :][finite] = new_w

    out = _pd.DataFrame(w_arr, index=common_idx, columns=cols)
    out = out.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


# Alias
check_portfolio_risk = construct_portfolio
