import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    load_prices,
    load_returns,
    load_returns_from_csv,
    load_returns_from_dataframe,
    load_returns_from_hdf5,
    load_returns_from_json,
    load_returns_from_parquet,
    load_returns_from_pickle,
    load_returns_from_prices,
    validate_returns_dataframe,
)


def test_validate_returns_dataframe_none():
    with pytest.raises(BABDataError):
        validate_returns_dataframe(None)


def test_validate_returns_dataframe_not_dataframe():
    with pytest.raises(BABDataError):
        validate_returns_dataframe([1, 2, 3])


def test_validate_returns_dataframe_empty():
    with pytest.raises(BABDataError):
        validate_returns_dataframe(pd.DataFrame())


def test_validate_returns_dataframe_insufficient_rows():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, min_rows=10)


def test_validate_returns_dataframe_infinite_values():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, np.inf, 0.02], "ETH": [0.01, 0.02, 0.03]}, index=idx)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df)


def test_validate_returns_dataframe_benchmark_missing():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"ETH": [0.01, 0.02, 0.03]}, index=idx)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_validate_returns_dataframe_benchmark_all_nan():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [np.nan, np.nan, np.nan], "ETH": [0.01, 0.02, 0.03]}, index=idx)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_validate_returns_dataframe_only_benchmark():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_load_returns_from_csv_file_not_found(tmp_path):
    with pytest.raises(BABDataError):
        load_returns_from_csv(tmp_path / "missing.csv")


def test_load_returns_from_csv_bad_parse(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("bad,data\nnot,a,datetime")
    with pytest.raises(BABDataError):
        load_returns_from_csv(p)


def test_load_returns_from_json_file_not_found(tmp_path):
    with pytest.raises(BABDataError):
        load_returns_from_json(tmp_path / "missing.json")


def test_load_returns_from_json_bad_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(BABDataError):
        load_returns_from_json(p)


def test_load_returns_from_parquet_not_found(tmp_path):
    with pytest.raises(BABDataError):
        load_returns_from_parquet(tmp_path / "missing.parquet")


def test_load_returns_from_hdf5_not_found(tmp_path):
    with pytest.raises(BABDataError):
        load_returns_from_hdf5(tmp_path / "missing.h5")


def test_load_returns_from_pickle_not_found(tmp_path):
    with pytest.raises(BABDataError):
        load_returns_from_pickle(tmp_path / "missing.pkl")


def test_load_returns_from_pickle_dict(tmp_path):
    p = tmp_path / "data.pkl"
    idx = pd.date_range("2023-01-01", periods=3)
    obj = {"date": idx, "BTC": [0.01, 0.02, 0.03], "ETH": [0.01, 0.015, 0.02]}
    with p.open("wb") as f:
        pickle.dump(obj, f)
    df = load_returns_from_pickle(p)
    assert isinstance(df.index, pd.DatetimeIndex)


def test_load_returns_from_pickle_dataframe(tmp_path):
    p = tmp_path / "data.pkl"
    idx = pd.date_range("2023-01-01", periods=3)
    obj = pd.DataFrame({"BTC": [0.01, 0.02, 0.03], "ETH": [0.01, 0.015, 0.02]}, index=idx)
    with p.open("wb") as f:
        pickle.dump(obj, f)
    df = load_returns_from_pickle(p)
    assert "BTC" in df.columns


def test_load_returns_from_pickle_bad_type(tmp_path):
    p = tmp_path / "bad.pkl"
    with p.open("wb") as f:
        pickle.dump([1, 2, 3], f)
    with pytest.raises(BABDataError):
        load_returns_from_pickle(p)


def test_load_returns_json_orient_records(tmp_path):
    p = tmp_path / "data.json"
    # records style
    data = [
        {"date": "2023-01-01", "BTC": 0.01, "ETH": 0.02},
        {"date": "2023-01-02", "BTC": 0.01, "ETH": 0.01},
        {"date": "2023-01-03", "BTC": -0.01, "ETH": 0.02},
    ]
    p.write_text(json.dumps(data))
    df = load_returns_from_json(p, orient="records")
    assert "BTC" in df.columns


def test_load_returns_dispatch_dataframe():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01], "ETH": [0.01, 0.01, 0.02]}, index=idx)
    out = load_returns(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_dispatch_unsupported(tmp_path):
    p = tmp_path / "bad.xyz"
    p.write_text("x")
    with pytest.raises(BABDataError):
        load_returns(p)


def test_load_prices_short():
    idx = pd.date_range("2023-01-01", periods=1)
    df = pd.DataFrame({"BTC": [100]}, index=idx)
    with pytest.raises(BABDataError):
        load_prices(df)


def test_load_prices_dataframe():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [100, 101, 102], "ETH": [10, 10.1, 10.2]}, index=idx)
    out = load_prices(df)
    assert "BTC" in out.columns


def test_load_prices_csv(tmp_path):
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [100, 101, 102], "ETH": [10, 10.1, 10.2]}, index=idx)
    p = tmp_path / "prices.csv"
    df.to_csv(p)
    out = load_prices(p)
    assert "BTC" in out.columns


def test_load_prices_json(tmp_path):
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [100, 101, 102], "ETH": [10, 10.1, 10.2]}, index=idx)
    p = tmp_path / "prices.json"
    df.to_json(p, date_format='iso')
    out = load_prices(p)
    assert "BTC" in out.columns


def test_load_prices_unsupported(tmp_path):
    p = tmp_path / "prices.txt"
    p.write_text("x")
    with pytest.raises(BABDataError):
        load_prices(p)


def test_aliases():
    assert load_returns_from_prices is load_prices


def test_promote_datetime_column_unnamed(tmp_path):
    # CSV with unnamed date column
    p = tmp_path / "test.csv"
    p.write_text(" ,BTC,ETH\n2023-01-01,0.01,0.02\n2023-01-02,0.01,0.01\n2023-01-03,-0.01,0.02\n")
    df = load_returns_from_csv(p)
    assert isinstance(df.index, pd.DatetimeIndex)


def test_coerce_numeric_percent_and_commas():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": ["1.5%", "2,000.00", "0.01"], "ETH": [0.01, 0.02, 0.03]}, index=idx)
    out = validate_returns_dataframe(df)
    assert out["BTC"].iloc[0] == 0.015


def test_coerce_numeric_na_markers():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": ["NA", "0.02", "0.03"], "ETH": [0.01, 0.02, 0.03]}, index=idx)
    out = validate_returns_dataframe(df)
    assert np.isnan(out["BTC"].iloc[0])


def test_drop_all_nan_columns():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03], "DELIST": [np.nan, np.nan, np.nan]}, index=idx)
    out = validate_returns_dataframe(df)
    assert "DELIST" not in out.columns


def test_all_nan_columns_raises():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"A": [np.nan, np.nan, np.nan], "B": [np.nan, np.nan, np.nan]}, index=idx)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df)


def test_tz_aware_index_normalized():
    idx = pd.date_range("2023-01-01", periods=3, tz="UTC")
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03], "ETH": [0.01, 0.01, 0.02]}, index=idx)
    out = validate_returns_dataframe(df)
    assert out.index.tz is None


def test_duplicate_index_removed():
    idx = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03], "ETH": [0.01, 0.01, 0.02]}, index=idx)
    out = validate_returns_dataframe(df)
    assert len(out) == 2
