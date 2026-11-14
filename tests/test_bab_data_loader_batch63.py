import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 63: direct _promote_datetime_column probes (canonical entrypoint bypasses unnamed-drop)


def test_843_873_unnamed_promote():
    df = pd.DataFrame(
        {"Unnamed: 0": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
    )
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_859_unnamed_tz_timestamp():
    df = pd.DataFrame(
        {
            "Unnamed: 0": [
                pd.Timestamp("2024-01-01", tz="UTC"),
                pd.Timestamp("2024-01-02", tz="UTC"),
            ],
            "BTC": [0.01, 0.02],
            "ETH": [0.03, 0.04],
        }
    )
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_867_868_single_row_unnamed():
    df = pd.DataFrame({"Unnamed: 0": ["2024-01-01"], "BTC": [0.01], "ETH": [0.04]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_885_907_last_resort():
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02], "ETH": [0.03, 0.04], "mystery": ["2024-01-01", "2024-01-02"]}
    )
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_901_903_last_resort_tz():
    df = pd.DataFrame(
        {
            "BTC": [0.01, 0.02],
            "ETH": [0.03, 0.04],
            "mystery": ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
        }
    )
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_908_914_last_resort_weird_set_index():
    class WeirdSet(pd.DataFrame):
        @property
        def _constructor(self):
            return WeirdSet

        def set_index(self, keys, *a, **k):
            res = super().set_index(keys, *a, **k)
            res.index = pd.Index(["a", "b"])
            return res

    df = WeirdSet(
        {"BTC": [0.01, 0.02], "ETH": [0.03, 0.04], "mystery": ["2024-01-01", "2024-01-02"]}
    )
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


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
    out = dl._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)
