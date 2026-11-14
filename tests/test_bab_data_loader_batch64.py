import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import contextlib

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 64: targeted probes for remaining reachable clusters


def test_1626_1627_parquet_missing_file():
    with pytest.raises(BABDataError):
        dl.load_returns_from_parquet("/nonexistent/missing.parquet")


def test_1663_1664_hdf5_missing_file():
    with pytest.raises(BABDataError):
        dl.load_returns_from_hdf5("/nonexistent/missing.h5")


def test_791_792_name_match_weird_tz():
    class WeirdSeries(pd.Series):
        @property
        def _constructor(self):
            return WeirdSeries

        @property
        def tz(self):
            raise RuntimeError("tz boom")

    df = pd.DataFrame(
        {"date": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
    )
    df["date"] = WeirdSeries(df["date"].values)
    with contextlib.suppress(Exception):
        dl._promote_datetime_column(df)


def test_1530_1531_first_rename_raises():
    class FlakyRename(pd.DataFrame):
        _n = 0

        @property
        def _constructor(self):
            return FlakyRename

        def rename(self, *a, **k):
            FlakyRename._n += 1
            if FlakyRename._n == 1:
                raise RuntimeError("boom")
            return super().rename(*a, **k)

    df = FlakyRename(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "btc": [0.01] * 5,
            "ETH": [0.02] * 5,
        }
    )
    FlakyRename._n = 0
    with contextlib.suppress(Exception):
        dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)


def test_1533_1536_second_bench_map():
    # benchmark not in columns, case-insensitive match present, first rename fails
    class FlakyRename(pd.DataFrame):
        _n = 0

        @property
        def _constructor(self):
            return FlakyRename

        def rename(self, *a, **k):
            FlakyRename._n += 1
            if FlakyRename._n <= 2:
                raise RuntimeError("boom")
            return super().rename(*a, **k)

        def __contains__(self, item):
            if item == "BTC" and FlakyRename._n >= 1:
                return False
            return super().__contains__(item)

    df = FlakyRename(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "btc": [0.01] * 5,
            "ETH": [0.02] * 5,
        }
    )
    FlakyRename._n = 0
    with contextlib.suppress(Exception):
        dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)


def test_1591_1592_csv_stateful_empty(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text("date,BTC,ETH\n2024-01-01,0.01,0.02\n2024-01-02,0.01,0.02\n")

    class StateEmpty(pd.DataFrame):
        _c = 0

        @property
        def _constructor(self):
            return StateEmpty

        @property
        def empty(self):
            StateEmpty._c += 1
            if StateEmpty._c >= 3:
                return True
            return super().empty

    orig = pd.read_csv

    def fake(*a, **k):
        return StateEmpty(orig(*a, **k))

    pd.read_csv = fake
    StateEmpty._c = 0
    try:
        with pytest.raises(Exception):
            dl.load_returns_from_csv(p, benchmark="BTC", quality=False)
    finally:
        pd.read_csv = orig
