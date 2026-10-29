import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy, BABConfig
from strategies.betting_against_beta.errors import BABDataError


FIX = os.path.join(os.path.dirname(__file__), "fixtures")


class TestStrategyMore:
    def test_run_with_returns_df_passed(self):
        dates = pd.date_range("2023-01-01", periods=60)
        rng = np.random.default_rng(101)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 60)
        df["ETH"] = 0.7 * df["BTC"] + rng.normal(0, 0.01, 60)
        df["SOL"] = 1.3 * df["BTC"] + rng.normal(0, 0.012, 60)
        s = BABStrategy(BABConfig(benchmark="BTC", beta_window=15, min_observations=10))
        res = s.run(returns_df=df)
        assert np.isfinite(res.weights.values).all()

    def test_no_tradable_assets_raises(self):
        dates = pd.date_range("2023-01-01", periods=40)
        df = pd.DataFrame({"BTC": np.ones(40)*0.01}, index=dates)
        cfg = BABConfig(universe=["ETH"], benchmark="BTC", beta_window=10, min_observations=5)
        s = BABStrategy(cfg)
        with pytest.raises(ValueError):
            s.run(returns_df=df)

    def test_rebalance_monthly_datetime(self):
        dates = pd.date_range("2023-01-01", periods=90)
        rng = np.random.default_rng(103)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 90)
        df["ETH"] = 0.8 * df["BTC"] + rng.normal(0, 0.01, 90)
        df["SOL"] = 1.2 * df["BTC"] + rng.normal(0, 0.011, 90)
        s = BABStrategy(BABConfig(rebalance_freq="monthly", beta_window=20, min_observations=10))
        res = s.run(returns_df=df)
        assert np.isfinite(res.weights.values).all()

    def test_weekly_rebalance_non_datetime_index(self):
        dates = list(range(100))
        rng = np.random.default_rng(107)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 100)
        df["ETH"] = 0.9 * df["BTC"] + rng.normal(0, 0.01, 100)
        df["SOL"] = 1.1 * df["BTC"] + rng.normal(0, 0.01, 100)
        s = BABStrategy(BABConfig(rebalance_freq="weekly", beta_window=15, min_observations=8))
        res = s.run(returns_df=df)
        assert np.isfinite(res.weights.values).all()

    def test_regime_and_beta_neutral_combo(self):
        dates = pd.date_range("2023-01-01", periods=100)
        rng = np.random.default_rng(109)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 100)
        df["ETH"] = 0.75 * df["BTC"] + rng.normal(0, 0.01, 100)
        df["SOL"] = 1.25 * df["BTC"] + rng.normal(0, 0.012, 100)
        cfg = BABConfig(regime_filter=True, beta_neutral=True, beta_neutral_enforcement=False,
                        beta_target=0.0, beta_tolerance=0.001, max_beta_drift=0.002,
                        enable_tracking_error_monitoring=True, tracking_error_tolerance=0.02,
                        beta_neutral_correction=True, beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(returns_df=df)
        assert np.isfinite(res.weights.values).all()

    def test_strategy_with_shorting_constraints_error_passthrough(self):
        dates = pd.date_range("2023-01-01", periods=50)
        rng = np.random.default_rng(113)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 50)
        df["ETH"] = 0.8 * df["BTC"] + rng.normal(0, 0.01, 50)
        # pass something that might cause issue but strategy catches non-BABDataError
        cfg = BABConfig(shorting_constraints={"bad": True}, beta_window=15, min_observations=8)
        s = BABStrategy(cfg)
        res = s.run(returns_df=df)
        assert np.isfinite(res.weights.values).all()
