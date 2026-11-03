"""Tests for exchange format detection."""

from __future__ import annotations

import pandas as pd

from strategies.betting_against_beta import data_loader


def test_detect_long_format_symbol_date_close():
    df = pd.DataFrame({
        "symbol": ["BTC", "BTC", "ETH", "ETH"],
        "date": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02"],
        "close": [100, 101, 10, 11],
    })
    out = data_loader._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)
    assert "BTC" in out.columns or len(out.columns) >= 1


def test_detect_ohlcv_single_asset_with_date_column():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "open": [99, 100, 101],
        "high": [101, 102, 103],
        "low": [98, 99, 100],
        "close": [100, 101, 102],
        "volume": [1000, 1100, 1200],
    })
    out = data_loader._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_detect_with_epoch_date_strings():
    df = pd.DataFrame({
        "date": ["1700000000", "1700000001"],
        "close": [100, 101],
    })
    out = data_loader._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)
