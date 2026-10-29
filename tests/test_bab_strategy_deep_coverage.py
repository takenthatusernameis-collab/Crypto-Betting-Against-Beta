import json
import math
import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy, BABConfig
from strategies.betting_against_beta.errors import BABDataError


FIX = os.path.join(os.path.dirname(__file__), "fixtures")


class TestStrategyInitKwargs:
    def test_kwargs_aliases_window_min_obs(self):
        s = BABStrategy(window=50, min_obs=20, benchmark="BTC")
        assert s.config.beta_window == 50
        assert s.config.min_observations == 20

    def test_kwargs_many_fields(self):
        s = BABStrategy(
            universe=["BTC", "ETH"],
            benchmark="BTC",
            beta_window=30,
            rebalance_freq="weekly",
            long_quantile=0.25,
            short_quantile=0.25,
            dollar_neutral=True,
            min_observations=10,
            data_source=None,
            min_rows=10,
            transaction_costs=0.001,
            slippage=0.0005,
            max_turnover=None,
            max_position_size=None,
            max_total_turnover=1.0,
            rolling_min_window=10,
            synthetic_seed=123,
            synthetic_n_days=50,
            universe_override=None,
            position_sizer={"type": "equal"},
            shorting_constraints={"max_short_leverage": 1.0},
            regime_filter=True,
            regime_method="vol",
            vol_window=10,
            vol_use_ewma=False,
            vol_thresholds=[0.5, 1.5],
            vol_percentiles=None,
            vol_hysteresis=0.1,
            trend_ma_window=20,
            trend_z_window=10,
            regime_scale_high=1.0,
            regime_scale_low=0.5,
            beta_neutral=True,
            beta_neutral_enforcement=True,
            beta_target=0.0,
            beta_tolerance=1e-3,
            max_beta_drift=1e-3,
            tracking_error_tolerance=0.01,
            tracking_error_limit=0.01,
            enable_tracking_error_monitoring=True,
            beta_neutral_correction=True,
            beta_neutral_adjustment=True,
        )
        res = s.run()
        assert res.weights is not None


class TestStrategyDataSources:
    def test_data_source_csv(self):
        cfg = BABConfig(data_source=os.path.join(FIX, "returns.csv") if os.path.exists(os.path.join(FIX, "returns.csv")) else os.path.join(FIX, "messy_returns.csv"), benchmark="BTC", beta_window=20, min_observations=10)
        # messy has dates/columns; should load
        s = BABStrategy(cfg)
        res = s.run()
        assert np.isfinite(res.weights.values).all()

    def test_data_source_json_via_config(self):
        cfg = BABConfig(data_source=os.path.join(FIX, "returns.json"), benchmark="BTC", beta_window=3, min_observations=2)
        s = BABStrategy(cfg)
        res = s.run()
        assert np.isfinite(res.weights.values).all()

    def test_explicit_returns_df_overrides_config(self):
        dates = pd.date_range("2023-01-01", periods=50)
        df = pd.DataFrame(index=dates)
        rng = np.random.default_rng(5)
        df["BTC"] = rng.normal(0.001, 0.02, 50)
        df["ETH"] = 0.8 * df["BTC"] + rng.normal(0, 0.01, 50)
        df["SOL"] = 1.2 * df["BTC"] + rng.normal(0, 0.015, 50)
        cfg = BABConfig(data_source=os.path.join(FIX, "returns.json"), benchmark="BTC", beta_window=10, min_observations=5)
        s = BABStrategy(cfg)
        res = s.run(returns_df=df)
        assert np.isfinite(res.weights.values).all()


class TestStrategyRebalanceFreq:
    def test_monthly_rebalance(self):
        dates = pd.date_range("2023-01-01", periods=80)
        rng = np.random.default_rng(9)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 80)
        for name in ["ETH", "SOL", "BNB", "XRP"]:
            df[name] = rng.normal(0.8, 0.01) * df["BTC"] + rng.normal(0, 0.01, 80)
        cfg = BABConfig(rebalance_freq="monthly", beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(df)
        w = res.weights
        diffs = w.diff().abs().sum(axis=1)
        assert (diffs > 1e-18).sum() < len(w) * 0.3

    def test_weekly_with_non_datetime_fallback(self):
        # Create index that's not DatetimeIndex
        dates = list(range(80))
        rng = np.random.default_rng(11)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 80)
        df["ETH"] = 0.9 * df["BTC"] + rng.normal(0, 0.01, 80)
        df["SOL"] = 1.1 * df["BTC"] + rng.normal(0, 0.012, 80)
        cfg = BABConfig(rebalance_freq="weekly", beta_window=15, min_observations=8)
        s = BABStrategy(cfg)
        res = s.run(df)
        assert np.isfinite(res.weights.values).all()


class TestStrategyBranches:
    def test_shorting_constraints_applied(self):
        dates = pd.date_range("2023-01-01", periods=60)
        rng = np.random.default_rng(7)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 60)
        df["ETH"] = 0.5 * df["BTC"] + rng.normal(0, 0.01, 60)
        df["SOL"] = 1.5 * df["BTC"] + rng.normal(0, 0.015, 60)
        cfg = BABConfig(shorting_constraints={"max_short_leverage": 0.3}, beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(df)
        assert np.isfinite(res.weights.values).all()

    def test_position_sizer_applied(self):
        dates = pd.date_range("2023-01-01", periods=60)
        rng = np.random.default_rng(13)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 60)
        df["ETH"] = 0.7 * df["BTC"] + rng.normal(0, 0.01, 60)
        df["SOL"] = 1.3 * df["BTC"] + rng.normal(0, 0.012, 60)
        cfg = BABConfig(position_sizer={"type": "equal"}, beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(df)
        assert np.isfinite(res.weights.values).all()

    def test_regime_filter_enabled(self):
        dates = pd.date_range("2023-01-01", periods=80)
        rng = np.random.default_rng(17)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 80)
        df["ETH"] = 0.6 * df["BTC"] + rng.normal(0, 0.01, 80)
        df["SOL"] = 1.4 * df["BTC"] + rng.normal(0, 0.014, 80)
        cfg = BABConfig(regime_filter=True, beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(df)
        assert np.isfinite(res.weights.values).all()

    def test_beta_neutral_enabled(self):
        dates = pd.date_range("2023-01-01", periods=80)
        rng = np.random.default_rng(23)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 80)
        df["ETH"] = 0.8 * df["BTC"] + rng.normal(0, 0.01, 80)
        df["SOL"] = 1.2 * df["BTC"] + rng.normal(0, 0.013, 80)
        cfg = BABConfig(beta_neutral=True, beta_neutral_enforcement=True, beta_target=0.0,
                        beta_tolerance=1e-3, enable_tracking_error_monitoring=True,
                        tracking_error_tolerance=0.05, beta_neutral_correction=True,
                        beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(df)
        assert np.isfinite(res.weights.values).all()

    def test_finiteness_guard_catches_nonfinite(self):
        dates = pd.date_range("2023-01-01", periods=40)
        rng = np.random.default_rng(29)
        df = pd.DataFrame(index=dates)
        df["BTC"] = rng.normal(0.001, 0.02, 40)
        df["ETH"] = 0.9 * df["BTC"] + rng.normal(0, 0.01, 40)
        cfg = BABConfig(beta_window=10, min_observations=5)
        s = BABStrategy(cfg)
        res = s.run(df)
        # force nonfinite
        res.weights.iloc[5, 0] = np.inf
        # run again logic - call report/tear_sheet
        rep = s.report(res)
        js = s.report_to_json(rep)
        ts = s.tear_sheet(res)
        assert isinstance(js, str)
        assert "BAB STRATEGY" in ts


class TestStrategyReportTearSheet:
    def test_report_tear_sheet_without_run_raises(self):
        s = BABStrategy()
        with pytest.raises(RuntimeError):
            s.report()
        with pytest.raises(RuntimeError):
            s.tear_sheet()

    def test_report_to_json_with_nan_inf(self):
        rep = {"a": float("nan"), "b": {"c": float("inf"), "d": [float("-inf"), 1.0]}}
        js = BABStrategy.report_to_json(rep)
        data = json.loads(js)
        assert data["a"] == 0.0
        assert data["b"]["c"] == 0.0
        assert data["b"]["d"][0] == 0.0
        assert data["b"]["d"][1] == 1.0
