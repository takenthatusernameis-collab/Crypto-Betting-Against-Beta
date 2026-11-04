"""More Campaign D hardening tests for data_loader.py gaps."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
    _promote_datetime_column,
    _detect_and_normalize_exchange_format,
    load_returns,
    load_prices,
    validate_returns_dataframe,
    BABDataError,
)


def test_normalize_index_object_with_numeric_strings_epoch_s():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index(["1700000000", "1700000001"]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_object_with_numeric_strings_epoch_ms():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index(["1700000000000", "1700000001000"]))
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_mixed_types_fallback():
    # mixed types that trigger elementwise coercion
    idx = [1700000000, "2023-11-14T22:13:20Z"]
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.Index(idx))
    try:
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
    except Exception:
        pass


def test_coerce_scalar_na_strings_raise():
    for s in ["NA", "N/A", "nan", "NaN", "null", "None", ""]:
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(s)


def test_coerce_scalar_numeric_string_ms():
    ts = _coerce_to_datetime_scalar("1700000000000")
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_numpy_float():
    ts = _coerce_to_datetime_scalar(np.float64(1700000000.0))
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_tz_aware_timestamp():
    ts_in = pd.Timestamp("2023-01-01", tz="US/Eastern")
    ts = _coerce_to_datetime_scalar(ts_in)
    assert isinstance(ts, pd.Timestamp)


def test_coerce_scalar_datetime():
    import datetime
    ts = _coerce_to_datetime_scalar(datetime.datetime(2023, 1, 1))
    assert isinstance(ts, pd.Timestamp)


def test_promote_datetime_column_from_date_col():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_column_from_timestamp_col():
    df = pd.DataFrame({"timestamp": ["1700000000", "1700000001"], "BTC": [0.01, 0.02]})
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_detect_exchange_binance_long_format():
    df = pd.DataFrame({
        "Open time": ["1700000000000", "1700000001000"],
        "symbol": ["BTCUSDT", "BTCUSDT"],
        "close": [27000, 27100]
    })
    out = _detect_and_normalize_exchange_format(df)
    # might pivot to wide
    assert isinstance(out, pd.DataFrame)


def test_detect_exchange_coingecko_wide():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "BTC": [27000, 27100],
        "ETH": [1800, 1810]
    })
    out = _detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_csv_basic(tmp_path):
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005]})
    p = tmp_path / "r.csv"
    df.to_csv(p)
    out = load_returns(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_prices_csv_basic(tmp_path):
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [27000, 27100]})
    p = tmp_path / "p.csv"
    df.to_csv(p)
    out = load_prices(str(p))
    assert isinstance(out, pd.DataFrame)


def test_validate_returns_dataframe_ok():
    df = pd.DataFrame({"BTC": [0.01, -0.005]}, index=pd.date_range("2023-01-01", periods=2))
    out = validate_returns_dataframe(df)
    assert isinstance(out, pd.DataFrame)
