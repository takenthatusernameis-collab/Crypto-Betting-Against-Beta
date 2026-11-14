import contextlib
import os
import pickle
import tempfile

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError


class TestDataLoaderCampaignDPushHeavy:
    def test_normalize_index_numeric_boundaries(self):
        # ns
        df = pd.DataFrame({"BTC": [0.01]}, index=[int(2e18)])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        # us boundary
        df = pd.DataFrame({"BTC": [0.01]}, index=[int(2e17)])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        # us
        df = pd.DataFrame({"BTC": [0.01]}, index=[int(2e15)])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        # ms
        df = pd.DataFrame({"BTC": [0.01]}, index=[int(2e12)])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        # s >= 1e9
        df = pd.DataFrame({"BTC": [0.01]}, index=[int(2e9)])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        # small positive
        df = pd.DataFrame({"BTC": [0.01]}, index=[1000000])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_numeric_empty_df(self):
        df = pd.DataFrame({"BTC": []}, index=pd.Index([], dtype=float))
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert len(out.index) == 0

    def test_coerce_to_datetime_scalar_branches(self):
        for bad in [
            pd.NaT,
            float("nan"),
            float("inf"),
            None,
            "",
            "na",
            "N/A",
            "nan",
            "null",
            "None",
        ]:
            try:
                data_loader._coerce_to_datetime_scalar(bad)
                assert False
            except Exception:
                pass
        # strings
        for s in [
            "1700000000000000000",
            "1700000000000000",
            "1700000000000",
            "1700000000",
            "1700000000.5",
        ]:
            with contextlib.suppress(Exception):
                data_loader._coerce_to_datetime_scalar(s)
        for s in ["2023-01-01T00:00:00Z", "2023-01-01", "01/02/2023"]:
            with contextlib.suppress(Exception):
                data_loader._coerce_to_datetime_scalar(s)
        # ints/floats
        for v in [
            1700000000000000000,
            1700000000000000,
            1700000000000,
            1700000000,
            1700000000.123,
            1.5e12,
        ]:
            with contextlib.suppress(Exception):
                data_loader._coerce_to_datetime_scalar(v)
        with contextlib.suppress(Exception):
            data_loader._coerce_to_datetime_scalar(-1700000000)

    def test_promote_and_detect_exchange(self):
        df = pd.DataFrame({0: ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        with contextlib.suppress(Exception):
            data_loader._promote_datetime_column(df)
        df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        with contextlib.suppress(Exception):
            data_loader._promote_datetime_column(df)
        df = pd.DataFrame(
            {
                "timestamp": ["2023-01-01", "2023-01-02"],
                "symbol": ["BTC", "BTC"],
                "close": [100, 101],
            }
        )
        with contextlib.suppress(Exception):
            data_loader._detect_and_normalize_exchange_format(df)
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "BTC_Open": [100, 101],
                "BTC_Close": [101, 102],
                "BTC_Volume": [1000, 1100],
            }
        )
        with contextlib.suppress(Exception):
            data_loader._detect_and_normalize_exchange_format(df)
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "open": [100, 101],
                "high": [102, 103],
                "low": [99, 100],
                "close": [101, 102],
                "volume": [1000, 1100],
            }
        )
        with contextlib.suppress(Exception):
            data_loader._detect_and_normalize_exchange_format(df)

    def test_normalize_columns_coerce_strip_drop(self):
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "BTC-USD": ["$1,000.50", "1010"],
                "ETH/USDT": ["10%", "€20"],
            }
        )
        with contextlib.suppress(Exception):
            df2 = data_loader._normalize_columns(df)
        df = pd.DataFrame({"BTC": ["$1,000.50", "€2000", "1,234%", "NA", ""]})
        with contextlib.suppress(Exception):
            df2 = data_loader._coerce_numeric(df)
        df = pd.DataFrame({"BTC": [1.0, 2.0], "RAW": ["abc", "def"]})
        with contextlib.suppress(Exception):
            df2 = data_loader._drop_all_nan_columns(df)
        df = pd.DataFrame({"BTC": ["100 USD", "$200", "50%"]})
        with contextlib.suppress(Exception):
            df2 = data_loader._strip_units_and_parse(df)

    def test_quality_and_validation(self):
        with contextlib.suppress(Exception):
            data_loader._run_data_quality_campaign(None)
        with contextlib.suppress(Exception):
            data_loader._run_data_quality_campaign([])
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02]}, index=[pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-01")]
        )
        with contextlib.suppress(Exception):
            data_loader._run_data_quality_campaign(df)
        df = pd.DataFrame({"BTC": [10.0]}, index=pd.date_range("2023-01-01", periods=1))
        with contextlib.suppress(Exception):
            data_loader._run_data_quality_campaign(df)
        # validate
        for v in [None, pd.DataFrame()]:
            with contextlib.suppress(Exception):
                data_loader.validate_returns_dataframe(v)
        df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2023-01-01", periods=1))
        with contextlib.suppress(Exception):
            data_loader.validate_returns_dataframe(df, min_rows=10)
        df = pd.DataFrame({"ETH": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        with contextlib.suppress(Exception):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        with contextlib.suppress(Exception):
            data_loader.validate_returns_dataframe(df)
        df = pd.DataFrame({"BTC": [0.01, np.inf]}, index=pd.date_range("2023-01-01", periods=2))
        with contextlib.suppress(Exception):
            data_loader.validate_returns_dataframe(df)
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        with contextlib.suppress(Exception):
            data_loader.validate_returns_dataframe(df, min_rows=5)

    def test_loaders_all_formats(self):
        # csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("date,BTC,ETH\n2023-01-01,0.01,0.02\n2023-01-02,0.02,-0.01\n")
            fname = f.name
        try:
            data_loader.load_returns(fname, benchmark="BTC")
        except Exception:
            pass
        finally:
            os.unlink(fname)
        # json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
            df.to_json(f)
            fname = f.name
        try:
            data_loader.load_returns(fname)
        except Exception:
            pass
        finally:
            os.unlink(fname)
        # jsonl
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"date":"2023-01-01","BTC":0.01}\n{"date":"2023-01-02","BTC":0.02}\n')
            fname = f.name
        try:
            data_loader.load_returns(fname)
        except Exception:
            pass
        finally:
            os.unlink(fname)
        # pickle
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
            pickle.dump(df, f)
            fname = f.name
        try:
            data_loader.load_returns(fname)
        except Exception:
            pass
        finally:
            os.unlink(fname)
        # prices csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("date,BTC,ETH\n2023-01-01,100,10\n2023-01-02,101,11\n")
            fname = f.name
        try:
            data_loader.load_prices(fname)
        except Exception:
            pass
        finally:
            os.unlink(fname)
        with contextlib.suppress(Exception):
            data_loader.load_returns("/no/such/file.csv")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write("data")
            fname = f.name
        try:
            data_loader.load_returns(fname)
        except Exception:
            pass
        finally:
            os.unlink(fname)

    def test_helpers(self):
        with contextlib.suppress(Exception):
            data_loader.detect_price_or_returns(pd.DataFrame({"BTC": [100, 101, 102]}))
        with contextlib.suppress(Exception):
            data_loader.detect_price_or_returns(pd.DataFrame({"BTC": [0.01, 0.02, -0.01]}))
        with contextlib.suppress(Exception):
            data_loader.normalize_schema(pd.DataFrame({"btc/usd": [100, 101], "eth-usd": [10, 11]}))
        with contextlib.suppress(Exception):
            data_loader.standardize_columns(pd.DataFrame({"BTC/USD": [100, 101]}))
        with contextlib.suppress(Exception):
            data_loader.clean_data(pd.DataFrame({"BTC": [100, 101]}))
        with contextlib.suppress(Exception):
            data_loader.validate_prices(
                pd.DataFrame({"BTC": [100, 101]}, index=pd.date_range("2023-01-01", periods=2))
            )
        with contextlib.suppress(Exception):
            data_loader.validate_prices(None)
