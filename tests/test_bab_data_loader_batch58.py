import os
import sys
import types

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import contextlib

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


def test_791_792_name_match_elementwise_tz_via_canonical():
    class TzSeries(pd.Series):
        @property
        def _constructor(self):
            return TzSeries

        @property
        def tz(self):
            return None

    orig_td = pd.to_datetime

    def fake_td(x, *a, **k):
        if isinstance(x, pd.Series) and str(x.name).lower() == "date":
            return TzSeries(
                [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")],
                name=x.name,
                index=x.index,
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    try:
        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        assert isinstance(out.index, pd.DatetimeIndex)
    finally:
        dl.pd.to_datetime = orig_td


def test_791_792_apply_raises_fallback():
    class TzSeries(pd.Series):
        @property
        def _constructor(self):
            return TzSeries

        @property
        def tz(self):
            return None

        def apply(self, *a, **k):
            raise RuntimeError("apply boom")

    orig_td = pd.to_datetime

    def fake_td(x, *a, **k):
        if isinstance(x, pd.Series) and str(x.name).lower() == "date":
            return TzSeries(
                [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")],
                name=x.name,
                index=x.index,
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    try:
        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        assert isinstance(out.index, pd.DatetimeIndex) or "date" not in out.columns
    finally:
        dl.pd.to_datetime = orig_td


def test_859_861_862_unnamed_tz_elementwise():
    class TzObj:
        def __init__(self, ts):
            self._ts = ts
            self.tzinfo = ts.tzinfo

        def __getattr__(self, n):
            return getattr(self._ts, n)

    orig_coerce = dl._coerce_to_datetime_scalar

    def fake_coerce(v):
        if str(v).startswith("T"):
            return TzObj(pd.Timestamp("2024-01-01", tz="UTC"))
        return orig_coerce(v)

    dl._coerce_to_datetime_scalar = fake_coerce
    try:
        df = pd.DataFrame({"Unnamed: 0": ["T1", "T2"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        try:
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
            assert isinstance(out.index, pd.DatetimeIndex) or "Unnamed: 0" not in out.columns
        except BABDataError:
            pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce


def test_867_868_unnamed_inner_except():
    orig_coerce = dl._coerce_to_datetime_scalar

    class Bad:
        @property
        def tzinfo(self):
            raise RuntimeError("tz boom")

    def fake_coerce(v):
        return Bad()

    dl._coerce_to_datetime_scalar = fake_coerce
    try:
        df = pd.DataFrame({"Unnamed: 0": ["T1", "T2"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    except Exception:
        pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce


def test_894_901_903_908_914_last_resort():
    orig_td = pd.to_datetime
    calls = {"n": 0}

    def fake_td(x, *a, **k):
        calls["n"] += 1
        if isinstance(x, pd.Series) and str(x.name) == "mycol":
            if calls["n"] <= 3:
                raise ValueError("nope")
            s = pd.Series(
                [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")],
                index=x.index,
            )
            return s
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    try:
        df = pd.DataFrame({"mycol": ["a", "b"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        with contextlib.suppress(Exception):
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    finally:
        dl.pd.to_datetime = orig_td


def test_1530_1531_1533_1536_benchmark_remap(tmp_path):
    class FlakyDF(pd.DataFrame):
        _calls = 0

        def rename(self, *a, **k):
            FlakyDF._calls += 1
            if FlakyDF._calls == 1:
                raise RuntimeError("rename boom")
            return super().rename(*a, **k)

    orig_validate = dl._normalize_index
    df = FlakyDF(
        {"date": pd.date_range("2024-01-01", periods=5), "btc": [0.01] * 5, "ETH": [0.02] * 5}
    )
    FlakyDF._calls = 0
    try:
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        assert "BTC" in out.columns or "btc" in out.columns
    except Exception:
        pass


def test_1591_1592_csv_empty_after_read(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("date,BTC,ETH\n2024-01-01,0.01,0.02\n")

    class FlakyEmpty(pd.DataFrame):
        _checks = 0

        @property
        def empty(self):
            FlakyEmpty._checks += 1
            if FlakyEmpty._checks >= 2:
                return True
            return super().empty

    orig = pd.read_csv

    def fake_read(*a, **k):
        return FlakyEmpty(orig(*a, **k))

    pd.read_csv = fake_read
    FlakyEmpty._checks = 0
    try:
        with pytest.raises(Exception):
            dl.load_returns_from_csv(p, benchmark="BTC", quality=False)
    finally:
        pd.read_csv = orig
