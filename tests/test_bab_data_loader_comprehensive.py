import numpy as np
import pandas as pd
from pathlib import Path

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError


class TestValidateReturnsDataframe:
    def test_none_raises(self):
        try:
            data_loader.validate_returns_dataframe(None)
            assert False
        except BABDataError:
            pass

    def test_non_df_raises(self):
        try:
            data_loader.validate_returns_dataframe([1, 2])
            assert False
        except BABDataError:
            pass

    def test_empty_raises(self):
        try:
            data_loader.validate_returns_dataframe(pd.DataFrame())
            assert False
        except BABDataError:
            pass

    def test_too_few_rows(self):
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2023-01-01", periods=1))
        try:
            data_loader.validate_returns_dataframe(df, min_rows=2)
            assert False
        except BABDataError:
            pass

    def test_benchmark_missing(self):
        df = pd.DataFrame({"ETH": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        try:
            data_loader.validate_returns_dataframe(df, benchmark="BTC")
            assert False
        except BABDataError:
            pass

    def test_benchmark_only(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        try:
            data_loader.validate_returns_dataframe(df, benchmark="BTC")
            assert False
        except BABDataError:
            pass

    def test_benchmark_all_nan(self):
        df = pd.DataFrame({"BTC": [np.nan, np.nan], "ETH": [0.01, 0.02]},
                          index=pd.date_range("2023-01-01", periods=2))
        try:
            data_loader.validate_returns_dataframe(df, benchmark="BTC")
            assert False
        except BABDataError:
            pass

    def test_duplicate_columns_raises(self):
        df = pd.DataFrame([[0.01, 0.02]], columns=["BTC", "BTC"],
                          index=pd.date_range("2023-01-01", periods=1))
        try:
            data_loader.validate_returns_dataframe(df, min_rows=1)
            assert False
        except BABDataError:
            pass

    def test_infinite_values_raises(self):
        df = pd.DataFrame({"BTC": [0.01, np.inf], "ETH": [0.02, 0.01]},
                          index=pd.date_range("2023-01-01", periods=2))
        try:
            data_loader.validate_returns_dataframe(df, benchmark="BTC")
            assert False
        except BABDataError:
            pass

    def test_datetime_promotion_from_column(self):
        df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        res = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_load_returns_from_dataframe(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01], "ETH": [0.02, 0.01, 0.03]},
                          index=pd.date_range("2023-01-01", periods=3))
        res = data_loader.load_returns_from_dataframe(df, benchmark="BTC")
        assert isinstance(res, pd.DataFrame)

    def test_load_returns_dispatch(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01], "ETH": [0.02, 0.01, 0.03]},
                          index=pd.date_range("2023-01-01", periods=3))
        res = data_loader.load_returns(df, benchmark="BTC")
        assert isinstance(res, pd.DataFrame)

    def test_load_returns_bad_extension(self):
        try:
            data_loader.load_returns("file.txt")
            assert False
        except BABDataError:
            pass

    def test_load_prices_basic(self):
        df = pd.DataFrame({"BTC": [100, 101, 102], "ETH": [50, 51, 52]},
                          index=pd.date_range("2023-01-01", periods=3))
        res = data_loader.load_prices(df, benchmark="BTC")
        assert isinstance(res, pd.DataFrame)

    def test_load_returns_from_csv(self, tmp_path):
        csv = tmp_path / "returns.csv"
        csv.write_text("date,BTC,ETH\n2023-01-01,0.01,0.02\n2023-01-02,-0.01,0.01\n")
        res = data_loader.load_returns_from_csv(csv, benchmark="BTC")
        assert isinstance(res, pd.DataFrame)

    def test_load_returns_from_json(self, tmp_path):
        json_path = tmp_path / "returns.json"
        json_path.write_text('{"BTC": [0.01, 0.02], "ETH": [0.03, 0.01]}')
        res = data_loader.load_returns_from_json(json_path, benchmark="BTC")
        assert isinstance(res, pd.DataFrame)
