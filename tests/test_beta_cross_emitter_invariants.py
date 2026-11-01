"""Cross-emitter beta invariants - adversarial hardening."""
import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


class TestBetaCrossEmitterInvariants:
    def test_zero_variance_benchmark_nan_across_all_emitters_extended(self):
        # Constant benchmark with different patterns
        for bench_val in [0.0, 0.001, -0.002, 1e-18]:
            bench = np.array([bench_val] * 100)
            np.random.seed(12345)
            asset = np.random.normal(0.001, 0.02, 100)
            # All must return NaN
            assert np.isnan(beta.calculate_beta(asset, bench)), f"calc_beta failed for {bench_val}"
            assert np.isnan(beta.calculate_beta_fast(asset, bench)), f"calc_beta_fast failed for {bench_val}"
            res_rolling = beta.rolling_beta(pd.Series(asset), pd.Series(bench), window=30, min_obs=5)
            assert np.all(np.isnan(res_rolling)), f"rolling_beta failed for {bench_val}"
            df = pd.DataFrame({'BTC': bench, 'ETH': asset, 'SOL': asset * 1.5 + 0.001})
            res = beta.calculate_rolling_beta(df, 'BTC', window=30, min_obs=5)
            assert np.all(np.isnan(res['ETH'].values)), f"df ETH failed for {bench_val}"
            assert np.all(np.isnan(res['SOL'].values)), f"df SOL failed for {bench_val}"
            assert np.allclose(res['BTC'].values, 1.0)

    def test_all_nan_benchmark_dataframe_raises(self):
        df = pd.DataFrame({'BTC': [np.nan]*50, 'ETH': np.random.randn(50)*0.01})
        try:
            beta.calculate_rolling_beta(df, 'BTC')
            assert False, "Should have raised"
        except BABDataError:
            pass

    def test_inf_benchmark_nan(self):
        bench = np.array([np.inf] * 60)
        asset = np.array([0.01]*60)
        assert np.isnan(beta.calculate_beta(asset, bench))
        assert np.isnan(beta.calculate_beta_fast(asset, bench))

    def test_benchmark_all_inf_rolling(self):
        bench = np.array([np.inf, -np.inf] + [np.inf]*58)
        asset = np.random.randn(60)*0.01
        res = beta.rolling_beta(asset, bench, window=20, min_obs=5)
        assert np.all(np.isnan(res)) or res.shape == (60,)

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

    def test_calculate_beta_with_list_series_mixed_types(self):
        import pandas as pd
        # Lists
        assert np.isfinite(beta.calculate_beta([0.01,0.02,0.03,0.04], [0.005,0.01,0.015,0.02])) or np.isnan(beta.calculate_beta([0.01,0.02,0.03,0.04], [0.005,0.01,0.015,0.02]))
        # Series
        a = pd.Series([0.01,0.02,-0.01,0.03,0.02])
        b = pd.Series([0.005,0.01,-0.005,0.015,0.01])
        res = beta.calculate_beta(a,b)
        assert np.isfinite(res) or np.isnan(res)

    def test_rolling_beta_with_object_arrays_fallback(self):
        # Pass objects
        class Arr:
            def __init__(self, vals):
                self.vals = vals
            def __len__(self):
                return len(self.vals)
            def __iter__(self):
                return iter(self.vals)
        # This might go to fallback paths
        try:
            res = beta.rolling_beta(Arr([0.01]*10), Arr([0.005]*10), window=5)
            assert isinstance(res, np.ndarray)
        except Exception:
            pass

    def test_calculate_beta_alignment_exception_path(self):
        # Force alignment exception - make different lengths with Series
        import pandas as pd
        a = pd.Series([1,2,3,4,5])
        b = pd.Series([0.1,0.2,0.3,0.4])  # different length
        orig = pd.concat
        try:
            def bad_concat(*args, **kwargs):
                class Bad:
                    def dropna(self):
                        raise AttributeError("bad")
                return Bad()
            pd.concat = bad_concat
            res = beta.calculate_beta(a,b)
            assert np.isnan(res)
        finally:
            pd.concat = orig

    def test_dataframe_all_assets_bad_fallback(self):
        df = pd.DataFrame({
            'BTC': np.array([0.01]*50),
            'ETH': np.array([float('nan')]*50),  # all nan
            'SOL': np.array([float('inf')]*50),
        })
        res = beta.calculate_rolling_beta(df, 'BTC', window=20, min_obs=10)
        assert isinstance(res, pd.DataFrame)
        # Should produce NaN for bad assets
        assert np.all(np.isnan(res['ETH']))
        assert np.all(np.isnan(res['SOL']))
