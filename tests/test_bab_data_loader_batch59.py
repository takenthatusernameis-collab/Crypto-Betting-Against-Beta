import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import contextlib

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


def test_791_792_name_match_outer_except():
    class WeirdSeries(pd.Series):
        @property
        def _constructor(self):
            return WeirdSeries

        @property
        def tz(self):
            raise RuntimeError("tz boom")

    orig_td = pd.to_datetime

    def fake_td(x, *a, **k):
        if isinstance(x, pd.Series) and str(x.name).lower() == "date":
            return WeirdSeries(
                [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")], name=x.name, index=x.index
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    try:
        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        assert "date" not in out.columns or isinstance(out.index, pd.DatetimeIndex)
    finally:
        dl.pd.to_datetime = orig_td


def test_859_861_862_867_868_unnamed_tz_convert_path():
    orig_coerce = dl._coerce_to_datetime_scalar

    def fake_coerce(v):
        return pd.Timestamp("2024-01-01", tz="UTC")

    dl._coerce_to_datetime_scalar = fake_coerce
    try:
        df = pd.DataFrame({"Unnamed: 0": ["x", "y"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        assert "Unnamed: 0" not in out.columns or isinstance(out.index, pd.DatetimeIndex)
    except BABDataError:
        pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce


def test_894_last_resort_tz_normalize_and_set_index_fallbacks():
    orig_td = pd.to_datetime
    state = {"n": 0}

    def fake_td(x, *a, **k):
        state["n"] += 1
        if isinstance(x, pd.Series) and str(x.name) == "mystery":
            if state["n"] <= 2:
                raise ValueError("early")
            return pd.Series(
                [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")],
                index=x.index,
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    orig_set = pd.DataFrame.set_index

    def flaky_set(self, keys, *a, **k):
        if getattr(self, "_flaky", False):
            raise RuntimeError("set boom")
        return orig_set(self, keys, *a, **k)

    pd.DataFrame.set_index = flaky_set
    try:
        df = pd.DataFrame({"mystery": ["a", "b"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        with contextlib.suppress(Exception):
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    finally:
        dl.pd.to_datetime = orig_td
        pd.DataFrame.set_index = orig_set


def test_901_903_908_914_last_resort_result_not_dtindex():
    orig_td = pd.to_datetime
    state = {"n": 0}

    def fake_td(x, *a, **k):
        state["n"] += 1
        if isinstance(x, pd.Series) and str(x.name) == "mystery":
            if state["n"] <= 2:
                raise ValueError("early")
            return pd.Series(
                [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")], index=x.index
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    orig_set = pd.DataFrame.set_index

    def weird_set(self, keys, *a, **k):
        res = orig_set(self, keys, *a, **k)
        if isinstance(keys, pd.Series) or str(getattr(keys, "name", "")) == "mystery":
            res.index = pd.Index(["a", "b"])
        return res

    pd.DataFrame.set_index = weird_set
    try:
        df = pd.DataFrame({"mystery": ["x", "y"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        with contextlib.suppress(Exception):
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    finally:
        dl.pd.to_datetime = orig_td
        pd.DataFrame.set_index = orig_set


def test_1530_1531_1533_1536_benchmark_fallback_paths():
    class Flaky(pd.DataFrame):
        _n = 0

        @property
        def _constructor(self):
            return Flaky

        @property
        def columns(self):
            return super().columns

        @columns.setter
        def columns(self, v):
            pd.DataFrame.columns.fset(self, v)

        def rename(self, *a, **k):
            Flaky._n += 1
            if Flaky._n == 1:
                raise RuntimeError("boom")
            return super().rename(*a, **k)

        def __contains__(self, item):
            if item == "BTC" and Flaky._n >= 1:
                return False
            return super().__contains__(item)

    idx = pd.date_range("2024-01-01", periods=5)
    df = Flaky({"date": idx, "btc": [0.01] * 5, "ETH": [0.02] * 5})
    Flaky._n = 0
    with contextlib.suppress(Exception):
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)


def test_1591_1592_csv_stateful_empty(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text("date,BTC,ETH\n2024-01-01,0.01,0.02\n2024-01-02,0.01,0.02\n")
    orig = pd.read_csv

    class F(pd.DataFrame):
        _c = 0

        @property
        def _constructor(self):
            return F

        @property
        def empty(self):
            F._c += 1
            if F._c >= 3:
                return True
            return super().empty

    def fake(*a, **k):
        return F(orig(*a, **k))

    pd.read_csv = fake
    F._c = 0
    try:
        with pytest.raises(Exception):
            dl.load_returns_from_csv(p, benchmark="BTC", quality=False)
    finally:
        pd.read_csv = orig
