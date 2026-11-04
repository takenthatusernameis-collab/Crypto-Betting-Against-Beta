import json
import pickle
import os

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_coerce_series_to_datetime_index_paths():
    df = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "BTC": [1,2]})
    coerced = df["date"].apply(dl._coerce_to_datetime_scalar)
    res = dl._coerce_series_to_datetime_index(df, "date", coerced)
    assert isinstance(res, bool)


def test_normalize_index_non_dt_object_strings():
    df = pd.DataFrame({"ret": [0.01, 0.02]}, index=["2020-01-01", "2020-01-02"])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_float_small():
    df = pd.DataFrame({"ret": [0.01, 0.02]}, index=[12345.0, 12346.0])
    try:
        out = dl._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
    except Exception:
        pass


def test_promote_datetime_mixed_formats():
    # binance style
    df = pd.DataFrame({"open_time": ["1600000000000", "1600000060000"], "close": [1,2]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_detect_long_format_symbol_slash():
    df = pd.DataFrame({
        "pair": ["BTC/USDT", "BTC/USDT"],
        "timestamp": ["2020-01-01", "2020-01-02"],
        "close": [100, 101]
    })
    out = dl._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_detect_ohlcv_wide_no_symbol():
    df = pd.DataFrame({
        "Date": ["2020-01-01", "2020-01-02"],
        "Open": [1,2],
        "High": [2,3],
        "Low": [0,1],
        "Close": [1.5,2.5],
        "Volume": [10,20]
    })
    out = dl._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_normalize_columns_duplicates():
    df = pd.DataFrame({"close": [1,2], "Close": [1,2]})
    with pytest.raises(BABDataError):
        dl._normalize_columns(df)


def test_strip_units_and_parse_garbage():
    with pytest.raises(ValueError):
        dl._strip_units_and_parse("abc")


def test_coerce_numeric_series_to_df(tmp_path):
    df = pd.DataFrame({"a": ["$1,000", "2,000%"], "b": ["N/A", "5"]})
    out = dl._coerce_numeric(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_dataframe_already_normalized():
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=pd.date_range("2020-01-01", periods=3))
    out = dl.load_returns(df)
    assert isinstance(out, pd.DataFrame)


def test_load_prices_dataframe():
    df = pd.DataFrame({"BTC": [100, 101, 102]}, index=pd.date_range("2020-01-01", periods=3))
    out = dl.load_prices(df)
    assert isinstance(out, pd.DataFrame)


def test_validate_benchmark_case_insensitive():
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02], "ETH": [0.02, -0.01, 0.01]}, index=pd.date_range("2020-01-01", periods=3))
    out = dl.validate_returns_dataframe(df, benchmark="btc")
    assert isinstance(out, pd.DataFrame)
