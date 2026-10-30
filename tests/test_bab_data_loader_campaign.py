"""Campaign tests for data_loader.py edge and error paths."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    _drop_all_nan_columns,
    _normalize_index,
    _normalize_columns,
    _prices_to_returns,
    _promote_datetime_column,
    load_returns,
    load_prices,
    validate_returns_dataframe,
)


def _make_df():
    idx = pd.date_range("2023-01-01", periods=40, freq="D")
    rng = np.random.default_rng(3)
    return pd.DataFrame(
        {"BTC": rng.normal(0, 0.01, 40), "ETH": 0.9 * rng.normal(0, 0.01, 40)},
        index=idx,
    )


def test_validate_unparseable_index_raises():
    df = pd.DataFrame({"BTC": [0.01] * 5}, index=["not-a-date", "also-bad", "x", "y", "z"])
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df)


def test_validate_tz_aware_index_rounds_trip():
    idx = pd.date_range("2023-01-01", periods=20, freq="D", tz="US/Eastern")
    df = _make_df().iloc[:20].copy()
    df.index = idx
    out = validate_returns_dataframe(df, benchmark="BTC")
    assert out.index.tz is None


def test_validate_duplicate_index_dedupes():
    idx = pd.date_range("2023-01-01", periods=5, freq="D").append(
        pd.date_range("2023-01-01", periods=3, freq="D")
    )
    df = pd.DataFrame(
        {"BTC": np.arange(8, dtype=float) * 0.01, "ETH": np.arange(8, dtype=float) * 0.02},
        index=idx,
    )
    out = validate_returns_dataframe(df, benchmark="BTC")
    assert not out.index.has_duplicates
    assert len(out) == 5


def test_promote_datetime_column_date_named_promoted():
    df = pd.DataFrame(
        {"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
    )
    out = _promote_datetime_column(df)
    assert list(out.index) == ["2023-01-01", "2023-01-02"]


def test_promote_datetime_column_unnamed_nondate():
    df = pd.DataFrame(
        {0: ["apple", "banana"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
    )
    out = _promote_datetime_column(df)
    assert not isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_column_unnamed_with_nat_skips():
    df = pd.DataFrame(
        {0: ["2023-01-01", None], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
    )
    out = _promote_datetime_column(df)
    assert not isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_column_unnamed_nondate():
    df = pd.DataFrame(
        {0: ["apple", "banana"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
    )
    out = _promote_datetime_column(df)
    assert "date" not in out.columns


def test_normalize_index_not_datetime_after_coercion():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=[[1, 2], [3, 4]])
    with pytest.raises(BABDataError):
        _normalize_index(df)


def test_drop_all_nan_columns_typeerror_path():
    df = pd.DataFrame({"BTC": [{"a": 1}, {"b": 2}], "ETH": [0.01, 0.02]})
    out = _drop_all_nan_columns(df)
    assert "ETH" in out.columns


def test_drop_all_nan_columns_all_nan_raises():
    df = pd.DataFrame({"BTC": [np.nan, np.nan], "ETH": [np.nan, np.nan]})
    with pytest.raises(BABDataError):
        _drop_all_nan_columns(df)


def test_coerce_numeric_percent_bad_value():
    df = pd.DataFrame({"BTC": ["1.5%", "abc%"], "ETH": [0.01, 0.02]})
    out = _coerce_numeric(df)
    assert np.isnan(out["BTC"].iloc[1])


def test_coerce_numeric_decimal_comma():
    df = pd.DataFrame({"BTC": ["1,5", "2,5"], "ETH": [0.01, 0.02]})
    out = _coerce_numeric(df)
    assert out["BTC"].iloc[0] == 15.0


def test_coerce_numeric_non_numeric_column_raises():
    df = pd.DataFrame({"BTC": [[1, 2], [3, 4]], "ETH": [0.01, 0.02]})
    with pytest.raises(BABDataError):
        _coerce_numeric(df)


def test_validate_benchmark_missing_raises():
    df = _make_df()
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="XRP")


def test_validate_benchmark_all_nan_raises():
    df = _make_df().copy()
    df["BTC"] = np.nan
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_validate_only_benchmark_raises():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_load_returns_unsupported_extension():
    with pytest.raises(BABDataError):
        load_returns("data.xyz")


def test_load_prices_unsupported_type():
    with pytest.raises(BABDataError):
        load_prices(123)


def test_load_prices_df_too_short():
    df = pd.DataFrame({"BTC": [100.0]}, index=pd.date_range("2023-01-01", periods=1))
    with pytest.raises(BABDataError):
        load_prices(df)


def test_load_returns_from_pickle_unsupported_type(tmp_path):
    import pickle

    p = tmp_path / "int.pkl"
    with p.open("wb") as handle:
        pickle.dump(7, handle)
    with pytest.raises(BABDataError):
        load_returns(p)


def test_load_returns_parquet_read_error(tmp_path):
    p = tmp_path / "bad.parquet"
    p.write_bytes(b"not a parquet file")
    with pytest.raises(BABDataError):
        load_returns(p)


def test_load_returns_hdf5_read_error(tmp_path):
    p = tmp_path / "bad.h5"
    p.write_bytes(b"not an hdf5 file")
    with pytest.raises(BABDataError):
        load_returns(p)


def test_json_records_bad_date_column(tmp_path):
    p = tmp_path / "r.json"
    data = [{"date": "not-a-date", "BTC": 0.01}, {"date": "nope", "BTC": 0.02}]
    p.write_text(json.dumps(data))
    with pytest.raises(BABDataError):
        load_returns(p, benchmark="BTC", orient="records")


def test_csv_missing_file_raises():
    with pytest.raises(BABDataError):
        load_returns("does_not_exist.csv")


def test_csv_is_directory_raises(tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    with pytest.raises(BABDataError):
        load_returns(d)


def test_normalize_columns_duplicate_raises():
    df = pd.DataFrame([[1, 2]], columns=["BTC", "BTC"])
    with pytest.raises(BABDataError):
        _normalize_columns(df)


def test_prices_to_returns_too_short():
    df = pd.DataFrame({"BTC": [100.0]}, index=pd.date_range("2023-01-01", periods=1))
    with pytest.raises(BABDataError):
        _prices_to_returns(df)
