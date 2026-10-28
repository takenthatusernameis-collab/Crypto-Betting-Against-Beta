"""TDD tests for messy-data coercion in validate_returns_dataframe.

These tests encode the contract: mixed dtypes, strings, NaN/inf, object
columns, and partial/leading/trailing NaNs must coerce to numeric safely and
raise BABDataError loudly for genuinely invalid input. No silent coercion to
zero.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    validate_returns_dataframe,
)


def _base_df():
    dates = pd.date_range("2023-01-01", periods=10)
    return pd.DataFrame(
        {
            "BTC": np.linspace(0.001, 0.002, 10),
            "ETH": np.linspace(0.002, 0.003, 10),
        },
        index=dates,
    )


class TestMixedDtypeCoercion:
    def test_string_numeric_column_coerces(self):
        df = _base_df()
        df["ETH"] = ["0.001"] * 10
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert np.issubdtype(out["ETH"].dtype, np.number)
        assert np.isfinite(out["ETH"].to_numpy()).all()

    def test_object_column_with_mixed_numbers_coerces(self):
        df = _base_df()
        df["ETH"] = [0.001, "0.002", 0.003, "0.004", 0.005, "0.006", 0.007, "0.008", 0.009, "0.010"]
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert np.issubdtype(out["ETH"].dtype, np.number)

    def test_garbage_string_column_raises(self):
        df = _base_df()
        df["ETH"] = ["abc"] * 10
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_integer_column_coerces_to_float(self):
        df = _base_df()
        df["ETH"] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert np.issubdtype(out["ETH"].dtype, np.number)


class TestInfHandling:
    def test_inf_values_raise(self):
        df = _base_df()
        df["ETH"] = [np.inf] * 10
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_negative_inf_values_raise(self):
        df = _base_df()
        df["ETH"] = [-np.inf] * 10
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_mixed_finite_and_inf_raise(self):
        df = _base_df()
        df["ETH"] = [0.001, 0.002, np.inf, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.010]
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")


class TestAllNanAndPartialNan:
    def test_all_nan_column_dropped(self):
        df = _base_df()
        df["ETH"] = np.nan
        df["ALT"] = np.linspace(0.003, 0.004, 10)
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "ETH" not in out.columns
        assert "ALT" in out.columns

    def test_all_nan_benchmark_raises(self):
        df = _base_df()
        df["BTC"] = np.nan
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_partial_nan_kept(self):
        df = _base_df()
        df.loc[df.index[:3], "ETH"] = np.nan
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "ETH" in out.columns
        assert np.isfinite(out["ETH"].to_numpy()[3:]).all()

    def test_leading_and_trailing_nan_kept(self):
        df = _base_df()
        df.loc[df.index[:2], "ETH"] = np.nan
        df.loc[df.index[-2:], "ETH"] = np.nan
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "ETH" in out.columns


class TestIndexAndShapeValidation:
    def test_unparseable_index_raises(self):
        df = pd.DataFrame(
            {"BTC": [1.0] * 5, "ETH": [2.0] * 5},
            index=["not_a_date"] * 5,
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_empty_dataframe_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe(pd.DataFrame())

    def test_none_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe(None)

    def test_non_dataframe_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe([1, 2, 3])

    def test_duplicate_index_deduplicated(self):
        dates = pd.date_range("2023-01-01", periods=5).tolist() + [pd.Timestamp("2023-01-01")]
        df = pd.DataFrame(
            {"BTC": np.arange(6, dtype=float), "ETH": np.arange(6, dtype=float)},
            index=dates,
        )
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert not out.index.has_duplicates
        assert len(out) == 5

    def test_duplicate_columns_raise(self):
        df = pd.DataFrame(
            np.arange(10, dtype=float).reshape(5, 2),
            columns=["BTC", "BTC"],
            index=pd.date_range("2023-01-01", periods=5),
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_insufficient_rows_raise(self):
        df = _base_df()
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC", min_rows=100)

    def test_benchmark_missing_raises(self):
        df = _base_df()
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="SOL")

    def test_only_benchmark_present_raises(self):
        df = pd.DataFrame(
            {"BTC": np.linspace(0.001, 0.002, 10)},
            index=pd.date_range("2023-01-01", periods=10),
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")