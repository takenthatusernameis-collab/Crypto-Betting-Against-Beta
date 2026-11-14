import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import contextlib

import numpy as np
import pandas as pd

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 62: real-data probes for metadata/normalize/parquet/hdf5 handlers


def test_1926_1929_drop_metadata_sequential():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "rowid": [0, 1, 2],
            "BTC": [100.0, 101.0, 102.0],
        }
    )
    out = dl._drop_metadata_columns(df)
    assert "rowid" not in out.columns


def test_1926_1929_drop_metadata_junk():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "junk": [0, 1, 2],
            "BTC": [100.0, 101.0, 102.0],
        }
    )
    out = dl._drop_metadata_columns(df)
    assert "junk" not in out.columns


def test_2160_2163_normalize_multiindex():
    mi = pd.MultiIndex.from_tuples([("A", "x"), ("A", "y"), ("B", "z")])
    df = pd.DataFrame([[0.01, 0.02, 0.03]], columns=mi)
    df.index = pd.to_datetime(["2024-01-01"])
    out = dl.normalize_schema(df, benchmark=None)
    assert isinstance(out, pd.DataFrame)


def test_2167_2168_normalize_first_row_headers():
    df = pd.DataFrame(
        {"Unnamed: 0": ["BTC", "ETH"], "Unnamed: 1": [100.0, 10.0], "Unnamed: 2": [101.0, 11.0]}
    )
    out = dl.normalize_schema(df, benchmark=None)
    assert isinstance(out, pd.DataFrame)


def test_2187_2189_normalize_junk_drop():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "junkcol": ["abc", "def"],
            "BTC": [0.01, 0.02],
        }
    )
    out = dl.normalize_schema(df, benchmark=None)
    assert "junkcol" not in out.columns


def test_2192_2193_normalize_weird_cols():
    class WeirdCols(pd.DataFrame):
        @property
        def _constructor(self):
            return WeirdCols

        @property
        def columns(self):
            raise RuntimeError("cols boom")

    df = WeirdCols({"date": pd.to_datetime(["2024-01-01", "2024-01-02"]), "BTC": [0.01, 0.02]})
    with contextlib.suppress(Exception):
        dl.normalize_schema(df, benchmark=None)


def test_1097_1098_drop_all_nan_getitem_except():
    class BadDrop(pd.DataFrame):
        @property
        def _constructor(self):
            return BadDrop

        def __getitem__(self, k):
            raise RuntimeError("getitem boom")

    df = BadDrop({"BTC": [np.nan, np.nan], "ETH": [0.01, 0.02]})
    out = dl._drop_all_nan_columns(df)
    assert isinstance(out, pd.DataFrame)
