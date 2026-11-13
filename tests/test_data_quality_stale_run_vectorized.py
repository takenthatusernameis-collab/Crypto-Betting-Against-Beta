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
from strategies.betting_against_beta.data_loader import _max_consecutive_equal_finite_frame


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


def _max_consecutive_equal_finite_frame_reference(arr):
    """Per-column oracle: ``[_max_consecutive_equal_finite(arr[:, j]) ...]``."""
    arr = np.asarray(arr, dtype=float)
    if arr.ndim == 1:
        return np.array([_max_consecutive_equal_finite_reference(arr)], dtype=np.int64)
    if arr.ndim != 2:
        return np.zeros(0, dtype=np.int64)
    n, m = arr.shape
    return np.array(
        [_max_consecutive_equal_finite_reference(arr[:, j]) for j in range(m)],
        dtype=np.int64,
    )


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


class TestMaxConsecutiveEqualFiniteFrame:
    """Oracle-equivalence + perf-ceiling for the 2-D frame helper.

    The 2-D path was re-implemented from a ``cumsum`` + ``bincount`` group-size
    tally to a single ``maximum.accumulate`` run-length pass. These tests prove
    the new implementation is numerically identical to the per-column 1-D oracle
    (including NaN/inf/constant/degenerate inputs) and that it stays fast at
    production scale.
    """

    @pytest.mark.parametrize(
        "arr",
        [
            np.array([[1.0, 1.0], [1.0, 2.0], [2.0, 2.0], [3.0, 3.0]]),
            np.array([[1.0, 1.0, 1.0, 1.0, 1.0]]),
            np.array([[1.0], [2.0], [3.0], [4.0], [5.0]]),
            np.array([[0.0, 0.0, 0.0]]),
            np.array([[np.nan, np.nan, np.nan]]),
            np.array([[np.nan, 1.0, 1.0, np.nan, 1.0, 1.0, 1.0]]),
            np.array([[1.0, np.nan, 1.0, 1.0, np.nan, 1.0, 1.0, 1.0]]),
            np.array([[1.0, 1.0, np.inf, 1.0, 1.0, 1.0]]),
            np.array([[-0.0, -0.0, 1.0]]),
            np.array([[1e-300, 1e-300, 1e-300, 2e-300]]),
            np.array([[1.0, 2.0], [np.nan, np.nan]]),
            np.array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]),
            np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]),
            np.array([[1.0, 1.0, 2.0], [1.0, 2.0, 2.0], [2.0, 2.0, 2.0]]),
            np.array([[], []], dtype=float).reshape(0, 2),
        ],
    )
    def test_matches_per_column_oracle(self, arr):
        got = _max_consecutive_equal_finite_frame(arr)
        expected = _max_consecutive_equal_finite_frame_reference(arr)
        assert got.dtype == np.int64
        assert got.shape == expected.shape
        np.testing.assert_array_equal(got, expected)

    def test_all_nan_columns_return_zero(self):
        arr = np.array([[1.0, np.nan], [1.0, np.nan], [1.0, np.nan]])
        got = _max_consecutive_equal_finite_frame(arr)
        np.testing.assert_array_equal(got, np.array([3, 0]))

    def test_constant_column_returns_length(self):
        arr = np.full((100, 4), 0.5)
        got = _max_consecutive_equal_finite_frame(arr)
        np.testing.assert_array_equal(got, np.array([100, 100, 100, 100]))

    def test_stale_run_in_middle_column(self):
        rng = np.random.default_rng(0)
        arr = rng.normal(0, 0.02, (250, 5))
        arr[50:110, 2] = 0.7  # 60-length stale run in column 2
        got = _max_consecutive_equal_finite_frame(arr)
        assert int(got[2]) == 60

    def test_1d_input_routes_through_1d_helper(self):
        arr = np.array([1.0, 1.0, 1.0, 2.0, 2.0])
        got = _max_consecutive_equal_finite_frame(arr)
        np.testing.assert_array_equal(got, np.array([3]))

    def test_non_2d_returns_empty(self):
        arr = np.array([[[1.0]]])
        got = _max_consecutive_equal_finite_frame(arr)
        assert got.shape == (0,)

    def test_production_scale_perf_ceiling(self):
        """2500 x 61 frame must complete well under 10 ms (generous CI ceiling)."""
        import time

        rng = np.random.default_rng(1234)
        arr = rng.normal(0, 0.02, (2500, 61))
        # warmup (lazy numpy dispatch / allocation)
        _max_consecutive_equal_finite_frame(arr)
        start = time.perf_counter()
        _max_consecutive_equal_finite_frame(arr)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.01, (
            f"_max_consecutive_equal_finite_frame took {elapsed:.4f}s on "
            "2500x61; stale-scan perf regression"
        )