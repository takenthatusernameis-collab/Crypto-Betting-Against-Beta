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

    try:
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

        # Clean signals elementwise
        try:
            if all(pd.api.types.is_numeric_dtype(s) for s in signals_df.dtypes):
                numeric = signals_df.copy()
            else:
                try:
                    numeric = signals_df.apply(pd.to_numeric, errors="coerce")
                except Exception:
                    numeric = signals_df.copy()
                    for col in numeric.columns:
                        try:
                            numeric[col] = pd.to_numeric(numeric[col], errors="coerce")
                        except Exception:
                            numeric[col] = 0.0
            arr = numeric.to_numpy(dtype=float)
        except Exception:
            return _pd.DataFrame(0.0, index=index, columns=columns)
        iv = np.trunc(arr)
        clean_arr = np.where(iv == 1.0, 1, np.where(iv == -1.0, -1, 0)).astype(np.int64)
        long_mask = clean_arr == 1
        short_mask = clean_arr == -1
        short_mask = short_mask & ~long_mask

        n_long = long_mask.sum(axis=1).astype(np.int64)
        n_short = short_mask.sum(axis=1).astype(np.int64)

        def _write_book(mask, row_counts, weights_1d):
            """Assign one weight per selected cell, or surface the failure.

            The weights are computed once per row and fanned out to the selected
            cells; if that fan-out raises (shape mismatch, read-only buffer,
            exotic dtype) the resulting book would have *missing* positions
            rather than wrong ones, and a silent swallow would return a
            plausible-looking empty/partial book.  The outer handler converts
            the failure into an explicit ``BABPortfolioError``.
            """
            mask = np.asarray(mask, dtype=bool)
            row_counts = np.asarray(row_counts, dtype=np.int64)
            w_row = np.asarray(weights_1d, dtype=float)
            expected = int(row_counts.sum())
            fanned = np.repeat(w_row, row_counts)
            if fanned.shape[0] != expected or mask.sum() != expected:
                # A fan-out that does not line up with the selected cells would
                # leave positions unwritten (a silently truncated book).
                raise BABPortfolioError(
                    "weight fan-out does not match selected cells: "
                    f"{fanned.shape[0]} weights for {expected} cells"
                )
            w_arr[mask] = fanned

        w_arr = np.zeros((n_rows, n_cols), dtype=float)

        long_rows = n_long > 0
        if np.any(long_rows):
            long_w = np.zeros(n_rows, dtype=float)
            with np.errstate(divide='ignore', invalid='ignore'):
                np.divide(1.0, n_long, out=long_w, where=long_rows)
            long_w[~np.isfinite(long_w)] = 0.0
            long_cell = long_mask & long_rows[:, None]
            if np.any(long_cell):
                _write_book(long_cell, long_mask[long_rows].sum(axis=1), long_w[long_rows])

        short_rows = (n_short > 0) & (dn | (n_long == 0))
        if np.any(short_rows):
            short_w = np.zeros(n_rows, dtype=float)
            with np.errstate(divide='ignore', invalid='ignore'):
                np.divide(-1.0, n_short, out=short_w, where=short_rows)
            short_w[~np.isfinite(short_w)] = 0.0
            short_cell = short_mask & short_rows[:, None]
            if np.any(short_cell):
                _write_book(short_cell, short_mask[short_rows].sum(axis=1), short_w[short_rows])

        w_arr[~np.isfinite(w_arr)] = 0.0
        if np.any(w_arr < -1e12) or np.any(w_arr > 1e12):
            np.clip(w_arr, -1e12, 1e12, out=w_arr)
            w_arr[~np.isfinite(w_arr)] = 0.0
        if dn:
            both = (n_long > 0) & (n_short > 0)
            if np.any(both):
                both_idx = np.nonzero(both)[0]
                w_b = w_arr[both_idx]
                pos = np.where(w_b > 0.0, w_b, 0.0)
                neg = np.where(w_b < 0.0, w_b, 0.0)
                long_sum = pos.sum(axis=1)
                short_sum = neg.sum(axis=1)
                with np.errstate(divide='ignore', invalid='ignore'):
                    pos_scale = np.where(long_sum > 1e-18, 1.0 / long_sum, 1.0)
                    neg_scale = np.where(short_sum < -1e-18, -1.0 / short_sum, 1.0)
                w_arr[both_idx] = pos * pos_scale[:, None] + neg * neg_scale[:, None]
            net = w_arr.sum(axis=1)
            need_fix = both & (np.abs(net) > 1e-12)
            if np.any(need_fix):
                fix_idx = np.nonzero(need_fix)[0]
                w_f = w_arr[fix_idx]
                pos = np.where(w_f > 0.0, w_f, 0.0)
                neg = np.where(w_f < 0.0, w_f, 0.0)
                long_sum = pos.sum(axis=1)
                with np.errstate(divide='ignore', invalid='ignore'):
                    scale = np.where(long_sum > 1e-18, (1.0 - net[fix_idx]) / long_sum, 1.0)
                w_arr[fix_idx] = pos * scale[:, None] + neg
            w_arr[~np.isfinite(w_arr)] = 0.0
    except BABPortfolioError:
        raise
    except Exception as exc:
        # A failure here means no usable book could be built (uncoercible
        # dtypes, exotic index/columns, unusable frame).  Returning an
        # all-zero frame would report "no positions" instead of a defect, so
        # surface it with the original exception attached.
        raise BABPortfolioError(f"portfolio construction failed: {exc}") from exc

    weights = _pd.DataFrame(w_arr, index=index, columns=columns)

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
        row_b = b_arr[i]
        finite = np.isfinite(row_b)
        if not np.any(finite):
            continue
        b_f = row_b[finite]
        # Pre-compute correction direction (depends only on betas, which are fixed).
        b_mean = float(np.sum(b_f)) / len(b_f)
        centered = b_f - b_mean
        s2_centered = float(np.sum(centered * centered))
        if s2_centered < 1e-18:
            continue
        # Iterate the minimum-norm correction until |port_beta - target| <= tol.
        # Each pass applies delta_i = alpha * (b_i - mean(b)), which exactly fixes
        # sum(delta * b) = residual and preserves sum(delta) = 0. Because gross
        # exposure (denom) changes after each pass, one pass is not sufficient to
        # drive beta to exactly ``target``; iterating converges. Cap at 50 passes.
        for _ in range(50):
            row_w = w_arr[i]
            w_f = row_w[finite]
            denom = np.abs(w_f).sum()
            if denom < 1e-18:
                break
            port_beta = float(np.sum(w_f * b_f) / denom)
            if abs(port_beta - target) <= tol:
                break
            if not correction:
                break
            residual = target - port_beta
            alpha = residual / s2_centered
            delta = alpha * centered
            new_w = w_f + delta
            # Clamp to finite values.
            new_w = np.where(np.isfinite(new_w), new_w, 0.0)
            # Write back only the finite positions.
            w_arr[i, finite] = new_w

    out = _pd.DataFrame(w_arr, index=common_idx, columns=cols)
    out = out.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


# Alias
check_portfolio_risk = construct_portfolio
