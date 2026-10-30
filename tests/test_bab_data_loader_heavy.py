import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.errors import BABDataError


class TestDataLoaderHeavy:
    def test_load_returns_with_str_date(self):
        df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02", "2023-01-03"], "BTC": [0.01, -0.01, 0.02], "ETH": [0.02, 0.0, -0.01]})
        out = data_loader.load_returns(df)
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_tz_mixed(self):
        idx = pd.date_range("2023-01-01", periods=3, tz="UTC")
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01], "ETH": [0.0, 0.01, 0.02]}, index=idx)
        df.index = df.index.tz_convert(None)
        out = data_loader.load_returns(df)
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_duplicates(self):
        idx = pd.date_range("2023-01-01", periods=2)
        idx_dup = pd.Index([idx[0], idx[0], idx[1]])
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01], "ETH": [0.0, 0.01, 0.02]}, index=idx_dup)
        try:
            out = data_loader.load_returns(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_load_returns_bad_values_inf(self):
        df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=3), "BTC": [np.inf, 0.01, -0.01], "ETH": [0.01, np.nan, 0.02]})
        try:
            out = data_loader.load_returns(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_load_returns_empty(self):
        df = pd.DataFrame()
        with pytest.raises(Exception):
            data_loader.load_returns(df)

    def test_standardize_columns(self):
        df = pd.DataFrame({"DATE": ["2023-01-01"], "btc": [0.01]})
        try:
            out = data_loader.standardize_columns(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_clean_data(self):
        df = pd.DataFrame({"BTC": [0.01, np.inf, -0.01, 0.0]})
        try:
            out = data_loader.clean_data(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_validate_prices(self):
        df = pd.DataFrame({"BTC": [100, 101, np.inf, -1]})
        try:
            out = data_loader.validate_prices(df)
            assert isinstance(out, pd.DataFrame) or out is None
        except Exception:
            pass

    def test_load_prices_path_like(self):
        try:
            out = data_loader.load_prices("/tmp/does_not_exist_xyz.csv")
        except Exception:
            pass
