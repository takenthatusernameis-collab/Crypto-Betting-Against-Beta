"""P35 WP0 — Beta-estimator library, single-asset correctness.

Covers estimate_rolling_ols_beta, estimate_ewma_beta, estimate_shrinkage_beta:
OLS parity vs calculate_rolling_beta, EWMA/shrinkage vs independent hand-computed
small cases, no-lookahead, NaN before min_obs, determinism, degenerate/empty input.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.beta_estimators import (
    estimate_ewma_beta,
    estimate_rolling_ols_beta,
    estimate_shrinkage_beta,
)

BENCH = "BTC"
ASSETS = ["ETH", "SOL", "BNB"]


def _make_returns(n_days=200, seed=7, n_assets=len(ASSETS)):
    rng = np.random.default_rng(seed)
    bench = rng.normal(0.0005, 0.02, size=n_days)
    data = {BENCH: bench}
    for j, a in enumerate(ASSETS[:n_assets]):
        beta_true = 0.5 + 0.5 * j / max(1, n_assets - 1)
        data[a] = beta_true * bench + rng.normal(0.0, 0.01, size=n_days)
    idx = pd.date_range("2023-01-02", periods=n_days, freq="D")
    return pd.DataFrame(data, index=idx)


def _ewm_mean_oracle(x, halflife, min_obs):
    """Independent adjust=False EWMA mean (recursion), NaN before min_obs."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    out = np.full(n, np.nan)
    if n == 0:
        return out
    decay = 0.5 ** (1.0 / float(halflife))
    alpha = 1.0 - decay
    out[0] = x[0]
    for t in range(1, n):
        out[t] = alpha * x[t] + (1.0 - alpha) * out[t - 1]
    if min_obs is not None:
        out[: min_obs - 1] = np.nan
    return out


def _ewma_beta_oracle(a, b, halflife, min_obs):
    """Independent EWMA beta = (E[ab] - E[a]E[b]) / (E[b^2] - E[b]^2)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n = len(a)
    out = np.full(n, np.nan)
    if n == 0:
        return out
    ea = _ewm_mean_oracle(a, halflife, min_obs)
    eb = _ewm_mean_oracle(b, halflife, min_obs)
    eab = _ewm_mean_oracle(a * b, halflife, min_obs)
    eb2 = _ewm_mean_oracle(b * b, halflife, min_obs)
    cov = eab - ea * eb
    var = eb2 - eb * eb
    beta = np.where(var > 1e-18, cov / var, np.nan)
    count = np.cumsum((~np.isnan(a)) & (~np.isnan(b)))
    beta = np.where(count >= min_obs, beta, np.nan)
    return beta


class TestRollingOlssParity:
    def test_parity_with_calculate_rolling_beta(self):
        df = _make_returns()
        a = estimate_rolling_ols_beta(df, BENCH, window=90, min_obs=60)
        b = calculate_rolling_beta(df, BENCH, window=90, min_obs=60)
        pd.testing.assert_frame_equal(a, b)
        assert (a[BENCH] == 1.0).all()
        assert list(a.columns) == list(df.columns)
        assert a.index.equals(df.index)

    def test_parity_different_windows(self):
        df = _make_returns()
        for window, min_obs in ((60, 60), (90, 60), (120, 90)):
            a = estimate_rolling_ols_beta(df, BENCH, window=window, min_obs=min_obs)
            b = calculate_rolling_beta(df, BENCH, window=window, min_obs=min_obs)
            np.testing.assert_array_equal(a.values, b.values)


class TestEwmaBeta:
    def test_matches_independent_oracle(self):
        df = _make_returns(n_days=120, seed=11)
        for halflife, min_obs in ((20, 30), (40, 60), (60, 30)):
            res = estimate_ewma_beta(df, BENCH, halflife=halflife, min_obs=min_obs)
            for c in ASSETS:
                expected = _ewma_beta_oracle(
                    df[c].to_numpy(dtype=float),
                    df[BENCH].to_numpy(dtype=float),
                    halflife,
                    min_obs,
                )
                np.testing.assert_allclose(
                    res[c].to_numpy(dtype=float), expected, rtol=1e-9, atol=1e-12
                )

    def test_nan_before_min_obs(self):
        df = _make_returns(n_days=100, seed=3)
        res = estimate_ewma_beta(df, BENCH, halflife=40, min_obs=60)
        for c in ASSETS:
            assert res[c].iloc[:59].isna().all()
            assert res[c].iloc[60:].notna().any()

    def test_no_lookahead(self):
        df = _make_returns(n_days=150, seed=5)
        base = df.iloc[:100]
        base_res = estimate_ewma_beta(base, BENCH, halflife=40, min_obs=40)
        full_res = estimate_ewma_beta(df, BENCH, halflife=40, min_obs=40)
        for c in ASSETS:
            np.testing.assert_array_equal(
                base_res[c].to_numpy(dtype=float),
                full_res[c].to_numpy(dtype=float)[: len(base)],
            )

    def test_deterministic(self):
        df = _make_returns(n_days=100, seed=9)
        a = estimate_ewma_beta(df, BENCH, halflife=40, min_obs=40)
        b = estimate_ewma_beta(df, BENCH, halflife=40, min_obs=40)
        pd.testing.assert_frame_equal(a, b)

    def test_benchmark_column_is_one(self):
        df = _make_returns(n_days=80, seed=2)
        res = estimate_ewma_beta(df, BENCH, halflife=40, min_obs=30)
        assert (res[BENCH] == 1.0).all()
        assert list(res.columns) == list(df.columns)

    def test_invalid_halflife(self):
        df = _make_returns(n_days=50, seed=1)
        with pytest.raises(ValueError):
            estimate_ewma_beta(df, BENCH, halflife=0, min_obs=10)
        with pytest.raises(ValueError):
            estimate_ewma_beta(df, BENCH, halflife=-5, min_obs=10)

    def test_empty_input(self):
        df = pd.DataFrame(
            {BENCH: pd.Series(dtype=float), "ETH": pd.Series(dtype=float)}
        )
        res = estimate_ewma_beta(df, BENCH, halflife=40, min_obs=5)
        assert res.empty
        assert (res[BENCH] == 1.0).all()


class TestShrinkageBeta:
    def test_intensity_zero_equals_ols_exactly(self):
        df = _make_returns(n_days=150, seed=13)
        ols = estimate_rolling_ols_beta(df, BENCH, window=90, min_obs=60)
        shrunk = estimate_shrinkage_beta(
            df, BENCH, window=90, shrink_target=1.0, shrink_intensity=0.0, min_obs=60
        )
        pd.testing.assert_frame_equal(shrunk, ols)

    def test_intensity_one_equals_target(self):
        df = _make_returns(n_days=150, seed=13)
        shrunk = estimate_shrinkage_beta(
            df,
            BENCH,
            window=90,
            shrink_target=1.0,
            shrink_intensity=1.0,
            min_obs=60,
        )
        ols = estimate_rolling_ols_beta(df, BENCH, window=90, min_obs=60)
        for c in ASSETS:
            expected = np.where(np.isfinite(ols[c]), 1.0, np.nan)
            np.testing.assert_allclose(shrunk[c].to_numpy(dtype=float), expected)

    def test_intensity_intermediate_is_convex_combo(self):
        df = _make_returns(n_days=150, seed=13)
        ols = estimate_rolling_ols_beta(df, BENCH, window=90, min_obs=60)
        intensity = 0.3
        shrunk = estimate_shrinkage_beta(
            df,
            BENCH,
            window=90,
            shrink_target=1.0,
            shrink_intensity=intensity,
            min_obs=60,
        )
        for c in ASSETS:
            expected = (1.0 - intensity) * ols[c] + intensity * 1.0
            np.testing.assert_allclose(
                shrunk[c].to_numpy(dtype=float),
                expected.to_numpy(dtype=float),
                rtol=1e-9,
                atol=1e-12,
            )

    def test_cross_sectional_mean_target(self):
        df = _make_returns(n_days=150, seed=17)
        ols = estimate_rolling_ols_beta(df, BENCH, window=90, min_obs=60)
        shrunk = estimate_shrinkage_beta(
            df,
            BENCH,
            window=90,
            shrink_target="cross_sectional_mean",
            shrink_intensity=0.5,
            min_obs=60,
        )
        target = ols[ASSETS].mean(axis=1)
        intensity = 0.5
        for c in ASSETS:
            expected = (1.0 - intensity) * ols[c] + intensity * target
            np.testing.assert_allclose(
                shrunk[c].to_numpy(dtype=float),
                expected.to_numpy(dtype=float),
                rtol=1e-9,
                atol=1e-12,
            )

    def test_invalid_intensity(self):
        df = _make_returns(n_days=50, seed=1)
        with pytest.raises(ValueError):
            estimate_shrinkage_beta(df, BENCH, shrink_intensity=-0.1, min_obs=10)
        with pytest.raises(ValueError):
            estimate_shrinkage_beta(df, BENCH, shrink_intensity=1.5, min_obs=10)

    def test_nan_before_min_obs(self):
        df = _make_returns(n_days=100, seed=3)
        res = estimate_shrinkage_beta(df, BENCH, min_obs=60, shrink_intensity=0.3)
        for c in ASSETS:
            assert res[c].iloc[:59].isna().all()

    def test_constant_benchmark_yields_nan(self):
        n_days = 100
        df = pd.DataFrame(
            {BENCH: np.ones(n_days), "ETH": np.random.default_rng(1).normal(0, 0.01, n_days)},
            index=pd.date_range("2023-01-02", periods=n_days, freq="D"),
        )
        res = estimate_shrinkage_beta(df, BENCH, window=60, min_obs=30, shrink_intensity=0.3)
        assert res["ETH"].iloc[60:].isna().all()

    def test_empty_input(self):
        df = pd.DataFrame(
            {BENCH: pd.Series(dtype=float), "ETH": pd.Series(dtype=float)}
        )
        res = estimate_shrinkage_beta(df, BENCH, min_obs=5, shrink_intensity=0.3)
        assert res.empty
        assert (res[BENCH] == 1.0).all()
