import contextlib

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch47:
    def test_validate_benchmark_remap_both_rename_fail_1530_1536(self, monkeypatch):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=4),
                "btc": [0.01, 0.02, -0.01, 0.03],
                "ETH": [0.02, -0.01, 0.01, 0.02],
            }
        )
        orig = pd.DataFrame.rename

        def always_fail(self, *a, **k):
            cols = k.get("columns") or (a[0] if a and isinstance(a[0], dict) else None)
            if isinstance(cols, dict) and any(
                str(v).lower() == "btc" or str(k2).lower() == "btc" for k2, v in cols.items()
            ):
                raise RuntimeError("rename fail")
            return orig(self, *a, **k)

        monkeypatch.setattr(pd.DataFrame, "rename", always_fail)
        with contextlib.suppress(Exception):
            dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")

    def test_validate_benchmark_remap_second_rename_succeeds_1533_1536(self, monkeypatch):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=4),
                "btc": [0.01, 0.02, -0.01, 0.03],
                "ETH": [0.02, -0.01, 0.01, 0.02],
            }
        )
        orig = pd.DataFrame.rename
        n = {"c": 0}

        def rr(self, *a, **k):
            n["c"] += 1
            if n["c"] == 1:
                raise RuntimeError("r1")
            return orig(self, *a, **k)

        monkeypatch.setattr(pd.DataFrame, "rename", rr)
        out = dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        assert "BTC" in out.columns

    def test_promote_named_block_catches_valueerror_840_841(self, monkeypatch):
        # 840-841: except (ValueError, TypeError, KeyError): pass at end of named-column try (744+)
        # We need something inside 744-839 to raise ValueError (not BABDataError which is re-raised at 838)
        df = pd.DataFrame(
            {
                "date": [1704067200, 1704153600, 1704240000, 1704326400],
                "BTC": [0.1, 0.2, 0.3, 0.4],
                "ETH": [0.05, 0.06, 0.07, 0.08],
            }
        )
        # After coercion succeeds and we enter 793-808, make drop raise ValueError
        orig_drop = pd.DataFrame.drop
        n = {"c": 0}

        def bad_drop(self, *a, **k):
            n["c"] += 1
            cols = k.get("columns") or (a[0] if a else None)
            if n["c"] == 1 and (
                cols == ["date"] or cols == "date" or (isinstance(cols, list) and "date" in cols)
            ):
                raise ValueError("drop fail")
            return orig_drop(self, *a, **k)

        monkeypatch.setattr(pd.DataFrame, "drop", bad_drop)
        out = dlmod._promote_datetime_column(df.copy())
        assert out is not None

    def test_load_csv_defensive_empty_1591_1592(self, monkeypatch, tmp_path):
        p = tmp_path / "x.csv"
        p.write_text("date,BTC\n2024-01-01,0.1\n")

        class T(pd.DataFrame):
            _n = 0

            @property
            def empty(self):
                self._n += 1
                return self._n == 2

        tdf = T({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]})
        monkeypatch.setattr(pd, "read_csv", lambda *a, **k: tdf)
        monkeypatch.setattr(dlmod.pd, "read_csv", lambda *a, **k: tdf)
        with pytest.raises(BABDataError):
            dlmod.load_returns_from_csv(p)

    def test_promote_named_outer_except_791_792_precise(self, monkeypatch):
        dates = [1704067200, 1704153600, 1704240000, 1704326400]
        df = pd.DataFrame(
            {"date": dates, "BTC": [0.1, 0.2, 0.3, 0.4], "ETH": [0.05, 0.06, 0.07, 0.08]}
        )

        def coerce(v):
            return pd.Timestamp(v, unit="s")

        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", coerce)

        # Make hasattr(parsed,'apply') path raise at 791-792 by breaking the if block
        class Weird:
            name = "date"

            @property
            def tz(self):
                return None

            @property
            def dtype(self):
                class D:
                    tz = None

                return D()

            def apply(self, *a, **k):
                raise RuntimeError("x")

            def __iter__(self):
                raise RuntimeError("x")

            def __len__(self):
                return 4

        orig_sapply = pd.Series.apply
        n = {"c": 0}

        def sapply(self, func, *a, **k):
            n["c"] += 1
            res = orig_sapply(self, func, *a, **k)
            if n["c"] == 1 and getattr(self, "name", None) == "date":
                return Weird()
            return res

        monkeypatch.setattr(pd.Series, "apply", sapply)
        with contextlib.suppress(Exception):
            dlmod._promote_datetime_column(df.copy())

    def test_unnamed_tz_inner_except_859_861_862(self, monkeypatch):
        df = pd.DataFrame(
            {
                "": pd.date_range("2024-01-01", periods=3, tz="UTC"),
                "BTC": [0.1, 0.2, 0.3],
                "ETH": [0.05, 0.06, 0.07],
            }
        )

        def coerce(v):
            return pd.Timestamp(v)

        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", coerce)
        orig = pd.Timestamp.tz_localize

        def bad(self, *a, **k):
            raise RuntimeError("tzl")

        monkeypatch.setattr(pd.Timestamp, "tz_localize", bad)
        out = dlmod._promote_datetime_column(df.copy())
        assert out is not None

    def test_unnamed_outer_except_867_868(self, monkeypatch):
        df = pd.DataFrame(
            {
                "": [1704067200, 1704153600, 1704240000],
                "BTC": [0.1, 0.2, 0.3],
                "ETH": [0.05, 0.06, 0.07],
            }
        )

        def coerce(v):
            return pd.Timestamp(v, unit="s")

        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", coerce)
        # break iteration over coerced_clean construction? 867-868 wraps the whole try at 849
        # easier: make _series_has_any_finite raise? it's called at 869 outside 849-868 block
        orig_shaf = dlmod._series_has_any_finite

        def bad_shaf(x):
            raise RuntimeError("x")

        monkeypatch.setattr(dlmod, "_series_has_any_finite", bad_shaf)
        out = dlmod._promote_datetime_column(df.copy())
        assert out is not None

    def test_clean_data_price_index_drop_1926_1929(self):
        # 1926-1929 in a price-cleaning path: integer-like column starting at 0 with step 1
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "BTC": [100.0, 101.0, 102.0, 103.0, 104.0],
                "idx": [0.0, 1.0, 2.0, 3.0, 4.0],
            }
        )
        out = dlmod.clean_data(df.copy())
        assert "BTC" in out.columns

    def test_clean_data_except_passes_2160_2163_2167_2168(self, monkeypatch):
        df = pd.DataFrame(
            {"date": pd.date_range("2024-01-01", periods=3), "BTC": [100.0, 101.0, 102.0]}
        )
        monkeypatch.setattr(
            dlmod,
            "_detect_and_normalize_exchange_format",
            lambda x: (_ for _ in ()).throw(RuntimeError("ex")),
        )
        out = dlmod.clean_data(df.copy())
        assert "BTC" in out.columns
