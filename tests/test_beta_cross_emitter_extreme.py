"""Extreme cross-emitter beta agreement tests."""
import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta


class TestBetaCrossEmitterExtreme:
    def test_all_paths_nan_for_constant_bench_various_shapes(self):
        rng = np.random.RandomState(999)
        for const_val in [0.0, 0.01, -0.001, 1e-12]:
            bench = np.full(100, const_val)
            asset = rng.randn(100) * 0.01
            # scalar paths
            assert np.isnan(beta.calculate_beta(asset, bench))
            assert np.isnan(beta.calculate_beta_fast(asset, bench))
            # rolling series
            r1 = beta.rolling_beta(pd.Series(asset), pd.Series(bench), window=50, min_obs=10)
            assert np.all(np.isnan(r1))
            r2 = beta.rolling_beta(list(asset), list(bench), window=50, min_obs=10)
            assert isinstance(r2, (np.ndarray, pd.Series))
            # dataframe
            df = pd.DataFrame({'BTC': bench, 'ETH': asset, 'SOL': asset*1.1})
            res = beta.calculate_rolling_beta(df, 'BTC', window=50, min_obs=10)
            assert np.all(np.isnan(res['ETH']))
            assert np.all(np.isnan(res['SOL']))
            assert np.allclose(res['BTC'], 1.0)

    def test_near_constant_benchmark_treated_as_degenerate(self):
        rng = np.random.RandomState(42)
        bench = np.full(80, 0.001)
        bench[5] = 0.001 + 1e-20  # effectively constant
        asset = rng.randn(80) * 0.01
        assert np.isnan(beta.calculate_beta(asset, bench))
        assert np.isnan(beta.calculate_beta_fast(asset, bench))
        df = pd.DataFrame({'BTC': bench, 'ETH': asset})
        res = beta.calculate_rolling_beta(df, 'BTC', window=30, min_obs=10)
        # Should be NaN due to degeneracy
        assert np.all(np.isnan(res['ETH'].values))
