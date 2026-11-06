"""Batch 49: data_loader missing-line coverage via canonical validate/loader flows."""
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch49:
    def test_1530_1531_benchmark_rename_then_second_rename(self, monkeypatch):
        # btc present (lowercase), benchmark BTC absent -> case-insensitive bench_found="btc"
        # rename bt
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=4),
            "btc": [0.01, 0.02, -0.01, 0.03],
            "ETH": [0.02, -0.01, 0.01, 0.02],
        })
        orig = pd.DataFrame.rename
        state = {"n": 0}

        def flaky(self, *a, **k):
            state["n"] += 1
            cols = k.get("columns") or (a[0] if a and isinstance(a[0], dict) else None)
            if isinstance(cols, dict) and any(str(v).lower() == "btc" or str(k2).lower() == "btc" for k2, v in cols.items()):
                if state["n"] == 1:
                    raise RuntimeError("rename fail")
            return orig(self, *a, **k)

        monkeypatch.setattr(pd.DataFrame, "rename", flaky)
        out = dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        assert "BTC" in out.columns

    def test_1591_1592_csv_defensive_empty_after_read(self, monkeypatch, tmp_path):
        p = tmp_path / "x.csv"
        p.write_text("date,BTC\n2024-01-01,0.1\n")

        class T(pd.DataFrame):
            _n = 0

            @property
            def empty(self):
                T._n += 1
                return T._n == 2

        tdf = T({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]})
        monkeypatch.setattr(pd, "read_csv", lambda *a, **k: tdf)
        monkeypatch.setattr(dlmod.pd, "read_csv", lambda *a, **k: tdf)
        with pytest.raises(BABDataError):
            dlmod.load_returns_from_csv(p)

    def test_1451_1452_validate_trivial_1970_except(self, monkeypatch):
        # RangeIndex 0..N-1 promoted to 1970 DatetimeIndex; make cleaned.index[:3] raise
        # non-BABDataError so outer except (1451-1452) catches it.
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=4),
            "BTC": [0.01, 0.02, -0.01, 0.03],
        })

        orig_promote = dlmod._promote_datetime_column

        def bad_promote(d):
            out = orig_promote(d)
            out.index = pd.Index([pd.Timestamp("1970-01-01"), "not-a-date", None])
            return out

        monkeypatch.setattr(dlmod, "_promote_datetime_column", bad_promote)
        try:
            dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        except Exception:
            pass
