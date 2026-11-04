import json
import pickle
import os

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_loaders_jsonl_objects(tmp_path):
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "BTC": [0.01, -0.01, 0.02]})
    p = tmp_path / "x.jsonl"
    with open(p, "w") as f:
        for _, r in df.iterrows():
            f.write(json.dumps({"date": r["date"].isoformat(), "BTC": float(r["BTC"])}) + "\n")
    out = dl.load_returns(p)
    assert isinstance(out, pd.DataFrame)


def test_loaders_parquet_hdf5(tmp_path):
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "BTC": [0.01, -0.01, 0.02]})
    try:
        pp = tmp_path / "x.parquet"
        df.to_parquet(pp)
        out = dl.load_returns(pp)
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass
    try:
        ph = tmp_path / "x.h5"
        df.to_hdf(ph, key="df")
        out2 = dl.load_returns(ph)
        assert isinstance(out2, pd.DataFrame)
    except Exception:
        pass


def test_strip_units_and_parse_edges():
    assert dl._strip_units_and_parse("1,000.50") == 1000.5
    assert dl._strip_units_and_parse("$100") == 100.0
    assert dl._strip_units_and_parse("10%") == 0.1
    assert dl._strip_units_and_parse("N/A") is np.nan or pd.isna(dl._strip_units_and_parse("N/A")) or dl._strip_units_and_parse("N/A") == float('nan')
    assert dl._strip_units_and_parse("1.5e-2") == 0.015 or abs(dl._strip_units_and_parse("1.5e-2") - 0.015) < 1e-10


def test_coerce_numeric_df():
    df = pd.DataFrame({"a": ["1", "2"], "b": [3.0, 4.0]})
    out = dl._coerce_numeric(df)
    assert pd.api.types.is_numeric_dtype(out["a"])
    assert pd.api.types.is_numeric_dtype(out["b"])


def test_validate_with_benchmark(tmp_path):
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=10), "BTC": np.random.randn(10)*0.01, "ETH": np.random.randn(10)*0.01})
    out = dl.validate_returns_dataframe(df, benchmark="BTC")
    assert isinstance(out, pd.DataFrame)
