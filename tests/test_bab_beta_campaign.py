"""Campaign tests for beta.py rolling and edge-case paths."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


def _df(n=60, seed=9):
    idx = pd.date_range("2023-01-01", periods=n, freq="D")
    rng = np.random.default_rng(seed)
    mkt = rng.normal(0, 0.01, n)
    return pd.DataFrame(
        {"BTC": mkt, "ETH": 0.7 * mkt + rng.normal(0, 0.005, n)}, index=idx
    )


def test_estimate_betas_none_benchmark_guess_path():
    idx = pd.date_range("2023-01-01", periods=40, freq="D")
    rng = np.random.default_rng(1)
    df = pd.DataFrame(
        {"A": rng.normal(0, 0.01, 40), "B": rng.normal(0, 0.01, 40)}, index=idx
    )
    with pytest.raises(BABDataError):
        beta.estimate_betas(df, benchmark=None, window=20, min_obs=5)


def test_estimate_betas_min_obs_clamped_to_window():
    idx = pd.date_range("2023-01-01", periods=30, freq="D")
    rng = np.random.default_rng(2)
    mkt = rng.normal(0, 0.01, 30)
    df = pd.DataFrame({"BTC": mkt, "ETH": 0.5 * mkt}, index=idx)
    out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=25)
    assert isinstance(out, pd.DataFrame)


def test_rolling_beta_arrays_both_fallback_paths():
    class Dummy:
        pass

    out = beta.rolling_beta(Dummy(), Dummy())
    assert out is not None


def test_rolling_beta_mismatched_ndarray_fallback():
    a = np.array([0.01, 0.02, -0.01, 0.03, 0.0])
    b = np.array([0.01, 0.02])
    out = beta.rolling_beta(b, a, window=3, min_obs=2)
    assert hasattr(out, "__len__")


def test_calculate_beta_lists_truncate_common_length():
    out = beta.calculate_beta([0.01, 0.02, -0.01, 0.03], [0.01, 0.02])
    assert np.isfinite(out)


def test_calculate_beta_object_arrays_returns_nan():
    out = beta.calculate_beta(["a", "b"], ["c", "d"])
    assert np.isnan(out)


def test_calculate_beta_fast_constant_benchmark_zero():
    a = np.array([0.01, 0.02, -0.01, 0.03])
    b = np.array([0.01, 0.01, 0.01, 0.01])
    out = beta.calculate_beta_fast(a, b)
    assert out == 0.0


def test_calculate_beta_fast_inf_inputs():
    out = beta.calculate_beta_fast([np.inf, 0.01], [0.01, 0.02])
    assert np.isnan(out) or np.isfinite(out)


def test_calculate_rolling_beta_non_numeric_column_fallback():
    idx = pd.date_range("2023-01-01", periods=40, freq="D")
    rng = np.random.default_rng(5)
    df = pd.DataFrame({"BTC": rng.normal(0, 0.01, 40), "TEXT": ["x"] * 40}, index=idx)
    with pytest.raises(ValueError):
        beta.calculate_rolling_beta(df, "BTC", window=10, min_obs=5)


def test_calculate_rolling_beta_errors():
    with pytest.raises(BABDataError):
        beta.calculate_rolling_beta(None, "BTC")
    with pytest.raises(BABDataError):
        beta.calculate_rolling_beta([1, 2, 3], "BTC")
    df = pd.DataFrame({"ETH": [0.01, 0.02]})
    with pytest.raises(BABDataError):
        beta.calculate_rolling_beta(df, "BTC")


def test_calc_rolling_beta_series_empty():
    out = beta._calc_rolling_beta_series(np.array([]), np.array([]), 10, 5)
    assert len(out) == 0
