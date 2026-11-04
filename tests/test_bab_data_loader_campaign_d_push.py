"""Campaign D push: adversarial tests for data_loader.py uncovered branches.

Targets helper edge cases (_not_null, _series_has_any_finite,
_coerce_series_to_datetime_index), _normalize_index numeric/non-numeric
magnitude branches and exception handlers, _coerce_to_datetime_scalar scalar
branches (NaT/None/NaN/inf/empty/NA-markers/epoch-magnitudes/normal strings/
ints/floats/Timestamps/garbage).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


class TestNotNullAndHasFinite:
    def test_not_null_none(self):
        assert dl._not_null(None) is False

    def test_not_null_nan(self):
        assert dl._not_null(np.nan) is False

    def test_not_null_inf(self):
        assert dl._not_null(np.inf) is True

    def test_not_null_regular(self):
        assert dl._not_null(1.0) is True
        assert dl._not_null("x") is True

    def test_series_has_any_finite_empty_series(self):
        assert dl._series_has_any_finite(pd.Series([], dtype=float)) is False

    def test_series_has_any_finite_all_nan(self):
        assert dl._series_has_any_finite(pd.Series([np.nan, np.nan])) is False

    def test_series_has_any_finite_mixed(self):
        assert dl._series_has_any_finite(pd.Series([1.0, np.nan])) is True

    def test_series_has_any_finite_list(self):
        assert dl._series_has_any_finite([1.0, np.nan]) is True
        assert dl._series_has_any_finite([np.nan, np.nan]) is False
        assert dl._series_has_any_finite([]) is False

    def test_series_has_any_finite_none(self):
        assert dl._series_has_any_finite(None) is False


class TestCoerceSeriesToDatetimeIndex:
    def test_empty_coerced_returns_false(self):
        df = pd.DataFrame({"x": [1.0]}, index=[0])
        assert dl._coerce_series_to_datetime_index(df, "x", []) is False

    def test_non_series_coerced_with_finite(self):
        df = pd.DataFrame({"x": [1.0]}, index=[0])
        coerced = [pd.Timestamp("2020-01-01")]
        assert dl._coerce_series_to_datetime_index(df, "x", coerced) is True

    def test_tz_aware_coerced_normalized(self):
        df = pd.DataFrame({"x": [1.0]}, index=[0])
        coerced = pd.Series([pd.Timestamp("2020-01-01", tz="UTC")])
        assert dl._coerce_series_to_datetime_index(df, "x", coerced) is True


class TestNormalizeIndexNumeric:
    def test_empty_numeric_index(self):
        df = pd.DataFrame({"BTC": []}, index=pd.Index([], dtype="int64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 0

    def test_nanoseconds_branch(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000000000, 1700000001000000000], dtype="int64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_microseconds_branch(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000000, 1700000001000000], dtype="int64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_milliseconds_branch(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000, 1700000001000], dtype="int64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_seconds_branch(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000, 1700000001], dtype="int64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_small_numbers_seconds_branch(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([100, 200], dtype="int64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_numeric_index_fallback_to_coercer(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index(["not-a-number", "also-bad"], dtype=object))
        with pytest.raises(BABDataError):
            dl._normalize_index(df)

    def test_numeric_index_float_sample(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1.6e9, 1.6e12], dtype="float64"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 2

    def test_tz_normalization_on_existing_datetimeindex(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"], tz="US/Eastern"))
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert out.index.tz is None

    def test_sort_index(self):
        df = pd.DataFrame({"BTC": [0.02, 0.01]}, index=pd.DatetimeIndex(["2020-01-02", "2020-01-01"]))
        out = dl._normalize_index(df)
        assert out.index.is_monotonic_increasing

    def test_drop_nat_rows(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=pd.DatetimeIndex(["2020-01-01", "NaT", "2020-01-03"]))
        out = dl._normalize_index(df)
        assert len(out) == 2

    def test_drop_duplicate_index(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=pd.DatetimeIndex(["2020-01-01", "2020-01-01", "2020-01-02"]))
        out = dl._normalize_index(df)
        assert len(out) == 2


class TestCoerceToDatetimeScalar:
    def test_nat_raises(self):
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
        for marker in {"na", "n/a", "nan", "null", "none"}:
            with pytest.raises(Exception):
                dl._coerce_to_datetime_scalar(marker)

    def test_epoch_ns_int(self):
        ts = dl._coerce_to_datetime_scalar(1700000000000000000)
        assert not pd.isna(ts)

    def test_epoch_us_int(self):
        ts = dl._coerce_to_datetime_scalar(1700000000000000)
        assert not pd.isna(ts)

    def test_epoch_ms_int(self):
        ts = dl._coerce_to_datetime_scalar(1700000000000)
        assert not pd.isna(ts)

    def test_epoch_s_int(self):
        ts = dl._coerce_to_datetime_scalar(1700000000)
        assert not pd.isna(ts)

    def test_epoch_ns_string(self):
        ts = dl._coerce_to_datetime_scalar("1700000000000000000")
        assert not pd.isna(ts)

    def test_epoch_us_string(self):
        ts = dl._coerce_to_datetime_scalar("1700000000000000")
        assert not pd.isna(ts)

    def test_epoch_ms_string(self):
        ts = dl._coerce_to_datetime_scalar("1700000000000")
        assert not pd.isna(ts)

    def test_epoch_s_string(self):
        ts = dl._coerce_to_datetime_scalar("1700000000")
        assert not pd.isna(ts)

    def test_iso_string_z(self):
        ts = dl._coerce_to_datetime_scalar("2020-01-01T00:00:00Z")
        assert not pd.isna(ts)

    def test_iso_string_no_z(self):
        ts = dl._coerce_to_datetime_scalar("2020-01-01 00:00:00")
        assert not pd.isna(ts)

    def test_dayfirst_string(self):
        ts = dl._coerce_to_datetime_scalar("01/02/2020 12:00:00")
        assert not pd.isna(ts)

    def test_int_epoch_ns(self):
        ts = dl._coerce_to_datetime_scalar(np.int64(1700000000000000000))
        assert not pd.isna(ts)

    def test_int_epoch_us(self):
        ts = dl._coerce_to_datetime_scalar(np.int64(1700000000000000))
        assert not pd.isna(ts)

    def test_int_epoch_ms(self):
        ts = dl._coerce_to_datetime_scalar(np.int64(1700000000000))
        assert not pd.isna(ts)

    def test_int_epoch_s(self):
        ts = dl._coerce_to_datetime_scalar(np.int64(1700000000))
        assert not pd.isna(ts)

    def test_float_epoch_ns(self):
        ts = dl._coerce_to_datetime_scalar(1.7e18)
        assert not pd.isna(ts)

    def test_float_epoch_us(self):
        ts = dl._coerce_to_datetime_scalar(1.7e15)
        assert not pd.isna(ts)

    def test_float_epoch_ms(self):
        ts = dl._coerce_to_datetime_scalar(1.7e12)
        assert not pd.isna(ts)

    def test_float_epoch_s(self):
        ts = dl._coerce_to_datetime_scalar(1.7e9)
        assert not pd.isna(ts)

    def test_float_non_epoch(self):
        ts = dl._coerce_to_datetime_scalar(100.5)
        assert not pd.isna(ts)

    def test_timestamp_tz_aware(self):
        ts = dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01", tz="UTC"))
        assert not pd.isna(ts)

    def test_timestamp_naive(self):
        ts = dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01"))
        assert not pd.isna(ts)

    def test_datetime_object(self):
        import datetime
        ts = dl._coerce_to_datetime_scalar(datetime.datetime(2020, 1, 1))
        assert not pd.isna(ts)

    def test_garbage_string_raises(self):
        with pytest.raises(Exception):
            dl._coerce_to_datetime_scalar("definitely-not-a-date")
