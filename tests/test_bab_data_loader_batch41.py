"""Batch 41: targeted data_loader missing-line coverage."""

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch41MissingLineTargets:
    def test_coerce_scalar_nat_raises_under_core_filename_not_hit_here(self):
        with pytest.raises((ValueError, Exception)):
            dlmod._coerce_to_datetime_scalar(pd.NaT)

    def test_promote_datetime_last_resort_paths_908_914(self):
        df = pd.DataFrame({"datestr": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]})
        out = dlmod._promote_datetime_column(df.copy())
        assert isinstance(out, pd.DataFrame)

    def test_validate_returns_bench_rename_exception_fallback_1530_1531(self, monkeypatch):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3),
                "btc": [0.01, 0.02, -0.01],
                "ETH": [0.02, -0.01, 0.01],
            }
        )
        orig_rename = pd.DataFrame.rename

        def bad_rename(self, *a, **k):
            cols = k.get("columns") or (a[0] if a and isinstance(a[0], dict) else None)
            if isinstance(cols, dict) and any(str(k2).lower() == "btc" for k2 in cols):
                raise RuntimeError("rename boom")
            return orig_rename(self, *a, **k)

        monkeypatch.setattr(pd.DataFrame, "rename", bad_rename)
        out = dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        assert "BTC" in out.columns

    def test_validate_returns_junk_drop_outer_exception_1474_1475(self, monkeypatch):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3),
                "BTC": [0.01, 0.02, -0.01],
                "ETH": [0.02, -0.01, 0.01],
            }
        )
        orig_isnum = pd.api.types.is_numeric_dtype
        calls = {"n": 0}

        def boom(arr_or_dtype):
            calls["n"] += 1
            if calls["n"] > 10:
                raise RuntimeError("isnum boom")
            return orig_isnum(arr_or_dtype)

        monkeypatch.setattr(pd.api.types, "is_numeric_dtype", boom)
        monkeypatch.setattr(dlmod.pd.api.types, "is_numeric_dtype", boom)
        out = dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        assert isinstance(out, pd.DataFrame)

    def test_validate_returns_coerce_retry_paths_1487_1490(self, monkeypatch):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3),
                "BTC": [0.01, 0.02, -0.01],
                "ETH": [0.02, -0.01, 0.01],
                "JUNK": ["a", "b", "c"],
            }
        )
        calls = {"n": 0}
        orig_coerce = dlmod._coerce_numeric

        def bad_coerce(x):
            calls["n"] += 1
            if calls["n"] == 1:
                raise BABDataError("coerce fail")
            return orig_coerce(x)

        monkeypatch.setattr(dlmod, "_coerce_numeric", bad_coerce)
        out = dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_csv_df_becomes_empty_after_read_1588_1592(self, monkeypatch, tmp_path):
        p = tmp_path / "x.csv"
        p.write_text("date,BTC\n2024-01-01,0.1\n")

        class EmptyDF(pd.DataFrame):
            @property
            def empty(self):
                return True

        monkeypatch.setattr(
            pd, "read_csv", lambda *a, **k: EmptyDF({"date": ["2024-01-01"], "BTC": [0.1]})
        )
        monkeypatch.setattr(
            dlmod.pd, "read_csv", lambda *a, **k: EmptyDF({"date": ["2024-01-01"], "BTC": [0.1]})
        )
        with pytest.raises(BABDataError):
            dlmod.load_returns_from_csv(p)

    def test_normalize_index_elementwise_coerce_retry_bab_passthrough_194_196(self, monkeypatch):
        idx = ["bad1", "bad2"]
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        calls = {"n": 0}
        orig_to_dt = pd.to_datetime

        def bad_to_dt(*a, **k):
            calls["n"] += 1
            raise ValueError("parse fail")

        monkeypatch.setattr(pd, "to_datetime", bad_to_dt)
        monkeypatch.setattr(dlmod.pd, "to_datetime", bad_to_dt)

        def coerce_bab(v):
            raise BABDataError("coerce bab")

        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", coerce_bab)
        with pytest.raises(BABDataError, match="coerce bab|Failed to normalize"):
            dlmod._normalize_index(df.copy())
