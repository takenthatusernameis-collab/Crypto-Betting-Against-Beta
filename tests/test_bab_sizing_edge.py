"""Edge-branch coverage for sizing.py.

Cover the lookback validation error and the empty-signals early return.
"""

import pandas as pd
import pytest

from strategies.betting_against_beta import sizing
from strategies.betting_against_beta.portfolio import _clean_signal_value
from strategies.betting_against_beta.sizing import BABSizingError, VolatilityTargetSizer


class TestVolatilityTargetSizerValidation:
    def test_lookback_must_be_ge_1(self):
        # sizing.py:55 ``raise BABSizingError("lookback must be >= 1")``
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(target_vol=0.15, lookback=0)

    def test_annualize_must_be_ge_1(self):
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(target_vol=0.15, annualize=0)


class TestApplyPositionSizing:
    def test_empty_signals_returns_empty_frame(self):
        # sizing.py:96 ``return pd.DataFrame()``
        res = sizing.apply_position_sizing(pd.DataFrame())
        assert res.empty

    def test_none_signals_returns_empty_frame(self):
        res = sizing.apply_position_sizing(None)
        assert res.empty


class TestCleanSignalValue:
    def test_string_non_unit_signal(self):
        # portfolio.py:29 ``return 0`` for parsed int that is neither 1 nor -1
        assert _clean_signal_value("2") == 0

    def test_none_signal(self):
        assert _clean_signal_value(None) == 0

    def test_nan_signal(self):
        assert _clean_signal_value(float("nan")) == 0
