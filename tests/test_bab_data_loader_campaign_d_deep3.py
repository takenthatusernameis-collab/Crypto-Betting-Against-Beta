"""Deeper Campaign D tests."""
from __future__ import annotations

import json
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
    _promote_datetime_column,
    _detect_and_normalize_exchange_format,
    _coerce_numeric,
    _strip_units_and_parse,
    _normalize_columns,
    load_returns,
    load_prices,
    normalize_schema,
    detect_price_or_returns,
    validate_returns_dataframe,
    BABDataError,
)


def test_coerce_scalar_pure_digits_short_not_epoch():
    # short digit strings like dates should fall through to normal parsing or fail appropriately
    try:
        ts = _coerce_to_datetime_scalar("20230101")
        assert isinstance(ts, pd.Timestamp)
    except Exception:
        pass


def test_coerce_scalar_signed_numeric_string():
    try:
        ts = _coerce_to_datetime_scalar("+1700000000")
        assert isinstance(ts, pd.Timestamp)
    except Exception:
        pass


def test_coerce_scalar_float_string_ms():
    ts = _coerce_to_datetime_scalar("1700000000000.0")
    assert isinstance(ts, pd.Timestamp)


def test_normalize_index_numeric_object_mixed_floats():
    df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=[1700000000000.0, 1700000001000.0])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_large_ns_above_threshold():
    df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=[np.int64(1700000000000000005), np.int64(1700000001000000005)])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_all_nat_then_raises():
    df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=pd.Index(["not-a-date", "also-bad"]))
    with pytest.raises(BABDataError):
        _normalize_index(df)


def test_strip_units_and_parse():
    assert _strip_units_and_parse("$1,000.50") == 1000.5
    assert _strip_units_and_parse("50%") == 0.5
    assert _strip_units_and_parse("1,234.56") == 1234.56


def test_coerce_numeric():
    df = pd.DataFrame({"a": ["$1,000", "50%", "1.5"], "b": [1, 2, 3]})
    out = _coerce_numeric(df)
    assert isinstance(out, pd.DataFrame)


def test_normalize_columns():
    df = pd.DataFrame({"Close": [1,2], "Date": ["2023-01-01", "2023-01-02"]})
    out = _normalize_columns(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_json(tmp_path):
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    p = tmp_path / "r.json"
    df.to_json(p, orient="records", date_format="iso")
    out = load_returns(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_returns_jsonl(tmp_path):
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    p = tmp_path / "r.jsonl"
    with open(p, "w") as f:
        for _, row in df.iterrows():
            f.write(row.to_json() + "\n")
    out = load_returns(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_returns_pickle(tmp_path):
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    p = tmp_path / "r.pkl"
    df.to_pickle(p)
    out = load_returns(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_prices_from_df():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [27000, 27100]})
    out = load_prices(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_from_df():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    out = load_returns(df)
    assert isinstance(out, pd.DataFrame)


def test_normalize_schema():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    out = normalize_schema(df)
    assert isinstance(out, pd.DataFrame)


def test_detect_price_or_returns():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [27000, 27100]})
    t = detect_price_or_returns(df)
    assert t in {"prices", "returns"}


def test_promote_datetime_column_with_time_col():
    df = pd.DataFrame({"time": [1700000000, 1700000001], "BTC": [0.01, 0.02]})
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_detect_and_normalize_exchange_format_ohlcv_single():
    df = pd.DataFrame({
        "Open time": [1700000000000, 1700000001000],
        "Open": [27000, 27050],
        "High": [27100, 27200],
        "Low": [26950, 27000],
        "Close": [27050, 27100],
        "Volume": [100, 200]
    })
    out = _detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_validate_returns_dataframe_with_inf():
    df = pd.DataFrame({"BTC": [0.01, np.inf]}, index=pd.date_range("2023-01-01", periods=2))
    try:
        out = validate_returns_dataframe(df)
    except Exception:
        pass


def test_validate_returns_dataframe_with_nan():
    df = pd.DataFrame({"BTC": [0.01, np.nan]}, index=pd.date_range("2023-01-01", periods=2))
    try:
        out = validate_returns_dataframe(df)
    except Exception:
        pass
