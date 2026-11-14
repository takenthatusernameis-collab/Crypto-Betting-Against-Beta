import io
import json
import os
import pickle
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    _coerce_series_to_datetime_index,
    _coerce_to_datetime_scalar,
    _detect_and_normalize_exchange_format,
    _drop_all_nan_columns,
    _drop_metadata_columns,
    _is_likely_returns,
    _normalize_asset_name,
    _normalize_columns,
    _normalize_index,
    _prices_to_returns,
    _promote_datetime_column,
    _run_data_quality_campaign,
    _series_has_any_finite,
    _strip_units_and_parse,
    clean_data,
    detect_price_or_returns,
    iter_assets,
    list_columns,
    load_prices,
    load_returns,
    load_returns_from_csv,
    load_returns_from_dataframe,
    load_returns_from_hdf5,
    load_returns_from_json,
    load_returns_from_parquet,
    load_returns_from_pickle,
    normalize_schema,
    standardize_columns,
    validate_prices,
    validate_returns_dataframe,
)


# Cover _normalize_index empty numeric index
def test_normalize_index_empty_numeric_index():
    df = pd.DataFrame({"BTC": []})
    df.index = pd.Index([], dtype="float64")
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert len(out) == 0


# Cover _normalize_index numeric epoch branches
def test_normalize_index_numeric_ns():
    idx = [1600000000000000000, 1600000000000000001]  # ns
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_us():
    idx = [1600000000000000, 1600000000000001]  # us
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_ms():
    idx = [1600000000000, 1600000000001]  # ms
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_s():
    idx = [1600000000, 1600000001]  # s
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_numeric_small():
    idx = [1, 2, 3]
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


# _coerce_to_datetime_scalar branches
def test_coerce_scalar_string_iso():
    assert isinstance(_coerce_to_datetime_scalar("2023-01-01"), pd.Timestamp)


def test_coerce_scalar_string_us_format():
    assert isinstance(_coerce_to_datetime_scalar("2023/01/01 12:00:00"), pd.Timestamp)


def test_coerce_scalar_int_seconds():
    assert isinstance(_coerce_to_datetime_scalar(1600000000), pd.Timestamp)


def test_coerce_scalar_float_ms():
    assert isinstance(_coerce_to_datetime_scalar(1600000000000.0), pd.Timestamp)


def test_coerce_scalar_nat_raises():
    with pytest.raises((ValueError, Exception)):
        _coerce_to_datetime_scalar(pd.NaT)


def test_coerce_scalar_none_raises():
    with pytest.raises(Exception):
        _coerce_to_datetime_scalar(None)


def test_coerce_scalar_garbage_raises():
    with pytest.raises(Exception):
        _coerce_to_datetime_scalar("not-a-date!!!")
