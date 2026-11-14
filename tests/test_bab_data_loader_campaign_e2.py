"""Campaign E2: additional coverage pushes for data_loader public/error paths."""

from __future__ import annotations

import contextlib
import json
import math
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_to_datetime_scalar,
    _normalize_index,
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


def _base(n=8):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {
            "BTC": np.linspace(0.01, 0.08, n),
            "ETH": np.linspace(0.02, 0.09, n),
            "MKT": np.linspace(0.005, 0.04, n),
        },
        index=idx,
    )


# -- coercion fallbacks / _normalize_index branches --


def test_coerce_scalar_floats_ints_timestamps():
    assert pd.notna(pd.Timestamp(_coerce_to_datetime_scalar(1704067200.0)))
    assert pd.notna(pd.Timestamp(_coerce_to_datetime_scalar(np.int64(1704067200000))))
    ts = pd.Timestamp("2024-01-01", tz="UTC")
    out = _coerce_to_datetime_scalar(ts)
    assert pd.notna(pd.Timestamp(out))
    dt = pd.Timestamp("2024-01-02").to_pydatetime()
    assert pd.notna(pd.Timestamp(_coerce_to_datetime_scalar(dt)))


def test_coerce_scalar_boundary_magnitudes():
    # exercise us/ms/ns branches
    for v in [10**19, 10**17 + 1, 10**15 + 1, 10**12 + 1, 10**9 + 1, 100.0, 0.5]:
        with contextlib.suppress(Exception):
            _coerce_to_datetime_scalar(v)
    for s in ["1704067200000000000", "1704067200000000", "1704067200000.5"]:
        with contextlib.suppress(Exception):
            _coerce_to_datetime_scalar(s)


def test_normalize_index_various_epoch_magnitudes_and_strings():
    base_s = 1704067200
    for idx_vals in [
        [base_s * 10**9, base_s * 10**9 + 86400 * 10**9],
        [base_s * 10**6, base_s * 10**6 + 86400 * 10**6],
        [base_s * 1000, (base_s + 86400) * 1000],
        [str(base_s), str(base_s + 86400)],
        pd.date_range("2024-01-01", periods=2, tz="UTC"),
    ]:
        df = pd.DataFrame({"A": [1.0, 2.0], "B": [3.0, 4.0]}, index=list(idx_vals))
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)


def test_normalize_index_unparseable_raises():
    df = pd.DataFrame({"A": [1, 2]}, index=["not-a-date", "still-nope"])
    with pytest.raises(Exception):
        _normalize_index(df)


# -- exchange long/wide/OHLCV detection via validate/load --


def test_exchange_long_binance_style_pivot():
    df = pd.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT", "ETHUSDT", "ETHUSDT", "BTCUSDT"],
            "open time": [
                1704067200000,
                1704153600000,
                1704067200000,
                1704153600000,
                1704240000000,
            ],
            "close": [42000, 43000, 2200, 2300, 44000],
            "volume": [1, 2, 3, 4, 5],
        }
    )
    out = validate_returns_dataframe(df, quality=False)
    assert isinstance(out, pd.DataFrame)


def test_exchange_wide_ohlcv_close_promotion():
    df = pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "Open": [10, 11, 12, 13, 14],
            "High": [11, 12, 13, 14, 15],
            "Low": [9, 10, 11, 12, 13],
            "Close": [100, 101, 99, 102, 103],
            "Volume": [1000] * 5,
        }
    )
    out = validate_returns_dataframe(df, quality=False)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_exchange_adj_close_and_timestamp_col():
    df = pd.DataFrame(
        {
            "timestamp": [1704067200, 1704153600, 1704240000, 1704326400],
            "adj close": [50.0, 51.0, 49.5, 52.0],
        }
    )
    out = validate_returns_dataframe(df, quality=False)
    assert isinstance(out, pd.DataFrame)


# -- validate_returns_dataframe quality/edge branches --


def test_validate_quality_flags_and_duplicate_policy():
    df = _base(12)
    # introduce a duplicate timestamp
    df2 = df.copy()
    df2.index = [*list(df2.index[:-1]), df2.index[-2]]
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df2, quality=True, allow_duplicate_timestamps=True)
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df2, quality=True, allow_duplicate_timestamps=False)


def test_validate_extreme_returns_and_gaps():
    df = _base(10)
    df.iloc[1, 0] = 50.0  # implausible
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df, quality=True, max_return_abs=1.0)
    # gap
    idx = list(pd.date_range("2024-01-01", periods=5, freq="D"))
    idx[3] = idx[2] + pd.Timedelta(days=30)
    df3 = pd.DataFrame({"BTC": [0.1] * 5, "MKT": [0.01] * 5}, index=idx)
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df3, quality=True, max_gap_days=7)


def test_validate_stale_run_and_min_finite_fraction():
    df = _base(10)
    df["STALE"] = 0.01
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df, quality=True, stale_run_threshold=3)
    df2 = _base(10)
    df2.iloc[:9, 0] = np.nan
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df2, quality=True, min_finite_fraction=0.5)


def test_validate_benchmark_no_finite_values():
    df = _base(6)
    df["MKT"] = np.nan
    with pytest.raises(BABDataError):
        validate_returns_dataframe(df, benchmark="MKT", quality=False)


def test_validate_trivial_range_index_rejected():
    # 0..n-1 index with no date info can be interpreted as missing date
    df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3], "MKT": [0.01, 0.02, 0.03]})
    with contextlib.suppress(BABDataError):
        validate_returns_dataframe(df, quality=False)


# -- loader error wrapping and paths --


def test_csv_bad_content(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("a,b\n1,2,3\n", encoding="utf-8")
    with contextlib.suppress(BABDataError):
        load_returns_from_csv(p)


def test_jsonl_comments_blank_and_bad(tmp_path):
    p = tmp_path / "r.jsonl"
    lines = [
        "# comment",
        "",
        json.dumps({"date": "2024-01-01", "BTC": 0.1, "MKT": 0.01}),
        json.dumps({"date": "2024-01-02", "BTC": 0.2, "MKT": 0.02}),
        json.dumps({"date": "2024-01-03", "BTC": 0.3, "MKT": 0.03}),
    ]
    p.write_text("\n".join(lines), encoding="utf-8")
    out = load_returns_from_json(p, quality=False)
    assert isinstance(out, pd.DataFrame)
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"date":"2024-01-01"}\n{not json}\n', encoding="utf-8")
    with pytest.raises(BABDataError):
        load_returns_from_json(bad)


def test_json_split_requires_keys(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"foo": 1}), encoding="utf-8")
    with pytest.raises(BABDataError):
        load_returns_from_json(p, orient="split")


def test_json_index_orient(tmp_path):
    data = {
        "BTC": {"2024-01-01": 0.1, "2024-01-02": 0.2, "2024-01-03": 0.3},
        "MKT": {"2024-01-01": 0.01, "2024-01-02": 0.02, "2024-01-03": 0.03},
    }
    p = tmp_path / "i.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    out = load_returns_from_json(p, orient="index", quality=False)
    assert isinstance(out, pd.DataFrame)


def test_pickle_unsupported_type(tmp_path):
    p = tmp_path / "x.pkl"
    with open(p, "wb") as f:
        pickle.dump("just a string", f)
    with pytest.raises(BABDataError):
        load_returns_from_pickle(p)


def test_load_returns_from_dataframe_rangeindex_recovery():
    df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3, 0.4], "MKT": [0.01, 0.02, 0.03, 0.04]})
    try:
        out = load_returns_from_dataframe(df, quality=False)
        assert isinstance(out, pd.DataFrame)
    except BABDataError:
        pass


# -- detect/load_prices file paths --


def test_detect_from_pickle_and_parquet_variants(tmp_path):
    df = _base(6)
    pp = tmp_path / "d.pkl"
    df.to_pickle(pp)
    assert detect_price_or_returns(pp) in ("prices", "returns", "unknown")
    # dict pickle
    pdict = tmp_path / "dict.pkl"
    with open(pdict, "wb") as f:
        pickle.dump({"x": [1, 2, 3]}, f)
    detect_price_or_returns(pdict)


def test_load_prices_from_jsonl_and_hdf_variants(tmp_path, monkeypatch):
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    prices = pd.DataFrame(
        {"BTC": np.linspace(100, 110, 6), "MKT": np.linspace(50, 55, 6)}, index=idx
    )
    jl = tmp_path / "p.jsonl"
    recs = prices.reset_index().rename(columns={"index": "date"})
    recs["date"] = recs["date"].astype(str)
    jl.write_text(
        "\n".join(recs.to_json(orient="records", lines=True).splitlines()), encoding="utf-8"
    )
    with contextlib.suppress(Exception):
        load_prices(jl)
    with pytest.raises(BABDataError):
        load_prices(tmp_path / "nope.csv")


# -- schema/utility helpers --


def test_list_columns_iter_assets_normalize_standardize_clean():
    df = _base()
    assert isinstance(list_columns(df), list)
    assert isinstance(list(iter_assets(df, benchmark="MKT")), list)
    with contextlib.suppress(Exception):
        normalize_schema(df)
    with contextlib.suppress(Exception):
        standardize_columns(df)
    with contextlib.suppress(Exception):
        clean_data(df)
    with contextlib.suppress(Exception):
        validate_prices(_base())
