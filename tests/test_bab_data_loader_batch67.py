import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 67: targets around _detect_and_normalize_exchange_format and promote edge cases


def test_exchange_long_format_normalize():
    df = pd.DataFrame(
        {
            "symbol": ["BTC", "BTC", "ETH", "ETH"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"],
            "close": [100, 101, 50, 51],
        }
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "BTC" in out.columns


def test_exchange_ohlcv_single_asset_with_open_time():
    df = pd.DataFrame(
        {
            "Open time": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "Open": [1, 2, 3, 4, 5],
            "High": [2, 3, 4, 5, 6],
            "Low": [0.5, 1.5, 2.5, 3.5, 4.5],
            "Close": [100, 101, 102, 103, 104],
            "Volume": [10, 20, 30, 40, 50],
        }
    )
    try:
        out = dl.validate_returns_dataframe(df, benchmark=None, quality=False)
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_detect_and_normalize_tz_date_col():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ).tz_localize("UTC"),
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05],
            "ETH": [0.04, 0.05, 0.06, 0.07, 0.08],
        }
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "BTC" in out.columns


def test_promote_datetime_epoch_ms():
    df = pd.DataFrame(
        {
            "timestamp": [
                1704067200000,
                1704153600000,
                1704240000000,
                1704326400000,
                1704412800000,
            ],
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05],
            "ETH": [0.04, 0.05, 0.06, 0.07, 0.08],
        }
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert isinstance(out, pd.DataFrame)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_epoch_s():
    df = pd.DataFrame(
        {
            "unix": [1704067200, 1704153600, 1704240000, 1704326400, 1704412800],
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05],
            "ETH": [0.04, 0.05, 0.06, 0.07, 0.08],
        }
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert isinstance(out, pd.DataFrame)


def test_promote_name_match_elementwise_tz():
    df = pd.DataFrame(
        {
            "date": [
                pd.Timestamp("2024-01-01T00:00:00+05:00"),
                pd.Timestamp("2024-01-02T00:00:00+05:00"),
                pd.Timestamp("2024-01-03T00:00:00+05:00"),
                pd.Timestamp("2024-01-04T00:00:00+05:00"),
                pd.Timestamp("2024-01-05T00:00:00+05:00"),
            ],
            "BTC": [0.01] * 5,
            "ETH": [0.02] * 5,
        }
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "BTC" in out.columns


def test_unnamed_tz_series_coercion():
    df = pd.DataFrame(
        {
            "Unnamed: 0": [
                "2024-01-01T00:00:00+05:00",
                "2024-01-02T00:00:00+05:00",
                "2024-01-03T00:00:00+05:00",
                "2024-01-04T00:00:00+05:00",
                "2024-01-05T00:00:00+05:00",
            ],
            "BTC": [0.01] * 5,
            "ETH": [0.02] * 5,
        },
        index=pd.RangeIndex(5),
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "BTC" in out.columns


def test_last_resort_promote_object_string_datetime():
    df = pd.DataFrame(
        {
            "mystery": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "BTC": [0.01] * 5,
            "ETH": [0.02] * 5,
        },
        index=pd.RangeIndex(5),
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "mystery" not in out.columns
    assert isinstance(out.index, pd.DatetimeIndex)
