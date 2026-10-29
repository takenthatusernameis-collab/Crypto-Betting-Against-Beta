"""Pluggable data sources for BAB strategy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd

from .data_loader import load_returns


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def load(self, **kwargs) -> pd.DataFrame:
        """Load returns data as a DataFrame."""
        raise NotImplementedError


class CSVDataSource(DataSource):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class ParquetDataSource(DataSource):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class HDF5DataSource(DataSource):
    def __init__(self, path: str | Path, key: str | None = None):
        self.path = Path(path)
        self.key = key

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        kwargs = dict(kwargs)
        if self.key is not None and "key" not in kwargs:
            kwargs["key"] = self.key
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class PickleDataSource(DataSource):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class DataFrameDataSource(DataSource):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.df, benchmark=benchmark, min_rows=min_rows, **kwargs)


class DataCache:
    """Simple in-memory cache for loaded data with basic size limits."""

    def __init__(self, max_entries: int = 32):
        self.max_entries = int(max_entries)
        self._cache: dict[str, pd.DataFrame] = {}
        self._order: list[str] = []

    def get(self, key: str) -> pd.DataFrame | None:
        if key in self._cache:
            # move to end (LRU-ish)
            try:
                self._order.remove(key)
            except ValueError:
                pass
            self._order.append(key)
            # return a copy to avoid external mutation
            cached = self._cache[key]
            if isinstance(cached, pd.DataFrame):
                return cached.copy()
            return cached
        return None

    def set(self, key: str, df: pd.DataFrame) -> None:
        if key in self._cache:
            try:
                self._order.remove(key)
            except ValueError:
                pass
        self._cache[key] = df.copy() if isinstance(df, pd.DataFrame) else df
        self._order.append(key)
        while len(self._order) > self.max_entries:
            oldest = self._order.pop(0)
            self._cache.pop(oldest, None)
