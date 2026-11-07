"""Batch 105 — beta.py branch hardening (production-realistic mechanisms).

Covers the previously-unreached branches in strategies/betting_against_beta/beta.py:
  - calculate_beta: 124 (all-NaN mask -> len 0), 130-131 (bad min_obs int cast),
    149-150 (non-array inputs -> outer except)
  - calculate_beta_fast: 162 (None input), 175-177 (mismatched lengths truncate),
    188 (all-NaN after mask), 195 (bad min_obs int cast -> return NaN),
    215-218 (inner/outer except)

Note: lines 169-170 (np.array(a).ravel() failure) are structurally dead: line 157
`np.asarray(a, dtype=float)` always yields an ndarray that line 167 `np.array(a).ravel()`
never chokes on, so the inner try at 166-170 cannot raise. Verified by probe.

No production semantics changed: all paths return NaN / raise as designed.
"""

from __future__ import annotations

import numpy as np
import pytest

from strategies.betting_against_beta import beta


class TestCalculateBetaResiduals:
    def test_all_nan_inputs_returns_nan(self):
        # mask is all-false -> len(y) == 0 -> line 124
        assert np.isnan(beta.calculate_beta(np.array([np.nan, np.nan]), np.array([np.nan, np.nan])))

    def test_bad_min_obs_int_cast_is_swallowed(self):
        # int("abc") raises -> except Exception: pass -> 130-131; beta still computed
        out = beta.calculate_beta([0.01, 0.02, 0.03], [0.005, 0.01, 0.015], min_obs="abc")
        assert np.isfinite(out)

    def test_non_array_inputs_raise_outer(self):
        # Neither input is array-like -> outer (TypeError,ValueError,AttributeError)
        # at 147-148 -> 149-150
        assert np.isnan(beta.calculate_beta("notarray", "notarray"))


class TestCalculateBetaFastResiduals:
    def test_none_input_returns_nan(self):
        # a is None -> line 162
        assert np.isnan(beta.calculate_beta_fast(None, np.array([1.0, 2.0])))

    def test_mismatched_lengths_truncate(self):
        # len(a) != len(b) -> truncate to min -> 175-177
        out = beta.calculate_beta_fast(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0]))
        assert np.isfinite(out)

    def test_all_nan_after_mask_returns_nan(self):
        # mask all-false -> len(a_m) == 0 -> 188
        assert np.isnan(beta.calculate_beta_fast(np.array([np.nan, np.nan]), np.array([np.nan, np.nan])))

    def test_bad_min_obs_returns_nan(self):
        # int("abc") raises -> except Exception: return np.nan -> 195
        out = beta.calculate_beta_fast(
            np.array([0.01, 0.02, 0.03]), np.array([0.005, 0.01, 0.015]), min_obs="abc"
        )
        assert np.isnan(out)

    def test_singular_fit_returns_nan(self):
        # lstsq singular -> 212-214; outer except -> 215-218
        assert np.isnan(beta.calculate_beta_fast(np.array([1.0, 1.0]), np.array([1.0, 1.0])))