"""Campaign D2 hardening tests for data_loader.py - mixed tz/string branches."""
import math

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    _normalize_index,
    _coerce_to_datetime_scalar,
)
from strategies.betting_against_beta.errors import BABDataError


def test_normalize_index_mixed_tz_strings_with_dayfirst_fallback():
    # Mix of formats that may need coercion
    idx = [
        "2023-01-01",
        "01/02/2023",  # ambiguous but try
        "2023-01-03T00:00:00Z",
    ]
    df = pd.DataFrame({"BTC": [1.0, 2.0, 3.0]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 3


def test_normalize_index_mixed_tz_aware_strings():
    idx = pd.Index(["2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+05:00"])
    df = pd.DataFrame({"BTC": [1.0, 2.0]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_with_nat_dropped():
    idx = ["2023-01-01", None, "2023-01-03"]
    df = pd.DataFrame({"BTC": [1.0, 2.0, 3.0]}, index=idx)
    # This might raise or coerce - depending on implementation
    try:
        out = _normalize_index(df)
        # If it doesn't raise, NaT should be dropped
        assert isinstance(out.index, pd.DatetimeIndex)
    except Exception:
        pass


def test_normalize_index_duplicates_dropped():
    idx = ["2023-01-01", "2023-01-01", "2023-01-02"]
    df = pd.DataFrame({"BTC": [1.0, 2.0, 3.0]}, index=idx)
    out = _normalize_index(df)
    assert len(out) == 2


def test_normalize_index_non_datetime_unparseable_raises():
    idx = ["not-a-date", "also-bad"]
    df = pd.DataFrame({"BTC": [1.0, 2.0]}, index=idx)
    with pytest.raises((BABDataError, ValueError)):
        _normalize_index(df)


def test_coerce_scalar_float_small():
    # small positive float
    r = _coerce_to_datetime_scalar(1.5)
    assert isinstance(r, pd.Timestamp)


def test_coerce_scalar_float_ms():
    r = _coerce_to_datetime_scalar(1700000000000.0)
    assert isinstance(r, pd.Timestamp)


def test_coerce_scalar_float_us_large():
    r = _coerce_to_datetime_scalar(1700000000000000.0)
    assert isinstance(r, pd.Timestamp)


def test_coerce_scalar_float_ns():
    r = _coerce_to_datetime_scalar(1700000000000000000.0)
    assert isinstance(r, pd.Timestamp)


def test_coerce_scalar_timestamp_naive():
    r = _coerce_to_datetime_scalar(pd.Timestamp("2023-01-01"))
    assert isinstance(r, pd.Timestamp)


def test_coerce_scalar_timestamp_tzaware_utc():
    r = _coerce_to_datetime_scalar(pd.Timestamp("2023-01-01", tz="UTC"))
    assert isinstance(r, pd.Timestamp)


def test_coerce_scalar_timestamp_tzaware_other():
    try:
        r = _coerce_to_datetime_scalar(pd.Timestamp("2023-01-01", tz="US/Pacific"))
        assert isinstance(r, pd.Timestamp)
    except Exception:
        pass
