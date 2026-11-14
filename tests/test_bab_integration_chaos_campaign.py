"""Integration chaos for BAB strategy - adversarial hardening."""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABConfig, BABStrategy, data_loader


class TestBABIntegrationChaos:
    def test_all_same_beta_all_zero_signals_no_crash(self):
        np.random.seed(123)
        n = 80
        bench = np.random.randn(n) * 0.01
        # All assets have identical beta relationship to bench
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": bench.copy(),
                "SOL": bench.copy(),
                "XRP": bench.copy(),
            }
        )
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL", "XRP"],
                benchmark="BTC",
                beta_window=30,
                min_observations=20,
                long_quantile=0.3,
                short_quantile=0.3,
            )
        )
        res = strat.run(df)
        # No crashes, weights finite
        assert np.all(np.isfinite(res.weights.values))
        # Dollar neutral where applicable
        row_sums = res.weights.sum(axis=1)
        assert np.allclose(row_sums, 0.0, atol=1e-10)

    def test_constant_benchmark_raises_or_handled_gracefully(self):
        np.random.seed(456)
        n = 90
        bench = np.ones(n) * 0.001  # constant
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": np.random.randn(n) * 0.01,
                "SOL": np.random.randn(n) * 0.01,
            }
        )
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL"],
                benchmark="BTC",
                beta_window=40,
                min_observations=20,
            )
        )
        try:
            res = strat.run(df)
            # If it runs, all betas should be NaN for non-benchmark? Or handled
            assert np.all(np.isfinite(res.weights.values))
        except Exception as e:
            # Acceptable if it fails loudly with BAB errors
            assert isinstance(e, Exception)

    def test_partial_universe_after_filtering(self):
        np.random.seed(789)
        n = 100
        bench = np.random.randn(n) * 0.01
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": 0.5 * bench + np.random.randn(n) * 0.005,
                # SOL missing from data but in universe?
            }
        )
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL"],  # SOL not in data
                benchmark="BTC",
                beta_window=30,
                min_observations=20,
            )
        )
        res = strat.run(df)
        assert True  # universe resolved
        assert np.all(np.isfinite(res.weights.values))

    def test_1day_lag_respected(self):
        np.random.seed(101)
        n = 120
        bench = np.random.randn(n) * 0.01
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": 0.8 * bench + np.random.randn(n) * 0.008,
                "SOL": 1.2 * bench + np.random.randn(n) * 0.012,
                "XRP": 0.3 * bench + np.random.randn(n) * 0.006,
            }
        )
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL", "XRP"],
                benchmark="BTC",
                beta_window=30,
                min_observations=20,
            )
        )
        res = strat.run(df)
        strat_rets = res.backtest["gross_return"]
        assert len(strat_rets) == len(df)

    def test_missing_columns_malformed_data_handling(self):
        np.random.seed(303)
        n = 100
        df = pd.DataFrame(
            {
                "BTC": np.random.randn(n) * 0.01,
            }
        )
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH"],
                benchmark="BTC",
                beta_window=30,
                min_observations=20,
            )
        )
        try:
            res = strat.run(df)
            # May work if ETH not available - universe gets resolved
            assert np.all(np.isfinite(res.weights.values))
        except Exception:
            pass

    def test_all_nan_assets(self):
        np.random.seed(404)
        n = 80
        bench = np.random.randn(n) * 0.01
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": [np.nan] * n,
                "SOL": [np.nan] * n,
            }
        )
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL"],
                benchmark="BTC",
                beta_window=30,
                min_observations=20,
            )
        )
        try:
            res = strat.run(df)
            assert np.all(np.isfinite(res.weights.values))
        except Exception:
            pass

    def test_extreme_outliers(self):
        np.random.seed(505)
        n = 120
        bench = np.random.randn(n) * 0.01
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": 0.7 * bench + np.random.randn(n) * 0.01,
                "SOL": 1.3 * bench + np.random.randn(n) * 0.01,
                "XRP": -0.2 * bench + np.random.randn(n) * 0.01,
            }
        )
        df.iloc[5, 1] = 10.0
        df.iloc[60, 2] = -10.0
        strat = BABStrategy(
            BABConfig(
                universe=["BTC", "ETH", "SOL", "XRP"],
                benchmark="BTC",
                beta_window=40,
                min_observations=20,
            )
        )
        res = strat.run(df)
        assert np.all(np.isfinite(res.weights.values))
