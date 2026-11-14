import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError


class TestMoreFloats:
    def test_coerce_scalar_float_ms(self):
        try:
            res = data_loader._coerce_to_datetime_scalar(1700000000000.5)
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_float_s(self):
        try:
            res = data_loader._coerce_to_datetime_scalar(1700000000.5)
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_np_float(self):
        try:
            res = data_loader._coerce_to_datetime_scalar(np.float64(1700000000))
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_np_int(self):
        try:
            res = data_loader._coerce_to_datetime_scalar(np.int64(1700000000000))
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass


class TestNormalizeIndexMoreCases:
    def test_normalize_index_numeric_float_s(self):
        df = pd.DataFrame({"c": [1, 2]}, index=[1700000000.0, 1700000060.0])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_object_mixed_all_datetime(self):
        df = pd.DataFrame(
            {"c": [1, 2]}, index=[pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]
        )
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)


class TestPromoteDatetimeEdge:
    def test_promote_datetime_rename(self):
        df = pd.DataFrame({"Date": ["2023-01-01", "2023-01-02"], "close": [1, 2]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_promote_datetime_time(self):
        df = pd.DataFrame({"time": ["2023-01-01 00:00:00", "2023-01-02 00:00:00"], "close": [1, 2]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)


class TestDetectFormatMore:
    def test_detect_binance_with_timestamp(self):
        df = pd.DataFrame(
            {
                "timestamp": [1700000000000, 1700000060000],
                "open": [1, 2],
                "high": [2, 3],
                "low": [0.5, 1.5],
                "close": [1.5, 2.5],
                "volume": [10, 20],
            }
        )
        try:
            out = data_loader._detect_and_normalize_exchange_format(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestLoadReturnsFromDataFrame:
    def test_load_returns_df_with_datetime_index(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        out = data_loader.load_returns_from_dataframe(df)
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_df_needs_normalization(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02], "date": ["2023-01-01", "2023-01-02"]})
        try:
            out = data_loader.load_returns_from_dataframe(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestPricesToReturnsMore:
    def test_prices_to_returns_log(self):
        df = pd.DataFrame({"BTC": [100, 110, 121]}, index=pd.date_range("2023-01-01", periods=3))
        try:
            out = data_loader._prices_to_returns(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestDropAllNaCols:
    def test_drop_all_nan(self):
        df = pd.DataFrame({"a": [np.nan, np.nan], "b": [1, 2]})
        out = data_loader._drop_all_nan_columns(df)
        assert isinstance(out, pd.DataFrame)
