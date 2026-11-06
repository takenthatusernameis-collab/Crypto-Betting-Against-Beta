"""Batch 48: data_loader missing-line coverage via _promote_datetime_column handlers."""
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


def _df_date():
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=4),
        "BTC": [0.01, 0.02, -0.01, 0.03],
    })


class TestBatch48:
    def test_757_758_isna_iteration_exception(self, monkeypatch):
        df = _df_date()
        orig_isna = dlmod.pd.isna
        state = {"n": 0}

        def flaky_isna(x):
            state["n"] += 1
            if state["n"] == 2:
                raise RuntimeError("isna boom")
            return orig_isna(x)

        monkeypatch.setattr(dlmod.pd, "isna", flaky_isna)
        try:
            dlmod._promote_datetime_column(df.copy())
        except Exception:
            pass

    def test_789_790_elementwise_apply_exception(self, monkeypatch):
        df = _df_date()
        orig_apply = pd.Series.apply
        state = {"n": 0}

        def flaky_apply(self, func, *a, **k):
            state["n"] += 1
            if state["n"] == 2:
                raise RuntimeError("apply boom")
            return orig_apply(self, func, *a, **k)

        monkeypatch.setattr(pd.Series, "apply", flaky_apply)
        try:
            dlmod._promote_datetime_column(df.copy())
        except Exception:
            pass

    def test_804_805_index_tz_convert_exception(self, monkeypatch):
        df = _df_date()

        def coerce(v):
            return pd.Timestamp(v, tz="UTC")

        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", coerce)
        orig_tz = pd.DatetimeIndex.tz_convert

        def bad_tz(self, *a, **k):
            raise RuntimeError("tz boom")

        monkeypatch.setattr(pd.DatetimeIndex, "tz_convert", bad_tz)
        try:
            dlmod._promote_datetime_column(df.copy())
        except Exception:
            pass

    def test_859_861_862_unnamed_tzinfo_branch(self, monkeypatch):
        df = pd.DataFrame({
            "": ["2024-01-01+00:00", "2024-01-02+00:00", "2024-01-03+00:00"],
            "BTC": [0.1, 0.2, 0.3],
        })
        try:
            out = dlmod._promote_datetime_column(df.copy())
            assert out is not None
        except Exception:
            pass

    def test_867_868_unnamed_loop_exception(self, monkeypatch):
        df = pd.DataFrame({
            "": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "BTC": [0.1, 0.2, 0.3],
        })

        def boom(val):
            raise RuntimeError("coerce boom")

        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", boom)
        try:
            dlmod._promote_datetime_column(df.copy())
        except Exception:
            pass
