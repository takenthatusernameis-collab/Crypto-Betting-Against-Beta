"""Edge-branch coverage for metrics.py.

Cover the all-NaN drawdown guard, the NaN turnover mean guard, and the
non-empty win_rate return path.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import metrics


class TestMaxDrawdown:
    def test_all_nan_returns_returns_nan(self):
        # metrics.py:71 ``if pd.isna(max_dd): return np.nan``
        s = pd.Series([np.nan, np.nan, np.nan])
        assert np.isnan(metrics.max_drawdown(s))


class TestTurnover:
    def test_single_row_weights_mean_nan(self):
        # metrics.py:97 ``if pd.isna(turnover_mean): return 0.0``
        df = pd.DataFrame({"A": [0.5]})
        assert metrics.turnover(df) == 0.0


class TestWinRate:
    def test_non_empty_returns_mean(self):
        # metrics.py:174 ``return float((r > 0.0).mean())``
        assert metrics.win_rate(pd.Series([0.01, -0.02])) == 0.5
