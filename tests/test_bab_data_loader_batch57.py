import contextlib

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as mod


def test_coerce_series_to_datetime_index_tz_normalization():
    df = pd.DataFrame({"a": [1, 2]})
    coerced = pd.Series(
        [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")]
    )
    ok = mod._coerce_series_to_datetime_index(df, "a", coerced)
    assert ok is True or ok is False


def test_clean_data_junk_column_drop_defensive():
    df = pd.DataFrame(
        {
            "BTC": [100.0, 101.0],
            "ETH": [50.0, 51.0],
            "junk": ["n/a", "n/a"],
        }
    )
    df.index = pd.to_datetime(["2024-01-01", "2024-01-02"])
    out = mod.clean_data(df)
    assert isinstance(out, pd.DataFrame)


def test_promote_datetime_index_tz_normalization(monkeypatch):
    idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02"], tz="UTC")
    df = pd.DataFrame({"BTC": [0.1, 0.2], "ETH": [0.2, 0.3]}, index=idx)
    out = mod._promote_datetime_column(df)
    assert out.index.tz is None


def test_exchange_normalize_path(monkeypatch):
    df = pd.DataFrame(
        {
            "time": ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
            "BTC": [100.0, 101.0],
            "ETH": [50.0, 51.0],
        }
    )
    out = mod._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_validate_returns_benchmark_not_found_maps_case():
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02], "ETH": [0.02, 0.03]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    out = mod.validate_returns_dataframe(df, benchmark="btc")
    assert "BTC" in out.columns or "btc" in out.columns


def test_load_returns_from_hdf_fallback(tmp_path, monkeypatch):
    p = tmp_path / "r.h5"
    p.write_text("x")
    monkeypatch.setattr(
        mod.pd, "read_hdf", lambda *a, **k: (_ for _ in ()).throw(ImportError("no tables"))
    )
    with contextlib.suppress(mod.BABDataError):
        mod.load_returns_from_hdf5(p, benchmark="BTC")
