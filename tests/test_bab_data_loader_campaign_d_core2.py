import os
import json
import pickle

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_normalize_index_empty_numeric_raises():
    df = pd.DataFrame({"ret": []}, index=pd.Index([], dtype=float))
    with pytest.raises(BABDataError):
        dl._normalize_index(df)


def test_coerce_to_datetime_scalar_float_int_variants():
    assert not pd.isna(dl._coerce_to_datetime_scalar(1_600_000_000.0))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1_600_000_000000.0))
    assert not pd.isna(dl._coerce_to_datetime_scalar(int(1_600_000_000)))
    assert not pd.isna(dl._coerce_to_datetime_scalar(int(1_600_000_000000)))
    assert not pd.isna(dl._coerce_to_datetime_scalar(int(1_600_000_0000000000)))


def test_promote_datetime_various():
    # coinbase/other
    df = pd.DataFrame({"time": ["2020-01-01", "2020-01-02"], "close": [10, 11]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    # timestamp
    df2 = pd.DataFrame({"timestamp": [1600000000, 1600000060], "price": [1,2]})
    out2 = dl._promote_datetime_column(df2)
    assert isinstance(out2.index, pd.DatetimeIndex)
    # unnamed single column
    df3 = pd.DataFrame({"": [1600000000, 1600000060], "BTC": [1,2]})
    out3 = dl._promote_datetime_column(df3)
    # may promote
    assert isinstance(out3, pd.DataFrame)
