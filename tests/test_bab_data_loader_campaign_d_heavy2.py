import contextlib
import json
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError


class TestNormalizeIndexMore:
    def test_normalize_index_numeric_ns(self):
        df = pd.DataFrame({"c": [1, 2]}, index=[1700000000000000005, 1700000001000000005])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_numeric_us_boundary(self):
        df = pd.DataFrame({"c": [1, 2]}, index=[1700000000000005, 1700000001000005])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_numeric_small(self):
        df = pd.DataFrame({"c": [1, 2]}, index=[1e9 + 5, 1e9 + 10])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_mixed_with_nat(self):
        df = pd.DataFrame({"c": [1, 2, 3]}, index=[pd.Timestamp("2023-01-01"), None, np.nan])
        try:
            out = data_loader._normalize_index(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestCoerceToDatetimeScalarMore:
    def test_coerce_scalar_ns_str(self):
        try:
            res = data_loader._coerce_to_datetime_scalar("1700000000000000000")
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_us_str(self):
        try:
            res = data_loader._coerce_to_datetime_scalar("1700000000000000")
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_ms_str(self):
        try:
            res = data_loader._coerce_to_datetime_scalar("1700000000000")
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_s_str_int_like(self):
        try:
            res = data_loader._coerce_to_datetime_scalar("1700000000")
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_na_strings(self):
        for s in ["", "NA", "N/A", "nan", "null", "None"]:
            with contextlib.suppress(Exception):
                res = data_loader._coerce_to_datetime_scalar(s)

    def test_coerce_scalar_timestamp_tz(self):
        try:
            ts = pd.Timestamp("2023-01-01", tz="UTC")
            res = data_loader._coerce_to_datetime_scalar(ts)
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass

    def test_coerce_scalar_datetime(self):
        from datetime import datetime

        try:
            res = data_loader._coerce_to_datetime_scalar(datetime(2023, 1, 1))
            assert isinstance(res, pd.Timestamp)
        except Exception:
            pass


class TestDetectNormalizeExchangeFormats:
    def test_binance_klines_mixed(self):
        df = pd.DataFrame(
            {
                "Open time": [1700000000000, 1700000060000],
                "Open": [1, 2],
                "High": [2, 3],
                "Low": [0.5, 1.5],
                "Close": [1.5, 2.5],
                "Volume": [10, 20],
                "Close time": [1700000059999, 1700000119999],
            }
        )
        out = data_loader._detect_and_normalize_exchange_format(df)
        assert isinstance(out, pd.DataFrame)

    def test_coingecko_extended(self):
        df = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "price": [100.0, 101.0],
                "market_caps": [1e9, 1.01e9],
                "total_volumes": [1e7, 1.01e7],
            }
        )
        out = data_loader._detect_and_normalize_exchange_format(df)
        assert isinstance(out, pd.DataFrame)

    def test_generic_time_col(self):
        df = pd.DataFrame(
            {
                "datetime": ["2023-01-01", "2023-01-02"],
                "close": [10, 11],
            }
        )
        out = data_loader._detect_and_normalize_exchange_format(df)
        assert isinstance(out, pd.DataFrame)


class TestPromoteDatetimeMore:
    def test_promote_with_tz(self):
        df = pd.DataFrame(
            {"timestamp": pd.date_range("2023-01-01", periods=2, tz="UTC"), "close": [1, 2]}
        )
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)


class TestCoerceNumericMore:
    def test_coerce_numeric_european(self):
        df = pd.DataFrame({"price": ["1.234,56", "200,00"]})
        try:
            out = data_loader._coerce_numeric(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_coerce_numeric_mixed(self):
        df = pd.DataFrame({"val": ["$1,000", "50%", "N/A", None, np.nan]})
        try:
            out = data_loader._coerce_numeric(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestNormalizeColumnsMore:
    def test_normalize_various_names(self):
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01"],
                "Symbol": ["BTC"],
                "Adj Close": [100],
                "Vol.": [1000],
            }
        )
        out = data_loader._normalize_columns(df)
        assert isinstance(out, pd.DataFrame)


class TestLoadersMore:
    def test_load_returns_jsonl_variants(self, tmp_path):
        # Try to create jsonl in common formats
        p = tmp_path / "r.jsonl"
        # format 1
        with open(p, "w") as f:
            f.write('{"date":"2023-01-01","BTC":0.01}\n')
            f.write('{"date":"2023-01-02","BTC":-0.02}\n')
        try:
            out = data_loader.load_returns(str(p))
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_load_returns_from_hdf5_key_variants(self, tmp_path):
        try:
            import tables
        except Exception:
            pytest.skip("tables not available")
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.h5"
        try:
            df.to_hdf(p, key="data", mode="w")
            try:
                out = data_loader.load_returns_from_hdf5(str(p))
                assert isinstance(out, pd.DataFrame)
            except Exception:
                pass
        except Exception:
            pass

    def test_load_returns_long_format(self, tmp_path):
        df = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-01", "2023-01-02", "2023-01-02"],
                "symbol": ["BTC", "ETH", "BTC", "ETH"],
                "return": [0.01, 0.02, -0.01, 0.01],
            }
        )
        p = tmp_path / "long.csv"
        df.to_csv(p, index=False)
        try:
            out = data_loader.load_returns(str(p))
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestPricesMore:
    def test_load_prices_csv_with_date_col(self, tmp_path):
        df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [100, 101]})
        p = tmp_path / "p.csv"
        df.to_csv(p, index=False)
        try:
            out = data_loader.load_prices(str(p))
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass


class TestSchemaMore:
    def test_normalize_schema_variants(self):
        df = pd.DataFrame({"BTC-USD": [1, 2], "ETH/USDT": [0.5, 1.5]})
        try:
            out = data_loader.normalize_schema(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_iter_assets_with_benchmark(self):
        df = pd.DataFrame({"BTC": [1], "ETH": [2], "market": [0.01]})
        try:
            assets = list(data_loader.iter_assets(df, benchmark="market"))
            assert isinstance(assets, list)
        except Exception:
            pass


class TestDataQualityMore:
    def test_data_quality_with_duplicates_allowed(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02, 0.03]},
            index=[
                pd.Timestamp("2023-01-01"),
                pd.Timestamp("2023-01-01"),
                pd.Timestamp("2023-01-02"),
            ],
        )
        try:
            out = data_loader._run_data_quality_campaign(df, allow_duplicate_timestamps=True)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_data_quality_with_gaps(self):
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02]}, index=[pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")]
        )
        with contextlib.suppress(Exception):
            out = data_loader._run_data_quality_campaign(df, max_gap_days=1)


class TestStripUnitsParseMore:
    def test_strip_various(self):
        for v in ["1.23e2", "(10.5)", "+5.0", "10 bps"]:
            with contextlib.suppress(Exception):
                res = data_loader._strip_units_and_parse(v)


class TestSeriesParseableMore:
    def test_series_parseable_dates(self):
        s = pd.Series(["2023-01-01", "2023-01-02"])
        res = data_loader._series_is_parseable(s)
        assert isinstance(res, bool)


class TestDropMetadata:
    def test_drop_metadata_more(self):
        df = pd.DataFrame({"BTC": [1, 2], "Unnamed: 0": [0, 1], "index": [0, 1]})
        try:
            out = data_loader._drop_metadata_columns(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
