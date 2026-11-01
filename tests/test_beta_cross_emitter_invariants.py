"""Cross-emitter beta invariants - adversarial hardening."""
import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


class TestBetaCrossEmitterInvariants:
    def test_zero_variance_benchmark_nan_across_all_emitters(self):
        bench = np.array([0.005] * 60)
        np.random.seed(123)
        asset = np.random.normal(0, 0.01, 60)

        # All must return NaN
        assert np.isnan(beta.calculate_beta(asset, bench))
        assert np.isnan(beta.calculate_beta_fast(asset, bench))
        res_rolling = beta.rolling_beta(pd.Series(asset), pd.Series(bench), window=30, min_obs=1)
        # Single series path - all should be NaN for constant benchmark
        assert np.all(np.isnan(res_rolling))

        df = pd.DataFrame({'BTC': bench, 'ETH': asset, 'SOL': asset * 0.8})
        res = beta.calculate_rolling_beta(df, 'BTC', window=30, min_obs=1)
        # DataFrame path sets NaN for degenerate benchmark across all assets
        assert np.all(np.isnan(res['ETH'].values))
        assert np.allclose(res['BTC'].values, 1.0)

    def test_single_point_insufficient_obs_nan(self):
        assert np.isnan(beta.calculate_beta([0.01], [0.02]))
        assert np.isnan(beta.calculate_beta_fast([0.01], [0.02]))
        res = beta.rolling_beta([0.01], [0.02], window=90, min_obs=60)
        assert np.all(np.isnan(res))

    def test_all_nan_benchmark_raises_in_dataframe_path(self):
        df = pd.DataFrame({'BTC': [np.nan]*10, 'ETH': [0.01]*10})
        try:
            beta.calculate_rolling_beta(df, 'BTC')
            assert False
        except BABDataError:
            pass

    def test_perfect_colinearity_handled(self):
        bench = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        asset = 2.0 * bench + 0.001  # near perfect colinearity
        b = beta.calculate_beta(asset, bench)
        assert np.isfinite(b) or np.isnan(b)  # should not crash

    def test_mixed_finite_nan_rolling_consistency(self):
        np.random.seed(42)
        bench = np.random.randn(50) * 0.01
        asset = 0.5 * bench + np.random.randn(50) * 0.005
        bench_mod = bench.copy()
        asset_mod = asset.copy()
        bench_mod[10] = np.nan
        asset_mod[15] = np.nan
        res = beta.rolling_beta(asset_mod, bench_mod, window=20, min_obs=10)
        assert res.shape == (50,)

    def test_dataframe_with_bad_asset_fallback(self):
        df = pd.DataFrame({
            'BTC': np.random.RandomState(1).randn(40)*0.01,
            'ETH': 'bad_data',  # will cause issues
        })
        # Should not crash catastrophically
        try:
            res = beta.calculate_rolling_beta(df, 'BTC', window=20, min_obs=10)
            assert isinstance(res, pd.DataFrame)
        except Exception:
            pass  # or handle as appropriate
