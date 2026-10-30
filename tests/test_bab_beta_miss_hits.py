import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_rolling_beta_fallback_arr_fails_both():
    class Bad:
        def __init__(self):
            pass
        def __len__(self):
            raise TypeError()
        def __iter__(self):
            raise TypeError()
    out = beta.rolling_beta(Bad(), Bad(), window=3)
    assert isinstance(out, np.ndarray)


def test_calculate_beta_alignment_inner_exception():
    a = pd.Series([1.0, 2.0, 3.0, 4.0])
    res = beta.calculate_beta(a, [1.0, 2.0, 3.0])
    assert isinstance(res, float)


def test_calculate_beta_nonfinite_all_masked():
    res = beta.calculate_beta([np.inf, -np.inf], [1.0, 2.0])
    assert np.isnan(res)


def test_calculate_beta_linalg_error():
    res = beta.calculate_beta([np.nan, 1, 2], [0.5, 0.5, 0.5])
    assert isinstance(res, float)


def test_calculate_beta_fast_all_nonfinite_after_mask():
    res = beta.calculate_beta_fast([np.nan, np.inf], [np.nan, np.inf])
    assert np.isnan(res)


def test_calculate_beta_fast_linalg():
    res = beta.calculate_beta_fast([1,2,3], [5,5,5])
    assert res == 0.0


def test_calculate_rolling_beta_bench_arr_fallback():
    df = pd.DataFrame({'MKT': [0.01]*100, 'A': [0.01]*100})
    res = beta.calculate_rolling_beta(df, 'MKT', window=60, min_obs=30)
    assert isinstance(res, pd.DataFrame)


def test_calculate_rolling_beta_fallback_in_outer():
    df = pd.DataFrame({
        'MKT': [0.01]*50,
        'A': [np.nan]*50,
        'B': [0.02]*50,
    })
    res = beta.calculate_rolling_beta(df, 'MKT', window=30, min_obs=15)
    assert isinstance(res, pd.DataFrame)
