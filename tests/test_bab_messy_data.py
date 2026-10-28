"""Tests for messy real-data robustness."""
import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy, BABConfig
from strategies.betting_against_beta.data_loader import BABDataError


FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "messy_returns.csv")
REAL_DEFECTS = os.path.join(os.path.dirname(__file__), "fixtures", "real_data_defects.csv")


class TestRealDataDefects:
    """Regression tests for a realistic messy CSV fixture.

    The fixture deliberately contains: a missing calendar date, a NaN block,
    a duplicate timestamp, a delisted asset column, and a non-BTC benchmark.
    The pipeline must never emit NaN weights silently on this input.
    """

    def test_real_data_defects_fixture_runs_finite(self):
        cfg = BABConfig(
            data_source=REAL_DEFECTS,
            benchmark="BTC",
            beta_window=3,
            min_observations=2,
        )
        strat = BABStrategy(cfg)
        res = strat.run()
        weights = res.weights
        assert not weights.empty
        assert not weights.isna().any().any(), "Found NaN weights"
        assert np.isfinite(weights.values).all(), "Found non-finite weights"
        # Columns outside the configured universe (e.g. delisted/legacy assets)
        # are excluded from the tradable set.
        assert "DEL" not in strat.config.universe
        assert "OLD" not in strat.config.universe

    def test_real_data_defects_fixture_missing_date_is_handled(self):
        # 2023-01-03 is absent from the fixture; the loader must not crash and
        # the resulting index must be a sorted DatetimeIndex.
        cfg = BABConfig(
            data_source=REAL_DEFECTS,
            benchmark="BTC",
            beta_window=3,
            min_observations=2,
        )
        strat = BABStrategy(cfg)
        res = strat.run()
        assert isinstance(res.returns.index, pd.DatetimeIndex)
        assert res.returns.index.is_monotonic_increasing


class TestMessyDataRobustness:
    def test_messy_csv_does_not_produce_nan_weights_silently(self):
        cfg = BABConfig(data_source=FIXTURE, benchmark="BTC", beta_window=3, min_observations=2)
        strat = BABStrategy(cfg)
        res = strat.run()
        weights = res.weights
        # No NaN weights
        assert not weights.isna().any().any(), f"Found NaN weights"
        # Weights should be finite
        assert np.isfinite(weights.values).all()

    def test_missing_benchmark_raises(self):
        df = pd.DataFrame({
            "date": pd.date_range("2023-01-01", periods=10),
            "ETH": np.random.randn(10) * 0.01,
        })
        cfg = BABConfig(benchmark="BTC")
        strat = BABStrategy(cfg)
        with pytest.raises(Exception):
            strat.run(returns_df=df)

    def test_all_nan_beta_period_excluded_safely(self):
        # Create data where a row might produce issues
        dates = pd.date_range("2023-01-01", periods=20)
        df = pd.DataFrame(index=dates)
        df["BTC"] = np.random.randn(20) * 0.01
        df["ETH"] = np.nan  # all nan
        df["ALT"] = np.random.randn(20) * 0.01
        cfg = BABConfig(benchmark="BTC", beta_window=5, min_observations=3)
        strat = BABStrategy(cfg)
        res = strat.run(returns_df=df)
        assert not res.weights.isna().any().any()

    def test_tz_aware_index_normalized(self):
        dates = pd.date_range("2023-01-01", periods=15, tz="UTC")
        df = pd.DataFrame(index=dates)
        df["BTC"] = np.random.randn(15) * 0.01
        df["ETH"] = np.random.randn(15) * 0.01
        cfg = BABConfig(benchmark="BTC", beta_window=5, min_observations=3)
        strat = BABStrategy(cfg)
        res = strat.run(returns_df=df)
        assert isinstance(res.returns.index, pd.DatetimeIndex)
        assert res.returns.index.tz is None
        weights = res.weights
        assert not weights.isna().any().any()
        assert np.isfinite(weights.values).all()
