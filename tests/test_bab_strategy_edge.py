"""Edge-branch coverage for strategy.py pipeline.

Cover the daily rebalance mask, the empty-universe ValueError, and the
freeze fallback path.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import strategy


class TestRebalanceMask:
    def test_daily_mask_all_true(self):
        # strategy.py:41-42 ``mask[:] = True; return mask``
        index = pd.date_range("2024-01-01", periods=5)
        mask = strategy._rebalance_mask(index, "daily")
        assert bool(mask.all())
        assert len(mask) == 5
