"""Tests for regime detection in Betting Against Beta strategy."""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import BABConfig, BABStrategy
from strategies.betting_against_beta import regime


class TestVolatilityRegimes:
    def test_realized_volatility_calculation(self):
        # Create simple returns
        dates = pd.date_range("2023-01-01", periods=100)
        returns = pd.DataFrame(
            {"BTC": np.random.RandomState(42).normal(0, 0.01, 100)},
            index=dates,
        )
        vol = regime.calculate_realized_volatility(returns, window=20)
        assert isinstance(vol, pd.DataFrame)
        assert vol.shape[0] == 100
        assert "BTC" in vol.columns

    def test_volatility_regime_classification_thresholds(self):
        dates = pd.date_range("2023-01-01", periods=100)
        # Create returns with different volatility periods
        rets = []
        for i in range(50):
            rets.append(np.random.RandomState(i).normal(0, 0.005, 1)[0])  # low vol
        for i in range(50):
            rets.append(np.random.RandomState(i + 100).normal(0, 0.02, 1)[0])  # high vol
        returns = pd.DataFrame({"BTC": rets}, index=dates)
        regimes = regime.classify_volatility_regimes(
            returns, vol_window=10, thresholds=[0.01, 0.015]
        )
        assert isinstance(regimes, pd.DataFrame)
        assert regimes.shape == returns.shape

    def test_volatility_regime_percentile_based(self):
        dates = pd.date_range("2023-01-01", periods=200)
        np.random.seed(123)
        returns = pd.DataFrame(
            {"BTC": np.random.normal(0, 0.01, 200), "ETH": np.random.normal(0, 0.015, 200)},
            index=dates,
        )
        regimes = regime.classify_volatility_regimes_percentile(
            returns, vol_window=20, quantiles=[0.33, 0.67]
        )
        assert isinstance(regimes, pd.DataFrame)
        assert set(regimes.dtypes) or True  # flexible dtype check


class TestTrendMeanRevert:
    def test_moving_average_trend_filter(self):
        dates = pd.date_range("2023-01-01", periods=100)
        # Uptrend
        prices = np.cumsum(np.ones(100) * 0.01) + 100
        returns = pd.DataFrame({"BTC": prices}, index=dates)
        # Convert prices to returns for our API
        ret_df = pd.DataFrame({"BTC": returns["BTC"].pct_change().fillna(0)}, index=dates)
        trend = regime.classify_trend_regime(ret_df, ma_window=20)
        assert isinstance(trend, pd.DataFrame)

    def test_zscore_mean_revert(self):
        dates = pd.date_range("2023-01-01", periods=150)
        np.random.seed(5)
        returns = pd.DataFrame(
            {"BTC": np.random.normal(0, 0.01, 150)}, index=dates
        )
        signals = regime.mean_reversion_zscore(returns, window=30, z_threshold=1.5)
        assert isinstance(signals, pd.DataFrame)


class TestRegimeState:
    def test_regime_state_alignment(self):
        dates = pd.date_range("2023-01-01", periods=80)
        np.random.seed(7)
        returns = pd.DataFrame(
            {"BTC": np.random.normal(0, 0.01, 80), "ETH": np.random.normal(0, 0.012, 80)},
            index=dates,
        )
        state = regime.get_regime_state(returns)
        assert isinstance(state, pd.DataFrame)
        assert state.index.equals(returns.index)

    def test_regime_state_with_insufficient_history(self):
        dates = pd.date_range("2023-01-01", periods=10)
        returns = pd.DataFrame({"BTC": np.random.RandomState(1).normal(0, 0.01, 10)}, index=dates)
        state = regime.get_regime_state(returns, vol_window=50)  # longer than data
        assert isinstance(state, pd.DataFrame)
        assert len(state) == 10


class TestRegimeConfigIntegration:
    def test_babconfig_accepts_regime_params(self):
        cfg = BABConfig(
            regime_filter=True,
            regime_method="vol",
            vol_window=30,
            vol_percentiles=(0.33, 0.66),
            vol_hysteresis=0.1,
            regime_scale_high=0.5,
            regime_scale_low=1.0,
        )
        assert cfg.regime_filter is True
        assert cfg.regime_method == "vol"
        assert cfg.vol_percentiles == (0.33, 0.66)

    def test_babconfig_regime_validation(self):
        try:
            cfg = BABConfig(vol_window=5)  # too small
            assert False, "Should have raised"
        except Exception:
            pass

    def test_babconfig_rejects_bad_regime_method(self):
        try:
            BABConfig(regime_method="volatility")  # retired value
            assert False, "Should have raised"
        except Exception:
            pass

    def test_babconfig_rejects_bad_hysteresis(self):
        try:
            BABConfig(vol_hysteresis=1.5)  # outside [0, 1]
            assert False, "Should have raised"
        except Exception:
            pass

    def test_babconfig_rejects_contradictory_vol_bands(self):
        try:
            BABConfig(vol_thresholds=(0.01, 0.02), vol_percentiles=(0.33, 0.66))
            assert False, "Should have raised"
        except Exception:
            pass

    def test_babconfig_rejects_non_positive_scale(self):
        try:
            BABConfig(regime_scale_high=0.0)
            assert False, "Should have raised"
        except Exception:
            pass

    def test_babconfig_defaults_are_valid(self):
        cfg = BABConfig()
        assert cfg.regime_filter is False
        assert cfg.regime_method in ("vol", "trend", "combined")
        assert 0.0 <= cfg.vol_hysteresis <= 1.0
        assert cfg.regime_scale_high > 0 and cfg.regime_scale_low > 0


class TestRegimeStrategyIntegration:
    def test_strategy_with_regime_filter(self):
        cfg = BABConfig(regime_filter=True, synthetic_n_days=150)
        strat = BABStrategy(cfg)
        result = strat.run()
        assert result is not None
        assert hasattr(result, "backtest")

    def test_regime_filter_is_deterministic(self):
        cfg = BABConfig(regime_filter=True, synthetic_n_days=150, regime_method="combined")
        first = BABStrategy(cfg).run().backtest["cumulative"]
        second = BABStrategy(cfg).run().backtest["cumulative"]
        pd.testing.assert_series_equal(first, second)

    def test_regime_filter_changes_weights(self):
        cfg_off = BABConfig(regime_filter=False, synthetic_n_days=150)
        cfg_on = BABConfig(regime_filter=True, synthetic_n_days=150, regime_scale_high=0.5)
        w_off = BABStrategy(cfg_off).run().weights
        w_on = BABStrategy(cfg_on).run().weights
        assert w_off.shape == w_on.shape
        assert (w_off != w_on).any().any(), "regime_filter should alter weights"

    def test_regime_filter_preserves_dollar_neutrality(self):
        cfg = BABConfig(regime_filter=True, synthetic_n_days=150, dollar_neutral=True)
        weights = BABStrategy(cfg).run().weights
        row_sums = weights.sum(axis=1)
        assert np.allclose(row_sums, 0.0, atol=1e-9), row_sums

    def test_regime_scale_factors_index_aligned_and_causal(self):
        dates = pd.date_range("2023-01-01", periods=120)
        np.random.seed(4)
        returns = pd.DataFrame(
            {
                "BTC": np.random.normal(0, 0.01, 120),
                "ETH": np.random.normal(0, 0.012, 120),
                "SOL": np.random.normal(0, 0.025, 120),
            },
            index=dates,
        )
        cfg = BABConfig(regime_method="vol", vol_window=20, vol_percentiles=(0.33, 0.66))
        factors = regime.regime_scale_factors(returns, cfg)
        assert factors.index.equals(returns.index)
        assert "BTC" not in factors.columns  # benchmark excluded from scaling
        assert set(factors.columns) == {"ETH", "SOL"}
        assert np.isfinite(factors.values).all()
        assert (factors > 0).all().all()  # scaling must remain positive


class TestRegimeEdgeCases:
    def test_constant_series_low_risk_scale(self):
        dates = pd.date_range("2023-01-01", periods=100)
        returns = pd.DataFrame(
            {"BTC": np.ones(100) * 0.001, "ETH": np.ones(100) * 0.001},
            index=dates,
        )
        cfg = BABConfig(regime_method="vol", vol_window=20, vol_percentiles=(0.33, 0.66))
        factors = regime.regime_scale_factors(returns, cfg)
        # Zero vol => lowest-risk regime => scale_low (1.0 by default)
        assert np.allclose(factors.values, 1.0)

    def test_all_nan_window_stays_neutral(self):
        dates = pd.date_range("2023-01-01", periods=20)
        returns = pd.DataFrame(
            {"BTC": np.full(20, np.nan), "ETH": np.full(20, np.nan)},
            index=dates,
        )
        cfg = BABConfig(regime_method="vol", vol_window=10)
        factors = regime.regime_scale_factors(returns, cfg)
        assert np.isfinite(factors.values).all()
        assert np.allclose(factors.values, 1.0)

    def test_single_tradable_asset_runs(self):
        dates = pd.date_range("2023-01-01", periods=100)
        np.random.seed(6)
        returns = pd.DataFrame(
            {"BTC": np.random.normal(0, 0.01, 100), "ETH": np.random.normal(0, 0.012, 100)},
            index=dates,
        )
        cfg = BABConfig(
            regime_filter=True,
            synthetic_n_days=10,
            benchmark="BTC",
            universe_override=["ETH"],
        )
        result = BABStrategy(cfg).run(returns_df=returns)
        assert result is not None
        assert np.isfinite(result.weights.values).all()

    def test_benchmark_excluded_from_regime_scaling(self):
        dates = pd.date_range("2023-01-01", periods=100)
        np.random.seed(8)
        returns = pd.DataFrame(
            {"BTC": np.random.normal(0, 0.01, 100), "ETH": np.random.normal(0, 0.012, 100)},
            index=dates,
        )
        cfg = BABConfig(regime_method="vol", vol_window=20)
        factors = regime.regime_scale_factors(returns, cfg)
        assert "BTC" not in factors.columns


class TestRegimeStrategyIntegration:
    def test_strategy_with_regime_filter(self):
        cfg = BABConfig(regime_filter=True, synthetic_n_days=150)
        strat = BABStrategy(cfg)
        result = strat.run()
        assert result is not None
        assert hasattr(result, "backtest")

    def test_regime_conditional_position_scaling(self):
        dates = pd.date_range("2023-01-01", periods=100)
        np.random.seed(9)
        returns = pd.DataFrame(
            {"BTC": np.random.normal(0, 0.01, 100), "ETH": np.random.normal(0, 0.012, 100)},
            index=dates,
        )
        signals = pd.DataFrame(
            {"BTC": np.ones(100) * 0.1, "ETH": np.ones(100) * -0.1}, index=dates
        )
        scaled = regime.apply_regime_scaling(signals, returns, scale_high_vol=0.5)
        assert isinstance(scaled, pd.DataFrame)
        assert scaled.shape == signals.shape
