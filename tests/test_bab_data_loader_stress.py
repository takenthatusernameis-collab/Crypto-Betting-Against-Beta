"""Stress tests for load_prices / load_returns on messy real-world data."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    load_prices,
    load_returns,
)


def _make_base_df():
    return pd.DataFrame(
        {
            "BTC": [0.01, 0.02, -0.01, 0.03, 0.0],
            "ETH": [0.02, -0.01, 0.01, 0.02, -0.02],
            "SOL": [0.03, 0.01, 0.02, -0.01, 0.01],
        },
        index=pd.date_range("2023-01-01", periods=5),
    )


class TestMixedDtypes:
    def test_mixed_int_float_object_columns(self):
        df = _make_base_df()
        df["BTC"] = df["BTC"].astype("float64")
        df["ETH"] = df["ETH"].astype("int64")
        df["SOL"] = df["SOL"].astype(object)
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert not out.empty
        assert all(out.dtypes == "float64")

    def test_mixed_dtypes_with_benchmark(self):
        df = _make_base_df()
        df["BTC"] = df["BTC"].astype("float32")
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert "BTC" in out.columns


class TestTimezoneAware:
    def test_utc_tz_aware_index(self):
        df = _make_base_df()
        df.index = df.index.tz_localize("UTC")
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert out.index.tz is None
        assert len(out) == 5

    def test_us_eastern_tz_aware_index(self):
        df = _make_base_df()
        df.index = df.index.tz_localize("US/Eastern")
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert out.index.tz is None
        assert len(out) == 5

    def test_mixed_tz_raises(self):
        df = _make_base_df()
        df.index = pd.DatetimeIndex(
            ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
        ).tz_localize("UTC")
        df.iloc[2, 0] = np.nan
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5


class TestDuplicateRows:
    def test_duplicate_timestamps_deduped(self):
        df = _make_base_df()
        df = pd.concat([df, df.iloc[[0, 2]]])
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert not out.index.has_duplicates
        assert len(out) == 5

    def test_duplicate_column_names_raise(self):
        df = _make_base_df()
        df.columns = ["BTC", "ETH", "BTC"]
        with pytest.raises(BABDataError, match="Duplicate column names"):
            load_returns(df, benchmark="BTC", min_rows=1)


class TestCommaPercentFormatted:
    def test_comma_thousand_separator(self):
        df = _make_base_df()
        df["BTC"] = ["0.01", "0,02", "-0.01", "0.03", "0.0"]
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5

    def test_percent_sign_returns(self):
        df = _make_base_df()
        df["BTC"] = ["1%", "-2%", "0.5%", "3%", "0%"]
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5
        assert abs(out["BTC"].iloc[0] - 0.01) < 1e-12
        assert abs(out["BTC"].iloc[1] - (-0.02)) < 1e-12


class TestNAStrings:
    def test_na_string_variants(self):
        df = _make_base_df()
        df["BTC"] = ["0.01", "NA", "n/a", "nan", None]
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5

    def test_null_string_variants(self):
        df = _make_base_df()
        df["BTC"] = ["0.01", "null", "NULL", "None", "#N/A"]
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5


class TestInfValues:
    def test_inf_in_data_raises(self):
        df = _make_base_df()
        df.loc["2023-01-02", "ETH"] = np.inf
        with pytest.raises(BABDataError, match="infinite values"):
            load_returns(df, benchmark="BTC", min_rows=1)

    def test_neg_inf_in_data_raises(self):
        df = _make_base_df()
        df.loc["2023-01-03", "SOL"] = -np.inf
        with pytest.raises(BABDataError, match="infinite values"):
            load_returns(df, benchmark="BTC", min_rows=1)


class TestEmptyFrames:
    def test_empty_dataframe_raises(self):
        df = pd.DataFrame()
        with pytest.raises(BABDataError, match="empty"):
            load_returns(df, benchmark="BTC", min_rows=1)

    def test_none_input_raises(self):
        with pytest.raises(BABDataError, match="None"):
            load_returns(None, benchmark="BTC", min_rows=1)

    def test_single_row_prices_raises(self):
        df = pd.DataFrame({"BTC": [100.0], "ETH": [50.0]}, index=["2023-01-01"])
        with pytest.raises(BABDataError, match="Insufficient rows"):
            load_prices(df, benchmark="BTC", min_rows=2)

    def test_insufficient_rows_raises(self):
        df = _make_base_df().iloc[:2]
        with pytest.raises(BABDataError, match="Insufficient rows"):
            load_returns(df, benchmark="BTC", min_rows=10)


class TestBenchmarkValidation:
    def test_missing_benchmark_raises(self):
        df = _make_base_df()
        with pytest.raises(BABDataError, match="not found"):
            load_returns(df, benchmark="NOTPRESENT", min_rows=1)

    def test_all_nan_benchmark_raises(self):
        df = _make_base_df()
        df["BTC"] = np.nan
        with pytest.raises(BABDataError, match="not found|no finite return values"):
            load_returns(df, benchmark="BTC", min_rows=1)

    def test_only_benchmark_column_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        with pytest.raises(BABDataError, match="no assets to trade"):
            load_returns(df, benchmark="BTC", min_rows=1)


class TestLoadPricesEdgeCases:
    def test_load_prices_with_tz_aware_prices(self):
        df = _make_base_df() * 100
        df.index = df.index.tz_localize("UTC")
        out = load_prices(df, benchmark="BTC", min_rows=2)
        assert not out.empty
        assert out.index.tz is None

    def test_load_prices_with_duplicate_rows(self):
        df = _make_base_df() * 100
        df = pd.concat([df, df.iloc[[0]]])
        out = load_prices(df, benchmark="BTC", min_rows=2)
        assert not out.index.has_duplicates

    def test_load_prices_all_nan_column_dropped(self):
        df = _make_base_df() * 100
        df["DELISTED"] = np.nan
        out = load_prices(df, benchmark="BTC", min_rows=2)
        assert "DELISTED" not in out.columns


class TestLoadReturnsFromDataFrame:
    def test_load_returns_from_dataframe_valid(self):
        df = _make_base_df()
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5
        assert "BTC" in out.columns

    def test_load_returns_preserves_row_count(self):
        df = _make_base_df()
        out = load_returns(df, benchmark="BTC", min_rows=1)
        assert len(out) == 5
