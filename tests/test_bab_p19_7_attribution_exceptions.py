"""P19-7 Milestone 4: attribution.py exception-handling hardening.

Sites covered (by current live line numbers):
- 85 -- fast-path finite repair failed; fall back to replace+fillna semantics (Class A)

All sites are Class A (intentional total/defensive contracts in attribution sanitization).
Broad catches are retained; each carries an inline P19-7 invariant in attribution.py
and is locked by regression tests here. Observable behavior is unchanged.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.attribution import _finite_sum

# ---------------------------------------------------------------------------
# Site 85 (Class A) -- fast-path finite repair failed -> replace+fillna fallback
# ---------------------------------------------------------------------------


def test_site85_fast_path_finite_repair_fallback(monkeypatch):
    """If to_numpy/finite repair fails, fall back to replace+fillna semantics."""
    values = pd.Series([1.0, 2.0, 3.0])

    # Patch to_numpy to raise
    original_to_numpy = pd.Series.to_numpy

    def patched_to_numpy(self, dtype=None, copy=None, na_value=None):
        raise RuntimeError("to_numpy boom")

    monkeypatch.setattr(pd.Series, "to_numpy", patched_to_numpy)

    # Should not raise; should fall back to replace+fillna path
    result = _finite_sum(values)
    assert isinstance(result, float)
    # Original values sum to 6.0
    assert result == 6.0


def test_site85_happy_path_unchanged():
    """Normal finite values use fast path and return correct sum."""
    values = pd.Series([1.0, 2.0, 3.0])
    result = _finite_sum(values)
    assert result == 6.0


def test_site85_with_inf_fast_path():
    """Fast path handles inf by replacing with 0."""
    values = pd.Series([1.0, float("inf"), 3.0, float("-inf")])
    result = _finite_sum(values)
    # inf and -inf replaced with 0 -> 1.0 + 0 + 3.0 + 0 = 4.0
    assert result == 4.0


def test_site85_with_nan_fast_path():
    """Fast path handles nan by replacing with 0."""
    values = pd.Series([1.0, float("nan"), 3.0])
    result = _finite_sum(values)
    # nan replaced with 0 -> 1.0 + 0 + 3.0 = 4.0
    assert result == 4.0


def test_site85_mixed_nonfinite_fallback(monkeypatch):
    """Fallback path also handles inf/nan correctly."""
    values = pd.Series([1.0, float("inf"), 3.0, float("-inf"), float("nan")])

    # Patch to_numpy to raise
    original_to_numpy = pd.Series.to_numpy

    def patched_to_numpy(self, dtype=None, copy=None, na_value=None):
        raise RuntimeError("to_numpy boom")

    monkeypatch.setattr(pd.Series, "to_numpy", patched_to_numpy)

    result = _finite_sum(values)
    # Fallback: astype -> replace inf/-inf with nan -> fillna(0) -> sum
    # 1.0 + nan + 3.0 + nan + nan -> 1.0 + 0 + 3.0 + 0 + 0 = 4.0
    assert result == 4.0


def test_site85_empty_series():
    """Empty series returns 0.0."""
    values = pd.Series([], dtype=float)
    result = _finite_sum(values)
    assert result == 0.0


def test_site85_all_nan():
    """All nan series returns 0.0."""
    values = pd.Series([float("nan"), float("nan")])
    result = _finite_sum(values)
    assert result == 0.0


def test_site85_list_input():
    """List input works (converted to Series)."""
    values = [1.0, 2.0, 3.0]
    result = _finite_sum(values)
    assert result == 6.0


def test_site85_numpy_array_input():
    """Numpy array input works (converted to Series)."""
    values = np.array([1.0, 2.0, 3.0])
    result = _finite_sum(values)
    assert result == 6.0
