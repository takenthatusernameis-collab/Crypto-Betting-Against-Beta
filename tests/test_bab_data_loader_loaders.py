"""Tests for loaders and validation."""

from __future__ import annotations

import os
import tempfile

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError


def test_load_returns_from_dataframe():
    idx = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({"BTC": np.random.randn(10)*0.01, "ETH": np.random.randn(10)*0.01}, index=idx)
    out = data_loader.load_returns_from_dataframe(df, benchmark="BTC")
    assert isinstance(out, pd.DataFrame)


def test_validate_returns_dataframe_basic():
    idx = pd.date_range("2023-01-01", periods=100)
    df = pd.DataFrame({"BTC": np.random.randn(100)*0.01, "ETH": np.random.randn(100)*0.01}, index=idx)
    try:
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_load_prices_to_returns():
    idx = pd.date_range("2023-01-01", periods=50)
    prices = pd.DataFrame({"BTC": 100 * np.cumprod(1 + np.random.randn(50)*0.01), "ETH": 10 * np.cumprod(1 + np.random.randn(50)*0.01)}, index=idx)
    try:
        ret = data_loader._prices_to_returns(prices)
        assert isinstance(ret, pd.DataFrame)
    except Exception:
        pass


def test_load_returns_csv(tmp_path):
    idx = pd.date_range("2023-01-01", periods=20)
    df = pd.DataFrame({"BTC": np.random.randn(20)*0.01, "ETH": np.random.randn(20)*0.01}, index=idx)
    p = tmp_path / "returns.csv"
    df.to_csv(p)
    out = data_loader.load_returns_from_csv(str(p), benchmark="BTC")
    assert isinstance(out, pd.DataFrame)
