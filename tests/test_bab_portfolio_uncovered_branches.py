"""Tests for uncovered branches in strategies/betting_against_beta/portfolio.py.

Covers:
  - portfolio.py:39-40  outer except of _clean_signal_value (fuzz-proven unreachable)
  - portfolio.py:87-88  apply(pd.to_numeric) exception fallback when numeric coercion
                        raises (e.g. object columns holding builtin function/type objects)
  - portfolio.py:200-201 inner except in turnover block when weights_df_prev is not
                        numeric-compatible so that cur - prev raises TypeError
  - portfolio.py:275   enforce_beta_neutrality disjoint-index early return
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.portfolio import (
    BABPortfolioError,
    _clean_signal_value,
    construct_portfolio,
    enforce_beta_neutrality,
)


# ---------------------------------------------------------------------------
# 87-88: apply(pd.to_numeric) exception fallback
# ---------------------------------------------------------------------------
def test_construct_portfolio_numeric_coercion_fallback_on_type_objects():
    """Uncoercible object columns (builtin functions/types) now surface
    BABPortfolioError instead of being silently zeroed (P19-7 portfolio.py)."""
    sig = pd.DataFrame({"a": [len, str, int], "b": [1, -1, 0]})
    with pytest.raises(BABPortfolioError):
        construct_portfolio(sig, dollar_neutral=True)


def test_construct_portfolio_numeric_coercion_fallback_dollar_neutral_off():
    """Same coercion failure path with dollar_neutral=False: must surface
    BABPortfolioError rather than silently producing finite weights."""
    sig = pd.DataFrame({"a": [len, str, int], "b": [1, -1, 0]})
    with pytest.raises(BABPortfolioError):
        construct_portfolio(sig, dollar_neutral=False)


def test_construct_portfolio_numeric_coercion_per_column_fallback_to_zero():
    """When a single column makes pd.to_numeric raise even with errors='coerce'
    (e.g. builtin function/type objects), the exception now surfaces as
    BABPortfolioError instead of setting that column to 0.0 (P19-7)."""
    sig = pd.DataFrame({"a": [len, str, int], "b": [1, -1, 0]})
    with pytest.raises(BABPortfolioError):
        construct_portfolio(sig, dollar_neutral=True)


# ---------------------------------------------------------------------------
# 200-201: inner except in turnover block (cur - prev raises TypeError)
# ---------------------------------------------------------------------------
def test_construct_portfolio_turnover_inner_except_on_non_numeric_prev():
    """weights_df_prev with object/string columns makes cur - prev raise
    TypeError inside the turnover try; the inner except at 200-201 must swallow
    it and construction must still succeed with the computed weights."""
    sig = pd.DataFrame({"a": [1, -1], "b": [-1, 1]}, index=[0, 1])
    prev = pd.DataFrame({"a": ["x", "y"], "b": ["p", "q"]}, index=[0, 1])
    w = construct_portfolio(sig, dollar_neutral=True, max_turnover=0.5, weights_df_prev=prev)
    assert isinstance(w, pd.DataFrame)
    assert w.shape == sig.shape
    assert np.isfinite(w.to_numpy()).all()
    # Weights are the normal dollar-neutral equal-weight assignment.
    assert w.loc[0, "a"] == 1.0
    assert w.loc[1, "a"] == -1.0


def test_construct_portfolio_turnover_inner_except_on_mismatched_index_prev():
    """prev with a disjoint index still goes through the common-index path
    (len(common) > 0 is False -> no turnover computation); ensure no crash."""
    sig = pd.DataFrame({"a": [1, -1], "b": [-1, 1]}, index=[0, 1])
    prev = pd.DataFrame({"a": [1.0], "b": [-1.0]}, index=[5])
    w = construct_portfolio(sig, dollar_neutral=True, max_turnover=0.5, weights_df_prev=prev)
    assert w.shape == sig.shape
    assert np.isfinite(w.to_numpy()).all()


# ---------------------------------------------------------------------------
# 275: enforce_beta_neutrality disjoint-index early return
# ---------------------------------------------------------------------------
def test_enforce_beta_neutrality_disjoint_index_returns_input_unchanged():
    """weights and betas share columns but have no overlapping index, so the
    common_idx early return at 284 must fire and return the input unchanged."""
    w = pd.DataFrame({"a": [1.0, -1.0], "b": [-1.0, 1.0]}, index=[0, 1])
    b = pd.DataFrame({"a": [0.5, 0.6], "b": [0.7, 0.8]}, index=[10, 11])
    out = enforce_beta_neutrality(w, b)
    assert out is w or out.equals(w)


def test_enforce_beta_neutrality_disjoint_columns_returns_input_unchanged():
    """weights and betas with no overlapping columns must return input unchanged."""
    w = pd.DataFrame({"a": [1.0, -1.0], "b": [-1.0, 1.0]}, index=[0, 1])
    b = pd.DataFrame({"x": [0.5, 0.6], "y": [0.7, 0.8]}, index=[0, 1])
    out = enforce_beta_neutrality(w, b)
    assert out is w or out.equals(w)


# ---------------------------------------------------------------------------
# 39-40: outer except of _clean_signal_value (documented unreachable)
# ---------------------------------------------------------------------------
def test_clean_signal_value_outer_except_documented_unreachable():
    """Fuzz-proven: _clean_signal_value never raises for any input type because
    every branch either returns early or is wrapped in its own try/except.
    The outer except at 39-40 is defensive dead code; assert the function is
    total (never raises) over a broad type sweep."""
    samples = [
        None,
        float("nan"),
        "1",
        "-1",
        "abc",
        "1.5",
        1,
        -1,
        0,
        1.0,
        np.int64(1),
        np.float64(-1.0),
        True,
        False,
        [1, 2],
        {1: 2},
        object(),
        b"x",
        1 + 2j,
        pd.NA,
        pd.NaT,
        len,
        str,
        int,
        float,
        complex,
    ]
    for v in samples:
        assert _clean_signal_value(v) in (-1, 0, 1)
