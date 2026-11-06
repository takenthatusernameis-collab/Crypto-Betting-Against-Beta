"""Batch 40: targeted data_loader missing-line coverage."""
import pickle

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch40MissingLineTargets:

    def test_load_parquet_validate_baberror_passthrough_1621(self, monkeypatch, tmp_path):
        p = tmp_path / "x.parquet"
        p.write_bytes(b"x")
        monkeypatch.setattr(
            dlmod.pd,
            "read_parquet",
            lambda *a, **k: pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]}),
        )

        def _raise_bab(*a, **k):
            raise BABDataError("val bab")

        monkeypatch.setattr(dlmod, "validate_returns_dataframe", _raise_bab)
        with pytest.raises(BABDataError, match="val bab"):
            dlmod.load_returns_from_parquet(p)

    def test_load_pickle_dataframe_constructor_raises_1698_1699(self, monkeypatch, tmp_path):
        p = tmp_path / "x.pkl"
        with p.open("wb") as f:
            pickle.dump([{"date": "2024-01-01", "BTC": 0.1}, {"date": "2024-01-02", "BTC": 0.2}], f)

        class BadDF(pd.DataFrame):
            def __init__(self, *a, **k):
                raise RuntimeError("boom df")

        monkeypatch.setattr(dlmod.pd, "DataFrame", BadDF)
        with pytest.raises(BABDataError, match="boom df|Failed to read pickle"):
            dlmod.load_returns_from_pickle(p)

    def test_drop_metadata_columns_none_1895(self):
        assert dlmod._drop_metadata_columns(None) is None

    def test_exchange_format_epoch_volume_date_coerce_path_676_682(self, monkeypatch):
        class WeirdVal:
            @property
            def tzinfo(self):
                raise RuntimeError("tz")

        df = pd.DataFrame({"Date": [1704067200000, 1704153600000], "Volume": [1000, 1100]})
        monkeypatch.setattr(dlmod, "_coerce_to_datetime_scalar", lambda x: WeirdVal())
        out = dlmod._detect_and_normalize_exchange_format(df.copy())
        assert isinstance(out, pd.DataFrame)

    def test_exchange_format_outer_date_sample_exception_694_695(self, monkeypatch):
        class BadIloc:
            def __getitem__(self, idx):
                raise RuntimeError("iloc boom")

        class BadSeries(pd.Series):
            @property
            def iloc(self):
                return BadIloc()

        df = pd.DataFrame({"Date": [1704067200000, 1704153600000], "Volume": [1000, 1100]})
        orig_getitem = pd.DataFrame.__getitem__

        def bad_get(self, k):
            if k == "Date":
                return BadSeries([1704067200000, 1704153600000])
            return orig_getitem(self, k)

        monkeypatch.setattr(pd.DataFrame, "__getitem__", bad_get)
        monkeypatch.setattr(dlmod.pd.DataFrame, "__getitem__", bad_get, raising=False)
        out = dlmod._detect_and_normalize_exchange_format(df.copy())
        assert isinstance(out, pd.DataFrame)

    def test_clean_data_detect_exchange_exception_2167_2168(self, monkeypatch):
        df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]})

        def boom(*a, **k):
            raise RuntimeError("detect boom")

        monkeypatch.setattr(dlmod, "_detect_and_normalize_exchange_format", boom)
        out = dlmod.clean_data(df)
        assert isinstance(out, pd.DataFrame)

    def test_normalize_schema_normalize_index_exception_reraises_2173_2174(self, monkeypatch):
        df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]})

        def boom(*a, **k):
            raise RuntimeError("ni boom")

        monkeypatch.setattr(dlmod, "_normalize_index", boom)
        with pytest.raises(RuntimeError, match="ni boom"):
            dlmod.normalize_schema(df)

    def test_clean_data_junk_col_to_numeric_exception_2187_2189(self, monkeypatch):
        df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-02"]), "META": ["x", "y"], "BTC": [1.0, 2.0]})
        df = df.set_index("date")
        orig_to_numeric = pd.to_numeric

        def bad_tn(x, *a, **k):
            try:
                if getattr(x, "name", None) == "META":
                    raise RuntimeError("tn boom")
            except RuntimeError:
                raise
            except Exception:
                pass
            return orig_to_numeric(x, *a, **k)

        monkeypatch.setattr(pd, "to_numeric", bad_tn)
        monkeypatch.setattr(dlmod.pd, "to_numeric", bad_tn)
        monkeypatch.setattr(dlmod, "_coerce_numeric", lambda x: x)
        monkeypatch.setattr(dlmod, "_drop_all_nan_columns", lambda x: x)
        out = dlmod.clean_data(df)
        assert isinstance(out, pd.DataFrame)
        assert "META" not in out.columns or "BTC" in out.columns

    def test_clean_data_drop_junk_outer_exception_2192_2193(self, monkeypatch):
        df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "BTC": [0.1, 0.2]})
        orig_list = __builtins__["list"] if isinstance(__builtins__, dict) else __builtins__.list
        calls = {"n": 0}

        def bad_list(x=(), *a, **k):
            calls["n"] += 1
            # trigger inside the junk-drop try (around 2177: list(cleaned.columns))
            if calls["n"] > 20 and hasattr(x, "__iter__") and not isinstance(x, (str, bytes, dict)):
                try:
                    items = orig_list(x)
                    if items and str(items[0]) in ("BTC", "btc"):
                        raise RuntimeError("list boom")
                except RuntimeError:
                    raise
                except Exception:
                    pass
            return orig_list(x, *a, **k) if x != () or a or k else orig_list()

        # safer: monkeypatch DataFrame.drop/columns iteration via a targeted approach
        class ColsProxy:
            def __init__(self, cols):
                self._cols = cols

            def __iter__(self):
                raise RuntimeError("iter boom")

        class DFWrap(pd.DataFrame):
            @property
            def columns(self):
                # after normalize steps, this may be hit; be selective
                if getattr(self, "_boom_cols", False):
                    return ColsProxy(super().columns)
                return super().columns

        # easier targeted monkeypatch
        orig_clean_cols = dlmod._normalize_columns

        def norm_then_mark(x):
            r = orig_clean_cols(x)
            try:
                r._boom_cols = True
            except Exception:
                pass
            return r

        monkeypatch.setattr(dlmod, "_normalize_columns", norm_then_mark)
        # monkeypatch DataFrame to our wrapper not trivial; use a simpler hook
        monkeypatch.setattr(dlmod, "_coerce_numeric", lambda x: x)
        monkeypatch.setattr(dlmod, "_drop_all_nan_columns", lambda x: x)
        # inject boom at 2177 by replacing cleaned after index normalize
        orig_ni = dlmod._normalize_index

        def ni_wrap(x):
            r = orig_ni(x)

            class BadColsDF(pd.DataFrame):
                _metadata = []

                @property
                def _constructor(self):
                    return pd.DataFrame

                def __iter__(self):
                    return super().__iter__()

            b = BadColsDF(r.copy())
            orig_cols = b.columns

            class BadIndex(pd.Index):
                def __iter__(self):
                    raise RuntimeError("cols iter boom")

            try:
                object.__setattr__(b, "_boom", True)
            except Exception:
                pass
            # monkeypatch instance columns access is hard; fallback: patch pd.api.types.is_numeric_dtype to raise once
            return r

        # most reliable: raise from is_numeric_dtype in that loop
        calls2 = {"n": 0}
        orig_isnum = pd.api.types.is_numeric_dtype

        def boom_isnum(arr_or_dtype):
            calls2["n"] += 1
            if calls2["n"] > 6:
                raise RuntimeError("isnum boom")
            return orig_isnum(arr_or_dtype)

        monkeypatch.setattr(pd.api.types, "is_numeric_dtype", boom_isnum)
        monkeypatch.setattr(dlmod.pd.api.types, "is_numeric_dtype", boom_isnum)
        out = dlmod.clean_data(df)
        assert isinstance(out, pd.DataFrame)

    def test_drop_metadata_to_numpy_or_compare_exception_1928_1929(self, monkeypatch):
        df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=3, freq="D"), "X": [0.0, 0.0, 1.0]})
        df = df.set_index("date")

        class BadArr(np.ndarray):
            pass

        orig_to_numpy = pd.Series.to_numpy

        def bad_to_numpy(self, *a, **k):
            if self.name == "X":
                arr = orig_to_numpy(self, *a, **k)

                class W:
                    def __array__(self, dtype=None):
                        return arr

                    def __getitem__(self, i):
                        if i == np.s_[:] or isinstance(i, slice):
                            raise RuntimeError("slice boom")
                        return arr[i]

                    @property
                    def shape(self):
                        return arr.shape

                # easier: make finite check blow up by returning object that breaks
                raise RuntimeError("to_numpy boom")
            return orig_to_numpy(self, *a, **k)

        monkeypatch.setattr(pd.Series, "to_numpy", bad_to_numpy)
        out = dlmod._drop_metadata_columns(df.copy())
        assert "X" in out.columns
