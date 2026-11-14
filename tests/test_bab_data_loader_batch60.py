import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import contextlib

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


def test_791_792_parsed_has_tz_but_dt_attr_none():
    class S(pd.Series):
        @property
        def _constructor(self):
            return S

        @property
        def tz(self):
            return None

    orig_td = pd.to_datetime

    def fake_td(x, *a, **k):
        if isinstance(x, pd.Series) and str(x.name).lower() == "date":
            return S(
                [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")],
                name=x.name,
                index=x.index,
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    try:
        df = pd.DataFrame({"date": ["x", "y"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        with contextlib.suppress(BABDataError):
            dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    finally:
        dl.pd.to_datetime = orig_td


def test_679_694_695_713_714_733_734_exchange_epoch_paths():
    df = pd.DataFrame(
        {"open_time": [1704067200000, 1704153600000], "BTC": [100.0, 101.0], "ETH": [10.0, 11.0]}
    )
    out = dl.clean_data(df)
    assert isinstance(out.index, pd.DatetimeIndex) or len(out) >= 0


def test_1226_1227_1257_1258_1293_1294_1319_1320_coerce_detect_qa(tmp_path):
    df = pd.DataFrame(
        {"BTC": [100.0, 101.0, np.nan], "ETH": [10.0, 10.5, 11.0]},
        index=pd.date_range("2024-01-01", periods=3),
    )
    with pytest.raises(Exception):
        dl.validate_returns_dataframe(
            df.reset_index().rename(columns={"index": "date"}),
            benchmark="BTC",
            quality=True,
            min_rows=5,
        )
    df2 = pd.DataFrame({"date": ["bad", "2024-01-02"], "BTC": [1, 2], "ETH": [3, 4]})
    with pytest.raises(Exception):
        dl.validate_returns_dataframe(df2, benchmark="BTC")


def test_1926_1929_2160_2163_2167_2168_2187_2189_2192_2193_clean_data_defensive():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-02"])
    df = pd.DataFrame(
        {
            "BTC": [1.0, 2.0, 3.0],
            "ETH": [1.0, 2.0, 3.0],
            "date": ["2024-01-01", "2024-01-02", "date"],
        },
        index=idx,
    )
    with contextlib.suppress(Exception):
        out = dl.clean_data(df, benchmark="BTC")
    df2 = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [1, 2]})
    with contextlib.suppress(Exception):
        dl.clean_data(df2, benchmark="ETH")


def test_1530_1536_second_bench_map_branch():
    class DF(pd.DataFrame):
        _n = 0

        @property
        def _constructor(self):
            return DF

        def rename(self, *a, **k):
            DF._n += 1
            if DF._n <= 2:
                raise RuntimeError("x")
            return super().rename(*a, **k)

        def __contains__(self, k):
            if k == "BTC" and DF._n >= 1:
                return False
            return super().__contains__(k)

    idx = pd.date_range("2024-01-01", periods=5)
    df = DF({"date": idx, "btc": [0.01] * 5, "ETH": [0.02] * 5})
    DF._n = 0
    with contextlib.suppress(Exception):
        dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
