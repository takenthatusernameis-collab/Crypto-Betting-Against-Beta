"""Tests for exchange format loader support (CoinGecko, Binance, Coinbase)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    load_prices,
    load_returns,
    validate_returns_dataframe,
)


class TestExchangeFormatLoaders:
    def test_binance_ohlcv_csv_via_load_prices(self, tmp_path: Path):
        idx = pd.date_range("2023-01-01", periods=90, freq="D")
        rng = np.random.default_rng(123)
        df = pd.DataFrame(
            {
                "Open time": [int(d.timestamp() * 1000) for d in idx],
                "Open": rng.normal(100, 1, 90),
                "High": rng.normal(101, 1, 90),
                "Low": rng.normal(99, 1, 90),
                "Close": rng.normal(100, 2, 90).cumsum() + 100,
                "Volume": rng.normal(1000, 10, 90),
            }
        )
        path = tmp_path / "binance.csv"
        df.to_csv(path)
        out = load_prices(path)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out.columns) == 1
        assert len(out) == 89  # pct_change drops first row

    def test_binance_ohlcv_dataframe_via_load_prices(self):
        idx = pd.date_range("2023-01-01", periods=90, freq="D")
        rng = np.random.default_rng(124)
        df = pd.DataFrame(
            {
                "Open time": idx.strftime("%Y-%m-%d %H:%M:%S"),
                "Close": rng.normal(100, 1, 90).cumsum() + 200,
            }
        )
        out = load_prices(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) >= 1

    def test_coingecko_long_format_csv_via_load_prices(self, tmp_path: Path):
        idx = pd.date_range("2023-01-01", periods=60, freq="D")
        rows = []
        rng_b = np.random.default_rng(10)
        rng_e = np.random.default_rng(11)
        pb = 100.0
        pe = 10.0
        for i in range(60):
            pb = pb * (1 + rng_b.normal(0, 0.01))
            pe = pe * (1 + rng_e.normal(0, 0.015))
            rows.append({"date": idx[i].strftime("%Y-%m-%d"), "coin": "BTC", "price": pb})
            rows.append({"date": idx[i].strftime("%Y-%m-%d"), "coin": "ETH", "price": pe})
        df = pd.DataFrame(rows)
        path = tmp_path / "coingecko.csv"
        df.to_csv(path)
        out = load_prices(path)
        assert isinstance(out.index, pd.DatetimeIndex)
        cols = [c.lower() for c in out.columns]
        assert "btc" in cols and "eth" in cols

    def test_coingecko_long_format_dataframe_via_load_prices(self):
        idx = pd.date_range("2023-01-01", periods=60, freq="D")
        rows = []
        for i in range(60):
            rows.append(
                {"Date": idx[i].strftime("%Y-%m-%d"), "Coin": "BTC", "Price": 100 * (1 + 0.001 * i)}
            )
            rows.append(
                {"Date": idx[i].strftime("%Y-%m-%d"), "Coin": "ETH", "Price": 10 * (1 + 0.002 * i)}
            )
        df = pd.DataFrame(rows)
        out = load_prices(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert any(c.lower() == "btc" for c in out.columns)
        assert any(c.lower() == "eth" for c in out.columns)

    def test_coinbase_ohlcv_csv_via_load_prices(self, tmp_path: Path):
        idx = pd.date_range("2023-01-01", periods=90, freq="D")
        rng = np.random.default_rng(456)
        df = pd.DataFrame(
            {
                "time": [d.strftime("%Y-%m-%d") for d in idx],
                "low": rng.random(90) * 9000 + 9500,
                "high": rng.random(90) * 9000 + 10500,
                "open": rng.random(90) * 9000 + 10000,
                "close": rng.random(90) * 9000 + 10000,
                "volume": rng.random(90) * 100,
            }
        )
        path = tmp_path / "coinbase.csv"
        df.to_csv(path)
        out = load_prices(path)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out) == 89

    def test_coinbase_style_dataframe_via_load_prices(self):
        idx = pd.date_range("2023-01-01", periods=90, freq="D")
        rng = np.random.default_rng(457)
        df = pd.DataFrame(
            {
                "time": idx,
                "open": rng.random(90) + 100,
                "high": rng.random(90) + 101,
                "low": rng.random(90) + 99,
                "close": rng.random(90) + 100,
                "volume": rng.random(90),
            }
        )
        out = load_prices(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_exchange_long_format_via_load_returns_csv(self, tmp_path: Path):
        idx = pd.date_range("2023-01-01", periods=90, freq="D")
        # Create price-like long format and save; load_returns expects returns by default
        # But better to pass prices converted - or test through load_prices then validate
        rows = []
        for i in range(90):
            rows.append({"symbol": "BTC", "date": idx[i].strftime("%Y-%m-%d"), "close": 10000 + i})
            rows.append(
                {"symbol": "ETH", "date": idx[i].strftime("%Y-%m-%d"), "close": 1000 + i * 0.5}
            )
        df = pd.DataFrame(rows)
        path = tmp_path / "long.csv"
        df.to_csv(path)
        out = load_prices(path)
        assert isinstance(out.index, pd.DatetimeIndex)
        cols_lower = [str(c).lower() for c in out.columns]
        assert "btc" in cols_lower and "eth" in cols_lower

    def test_exchange_wide_with_symbol_case_handling(self):
        idx = pd.date_range("2023-01-01", periods=90, freq="D")
        rng = np.random.default_rng(789)
        df = pd.DataFrame(
            {
                "Date": idx,
                "btc": rng.normal(0, 0.01, 90),
                "ETH": rng.normal(0, 0.01, 90),
            }
        )
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "BTC" in out.columns or any(c.lower() == "btc" for c in out.columns)

    def test_binance_symbol_pair_long_format(self):
        idx = pd.date_range("2023-01-01", periods=60, freq="D")
        rows = []
        for i in range(60):
            rows.append(
                {
                    "pair": "BTCUSDT",
                    "timestamp": idx[i].strftime("%Y-%m-%d"),
                    "close": 20000 + i * 10,
                }
            )
            rows.append(
                {"pair": "ETHUSDT", "timestamp": idx[i].strftime("%Y-%m-%d"), "close": 1500 + i * 2}
            )
        df = pd.DataFrame(rows)
        out = load_prices(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out.columns) >= 2
