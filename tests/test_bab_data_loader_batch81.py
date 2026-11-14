import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


class RaisingTzDTI(pd.DatetimeIndex):
    @property
    def tz(self):
        raise RuntimeError("tz boom")


def test_713_714_normalize_index_tz_property_raises():
    idx = RaisingTzDTI(pd.to_datetime(["2024-01-01", "2024-01-02"]))
    df = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}, index=idx)
    out = dl.validate_returns_dataframe(df.copy(), benchmark="BTC", quality=False)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_733_734_promote_exchange_branch_tz_property_raises():
    orig_ex = dl._detect_and_normalize_exchange_format

    def fake_ex(df):
        out = df.copy()
        out.index = RaisingTzDTI(pd.to_datetime(["2024-01-01", "2024-01-02"]))
        return out

    dl._detect_and_normalize_exchange_format = fake_ex
    try:
        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        out = dl._promote_datetime_column(df.copy())
        assert isinstance(out.index, pd.DatetimeIndex)
    finally:
        dl._detect_and_normalize_exchange_format = orig_ex


class TzFailDTI(pd.DatetimeIndex):
    @property
    def tz(self):
        return "UTC"

    def tz_convert(self, *a, **k):
        raise RuntimeError("tz_convert boom")


def test_731_732_promote_exchange_branch_tz_convert_fails():
    orig_ex = dl._detect_and_normalize_exchange_format

    def fake_ex(df):
        out = df.copy()
        out.index = TzFailDTI(pd.to_datetime(["2024-01-01", "2024-01-02"]))
        return out

    dl._detect_and_normalize_exchange_format = fake_ex
    try:
        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        out = dl._promote_datetime_column(df.copy())
        assert isinstance(out.index, pd.DatetimeIndex)
    finally:
        dl._detect_and_normalize_exchange_format = orig_ex
