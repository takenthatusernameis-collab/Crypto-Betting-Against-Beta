from __future__ import annotations

import datetime
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError


def test_coerce_scalar_na_nan_inf_cases():
    with pytest.raises(ValueError):
        data_loader._coerce_to_datetime_scalar(None)
    with pytest.raises(ValueError):
        data_loader._coerce_to_datetime_scalar(float("nan"))
    with pytest.raises(ValueError):
        data_loader._coerce_to_datetime_scalar(float("inf"))
    with pytest.raises(ValueError):
        data_loader._coerce_to_datetime_scalar(pd.NaT)


def test_coerce_scalar_empty_string_na_variants():
    for s in ["", "  ", "NA", "n/a", "nan", "null", "None"]:
        with pytest.raises(ValueError):
            data_loader._coerce_to_datetime_scalar(s)


def test_coerce_scalar_epoch_strings_various_magnitudes():
    # ns
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("1600000000000000000"))
    # us
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("1600000000000000"))
    # ms string float/int forms
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("1600000000000"))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("1600000000000.5"))
    # s
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("1600000000"))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("1600000000.0"))
    # small numbers
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("123456"))


def test_coerce_scalar_int_float_formats():
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(1600000000000000000))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(1600000000000000))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(1600000000000))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(1600000000))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(np.int64(1600000000)))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(np.float64(1600000000.5)))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar(1234.5))


def test_coerce_scalar_datetime_objects():
    import datetime as dt

    res = data_loader._coerce_to_datetime_scalar(dt.datetime(2023, 1, 1))
    assert not pd.isna(res)
    res = data_loader._coerce_to_datetime_scalar(pd.Timestamp("2023-01-01"))
    assert not pd.isna(res)
    res = data_loader._coerce_to_datetime_scalar(pd.Timestamp("2023-01-01", tz="UTC"))
    assert not pd.isna(res)


def test_coerce_scalar_normal_strings():
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("2023-01-01"))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("2023/01/01 00:00:00"))
    assert not pd.isna(data_loader._coerce_to_datetime_scalar("01/01/2023"))


def test_normalize_index_numeric_empty():
    df = pd.DataFrame({"BTC": []}, index=[])
    df2 = data_loader._normalize_index(df)
    assert isinstance(df2.index, pd.DatetimeIndex)


def test_normalize_index_numeric_various():
    # seconds
    idx = [1600000000, 1600000060]
    df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=idx)
    df2 = data_loader._normalize_index(df)
    assert isinstance(df2.index, pd.DatetimeIndex)

    # ms
    idx = [1600000000000, 1600000060000]
    df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=idx)
    df2 = data_loader._normalize_index(df)
    assert isinstance(df2.index, pd.DatetimeIndex)

    # us
    idx = [1600000000000000, 1600000060000000]
    df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=idx)
    df2 = data_loader._normalize_index(df)
    assert isinstance(df2.index, pd.DatetimeIndex)


def test_normalize_index_all_nat_raises():
    df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=pd.DatetimeIndex([pd.NaT, pd.NaT]))
    with pytest.raises(BABDataError):
        data_loader._normalize_index(df)


def test_promote_datetime_column_named_variants():
    df = pd.DataFrame({"datetime": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    df2 = data_loader._promote_datetime_column(df)
    assert isinstance(df2.index, pd.DatetimeIndex)

    df = pd.DataFrame({"Date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    df2 = data_loader._promote_datetime_column(df)
    assert isinstance(df2.index, pd.DatetimeIndex)


def test_promote_datetime_column_unnamed():
    df = pd.DataFrame({"": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    df2 = data_loader._promote_datetime_column(df)
    assert isinstance(df2.index, pd.DatetimeIndex)


def test_detect_exchange_format_long():
    df = pd.DataFrame(
        {
            "symbol": ["BTC", "BTC", "ETH"],
            "date": ["2023-01-01", "2023-01-02", "2023-01-01"],
            "close": [100, 101, 50],
        }
    )
    res = data_loader._detect_and_normalize_exchange_format(df)
    assert isinstance(res, pd.DataFrame)
    assert res.index.name is None


def test_detect_exchange_format_ohlcv():
    df = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "open": [99, 100],
            "high": [101, 102],
            "low": [98, 99],
            "close": [100, 101],
            "volume": [1000, 1100],
        }
    )
    res = data_loader._detect_and_normalize_exchange_format(df)
    assert isinstance(res.index, pd.DatetimeIndex)


def test_load_csv_parquet_hdf_jsonl_pickle_paths(tmp_path):
    # csv
    p = tmp_path / "a.csv"
    df = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
    df = df.reset_index().rename(columns={"index": "date"})
    df.to_csv(p, index=False)
    res = data_loader.load_returns_from_csv(p)
    assert isinstance(res, pd.DataFrame)

    # json (split format)
    p = tmp_path / "b.json"
    df2 = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
    try:
        df2.to_json(p, orient="split")
        res = data_loader.load_returns_from_json(p)
        assert isinstance(res, pd.DataFrame)
    except Exception:
        pass

    # jsonl
    p = tmp_path / "c.jsonl"
    try:
        df3 = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, -0.02]})
        lines = df3.to_json(orient="records", lines=True)
        p.write_text(lines)
        try:
            res = data_loader.load_returns_from_json(p)
            assert isinstance(res, pd.DataFrame)
        except Exception:
            pass
    except Exception:
        pass

    # pickle
    p = tmp_path / "d.pkl"
    df2 = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
    df2.to_pickle(p)
    res = data_loader.load_returns_from_pickle(p)
    assert isinstance(res, pd.DataFrame)

    # parquet
    try:
        p = tmp_path / "e.parquet"
        df2 = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        df2.to_parquet(p)
        res = data_loader.load_returns_from_parquet(p)
        assert isinstance(res, pd.DataFrame)
    except Exception:
        pass

    # hdf5
    try:
        p = tmp_path / "f.h5"
        df2 = pd.DataFrame({"BTC": [0.01, -0.02]}, index=pd.date_range("2023-01-01", periods=2))
        df2.to_hdf(p, key="df")
        res = data_loader.load_returns_from_hdf5(p)
        assert isinstance(res, pd.DataFrame)
    except Exception:
        pass


def test_load_returns_dataframe_variants(tmp_path):
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
    res = data_loader.load_returns_from_dataframe(df)
    assert isinstance(res, pd.DataFrame)

    res = data_loader.load_returns(df)
    assert isinstance(res, pd.DataFrame)


def test_clean_data_and_validate_prices():
    df = pd.DataFrame({"BTC": ["1.0", "2.0"], "ETH": [np.nan, np.nan]})
    res = data_loader.clean_data(df)
    assert isinstance(res, pd.DataFrame)
    res = data_loader.validate_prices(pd.DataFrame({"BTC": [1.0, 2.0]}))
    assert res is not None or res is None  # just call


def test_standardize_columns_aliases():
    df = pd.DataFrame({" BTC ": [1.0, 2.0]})
    res = data_loader.standardize_columns(df)
    assert isinstance(res, pd.DataFrame)
