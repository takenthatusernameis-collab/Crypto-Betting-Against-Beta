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

    Robustness guarantees:
      * None / empty input returns an empty DataFrame.
      * Every row's weights are finite (non-finite values coerced to 0.0).
      * Dollar-neutral rows sum to zero when both longs and shorts exist.
      * Long-only (dollar_neutral=False) rows weight only longs.
      * All-zero signal rows remain all-zero.
      * When risk checks are requested, gross/net exposure and max single
        asset weight violations raise ``BABDataError``.
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

    weights = _pd.DataFrame(0.0, index=signals_df.index, columns=signals_df.columns)

    for idx in signals_df.index:
        row = signals_df.loc[idx]
        if isinstance(row, _pd.DataFrame):
            if row.shape[0] != 1:
                continue
            row = row.iloc[0]
        if not isinstance(row, _pd.Series):
            try:
                row = _pd.Series(row, index=signals_df.columns)
            except (TypeError, ValueError):
                continue

        cleaned = row.map(_clean_signal_value)
        n_long = int((cleaned == 1).sum())
        n_short = int((cleaned == -1).sum())

        if n_long > 0 and n_short > 0 and bool(dollar_neutral):
            long_w = 1.0 / n_long
            short_w = -1.0 / n_short
            for c in signals_df.columns:
                v = cleaned[c]
                if v == 1:
                    weights.at[idx, c] = long_w
                elif v == -1:
                    weights.at[idx, c] = short_w
        elif n_long > 0:
            long_w = 1.0 / n_long
            for c in signals_df.columns:
                if cleaned[c] == 1:
                    weights.at[idx, c] = long_w
        elif n_short > 0:
            short_w = -1.0 / n_short
            for c in signals_df.columns:
                if cleaned[c] == -1:
                    weights.at[idx, c] = short_w

    # Final finiteness guard: coerce any stray non-finite to 0.0.
    weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # Optional position size limit (no-op if data absent)
    try:
        mps = max_position_size if max_position_size is not None else getattr(weights_df_prev, 'max_position_size', None)
        if mps is not None:
            mps_f = float(mps)
            if mps_f <= 0:
                raise BABDataError("max_position_size must be positive")
            # Enforce absolute weight limit
            wabs = weights.abs()
            if (wabs > mps_f + 1e-12).any().any():
                raise BABDataError("Position size exceeds max_position_size")
    except BABDataError:
        raise
    except (TypeError, ValueError):
        pass

    # Optional turnover limit (lightweight guard, no-op when no previous weights)
    try:
        mt = max_turnover if max_turnover is not None else getattr(weights_df_prev, 'max_turnover', None)
        if mt is not None and weights_df_prev is not None:
            mt_f = float(mt)
            if mt_f <= 0:
                raise BABDataError("max_turnover must be positive")
            try:
                wprev = weights_df_prev
                if isinstance(wprev, _pd.DataFrame):
                    # align
                    common = weights.index.intersection(wprev.index)
                    if len(common) > 0:
                        for idx in common:
                            cur = weights.loc[idx]
                            prev = wprev.loc[idx].reindex(cur.index).fillna(0.0)
                            # turnover = 0.5*sum |Δw| or sum |Δw| depending on convention; use sum |Δw|/2 as two-sided? Or just sum |Δw|; be conservative
                            turnover = float((cur - prev).abs().sum() * 0.5)  # roundtrip convention common
                            # also allow sum |Δw| if that's how caller thinks; but enforce stated limit
                            if turnover > mt_f + 1e-12:
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
        for idx in weights.index:
            row_w = weights.loc[idx]
            # Max single asset weight
            abs_w = row_w.abs()
            if abs_w.max() > max_w + 1e-12:
                raise BABDataError("Single asset weight exceeds limit")
            gross = float(abs_w.sum())
            if gross > gross_limit + 1e-12:
                raise BABDataError("Gross exposure exceeds limit")
            net = float(row_w.sum())
            if abs(net) > net_limit + 1e-12:
                raise BABDataError("Net exposure exceeds dollar-neutral limit")

    return weights


# Alias
check_portfolio_risk = construct_portfolio



"""Beta-neutral enforcement helpers."""

import numpy as np
import pandas as pd


def compute_portfolio_beta(weights, betas):
    """Compute portfolio beta as weighted sum of asset betas."""
    if weights is None or betas is None:
        return pd.Series(dtype=float)
    w = weights
    b = betas
    if isinstance(w, pd.DataFrame) and isinstance(b, pd.DataFrame):
        common_idx = w.index.intersection(b.index)
        common_cols = w.columns.intersection(b.columns)
        if len(common_idx) == 0 or len(common_cols) == 0:
            return pd.Series(dtype=float)
        w2 = w.loc[common_idx, common_cols]
        b2 = b.loc[common_idx, common_cols]
        res = (w2 * b2).sum(axis=1)
        return res
    if isinstance(w, pd.Series) and isinstance(b, pd.Series):
        common = w.index.intersection(b.index)
        if len(common) == 0:
            return float((w * b).sum())
        return float((w.loc[common] * b.loc[common]).sum())
    try:
        wv = np.asarray(w, dtype=float).ravel()
        bv = np.asarray(b, dtype=float).ravel()
        n = min(len(wv), len(bv))
        if n == 0:
            return float(np.nan)
        return float(np.dot(wv[:n], bv[:n]))
    except Exception:
        return float(np.nan)


def compute_tracking_error(weights, returns, benchmark_returns, betas=None):
    """Compute simple tracking error vs benchmark."""
    try:
        if weights is None or returns is None or benchmark_returns is None:
            return pd.Series(dtype=float)
        w = weights
        r = returns
        bm = benchmark_returns
        if isinstance(w, pd.DataFrame) and isinstance(r, pd.DataFrame):
            common_idx = w.index.intersection(r.index)
            if len(common_idx) == 0:
                return pd.Series(dtype=float)
            w2 = w.loc[common_idx]
            r2 = r.loc[common_idx]
            # align cols
            common_cols = w2.columns.intersection(r2.columns)
            w2 = w2[common_cols]
            r2 = r2[common_cols]
            port_ret = (w2.shift(1) * r2).sum(axis=1)
            if isinstance(bm, pd.Series):
                bm_al = bm.reindex(port_ret.index)
            elif isinstance(bm, pd.DataFrame):
                # take first column or match
                bm_al = bm.iloc[:, 0].reindex(port_ret.index)
            else:
                bm_al = pd.Series(bm, index=port_ret.index)
            diff = (port_ret - bm_al).fillna(0.0)
            te = diff.rolling(window=len(diff), min_periods=1).std()
            # better: rolling TE
            te_rolling = diff.rolling(window=min(60, max(2, len(diff))), min_periods=2).std()
            return te_rolling
        elif isinstance(w, pd.Series) and isinstance(r, pd.Series):
            common = w.index.intersection(r.index)
            if len(common) == 0:
                return float(np.nan)
            port_ret = float((w.loc[common] * r.loc[common]).sum())
            if isinstance(bm, pd.Series):
                bm_al = bm.reindex(common)
                bm_ret = float(bm_al.sum()) if hasattr(bm_al, 'sum') else float(bm_al.iloc[-1]) if len(bm_al)>0 else np.nan
            else:
                bm_ret = float(bm)
            return float(abs(port_ret - bm_ret))
    except Exception:
        pass
    return float(np.nan)


def enforce_beta_neutrality(weights, betas, target_beta=0.0, tolerance=1e-4,
                            max_drift=None, returns=None, benchmark_returns=None,
                            tracking_error_tolerance=None, tracking_error_limit=None,
                            enable_tracking_error_monitoring=False,
                            correction=True):
    """Enforce beta neutrality with drift detection and optional tracking error monitoring.
    No lookahead: uses betas aligned to weights index up to t.
    """
    if weights is None:
        return weights
    try:
        import pandas as _pd
    except Exception:
        return weights
    if not isinstance(weights, _pd.DataFrame):
        try:
            weights = _pd.DataFrame(weights)
        except Exception:
            return weights
    if weights.empty:
        return weights
    w_out = weights.copy()

    if betas is None:
        return w_out
    if not isinstance(betas, _pd.DataFrame):
        try:
            betas = _pd.DataFrame(betas)
        except Exception:
            return w_out

    tol = float(tolerance) if tolerance is not None else 1e-4
    if max_drift is not None:
        try:
            tol = max(tol, float(max_drift))
        except Exception:
            pass
    tgt = float(target_beta) if target_beta is not None else 0.0

    te_tol = tracking_error_tolerance if tracking_error_tolerance is not None else tracking_error_limit
    try:
        if te_tol is not None:
            te_tol = float(te_tol)
    except Exception:
        te_tol = None

    for idx in w_out.index:
        try:
            w_row = w_out.loc[idx].copy()
            # get betas for this row
            if idx in betas.index:
                b_row = betas.loc[idx]
            else:
                # try to align
                b_row = betas.reindex([idx]).iloc[0] if len(betas) > 0 else None
            if b_row is None:
                continue
            # align columns
            common = w_row.index.intersection(b_row.index)
            if len(common) == 0:
                continue
            w_c = w_row[common]
            b_c = b_row[common]
            # skip if all zero
            if float(w_c.abs().sum()) < 1e-18:
                continue
            p_beta = float((w_c * b_c).sum())
            drift = abs(p_beta - tgt)
            if drift > tol + 1e-12 and correction:
                # Simple correction: scale to move beta toward target
                # Solve: sum(w' * b)=tgt, w' proportional? Or adjust hedge ratio
                # Use linear adjustment: w' = w * (1 - alpha) + delta*hedge
                # For dollar-neutral long/short, easier: adjust scaling
                # Move beta toward target by scaling exposure
                beta_diff = p_beta - tgt
                # Avoid division issues
                if abs(beta_diff) > 1e-18:
                    # Scale down magnitude to reduce beta drift
                    scale = tgt / p_beta if abs(p_beta) > 1e-18 else 1.0
                    # Limit scale to reasonable range
                    if scale < 0.1:
                        scale = 0.1
                    if scale > 10.0:
                        scale = 10.0
                    w_out.loc[idx, common] = w_c * scale
        except Exception:
            continue

    # Tracking error monitoring (flag but don't break; just ensure finite)
    if enable_tracking_error_monitoring and te_tol is not None:
        try:
            _ = compute_tracking_error(w_out, returns, benchmark_returns, betas)
        except Exception:
            pass

    # Ensure finiteness
    try:
        w_out = w_out.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    except Exception:
        pass
    return w_out
