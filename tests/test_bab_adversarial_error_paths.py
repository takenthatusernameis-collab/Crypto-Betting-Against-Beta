"""Regression tests for the hardened error paths in BABStrategy.run().

The bare ``except Exception: pass`` blocks in strategy.py were replaced with
narrow ``except (TypeError, ValueError, AttributeError)`` handlers that raise
``BABDataError``.  These tests ensure misconfigured optional features surface
as BAB-specific errors instead of being silently swallowed, and that the
benchmark column always carries a beta of exactly 1.0 (the invariant that was
previously violated by the fast path).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABConfig, BABStrategy
from strategies.betting_against_beta.errors import BABDataError


def _make_returns(n_days: int, n_assets: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n_days, freq="D")
    bench = rng.normal(0.0005, 0.02, n_days)
    data = {"BTC": bench}
    for i in range(n_assets - 1):
        data[f"ASSET_{i:03d}"] = rng.normal(0.0004, 0.025, n_days)
    return pd.DataFrame(data, index=idx)


class TestBenchmarkBetaInvariant:
    """The benchmark column must always carry a beta of exactly 1.0."""

    def test_benchmark_beta_is_one_fast_path(self):
        df = _make_returns(300, 10, 7)
        cfg = BABConfig(benchmark="BTC", beta_window=90, min_observations=60)
        res = BABStrategy(cfg).run(returns_df=df)
        bench_beta = res.betas["BTC"].to_numpy(dtype=float)
        valid = bench_beta[np.isfinite(bench_beta)]
        assert len(valid) > 0
        assert np.allclose(valid, 1.0)

    def test_benchmark_beta_is_one_with_nans(self):
        df = _make_returns(300, 10, 7).copy()
        df.iloc[50, 0] = np.nan  # benchmark NaN mid-series
        df.iloc[150, 2] = np.nan
        cfg = BABConfig(benchmark="BTC", beta_window=90, min_observations=60)
        res = BABStrategy(cfg).run(returns_df=df)
        bench_beta = res.betas["BTC"].to_numpy(dtype=float)
        valid = bench_beta[np.isfinite(bench_beta)]
        assert len(valid) > 0
        assert np.allclose(valid, 1.0)

    def test_benchmark_beta_is_one_short_window(self):
        df = _make_returns(120, 5, 11)
        cfg = BABConfig(benchmark="BTC", beta_window=30, min_observations=20)
        res = BABStrategy(cfg).run(returns_df=df)
        bench_beta = res.betas["BTC"].to_numpy(dtype=float)
        valid = bench_beta[np.isfinite(bench_beta)]
        assert len(valid) > 0
        assert np.allclose(valid, 1.0)


class TestHardenedErrorPaths:
    """Misconfigured optional features must raise BABDataError, not silently pass.

    The bare ``except Exception: pass`` blocks in strategy.py were replaced with
    narrow ``except (TypeError, ValueError, AttributeError)`` handlers that
    re-raise as ``BABDataError``.  These tests inject invalid values onto an
    already-constructed config (bypassing construction-time validation) so the
    hardened handlers in ``run()`` are actually exercised.
    """

    def test_invalid_shorting_constraints_raises(self):
        df = _make_returns(250, 8, 3)
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=40)
        object.__setattr__(cfg, "shorting_constraints", 12345)  # bypass validation
        with pytest.raises(BABDataError):
            BABStrategy(cfg).run(returns_df=df)

    def test_invalid_position_sizer_raises(self):
        df = _make_returns(250, 8, 3)
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=40)
        object.__setattr__(cfg, "position_sizer", 12345)  # bypass validation
        with pytest.raises(BABDataError):
            BABStrategy(cfg).run(returns_df=df)

    def test_invalid_regime_filter_raises(self):
        df = _make_returns(250, 8, 3)
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=40)
        object.__setattr__(cfg, "regime_filter", 12345)  # bypass validation
        with pytest.raises(BABDataError):
            BABStrategy(cfg).run(returns_df=df)

    def test_valid_optional_features_still_work(self):
        df = _make_returns(300, 8, 5)
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=40, regime_filter=True)
        res = BABStrategy(cfg).run(returns_df=df)
        assert np.isfinite(res.weights.values).all()
