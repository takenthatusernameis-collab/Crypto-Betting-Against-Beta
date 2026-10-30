"""Data source tests for `strategies/betting_against_beta/data_sources.py`."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import (
    CSVDataSource,
    DataCache,
    DataFrameDataSource,
    DataSource,
    HDF5DataSource,
    ParquetDataSource,
    PickleDataSource,
)


def _df(n=30):
    rng = np.random.RandomState(1)
    idx = pd.date_range("2023-01-01", periods=n)
    return pd.DataFrame(
        {"BTC": rng.normal(0, 0.01, n), "ETH": rng.normal(0, 0.015, n)}, index=idx
    )


def test_datasource_abstract_cannot_instantiate():
    with pytest.raises(TypeError):
        DataSource()


def test_csv_datasource_load(tmp_path):
    p = tmp_path / "r.csv"
    _df().to_csv(p)
    out = CSVDataSource(p).load()
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_parquet_datasource_load(tmp_path):
    pytest.importorskip("pyarrow")
    p = tmp_path / "r.parquet"
    _df().to_parquet(p)
    out = ParquetDataSource(p).load()
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_hdf5_datasource_load_with_key(tmp_path):
    pytest.importorskip("tables")
    p = tmp_path / "r.h5"
    _df().to_hdf(p, key="data", mode="w")
    out = HDF5DataSource(p, key="data").load()
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_pickle_datasource_load(tmp_path):
    p = tmp_path / "r.pkl"
    _df().to_pickle(p)
    out = PickleDataSource(p).load()
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_dataframe_datasource_load():
    df = _df()
    out = DataFrameDataSource(df).load()
    pd.testing.assert_frame_equal(out, df)


def test_datasource_load_benchmark_and_min_rows(tmp_path):
    p = tmp_path / "r.csv"
    _df().to_csv(p)
    out = CSVDataSource(p).load(benchmark="BTC", min_rows=5)
    assert isinstance(out, pd.DataFrame)


def test_datasource_load_pass_through_kwargs(tmp_path):
    p = tmp_path / "r.csv"
    _df().to_csv(p)
    out = CSVDataSource(p).load(benchmark="BTC")
    assert isinstance(out, pd.DataFrame)


def test_data_cache_get_set_miss():
    cache = DataCache(max_entries=4)
    assert cache.get("missing") is None
    df = _df(10)
    cache.set("a", df)
    got = cache.get("a")
    assert isinstance(got, pd.DataFrame)
    pd.testing.assert_frame_equal(got, df)
    # external mutation must not affect cache
    df.iloc[0, 0] = 999.0
    assert cache.get("a").iloc[0, 0] != 999.0


def test_data_cache_eviction_lru():
    cache = DataCache(max_entries=2)
    cache.set("a", _df(5))
    cache.set("b", _df(5))
    cache.get("a")  # a now most recently used
    cache.set("c", _df(5))  # evicts b (least recently used)
    assert cache.get("b") is None
    assert cache.get("a") is not None
    assert cache.get("c") is not None


def test_data_cache_overwrite_moves_to_end():
    cache = DataCache(max_entries=2)
    cache.set("a", _df(5))
    cache.set("b", _df(5))
    cache.set("a", _df(5))  # a refreshed, now MRU
    cache.set("c", _df(5))  # evicts b
    assert cache.get("b") is None
    assert cache.get("a") is not None


def test_data_cache_max_entries_non_positive():
    cache = DataCache(max_entries=0)
    cache.set("a", _df(5))
    assert cache.get("a") is None


def test_hdf5_datasource_load_no_key_passes_through(tmp_path):
    pytest.importorskip("tables")
    p = tmp_path / "r.h5"
    _df().to_hdf(p, key="data", mode="w")
    out = HDF5DataSource(p).load(key="data")
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_hdf5_datasource_load_no_key_no_extra_kwargs(tmp_path):
    pytest.importorskip("tables")
    p = tmp_path / "r.h5"
    df = _df()
    df.to_hdf(p, key="data", mode="w")
    out = HDF5DataSource(p).load()
    assert isinstance(out, pd.DataFrame)


def test_parquet_pass_through_kwargs(tmp_path):
    pytest.importorskip("pyarrow")
    p = tmp_path / "r.parquet"
    _df().to_parquet(p)
    out = ParquetDataSource(p).load(benchmark="BTC", min_rows=1)
    assert isinstance(out, pd.DataFrame)


def test_pickle_pass_through_kwargs(tmp_path):
    p = tmp_path / "r.pkl"
    _df().to_pickle(p)
    out = PickleDataSource(p).load(benchmark="BTC")
    assert isinstance(out, pd.DataFrame)


def test_csv_pass_through(tmp_path):
    p = tmp_path / "r.csv"
    _df().to_csv(p)
    out = CSVDataSource(p).load(min_rows=10)
    assert isinstance(out, pd.DataFrame)


def test_dataframe_source_pass_through_kwargs():
    df = _df()
    out = DataFrameDataSource(df).load(benchmark="BTC", min_rows=5)
    assert isinstance(out, pd.DataFrame)


def test_data_cache_get_when_cached_not_dataframe():
    cache = DataCache(max_entries=4)
    # manually inject non-DataFrame
    cache._cache["x"] = "notdf"
    cache._order = ["x"]
    assert cache.get("x") == "notdf"


def test_data_cache_set_when_existing_key_updates_order():
    cache = DataCache(max_entries=10)
    cache.set("a", _df(3))
    cache.set("a", _df(4))  # overwrite existing
    got = cache.get("a")
    assert isinstance(got, pd.DataFrame)


def test_data_cache_evict_when_order_corrupted_value_error():
    cache = DataCache(max_entries=1)
    cache.set("a", _df(3))
    # corrupt order
    cache._order = []
    cache.get("a")  # should handle ValueError on remove
    cache.set("b", _df(3))  # should still evict properly


def test_data_cache_set_non_dataframe_stored_as_is():
    cache = DataCache(max_entries=3)
    cache.set("x", "hello")
    assert cache.get("x") == "hello"
