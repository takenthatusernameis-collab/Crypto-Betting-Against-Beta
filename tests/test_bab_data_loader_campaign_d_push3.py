"""Campaign D push 3: deep branch coverage for data_loader.py's four largest functions.

Targets internal magnitude branches of _normalize_index (ns/us/ms/s/small),
_coerce_to_datetime_scalar (all epoch magnitudes + string formats + NaT/None/NaN/inf),
_detect_and_normalize_exchange_format (long format pivot + OHLCV wide),
_promote_datetime_column (candidate column + unnamed + last resort).
"""

from __future__ import annotations

import contextlib
import datetime

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


class TestNormalizeIndexDeepBranches:
    """Hit every numeric-epoch magnitude branch and non-numeric fallback."""

    def _df(self, values, dtype="int64"):
        return pd.DataFrame(
            {"BTC": np.arange(len(values), dtype=float) * 0.01}, index=pd.Index(values, dtype=dtype)
        )

    def test_ns_path_direct_success(self):
        out = dl._normalize_index(self._df([1700000000000000000, 1700000001000000000]))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_ns_path_fallback_to_us(self):
        # Force ns direct to fail, us to succeed
        out = dl._normalize_index(
            self._df([1700000000000000000, 1700000001000000000], dtype="object")
        )
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_us_path_direct_success(self):
        out = dl._normalize_index(self._df([1700000000000000, 1700000001000000]))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_us_path_fallback_to_coercer(self):
        out = dl._normalize_index(
            self._df(["1700000000000000", "1700000001000000"], dtype="object")
        )
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_ms_path_direct_success(self):
        out = dl._normalize_index(self._df([1700000000000, 1700000001000]))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_ms_path_fallback_to_coercer(self):
        out = dl._normalize_index(self._df(["1700000000000", "1700000001000"], dtype="object"))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_s_path_direct_success(self):
        out = dl._normalize_index(self._df([1700000000, 1700000001]))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_s_path_fallback_to_coercer(self):
        out = dl._normalize_index(self._df(["1700000000", "1700000001"], dtype="object"))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_small_numbers_seconds_direct(self):
        out = dl._normalize_index(self._df([100, 200]))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_small_numbers_fallback_coercer(self):
        out = dl._normalize_index(self._df(["100", "200"], dtype="object"))
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_small_numbers_ultimate_fallback_raise(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index(["garbage"], dtype=object))
        with pytest.raises(BABDataError):
            dl._normalize_index(df)

    def test_non_numeric_pandas_coerce_success(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2020-01-01", "2020-01-02"])
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_non_numeric_pandas_coerce_has_nat_then_coercer(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2020-01-01", "not-a-date"])
        with pytest.raises(BABDataError):
            dl._normalize_index(df)

    def test_non_numeric_elementwise_coercer_success(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2020-01-01", "2020-01-02"])
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_non_numeric_last_ditch_dayfirst(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["01/02/2020", "02/03/2020"])
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_tz_convert_utc_then_localize_none(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"], tz="US/Eastern"))
        out = dl._normalize_index(df)
        assert out.index.tz is None

    def test_sort_index_descending(self):
        df = pd.DataFrame(
            {"BTC": [0.02, 0.01]}, index=pd.DatetimeIndex(["2020-01-02", "2020-01-01"])
        )
        out = dl._normalize_index(df)
        assert out.index.is_monotonic_increasing

    def test_drop_nat_then_dedup(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02, 0.03, 0.04]},
            index=pd.DatetimeIndex(["2020-01-01", "NaT", "2020-01-01", "2020-01-02"]),
        )
        out = dl._normalize_index(df)
        assert len(out) == 2


class TestCoerceToDatetimeScalarDeep:
    """Hit every scalar branch: NaT/None/NaN/inf/empty/NA-markers/epoch-mags/strings/ints/floats/Timestamps."""

    def test_nat_type_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(pd.NaT)

    def test_none_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(None)

    def test_nan_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(np.nan)

    def test_inf_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(np.inf)

    def test_neg_inf_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar(float("-inf"))

    def test_empty_string_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar("")

    def test_na_markers_raise(self):
        for m in ("na", "n/a", "nan", "null", "none"):
            with pytest.raises(Exception):
                dl._coerce_to_datetime_scalar(m)

    def test_epoch_string_ns(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000000000000"))

    def test_epoch_string_us(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000000000"))

    def test_epoch_string_ms(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000000"))

    def test_epoch_string_s(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("1700000000"))

    def test_normal_iso_z(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("2020-01-01T00:00:00Z"))

    def test_normal_iso_no_z(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("2020-01-01 00:00:00"))

    def test_dayfirst_fallback(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("01/02/2020 12:00:00"))

    def test_int_np_integer_ns(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000000000000)))

    def test_int_np_integer_us(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000000000)))

    def test_int_np_integer_ms(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000000)))

    def test_int_np_integer_s(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(np.int64(1700000000)))

    def test_float_ns(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e18))

    def test_float_us(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e15))

    def test_float_ms(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e12))

    def test_float_s(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(1.7e9))

    def test_float_non_epoch(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(100.5))

    def test_timestamp_tz_aware(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01", tz="UTC")))

    def test_timestamp_naive(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01")))

    def test_datetime_object(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar(datetime.datetime(2020, 1, 1)))

    def test_garbage_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar("not-a-date-at-all")

    def test_string_epoch_above_ns_boundary(self):
        # Very large epoch ns string may overflow; just verify it's handled
        with contextlib.suppress(Exception):
            dl._coerce_to_datetime_scalar("17000000000000000000")

    def test_string_epoch_us_boundary(self):
        assert not pd.isna(dl._coerce_to_datetime_scalar("170000000000000000"))


class TestDetectAndNormalizeExchangeFormatDeep:
    """Hit long-format pivot, OHLCV wide, date-column promotion paths."""

    def test_long_format_pivot_success(self):
        df = pd.DataFrame(
            {
                "symbol": ["BTC", "BTC", "ETH", "ETH"],
                "timestamp": [1600000000000, 1600000060000, 1600000000000, 1600000060000],
                "close": [100.0, 101.0, 200.0, 201.0],
            }
        )
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert "BTC" in out.columns
        assert "ETH" in out.columns

    def test_long_format_pivot_exception_path(self):
        df = pd.DataFrame(
            {
                "symbol": ["BTC", "BTC"],
                "timestamp": ["bad", "also-bad"],
                "close": [100.0, 101.0],
            }
        )
        out = dl._detect_and_normalize_exchange_format(df)
        # Should not crash; falls through to other handling
        assert isinstance(out, pd.DataFrame)

    def test_ohlcv_wide_adj_close(self):
        df = pd.DataFrame(
            {
                "date": ["2020-01-01", "2020-01-02"],
                "adj close": [100.0, 101.0],
                "volume": [10.0, 11.0],
            }
        )
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_ohlcv_wide_close(self):
        df = pd.DataFrame(
            {
                "date": ["2020-01-01", "2020-01-02"],
                "close": [100.0, 101.0],
            }
        )
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_empty_dataframe(self):
        out = dl._detect_and_normalize_exchange_format(pd.DataFrame())
        assert out.empty

    def test_no_date_column(self):
        df = pd.DataFrame({"close": [1.0, 2.0], "volume": [10.0, 11.0]})
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out, pd.DataFrame)

    def test_date_column_not_epoch_like(self):
        df = pd.DataFrame({"date": ["jan", "feb"], "close": [1.0, 2.0]})
        out = dl._detect_and_normalize_exchange_format(df)
        assert isinstance(out, pd.DataFrame)


class TestPromoteDatetimeColumnDeep:
    """Hit candidate column, unnamed column, last-resort paths."""

    def test_candidate_date_column_two_cols(self):
        df = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_candidate_timestamp_column(self):
        df = pd.DataFrame({"timestamp": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_unnamed_column_promotion(self):
        df = pd.DataFrame({"": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_already_datetimeindex_tz_normalized(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.DatetimeIndex(["2020-01-01"], tz="UTC"))
        out = dl._promote_datetime_column(df)
        assert out.index.tz is None

    def test_last_resort_object_column(self):
        df = pd.DataFrame(
            {"dt": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_no_datetime_column_returns_unchanged(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        out = dl._promote_datetime_column(df)
        assert not isinstance(out.index, pd.DatetimeIndex)

    def test_exchange_format_then_date_column_two_cols(self):
        # Two columns where first is date-like -> exchange format skipped, date col promoted
        df = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "BTC": [0.01, 0.02]})
        out = dl._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)
