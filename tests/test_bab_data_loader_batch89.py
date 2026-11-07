"""Batch 89: reachable exception handler in _coerce_numeric (1226-1227)."""
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl


class _AstypeFailCopyFailDF(pd.DataFrame):
    @property
    def _constructor(self):
        return _AstypeFailCopyFailDF

    def astype(self, *a, **k):
        raise ValueError("astype boom")

    def copy(self, deep=True):
        raise TypeError("copy boom")


def test_coerce_numeric_copy_exception_wrapped_1226_1227():
    df = _AstypeFailCopyFailDF({"A": [0.1, 0.2], "B": [0.3, 0.4]})
    with pytest.raises(dl.BABDataError, match="copy boom"):
        dl._coerce_numeric(df)
