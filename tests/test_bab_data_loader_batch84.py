import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


class SetterCounterDF(pd.DataFrame):
    _n = 0
    @property
    def _constructor(self):
        return SetterCounterDF
    @property
    def index(self):
        return super().index
    @index.setter
    def index(self, v):
        SetterCounterDF._n += 1
        if SetterCounterDF._n >= 2:
            raise RuntimeError("index setter boom")
        super().__setattr__('index', v)


def test_194_196_numeric_index_setter_raises():
    """Lines 194, 196: numeric index where pd.to_datetime(unit=) fails and index setter raises."""
    df = SetterCounterDF({'BTC': [0.01, 0.02]}, index=pd.Index([1700000000.0, float('nan')], dtype='float64'))
    SetterCounterDF._n = 0
    with pytest.raises(Exception):
        dl._normalize_index(df.copy())