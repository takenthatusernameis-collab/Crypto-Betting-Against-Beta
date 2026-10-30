import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


class TestBetaCoverageExtra:
    def test_estimate_betas_alias_and_clamps(self):
        # min_observations alias
        returns = pd.DataFrame({
            'MKT': [0.01, 0.02, -0.01, 0.03, 0.0, 0.01] * 20,
            'A':   [0.015, 0.025, -0.005, 0.035, 0.005, 0.015] * 20,
        })
        res = beta.estimate_betas(returns, benchmark='MKT', window=60, min_observations=10)
        assert 'A' in res.columns
        # min_obs > window clamped
        res2 = beta.estimate_betas(returns, benchmark='MKT', window=5, min_obs=10)
        assert 'A' in res2.columns

    def test_rolling_beta_series_fallback_paths(self):
        # both not Series - go to _calc_rolling_beta_series via try
        a = np.array([0.01, 0.02, -0.01, 0.03])
        b = np.array([0.005, 0.01, -0.005, 0.015])
        out = beta.rolling_beta(a, b, window=3, min_obs=2)
        assert len(out) == 4
        # pass lists
        out2 = beta.rolling_beta([0.01, 0.02, 0.0], [0.01, 0.015, 0.005], window=2)
        assert len(out2) == 3
        # force exceptions in both tries -> fallback empty/NaN
        class Bad:
            def __len__(self):
                raise TypeError()
            def __iter__(self):
                raise TypeError()
        out3 = beta.rolling_beta(Bad(), Bad())
        assert hasattr(out3, '__len__')

    def test_calculate_beta_alignment_and_truncation(self):
        # different lengths, lists
        a = [0.01, 0.02, -0.01, 0.03, 0.0]
        b = [0.01, 0.02, -0.01]
        res = beta.calculate_beta(a, b)
        assert isinstance(res, float) or np.isnan(res)
        # Series + ndarray mixing
        res2 = beta.calculate_beta(pd.Series([0.01,0.02,0.03,0.04]), np.array([0.01,0.015,0.025,0.035]))
        assert np.isfinite(res2)
        # all non-finite after mask
        res3 = beta.calculate_beta([np.nan, np.inf], [1.0, 2.0])
        assert np.isnan(res3)
        # min_obs larger than available
        res4 = beta.calculate_beta([0.01,0.02],[0.01,0.02], min_obs=10)
        assert np.isnan(res4)

    def test_calculate_beta_fast_branches(self):
        res = beta.calculate_beta_fast([0.01, np.nan, 0.02], [0.01, 0.02, 0.03])
        assert np.isfinite(res)
        res2 = beta.calculate_beta_fast([np.nan, np.inf], [1.0, np.nan])
        assert np.isnan(res2)
        res3 = beta.calculate_beta_fast([], [])
        # may be nan or 0.0
        assert isinstance(res3, float)
        res4 = beta.calculate_beta_fast([0.01,0.02],[0.01,0.02], min_obs=5)
        assert np.isnan(res4)
        res5 = beta.calculate_beta_fast([0.01, 0.02, -0.01], [0.005, 0.005, 0.005])
        assert res5 == 0.0
        class BadArr:
            def __array__(self, *args, **kwargs):
                raise ValueError()
        res6 = beta.calculate_beta_fast(BadArr(), BadArr())
        assert res6 == 0.0

    def test_calculate_rolling_beta_edge_cases(self):
        df = pd.DataFrame({'MKT': [np.nan, np.inf], 'A': [0.01, 0.02]})
        with pytest.raises(BABDataError):
            beta.calculate_rolling_beta(df, 'MKT')
        df2 = pd.DataFrame({
            'MKT': [0.01, 0.02, -0.01, 0.03, 0.0, 0.01]*15,
            'A':   [np.nan, 0.02, -0.01, 0.03, 0.0, 0.01]*15,
            'B':   [0.01, 0.02, -0.01, 0.03, 0.0, 0.01]*15,
        })
        res = beta.calculate_rolling_beta(df2, 'MKT', window=60, min_obs=30)
        assert 'A' in res.columns
        df3 = pd.DataFrame({
            'MKT': [0.01, 0.02, -0.01, 0.03]*100,
            'A':   [0.015, 0.025, -0.005, 0.035]*100,
        })
        res3 = beta.calculate_rolling_beta(df3, 'MKT')
        assert 'A' in res3.columns
