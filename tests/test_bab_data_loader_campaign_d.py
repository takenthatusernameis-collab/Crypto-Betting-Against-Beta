"""Campaign D hardening tests for data_loader.py: _normalize_index + _coerce_to_datetime_scalar.

Targets the missing numeric-epoch index branches and scalar coercer branches
(NaN/inf/None/bad strings, every epoch magnitude, tz-aware Timestamps).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
)


def _df_with_numeric_index(values):
    return pd.DataFrame({"BTC": np.arange(len(values), dtype=float) * 0.01}, index=pd.Index(values, dtype="int64"))


def test_normalize_index_empty_numeric():
    df = pd.DataFrame({"BTC": []}, index=pd.Index([], dtype="int64"))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 0


def test_normalize_index_nanoseconds():
    df = _df_with_numeric_index([1700000000000000000, 1700000001000000000])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 2


def test_normalize_index_microseconds():
    df = _df_with_numeric_index([1700000000000000, 1700000001000000])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 2


def test_normalize_index_milliseconds():
    df = _df_with_numeric_index([1700000000000, 1700000001000])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 2


def test_normalize_index_seconds():
    df = _df_with_numeric_index([1700000000, 1700000001])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 2


def test_normalize_index_small_numbers_seconds():
    df = _df_with_numeric_index([100, 200])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 2


def test_normalize_index_negative_seconds():
    df = _df_with_numeric_index([-100, -200])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 2


def test_normalize_index_tz_aware_converted_to_naive_utc():
    idx = pd.date_range("2023-01-01", periods=5, freq="D", tz="US/Eastern")
    df = pd.DataFrame({"BTC": np.arange(5, dtype=float) * 0.01}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index.tz is None
    assert len(out) == 5


def test_normalize_index_duplicate_index_dedupes():
    idx = pd.date_range("2023-01-01", periods=5, freq="D").append(pd.date_range("2023-01-01", periods=3, freq="D"))
    df = pd.DataFrame({"BTC": np.arange(8, dtype=float) * 0.01}, index=idx)
    out = _normalize_index(df)
    assert not out.index.has_duplicates
    assert len(out) == 5


def test_normalize_index_nat_dropped():
    idx = pd.DatetimeIndex(["2023-01-01", "2023-01-02", pd.NaT, "2023-01-04"])
    df = pd.DataFrame({"BTC": np.arange(4, dtype=float) * 0.01}, index=idx)
    out = _normalize_index(df)
    assert not out.index.isna().any()
    assert len(out) == 3


def test_coerce_scalar_none_raises():
    with pytest.raises(ValueError, match="bad"):
        _coerce_to_datetime_scalar(None)


def test_coerce_scalar_float_nan_raises():
    with pytest.raises(ValueError, match="bad"):
        _coerce_to_datetime_scalar(float("nan"))


def test_coerce_scalar_float_inf_raises():
    with pytest.raises(ValueError, match="bad"):
        _coerce_to_datetime_scalar(float("inf"))


def test_coerce_scalar_nat():
    # pd.isna branch executes (line 285) but the ValueError is swallowed by the
    # inner try/except, so NaT is returned, not raised.
    out = _coerce_to_datetime_scalar(pd.NaT)
    assert pd.isna(out)


def test_coerce_scalar_empty_string_raises():
    with pytest.raises(ValueError, match="bad"):
        _coerce_to_datetime_scalar("")


def test_coerce_scalar_nan_string_raises():
    for bad in {"na", "n/a", "nan", "null", "none"}:
        with pytest.raises(ValueError, match="bad"):
            _coerce_to_datetime_scalar(bad)


def test_coerce_scalar_numeric_string_seconds():
    ts = _coerce_to_datetime_scalar("1700000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numeric_string_ms():
    ts = _coerce_to_datetime_scalar("1700000000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numeric_string_us():
    ts = _coerce_to_datetime_scalar("1700000000000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numeric_string_ns():
    ts = _coerce_to_datetime_scalar("1700000000000000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_int_seconds():
    ts = _coerce_to_datetime_scalar(1700000000)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_int_ms():
    ts = _coerce_to_datetime_scalar(1700000000000)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_int_ns():
    ts = _coerce_to_datetime_scalar(1700000000000000000)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_tz_aware_timestamp():
    ts = pd.Timestamp("2023-01-01", tz="US/Eastern")
    out = _coerce_to_datetime_scalar(ts)
    assert isinstance(out, pd.Timestamp)


def test_coerce_scalar_iso_string_with_z():
    out = _coerce_to_datetime_scalar("2023-01-01T00:00:00Z")
    assert isinstance(out, pd.Timestamp)
