"""More loader tests."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    load_prices,
    load_returns,
)


def test_load_returns_unsupported_extension(tmp_path):
    p = tmp_path / "bad.txt"
    p.write_text("hello")
    with pytest.raises(BABDataError):
        load_returns(str(p))


def test_load_returns_directory(tmp_path):
    with pytest.raises(BABDataError):
        load_returns(str(tmp_path))


def test_load_returns_none():
    with pytest.raises(BABDataError):
        load_returns(None)


def test_load_prices_from_prices_csv(tmp_path):
    df = pd.DataFrame(
        {"date": ["2023-01-01", "2023-01-02", "2023-01-03"], "BTC": [27000, 27100, 27200]}
    )
    p = tmp_path / "p.csv"
    df.to_csv(p)
    out = load_prices(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_returns_auto_detect_prices(tmp_path):
    df = pd.DataFrame(
        {"date": ["2023-01-01", "2023-01-02", "2023-01-03"], "BTC": [27000, 27100, 27200]}
    )
    p = tmp_path / "p.csv"
    df.to_csv(p)
    out = load_returns(str(p))
    assert isinstance(out, pd.DataFrame)


def test_load_returns_with_benchmark(tmp_path):
    df = pd.DataFrame(
        {"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.005], "ETH": [0.02, -0.01]}
    )
    p = tmp_path / "r.csv"
    df.to_csv(p)
    out = load_returns(str(p), benchmark="BTC")
    assert isinstance(out, pd.DataFrame)
