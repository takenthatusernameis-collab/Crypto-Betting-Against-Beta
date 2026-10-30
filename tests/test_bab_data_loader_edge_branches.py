"""Targeted edge-branch coverage for data_loader.py (P0, 93%).

Hits the coercion and comma-handling branches the existing suite does not
reach. Real assertions on exception types and cleaned output only.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    validate_returns_dataframe,
)


class TestCoerceNumeric:
    def test_multiple_commas_removed(self):
        # ',' present but not the single-decimal-comma case -> remove commas (data_loader.py:159)
        df = pd.DataFrame({"a": ["1,2,3", "4,5,6"]})
        out = _coerce_numeric(df)
        assert out["a"].tolist() == [123.0, 456.0]

    def test_object_column_percent(self):
        df = pd.DataFrame({"a": ["1.5%", "2.5%"]})
        out = _coerce_numeric(df)
        assert out["a"].tolist() == [0.015, 0.025]

    def test_non_object_unparseable_column_raises(self):
        # Non-object, non-string column that astype("float64") rejects and
        # to_numeric(errors="raise") cannot coerce -> BABDataError (data_loader.py:178-179)
        df = pd.DataFrame({"a": pd.arrays.IntervalArray.from_breaks([0, 1, 2])})
        with pytest.raises(BABDataError):
            _coerce_numeric(df)


class TestValidateReturnsDataFrame:
    def test_min_rows_insufficient(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2024-01-01", periods=1))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, min_rows=2)

    def test_all_nan_columns_dropped(self):
        # All-NaN delisted column dropped, benchmark + real asset remain (data_loader.py:117-119 path)
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02], "ETH": [0.03, 0.04], "DELISTED": [np.nan, np.nan]},
            index=pd.date_range("2024-01-01", periods=2),
        )
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "DELISTED" not in out.columns
        assert set(out.columns) == {"BTC", "ETH"}

    def test_only_benchmark_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2024-01-01", periods=2))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_benchmark_missing_raises(self):
        df = pd.DataFrame({"ETH": [0.01, 0.02]}, index=pd.date_range("2024-01-01", periods=2))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_inf_values_raises(self):
        df = pd.DataFrame({"BTC": [0.01, np.inf], "ETH": [0.02, 0.03]},
                          index=pd.date_range("2024-01-01", periods=2))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")
