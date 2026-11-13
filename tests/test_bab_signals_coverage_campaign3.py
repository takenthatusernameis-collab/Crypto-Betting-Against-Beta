"""Coverage campaign 3 for strategies/betting_against_beta/signals.py.

Targets residual uncovered/defensive paths: quantile coercion/clamping,
all-non-finite fast-path guard, coercion/argsort exception fallbacks,
and non-numeric dtype handling. Production-realistic controlled inputs;
scoped monkeypatches only for defensive branches unreachable via public API.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.signals import (
    _finite_beta_series,
    generate_bab_signals,
)


class TestFiniteBetaSeriesResiduals:
    def test_object_dtype_coerced_to_float64_kept(self):
        # After to_numeric on numeric object values, dtype may remain object;
        # branch at 37 casts to float64. Numeric values (not strings) kept.
        s = pd.Series([1.0, 2.0, np.nan], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert out.dtype == "float64"
        assert set(out.tolist()) == {1.0, 2.0}


class TestQuantileCoercionAndClamping:
    def test_invalid_long_quantile_falls_back(self):
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]})
        out = generate_bab_signals(df, long_quantile="bad", short_quantile=0.3)
        ref = generate_bab_signals(df, long_quantile=0.3, short_quantile=0.3)
        pd.testing.assert_frame_equal(out, ref)

    def test_invalid_short_quantile_falls_back(self):
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]})
        out = generate_bab_signals(df, long_quantile=0.3, short_quantile=object())
        ref = generate_bab_signals(df, long_quantile=0.3, short_quantile=0.3)
        pd.testing.assert_frame_equal(out, ref)

    def test_nonfinite_quantiles_fall_back(self):
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]})
        ref = generate_bab_signals(df, long_quantile=0.3, short_quantile=0.3)
        out = generate_bab_signals(df, long_quantile=np.nan, short_quantile=np.inf)
        pd.testing.assert_frame_equal(out, ref)

    def test_negative_quantiles_clamped_to_zero(self):
        df = pd.DataFrame({"A": [0.1], "B": [0.2], "C": [0.3], "D": [0.4]})
        out = generate_bab_signals(df, long_quantile=-1.0, short_quantile=-0.5)
        assert np.isfinite(out.to_numpy()).all()
        assert (out.to_numpy() == 0).all()

    def test_quantiles_at_or_above_one_clamped(self):
        df = pd.DataFrame({"A": [0.1], "B": [0.2], "C": [0.3], "D": [0.4]})
        out = generate_bab_signals(df, long_quantile=1.0, short_quantile=2.0)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()
        # full quantiles -> overlap resolved, still valid {-1,0,1}
        assert set(np.unique(out.to_numpy())).issubset({-1, 0, 1})

    def test_zero_long_quantile(self):
        df = pd.DataFrame({"A": [0.1], "B": [0.2], "C": [0.3], "D": [0.4]})
        out = generate_bab_signals(df, long_quantile=0.0, short_quantile=0.5)
        assert (out.to_numpy() >= -1).all()
        assert (out.to_numpy() <= 0).all()  # no longs
        assert (out.to_numpy() == -1).any()

    def test_zero_short_quantile(self):
        df = pd.DataFrame({"A": [0.1], "B": [0.2], "C": [0.3], "D": [0.4]})
        out = generate_bab_signals(df, long_quantile=0.5, short_quantile=0.0)
        assert (out.to_numpy() >= 0).all()
        assert (out.to_numpy() <= 1).all()  # no shorts
        assert (out.to_numpy() == 1).any()


class TestAllNonFiniteRowsGuard:
    def test_all_rows_insufficient_finite_returns_zero_frame(self):
        # Every row has < 2 finite values -> valid.any() False path (151-154)
        df = pd.DataFrame(
            {
                "A": [np.nan, np.inf, np.nan],
                "B": [np.nan, np.nan, -np.inf],
                "C": [1.0, np.nan, np.nan],  # only 1 finite per row
            }
        )
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert (out.to_numpy() == 0).all()

    def test_single_column_always_flat(self):
        df = pd.DataFrame({"BTC": [0.5, 0.6, 0.7]})
        out = generate_bab_signals(df)
        assert (out.to_numpy() == 0).all()


class TestNonNumericDtypeHandling:
    def test_object_column_with_mixed_types_coerced(self):
        df = pd.DataFrame(
            {"A": [0.1, "0.2", 0.3, 0.4], "B": [0.5, 0.6, "0.7", 0.8], "C": [0.9, 1.0, 1.1, 1.2]},
            dtype=object,
        )
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()
        assert set(np.unique(out.to_numpy())).issubset({-1, 0, 1})

    def test_non_numeric_string_column_becomes_nan_handled(self):
        df = pd.DataFrame({"A": ["x", "y", "z", "w"], "B": [0.1, 0.2, 0.3, 0.4], "C": [0.5, 0.6, 0.7, 0.8]})
        out = generate_bab_signals(df)
        assert np.isfinite(out.to_numpy()).all()
        # column A all NaN after coercion -> rows have 2 finite (B,C) still valid
        assert out.shape == df.shape


class TestDefensiveExceptionFallbacks:
    def test_to_numeric_outer_failure_falls_back(self, monkeypatch):
        # Force the outer numeric-fast-path try to fail via broken to_numpy;
        # the inner to_numeric fallback then also fails -> zero frame (136-142)
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]})

        class BadDF(pd.DataFrame):
            @property
            def _constructor(self):
                return BadDF

            def to_numpy(self, *a, **k):
                raise RuntimeError("no to_numpy")

        bdf = BadDF(df)
        out = generate_bab_signals(bdf)
        assert out.shape == bdf.shape
        assert (out.to_numpy() == 0).all()

    def test_argsort_failure_uses_fallback_rank(self, monkeypatch):
        # Force np.argsort to raise on first stable call path -> fallback (159-161)
        df = pd.DataFrame(
            {"A": [0.1, 0.5, 0.2], "B": [0.3, 0.1, 0.4], "C": [0.2, 0.3, 0.1], "D": [0.4, 0.2, 0.3]}
        )
        real_argsort = np.argsort
        calls = {"n": 0}

        def flaky_argsort(a, *args, **kwargs):
            calls["n"] += 1
            # Fail on the rank-computing double-argsort with kind="stable" (line 158)
            if kwargs.get("kind") == "stable":
                raise RuntimeError("stable argsort failed")
            return real_argsort(a, *args, **kwargs)

        monkeypatch.setattr(np, "argsort", flaky_argsort)
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()
        assert set(np.unique(out.to_numpy())).issubset({-1, 0, 1})

    def test_copy_failure_in_fallback_still_returns_frame(self, monkeypatch):
        # Outer to_numpy fails and the inner to_numeric fallback also fails ->
        # defensive zero frame instead of propagating the coercion error.
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]})

        class BadDF(pd.DataFrame):
            @property
            def _constructor(self):
                return BadDF

            def to_numpy(self, *a, **k):
                raise RuntimeError("no to_numpy")

        bdf = BadDF(df)
        out = generate_bab_signals(bdf)
        assert out.shape == bdf.shape
        assert (out.to_numpy() == 0).all()
