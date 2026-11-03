"""More Campaign D tests for _coerce_to_datetime_scalar."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import _coerce_to_datetime_scalar


def test_coerce_scalar_float_seconds():
    ts = _coerce_to_datetime_scalar(1700000000.0)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_float_ms():
    ts = _coerce_to_datetime_scalar(1700000000000.0)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_float_us():
    ts = _coerce_to_datetime_scalar(1700000000000000.0)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_float_ns():
    ts = _coerce_to_datetime_scalar(1700000000000000000.0)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_float_large_ns():
    ts = _coerce_to_datetime_scalar(1.7e18)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_float_us_boundary():
    ts = _coerce_to_datetime_scalar(1e17 + 1000)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_float_small():
    ts = _coerce_to_datetime_scalar(100.0)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numpy_int():
    ts = _coerce_to_datetime_scalar(np.int64(1700000000))
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numeric_string_us():
    ts = _coerce_to_datetime_scalar("1700000000000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numeric_string_ns():
    ts = _coerce_to_datetime_scalar("1700000000000000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_z_string():
    ts = _coerce_to_datetime_scalar("2023-11-14T22:13:20Z")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_offset_string():
    ts = _coerce_to_datetime_scalar("2023-11-14T22:13:20+00:00")
    assert isinstance(ts, pd.Timestamp)
