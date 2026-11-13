"""Regression tests for the vectorized stale-run detector.

The per-column stale-data check in ``_run_data_quality_campaign`` used to be a
Python loop over every row. It was replaced with ``_max_consecutive_equal_finite``
(a numpy vectorized implementation) as part of the Step 3 performance campaign.
These tests prove the replacement produces identical results to the original
loop semantics, including NaN handling, and that the campaign still rejects
frozen columns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import _run_data_quality_campaign
from strategies.betting_against_beta.data_loader import _max_consecutive_equal_finite


def _max_consecutive_equal_finite_reference(arr):
    """Original per-element loop semantics, kept as an oracle."""
    arr = np.asarray(arr, dtype=float)
    max_run = 0
    run = 0
    prev = None
    for v in arr:
        if np.isfinite(v) and prev is not None and v == prev:
            run += 1
        else:
            run = 1
        if np.isfinite(v):
            max_run = max(max_run, run)
        prev = v
    return max_run


class TestMaxConsecutiveEqualFinite:
    @pytest.mark.parametrize(
        "arr",
        [
            [1.0, 1.0, 1.0, 2.0, 2.0, 3.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 2.0, 3.0, 4.0, 5.0],
            [0.0, 0.0, 0.0],
            [np.nan, np.nan, np.nan],
            [np.nan, 1.0, 1.0, np.nan, 1.0, 1.0, 1.0],
            [1.0, np.nan, 1.0, 1.0, np.nan, 1.0, 1.0, 1.0],
            [],
            [1.0],
            [np.nan],
            [1.0, 1.0, np.inf, 1.0, 1.0, 1.0],
            [-0.0, -0.0, 1.0],
            [1e-300, 1e-300, 1e-300, 2e-300],
        ],
    )
    def test_matches_reference_loop(self, arr):
        assert _max_consecutive_equal_finite(arr) == _max_consecutive_equal_finite_reference(arr)

    def test_empty_returns_zero(self):
        assert _max_consecutive_equal_finite([]) == 0

    def test_all_non_finite_returns_zero(self):
        assert _max_consecutive_equal_finite([np.nan, np.nan]) == 0

    def test_single_finite_returns_one(self):
        assert _max_consecutive_equal_finite([0.5]) == 1


class TestStaleRunCampaignRejection:
    def test_frozen_column_rejected(self):
        df = pd.DataFrame(
            {
                "BTC": np.linspace(0.01, 0.02, 200),
                "ETH": np.full(200, 0.001),
            }
        )
        with pytest.raises(Exception):
            _run_data_quality_campaign(df, stale_run_threshold=50)

    def test_non_frozen_column_accepted(self):
        df = pd.DataFrame(
            {
                "BTC": np.linspace(0.01, 0.02, 200),
                "ETH": np.linspace(0.001, 0.002, 200),
            }
        )
        out = _run_data_quality_campaign(df, stale_run_threshold=50)
        assert "ETH" in out.columns

    def test_short_frozen_run_accepted(self):
        # A run of 49 equal values is below the threshold of 50.
        arr = np.full(200, 0.001)
        arr[0:49] = 0.001  # 49 consecutive equal at the start
        arr[49] = 0.002
        arr[50:] = np.linspace(0.002, 0.003, 150)
        df = pd.DataFrame({"BTC": np.linspace(0.01, 0.02, 200), "ETH": arr})
        out = _run_data_quality_campaign(df, stale_run_threshold=50)
        assert "ETH" in out.columns

    def test_nan_breaks_run(self):
        # NaN in the middle must not extend a stale run across it.
        arr = np.full(200, 0.001)
        arr[50] = np.nan
        arr[51:102] = 0.001  # 51 consecutive equal after the NaN
        df = pd.DataFrame({"BTC": np.linspace(0.01, 0.02, 200), "ETH": arr})
        with pytest.raises(Exception):
            _run_data_quality_campaign(df, stale_run_threshold=50)