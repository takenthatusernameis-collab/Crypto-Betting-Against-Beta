"""Batch 95: `_drop_metadata_columns` sequential-int inner check (1926-1927).

The sequential-int inner check at 1924-1927 is NOT subsumed by the tight check at
1915-1918. The two predicates use DIFFERENT tolerances:

  1916: np.allclose(diffs, 1.0, rtol=0, atol=1e-9)   # tight
  1925: np.allclose(np.diff(vals[finite]), 1.0)       # default (rtol=1e-05)

A numeric column whose values are integers plus sub-1e-9 noise escapes the tight
check (1916 False) but satisfies the default check (1924/1925 True). This is a
realistic shape: a CSV row-index column written as floats (e.g. by numpy
`arange(..., dtype=float)` plus rounding noise) lands exactly in the tolerance
window between the two `allclose` calls.

The path: `minv <= 0` (1922, first value 0.0) -> `np.allclose(vals[finite],
np.round(vals[finite]))` (1924 True) -> `float(vals[finite][0]) == 0.0` (1925
True) -> `np.allclose(np.diff(vals[finite]), 1.0)` (1925 True) -> drop at 1926,
`continue` at 1927.
"""
import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader as dl


def test_1926_1927_sequential_int_inner_check_tiny_noise():
    # Values: 0, 1+eps, 2+2eps, 3+3eps with eps just above the tight atol.
    # Tight check (1916, atol=1e-9) fails; default check (1924/1925) passes.
    eps = 1e-8
    vals = np.array([0.0, 1.0 + eps, 2.0 + 2 * eps, 3.0 + 3 * eps])
    df = pd.DataFrame({"rowidx": vals, "BTC": [100.0, 101.0, 102.0, 103.0]})
    out = dl._drop_metadata_columns(df.copy())
    assert "rowidx" not in out.columns
    assert "BTC" in out.columns


def test_1926_1927_sequential_int_inner_check_integer_floats():
    # Plain integer-valued floats satisfy the tight check (1916) and are
    # dropped there; this test confirms the deterministic drop path still
    # works for the canonical integer-float shape (row-index artifact).
    vals = np.array([0.0, 1.0, 2.0, 3.0], dtype=float)
    df = pd.DataFrame({"rowidx": vals, "BTC": [100.0, 101.0, 102.0, 103.0]})
    out = dl._drop_metadata_columns(df.copy())
    assert "rowidx" not in out.columns
    assert "BTC" in out.columns