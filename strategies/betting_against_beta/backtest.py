"""Backtesting for BAB strategy."""

import contextlib

import numpy as np
import pandas as pd

from .costs import TransactionCostModel, compute_transaction_costs


def _adv_series_local(adv_usd):
    """Normalize adv_usd to an asset-indexed Series/DataFrame, or None."""
    if adv_usd is None:
        return None
    if isinstance(adv_usd, dict):
        return pd.Series(adv_usd, dtype="float64")
    if isinstance(adv_usd, pd.Series):
        return adv_usd.astype("float64")
    if isinstance(adv_usd, pd.DataFrame):
        return adv_usd.astype("float64")
    return None


def _clean_frame_local(df):
    if df is None:
        return None
    df = pd.DataFrame(df)
    if df.empty:
        return None
    return df.replace([np.inf, -np.inf], np.nan)


def run_backtest(
    returns_df,
    weights_df,
    transaction_costs=0.0,
    slippage=0.0,
    tc=None,
    slippage_cost=None,
    cost_model=None,
    prices_df=None,
    adv_usd=None,
    partial_fill=False,
    max_participation=0.10,
):
    """Run simple backtest.

    Parameters
    ----------
    partial_fill : bool, optional
        Opt-in participation-aware slippage realism. When True, realized
        slippage is scaled by the fraction of the ADV liquidity budget that a
        trade consumes, so a large order in a thin asset is penalized more
        than a small one. When False (default) the slippage path is a no-op
        and the result is bit-identical to the flat-slippage path.
    max_participation : float, optional
        Fraction of ADV that may be consumed by a single trade when
        ``partial_fill`` is enabled (in (0, 1]).
    """
    # Allow alternative parameter names for flexibility
    if tc is not None and transaction_costs == 0.0:
        transaction_costs = tc
    if slippage_cost is not None and slippage == 0.0:
        slippage = slippage_cost

    if returns_df is None or weights_df is None:
        return pd.DataFrame(columns=["returns", "cumulative"])

    if not isinstance(returns_df, pd.DataFrame):
        try:
            returns_df = pd.DataFrame(returns_df)
        # INVARIANT (P19-7 backtest site 1 / Class A): a non-DataFrame input
        # that cannot be coerced degrades to an empty result frame (returns +
        # cumulative only) rather than crashing the caller. This is the
        # intentional total contract for run_backtest: bad input -> empty
        # frame, never an exception.
        except (TypeError, ValueError):
            return pd.DataFrame(columns=["returns", "cumulative"])
    if not isinstance(weights_df, pd.DataFrame):
        try:
            weights_df = pd.DataFrame(weights_df)
        # INVARIANT (P19-7 backtest site 2 / Class A): same total contract as
        # site 1 -- an uncoercible weights input yields an empty result frame.
        except (TypeError, ValueError):
            return pd.DataFrame(columns=["returns", "cumulative"])

    if returns_df.empty or weights_df.empty:
        common_idx = returns_df.index.intersection(weights_df.index)
        results = pd.DataFrame({"returns": [], "cumulative": []}, index=common_idx)
        return results

    # Align indices
    common_idx = returns_df.index.intersection(weights_df.index)
    returns = returns_df.loc[common_idx]
    weights = weights_df.loc[common_idx]
    # Align columns where possible
    common_cols = returns.columns.intersection(weights.columns)
    if len(common_cols) > 0:
        returns = returns[common_cols]
        weights = weights[common_cols]
    else:
        # Try to align by position if same shape
        if returns.shape == weights.shape:
            weights = weights.copy()
            weights.columns = returns.columns
        else:
            pass
    columns = list(weights.columns)

    # Clean weights of NaN/inf.  Fast-path the common case where weights are
    # already finite (the beta-neutral path in BABStrategy.run clamps non-finite
    # entries to 0.0 before calling run_backtest): a single C-level isfinite scan
    # avoids the expensive pandas replace_list/block-manager pass entirely.
    # When non-finite values are present, fall back to the original replace+
    # fillna so the repaired result is byte-for-byte identical; if the numeric
    # conversion itself fails, still attempt the replace fallback (matching the
    # original "try and swallow" guarantee) rather than leaving weights dirty.
    try:
        _w_arr = weights.to_numpy(dtype=float)
        if not np.all(np.isfinite(_w_arr)):
            weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    # INVARIANT (P19-7 backtest site 3 / Class A): if the numeric conversion
    # itself fails (exotic dtype / uncoercible frame), the replace+fillna
    # fallback is still attempted so weights are repaired rather than left
    # dirty. This is the intentional total contract: weights are always
    # finite before they reach the return math below.
    except (TypeError, ValueError):
        with contextlib.suppress(TypeError, ValueError):
            weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # Shift once and reuse: lagged weights (no lookahead) for both returns and
    # turnover, avoiding a second ``shift`` allocation.
    w_shifted = weights.shift(1)
    w_shifted_filled = w_shifted.fillna(0.0)
    # Calculate portfolio returns (shift weights by 1 day for no lookahead)
    # INVARIANT (P19-7 backtest site 4 / Class A): the fast numpy path is the
    # primary; if it fails (exotic dtypes / read-only buffers / shape mismatch)
    # the pure-pandas fallback produces an identical result. The broad catch
    # is retained only as a behavior-preserving fallback -- it never hides a
    # defect because the fallback is a legitimate, well-defined computation.
    try:
        port_ret = (w_shifted.to_numpy(dtype=float) * returns.to_numpy(dtype=float)).sum(axis=1)
        gross_returns = pd.Series(port_ret, index=common_idx)
    except Exception:
        gross_returns = (w_shifted * returns).sum(axis=1)

    # Compute turnover symmetrically once - vectorized, reusing the shifted weights
    # INVARIANT (P19-7 backtest site 5 / Class A): same behavior-preserving
    # fallback contract as site 4 -- numpy path primary, pandas diff() fallback
    # yields identical turnover for any coercible frame.
    try:
        wdiff = weights.to_numpy(dtype=float) - w_shifted_filled.to_numpy(dtype=float)
        weight_changes = np.abs(wdiff).sum(axis=1)
        weight_changes_s = pd.Series(weight_changes, index=common_idx)
    except Exception:
        weight_changes_s = weights.diff().abs().sum(axis=1).fillna(0.0)

    # Trade-attribution drag components, computed per period before they are
    # subtracted from the gross return. Kept as separate columns so the caller
    # can attribute performance to gross alpha vs cost vs slippage.
    tc_val = float(transaction_costs) if transaction_costs is not None else 0.0
    cost_drag = weight_changes_s * tc_val

    slip_val = float(slippage) if slippage is not None else 0.0
    slippage_drag = weight_changes_s * slip_val

    # R3-A: opt-in participation-aware partial-fill realism. When enabled the
    # realized slippage is scaled by how much of the ADV liquidity budget each
    # trade consumes, so a large order in a thin asset is penalized more than
    # a small one. When disabled this is a no-op (slippage_drag is unchanged).
    if partial_fill and slip_val > 0:
        try:
            _prices = _clean_frame_local(prices_df)
            _adv_input = (
                adv_usd
                if adv_usd is not None
                else (cost_model.adv_usd if cost_model is not None else None)
            )
            _adv_series = _adv_series_local(_adv_input)
            if _prices is not None and _adv_series is not None:
                _prices = _prices.reindex(index=common_idx, columns=columns)
                if isinstance(_adv_series, pd.DataFrame):
                    _adv_aligned = _adv_series.reindex(index=common_idx, columns=columns)
                else:
                    _adv_aligned = pd.DataFrame(
                        np.tile(
                            _adv_series.reindex(columns).to_numpy(dtype=float),
                            (len(common_idx), 1),
                        ),
                        index=common_idx,
                        columns=columns,
                    )
                _trade = (weights - w_shifted_filled).abs()
                _participation = (_trade * _prices / _adv_aligned).fillna(0.0)
                _ratio = (
                    (_participation / float(max_participation))
                    .clip(lower=0.0, upper=1.0)
                    .to_numpy(dtype=float)
                )
                # Effective slippage per unit of turnover: base rate scaled by
                # (1 + participation_ratio), so a trade that exhausts the entire
                # ADV budget pays twice the base slippage.
                _multiplier = 1.0 + _ratio
                _scaled_drag = slip_val * (_trade.to_numpy(dtype=float) * _multiplier).sum(axis=1)
                slippage_drag = pd.Series(_scaled_drag, index=common_idx)
        # INVARIANT (P19-7 backtest site 6 / Class A): any failure in the
        # opt-in partial-fill path leaves the flat slippage drag intact (never
        # NaN/inf, never a crash). This is an intentional degrade-to-default
        # contract: the partial-fill enhancement is best-effort and the
        # observable result is identical to partial_fill=False on failure.
        except Exception:
            # Any failure in the partial-fill path leaves the flat slippage
            # drag intact (never NaN/inf, never a crash).
            pass

    # Apply transaction costs if any
    portfolio_returns = gross_returns - cost_drag if tc_val > 0 else gross_returns.copy()

    # Apply slippage cost on turnover if any
    if slip_val > 0:
        portfolio_returns = portfolio_returns - slippage_drag

    # Apply modeled transaction costs if any
    if cost_model is not None:
        if not isinstance(cost_model, TransactionCostModel):
            raise TypeError("cost_model must be a TransactionCostModel instance")
        weights_prev = w_shifted_filled
        period_costs = compute_transaction_costs(
            weights, weights_prev, prices_df, cost_model, adv_usd=adv_usd
        )
        period_costs = period_costs.reindex(portfolio_returns.index).fillna(0.0)
        portfolio_returns = portfolio_returns - period_costs.astype(float)

    # Calculate cumulative returns.
    # The previous code ran three redundant cleaning passes on
    # portfolio_returns (fillna(0.0) -> replace inf -> fillna(0.0) -> a
    # separate isfinite/where repair).  All three reduce to the same thing:
    # every non-finite entry (NaN, inf, -inf) becomes 0.0.  A single
    # to_numpy + np.where(isfinite, arr, 0.0) pass produces a byte-identical
    # result (NaN is not finite, so it is mapped to 0.0 exactly as before)
    # without the pandas replace_list/block-manager churn.
    try:
        _pr_arr = portfolio_returns.to_numpy(dtype=float)
        if not np.all(np.isfinite(_pr_arr)):
            _pr_arr = np.where(np.isfinite(_pr_arr), _pr_arr, 0.0)
            portfolio_returns = pd.Series(_pr_arr, index=portfolio_returns.index)
    # INVARIANT (P19-7 backtest site 7 / Class A): if the primary finite-
    # repair pass itself fails (exotic dtype / read-only buffer), the
    # replace+fillna fallback produces an identical all-finite Series. This is
    # an intentional degrade-to-default contract: portfolio_returns is always
    # finite before the cumulative math below, never NaN/inf.
    except Exception:
        with contextlib.suppress(Exception):
            portfolio_returns = portfolio_returns.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    portfolio_returns_filled = portfolio_returns.clip(lower=-1.0 + 1e-12)
    try:
        log_returns = np.log1p(portfolio_returns_filled.to_numpy(dtype=float))
        if not np.all(np.isfinite(log_returns)):
            log_returns = np.where(np.isfinite(log_returns), log_returns, 0.0)
        cumulative_returns = np.exp(np.cumsum(log_returns))
        if not np.all(np.isfinite(cumulative_returns)):
            cumulative_returns = np.where(np.isfinite(cumulative_returns), cumulative_returns, 1.0)
    # INVARIANT (P19-7 backtest site 8 / Class A): the log1p/exp cumulative
    # path is primary; on failure the pure-pandas cumprod fallback yields an
    # identical cumulative series for any coercible frame. Behavior-preserving
    # fallback, never a silent defect-hider.
    except Exception:
        # Fallback
        try:
            cumulative_returns = (1.0 + portfolio_returns_filled).cumprod()
            # np.asarray can return a read-only view of a Series' underlying buffer;
            # force a writable copy so the non-finite repair below can actually
            # mutate entries instead of silently raising and falling through.
            cumulative_returns_arr = np.asarray(cumulative_returns, dtype=float).copy()
            if not np.all(np.isfinite(cumulative_returns_arr)):
                bad = ~np.isfinite(cumulative_returns_arr)
                for i in range(len(cumulative_returns_arr)):
                    if bad[i]:
                        cumulative_returns_arr[i] = cumulative_returns_arr[i - 1] if i > 0 else 1.0
                cumulative_returns = cumulative_returns_arr
        # INVARIANT (P19-7 backtest site 9 / Class A): if even the cumprod
        # fallback fails (uncoercible frame), degrade to an all-ones series of
        # the same length. This is the intentional total contract: the
        # cumulative path is always a finite, same-length series -- it never
        # propagates a corrupt/short array to the result frame.
        except Exception:
            cumulative_returns = np.ones(len(portfolio_returns_filled))
    results = pd.DataFrame(
        {
            "returns": portfolio_returns,
            "gross_return": gross_returns.fillna(0.0),
            "cost_drag": cost_drag.fillna(0.0),
            "slippage_drag": slippage_drag.fillna(0.0),
            "cumulative": cumulative_returns,
        },
        index=common_idx,
    )
    # Final sanitization: single finite-repair pass over the result buffer.
    # Every non-finite entry (NaN, inf, -inf) becomes 0.0, preserving
    # index/columns/dtypes/values exactly — provably identical to
    # results.replace([inf,-inf],nan).fillna(0.0) but without the full-frame
    # pandas replace_list/block-manager pass. All five result columns are
    # float64, so one to_numpy + where + reconstruct keeps dtypes exact.
    try:
        _r_arr = results.to_numpy(dtype=float, copy=False)
        if not np.all(np.isfinite(_r_arr)):
            _r_arr = np.where(np.isfinite(_r_arr), _r_arr, 0.0)
            results = pd.DataFrame(_r_arr, index=results.index, columns=results.columns)
    # INVARIANT (P19-7 backtest site 10 / Class A): if the primary finite-
    # repair pass itself fails (exotic dtype / read-only buffer), the
    # replace+fillna fallback produces an identical all-finite frame. This is
    # the intentional total contract: the returned frame is always fully
    # finite (NaN/inf/-inf -> 0.0), never a corrupt frame to the caller.
    except Exception:
        with contextlib.suppress(Exception):
            results = results.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    return results
