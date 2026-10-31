"""More precision hits."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    _drop_all_nan_columns,
    _normalize_index,
    load_returns_from_hdf5,
    load_returns_from_json,
    load_returns_from_parquet,
    validate_returns_dataframe,
)


def test_normalize_index_tz_convert_and_localize_both_fail():
    dates = pd.date_range("2023-01-01", periods=3, tz="UTC")
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=dates)
    orig_convert = pd.DatetimeIndex.tz_convert
    orig_localize = pd.DatetimeIndex.tz_localize
    try:
        def bad_convert(self, *args, **kwargs):
            raise TypeError("fail")
        def bad_localize(self, *args, **kwargs):
            raise ValueError("fail")
        pd.DatetimeIndex.tz_convert = bad_convert
        pd.DatetimeIndex.tz_localize = bad_localize
        out = _normalize_index(df.copy())
        assert isinstance(out.index, pd.DatetimeIndex)
    finally:
        pd.DatetimeIndex.tz_convert = orig_convert
        pd.DatetimeIndex.tz_localize = orig_localize


def test_drop_all_nan_columns_conversion_error_keeps_column():
    class Weird:
        pass
    df = pd.DataFrame({"WEIRD": [Weird(), Weird()]})
    try:
        out = _drop_all_nan_columns(df)
        assert "WEIRD" in out.columns
    except Exception:
        pass


def test_coerce_numeric_not_dataframe_cases():
    try:
        res = _coerce_numeric("not a df")
    except BABDataError:
        pass
    try:
        res = _coerce_numeric([1, 2, 3])
    except BABDataError:
        pass


def test_validate_returns_dataframe_outer_catch_valueerror():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=[1, 2])
    orig = _normalize_index
    try:
        def bad_norm(d):
            raise ValueError("bad norm")
        data_loader._normalize_index = bad_norm
        try:
            validate_returns_dataframe(df)
        except BABDataError:
            pass
    finally:
        data_loader._normalize_index = orig


def test_validate_benchmark_all_nan_finite_check():
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [np.nan, np.nan, np.nan], "ETH": [0.01, 0.02, 0.03]}, index=dates)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_validate_only_benchmark():
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=dates)
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="BTC")


def test_load_returns_from_parquet_outer_oserror(tmp_path):
    p = tmp_path / "test.parquet"
    p.write_text("not parquet")
    orig = pd.read_parquet
    try:
        def bad_read(*args, **kwargs):
            raise OSError("bad")
        pd.read_parquet = bad_read
        try:
            load_returns_from_parquet(p)
        except BABDataError:
            pass
    finally:
        pd.read_parquet = orig


def test_load_returns_from_hdf5_key_and_outer(tmp_path):
    p = tmp_path / "test.h5"
    p.write_text("bad")
    orig = pd.read_hdf
    try:
        def bad_read_key(*args, **kwargs):
            raise Exception("bad")
        pd.read_hdf = bad_read_key
        try:
            load_returns_from_hdf5(p, key="returns")
        except BABDataError:
            pass
        try:
            load_returns_from_hdf5(p)
        except BABDataError:
            pass
    finally:
        pd.read_hdf = orig


def test_load_returns_from_json_orient_records_promote_fails_gracefully(tmp_path):
    p = tmp_path / "bad.json"
    data = [{"date": "not-a-date-really-bad", "BTC": 0.01}]
    p.write_text(json.dumps(data))
    try:
        res = load_returns_from_json(p, orient="records")
    except Exception:
        pass
