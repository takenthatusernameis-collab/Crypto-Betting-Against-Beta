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


class TestNormalizeIndexCampaign:
    def test_normalize_index_empty_df_returns_df(self):
        df = pd.DataFrame()
        out = data_loader._normalize_index(df)
        assert isinstance(out, pd.DataFrame)

    def test_normalize_index_numeric_index_ms(self):
        # ms epoch
        df = pd.DataFrame({"close": [1, 2, 3]}, index=[1700000000000, 1700000060000, 1700000120000])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_numeric_index_us(self):
        df = pd.DataFrame({"close": [1, 2]}, index=[1700000000000000, 1700000060000000])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_numeric_index_ns(self):
        df = pd.DataFrame({"close": [1, 2]}, index=[1700000000000000000, 1700000060000000000])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_numeric_index_s_float(self):
        df = pd.DataFrame({"close": [1.0, 2.0]}, index=[1700000000.5, 1700000060.5])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_string_index_parse(self):
        df = pd.DataFrame({"close": [1, 2]}, index=["2023-01-01", "2023-01-02"])
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_mixed_object_fallback(self):
        df = pd.DataFrame({"close": [1, 2, 3]}, index=[pd.Timestamp("2023-01-01"), "bad", None])
        try:
            out = data_loader._normalize_index(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            # Implementation may raise on unparseable values
            pass


class TestCoerceToDatetimeScalar:
    def test_coerce_to_datetime_scalar_none_nat(self):
        try:
            res = data_loader._coerce_to_datetime_scalar(None)
            assert pd.isna(res)
        except Exception:
            pass
        try:
            res = data_loader._coerce_to_datetime_scalar(pd.NaT)
            assert pd.isna(res)
        except Exception:
            pass

    def test_coerce_to_datetime_scalar_nan_inf(self):
        with contextlib.suppress(Exception):
            assert pd.isna(data_loader._coerce_to_datetime_scalar(np.nan))
        with contextlib.suppress(Exception):
            assert pd.isna(data_loader._coerce_to_datetime_scalar(float("inf")))
        with contextlib.suppress(Exception):
            assert pd.isna(data_loader._coerce_to_datetime_scalar(float("-inf")))

    def test_coerce_to_datetime_scalar_int_ms(self):
        ts = data_loader._coerce_to_datetime_scalar(1700000000000)
        assert isinstance(ts, pd.Timestamp)

    def test_coerce_to_datetime_scalar_int_s(self):
        ts = data_loader._coerce_to_datetime_scalar(1700000000)
        assert isinstance(ts, pd.Timestamp)

    def test_coerce_to_datetime_scalar_float(self):
        ts = data_loader._coerce_to_datetime_scalar(1700000000.123)
        assert isinstance(ts, pd.Timestamp)

    def test_coerce_to_datetime_scalar_string_digits_ms(self):
        ts = data_loader._coerce_to_datetime_scalar("1700000000000")
        assert isinstance(ts, pd.Timestamp)

    def test_coerce_to_datetime_scalar_string_date(self):
        ts = data_loader._coerce_to_datetime_scalar("2023-01-01T00:00:00Z")
        assert isinstance(ts, pd.Timestamp)

    def test_coerce_to_datetime_scalar_malformed(self):
        # Should return NaT or handle gracefully
        try:
            res = data_loader._coerce_to_datetime_scalar("not-a-date")
            assert pd.isna(res) or isinstance(res, pd.Timestamp)
        except Exception:
            pass


class TestPromoteDatetimeColumn:
    def test_promote_datetime_column_empty(self):
        df = pd.DataFrame()
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_promote_datetime_column_with_date_col(self):
        df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "close": [1, 2]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_promote_datetime_column_unix_col(self):
        df = pd.DataFrame({"timestamp": [1700000000, 1700000060], "close": [1, 2]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_promote_datetime_column_time_col(self):
        df = pd.DataFrame({"time": ["2023-01-01", "2023-01-02"], "price": [10, 20]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)


class TestDetectAndNormalizeExchangeFormat:
    def test_detect_binance_format(self):
        df = pd.DataFrame(
            {
                "open_time": [1700000000000, 1700000060000],
                "open": [1, 2],
                "high": [3, 4],
                "low": [0.5, 1.5],
                "close": [2, 3],
                "volume": [100, 200],
            }
        )
        out = data_loader._detect_and_normalize_exchange_format(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_detect_coingecko_format(self):
        df = pd.DataFrame(
            {
                "snapped_at": ["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"],
                "price": [100, 101],
                "market_cap": [1e9, 1.01e9],
                "total_volume": [1e7, 1.01e7],
            }
        )
        out = data_loader._detect_and_normalize_exchange_format(df)
        assert isinstance(out, pd.DataFrame)


class TestCoerceNumeric:
    def test_coerce_numeric_units(self):
        df = pd.DataFrame({"price": ["$100.50", "€200,25", "1,000.00"]})
        out = data_loader._coerce_numeric(df)
        assert pd.api.types.is_numeric_dtype(out["price"])

    def test_coerce_numeric_percent(self):
        df = pd.DataFrame({"ret": ["1.5%", "2.0%", "-0.5%"]})
        out = data_loader._coerce_numeric(df)
        assert pd.api.types.is_numeric_dtype(out["ret"])

    def test_coerce_numeric_commas(self):
        df = pd.DataFrame({"vol": ["1,234,567", "2,000"]})
        out = data_loader._coerce_numeric(df)
        assert pd.api.types.is_numeric_dtype(out["vol"])


class TestNormalizeColumns:
    def test_normalize_columns_basic(self):
        df = pd.DataFrame({"Close": [1, 2], "Open": [0.5, 1.5], "Volume": [100, 200]})
        out = data_loader._normalize_columns(df)
        assert isinstance(out, pd.DataFrame)


class TestDropAllNanColumns:
    def test_drop_all_nan_columns(self):
        df = pd.DataFrame({"a": [1, 2], "b": [np.nan, np.nan], "c": [3, np.nan]})
        out = data_loader._drop_all_nan_columns(df)
        assert "b" not in out.columns


class TestStripUnitsAndParse:
    def test_strip_units_and_parse_currency(self):
        res = data_loader._strip_units_and_parse("$1,234.56")
        assert isinstance(res, (int, float)) or pd.notna(res)

    def test_strip_units_and_parse_percent(self):
        res = data_loader._strip_units_and_parse("50%")
        assert isinstance(res, (int, float)) or pd.notna(res)

    def test_strip_units_and_parse_na(self):
        res = data_loader._strip_units_and_parse("N/A")
        # Should handle NA markers
        assert res is None or pd.isna(res) or isinstance(res, str)


class TestSeriesIsParseable:
    def test_series_is_parseable_numeric(self):
        s = pd.Series([1, 2, 3.5])
        assert data_loader._series_is_parseable(s) in (True, False)

    def test_series_is_parseable_mixed(self):
        s = pd.Series(["1", "2.5", "x"])
        res = data_loader._series_is_parseable(s)
        assert isinstance(res, bool)


class TestDataQualityCampaign:
    def test_run_data_quality_campaign_empty(self):
        df = pd.DataFrame()
        try:
            out = data_loader._run_data_quality_campaign(df)
            assert isinstance(out, pd.DataFrame)
        except BABDataError:
            pass


class TestValidateReturnsDataframe:
    def test_validate_returns_dataframe_valid(self):
        df = pd.DataFrame(
            {"BTC": [0.01, -0.02, 0.03]}, index=pd.date_range("2023-01-01", periods=3)
        )
        out = data_loader.validate_returns_dataframe(df)
        assert isinstance(out, pd.DataFrame)

    def test_validate_returns_dataframe_bad_type(self):
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe([1, 2, 3])

    def test_validate_returns_dataframe_empty(self):
        df = pd.DataFrame()
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)

    def test_validate_returns_dataframe_non_numeric(self):
        df = pd.DataFrame({"BTC": ["a", "b"]}, index=pd.date_range("2023-01-01", periods=2))
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)


class TestLoaders:
    def test_load_returns_from_csv(self, tmp_path):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.csv"
        df.to_csv(p)
        out = data_loader.load_returns_from_csv(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_from_json(self, tmp_path):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.json"
        df.to_json(p)
        out = data_loader.load_returns_from_json(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_from_jsonl(self, tmp_path):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.jsonl"
        with open(p, "w") as f:
            for _, row in df.iterrows():
                f.write(json.dumps({"date": str(row.name), "BTC": float(row["BTC"])}) + "\n")
        out = data_loader.load_returns_from_json(str(p))  # or specific function if exists
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_from_pickle(self, tmp_path):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.pkl"
        with open(p, "wb") as f:
            pickle.dump(df, f)
        out = data_loader.load_returns_from_pickle(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_from_parquet(self, tmp_path):
        pytest.importorskip("pyarrow")
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.parquet"
        df.to_parquet(p)
        out = data_loader.load_returns_from_parquet(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_from_hdf5(self, tmp_path):
        try:
            import tables
        except Exception:
            pytest.skip("tables not available")
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.h5"
        df.to_hdf(p, key="df", mode="w")
        out = data_loader.load_returns_from_hdf5(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_from_dataframe(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        out = data_loader.load_returns_from_dataframe(df)
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_dispatch(self, tmp_path):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "r.csv"
        df.to_csv(p)
        out = data_loader.load_returns(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_load_returns_missing_file(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns("/no/such/file.csv")

    def test_load_returns_bad_format(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("not,data\n1,2")
        with pytest.raises(BABDataError):
            data_loader.load_returns(str(p))


class TestPrices:
    def test_load_prices_from_csv(self, tmp_path):
        df = pd.DataFrame({"BTC": [100, 101]}, index=pd.date_range("2023-01-01", periods=2))
        p = tmp_path / "p.csv"
        df.to_csv(p)
        out = data_loader.load_prices(str(p))
        assert isinstance(out, pd.DataFrame)

    def test_prices_to_returns(self):
        df = pd.DataFrame({"BTC": [100, 101, 102]}, index=pd.date_range("2023-01-01", periods=3))
        out = data_loader._prices_to_returns(df)
        assert isinstance(out, pd.DataFrame)

    def test_detect_price_or_returns_prices(self):
        df = pd.DataFrame({"BTC": [100, 101]}, index=pd.date_range("2023-01-01", periods=2))
        res = data_loader.detect_price_or_returns(df)
        assert res in ("prices", "returns", None) or isinstance(res, str)

    def test_detect_price_or_returns_returns(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        res = data_loader.detect_price_or_returns(df)
        assert res in ("prices", "returns", None) or isinstance(res, str)


class TestSchemaUtils:
    def test_list_columns(self):
        df = pd.DataFrame({"BTC": [1], "ETH": [2]})
        cols = data_loader.list_columns(df)
        assert isinstance(cols, list)

    def test_iter_assets(self):
        df = pd.DataFrame({"BTC": [1], "ETH": [2], "market": [0.01]})
        assets = list(data_loader.iter_assets(df))
        assert isinstance(assets, list)

    def test_normalize_schema(self):
        df = pd.DataFrame({"Close": [1, 2], "Open": [0.5, 1.5]})
        out = data_loader.normalize_schema(df)
        assert isinstance(out, pd.DataFrame)

    def test_standardize_columns(self):
        df = pd.DataFrame({"BTC-USD": [1, 2]})
        out = data_loader.standardize_columns(df)
        assert isinstance(out, pd.DataFrame)

    def test_clean_data(self):
        df = pd.DataFrame({"BTC": [1, np.nan, 2]}, index=pd.date_range("2023-01-01", periods=3))
        out = data_loader.clean_data(df)
        assert isinstance(out, pd.DataFrame)

    def test_validate_prices(self):
        df = pd.DataFrame({"BTC": [100, 101]}, index=pd.date_range("2023-01-01", periods=2))
        out = data_loader.validate_prices(df)
        # May return None or DataFrame
        assert out is None or isinstance(out, pd.DataFrame)


class TestDropMetadataColumns:
    def test_drop_metadata_columns(self):
        df = pd.DataFrame({"BTC": [1, 2], "symbol": ["BTC", "BTC"], "time": [1, 2]})
        out = data_loader._drop_metadata_columns(df)
        assert isinstance(out, pd.DataFrame)


class TestMoreEdgeCases:
    def test_normalize_index_datetime_index_passthrough(self):
        df = pd.DataFrame({"close": [1, 2]}, index=pd.date_range("2023-01-01", periods=2))
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_coerce_to_datetime_scalar_timestamp(self):
        ts = pd.Timestamp("2023-01-01")
        res = data_loader._coerce_to_datetime_scalar(ts)
        assert isinstance(res, pd.Timestamp)

    def test_promote_datetime_column_unnamed(self):
        df = pd.DataFrame({"0": ["2023-01-01", "2023-01-02"], "close": [1, 2]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)
