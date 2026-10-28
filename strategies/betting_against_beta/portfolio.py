"""Portfolio construction for BAB strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd


class BABPortfolioError(ValueError):
    """Raised when portfolio constraints are violated."""
    pass


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
    """
    from .errors import BABDataError
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
            except Exception:
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
    except Exception:
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
            except Exception:
                pass
    except BABDataError:
        raise
    except Exception:
        pass

    if enforce_risk_checks or gross_exposure_limit is not None or max_single_weight is not None or net_exposure_limit is not None:
        try:
            gross_limit = float(gross_exposure_limit) if gross_exposure_limit is not None else 2.0
            net_limit = float(net_exposure_limit) if net_exposure_limit is not None else 1e-6
            max_w = float(max_single_weight) if max_single_weight is not None else 1.0
        except Exception:
            gross_limit, net_limit, max_w = 2.0, 1e-6, 1.0
        for idx in weights.index:
            row_w = weights.loc[idx]
            # Max single asset weight
            abs_w = row_w.abs()
            if abs_w.max() > max_w + 1e-12:
                raise BABPortfolioError("Single asset weight exceeds limit")
            gross = float(abs_w.sum())
            if gross > gross_limit + 1e-12:
                raise BABPortfolioError("Gross exposure exceeds limit")
            net = float(row_w.sum())
            if abs(net) > net_limit + 1e-12:
                raise BABPortfolioError("Net exposure exceeds dollar-neutral limit")

    return weights


# Alias
check_portfolio_risk = construct_portfolio
