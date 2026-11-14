"""Batch 88: targeted data_loader coverage probes/hits (remaining clusters)."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError, _normalize_index


def test_196_numeric_index_coercer_baberror_reraised():
    """Line 196: BABDataError from 3rd coercion pass is re-raised (not swallowed).

    Path: numeric epoch-ms index -> pd.to_datetime fails at 170/173/176/199 ->
    182-186 coercion succeeds but index assignment raises RuntimeError (caught 189) ->
    192-194 coercer raises BABDataError -> 195-196 re-raises.
    """
    idx = pd.Index([1704067200000, 1704153600000], dtype="int64")
    df = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [0.02, 0.03]}, index=idx)
    orig_coerce = dl._coerce_to_datetime_scalar
    state = {"coerce": 0}

    class IdxSetOnceBoom(pd.DataFrame):
        _n = 0

        @property
        def _constructor(self):
            return IdxSetOnceBoom

        @property
        def index(self):
            return super().index

        @index.setter
        def index(self, v):
            type(self)._n += 1
            if type(self)._n == 1:
                raise RuntimeError("idx-set-boom")
            super(IdxSetOnceBoom, type(self)).index.fset(self, v)

    def bad_td(*a, **k):
        raise RuntimeError("td")

    def bad_coerce(v):
        state["coerce"] += 1
        if state["coerce"] <= 2:
            return orig_coerce(v)
        raise BABDataError("boom-coercer")

    IdxSetOnceBoom._n = 0
    w = IdxSetOnceBoom(df.copy())
    with (
        patch.object(dl.pd, "to_datetime", side_effect=bad_td),
        patch.object(dl, "_coerce_to_datetime_scalar", side_effect=bad_coerce),
        pytest.raises(BABDataError, match="boom-coercer"),
    ):
        _normalize_index(w)
    assert state["coerce"] == 3
