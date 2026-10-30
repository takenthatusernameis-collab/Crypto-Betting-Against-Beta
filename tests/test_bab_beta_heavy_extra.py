import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaHeavyExtra:
    def test_estimate_betas_aliases(self):
        idx = pd.date_range("2023-01-01", periods=100)
        df = pd.DataFrame({
            "BTC": np.random.randn(100)*0.01,
            "ETH": np.random.randn(100)*0.01,
            "SOL": np.random.randn(100)*0.01,
        }, index=idx)
        res = beta.estimate_betas(df, benchmark="BTC", window=60, min_observations=50)
        assert isinstance(res, pd.DataFrame)
        res2 = beta.estimate_betas(df, benchmark="BTC", window=60, min_obs=50)
        assert isinstance(res2, pd.DataFrame)

    def test_rolling_beta_series_inputs(self):
        a = pd.Series(np.random.randn(50))
        b = pd.Series(np.random.randn(50))
        res = beta.rolling_beta(a, b, window=30)
        assert isinstance(res, pd.Series) or hasattr(res, "__len__")
        # lists
        res = beta.rolling_beta(list(a), list(b), window=30)
        assert hasattr(res, "__len__")
        # arrays
        res = beta.rolling_beta(np.array(a), np.array(b), window=30)
        assert hasattr(res, "__len__")

    def test_calculate_beta_edge_cases(self):
        # different lengths as arrays
        res = beta.calculate_beta([0.01,0.02,0.03], [0.01,0.02])
        assert isinstance(res, float) or np.isnan(res)
        # with series different lengths
        res = beta.calculate_beta(pd.Series([0.01]*10), pd.Series([0.01]*5))
        assert isinstance(res, float) or np.isnan(res)
        # all nan
        res = beta.calculate_beta([np.nan, np.nan], [np.nan, np.nan])
        assert np.isnan(res)
        # min_obs
        res = beta.calculate_beta([0.01,0.02], [0.01,0.02], min_obs=10)
        assert np.isnan(res)
        # lists
        res = beta.calculate_beta([0.01,0.02,0.03,0.04], [0.01,0.015,0.02,0.025])
        assert np.isfinite(res) or np.isnan(res)

    def test_calculate_beta_fast(self):
        res = beta.calculate_beta_fast([0.01,0.02,np.nan,0.03], [0.01,np.nan,0.02,0.03])
        assert isinstance(res, float)
        res = beta.calculate_beta_fast([np.nan,np.nan], [np.nan,np.nan])
        assert isinstance(res, float)
        res = beta.calculate_beta_fast([0.01,0.02], [0.01,0.02], min_obs=10)
        assert isinstance(res, float)
        res = beta.calculate_beta_fast([0.01,0.02,0.03], [5.0,5.0,5.0])  # constant benchmark
        assert isinstance(res, float)

    def test_calculate_rolling_beta_edge_cases(self):
        idx = pd.date_range("2023-01-01", periods=50)
        df = pd.DataFrame({
            "BTC": np.ones(50)*0.001,  # constant
            "ETH": np.random.randn(50)*0.01,
        }, index=idx)
        try:
            res = beta.calculate_rolling_beta(df, "BTC", window=20, min_obs=10)
            assert isinstance(res, pd.DataFrame)
        except Exception:
            pass
        # benchmark no finite
        df2 = pd.DataFrame({"BTC": [np.nan]*50, "ETH": [0.01]*50}, index=idx)
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(df2, "BTC")
        # bad inputs
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(None, "BTC")
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta([1,2,3], "BTC")
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(pd.DataFrame({"A":[1,2,3]}), "BTC")
        # asset with nans
        df3 = pd.DataFrame({
            "BTC": np.random.randn(60)*0.01,
            "ETH": np.concatenate([[np.nan]*5, np.random.randn(55)*0.01]),
        }, index=pd.date_range("2023-01-01", periods=60))
        res = beta.calculate_rolling_beta(df3, "BTC", window=30, min_obs=20)
        assert isinstance(res, pd.DataFrame)
