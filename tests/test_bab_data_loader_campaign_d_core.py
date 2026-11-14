import contextlib
import json
import os
import pickle

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_normalize_index_numeric_variants():
    df = pd.DataFrame({"ret": [0.01, -0.01]}, index=[1_600_000_000, 1_600_000_000000])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    df2 = pd.DataFrame({"ret": [0.01, -0.01]}, index=[1.6e9, 1.6e12])
    out2 = dl._normalize_index(df2)
    assert isinstance(out2.index, pd.DatetimeIndex)
    df3 = pd.DataFrame({"ret": [0.01, -0.01]}, index=["1600000000", "1600000000000"])
    out3 = dl._normalize_index(df3)
    assert isinstance(out3.index, pd.DatetimeIndex)
    df4 = pd.DataFrame({"ret": []})
    with contextlib.suppress(Exception):
        dl._normalize_index(df4)
    df5 = pd.DataFrame({"ret": [0.01, -0.01]}, index=[pd.Timestamp("2020-01-01"), 1600000000])
    out5 = dl._normalize_index(df5)
    assert isinstance(out5.index, pd.DatetimeIndex)


def test_coerce_to_datetime_scalar_branches():
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar(None)
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar(np.nan)
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar(float("inf"))
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar(float("-inf"))
    with pytest.raises(Exception):
        dl._coerce_to_datetime_scalar(pd.NaT)
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000000))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1.6e9))
    assert not pd.isna(dl._coerce_to_datetime_scalar("1600000000"))
    assert not pd.isna(dl._coerce_to_datetime_scalar("1600000000000"))
    ts = dl._coerce_to_datetime_scalar("2020-01-01T00:00:00Z")
    assert not pd.isna(ts)
    ts2 = dl._coerce_to_datetime_scalar("2020-01-01 00:00:00")
    assert not pd.isna(ts2)
    assert not pd.isna(dl._coerce_to_datetime_scalar(pd.Timestamp("2020-01-01")))


def test_promote_datetime_and_detect_exchange_format():
    df = pd.DataFrame(
        {"open_time": [1600000000000, 1600000060000], "close": [1, 2], "open": [1, 2]}
    )
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    df2 = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "price": [1, 2]})
    out2 = dl._promote_datetime_column(df2.copy())
    assert isinstance(out2.index, pd.DatetimeIndex)
    df3 = pd.DataFrame({"0": [1600000000], "value": [5]})
    out3 = dl._detect_and_normalize_exchange_format(df3.copy())
    assert isinstance(out3, pd.DataFrame)


def test_normalize_columns_and_coercion():
    df = pd.DataFrame(
        {"Price": ["$1,000.50", "€2.000,00"], "Ret%": ["10%", "-5%"], "val": ["N/A", "123"]}
    )
    out = dl._normalize_columns(df)
    assert isinstance(out, pd.DataFrame)
    s = dl._coerce_numeric(pd.DataFrame({"a": ["1,234.56", "$100", "50%"]}))
    assert pd.api.types.is_numeric_dtype(s["a"])


def test_series_is_parseable():
    assert dl._series_is_parseable(pd.Series(["2020-01-01", "2020-01-02"])) is True
    assert dl._series_is_parseable(pd.Series([1600000000, 1600000060000])) is True


def test_loaders_various_formats(tmp_path):
    df = pd.DataFrame(
        {"date": pd.date_range("2020-01-01", periods=5), "ret": [0.01, -0.01, 0.0, 0.02, -0.005]}
    )
    p = tmp_path / "r.csv"
    df.to_csv(p)
    out = dl.load_returns(p)
    assert isinstance(out, pd.DataFrame)
    pj = tmp_path / "r.json"
    df.to_json(pj, orient="records", date_format="iso")
    outj = dl.load_returns(pj)
    assert isinstance(outj, pd.DataFrame)
    pjl = tmp_path / "r.jsonl"
    with open(pjl, "w") as f:
        for _, row in df.iterrows():
            f.write(json.dumps({"date": row["date"].isoformat(), "ret": float(row["ret"])}) + "\n")
    outjl = dl.load_returns(pjl)
    assert isinstance(outjl, pd.DataFrame)
    pp = tmp_path / "r.pkl"
    with open(pp, "wb") as f:
        pickle.dump(df, f)
    outp = dl.load_returns(pp)
    assert isinstance(outp, pd.DataFrame)
    dp = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "price": [10, 11, 12]})
    pp2 = tmp_path / "p.csv"
    dp.to_csv(pp2)
    outpr = dl.load_prices(pp2)
    assert isinstance(outpr, pd.DataFrame)


def test_detect_and_validate_errors():
    with pytest.raises(BABDataError):
        dl.load_returns("/no/such/file.csv")
    with pytest.raises(BABDataError):
        dl.load_returns("bad.txt")
    bad = pd.DataFrame({"x": [1, 2, 3]})
    with pytest.raises(BABDataError):
        dl.validate_returns_dataframe(bad)
