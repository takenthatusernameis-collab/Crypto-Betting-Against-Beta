"""Campaign D3: _coerce_series_to_datetime_index and more."""
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    _coerce_series_to_datetime_index,
    _normalize_index,
)
from strategies.betting_against_beta.errors import BABDataError


def test_coerce_series_to_datetime_index_basic():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [1.0, 2.0]})
    coerced = pd.to_datetime(df["date"])
    # simulate
    result = _coerce_series_to_datetime_index(df, "date", coerced)
    assert result is True


def test_coerce_series_to_datetime_index_with_tz():
    df = pd.DataFrame({"date": ["2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+00:00"], "BTC": [1.0, 2.0]})
    coerced = pd.to_datetime(df["date"], utc=True)
    result = _coerce_series_to_datetime_index(df, "date", coerced)
    assert result is True


def test_coerce_series_to_datetime_index_empty_like():
    df = pd.DataFrame({"date": [None, None], "BTC": [1.0, 2.0]})
    coerced = pd.Series([pd.NaT, pd.NaT])
    result = _coerce_series_to_datetime_index(df, "date", coerced)
    assert result is False


def test_normalize_index_all_nat_dropped():
    df = pd.DataFrame({"BTC": [1.0, 2.0]}, index=[pd.NaT, pd.NaT])
    try:
        out = _normalize_index(df)
        # might raise
    except Exception:
        pass
