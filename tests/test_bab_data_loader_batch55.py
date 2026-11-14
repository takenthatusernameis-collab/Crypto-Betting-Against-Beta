import contextlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as mod


class _SetIndexRaisesOnce:
    def __init__(self, real_set_index, raise_on_call=1):
        self.real_set_index = real_set_index
        self.raise_on_call = raise_on_call
        self.calls = 0

    def __call__(self, df_self, *args, **kwargs):
        self.calls += 1
        if self.calls == self.raise_on_call:
            raise ValueError("patched set_index")
        return self.real_set_index(df_self, *args, **kwargs)


def test_promote_name_match_set_index_raises_falls_through(monkeypatch):
    monkeypatch.setattr(
        pd.DataFrame, "set_index", _SetIndexRaisesOnce(pd.DataFrame.set_index, raise_on_call=1)
    )
    df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2], "ETH": [0.2, 0.3]})
    out = mod._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)


def test_promote_name_match_elementwise_apply_exception_path(monkeypatch):
    real_to_datetime = pd.to_datetime

    def fake_to_datetime(arg, *args, **kwargs):
        if kwargs.get("errors") == "raise" and getattr(arg, "name", None) == "date":
            s = real_to_datetime(arg, *args, errors="coerce")
            s = s.copy()

            def bad_apply(fn):
                raise RuntimeError("apply boom")

            s.apply = bad_apply
            return s
        return real_to_datetime(arg, *args, **kwargs)

    monkeypatch.setattr(mod.pd, "to_datetime", fake_to_datetime)
    df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2], "ETH": [0.2, 0.3]})
    out = mod._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)
    assert "BTC" in out.columns


def test_promote_unnamed_tz_aware_coerced_normalized(monkeypatch):
    def fake_coerce(v):
        return pd.Timestamp("2024-01-01", tz="UTC")

    monkeypatch.setattr(mod, "_coerce_to_datetime_scalar", fake_coerce)
    df = pd.DataFrame({"Unnamed: 0": [1, 2], "BTC": [0.1, 0.2], "ETH": [0.2, 0.3]})
    out = mod._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index.tz is None


def test_promote_last_resort_tz_aware_returns_df():
    df = pd.DataFrame(
        {
            "BTC": [0.1, 0.2],
            "ETH": [0.2, 0.3],
            "note": ["2024-01-01T00:00:00+00:00", "2024-01-02T00:00:00+00:00"],
        }
    )
    out = mod._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)
    assert "BTC" in out.columns and "ETH" in out.columns


def test_validate_benchmark_case_insensitive_remap():
    df = pd.DataFrame(
        {"btc": [0.01, 0.02], "eth": [0.02, 0.03]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    out = mod.validate_returns_dataframe(df, benchmark="BTC")
    assert "BTC" in out.columns


def test_validate_benchmark_remap_rename_exception(monkeypatch):
    real_rename = pd.DataFrame.rename

    def bad_rename(self, *args, **kwargs):
        cols = kwargs.get("columns") or (args[0] if args else None)
        if isinstance(cols, dict) and ("BTC" in cols.values() or "btc" in cols.values()):
            raise RuntimeError("rename boom")
        return real_rename(self, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "rename", bad_rename)
    df = pd.DataFrame(
        {"btc": [0.01, 0.02], "eth": [0.02, 0.03]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    out = mod.validate_returns_dataframe(df, benchmark="BTC")
    assert isinstance(out, pd.DataFrame)


def test_load_csv_stateful_empty_defensive(tmp_path, monkeypatch):
    p = tmp_path / "r.csv"
    p.write_text("date,BTC,ETH\n2024-01-01,0.1,0.2\n2024-01-02,0.2,0.3\n")
    real_read_csv = mod.pd.read_csv
    calls = {"n": 0}

    def fake_read_csv(*args, **kwargs):
        calls["n"] += 1
        df = real_read_csv(*args, **kwargs)
        if calls["n"] == 1:
            orig_getattr = type(df).__getattribute__

            class FlipEmpty(type(df)):
                def __getattribute__(self, name):
                    if name == "empty":
                        calls["n"] += 1
                        if calls["n"] == 2:
                            return False
                        return super().__getattribute__("empty")
                    return super().__getattribute__(name)

            with contextlib.suppress(Exception):
                df.__class__ = type("_D", (FlipEmpty, type(df)), {})
        return df

    monkeypatch.setattr(mod.pd, "read_csv", fake_read_csv)
    with contextlib.suppress(mod.BABDataError):
        mod.load_returns_from_csv(p, benchmark="BTC")


def test_exchange_epoch_format_normalization():
    df = pd.DataFrame(
        {
            "timestamp": [1704067200000, 1704153600000],
            "BTC": [100.0, 101.0],
            "ETH": [50.0, 51.0],
        }
    )
    out = mod.load_prices(df, benchmark="BTC")
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index.tz is None


def test_clean_data_runs():
    df = pd.DataFrame({"BTC": [100.0, 101.0], "ETH": [50.0, 51.0]})
    df.index = pd.to_datetime(["2024-01-01", "2024-01-02"])
    out = mod.clean_data(df)
    assert isinstance(out, pd.DataFrame)


def test_promote_last_resort_set_index_exception(monkeypatch):
    real_set_index = pd.DataFrame.set_index

    def bad_set_index(self, *args, **kwargs):
        if len(args) >= 1 and args[0] is getattr(self, "index", None):
            raise ValueError("nope")
        if kwargs.get("keys", object()) is getattr(self, "index", object()):
            raise ValueError("nope")
        return real_set_index(self, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "set_index", bad_set_index)
    df = pd.DataFrame(
        {
            "BTC": [0.1, 0.2],
            "ETH": [0.2, 0.3],
            "note": ["2024-01-01", "2024-01-02"],
        }
    )
    out = mod._promote_datetime_column(df)
    assert isinstance(out, pd.DataFrame)
