import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data import generate_synthetic_returns
from strategies.betting_against_beta.data_loader import BABDataError


class TestCalculateBeta:
    def test_simple_beta(self):
        asset = [0.01, 0.02, -0.01]
        bench = [0.005, 0.01, -0.005]
        b = beta.calculate_beta(asset, bench)
        assert abs(b - 2.0) < 1e-6

    def test_with_min_obs(self):
        asset = [0.01, 0.02]
        bench = [0.005, 0.01]
        b = beta.calculate_beta(asset, bench, min_obs=5)
        assert np.isnan(b)

    def test_nan_values(self):
        asset = [0.01, np.nan, 0.02]
        bench = [0.005, 0.01, 0.01]
        b = beta.calculate_beta(asset, bench)
        assert np.isfinite(b)

    def test_constant_benchmark(self):
        asset = [0.01, 0.02, 0.03]
        bench = [0.01, 0.01, 0.01]
        b = beta.calculate_beta(asset, bench)
        assert np.isnan(b) or np.isfinite(b)

    def test_mismatched_lengths(self):
        asset = pd.Series([0.01, 0.02, 0.03], index=[0, 1, 2])
        bench = pd.Series([0.005, 0.01, 0.015], index=[1, 2, 3])
        b = beta.calculate_beta(asset, bench)
        assert abs(b - 2.0) < 1e-6

    def test_all_nan(self):
        asset = [np.nan, np.nan]
        bench = [0.01, 0.02]
        b = beta.calculate_beta(asset, bench)
        assert np.isnan(b)


class TestCalculateBetaFast:
    def test_fast_basic(self):
        asset = np.array([0.01, 0.02, -0.01])
        bench = np.array([0.005, 0.01, -0.005])
        b = beta.calculate_beta_fast(asset, bench)
        assert abs(b - 2.0) < 1e-6

    def test_fast_min_obs(self):
        b = beta.calculate_beta_fast([0.01], [0.005], min_obs=5)
        assert np.isnan(b)

    def test_fast_constant_bench(self):
        b = beta.calculate_beta_fast([0.01, 0.02, 0.03], [0.01, 0.01, 0.01])
        assert b == 0.0


class TestRollingBeta:
    def test_rolling_beta_series(self):
        df = generate_synthetic_returns(n_days=150, n_assets=4, seed=123)
        asset_col = [c for c in df.columns if c != "BTC"][0]
        res = beta.rolling_beta(df["BTC"], df[asset_col], window=60, min_obs=30)
        assert hasattr(res, "__len__")
        assert len(res) == len(df)

    def test_rolling_beta_with_min_periods(self):
        df = generate_synthetic_returns(n_days=150, n_assets=4, seed=123)
        asset_col = [c for c in df.columns if c != "BTC"][0]
        res = beta.rolling_beta(df["BTC"], df[asset_col], window=60, min_periods=30)
        assert len(res) == len(df)

    def test_estimate_betas(self):
        df = generate_synthetic_returns(n_days=150, n_assets=4, seed=123)
        betas = beta.estimate_betas(df, benchmark="BTC", window=60, min_obs=30)
        assert isinstance(betas, pd.DataFrame)
        assert "BTC" in betas.columns


class TestCalculateRollingBeta:
    def test_raises_on_none(self):
        try:
            beta.calculate_rolling_beta(None, "BTC")
            assert False
        except BABDataError:
            pass

    def test_raises_on_non_df(self):
        try:
            beta.calculate_rolling_beta([1, 2, 3], "BTC")
            assert False
        except BABDataError:
            pass

    def test_raises_on_missing_benchmark(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=1)
        try:
            beta.calculate_rolling_beta(df, "MISSING")
            assert False
        except BABDataError:
            pass

    def test_benchmark_all_nan_raises(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=1)
        df["BTC"] = np.nan
        try:
            beta.calculate_rolling_beta(df, "BTC")
            assert False
        except BABDataError:
            pass

    def test_handles_nan_in_assets(self):
        df = generate_synthetic_returns(n_days=150, n_assets=4, seed=5)
        asset_cols = [c for c in df.columns if c != "BTC"]
        df.iloc[10:20, df.columns.get_loc(asset_cols[0])] = np.nan
        betas = beta.calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
        assert isinstance(betas, pd.DataFrame)
        assert len(betas) == len(df)
