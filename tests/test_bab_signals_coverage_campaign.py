"""Coverage campaign for strategies/betting_against_beta/signals.py.

Real-behavior tests (no vacuous mocks) targeting the uncovered signal-generation
paths: string/NaN handling in ``_finite_beta_series``, reference single-asset
and no-finite skips, vectorized ranking/quantiles, object-column coercion, and
the defensive coercion/argsort fallbacks in ``generate_bab_signals``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.signals import (
    _finite_beta_series,
    _reference_generate_bab_signals,
    generate_bab_signals,
)


class TestFiniteBetaSeriesStringPath:
    """_finite_beta_series: object-dtype string entries must be zeroed to NaN
    (str_mask branch) so numeric-looking strings such as "1.5" are rejected."""

    def test_numeric_string_entries_zeroed_to_nan_keeps_real_numbers(self):
        # "1.5" is a str entry -> zeroed to NaN; 2.0 is real -> kept.
        s = pd.Series(["1.5", 2.0, "garbage"], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert list(out.index) == [1]
        assert abs(float(out.iloc[0]) - 2.0) < 1e-12

    def test_all_string_entries_become_nan_returns_none(self):
        s = pd.Series(["1.5", "2.0", "garbage"], dtype=object)
        assert _finite_beta_series(s) is None

    def test_mixed_numeric_and_strings_keeps_only_finite_numbers(self):
        s = pd.Series([np.nan, "1.5", 3.0, -1.0, np.inf], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert sorted(out.index.tolist()) == [2, 3]
        assert set(out.tolist()) == {3.0, -1.0}

    def test_single_row_dataframe_extracts_series(self):
        # Line 26-28: betas = betas.iloc[0] for a 1-row DataFrame.
        df = pd.DataFrame([[0.5]], columns=["A"])
        out = _finite_beta_series(df)
        assert out is not None
        assert float(out.iloc[0]) == 0.5

    def test_multi_row_dataframe_returns_none(self):
        assert _finite_beta_series(pd.DataFrame({"a": [1.0, 2.0]})) is None

    def test_non_series_returns_none(self):
        assert _finite_beta_series([1.0, 2.0]) is None
        assert _finite_beta_series(1.0) is None

    def test_all_non_finite_returns_none(self):
        assert _finite_beta_series(pd.Series([np.inf, -np.inf, np.nan])) is None

    def test_empty_series_returns_none(self):
        assert _finite_beta_series(pd.Series([], dtype=float)) is None


class TestReferenceGenerateBabSignals:
    def test_none_and_empty_return_empty_frame(self):
        assert _reference_generate_bab_signals(None).empty
        assert _reference_generate_bab_signals(pd.DataFrame()).empty

    def test_single_asset_row_stays_flat(self):
        df = pd.DataFrame({"BTC": [0.5, 0.6, 0.7]}, index=range(3))
        out = _reference_generate_bab_signals(df)
        assert (out.values == 0).all()

    def test_no_finite_betas_row_stays_flat(self):
        out = _reference_generate_bab_signals(pd.DataFrame([[np.nan, np.nan]], columns=["A", "B"]))
        assert (out.iloc[0] == 0).all()

    def test_overlap_shrink_disjoint_quantiles(self):
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]}, index=range(2))
        out = _reference_generate_bab_signals(df, long_quantile=0.9, short_quantile=0.9)
        assert out.shape == df.shape
        assert np.isfinite(out.values).all()


class TestGenerateBabSignalsRealBehavior:
    def test_none_and_empty_return_empty_frame(self):
        assert generate_bab_signals(None).empty
        assert generate_bab_signals(pd.DataFrame()).empty

    def test_all_zero_input_returns_finite_frame_same_shape(self):
        # All-zero betas: every row is valid (>=2 finite) and ranked; output
        # keeps shape and finiteness (no crash on uniform values).
        df = pd.DataFrame({"A": [0.0, 0.0], "B": [0.0, 0.0]}, index=range(2))
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()

    def test_nan_rows_stay_flat_no_crash(self):
        df = pd.DataFrame({"A": [np.nan, 0.5], "B": [0.4, np.nan]}, index=range(2))
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()
        # Row 0 has only one finite beta -> flat.
        assert (out.iloc[0] == 0).all()

    def test_vectorized_matches_reference_on_random_input(self):
        rng = np.random.default_rng(11)
        betas = pd.DataFrame(rng.normal(1.0, 0.5, size=(30, 6)))
        vec = generate_bab_signals(betas)
        ref = _reference_generate_bab_signals(betas)
        pd.testing.assert_frame_equal(vec, ref)
        assert np.all(np.isfinite(vec.to_numpy()))

    def test_vectorized_matches_reference_with_nan_and_strings(self):
        rng = np.random.default_rng(12)
        betas = pd.DataFrame(rng.normal(1.0, 0.5, size=(20, 4)))
        betas.iloc[3, 1] = np.nan
        betas.iloc[5, 2] = np.inf
        # Insert object column with a numeric-looking string (rejected) and a real number.
        betas["C"] = ["1.5", 2.0, np.nan, 0.5] + [0.1] * 16
        vec = generate_bab_signals(betas)
        ref = _reference_generate_bab_signals(betas)
        pd.testing.assert_frame_equal(vec, ref)
        assert np.all(np.isfinite(vec.to_numpy()))

    def test_single_asset_row_flat(self):
        df = pd.DataFrame({"BTC": [0.5, 0.6, 0.7]}, index=range(3))
        out = generate_bab_signals(df)
        assert (out.values == 0).all()

    def test_quantile_clamping_out_of_range(self):
        df = pd.DataFrame({"A": [0.1, 0.2, 0.3], "B": [0.3, 0.2, 0.1]}, index=range(3))
        out = generate_bab_signals(df, long_quantile=5.0, short_quantile=-2.0)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()

    def test_quantile_zero_produces_no_positions(self):
        df = pd.DataFrame({"A": [0.1, 0.2, 0.3, 0.4], "B": [0.4, 0.3, 0.2, 0.1]}, index=range(4))
        out = generate_bab_signals(df, long_quantile=0.0, short_quantile=0.0)
        assert (out.values == 0).all()

    def test_non_numeric_column_coerced_object_path(self):
        # Non-numeric-dtype frame -> object-column coercion path (line 131-135).
        df = pd.DataFrame({"A": [0.1, 0.2], "B": ["0.3", "0.4"]}, index=range(2), dtype=object)
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()

    def test_ranking_long_low_beta_short_high_beta(self):
        # Long = lowest betas, short = highest betas. n=4, quantile 0.5 ->
        # n_long=2, n_short=2. Long=A(0.1),D(0.2); Short=C(0.9),B(0.5).
        df = pd.DataFrame(
            {"A": [0.1, 0.1], "B": [0.5, 0.5], "C": [0.9, 0.9], "D": [0.2, 0.2]},
            index=range(2),
        )
        out = generate_bab_signals(df, long_quantile=0.5, short_quantile=0.5)
        assert out.loc[0, "A"] == 1
        assert out.loc[0, "D"] == 1
        assert out.loc[0, "B"] == -1
        assert out.loc[0, "C"] == -1
