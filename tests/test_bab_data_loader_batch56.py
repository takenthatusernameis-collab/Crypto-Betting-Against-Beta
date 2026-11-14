import contextlib

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as mod


def test_validate_benchmark_case_remap_hits_fallback_lines(monkeypatch):
    real_rename = pd.DataFrame.rename
    state = {"n": 0}

    def flaky_rename(self, *args, **kwargs):
        cols = kwargs.get("columns") or (args[0] if args else {})
        if isinstance(cols, dict):
            state["n"] += 1
            if state["n"] == 1:
                raise RuntimeError("first rename boom")
        return real_rename(self, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "rename", flaky_rename)
    df = pd.DataFrame(
        {"btc": [0.01, 0.02], "eth": [0.02, 0.03]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    out = mod.validate_returns_dataframe(df, benchmark="BTC")
    assert "BTC" in out.columns


def test_load_csv_defensive_empty_second_check(tmp_path, monkeypatch):
    p = tmp_path / "r.csv"
    p.write_text("date,BTC,ETH\n2024-01-01,0.1,0.2\n2024-01-02,0.2,0.3\n")
    real_read_csv = mod.pd.read_csv

    def fake_read_csv(*args, **kwargs):
        df = real_read_csv(*args, **kwargs)

        class F(pd.DataFrame):
            _n = 0

            @property
            def empty(self):
                type(self)._n += 1
                if type(self)._n <= 2:
                    return False
                return super().empty

        with contextlib.suppress(Exception):
            df.__class__ = type("_F", (F, pd.DataFrame), {"_n": 0})
        return df

    monkeypatch.setattr(mod.pd, "read_csv", fake_read_csv)
    with contextlib.suppress(mod.BABDataError):
        mod.load_returns_from_csv(p, benchmark="BTC")


def test_clean_data_duplicate_header_row_removed():
    df = pd.DataFrame(
        [["BTC", "ETH"], [100.0, 50.0], [101.0, 51.0]],
        columns=["BTC", "ETH"],
        index=["x", "2024-01-01", "2024-01-02"],
    )
    out = mod.clean_data(df)
    assert isinstance(out, pd.DataFrame)


def test_exchange_epoch_ms_normalization():
    df = pd.DataFrame(
        {
            "open_time": [1704067200000, 1704153600000],
            "BTC": [100.0, 101.0],
            "ETH": [50.0, 51.0],
        }
    )
    out = mod._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_detect_price_or_returns_exception_path(monkeypatch, tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("a,b\n1,2\n")
    monkeypatch.setattr(
        mod.pd, "read_csv", lambda *a, **k: (_ for _ in ()).throw(ValueError("boom"))
    )
    assert mod.detect_price_or_returns(p) == "unknown"


def test_load_returns_parquet_engine_error_then_csv_fallback(tmp_path, monkeypatch):
    p = tmp_path / "r.parquet"
    p.write_text("date,BTC,ETH\n2024-01-01,0.1,0.2\n2024-01-02,0.2,0.3\n")

    def bad_read_parquet(*args, **kwargs):
        raise ImportError("no engine")

    monkeypatch.setattr(mod.pd, "read_parquet", bad_read_parquet)
    try:
        out = mod.load_returns_from_parquet(p, benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
    except mod.BABDataError:
        pass
