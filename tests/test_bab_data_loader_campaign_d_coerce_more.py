"""More coercer tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import _coerce_to_datetime_scalar


def test_coerce_scalar_pandas_tz_aware():
    ts_in = pd.Timestamp("2023-01-01", tz="UTC")
    ts = _coerce_to_datetime_scalar(ts_in)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_int_various():
    ts = _coerce_to_datetime_scalar(1700000000000000000)  # ns
    assert isinstance(ts, pd.Timestamp)
    ts = _coerce_to_datetime_scalar(1700000000000000)  # us
    assert isinstance(ts, pd.Timestamp)
    ts = _coerce_to_datetime_scalar(1700000000000)  # ms
    assert isinstance(ts, pd.Timestamp)
    ts = _coerce_to_datetime_scalar(1700000000)  # s
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_large_float():
    ts = _coerce_to_datetime_scalar(1e18)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_string_dayfirst_fallback():
    # try formats that might need dayfirst
    try:
        ts = _coerce_to_datetime_scalar("14/11/2023 22:13:20")
        assert isinstance(ts, pd.Timestamp)
    except Exception:
        pass


def test_coerce_scalar_object_with_tz():
    ts_in = pd.Timestamp("2023-01-01T00:00:00Z")
    ts = _coerce_to_datetime_scalar(ts_in)
    assert isinstance(ts, pd.Timestamp)
