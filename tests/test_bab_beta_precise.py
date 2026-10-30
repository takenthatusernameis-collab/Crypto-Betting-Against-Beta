import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_estimate_betas_benchmark_none_and_minobs_clamps():
    returns = pd.DataFrame({
        'A': [0.01]*100,
        'B': [0.02]*100,
    })
    # window None
    res = beta.estimate_betas(returns, benchmark='A', window=60, min_obs=None)
    assert isinstance(res, pd.DataFrame)
    # min_obs > window
    res = beta.estimate_betas(returns, benchmark='A', window=5, min_obs=10)
    assert isinstance(res, pd.DataFrame)


def test_rolling_beta_all_paths():
    a = pd.Series([0.01,0.02,0.03,0.04,0.05])
    b = pd.Series([0.01,0.015,0.025,0.035,0.045])
    out = beta.rolling_beta(a,b,window=3)
    assert hasattr(out, '__len__')
    out = beta.rolling_beta(np.array([0.01,0.02,0.03]), np.array([0.01,0.01,0.01]), window=2)
    assert len(out)==3


def test_calculate_beta_y_x_none_and_edge():
    res = beta.calculate_beta([1,2,3,4], [1,2,3])
    assert isinstance(res, float)
    res = beta.calculate_beta([np.nan], [np.nan])
    assert np.isnan(res)
