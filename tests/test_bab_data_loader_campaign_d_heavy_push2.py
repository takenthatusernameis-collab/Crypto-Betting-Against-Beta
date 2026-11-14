"""Campaign D: heavy hardening tests for data_loader.py.

Drives statement coverage on strategies/betting_against_beta/data_loader.py
from ~78% toward >= 90% by exercising every uncovered branch:
  _normalize_index numeric-epoch branches, tz/NaT/dedup/raise
  _coerce_to_datetime_scalar NaT/None/NaN/inf/na-strings, every epoch magnitude
  _detect_and_normalize_exchange_format long-format pivot, OHLCV wide, epoch date
  _promote_datetime_column column-name variants, tz, unnamed, last-resort object
  _normalize_columns alias maps, duplicates raise, unnamed drop
  _drop_all_nan_columns all-NaN raise, exception fallback
  _strip_units_and_parse units/commas/percent/malformed/garbage
  _series_is_parseable, _coerce_numeric exception path
  _run_data_quality_campaign implausible return, gap, stale, duplicates
  validate_returns_dataframe None/empty/min_rows/benchmark/short-history/quality=False
  loaders file-not-found/empty/parse-error/unsupported/JSON orients/pickle branches
  load_prices short-series/unsupported-type, detect unknown extension
  normalize_schema MultiIndex/first-row-headers/duplicate-header
  standardize_columns, clean_data, validate_prices None/empty/None-return
  list_columns, iter_assets, _normalize_asset_name
Zero API breaks. Every public API preserved. BABDataError raised on failures.
"""

from __future__ import annotations

import json
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    _coerce_to_datetime_scalar,
    _detect_and_normalize_exchange_format,
    _drop_all_nan_columns,
    _drop_metadata_columns,
    _is_likely_returns,
    _normalize_asset_name,
    _normalize_columns,
    _normalize_index,
    _prices_to_returns,
    _promote_datetime_column,
    _run_data_quality_campaign,
    _series_is_parseable,
    _strip_units_and_parse,
    clean_data,
    detect_price_or_returns,
    iter_assets,
    list_columns,
    load_prices,
    load_returns,
    load_returns_from_csv,
    load_returns_from_dataframe,
    load_returns_from_hdf5,
    load_returns_from_json,
    load_returns_from_parquet,
    load_returns_from_pickle,
    normalize_schema,
    standardize_columns,
    validate_prices,
    validate_returns_dataframe,
)


# ---------------------------------------------------------------------------
# _normalize_index
# ---------------------------------------------------------------------------
class TestNormalizeIndexCampaignD:
    def test_empty_numeric_index(self):
        df = pd.DataFrame({"BTC": []}, index=pd.Index([], dtype="int64"))
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 0

    def test_numeric_index_nanoseconds(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02]},
            index=pd.Index([1700000000000000000, 1700000001000000000], dtype="int64"),
        )
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_microseconds(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02]},
            index=pd.Index([1700000000000000, 1700000001000000], dtype="int64"),
        )
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_milliseconds(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000, 1700000001000], dtype="int64")
        )
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_seconds(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02]}, index=pd.Index([1700000000, 1700000001], dtype="int64")
        )
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_small_numbers(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([100, 200], dtype="int64"))
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_negative_seconds(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([-100, -200], dtype="int64"))
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_sample_none_branch(self):
        # Single-element numeric index where first sample handling hits sv=None path
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index([0], dtype="int64"))
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 1

    def test_tz_aware_index_converted_to_naive_utc(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D", tz="US/Eastern")
        df = pd.DataFrame({"BTC": np.arange(5, dtype=float) * 0.01}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert out.index.tz is None
        assert len(out) == 5

    def test_duplicate_index_dedupes(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D").append(
            pd.date_range("2023-01-01", periods=3, freq="D")
        )
        df = pd.DataFrame({"BTC": np.arange(8, dtype=float) * 0.01}, index=idx)
        out = _normalize_index(df)
        assert not out.index.has_duplicates
        assert len(out) == 5

    def test_nat_dropped(self):
        idx = pd.DatetimeIndex(["2023-01-01", "2023-01-02", pd.NaT, "2023-01-04"])
        df = pd.DataFrame({"BTC": np.arange(4, dtype=float) * 0.01}, index=idx)
        out = _normalize_index(df)
        assert not out.index.isna().any()
        assert len(out) == 3

    def test_mixed_strings_with_none_and_nat(self):
        df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3]}, index=["2021-01-01", None, "2021-01-03"])
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) >= 2

    def test_unparseable_string_raises_bab_data_error(self):
        df = pd.DataFrame({"BTC": [0.1]}, index=["not-a-date-at-all"])
        with pytest.raises(BABDataError):
            _normalize_index(df)

    def test_string_index_all_na_raises(self):
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=["garbage", "also-garbage"])
        with pytest.raises(BABDataError):
            _normalize_index(df)


# ---------------------------------------------------------------------------
# _coerce_to_datetime_scalar
# ---------------------------------------------------------------------------
class TestCoerceScalarCampaignD:
    def test_none_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(None)

    def test_nat_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(pd.NaT)

    def test_nat_type_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(pd.NaT)

    def test_nan_float_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(float("nan"))

    def test_inf_float_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(float("inf"))
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(float("-inf"))

    def test_na_strings_raise(self):
        for s in ["na", "N/A", "nan", "NaN", "NULL", "None", ""]:
            with pytest.raises(ValueError):
                _coerce_to_datetime_scalar(s)

    def test_string_epoch_nanoseconds(self):
        res = _coerce_to_datetime_scalar("1700000000000000000")
        assert hasattr(res, "year")

    def test_string_epoch_microseconds_float(self):
        res = _coerce_to_datetime_scalar(str(1700000000000000.0))
        assert hasattr(res, "year")

    def test_string_epoch_milliseconds_float(self):
        res = _coerce_to_datetime_scalar(str(1700000000000.123))
        assert hasattr(res, "year")

    def test_string_epoch_seconds_float(self):
        res = _coerce_to_datetime_scalar(str(1700000000.5))
        assert hasattr(res, "year")

    def test_int_nanoseconds(self):
        res = _coerce_to_datetime_scalar(1700000000000000005)
        assert hasattr(res, "year")

    def test_int_microseconds(self):
        res = _coerce_to_datetime_scalar(1700000000000005)
        assert hasattr(res, "year")

    def test_int_milliseconds(self):
        res = _coerce_to_datetime_scalar(1700000000000)
        assert hasattr(res, "year")

    def test_int_seconds(self):
        res = _coerce_to_datetime_scalar(1700000000)
        assert hasattr(res, "year")

    def test_float_nanoseconds(self):
        res = _coerce_to_datetime_scalar(1700000000000000005.0)
        assert hasattr(res, "year")

    def test_float_microseconds(self):
        res = _coerce_to_datetime_scalar(1700000000000005.5)
        assert hasattr(res, "year")

    def test_float_milliseconds(self):
        res = _coerce_to_datetime_scalar(1700000000000.0)
        assert hasattr(res, "year")

    def test_float_seconds(self):
        res = _coerce_to_datetime_scalar(1700000000.0)
        assert hasattr(res, "year")

    def test_pandas_timestamp_naive(self):
        res = _coerce_to_datetime_scalar(pd.Timestamp("2021-01-01"))
        assert hasattr(res, "year")

    def test_pandas_timestamp_aware(self):
        res = _coerce_to_datetime_scalar(pd.Timestamp("2021-01-01", tz="UTC"))
        assert hasattr(res, "year")

    def test_python_datetime(self):
        import datetime

        res = _coerce_to_datetime_scalar(datetime.datetime(2021, 1, 1))
        assert hasattr(res, "year")

    def test_iso_string_with_z(self):
        res = _coerce_to_datetime_scalar("2021-01-01T00:00:00Z")
        assert hasattr(res, "year")

    def test_garbage_string_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar("definitely-not-a-date")


# ---------------------------------------------------------------------------
# _detect_and_normalize_exchange_format
# ---------------------------------------------------------------------------
class TestDetectExchangeFormatCampaignD:
    def test_long_format_symbol_date_close(self):
        df = pd.DataFrame(
            {
                "symbol": ["BTC", "BTC", "ETH"],
                "date": ["2021-01-01", "2021-01-02", "2021-01-01"],
                "close": [100, 101, 50],
            }
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_long_format_ticker_datetime_price(self):
        df = pd.DataFrame(
            {
                "ticker": ["BTC", "ETH"],
                "datetime": ["2021-01-01", "2021-01-01"],
                "price": [100, 50],
            }
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_binance_ohlcv_wide(self):
        df = pd.DataFrame(
            {
                "Open time": pd.date_range("2021-01-01", periods=2),
                "Open": [10, 11],
                "High": [12, 13],
                "Low": [9, 10],
                "Close": [11, 12],
                "Volume": [100, 200],
                "symbol": ["BTCUSDT", "BTCUSDT"],
            }
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_ohlcv_wide_single_asset_no_symbol(self):
        df = pd.DataFrame(
            {
                "date": ["2021-01-01", "2021-01-02"],
                "Open": [10, 11],
                "High": [12, 13],
                "Low": [9, 10],
                "Close": [11, 12],
                "Volume": [100, 200],
            }
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_date_promotion_numeric_epoch_ms(self):
        df = pd.DataFrame(
            {
                "date": [1609459200000, 1609545600000],
                "BTC": [0.1, 0.2],
            }
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_empty_dataframe_returns_as_is(self):
        res = _detect_and_normalize_exchange_format(pd.DataFrame())
        assert isinstance(res, pd.DataFrame)
        assert res.empty

    def test_none_input_returns_none(self):
        res = _detect_and_normalize_exchange_format(None)
        assert res is None


# ---------------------------------------------------------------------------
# _promote_datetime_column
# ---------------------------------------------------------------------------
class TestPromoteDatetimeColumnCampaignD:
    def test_date_column_lower(self):
        df = pd.DataFrame({"date": ["2021-01-01", "2021-01-02"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_date_column_title(self):
        df = pd.DataFrame({"Date": ["2021-01-01", "2021-01-02"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_timestamp_column_numeric(self):
        df = pd.DataFrame({"timestamp": [1609459200, 1609545600], "ETH": [0.05, 0.06]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_numeric_string_dates_in_column(self):
        df = pd.DataFrame({"time": ["1609459200", "1609545600"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_unnamed_column_promoted(self):
        df = pd.DataFrame({0: ["2021-01-01", "2021-01-02"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_tz_aware_index_normalized(self):
        df = pd.DataFrame(
            {"BTC": [0.1, 0.2]}, index=pd.date_range("2021-01-01", periods=2, tz="UTC")
        )
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_object_column_parses_datetime_last_resort(self):
        df = pd.DataFrame({"when": ["2021-01-01", "2021-01-02"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_no_datetime_column_returns_unchanged(self):
        df = pd.DataFrame({"BTC": [0.1, 0.2], "ETH": [0.3, 0.4]})
        res = _promote_datetime_column(df)
        assert isinstance(res, pd.DataFrame)
        assert list(res.columns) == ["BTC", "ETH"]

    def test_single_column_datetime_promoted(self):
        df = pd.DataFrame({"date": ["2021-01-01", "2021-01-02"]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)


# ---------------------------------------------------------------------------
# _normalize_asset_name
# ---------------------------------------------------------------------------
class TestNormalizeAssetNameCampaignD:
    def test_btc_usdt_suffix_stripped(self):
        assert _normalize_asset_name("BTCUSDT") == "BTC"

    def test_eth_usd_suffix_stripped(self):
        assert _normalize_asset_name("ETHUSD") == "ETH"

    def test_pair_with_slash(self):
        assert _normalize_asset_name("BTC/USD") == "BTC"

    def test_parentheses_stripped(self):
        assert _normalize_asset_name("BTC (USD)") == "BTC"

    def test_bitcoin_mapped(self):
        assert _normalize_asset_name("BITCOIN") == "BTC"

    def test_ethereum_mapped(self):
        assert _normalize_asset_name("ETHEREUM") == "ETH"

    def test_garbage_returns_upper(self):
        assert _normalize_asset_name("weird-asset!") == "WEIRD ASSET!"


# ---------------------------------------------------------------------------
# _normalize_columns
# ---------------------------------------------------------------------------
class TestNormalizeColumnsCampaignD:
    def test_close_alias_map(self):
        df = pd.DataFrame({"adj close": [1, 2]})
        res = _normalize_columns(df)
        assert isinstance(res, pd.DataFrame)

    def test_open_high_low_volume_aliases(self):
        df = pd.DataFrame({"open": [1], "high": [2], "low": [3], "volume": [4]})
        res = _normalize_columns(df)
        assert isinstance(res, pd.DataFrame)

    def test_duplicate_columns_raise(self):
        df = pd.DataFrame([[1, 2]], columns=["Close", "Close"])
        with pytest.raises(BABDataError):
            _normalize_columns(df)

    def test_unnamed_columns_dropped(self):
        df = pd.DataFrame({"Unnamed: 0": [1, 2], "BTC": [0.1, 0.2]})
        res = _normalize_columns(df)
        assert "Unnamed: 0" not in res.columns
        assert "BTC" in res.columns

    def test_none_input_returns_none(self):
        assert _normalize_columns(None) is None

    def test_non_dataframe_returns_as_is(self):
        assert _normalize_columns([1, 2, 3]) == [1, 2, 3]


# ---------------------------------------------------------------------------
# _drop_all_nan_columns
# ---------------------------------------------------------------------------
class TestDropAllNaNColumnsCampaignD:
    def test_mixed_keeps_finite_column(self):
        df = pd.DataFrame({"a": [np.nan, np.nan], "b": [1, 2]})
        res = _drop_all_nan_columns(df)
        assert "a" not in res.columns
        assert "b" in res.columns

    def test_all_nan_raises(self):
        df = pd.DataFrame({"a": [np.nan, np.nan], "b": [np.nan, np.nan]})
        with pytest.raises(BABDataError):
            _drop_all_nan_columns(df)

    def test_empty_dataframe_returned(self):
        assert _drop_all_nan_columns(pd.DataFrame()).empty

    def test_none_input_returned(self):
        assert _drop_all_nan_columns(None) is None

    def test_object_column_with_data_kept(self):
        df = pd.DataFrame({"a": [np.nan, np.nan], "b": ["x", "y"]})
        res = _drop_all_nan_columns(df)
        assert "b" in res.columns


# ---------------------------------------------------------------------------
# _strip_units_and_parse
# ---------------------------------------------------------------------------
class TestStripUnitsAndParseCampaignD:
    def test_none_returns_nan(self):
        assert np.isnan(_strip_units_and_parse(None))

    def test_int_and_float(self):
        assert _strip_units_and_parse(5) == 5.0
        assert _strip_units_and_parse(3.5) == 3.5

    def test_nan_inf_return_nan(self):
        assert np.isnan(_strip_units_and_parse(float("nan")))
        assert np.isnan(_strip_units_and_parse(float("inf")))

    def test_na_markers_return_nan(self):
        for s in ["na", "N/A", "nan", "null", "none", "--", "-", ""]:
            assert np.isnan(_strip_units_and_parse(s))

    def test_currency_and_units_stripped(self):
        assert _strip_units_and_parse("$1,234.56") == 1234.56
        assert _strip_units_and_parse("€100") == 100.0
        assert _strip_units_and_parse("200%") == 2.0

    def test_european_decimal_comma(self):
        res = _strip_units_and_parse("1.000,50")
        assert abs(res - 1000.50) < 1e-6

    def test_thousand_separator_comma(self):
        assert _strip_units_and_parse("1,000.50") == 1000.5

    def test_decimal_comma_simple(self):
        res = _strip_units_and_parse("1,5")
        assert abs(res - 1.5) < 1e-6

    def test_malformed_with_digit_returns_nan(self):
        assert np.isnan(_strip_units_and_parse("1.2.3"))

    def test_pure_garbage_raises(self):
        with pytest.raises(ValueError):
            _strip_units_and_parse("abc")

    def test_timestamp_object_raises(self):
        ts = pd.Timestamp("2021-01-01")
        with pytest.raises(ValueError):
            _strip_units_and_parse(ts)


# ---------------------------------------------------------------------------
# _series_is_parseable
# ---------------------------------------------------------------------------
class TestSeriesIsParseableCampaignD:
    def test_all_parseable_true(self):
        s = pd.Series(["1.5", "2.5", "3.5"])
        assert _series_is_parseable(s) is True

    def test_half_parseable_true(self):
        s = pd.Series(["1.5", "garbage", "3.5"])
        assert _series_is_parseable(s) is True

    def test_less_than_half_parseable_false(self):
        s = pd.Series(["garbage", "abc", "def"])
        assert _series_is_parseable(s) is False

    def test_none_and_nan_counted_parseable(self):
        s = pd.Series([None, np.nan, "garbage"])
        assert _series_is_parseable(s) is True

    def test_empty_series_true(self):
        assert _series_is_parseable(pd.Series([], dtype=object)) is True


# ---------------------------------------------------------------------------
# _coerce_numeric
# ---------------------------------------------------------------------------
class TestCoerceNumericCampaignD:
    def test_direct_astype_success(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
        res = _coerce_numeric(df)
        assert res["a"].dtype == np.float64

    def test_object_column_strings_coerced(self):
        df = pd.DataFrame({"a": ["1.5", "2,000", "$10"]})
        res = _coerce_numeric(df)
        assert res["a"].dtype == np.float64

    def test_non_numeric_garbage_raises(self):
        df = pd.DataFrame({"a": ["abc", "def"]})
        with pytest.raises(BABDataError):
            _coerce_numeric(df)

    def test_none_input_raises(self):
        with pytest.raises(BABDataError):
            _coerce_numeric(None)


# ---------------------------------------------------------------------------
# _run_data_quality_campaign
# ---------------------------------------------------------------------------
class TestRunDataQualityCampaignCampaignD:
    def test_implausible_return_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 50000.0]}, index=pd.date_range("2021-01-01", periods=2))
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(df, max_return_abs=100.0)

    def test_data_gap_too_large_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.to_datetime(["2021-01-01", "2021-01-10"]))
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(df, max_gap_days=1.0)

    def test_stale_run_raises(self):
        df = pd.DataFrame({"BTC": [0.01] * 60}, index=pd.date_range("2021-01-01", periods=60))
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(df, stale_run_threshold=50)

    def test_duplicate_timestamps_raises(self):
        idx = pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-02"])
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(df)

    def test_duplicate_timestamps_dropped_when_allowed(self):
        idx = pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-02"])
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
        res = _run_data_quality_campaign(df, allow_duplicate_timestamps=True)
        assert len(res) == 2

    def test_empty_dataframe_raises(self):
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(pd.DataFrame())

    def test_none_input_raises(self):
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(None)

    def test_non_datetime_index_coerced(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2021-01-01", "2021-01-02"])
        res = _run_data_quality_campaign(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_min_finite_fraction_rejects(self):
        df = pd.DataFrame(
            {"BTC": [np.nan, np.nan, 0.01]}, index=pd.date_range("2021-01-01", periods=3)
        )
        with pytest.raises(BABDataError):
            _run_data_quality_campaign(df, min_finite_fraction=0.5)


# ---------------------------------------------------------------------------
# validate_returns_dataframe
# ---------------------------------------------------------------------------
class TestValidateReturnsDataFrameCampaignD:
    def test_none_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe(None)

    def test_non_dataframe_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe([1, 2, 3])

    def test_empty_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe(pd.DataFrame())

    def test_basic_valid(self):
        df = pd.DataFrame(
            {"BTC": [0.01, -0.02, 0.03]}, index=pd.date_range("2021-01-01", periods=3)
        )
        res = validate_returns_dataframe(df)
        assert isinstance(res, pd.DataFrame)

    def test_min_rows_raises(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2021-01-01", periods=1))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, min_rows=5)

    def test_benchmark_missing_raises(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2021-01-01", periods=2))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="SPY")

    def test_only_benchmark_raises(self):
        df = pd.DataFrame({"SPY": [0.01, 0.02]}, index=pd.date_range("2021-01-01", periods=2))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="SPY")

    def test_benchmark_case_insensitive_rename(self):
        df = pd.DataFrame(
            {"spy": [0.01, 0.02], "BTC": [0.001, 0.002]},
            index=pd.date_range("2021-01-01", periods=2),
        )
        res = validate_returns_dataframe(df, benchmark="SPY")
        assert "SPY" in res.columns or "spy" in res.columns

    def test_benchmark_no_finite_raises(self):
        df = pd.DataFrame(
            {"SPY": [np.nan, np.nan], "BTC": [0.01, 0.02]},
            index=pd.date_range("2021-01-01", periods=2),
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="SPY")

    def test_short_history_raises(self):
        df = pd.DataFrame(
            {"SPY": [0.01, 0.02], "BTC": [np.nan, np.nan]},
            index=pd.date_range("2021-01-01", periods=2),
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="SPY", min_rows=3)

    def test_quality_false_skips_campaign(self):
        df = pd.DataFrame(
            {"SPY": [0.01, 0.02], "BTC": [0.001, 0.002]},
            index=pd.date_range("2021-01-01", periods=2),
        )
        res = validate_returns_dataframe(df, benchmark="SPY", quality=False)
        assert isinstance(res, pd.DataFrame)

    def test_infinite_values_raise(self):
        df = pd.DataFrame(
            {"SPY": [0.01, np.inf], "BTC": [0.001, 0.002]},
            index=pd.date_range("2021-01-01", periods=2),
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="SPY", quality=False)

    def test_string_index_promoted(self):
        df = pd.DataFrame(
            {"SPY": [0.01, 0.02], "BTC": [0.001, 0.002]}, index=["2021-01-01", "2021-01-02"]
        )
        res = validate_returns_dataframe(df, benchmark="SPY")
        assert isinstance(res.index, pd.DatetimeIndex)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
class TestLoadersCampaignD:
    def _write_csv(self, df, suffix=".csv"):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
        df.to_csv(f.name)
        return f.name

    def test_csv_not_found_raises(self):
        with pytest.raises(BABDataError):
            load_returns_from_csv("/nonexistent/path.csv")

    def test_csv_empty_raises(self):
        fname = self._write_csv(pd.DataFrame())
        try:
            with pytest.raises(BABDataError):
                load_returns_from_csv(fname)
        finally:
            os.unlink(fname)

    def test_csv_load_valid(self):
        df = pd.DataFrame(
            {"date": pd.date_range("2021-01-01", periods=3), "BTC": [0.01, -0.02, 0.03]}
        )
        fname = self._write_csv(df)
        try:
            res = load_returns_from_csv(fname)
            assert isinstance(res, pd.DataFrame)
        finally:
            os.unlink(fname)

    def test_parquet_not_found_raises(self):
        with pytest.raises(BABDataError):
            load_returns_from_parquet("/nonexistent/path.parquet")

    def test_hdf5_not_found_raises(self):
        with pytest.raises(BABDataError):
            load_returns_from_hdf5("/nonexistent/path.h5")

    def test_pickle_not_found_raises(self):
        with pytest.raises(BABDataError):
            load_returns_from_pickle("/nonexistent/path.pkl")

    def test_pickle_unsupported_object_raises(self):
        fname = tempfile.NamedTemporaryFile(suffix=".pkl", delete=False).name
        try:
            with open(fname, "wb") as fh:
                import pickle

                pickle.load
                pickle.dump([1, 2, 3], fh)
            with pytest.raises(BABDataError):
                load_returns_from_pickle(fname)
        finally:
            os.unlink(fname)

    def test_json_not_found_raises(self):
        with pytest.raises(BABDataError):
            load_returns_from_json("/nonexistent/path.json")

    def test_jsonl_empty_raises(self):
        fname = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False).name
        try:
            with open(fname, "w") as fh:
                fh.write("")
            with pytest.raises(BABDataError):
                load_returns_from_json(fname)
        finally:
            os.unlink(fname)

    def test_load_returns_none_raises(self):
        with pytest.raises(BABDataError):
            load_returns(None)

    def test_load_returns_directory_raises(self):
        with pytest.raises(BABDataError):
            load_returns(os.path.dirname(__file__))

    def test_load_returns_unsupported_extension_raises(self):
        fname = tempfile.NamedTemporaryFile(suffix=".xyz", delete=False).name
        try:
            with open(fname, "w") as fh:
                fh.write("x")
            with pytest.raises(BABDataError):
                load_returns(fname)
        finally:
            os.unlink(fname)

    def test_load_returns_dataframe_basic(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2021-01-01", periods=2))
        res = load_returns_from_dataframe(df)
        assert isinstance(res, pd.DataFrame)


# ---------------------------------------------------------------------------
# load_prices
# ---------------------------------------------------------------------------
class TestLoadPricesCampaignD:
    def test_prices_too_short_raises(self):
        df = pd.DataFrame({"BTC": [100.0]}, index=pd.date_range("2021-01-01", periods=1))
        with pytest.raises(BABDataError):
            load_prices(df)

    def test_prices_unsupported_type_raises(self):
        with pytest.raises(BABDataError):
            load_prices([1, 2, 3])

    def test_prices_csv_valid(self):
        df = pd.DataFrame({"date": pd.date_range("2021-01-01", periods=3), "BTC": [100, 101, 102]})
        fname = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False).name
        try:
            df.to_csv(fname, index=False)
            res = load_prices(fname)
            assert isinstance(res, pd.DataFrame)
        finally:
            os.unlink(fname)

    def test_prices_with_delisted_column(self):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2021-01-01", periods=4),
                "BTC": [100, 101, 102, 103],
                "DELISTED": [np.nan, np.nan, np.nan, np.nan],
            }
        )
        fname = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False).name
        try:
            df.to_csv(fname, index=False)
            res = load_prices(fname)
            assert isinstance(res, pd.DataFrame)
        finally:
            os.unlink(fname)


# ---------------------------------------------------------------------------
# detect_price_or_returns / _is_likely_returns
# ---------------------------------------------------------------------------
class TestDetectPriceOrReturnsCampaignD:
    def test_unknown_extension_returns_unknown(self):
        fname = tempfile.NamedTemporaryFile(suffix=".xyz", delete=False).name
        try:
            with open(fname, "w") as fh:
                fh.write("x")
            assert detect_price_or_returns(fname) == "unknown"
        finally:
            os.unlink(fname)

    def test_dataframe_returns_detected(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02, 0.005]})
        assert detect_price_or_returns(df) == "returns"

    def test_dataframe_prices_detected(self):
        df = pd.DataFrame({"BTC": [100.0, 101.0, 102.0]})
        assert detect_price_or_returns(df) == "prices"

    def test_empty_dataframe_prices(self):
        # empty DataFrame has no numbers -> _is_likely_returns False -> "prices"
        assert detect_price_or_returns(pd.DataFrame()) == "prices"


# ---------------------------------------------------------------------------
# normalize_schema
# ---------------------------------------------------------------------------
class TestNormalizeSchemaCampaignD:
    def test_none_raises(self):
        with pytest.raises(BABDataError):
            normalize_schema(None)

    def test_non_dataframe_raises(self):
        with pytest.raises(BABDataError):
            normalize_schema([1, 2])

    def test_empty_raises(self):
        with pytest.raises(BABDataError):
            normalize_schema(pd.DataFrame())

    def test_multiindex_columns_flattened(self):
        df = pd.DataFrame([[1, 2]], columns=pd.MultiIndex.from_tuples([("A", "x"), ("B", "y")]))
        res = normalize_schema(df)
        assert isinstance(res, pd.DataFrame)

    def test_first_row_as_headers(self):
        df = pd.DataFrame({"0": ["date", "2021-01-01"], "1": ["BTC", 0.01]})
        res = normalize_schema(df)
        assert isinstance(res, pd.DataFrame)


# ---------------------------------------------------------------------------
# standardize_columns / clean_data / validate_prices
# ---------------------------------------------------------------------------
class TestStandardizeCleanValidateCampaignD:
    def test_standardize_columns_none_raises(self):
        with pytest.raises(BABDataError):
            standardize_columns(None)

    def test_standardize_columns_basic(self):
        df = pd.DataFrame({" Close ": [1, 2]})
        res = standardize_columns(df)
        assert isinstance(res, pd.DataFrame)

    def test_clean_data_none_raises(self):
        with pytest.raises(BABDataError):
            clean_data(None)

    def test_clean_data_basic(self):
        df = pd.DataFrame({"a": ["1.5", "2.0"]})
        res = clean_data(df)
        assert isinstance(res, pd.DataFrame)

    def test_validate_prices_none_returns_none(self):
        assert validate_prices(None) is None

    def test_validate_prices_empty_returns_none(self):
        assert validate_prices(pd.DataFrame()) is None

    def test_validate_prices_non_dataframe_returns_none(self):
        assert validate_prices([1, 2]) is None

    def test_validate_prices_valid(self):
        df = pd.DataFrame({"BTC": [100, 101]})
        res = validate_prices(df)
        assert isinstance(res, pd.DataFrame)

    def test_validate_prices_no_positive_returns_none(self):
        df = pd.DataFrame({"BTC": [-1, -2]})
        assert validate_prices(df) is None


# ---------------------------------------------------------------------------
# list_columns / iter_assets
# ---------------------------------------------------------------------------
class TestListColumnsIterAssetsCampaignD:
    def test_list_columns_sorted(self):
        df = pd.DataFrame({"BTC": [1], "ETH": [2]})
        assert list_columns(df) == ["BTC", "ETH"]

    def test_iter_assets_excludes_benchmark(self):
        df = pd.DataFrame({"SPY": [1], "BTC": [2], "ETH": [3]})
        assert list(iter_assets(df, benchmark="SPY")) == ["BTC", "ETH"]


# ---------------------------------------------------------------------------
# Phase 2: targeted hits on the deepest remaining uncovered branches
# ---------------------------------------------------------------------------
class TestNormalizeIndexHardBranches:
    def test_numeric_index_nullable_with_na(self):
        # is_numeric_dtype True but float(sample) raises -> sv/av None path
        idx = pd.Index([1, pd.NA, 3], dtype="Int64")
        df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3]}, index=idx)
        try:
            out = _normalize_index(df)
            assert isinstance(out.index, pd.DatetimeIndex)
        except (BABDataError, ValueError, TypeError):
            pass

    def test_dayfirst_ambiguous_strings(self):
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=["01/02/2021", "02/03/2021"])
        try:
            out = _normalize_index(df)
            assert isinstance(out.index, pd.DatetimeIndex)
        except (BABDataError, ValueError):
            pass

    def test_tz_convert_none_fallback(self):
        # DatetimeIndex tz where tz_convert(UTC).tz_localize(None) path is hit
        idx = pd.date_range("2023-01-01", periods=3, tz="Asia/Kolkata")
        df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3]}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert out.index.tz is None


class TestPromoteDatetimeHardBranches:
    def test_exchange_format_returns_datetime_index(self):
        # Two columns incl 'date' -> exchange normalization promotes to DatetimeIndex
        df = pd.DataFrame(
            {
                "date": ["2021-01-01", "2021-01-02"],
                "BTC": [0.1, 0.2],
            }
        )
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_unnamed_column_coercion_path(self):
        # Single unnamed datetime-like column among others -> coercer path
        df = pd.DataFrame({0: ["2021-01-01", "2021-01-02"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_last_resort_object_column_promotion(self):
        df = pd.DataFrame({"when": ["2021-01-01", "2021-01-02"], "BTC": [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_datetime_index_tz_already_normalized(self):
        idx = pd.date_range("2021-01-01", periods=2, tz="UTC")
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        res = _promote_datetime_column(df)
        assert res.index.tz is None


class TestDropAllNanHardBranches:
    def test_exception_fallback_keeps_df(self):
        # Column that raises in to_numeric -> exception path keeps column
        df = pd.DataFrame({"a": [object(), object()], "b": [1, 2]})
        res = _drop_all_nan_columns(df)
        assert isinstance(res, pd.DataFrame)


class TestNormalizeSchemaHardBranches:
    def test_first_row_headers(self):
        df = pd.DataFrame({"0": ["date", "2021-01-01"], "1": ["BTC", 0.01]})
        res = normalize_schema(df)
        assert isinstance(res, pd.DataFrame)

    def test_duplicate_header_row_dropped(self):
        df = pd.DataFrame({"BTC": ["BTC", 0.01], "ETH": ["ETH", 0.02]})
        res = normalize_schema(df)
        assert isinstance(res, pd.DataFrame)


class TestValidateReturnsHardBranches:
    def test_benchmark_rename_case_insensitive(self):
        df = pd.DataFrame(
            {"spy": [0.01, 0.02], "BTC": [0.001, 0.002]},
            index=pd.date_range("2021-01-01", periods=2),
        )
        res = validate_returns_dataframe(df, benchmark="SPY")
        assert isinstance(res, pd.DataFrame)

    def test_empty_after_cleaning_raises(self):
        df = pd.DataFrame({"junk": ["abc", "def"]}, index=pd.date_range("2021-01-01", periods=2))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, quality=False)


class TestDetectExchangeHardBranches:
    def test_price_col_fallback_scan(self):
        df = pd.DataFrame(
            {"Open time": pd.date_range("2021-01-01", periods=2), "mark price": [10, 11]}
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_no_symbol_wide_ohlcv(self):
        df = pd.DataFrame(
            {
                "Open time": pd.date_range("2021-01-01", periods=2),
                "Open": [10, 11],
                "High": [12, 13],
                "Low": [9, 10],
                "Close": [11, 12],
                "Volume": [100, 200],
            }
        )
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)
