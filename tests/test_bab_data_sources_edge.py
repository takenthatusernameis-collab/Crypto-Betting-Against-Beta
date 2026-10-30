"""Edge-branch coverage for data_sources.py.

Cover the abstract ``NotImplementedError``, HDF5 key injection, and the
DataCache ``set`` ValueError path.
"""

import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import (
    CSVDataSource,
    DataCache,
    DataSource,
    HDF5DataSource,
)


class TestDataSourceAbstract:
    def test_unimplemented_load_raises(self):
        # data_sources.py:20 ``raise NotImplementedError``

        class Raw(DataSource):
            def load(self, **kwargs):
                return super().load(**kwargs)

        src = Raw()
        with pytest.raises(NotImplementedError):
            src.load()


class TestHDF5DataSource:
    def test_key_injected_into_kwargs(self):
        # data_sources.py:47 ``kwargs["key"] = self.key``
        src = HDF5DataSource("/tmp/nonexistent.h5", key="mygroup")
        captured = {}

        import strategies.betting_against_beta.data_sources as ds

        orig = ds.load_returns

        def fake_load_returns(path, benchmark=None, min_rows=1, **kw):
            captured.update(kw)
            raise RuntimeError("stop before IO")

        ds.load_returns = fake_load_returns
        try:
            with pytest.raises(RuntimeError):
                src.load()
        finally:
            ds.load_returns = orig
        assert captured.get("key") == "mygroup"


class TestDataCache:
    def test_set_remove_valueerror_path(self):
        # data_sources.py:94-95 ``except ValueError: pass`` when key is cached
        # but absent from the order list.
        cache = DataCache(max_entries=4)
        import pandas as pd

        df = pd.DataFrame({"a": [1.0]})
        # Corrupt state: present in _cache but absent from _order.
        cache._cache["k"] = df
        cache.set("k", df)
        assert cache.get("k") is not None
        assert "k" in cache._order
