"""Campaign tests for data_sources.py pass-through and error paths."""

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
from strategies.betting_against_beta.errors import BABDataError


def _df(n=30):
    rng = np.random.default_rng(1)
    idx = pd.date_range("2023-01-01", periods=n)
    return pd.DataFrame(
        {"BTC": rng.normal(0, 0.01, n), "ETH": rng.normal(0, 0.015, n)}, index=idx
    )


def test_datasource_abstract_cannot_instantiate():
    with pytest.raises(TypeError):
        DataSource()


def test_csv_datasource_missing_file_raises():
    with pytest.raises(BABDataError):
        CSVDataSource("no_such_file.csv").load()


def test_csv_datasource_directory_read_error(tmp_path):
    d = tmp_path / "adir.csv"
    d.mkdir()
    with pytest.raises(BABDataError):
        CSVDataSource(d).load()


def test_csv_datasource_load(tmp_path):
    p = tmp_path / "r.csv"
    _df().to_csv(p)
    out = CSVDataSource(p).load()
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_dataframe_datasource_pass_through_benchmark_min_rows():
    df = _df()
    out = DataFrameDataSource(df).load(benchmark="BTC", min_rows=5)
    assert isinstance(out, pd.DataFrame)


def test_pickle_datasource_load(tmp_path):
    p = tmp_path / "r.pkl"
    _df().to_pickle(p)
    out = PickleDataSource(p).load()
    assert isinstance(out, pd.DataFrame) and not out.empty


def test_parquet_datasource_skipped_without_engine(tmp_path):
    p = tmp_path / "r.parquet"
    p.write_bytes(b"not parquet")
    with pytest.raises(BABDataError):
        ParquetDataSource(p).load()


def test_hdf5_datasource_skipped_without_engine(tmp_path):
    p = tmp_path / "r.h5"
    p.write_bytes(b"not hdf5")
    with pytest.raises(BABDataError):
        HDF5DataSource(p).load()


def test_data_cache_get_returns_copy_dataframe():
    cache = DataCache(max_entries=4)
    df = _df(10)
    cache.set("a", df)
    got = cache.get("a")
    assert isinstance(got, pd.DataFrame)
    got.iloc[0, 0] = 999.0
    assert cache.get("a").iloc[0, 0] != 999.0


def test_data_cache_get_when_cached_not_dataframe():
    cache = DataCache(max_entries=4)
    cache._cache["x"] = "notdf"
    cache._order = ["x"]
    assert cache.get("x") == "notdf"


def test_data_cache_max_entries_zero_evicts_immediately():
    cache = DataCache(max_entries=0)
    cache.set("a", _df(5))
    assert cache.get("a") is None


def test_data_cache_evict_when_order_corrupted_value_error():
    cache = DataCache(max_entries=1)
    cache.set("a", _df(3))
    cache._order = []
    cache.get("a")
    cache.set("b", _df(3))
    assert cache.get("b") is not None
