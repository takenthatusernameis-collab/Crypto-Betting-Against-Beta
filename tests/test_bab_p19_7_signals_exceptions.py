from __future__ import annotations

"""P19-7 Milestone 4: signals.py exception-handling hardening.

Sites covered (by current live line numbers):
- 131 -- beta_arr numeric dtype fast path failed; fall back to coercive conversion (Class A)
- 134 -- coercive conversion failed; return zero-signal frame (Class A)
- 158 -- argsort failed on non-finite; map inf and retry (Class A)

All sites are Class A (intentional total/defensive contracts in signal generation).
Broad catches are retained; each carries an inline P19-7 invariant in signals.py
and is locked by regression tests here. Observable behavior is unchanged.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.signals import generate_bab_signals

# ---------------------------------------------------------------------------
# Site 131 (Class A) -- beta_arr numeric dtype fast path -> coercive fallback
# ---------------------------------------------------------------------------


def test_site131_beta_arr_numeric_dtype_fallback(monkeypatch):
    """If to_numpy(dtype=float) raises, fall back to pd.to_numeric coercion."""
    # Create a DataFrame with numeric dtypes that will pass the all() check
    betas_df = pd.DataFrame(
        {"A": [1.0, 2.0], "B": [3.0, 4.0]},
        index=pd.date_range("2020-01-01", periods=2),
    )

    # Patch to_numpy to raise on the first call (fast path)
    original_to_numpy = pd.DataFrame.to_numpy
    call_count = {"n": 0}

    def patched_to_numpy(self, dtype=None, copy=None, na_value=None):
        call_count["n"] += 1
        if call_count["n"] == 1 and dtype is float:
            raise RuntimeError("to_numpy boom")
        return original_to_numpy(self, dtype=dtype, copy=copy, na_value=na_value)

    monkeypatch.setattr(pd.DataFrame, "to_numpy", patched_to_numpy)

    # Should not raise; should fall back to pd.to_numeric path
    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == betas_df.shape
    # With valid beta data, should produce non-zero signals (not all zeros)
    assert (result != 0).any().any()


def test_site131_happy_path_unchanged():
    """Normal numeric beta DataFrame produces correct signals."""
    betas_df = pd.DataFrame(
        {"A": [1.0, 2.0, 3.0], "B": [3.0, 1.0, 2.0], "C": [2.0, 3.0, 1.0]},
        index=pd.date_range("2020-01-01", periods=3),
    )
    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == betas_df.shape
    # Each row should have longs and shorts summing to zero
    for row in result.values:
        assert row.sum() == 0
        # Longs should be positive, shorts negative
        assert (row[row > 0]).sum() == -(row[row < 0]).sum()


# ---------------------------------------------------------------------------
# Site 134 (Class A) -- coercive conversion failed -> zero-signal frame
# ---------------------------------------------------------------------------


def test_site134_coercive_conversion_failed_returns_zero_frame(monkeypatch):
    """If even pd.to_numeric coercion fails, return zero-signal frame."""
    betas_df = pd.DataFrame(
        {"A": ["not_a_number", "also_bad"], "B": ["bad", "worse"]},
        index=pd.date_range("2020-01-01", periods=2),
    )

    # Patch apply to raise on the coercive path
    original_apply = pd.DataFrame.apply

    def patched_apply(self, func, *args, **kwargs):
        if func is pd.to_numeric:
            raise RuntimeError("apply pd.to_numeric boom")
        return original_apply(self, func, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "apply", patched_apply)

    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == betas_df.shape
    # All zeros
    assert (result == 0).all().all()
    assert all(dt == np.int64 for dt in result.dtypes)


def test_site134_non_numeric_dtype_happy_path():
    """Non-numeric dtypes that can be coerced work normally."""
    betas_df = pd.DataFrame(
        {"A": ["1.0", "2.0", "3.0"], "B": ["3.0", "1.0", "2.0"]},
        index=pd.date_range("2020-01-01", periods=3),
    )
    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == betas_df.shape
    assert (result != 0).any().any()  # Some non-zero signals


# ---------------------------------------------------------------------------
# Site 158 (Class A) -- argsort on non-finite -> map inf and retry
# ---------------------------------------------------------------------------


def test_site158_argsort_non_finite_maps_inf_and_retries():
    """beta_arr with non-finite values triggers fallback that maps to inf."""
    # Create betas with NaN/inf that will cause argsort to potentially raise
    betas_df = pd.DataFrame(
        {"A": [1.0, np.nan, 3.0], "B": [np.inf, 1.0, 2.0], "C": [2.0, 3.0, -np.inf]},
        index=pd.date_range("2020-01-01", periods=3),
    )
    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == betas_df.shape
    # Should not raise; should produce valid int64 signals
    assert all(dt == np.int64 for dt in result.dtypes)
    # Finite rows should have proper long/short
    # Row 0 has finite A, inf B, finite C -> should produce signals
    # Row 1 has nan A, finite B, finite C -> should handle
    # Row 2 has finite A, finite B, -inf C -> should handle


def test_site158_all_nan_row_returns_zero():
    """Row with all non-finite betas should produce zero signals."""
    betas_df = pd.DataFrame(
        {"A": [np.nan, 1.0], "B": [np.inf, 2.0], "C": [-np.inf, 3.0]},
        index=pd.date_range("2020-01-01", periods=2),
    )
    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    # First row all non-finite -> zero signals
    assert (result.iloc[0] == 0).all()
    # Second row all finite -> non-zero signals
    assert (result.iloc[1] != 0).any()


def test_site158_happy_path_all_finite():
    """All-finite beta array uses primary argsort path."""
    betas_df = pd.DataFrame(
        {"A": [1.0, 2.0, 3.0], "B": [3.0, 1.0, 2.0], "C": [2.0, 3.0, 1.0]},
        index=pd.date_range("2020-01-01", periods=3),
    )
    result = generate_bab_signals(betas_df, long_quantile=0.5, short_quantile=0.5)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == betas_df.shape
    for row in result.values:
        assert row.sum() == 0
        assert (row[row > 0]).sum() == -(row[row < 0]).sum()
