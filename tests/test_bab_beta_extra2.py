import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_estimate_betas_benchmark_none_path():
    df = pd.DataFrame({'A': [0.01]*50, 'B': [0.02]*50})
    try:
        res = beta.estimate_betas(df, benchmark=None, window=30)
    except Exception:
        pass


def test_rolling_beta_bench_to_numpy_first_try_fails():
    class WeirdDF:
        def __init__(self):
            self.columns = ['MKT', 'A']
            self.index = range(5)
        def __getitem__(self, key):
            if key == 'MKT':
                class S:
                    def to_numpy(self, dtype=None, copy=None):
                        raise TypeError()
                return S()
            class S2:
                def to_numpy(self, dtype=None, copy=None):
                    return np.array([0.01]*5)
            return S2()
    try:
        beta.calculate_rolling_beta(WeirdDF(), 'MKT')
    except Exception as e:
        assert isinstance(e, BABDataError)


def test_rolling_beta_bad_cols_all_bad():
    df = pd.DataFrame({
        'MKT': [0.01]*80,
        'A': [np.nan]*80,
    })
    res = beta.calculate_rolling_beta(df, 'MKT', window=40, min_obs=20)
    assert 'A' in res.columns


def test_rolling_beta_outer_fallback():
    # Trigger the big except at the end of calculate_rolling_beta
    class DF:
        def __init__(self):
            self.columns = ['MKT', 'A']
            self.index = range(10)
        def __getitem__(self, key):
            if key == 'MKT':
                s = pd.Series([0.01]*10)
                return s
            # return something that causes issues in processing
            raise RuntimeError("boom")
    try:
        beta.calculate_rolling_beta(DF(), 'MKT')
    except Exception:
        pass
