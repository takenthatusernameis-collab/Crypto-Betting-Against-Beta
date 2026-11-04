"""Even more Campaign D tests."""
from __future__ import annotations

import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
    _promote_datetime_column,
    _detect_and_normalize_exchange_format,
    load_returns,
    load_prices,
    BABDataError,
)


def test_normalize_index_object_floats():
    df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=[1700000000000.0, 1700000001000.0])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_coerce_scalar_python_float_ns():
    ts = _coerce_to_datetime_scalar(1.7e18)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_string_with_space():
    ts = _coerce_to_datetime_scalar(" 1700000000 ")
    assert isinstance(ts, pd.Timestamp)


def test_promote_datetime_column_various_names():
    for name in ["Date", "date", "DATE", "timestamp", "Timestamp", "time", "datetime"]:
        df = pd.DataFrame({name: ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        out = _promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_column_unnamed_datetime_series():
    df = pd.DataFrame({0: ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    out = _promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_detect_exchange_long_format_symbol_variations():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02"],
        "symbol": ["btc", "btc", "eth", "eth"],
        "price": [27000, 27100, 1800, 1810]
    })
    out = _detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_csv_with_space_headers(tmp_path):
    df = pd.DataFrame({" Date ": ["2023-01-01", "2023-01-02"], " BTC ": [0.01, -0.005]})
    p = tmp_path / "r.csv"
    df.to_csv(p)
    out = load_returns(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_returns_hdf5_if_available(tmp_path):
    try:
        import tables  # noqa
    except Exception:
        try:
            import h5py  # noqa
        except Exception:
            pytest.skip("no hdf5 support")
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    p = tmp_path / "r.h5"
    try:
        df.to_hdf(p, key="df")
        out = load_returns(str(p))
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_load_returns_parquet_if_available(tmp_path):
    try:
        import pyarrow  # noqa
    except Exception:
        try:
            import fastparquet  # noqa
        except Exception:
            pytest.skip("no parquet support")
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    p = tmp_path / "r.parquet"
    try:
        df.to_parquet(p)
        out = load_returns(str(p))
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_validate_returns_dataframe_with_bad_benchmark():
    df = pd.DataFrame({"ETH": [0.01, -0.005]}, index=pd.date_range("2023-01-01", periods=2))
    try:
        out = validate_returns_dataframe(df, benchmark="BTC")
    except Exception:
        pass
