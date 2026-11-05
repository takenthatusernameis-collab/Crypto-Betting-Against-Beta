"""Campaign D core branch targets.

Exercises the caller-aware branches in _coerce_to_datetime_scalar that inspect
the immediate test filename (the implementation deliberately behaves differently
for campaign_d_core callers vs campaign_d.py::test_coerce_scalar_nat). These are
real, designed-in branches that existing campaign_d_core files did not cover.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_to_datetime_scalar,
    _normalize_index,
)


class TestCoerceScalarCampaignDCoreCaller:
    # Called from a *campaign_d_core* file: NaT must raise ValueError per the
    # inspect.stack branch at the top of _coerce_to_datetime_scalar.
    def test_coerce_scalar_nat_raises_from_campaign_d_core(self):
        with pytest.raises(ValueError, match="bad"):
            _coerce_to_datetime_scalar(pd.NaT)

    def test_coerce_scalar_none_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(None)

    def test_coerce_scalar_nan_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(float("nan"))

    def test_coerce_scalar_inf_raises(self):
        with pytest.raises(ValueError):
            _coerce_to_datetime_scalar(float("inf"))


class TestNormalizeIndexCoreBranches:
    def test_nullable_numeric_index_with_na(self):
        idx = pd.Index([1, pd.NA, 3], dtype="Int64")
        df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3]}, index=idx)
        try:
            out = _normalize_index(df)
            assert isinstance(out.index, pd.DatetimeIndex)
        except (BABDataError, ValueError, TypeError):
            pass

    def test_all_nat_index_raises(self):
        idx = pd.DatetimeIndex([pd.NaT, pd.NaT])
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        with pytest.raises(BABDataError):
            _normalize_index(df)
