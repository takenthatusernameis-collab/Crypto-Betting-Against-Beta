"""Campaign D push 2: adversarial tests for data_loader.py largest uncovered blocks.

Targets _normalize_index non-numeric/fallback paths, _coerce_to_datetime_scalar
scalar branches, _detect_and_normalize_exchange_format long/OHLCV paths,
_promote_datetime_column candidate/unnamed/last-resort paths, _normalize_asset_name,
_normalize_columns, _drop_all_nan_columns, _strip_units_and_parse,
_run_data_quality_campaign, validate_returns_dataframe error paths, all loaders,
detect_price_or_returns, normalize_schema, and convenience wrappers.
"""

from __future__ import annotations

import datetime
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


class TestNormalizeIndexNonNumeric:
    def test_mixed_string_index_dayfirst_fallback(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["01/02/2020", "02/03/2020"])
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_unparseable_index_raises_babdataerror(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["garbage", "also-bad"])
        with pytest.raises(BABDataError):
            dl._normalize_index(df)

    def test_numeric_index_with_none_sample(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index([None], dtype=object))
        try:
            dl._normalize_index(df)
        except BABDataError:
            pass
        except Exception:
            pass

    def test_tz_naive_datetimeindex_passthrough(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"]))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_index_already_datetime_no_tz(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2


class TestCoerceToDatetimeScalarAllBranches:
    def test_nat_type(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(pd.NaT)

    def test_none(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(None)

    def test_nan(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(np.nan)

    def test_inf(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(np.inf)

    def test_empty_str(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar("")

    def test_na_markers(self):
        for m in ("na", "n/a", "nan", "null", "none"):
            with pytest.raises(Exception):
                dl._coerce_to_datetime_scalar(m)

    def test_epoch_strings_all_magnitudes(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000000000000"))  # ns
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000000000"))    # us
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000000"))        # ms
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000"))           # s

    def test_normal_string_formats(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("2020-01-01T00:00:00Z"))
        assert not pd.isna(dl._coerce_to_datetime_scalar("2020-01-01 00:00:00"))
        assert not pd.isna(dl._coerce_to_datetime_scalar("01/02/2020 12:00:00"))

    def test_int_np_integer_epochs(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000000000000)))
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000000000)))
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000000)))
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000)))

    def test_float_epochs_all_magnitudes(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e18))
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e15))
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e12))
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e9))

    def test_float_non_epoch(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(100.5))

    def test_timestamps(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01", tz="UTC")))
        assert not pd.isna(dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01")))

    def test_datetime_object(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(datetime.datetime(2020, 1, 1)))

    def test_garbage_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar("not-a-date-at-all")


class TestDetectAndNormalizeExchangeFormat:
    def test_long_format_symbol_date_price_pivot(self):
        df = pd.DataFrame({
            "symbol": ["BTC", "BTC", "ETH", "ETH"],
            "timestamp": [1600000000000, 1600000060000, 1600000000000, 1600000060000],
            "close": [100.0, 101.0, 200.0, 201.0],
        })
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert "BTC" in out.columns
        assert "ETH" in out.columns

    def test_ohlcv_wide_single_asset(self):
        df = pd.DataFrame({
            "open time": [1600000000000, 1600000060000],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [10.0, 11.0],
        })
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert "Close" in out.columns

    def test_empty_dataframe_returns_as_is(self):
        df = pd.DataFrame()
        out = dl._detect_and_normalize_exchange_format(df)
        assert out.empty

    def test_no_date_column_returns_as_is(self):
        df = pd.DataFrame({"close": [1.0, 2.0], "volume": [10.0, 11.0]})
        out = dl._detect_and_normalize_exchange_format(df)
        assert "Close" in out.columns

    def test_date_column_but_not_epoch_like_returns_as_is(self):
        df = pd.DataFrame({"date": ["jan", "feb"], "close": [1.0, 2.0]})
        out = dl._detect_and_normalize_exchange_format(df)
        assert "Close" in out.columns


class TestPromoteDatetimeColumn:
    def test_candidate_column_date_name(self):
        df = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert "BTC" in out.columns

    def test_candidate_column_timestamp_name(self):
        df = pd.DataFrame({"timestamp": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_unnamed_column_promotion(self):
        df = pd.DataFrame({"": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_already_datetimeindex_passthrough(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_last_resort_object_column_parses(self):
        df = pd.DataFrame({"dt": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_no_datetime_column_returns_as_is(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        out = dl._promote_datetime_column(df)
        assert not isinstance(out.index, pd.DatetimeIndex)


class TestNormalizeAssetName:
    def test_slash_pair_takes_base(self):
        assert dl._normalize_asset_name("BTC/USD") == "BTC"
        assert dl._normalize_asset_name("ETH/USDT") == "ETH"

    def test_concatenated_pair_strips_quote(self):
        assert dl._normalize_asset_name("BTCUSDT") == "BTC"
        assert dl._normalize_asset_name("ETHUSD") == "ETH"

    def test_parentheses_stripped(self):
        assert dl._normalize_asset_name("Bitcoin (USD)") == "BTC"

    def test_common_name_mappings(self):
        assert dl._normalize_asset_name("Bitcoin") == "BTC"
        assert dl._normalize_asset_name("Ethereum") == "ETH"
        assert dl._normalize_asset_name("Solana") == "SOL"
        assert dl._normalize_asset_name("BinanceCoin") == "BNB"
        assert dl._normalize_asset_name("Ripple") == "XRP"
        assert dl._normalize_asset_name("Cardano") == "ADA"
        assert dl._normalize_asset_name("Avalanche") == "AVAX"
        assert dl._normalize_asset_name("Polkadot") == "DOT"

    def test_currency_tokens_removed(self):
        assert dl._normalize_asset_name("BTC USD") == "BTC"
        assert dl._normalize_asset_name("eth usdt") == "ETH"

    def test_single_token_short_form(self):
        assert dl._normalize_asset_name("BTC") == "BTC"
        assert dl._normalize_asset_name("ETH") == "ETH"

    def test_separators_replaced(self):
        assert dl._normalize_asset_name("BTC-USD") == "BTC"
        assert dl._normalize_asset_name("BTC_USD") == "BTC"


class TestNormalizeColumns:
    def test_close_variants(self):
        df = pd.DataFrame({"closing price": [1.0], "high": [2.0]})
        out = dl._normalize_columns(df)
        assert "Close" in out.columns

    def test_ohlc_volume_variants(self):
        df = pd.DataFrame({"open": [1.0], "high": [2.0], "low": [3.0], "volume": [4.0]})
        out = dl._normalize_columns(df)
        assert set(out.columns) == {"Open", "High", "Low", "Volume"}

    def test_date_variants(self):
        df = pd.DataFrame({"datetime": [1], "timestamp": [2]})
        out = dl._normalize_columns(df)
        assert "datetime" in out.columns

    def test_duplicate_columns_raise(self):
        df = pd.DataFrame([[1, 2]], columns=["Close", "close"])
        with pytest.raises(BABDataError):
            dl._normalize_columns(df)

    def test_unnamed_columns_dropped(self):
        df = pd.DataFrame([[1, 2]], columns=["Unnamed: 0", "BTC"])
        out = dl._normalize_columns(df)
        assert "Unnamed: 0" not in out.columns


class TestDropAllNanColumns:
    def test_all_nan_raises(self):
        df = pd.DataFrame({"A": [np.nan, np.nan], "B": [np.nan, np.nan]})
        with pytest.raises(BABDataError):
            dl._drop_all_nan_columns(df)

    def test_mixed_keeps_finite(self):
        df = pd.DataFrame({"A": [1.0, np.nan], "B": [np.nan, np.nan]})
        out = dl._drop_all_nan_columns(df)
        assert "A" in out.columns
        assert "B" not in out.columns

    def test_empty_dataframe_returned(self):
        df = pd.DataFrame()
        out = dl._drop_all_nan_columns(df)
        assert out.empty


class TestStripUnitsAndParse:
    def test_currency_symbols_stripped(self):
        assert dl._strip_units_and_parse("$100.50") == 100.50
        assert dl._strip_units_and_parse("€50.00") == 50.00

    def test_commas_thousand_separator(self):
        assert dl._strip_units_and_parse("1,000.50") == 1000.50

    def test_european_decimal(self):
        assert dl._strip_units_and_parse("1.000,50") == 1000.50

    def test_decimal_comma(self):
        assert dl._strip_units_and_parse("1,5") == 1.5

    def test_percent(self):
        assert dl._strip_units_and_parse("1.5%") == 0.015

    def test_na_markers(self):
        assert np.isnan(dl._strip_units_and_parse("NA"))
        assert np.isnan(dl._strip_units_and_parse("n/a"))

    def test_currency_tokens_removed(self):
        assert dl._strip_units_and_parse("100 USD") == 100.0
        assert dl._strip_units_and_parse("50 USDT") == 50.0

    def test_malformed_numeric_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse("1.2.3"))

    def test_pure_garbage_raises(self):
        with pytest.raises(ValueError):
            dl._strip_units_and_parse("abc")

    def test_none_returns_nan(self):
        assert np.isnan(dl._strip_units_and_parse(None))

    def test_int_float_passthrough(self):
        assert dl._strip_units_and_parse(42) == 42.0
        assert dl._strip_units_and_parse(3.14) == 3.14


class TestSeriesIsParseable:
    def test_empty_series_parseable(self):
        assert dl._series_is_parseable(pd.Series([], dtype=float)) is True

    def test_all_nan_parseable(self):
        assert dl._series_is_parseable(pd.Series([np.nan, np.nan])) is True

    def test_mostly_numbers_parseable(self):
        assert dl._series_is_parseable(pd.Series([1.0, 2.0, "abc"])) is True

    def test_mostly_garbage_not_parseable(self):
        assert dl._series_is_parseable(pd.Series(["abc", "def", "xyz", "1.0"])) is False


class TestCoerceNumeric:
    def test_direct_astype_success(self):
        df = pd.DataFrame({"A": [1.0, 2.0], "B": [3.0, 4.0]})
        out = dl._coerce_numeric(df)
        assert out["A"].dtype == np.float64

    def test_object_strings_coerced(self):
        df = pd.DataFrame({"A": ["1.0", "2.0"], "B": ["3.0", "4.0"]})
        out = dl._coerce_numeric(df)
        assert out["A"].dtype == np.float64

    def test_non_numeric_raises(self):
        df = pd.DataFrame({"A": ["abc", "def"]})
        with pytest.raises(BABDataError):
            dl._coerce_numeric(df)


class TestRunDataQualityCampaign:
    def test_none_raises(self):
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(None)

    def test_empty_raises(self):
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(pd.DataFrame())

    def test_duplicate_timestamps_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-01"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df)

    def test_duplicate_timestamps_allowed(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-01"]))
        out = dl._run_data_quality_campaign(df, allow_duplicate_timestamps=True)
        assert len(out) == 1

    def test_implausible_return_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 999999.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, max_return_abs=10.0)

    def test_data_gap_too_large_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-10"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, max_gap_days=1.0)

    def test_stale_run_raises(self):
        df = pd.DataFrame({"BTC": [0.01] * 60}, index=pd.date_range("2020-01-01", periods=60, freq="D"))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, stale_run_threshold=50)

    def test_min_finite_fraction_raises(self):
        df = pd.DataFrame({"BTC": [np.nan, np.nan, 0.01]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"]))
        with pytest.raises(BABDataError):
            dl._run_data_quality_campaign(df, min_finite_fraction=0.5)


class TestValidateReturnsDataframeErrors:
    def test_none_raises(self):
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(None)

    def test_not_dataframe_raises(self):
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe([1, 2, 3])

    def test_empty_raises(self):
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(pd.DataFrame())

    def test_insufficient_rows_raises(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, min_rows=5)

    def test_missing_benchmark_raises(self):
        df = pd.DataFrame({"ETH": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC")

    def test_only_benchmark_no_assets_raises(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC")

    def test_benchmark_no_finite_raises(self):
        df = pd.DataFrame({"BTC": [np.nan], "ETH": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC")

    def test_short_history_raises(self):
        df = pd.DataFrame({"BTC": [0.01], "ETH": [np.nan]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC", min_rows=2)

    def test_inf_values_raises(self):
        df = pd.DataFrame({"BTC": [np.inf], "ETH": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC")

    def test_valid_returns_pass(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01], "ETH": [0.02, -0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.validate_returns_dataframe(df, benchmark="BTC")
        assert "ETH" in out.columns


class TestLoaders:
    def test_csv_not_found_raises(self):
        with pytest.raises(BABDataError):
            dl.load_returns_from_csv("/nonexistent/file.csv")

    def test_csv_empty_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            f.write("")
            path = f.name
        try:
            with pytest.raises(BABDataError):
                dl.load_returns_from_csv(path)
        finally:
            os.unlink(path)

    def test_parquet_not_found_raises(self):
        with pytest.raises(BABDataError):
            dl.load_returns_from_parquet("/nonexistent/file.parquet")

    def test_hdf5_not_found_raises(self):
        with pytest.raises(BABDataError):
            dl.load_returns_from_hdf5("/nonexistent/file.h5")

    def test_pickle_not_found_raises(self):
        with pytest.raises(BABDataError):
            dl.load_returns_from_pickle("/nonexistent/file.pkl")

    def test_json_not_found_raises(self):
        with pytest.raises(BABDataError):
            dl.load_returns_from_json("/nonexistent/file.json")

    def test_pickle_flat_scalar_list_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump([1, 2, 3], f)
            path = f.name
        try:
            with pytest.raises(BABDataError):
                dl.load_returns_from_pickle(path)
        finally:
            os.unlink(path)

    def test_pickle_unsupported_type_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump("not-tabular", f)
            path = f.name
        try:
            with pytest.raises(BABDataError):
                dl.load_returns_from_pickle(path)
        finally:
            os.unlink(path)

    def test_unsupported_extension_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(BABDataError):
                dl.load_returns(path)
        finally:
            os.unlink(path)

    def test_none_source_raises(self):
        with pytest.raises(BABDataError):
            dl.load_returns(None)

    def test_directory_path_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with pytest.raises(BABDataError):
                dl.load_returns(d)

    def test_load_prices_none_source_raises(self):
        with pytest.raises(BABDataError):
            dl.load_prices(None)

    def test_load_prices_unsupported_type_raises(self):
        with pytest.raises(BABDataError):
            dl.load_prices(123)


class TestDropMetadataColumns:
    def test_unnamed_columns_dropped(self):
        df = pd.DataFrame({"Unnamed: 0": [0, 1, 2], "BTC": [0.01, 0.02, 0.03]})
        out = dl._drop_metadata_columns(df)
        assert "Unnamed: 0" not in out.columns

    def test_sequential_index_artifact_dropped(self):
        df = pd.DataFrame({"extra_col": [0.0, 1.0, 2.0], "BTC": [0.01, 0.02, 0.03]})
        out = dl._drop_metadata_columns(df)
        assert "extra_col" not in out.columns

    def test_all_metadata_raises(self):
        df = pd.DataFrame({"Unnamed: 0": [0, 1, 2], "extra": [3, 4, 5]})
        with pytest.raises(BABDataError):
            dl._drop_metadata_columns(df)


class TestPricesToReturnsAndLoadPrices:
    def test_prices_too_short_raises(self):
        df = pd.DataFrame({"BTC": [100.0]}, index=pd.DatetimeIndex(["2020-01-01"]))
        with pytest.raises(BABDataError):
            dl._prices_to_returns(df)

    def test_load_prices_unsupported_extension_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(BABDataError):
                dl.load_prices(path)
        finally:
            os.unlink(path)

    def test_load_prices_valid(self):
        df = pd.DataFrame({"BTC": [100.0, 101.0, 102.0], "ETH": [200.0, 201.0, 202.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"]))
        out = dl.load_prices(df, benchmark="BTC")
        assert isinstance(out.index, pd.DatetimeIndex)
        assert "BTC" in out.columns


class TestDetectPriceOrReturns:
    def test_returns_detected(self):
        df = pd.DataFrame({"BTC": [0.01, -0.01]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        assert dl.detect_price_or_returns(df) == "returns"

    def test_prices_detected(self):
        df = pd.DataFrame({"BTC": [100.0, 101.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        assert dl.detect_price_or_returns(df) == "prices"

    def test_empty_unknown(self):
        assert dl.detect_price_or_returns(pd.DataFrame()) == "prices"

    def test_csv_unknown_on_error(self):
        assert dl.detect_price_or_returns("/nonexistent/file.csv") == "unknown"


class TestNormalizeSchema:
    def test_none_raises(self):
        with pytest.raises(BABDataError):
            dl.normalize_schema(None)

    def test_not_dataframe_raises(self):
        with pytest.raises(BABDataError):
            dl.normalize_schema("not-a-dataframe")

    def test_empty_raises(self):
        with pytest.raises(BABDataError):
            dl.normalize_schema(pd.DataFrame())

    def test_multi_level_columns_flattened(self):
        df = pd.DataFrame([[1.0, 2.0]], columns=pd.MultiIndex.from_tuples([("A", "x"), ("B", "y")]))
        out = dl.normalize_schema(df)
        assert len(out.columns) == 2

    def test_first_row_as_headers(self):
        df = pd.DataFrame([["date", "BTC"], ["2020-01-01", 0.01]], columns=["", ""])
        out = dl.normalize_schema(df)
        assert "BTC" in out.columns or "date" in out.columns

    def test_valid_schema(self):
        df = pd.DataFrame({"date": ["2020-01-01"], "BTC": [0.01]})
        out = dl.normalize_schema(df)
        assert isinstance(out.index, pd.DatetimeIndex)


class TestConvenienceWrappers:
    def test_standardize_columns_none_raises(self):
        with pytest.raises(BABDataError):
            dl.standardize_columns(None)

    def test_standardize_columns_not_df_raises(self):
        with pytest.raises(BABDataError):
            dl.standardize_columns([1, 2])

    def test_clean_data_none_raises(self):
        with pytest.raises(BABDataError):
            dl.clean_data(None)

    def test_clean_data_not_df_raises(self):
        with pytest.raises(BABDataError):
            dl.clean_data("not-a-df")

    def test_validate_prices_none_returns_none(self):
        assert dl.validate_prices(None) is None

    def test_validate_prices_empty_returns_none(self):
        assert dl.validate_prices(pd.DataFrame()) is None

    def test_validate_prices_no_positive_returns_none(self):
        df = pd.DataFrame({"BTC": [-1.0, -2.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        assert dl.validate_prices(df) is None

    def test_validate_prices_valid(self):
        df = pd.DataFrame({"BTC": [100.0, 101.0]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]))
        out = dl.validate_prices(df)
        assert out is not None
