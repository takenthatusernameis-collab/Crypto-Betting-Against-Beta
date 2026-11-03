"""Campaign D4: _promote_datetime_column and _coerce_numeric paths."""
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    _promote_datetime_column,
    _coerce_numeric,
)
from strategies.betting_against_beta.errors import BABDataError


def test_promote_datetime_from_date_column():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [1.0, 2.0]})
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_from_timestamp_column():
    df = pd.DataFrame({"timestamp": [1672531200, 1672617600], "BTC": [1.0, 2.0]})  # seconds
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_unparseable_raises():
    df = pd.DataFrame({"date": ["bad", "also-bad"], "BTC": [1.0, 2.0]})
    with pytest.raises(BABDataError):
        _promote_datetime_column(df)


def test_coerce_numeric_mixed():
    df = pd.DataFrame({"BTC": ["1.0", "2.5"], "ETH": [1, np.nan]})
    out = _coerce_numeric(df)
    # numeric columns should be numeric
    assert np.isfinite(out["BTC"].iloc[0])


def test_coerce_numeric_garbage_raises():
    df = pd.DataFrame({"BTC": ["abc", "def"]})
    with pytest.raises(BABDataError):
        _coerce_numeric(df)
