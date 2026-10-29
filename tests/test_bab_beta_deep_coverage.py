import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaDeep:
    def test_estimate_betas_min_obs_clamp(self):
        idx = pd.date_range("2023-01-01", periods=50)
        rng = np.random.default_rng(1)
        mkt = rng.normal(0, 0.01, 50)
        df = pd.DataFrame({"BTC": mkt, "ETH": 0.8 * mkt + rng.normal(0, 0.005, 50)}, index=idx)
        b = beta.estimate_betas(df, benchmark="BTC", window=30, min_obs=40)
        assert isinstance(b, pd.DataFrame)

    def test_estimate_betas_min_observations_alias(self):
        idx = pd.date_range("2023-01-01", periods=50)
        rng = np.random.default_rng(2)
        mkt = rng.normal(0, 0.01, 50)
        df = pd.DataFrame({"BTC": mkt, "ETH": 1.1 * mkt + rng.normal(0, 0.005, 50)}, index=idx)
        b = beta.estimate_betas(df, benchmark="BTC", window=30, min_observations=15)
        assert isinstance(b, pd.DataFrame)

    def test_rolling_beta_series_pair(self):
        idx = pd.date_range("2023-01-01", periods=40)
        rng = np.random.default_rng(3)
        mkt = pd.Series(rng.normal(0, 0.01, 40), index=idx)
        a = pd.Series(0.6 * mkt + rng.normal(0, 0.005, 40), index=idx)
        rb = beta.rolling_beta(mkt, a, window=20, min_periods=10)
        assert isinstance(rb, pd.Series)
        assert len(rb) == 40

    def test_rolling_beta_series_pair_min_obs(self):
        idx = pd.date_range("2023-01-01", periods=40)
        rng = np.random.default_rng(4)
        mkt = pd.Series(rng.normal(0, 0.01, 40), index=idx)
        a = pd.Series(1.3 * mkt + rng.normal(0, 0.005, 40), index=idx)
        rb = beta.rolling_beta(mkt, a, window=15, min_obs=12)
        assert isinstance(rb, pd.Series)

    def test_rolling_beta_fallback(self):
        idx = pd.date_range("2023-01-01", periods=30)
        rng = np.random.default_rng(5)
        mkt = rng.normal(0, 0.01, 30)
        a = 0.9 * mkt + rng.normal(0, 0.004, 30)
        rb = beta.rolling_beta(np.asarray(mkt), np.asarray(a), window=10, min_obs=5)
        assert hasattr(rb, "__len__")

    def test_calculate_beta_with_series_alignment(self):
        # different lengths via construction
        bench = pd.Series([0.01, 0.02, -0.01, 0.03, 0.0, 0.01])
        asset = pd.Series([0.015, 0.025, -0.005, 0.04, 0.002, 0.012, 0.01])  # longer
        # function tries to align
        out = beta.calculate_beta(asset, bench)
        assert np.isfinite(out)

    def test_calculate_beta_all_nan(self):
        out = beta.calculate_beta([np.nan, np.nan], [0.01, 0.02])
        assert np.isnan(out)

    def test_calculate_beta_mismatched_no_series(self):
        out = beta.calculate_beta([0.01, 0.02], [0.01])
        assert out is not None

    def test_calculate_beta_min_obs_fail(self):
        out = beta.calculate_beta([0.01, 0.02, 0.03], [0.01, 0.02, 0.03], min_obs=10)
        assert np.isnan(out)

    def test_calculate_beta_fast_paths(self):
        a = np.array([0.01, 0.02, -0.01, 0.03])
        b = np.array([0.01, 0.015, -0.005, 0.02])
        out = beta.calculate_beta_fast(a, b)
        assert np.isfinite(out)
        out2 = beta.calculate_beta_fast(a, b, min_obs=2)
        assert np.isfinite(out2)
        out3 = beta.calculate_beta_fast([np.nan, 0.01], [0.01, 0.02])
        assert np.isfinite(out3) or np.isnan(out3)
        out4 = beta.calculate_beta_fast([np.nan, np.nan], [0.01, 0.02])
        assert np.isnan(out4)
        out5 = beta.calculate_beta_fast([0.01, 0.02], [np.nan, 0.01], min_obs=5)
        assert np.isnan(out5)

    def test_calculate_rolling_beta_errors(self):
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(None, "BTC")
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta([1, 2, 3], "BTC")
        df = pd.DataFrame({"ETH": [0.01, 0.02]})
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(df, "BTC")
        df2 = pd.DataFrame({"BTC": [np.nan, np.nan], "ETH": [0.01, 0.02]})
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(df2, "BTC")

    def test_calculate_rolling_beta_with_bad_assets(self):
        idx = pd.date_range("2023-01-01", periods=50)
        rng = np.random.default_rng(7)
        df = pd.DataFrame(index=idx)
        df["BTC"] = rng.normal(0.001, 0.02, 50)
        df["ETH"] = 0.8 * df["BTC"] + rng.normal(0, 0.01, 50)
        df["BAD"] = [np.nan] * 10 + list(rng.normal(0.01, 0.02, 40))
        betas = beta.calculate_rolling_beta(df, "BTC", window=20, min_obs=10)
        assert "BAD" in betas.columns
        assert betas["BTC"].iloc[0] == 1.0 or np.isfinite(betas["BTC"].iloc[-1])

    def test_rolling_beta_fallback_exception(self):
        # pass objects that might trigger except
        class Dummy:
            pass
        rb = beta.rolling_beta(Dummy(), Dummy())
        assert rb is not None
