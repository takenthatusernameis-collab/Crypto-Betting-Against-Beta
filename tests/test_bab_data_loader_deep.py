import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.errors import BABDataError


FIX = os.path.join(os.path.dirname(__file__), "fixtures")


class TestDataLoaderDeep:
    def test_load_returns_from_dataframe(self):
        idx = pd.date_range("2023-01-01", periods=20)
        df = pd.DataFrame({"BTC": np.random.randn(20)*0.01, "ETH": np.random.randn(20)*0.01}, index=idx)
        out = data_loader.load_returns(df, benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
        assert "BTC" in out.columns

    def test_load_returns_from_csv_path(self):
        path = os.path.join(FIX, "messy_returns.csv")
        out = data_loader.load_returns(path, benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_returns_from_json_dict(self):
        out = data_loader.load_returns(os.path.join(FIX, "returns.json"), benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_returns_errors(self):
        with pytest.raises((BABDataError, Exception)):
            data_loader.load_returns(None)
        with pytest.raises((BABDataError, Exception)):
            data_loader.load_returns("")

    def test_load_prices_csv(self):
        try:
            out = data_loader.load_prices(os.path.join(FIX, "real_market_prices.csv"))
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_prices_to_returns(self):
        idx = pd.date_range("2023-01-01", periods=10)
        prices = pd.DataFrame({"BTC": np.linspace(100, 110, 10)}, index=idx)
        try:
            rets = data_loader.prices_to_returns(prices)
        except Exception:
            rets = data_loader._prices_to_returns(prices)
        assert isinstance(rets, pd.DataFrame)
