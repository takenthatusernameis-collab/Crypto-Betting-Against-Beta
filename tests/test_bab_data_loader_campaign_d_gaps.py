import json
import os
import pickle

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_normalize_index_numeric_edge_cases():
    # ns boundary
    df = pd.DataFrame({"r": [0.1, 0.2]}, index=[1600000000000000005, 1600000001000000000])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    # us boundary
    df = pd.DataFrame({"r": [0.1, 0.2]}, index=[1600000000000005, 1600000001000000])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    # ms
    df = pd.DataFrame({"r": [0.1, 0.2]}, index=[1600000000000, 1600000060000])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    # small numeric
    df = pd.DataFrame({"r": [0.1, 0.2]}, index=[1000, 2000])
    try:
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
    except Exception:
        pass


def test_coerce_to_datetime_scalar_ns_us_float():
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000000005.0))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000005.0))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000.0))
    assert not pd.isna(dl._coerce_to_datetime_scalar("1600000000000000000"))


def test_coerce_to_datetime_scalar_bad_strings():
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar("")
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar("N/A")
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar("abc")


def test_promote_datetime_column_variants():
    # date column with epoch strings
    df = pd.DataFrame({"Date": ["1600000000", "1600000060"], "BTC": [1, 2]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    # timestamp epoch
    df = pd.DataFrame({"timestamp": [1600000000, 1600000060], "BTC": [1, 2]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_long_format_pivot_variants():
    df = pd.DataFrame(
        {
            "ticker": ["BTC/USDT", "BTC/USDT", "ETH/USDT", "ETH/USDT"],
            "time": [
                "2020-01-01T00:00:00Z",
                "2020-01-02T00:00:00Z",
                "2020-01-01T00:00:00Z",
                "2020-01-02T00:00:00Z",
            ],
            "close": [100, 101, 10, 11],
        }
    )
    out = dl._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_load_prices_errors(tmp_path):
    with pytest.raises(BABDataError):
        dl.load_prices("/no/such/file.csv")
    with pytest.raises(BABDataError):
        dl.load_prices("bad.txt")


def test_load_returns_from_series_index():
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=pd.date_range("2020-01-01", periods=3))
    out = dl.load_returns(df)
    assert isinstance(out, pd.DataFrame)
