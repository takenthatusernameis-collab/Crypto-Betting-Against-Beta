"""Adversarial beta hardening - cross-emitter consistency."""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta


class TestBetaAdversarialHardening:
    def test_constant_benchmark_across_all_calculators_identical_nan(self):
        bench = np.ones(90) * 0.002
        np.random.seed(7)
        asset = np.random.randn(90) * 0.01
        b1 = beta.calculate_beta(asset, bench)
        b2 = beta.calculate_beta_fast(asset, bench)
        r = beta.rolling_beta(pd.Series(asset), pd.Series(bench), window=45, min_obs=20)
        assert np.all(np.isnan(r.values))
        assert np.isnan(b1)
        assert np.isnan(b2)

    def test_rolling_beta_series_constant_benchmark_all_nan(self):
        bench = np.array([0.001] * 50)
        asset = np.random.RandomState(11).randn(50) * 0.01
        res = beta._calc_rolling_beta_series(bench, asset, window=20, min_obs=10)
        assert np.all(np.isnan(res))

    def test_dataframe_mixed_bad_finite_assets_constant_bench_nan(self):
        np.random.seed(1234)
        bench = np.array([0.003] * 80)
        df = pd.DataFrame(
            {
                "BTC": bench,
                "ETH": np.random.randn(80) * 0.01,
                "SOL": [np.nan] * 80,
                "XRP": list(np.random.randn(80) * 0.01),
            }
        )
        res = beta.calculate_rolling_beta(df, "BTC", window=30, min_obs=15)
        # SOL is all NaN - per-series path should still give NaN; ETH/XRP
        # finite but benchmark constant -> NaN
        assert np.all(np.isnan(res["ETH"].values))
        assert np.all(np.isnan(res["SOL"].values))
        assert np.all(np.isnan(res["XRP"].values))
        assert np.allclose(res["BTC"].values, 1.0)
