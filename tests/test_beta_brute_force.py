import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_brute1():
    # rolling_beta: try to make all paths fail
    class X:
        def __init__(self):
            pass
        def __len__(self):
            raise RuntimeError()
    res = beta.rolling_beta(X(), X())
    assert isinstance(res, np.ndarray)


def test_brute2():
    # empty
    res = beta.rolling_beta([], [])
    assert isinstance(res, np.ndarray)
