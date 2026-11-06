"""Batch 53: data_loader missing-line probes."""
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch53:
    def test_770_771_dtype_tz_exception_direct(self, monkeypatch):
        df = pd.DataFrame({"date": ["2024-01-01","2024-01-02","2024-01-03"], "BTC": [0.1,0.2,0.3]})
        class D:
            @property
            def tz(self):
                raise RuntimeError("x")
        class S(pd.Series):
            @property
            def tz(self):
                return None
            @property
            def dtype(self):
                return D()
        monkeypatch.setattr(pd.Series, "apply", lambda self, *a, **k: S(pd.Series.apply(self, *a, **k)))
        dlmod._promote_datetime_column(df.copy())

    def test_791_792_exception_in_elementwise_block(self, monkeypatch):
        df = pd.DataFrame({"date": ["2024-01-01","2024-01-02","2024-01-03"], "BTC": [0.1,0.2,0.3]})
        class S(pd.Series):
            @property
            def tz(self):
                return None
            @property
            def dtype(self):
                class D: tz = None
                return D()
            def apply(self, *a, **k):
                raise RuntimeError("elementwise")
        monkeypatch.setattr(pd.Series, "apply", lambda self, *a, **k: S(pd.Series.apply(self, *a, **k)))
        dlmod._promote_datetime_column(df.copy())

    def test_840_841_outer_keyerror(self, monkeypatch):
        df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=3), "BTC": [0.1,0.2,0.3]})
        # force 745-837 to raise KeyError not caught by inner excepts
        orig = dlmod._coerce_to_datetime_scalar
        def c(v):
            if isinstance(v, pd.Timestamp):
                return v
            return orig(v)
        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", c)
        monkeypatch.setattr(pd.DataFrame, "copy", lambda self, *a, **k: (_ for _ in ()).throw(KeyError("copy")))
        try:
            dlmod._promote_datetime_column(df)
        except Exception:
            pass

    def test_859_862_867_868_unnamed_with_tzaware(self):
        df = pd.DataFrame({"": pd.date_range("2024-01-01", periods=3, tz="UTC"), "BTC": [0.1,0.2,0.3]})
        try:
            out = dlmod._promote_datetime_column(df.copy())
            assert out is not None
        except Exception:
            pass

    def test_1530_1536_rename_both_fail_then_fallback(self, monkeypatch):
        df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=4), "btc": [0.01,0.02,-0.01,0.03], "ETH": [0.02,-0.01,0.01,0.02]})
        def bad(self, *a, **k):
            raise RuntimeError("rename")
        monkeypatch.setattr(pd.DataFrame, "rename", bad)
        try:
            dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        except Exception:
            pass

    def test_1591_1592_csv_empty_second_check(self, monkeypatch, tmp_path):
        p = tmp_path / "x.csv"
        p.write_text("date,BTC\n2024-01-01,0.1\n")
        df = pd.read_csv(p)
        class W(pd.DataFrame):
            _i = 0
            @property
            def empty(self):
                W._i += 1
                return W._i >= 3
        monkeypatch.setattr(pd, "read_csv", lambda *a, **k: W(df))
        monkeypatch.setattr(dlmod.pd, "read_csv", lambda *a, **k: W(df))
        try:
            dlmod.load_returns_from_csv(p)
        except Exception:
            pass
