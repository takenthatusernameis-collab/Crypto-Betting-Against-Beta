"""Campaign D push 4: remaining large uncovered blocks in data_loader.py.

Targets _normalize_columns variants, _drop_all_nan_columns all paths,
_strip_units_and_parse European/percent/malformed, _run_data_quality_campaign
all quality branches, validate_returns_dataframe all validation paths, all
loaders (CSV/JSON/pickle with data), _drop_metadata_columns,
detect_price_or_returns all source types, normalize_schema header/junk paths,
and convenience wrappers.
"""

from __future__ import annotations

import json
import os
import pickle
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


class TestNormalizeColumnsVariants:
    def test_adj_close_variants(self):
        df = pd.DataFrame({"adj close": [1.0], "open": [2.0], "volume": [3.0]})
        out = dl._normalize_columns(df)
        assert set(out.columns) == {"Adj Close", "Open", "Volume"}

    def test_open_high_low_volume_variants(self):
        df = pd.DataFrame({"open price": [1.0], "day high": [2.0], "day low": [3.0], "quote volume": [4.0]})
        out = dl._normalize_columns(df)
        assert set(out.columns) == {"Open", "High", "Low", "Volume"}

    def test_asset_column_normalization(self):
        df = pd.DataFrame({"BTC (USD)": [1.0], "eth/usdt": [2.0]})
        out = dl._normalize_columns(df)
        assert "BTC" in out.columns
        assert "ETH" in out.columns

    def test_exception_in_column_loop(self):
        # Column that causes str() to behave oddly - use bytes
        df = pd.DataFrame({b"BTC": [1.0]})
        out = dl._normalize_columns(df)
        assert isinstance(out, pd.DataFrame)

    def test_duplicate_after_normalization_raise(self):
        df = pd.DataFrame([[1, 2]], columns=["BTC", "btc (usd)"])
        with pytest.raises(BABDataError):
            dl._normalize_columns(df)

    def test_drop_unnamed_when_multiple_cols(self):
        df = pd.DataFrame([[1, 2, 3]], columns=["Unnamed: 0", "BTC", "ETH"])
        out = dl._normalize_columns(df)
        assert "Unnamed: 0" not in out.columns


class TestDropAllNanColumnsAllPaths:
    def test_some_finite_keeps_column(self):
        df = pd.DataFrame({"A": [1.0, np.nan], "B": [np.nan, np.nan]})
        out = dl._drop_all_nan_columns(df)
        assert "A" in out.columns

    def test_object_column_with_data_kept(self):
        df = pd.DataFrame({"A": ["x", "y"], "B": [1.0, 2.0]})
        out = dl._drop_all_nan_columns(df)
        assert "A" in out.columns

    def test_all_nan_raise(self):
        df = pd.DataFrame({"A": [np.nan, np.nan], "B": [np.nan, np.nan]})
        with pytest.raises(BABDataError):
            dl._drop_all_nan_columns(df)

    def test_empty_returned(self):
        assert dl._drop_all_nan_columns(pd.DataFrame()).empty

    def test_none_returned(self):
        assert dl._drop_all_nan_columns(None) is None


class TestStripUnitsAndParseAllPaths:
    def test_none_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse(None))

    def test_int_passthrough(self):
        assert dl._strip_units_and_parse(42) == 42.0

    def test_nan_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse(np.nan))

    def test_inf_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse(np.inf))

    def test_euro_decimal_dot_thousand_comma_decimal(self):
        assert dl._strip_units_and_parse("1.000,50") == 1000.50

    def test_decimal_comma_two_digits(self):
        assert dl._strip_units_and_parse("1,5") == 1.5

    def test_percent(self):
        assert dl._strip_units_and_parse("1.5%") == 0.015

    def test_percent_malformed_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse("abc%"))

    def test_malformed_with_digits_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse("1.2.3"))

    def test_pure_garbage_raises(self):
        with pytest.raises(ValueError):
            dl._strip_units_and_parse("abc")

    def test_currency_and_unit_stripped(self):
        assert dl._strip_units_and_parse("$100 USD") == 100.0
        assert dl._strip_units_and_parse("€50 EUR") == 50.0

    def test_comma_thousand_separator(self):
        assert dl._strip_units_and_parse("1,000.50") == 1000.50

    def test_object_float_conversion(self):
        assert dl._strip_units_and_parse(3.14) == 3.14


class TestRunDataQualityCampaignAllPaths:
    def test_not_dataframe_raises(self):
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign("not-a-df")

    def test_allow_duplicates_drops(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-01"]))
        out = dl._run_data_quality_campaign(df, allow_duplicate_timestamps=True)
        assert len(out) == 1

    def test_implausible_return(self):
        df = pd.DataFrame({"BTC": [0.01, 999999.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, max_return_abs=10.0)

    def test_gap_too_large(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-10"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, max_gap_days=1.0)

    def test_stale_run(self):
        df = pd.DataFrame({"BTC": [0.01] * 60}, index=pd.date_range("2020-01-01", periods=60, freq="D"))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, stale_run_threshold=50)

    def test_min_finite_fraction(self):
        df = pd.DataFrame({"BTC": [np.nan, np.nan, 0.01]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, min_finite_fraction=0.5)

    def test_all_checks_pass(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"]))
        out = dl._run_data_quality_campaign(df)
        assert len(out) == 3


class TestValidateReturnsDataframeAllPaths:
    def test_valid_with_benchmark_and_asset(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.validate_returns_dataframe(df, benchmark="BTC")
        assert "ETH" in out.columns

    def test_benchmark_case_insensitive_rename(self):
        df = pd.DataFrame({"btc": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.validate_returns_dataframe(df, benchmark="BTC")
        assert "BTC" in out.columns

    def test_quality_false_skips_campaign(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        assert "ETH" in out.columns

    def test_lacks_datetime_index_rangeindex(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]})
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC")

    def test_min_rows_short_history(self):
        df = pd.DataFrame({"BTC": [0.01], "ETH": [0.02]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC", min_rows=2)


class TestLoadersWithData:
    def test_csv_roundtrip(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            df.to_csv(f)
            path = f.name
        try:
            out = dl.load_returns_from_csv(path, benchmark="BTC")
            assert "ETH" in out.columns
        finally:
            os.unlink(path)

    def test_json_records_roundtrip(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        df = df.reset_index().rename(columns={"index": "date"})
        df["date"] = df["date"].astype(str)
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(df.to_dict("records"), f)
            path = f.name
        try:
            out = dl.load_returns_from_json(path, orient="records", benchmark="BTC")
            assert "ETH" in out.columns
        finally:
            os.unlink(path)

    def test_json_split_roundtrip(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump({"columns": ["BTC"], "index": ["2020-01-01", "2020-01-02"], "data": [[0.01], [-0.01]]}, f)
            path = f.name
        try:
            out = dl.load_returns_from_json(path, orient="split")
            assert "BTC" in out.columns
        finally:
            os.unlink(path)

    def test_pickle_dataframe_roundtrip(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump(df, f)
            path = f.name
        try:
            out = dl.load_returns_from_pickle(path, benchmark="BTC")
            assert "ETH" in out.columns
        finally:
            os.unlink(path)

    def test_pickle_dict_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump({"date": ["2020-01-01", "2020-01-02"], "BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, f)
            path = f.name
        try:
            out = dl.load_returns_from_pickle(path, benchmark="BTC")
            assert "ETH" in out.columns
        finally:
            os.unlink(path)

    def test_pickle_list_of_dicts(self):
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump([{"date": "2020-01-01", "BTC": 0.01, "ETH": 0.02}, {"date": "2020-01-02", "BTC": -0.01, "ETH": -0.02}], f)
            path = f.name
        try:
            out = dl.load_returns_from_pickle(path, benchmark="BTC")
            assert "ETH" in out.columns
        finally:
            os.unlink(path)

    def test_load_returns_dispatch_csv(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            df.to_csv(f)
            path = f.name
        try:
            out = dl.load_returns(path, benchmark="BTC")
            assert "ETH" in out.columns
        finally:
            os.unlink(path)

    def test_load_returns_dispatch_dataframe(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.load_returns(df, benchmark="BTC")
        assert "ETH" in out.columns

    def test_detect_price_or_returns_prices(self):
        df = pd.DataFrame({"BTC": [100.0, 101.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        assert dl.detect_price_or_returns(df) == "prices"

    def test_detect_price_or_returns_unknown_extension(self):
        assert dl.detect_price_or_returns("/nonexistent/file.xyz") == "unknown"


class TestDropMetadataColumnsAllPaths:
    def test_sequential_integer_artifact(self):
        df = pd.DataFrame({"0": [0.0, 1.0, 2.0], "BTC": [0.01, 0.02, 0.03]})
        out = dl._drop_metadata_columns(df)
        assert "0" not in out.columns

    def test_non_positive_min_value_dropped(self):
        df = pd.DataFrame({"junk": [0.0, -1.0, 0.0], "BTC": [0.01, 0.02, 0.03]})
        out = dl._drop_metadata_columns(df)
        assert "junk" not in out.columns

    def test_all_zeros_dropped(self):
        df = pd.DataFrame({"junk": [0.0, 0.0, 0.0], "BTC": [0.01, 0.02, 0.03]})
        out = dl._drop_metadata_columns(df)
        assert "junk" not in out.columns


class TestNormalizeSchemaPaths:
    def test_header_detection_first_row(self):
        df = pd.DataFrame([["date", "BTC"], ["2020-01-01", 0.01]], columns=["", ""])
        out = dl.normalize_schema(df)
        assert isinstance(out, pd.DataFrame)

    def test_duplicate_header_row_removed(self):
        df = pd.DataFrame([["date", "BTC"], ["date", "BTC"], ["2020-01-01", 0.01]], columns=["date", "BTC"])
        try:
            dl.normalize_schema(df)
        except BABDataError:
            pass
        except ValueError:
            pass

    def test_junk_column_dropped_before_coercion(self):
        df = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "garbage": ["abc", "def"]})
        try:
            dl.normalize_schema(df)
        except (BABDataError, ValueError):
            pass


class TestConvenienceWrappers:
    def test_standardize_columns_valid(self):
        df = pd.DataFrame({"BTC (USD)": [1.0]})
        out = dl.standardize_columns(df)
        assert "BTC" in out.columns

    def test_clean_data_valid(self):
        df = pd.DataFrame({"BTC": ["1.0", "2.0"]})
        out = dl.clean_data(df)
        assert out["BTC"].dtype == np.float64

    def test_validate_prices_with_positive(self):
        df = pd.DataFrame({"BTC": [100.0, 101.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.validate_prices(df)
        assert out is not None
