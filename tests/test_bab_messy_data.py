"""Tests for messy real-data robustness."""
import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy, BABConfig
from strategies.betting_against_beta.data_loader import BABDataError


FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "messy_returns.csv")


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
