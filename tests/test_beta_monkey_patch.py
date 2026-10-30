import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta


def test_align_except():
    orig_concat = pd.concat
    def bad_concat(*args, **kwargs):
        raise ValueError('x')
    pd.concat = bad_concat
    try:
        a = pd.Series([0.01,0.02,0.03])
        b = pd.Series([0.005,0.01,0.015,0.02], index=[1,2,3,4])
        res = beta.calculate_beta(a,b)
        assert np.isnan(res)
    finally:
        pd.concat = orig_concat


def test_calculate_beta_y_none_path():
    res = beta.calculate_beta(object(), object())
    assert np.isnan(res)
