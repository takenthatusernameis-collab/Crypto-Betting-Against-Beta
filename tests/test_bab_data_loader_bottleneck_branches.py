"""Bottleneck branch coverage for data_loader.py.

Hits reachable uncovered branches left behind by the existing suite: empty
all-NaN column short-circuit, unnamed-column datetime parse failure, corrupt
pickle, and unreadable CSV. Real assertions on exception types and output
only. Unreachable paths left alone per the no-spinning rule.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _drop_all_nan_columns,
    _promote_datetime_column,
    load_returns_from_csv,
    load_returns_from_pickle,
)


class TestDropAllNanColumns:
    def test_empty_dataframe_returned_as_is(self):
        # data_loader.py:106-107 empty df short-circuit
        df = pd.DataFrame()
        out = _drop_all_nan_columns(df)
        assert out.empty


class TestPromoteDatetimeColumn:
    def test_unnamed_datetime_parse_failure(self):
        # data_loader.py:71-73 to_datetime raise -> parsed None, fall through
        df = pd.DataFrame({"": ["foo", "bar"], "BTC": [0.01, 0.02]})
        out = _promote_datetime_column(df)
        assert list(out.columns) == ["", "BTC"]


class TestLoaders:
    def test_corrupt_pickle_raises(self, tmp_path):
        # data_loader.py:363-364 unpickle error -> BABDataError
        p = tmp_path / "bad.pkl"
        p.write_bytes(b"not a pickle")
        with pytest.raises(BABDataError):
            load_returns_from_pickle(p)

    def test_csv_directory_raises(self, tmp_path):
        # data_loader.py:282-283 read_csv OSError/ParserError -> BABDataError
        d = tmp_path / "adir"
        d.mkdir()
        with pytest.raises(BABDataError):
            load_returns_from_csv(d)
