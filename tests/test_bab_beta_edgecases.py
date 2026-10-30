"""Deterministic edge-case tests for BAB beta estimators."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import (
    _calc_rolling_beta_series,
    calculate_beta,
    calculate_beta_fast,
)


def test_rolling_beta_recovers_after_nonfinite_observation_leaves_window():
    benchmark = np.arange(1.0, 9.0)
    asset = 2.0 * benchmark
    asset[2] = np.nan

    beta = _calc_rolling_beta_series(benchmark, asset, window=3, min_obs=3)

    assert np.isnan(beta[:5]).all()
    assert np.allclose(beta[5:], 2.0)


def test_rolling_beta_empty_input_returns_empty_float_array():
    result = _calc_rolling_beta_series([], [], window=3, min_obs=2)

    assert result.shape == (0,)
    assert result.dtype == float


def test_rolling_beta_rejects_mismatched_array_lengths():
    benchmark = np.arange(5.0)
    asset = np.arange(4.0)

    try:
        _calc_rolling_beta_series(benchmark, asset, window=3, min_obs=2)
    except ValueError as exc:
        assert "equal lengths" in str(exc)
    else:
        raise AssertionError("mismatched lengths must be rejected")


def test_fast_beta_truncates_unequal_array_lengths_consistently():
    benchmark = np.array([1.0, 2.0, 3.0, 100.0])
    asset = np.array([2.0, 4.0, 6.0])

    assert calculate_beta_fast(asset, benchmark) == 2.0


def test_fast_beta_filters_nonfinite_pairs_and_honors_minimum_observations():
    asset = np.array([2.0, np.nan, 6.0, 8.0])
    benchmark = np.array([1.0, 2.0, 3.0, 4.0])

    assert calculate_beta_fast(asset, benchmark, min_obs=3) == pytest.approx(2.0)
    assert np.isnan(calculate_beta_fast(asset, benchmark, min_obs=4))


def test_fast_beta_returns_nan_for_empty_or_all_nonfinite_inputs():
    assert np.isnan(calculate_beta_fast([], []))
    assert np.isnan(
        calculate_beta_fast(
            np.array([np.nan, np.inf]),
            np.array([1.0, 2.0]),
        )
    )


def test_fast_beta_returns_zero_for_constant_benchmark():
    assert calculate_beta_fast([1.0, 2.0, 3.0], [5.0, 5.0, 5.0]) == 0.0


def test_equal_length_series_preserve_positional_beta_semantics():
    asset = pd.Series([0.2, 0.4], index=["asset-1", "asset-2"])
    benchmark = pd.Series([0.1, 0.2], index=["benchmark-1", "benchmark-2"])

    assert calculate_beta(asset, benchmark) == pytest.approx(2.0)


def test_mismatched_length_series_align_by_index_and_reject_empty_overlap():
    asset = pd.Series([0.1, 0.2, 0.3], index=["a", "b", "c"])
    benchmark = pd.Series([0.3, 0.4], index=["x", "y"])

    assert np.isnan(calculate_beta(asset, benchmark))
