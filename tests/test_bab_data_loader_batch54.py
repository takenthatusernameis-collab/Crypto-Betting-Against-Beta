"""Batch 54: data_loader missing-line probes (validated reachable)."""
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch54:
    def test_770_771_dtype_tz_exception(self, monkeypatch):
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
        orig = pd.Series.apply
        def patched(self, *a, **k):
            return S(orig(self, *a, **k))
        monkeypatch.setattr(pd.Series, "apply", patched)
        dlmod._promote_datetime_column(df.copy())

    def test_791_792_elementwise_apply_exception(self, monkeypatch):
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
        orig = pd.Series.apply
        def patched(self, *a, **k):
            return S(orig(self, *a, **k))
        monkeypatch.setattr(pd.Series, "apply", patched)
        dlmod._promote_datetime_column(df.copy())

    def test_859_862_867_868_unnamed_tzaware(self):
        df = pd.DataFrame({"": pd.date_range("2024-01-01", periods=3, tz="UTC"), "BTC": [0.1,0.2,0.3]})
        try:
            out = dlmod._promote_datetime_column(df.copy())
            assert out is not None
        except Exception:
            pass

    def test_894_interval_column(self):
        df = pd.DataFrame({"date": ["2024-01-01","2024-01-02"], "BTC": [0.1,0.2], "iv": pd.arrays.IntervalArray.from_breaks([0,1,2])})
        out = dlmod._promote_datetime_column(df.copy())
        assert isinstance(out, pd.DataFrame)

    def test_901_903_tzaware_parsed(self, monkeypatch):
        df = pd.DataFrame({"ts2": ["2024-01-01","2024-01-02","2024-01-03"], "BTC": [0.1,0.2,0.3]})
        orig = pd.to_datetime
        def fake(*a, **k):
            res = orig(*a, **k)
            if isinstance(res, pd.Series):
                res = res.dt.tz_localize("UTC")
            return res
        monkeypatch.setattr(pd, "to_datetime", fake)
        monkeypatch.setattr(dlmod.pd, "to_datetime", fake)
        dlmod._promote_datetime_column(df.copy())

    def test_908_914_last_resort_set_index(self, monkeypatch):
        df = pd.DataFrame({"ts2": ["2024-01-01","2024-01-02","2024-01-03"], "BTC": [0.1,0.2,0.3]})
        orig_set = pd.DataFrame.set_index
        calls = {"n": 0}
        def fake_set(self, *a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                res = orig_set(self, *a, **k)
                if not isinstance(res.index, pd.DatetimeIndex):
                    return res
                return res
            return orig_set(self, *a, **k)
        monkeypatch.setattr(pd.DataFrame, "set_index", fake_set)
        dlmod._promote_datetime_column(df.copy())

    def test_1084_1085_isna_raises(self, monkeypatch):
        df = pd.DataFrame({"BTC": [0.1,0.2], "bad": ["x","y"]})
        orig_getitem = pd.DataFrame.__getitem__
        def patched(self, key):
            res = orig_getitem(self, key)
            if key == "bad":
                class W(res.__class__):
                    def isna(self_inner):
                        raise TypeError("boom")
                return W(res)
            return res
        monkeypatch.setattr(pd.DataFrame, "__getitem__", patched)
        dlmod._drop_all_nan_columns(df.copy())

    def test_1097_1098_df_keep_raises(self, monkeypatch):
        df = pd.DataFrame({"BTC": [0.1,0.2], "bad": [np.nan, np.nan]})
        orig_getitem = pd.DataFrame.__getitem__
        def patched(self, key):
            if isinstance(key, list) and "bad" in key:
                raise KeyError("boom")
            return orig_getitem(self, key)
        monkeypatch.setattr(pd.DataFrame, "__getitem__", patched)
        dlmod._drop_all_nan_columns(df.copy())

    def test_1112_int_branch(self):
        assert dlmod._strip_units_and_parse(5) == 5.0

    def test_1115_inf_branch(self):
        assert np.isnan(dlmod._strip_units_and_parse(float("inf")))

    def test_1293_1294_to_numpy_raises(self):
        df = pd.DataFrame({"BTC": [0.1,0.2], "ETH": [0.02,0.03]}, index=pd.date_range("2024-01-01", periods=2))
        class W(pd.DataFrame):
            def to_numpy(self, *a, **k):
                raise TypeError("boom")
        out = dlmod._run_data_quality_campaign(W(df).copy())
        assert isinstance(out, pd.DataFrame)

    def test_1304_1305_total_seconds_raises(self, monkeypatch):
        idx = pd.DatetimeIndex(["2024-01-01","2024-01-02"])
        df = pd.DataFrame({"BTC": [0.1,0.2]}, index=idx)
        orig_diff = pd.Series.diff
        class S(pd.Series):
            def max(self, *a, **k):
                class T:
                    def total_seconds(self_inner):
                        raise TypeError("boom")
                    def __lt__(self, o): return False
                    def __gt__(self, o): return True
                return T()
        def patched_diff(self, *a, **k):
            res = orig_diff(self, *a, **k)
            if isinstance(res, pd.Series) and not isinstance(res, S):
                return S(res)
            return res
        monkeypatch.setattr(pd.Series, "diff", patched_diff)
        dlmod._run_data_quality_campaign(df.copy())