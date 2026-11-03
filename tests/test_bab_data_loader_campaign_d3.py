"""More Campaign D tests for tricky branches."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
)


def test_normalize_index_numeric_us_boundary():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([1700000000000000, 1700000001000000]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_us_boundary_high():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index([1e17 + 5]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_above_ns():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index([1e19]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_small_positive():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index([5, 6]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_zero_or_negative_magnitude():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.Index([0]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_object_index_with_mixed_tz_strings():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2023-01-01T00:00:00+02:00", "2023-01-02T00:00:00-07:00"])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index.tz is None


def test_normalize_index_unparseable_raises_babdataerror():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["not-a-date", "also-bad"])
    with pytest.raises(Exception):
        _normalize_index(df)
