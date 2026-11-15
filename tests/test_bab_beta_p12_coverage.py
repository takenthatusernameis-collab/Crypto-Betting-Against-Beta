"""P12 coverage campaign for beta.py rolling fast paths (beta.py).

Covers real missed branches with synthetic data + fakes/mocks only (no network):
1D/2D _rolling_sum_finite, _rolling_sum_finite_stack, _rolling_sum finite/NaN
paths, plus calculate_beta / calculate_beta_fast degenerate and error paths and
calculate_rolling_beta validation / fallback paths.

Proves semantic equivalence to a pandas rolling-OLS reference on finite/NaN /
window / min-period inputs. No production logic is modified.
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import (
    _calc_rolling_beta_series,
    _rolling_sum,
    _rolling_sum_finite,
    _rolling_sum_finite_stack,
    calculate_beta,
    calculate_beta_fast,
    calculate_rolling_beta,
)
from strategies.betting_against_beta.errors import BABDataError


def _pandas_rolling_beta(asset, bench, window, min_obs):
    """Reference: pandas OLS slope per window, NaN-safe like the implementation."""
    df = pd.concat([bench, asset], axis=1)
    df.columns = ["b", "a"]
    out = []
    for i in range(len(df)):
        start = max(0, i - window + 1)
        win = df.iloc[start : i + 1]
        valid = win.dropna()
        if len(valid) < min_obs:
            out.append(np.nan)
            continue
        b = valid["b"].to_numpy(dtype=float)
        a = valid["a"].to_numpy(dtype=float)
        if b.std() < 1e-12:
            out.append(np.nan)
            continue
        X = np.column_stack([np.ones(len(b)), b])
        coef, _, _, _ = np.linalg.lstsq(X, a, rcond=None)
        out.append(coef[1])
    return np.array(out, dtype=float)


# ---------------------------------------------------------------------------
# calculate_beta
# ---------------------------------------------------------------------------

def test_calculate_beta_empty_returns_nan():
    assert np.isnan(calculate_beta(np.array([]), np.array([])))


def test_calculate_beta_mismatched_lengths_aligns():
    a = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    b = np.array([0.005, 0.01, 0.015])  # shorter
    beta = calculate_beta(a, b)
    assert np.isfinite(beta)


def test_calculate_beta_all_nonfinite_returns_nan():
    assert np.isnan(calculate_beta(np.array([np.nan, np.inf]), np.array([0.01, 0.02])))


def test_calculate_beta_min_obs_gate_returns_nan():
    a = np.array([0.01, 0.02])
    b = np.array([0.005, 0.01])
    assert np.isnan(calculate_beta(a, b, min_obs=5))


def test_calculate_beta_constant_benchmark_returns_nan():
    a = np.array([0.01, 0.02, 0.03])
    b = np.array([0.01, 0.01, 0.01])
    assert np.isnan(calculate_beta(a, b))


def test_calculate_beta_none_raises():
    with pytest.raises(BABDataError):
        calculate_beta(None, np.array([0.01, 0.02]))


# ---------------------------------------------------------------------------
# calculate_beta_fast
# ---------------------------------------------------------------------------

def test_calculate_beta_fast_empty_returns_nan():
    assert np.isnan(calculate_beta_fast(np.array([]), np.array([])))


def test_calculate_beta_fast_non_1d_returns_nan():
    assert np.isnan(calculate_beta_fast(np.array([[0.01, 0.02]]), np.array([0.01, 0.02])))


def test_calculate_beta_fast_mismatched_lengths_truncates():
    a = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    b = np.array([0.005, 0.01, 0.015])
    beta = calculate_beta_fast(a, b)
    assert np.isfinite(beta)


def test_calculate_beta_fast_all_nonfinite_returns_nan():
    assert np.isnan(calculate_beta_fast(np.array([np.nan, np.inf]), np.array([0.01, 0.02])))


def test_calculate_beta_fast_min_obs_gate_returns_nan():
    assert np.isnan(calculate_beta_fast(np.array([0.01, 0.02]), np.array([0.005, 0.01]), min_obs=5))


def test_calculate_beta_fast_constant_benchmark_returns_nan():
    assert np.isnan(calculate_beta_fast(np.array([0.01, 0.02, 0.03]), np.array([0.01, 0.01, 0.01])))


# ---------------------------------------------------------------------------
# _rolling_sum (1-D and 2-D, finite and NaN)
# ---------------------------------------------------------------------------

def test_rolling_sum_1d_finite_matches_pandas():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sums, counts = _rolling_sum(arr, window=3, min_periods=2)
    expected = pd.Series(arr).rolling(3, min_periods=2).sum().to_numpy(dtype=float)
    np.testing.assert_allclose(sums, expected)
    np.testing.assert_array_equal(counts, np.minimum(np.arange(len(arr)) + 1, 3))


def test_rolling_sum_1d_nan_not_poisoned():
    arr = np.array([1.0, np.nan, 3.0, 4.0, 5.0])
    sums, counts = _rolling_sum(arr, window=3, min_periods=1)
    expected = pd.Series(arr).rolling(3, min_periods=1).sum().to_numpy(dtype=float)
    np.testing.assert_allclose(sums, expected, equal_nan=True)


def test_rolling_sum_1d_min_periods_gate():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sums, _ = _rolling_sum(arr, window=3, min_periods=5)
    assert np.all(np.isnan(sums))


def test_rolling_sum_2d_finite_matches_pandas():
    arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], dtype=float)
    sums, counts = _rolling_sum(arr, window=2, min_periods=1)
    for j in range(2):
        expected = pd.Series(arr[:, j]).rolling(2, min_periods=1).sum().to_numpy(dtype=float)
        np.testing.assert_allclose(sums[:, j], expected)


def test_rolling_sum_2d_nan_not_poisoned():
    arr = np.array([[1.0, np.nan], [3.0, 4.0], [np.nan, 6.0], [7.0, 8.0]], dtype=float)
    sums, _ = _rolling_sum(arr, window=2, min_periods=1)
    for j in range(2):
        expected = pd.Series(arr[:, j]).rolling(2, min_periods=1).sum().to_numpy(dtype=float)
        np.testing.assert_allclose(sums[:, j], expected, equal_nan=True)


# ---------------------------------------------------------------------------
# _rolling_sum_finite (all-finite fast path, 1-D and 2-D)
# ---------------------------------------------------------------------------

def test_rolling_sum_finite_1d_matches_pandas():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sums, counts = _rolling_sum_finite(arr, window=3, min_periods=2)
    expected = pd.Series(arr).rolling(3, min_periods=2).sum().to_numpy(dtype=float)
    np.testing.assert_allclose(sums, expected)


def test_rolling_sum_finite_2d_matches_pandas():
    arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], dtype=float)
    sums, counts = _rolling_sum_finite(arr, window=2, min_periods=1)
    for j in range(2):
        expected = pd.Series(arr[:, j]).rolling(2, min_periods=1).sum().to_numpy(dtype=float)
        np.testing.assert_allclose(sums[:, j], expected)
    assert counts.shape == (len(arr),)


def test_rolling_sum_finite_min_periods_gate_2d():
    arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=float)
    sums, _ = _rolling_sum_finite(arr, window=3, min_periods=5)
    assert np.all(np.isnan(sums))


# ---------------------------------------------------------------------------
# _rolling_sum_finite_stack (stacked single-pass, 1-D delegates, 2-D)
# ---------------------------------------------------------------------------

def test_rolling_sum_finite_stack_1d_delegates():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sums, counts = _rolling_sum_finite_stack(arr, window=3, min_periods=2)
    expected = pd.Series(arr).rolling(3, min_periods=2).sum().to_numpy(dtype=float)
    np.testing.assert_allclose(sums, expected)


def test_rolling_sum_finite_stack_2d_matches_pandas():
    arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], dtype=float)
    sums, counts = _rolling_sum_finite_stack(arr, window=2, min_periods=1)
    for j in range(2):
        expected = pd.Series(arr[:, j]).rolling(2, min_periods=1).sum().to_numpy(dtype=float)
        np.testing.assert_allclose(sums[:, j], expected)
    assert counts.shape == (len(arr),)


# ---------------------------------------------------------------------------
# _calc_rolling_beta_series (per-series fallback used by bad_cols / except path)
# ---------------------------------------------------------------------------

def test_calc_rolling_beta_series_matches_reference_finite():
    rng = np.random.default_rng(0)
    bench = rng.normal(0, 0.01, 120)
    asset = 0.7 * bench + rng.normal(0, 0.005, 120)
    got = _calc_rolling_beta_series(bench, asset, window=30, min_obs=10)
    ref = _pandas_rolling_beta(pd.Series(asset), pd.Series(bench), 30, 10)
    np.testing.assert_allclose(got, ref, equal_nan=True, rtol=1e-6, atol=1e-6)


def test_calc_rolling_beta_series_nan_window_equivalence():
    rng = np.random.default_rng(1)
    bench = rng.normal(0, 0.01, 80)
    asset = 0.6 * bench + rng.normal(0, 0.004, 80)
    bench[15:18] = np.nan
    asset[40:43] = np.nan
    got = _calc_rolling_beta_series(bench, asset, window=20, min_obs=8)
    ref = _pandas_rolling_beta(pd.Series(asset), pd.Series(bench), 20, 8)
    np.testing.assert_allclose(got, ref, equal_nan=True, rtol=1e-6, atol=1e-6)


# ---------------------------------------------------------------------------
# calculate_rolling_beta validation branches
# ---------------------------------------------------------------------------

def test_calculate_rolling_beta_none_raises():
    with pytest.raises(BABDataError, match="returns_df is None"):
        calculate_rolling_beta(None, "BTC")


def test_calculate_rolling_beta_non_dataframe_raises():
    with pytest.raises(BABDataError, match="Expected DataFrame"):
        calculate_rolling_beta([1, 2, 3], "BTC")


def test_calculate_rolling_beta_missing_benchmark_raises():
    df = pd.DataFrame({"ETH": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
    with pytest.raises(BABDataError, match="Benchmark .* not found"):
        calculate_rolling_beta(df, "BTC")


def test_calculate_rolling_beta_benchmark_no_finite_raises():
    df = pd.DataFrame(
        {"BTC": [np.nan, np.inf], "ETH": [0.01, 0.02]},
        index=pd.date_range("2023-01-01", periods=2),
    )
    with pytest.raises(BABDataError, match="no finite return values"):
        calculate_rolling_beta(df, "BTC")


def test_calculate_rolling_beta_benchmark_is_one_and_finite_output():
    rng = np.random.default_rng(2)
    df = pd.DataFrame(
        {
            "BTC": rng.normal(0, 0.01, 100),
            "ETH": 0.5 * rng.normal(0, 0.01, 100) + rng.normal(0, 0.005, 100),
        },
        index=pd.date_range("2023-01-01", periods=100, freq="D"),
    )
    betas = calculate_rolling_beta(df, "BTC", window=20, min_obs=10)
    assert "BTC" in betas.columns
    assert (betas["BTC"] == 1.0).all()
    assert "ETH" in betas.columns
    assert betas["ETH"].notna().any()


def test_calculate_rolling_beta_bad_cols_fallback_path():
    # A coercible-but-not-finite asset column routes to the per-series
    # _calc_rolling_beta_series path (bad_cols branch).
    idx = pd.date_range("2023-01-01", periods=60, freq="D")
    rng = np.random.default_rng(3)
    df = pd.DataFrame(
        {
            "BTC": rng.normal(0, 0.01, 60),
            "ETH": 0.5 * rng.normal(0, 0.01, 60) + rng.normal(0, 0.005, 60),
            "WEIRD": np.full(60, np.nan),
        },
        index=idx,
    )
    betas = calculate_rolling_beta(df, "BTC", window=20, min_obs=10)
    assert "WEIRD" in betas.columns
    assert betas["WEIRD"].isna().all()


def test_calculate_rolling_beta_babdataerror_reraised():
    # BABDataError raised inside the bad_cols path propagates unchanged.
    idx = pd.date_range("2023-01-01", periods=60, freq="D")
    rng = np.random.default_rng(4)
    df = pd.DataFrame(
        {
            "BTC": rng.normal(0, 0.01, 60),
            "ETH": 0.5 * rng.normal(0, 0.01, 60) + rng.normal(0, 0.005, 60),
            "WEIRD": np.full(60, np.nan),
        },
        index=idx,
    )
    with mock.patch(
        "strategies.betting_against_beta.beta._calc_rolling_beta_series",
        side_effect=BABDataError("series boom"),
    ):
        with pytest.raises(BABDataError, match="series boom"):
            calculate_rolling_beta(df, "BTC", window=20, min_obs=10)
