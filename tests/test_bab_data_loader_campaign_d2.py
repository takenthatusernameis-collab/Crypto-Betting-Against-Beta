"""More Campaign D tests for data_loader.py uncovered branches."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_to_datetime_scalar,
    _normalize_index,
)


def test_normalize_index_float_numeric_seconds():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000.0, 1700000001.5]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_float_numeric_ms():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000.0, 1700000001000.0]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_float_numeric_us():
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000000.0, 1700000001000000.0])
    )
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_float_numeric_ns():
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000000000.0, 1700000001000000000.0])
    )
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_float_large_ns():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index([1.7e18]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_mixed_string_z_and_naive():
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03]},
        index=["2023-01-01T00:00:00Z", "2023-01-02T00:00:00", "2023-01-03T00:00:00+00:00"],
    )
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index.tz is None


def test_normalize_index_string_with_dayfirst_fallback():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["01/02/2023", "02/02/2023"])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_elementwise_coercion_strings():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2023-01-01", "2023-01-02"])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_coerce_scalar_float_int_like():
    ts = _coerce_to_datetime_scalar(1700000000000.0)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_tz_aware_timestamp_converted():
    ts = pd.Timestamp("2023-01-01", tz="UTC")
    out = _coerce_to_datetime_scalar(ts)
    assert isinstance(out, pd.Timestamp)


def test_coerce_scalar_datetime_naive():
    import datetime

    dt = datetime.datetime(2023, 1, 1)
    out = _coerce_to_datetime_scalar(dt)
    assert isinstance(out, pd.Timestamp)


def test_coerce_scalar_numeric_string_small():
    ts = _coerce_to_datetime_scalar("12345")
    assert isinstance(ts, pd.Timestamp)
