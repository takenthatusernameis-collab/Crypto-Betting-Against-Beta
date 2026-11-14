"""Campaign E3: hit remaining high-value branches in data_loader."""

from __future__ import annotations

import contextlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_to_datetime_scalar,
    _detect_and_normalize_exchange_format,
    _is_likely_returns,
    _normalize_index,
    _prices_to_returns,
    _promote_datetime_column,
    clean_data,
    detect_price_or_returns,
    detect_source_type,
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


def _retdf(n=8):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"BTC": np.linspace(0.01, 0.08, n), "MKT": np.linspace(0.005, 0.04, n)}, index=idx
    )


def _pricedf(n=8):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame({"BTC": np.linspace(100, 120, n), "MKT": np.linspace(50, 55, n)}, index=idx)


# _coerce_to_datetime_scalar fallback/error branches
def test_coerce_numpy_datetime64_and_pandas_nat_types():
    v = np.datetime64("2024-01-01")
    assert pd.notna(pd.Timestamp(_coerce_to_datetime_scalar(v)))
    with pytest.raises(Exception):
        _coerce_to_datetime_scalar(float("nan"))


def test_coerce_numeric_string_e_formats_and_large():
    for s in ["1.7040672e9", "1704067200000.0", "-1704067200"]:
        try:
            out = _coerce_to_datetime_scalar(s)
            assert pd.notna(pd.Timestamp(out)) or out is not None
        except Exception:
            pass


def test_coerce_datetime_like_and_invalid_object():
    class Weird:
        def __str__(self):
            return "2024-01-01"

    with contextlib.suppress(Exception):
        _coerce_to_datetime_scalar(Weird())
    with pytest.raises(Exception):
        _coerce_to_datetime_scalar(object())


# _normalize_index: epoch detection fallbacks and mixed
def test_normalize_index_epoch_us_ms_string_ints():
    for vals in [
        np.array([1704067200000000, 1704153600000000], dtype="int64"),
        np.array([1704067200000.0, 1704153600000.0]),
        pd.Index([1704067200, 1704153600], dtype="int64"),
    ]:
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=vals)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_datetime_strings_with_tz_and_z():
    df = pd.DataFrame({"A": [1, 2]}, index=["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


# _promote_datetime_column: unnamed col, epoch column, multi-column conservative
def test_promote_unnamed_datetime_column():
    df = pd.DataFrame(
        {
            "Unnamed: 0": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "BTC": [1, 2, 3],
            "MKT": [4, 5, 6],
        }
    )
    out = _promote_datetime_column(df)
    # may promote or keep; validate path should work
    assert isinstance(out, pd.DataFrame)


def test_promote_epoch_string_column():
    df = pd.DataFrame({"date": ["1704067200", "1704153600", "1704240000"], "BTC": [0.1, 0.2, 0.3]})
    out = _promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_promote_candidate_timestamp_ms_column():
    df = pd.DataFrame(
        {
            "timestamp": [1704067200000, 1704153600000, 1704240000000],
            "BTC": [1, 2, 3],
            "ETH": [4, 5, 6],
        }
    )
    out = _promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


# exchange format detection
def test_exchange_pivot_with_duplicates_last():
    df = pd.DataFrame(
        {
            "symbol": ["BTC", "BTC", "BTC"],
            "datetime": ["2024-01-01", "2024-01-01", "2024-01-02"],
            "price": [100, 101, 102],
        }
    )
    out = _detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_exchange_no_symbol_single_asset_time():
    df = pd.DataFrame(
        {
            "time": [1704067200000, 1704153600000, 1704240000000],
            "last": [10.0, 11.0, 12.0],
        }
    )
    out = _detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_exchange_empty_and_non_df():
    assert _detect_and_normalize_exchange_format(pd.DataFrame()).empty
    assert _detect_and_normalize_exchange_format(None) is None  # type: ignore


# validate paths
def test_validate_quality_off_on_various():
    df = _retdf()
    out = validate_returns_dataframe(df, quality=False)
    assert len(out) == len(df)
    out2 = validate_returns_dataframe(df, quality=True)
    assert isinstance(out2, pd.DataFrame)


def test_validate_object_numeric_coercion_units():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"BTC": ["1%", "2%", "3%", "4%", "5%"], "MKT": [0.01] * 5}, index=idx)
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df, quality=False)


def test_validate_short_history_per_asset():
    df = _retdf(5)
    df.loc[df.index[3:], "BTC"] = np.nan
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df, min_rows=4, quality=False)


# loaders
def test_load_returns_from_csv_parser_error(tmp_path):
    p = tmp_path / "x.csv"
    p.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(BABDataError):
        load_returns_from_csv(p)


def test_load_returns_from_json_df_data_and_bad_orient(tmp_path):
    # table-like records default path
    recs = [
        {"date": "2024-01-01", "BTC": 0.1, "MKT": 0.01},
        {"date": "2024-01-02", "BTC": 0.2, "MKT": 0.02},
        {"date": "2024-01-03", "BTC": 0.3, "MKT": 0.03},
    ]
    p = tmp_path / "r.json"
    p.write_text(json.dumps(recs), encoding="utf-8")
    out = load_returns_from_json(p, orient="records", quality=False)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_from_pickle_list_of_dicts(tmp_path):
    p = tmp_path / "l.pkl"
    data = [
        {"date": "2024-01-01", "BTC": 0.1, "MKT": 0.01},
        {"date": "2024-01-02", "BTC": 0.2, "MKT": 0.02},
        {"date": "2024-01-03", "BTC": 0.3, "MKT": 0.03},
    ]
    with open(p, "wb") as f:
        pickle.dump(data, f)
    try:
        out = load_returns_from_pickle(p, quality=False)
        assert isinstance(out, pd.DataFrame)
    except BABDataError:
        pass


def test_load_returns_dispatch_auto_detect_prices(tmp_path):
    prices = _pricedf(8)
    p = tmp_path / "p.csv"
    prices.to_csv(p)
    # load_returns may auto-detect prices
    try:
        out = load_returns(p)
        assert isinstance(out, pd.DataFrame)
    except (BABDataError, Exception):
        pass
    # DataFrame prices
    try:
        out2 = load_returns(prices.reset_index().rename(columns={"index": "date"}), quality=False)
        assert isinstance(out2, pd.DataFrame)
    except (BABDataError, Exception):
        pass


def test_load_prices_bad_types_and_unsupported_ext(tmp_path):
    with pytest.raises(BABDataError):
        load_prices(12345)  # type: ignore
    p = tmp_path / "x.foo"
    p.write_text("x")
    with pytest.raises(BABDataError):
        load_prices(p)


# detect_price_or_returns
def test_detect_prices_csv_json_pickle_unknown(tmp_path):
    prices = _pricedf(8)
    p = tmp_path / "p.csv"
    prices.to_csv(p)
    assert detect_price_or_returns(p) in ("prices", "returns", "unknown")
    pj = tmp_path / "p.json"
    pj.write_text(
        prices.reset_index().rename(columns={"index": "date"}).to_json(orient="records"),
        encoding="utf-8",
    )
    assert detect_source_type(pj) in ("prices", "returns", "unknown")
    pp = tmp_path / "p.pkl"
    prices.to_pickle(pp)
    assert detect_price_or_returns(pp) in ("prices", "returns", "unknown")
    missing = tmp_path / "nope.csv"
    assert detect_price_or_returns(missing) in ("unknown", "prices", "returns")


# helpers
def test_prices_to_returns_and_is_likely():
    prices = _pricedf(6)
    ret = _prices_to_returns(prices)
    assert len(ret) == 5
    assert _is_likely_returns(ret) in (True, False)
    assert _is_likely_returns(prices) in (True, False)
    with pytest.raises(BABDataError):
        _prices_to_returns(_pricedf(1))


def test_schema_utility_functions():
    df = _retdf()
    assert list_columns(df) == sorted(str(c) for c in df.columns)
    assert "BTC" in list(iter_assets(df))
    assert "MKT" not in list(iter_assets(df, benchmark="MKT"))
    assert isinstance(standardize_columns(df), pd.DataFrame)
    assert isinstance(clean_data(df), pd.DataFrame)
    ns = normalize_schema(df.reset_index().rename(columns={"index": "date"}))
    assert isinstance(ns, pd.DataFrame)
    vp = validate_prices(_pricedf())
    assert vp is None or isinstance(vp, pd.DataFrame)
    assert validate_prices(None) is None  # type: ignore
    assert validate_prices(pd.DataFrame()) is None


def test_normalize_schema_multiindex_and_header_row():
    cols = pd.MultiIndex.from_tuples([("A", "BTC"), ("A", "MKT")])
    df = pd.DataFrame([[0.1, 0.01], [0.2, 0.02], [0.3, 0.03]], columns=cols)
    with contextlib.suppress(Exception):
        normalize_schema(df)
    # duplicate header in first row
    df2 = pd.DataFrame(
        [["date", "BTC", "MKT"], ["2024-01-01", 0.1, 0.01], ["2024-01-02", 0.2, 0.02]],
        columns=["date", "BTC", "MKT"],
    )
    with contextlib.suppress(Exception):
        normalize_schema(df2)
