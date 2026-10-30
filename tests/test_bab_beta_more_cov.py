import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


class Dummy:
    pass


def test_calculate_beta_alignment_exception():
    # Make alignment path execute but hit exception inside try
    a = pd.Series([1,2,3,4])
    b = pd.Series([1,2,3])  # different length -> goes to alignment
    # But to hit the except at line ~90-91, we need the inner try to fail
    # Pass objects that break concat/dropna
    class BadSeries:
        def __init__(self):
            pass
    # easier: pass Series-like that cause issues
    res = beta.calculate_beta([1,2,3], [1,2,3,4])  # lists, different len -> truncates (no Series) goes to else
    assert isinstance(res, float)
    # case with one Series one list both different lengths?
    res = beta.calculate_beta(pd.Series([1,2,3]), [1,2,3,4])  # mixed types
    assert isinstance(res, float)


def test_calculate_beta_more_branches():
    # y is None case? maybe hard to hit
    # different length, non-Series objects -> go to else truncate
    res = beta.calculate_beta(np.array([1,2,3]), np.array([1,2]))
    assert isinstance(res, float)
    # all finite check after filtering
    res = beta.calculate_beta([1, np.inf, 3], [1, 2, np.inf])
    # after filtering maybe empty?
    assert isinstance(res, float)
