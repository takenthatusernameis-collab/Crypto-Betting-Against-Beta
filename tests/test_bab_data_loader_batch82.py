import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

orig_coerce = dl._coerce_to_datetime_scalar


class NoTzInfo:
    def __init__(self, ts):
        self._ts = ts
    def __str__(self):
        return str(self._ts)
    def __repr__(self):
        return f"NoTzInfo({self._ts})"


_counter = {'i': 0}
def no_tzinfo_coerce(v):
    _counter['i'] += 1
    return NoTzInfo(pd.Timestamp('2024-01-0' + str(_counter['i']), tz='UTC'))


def test_561_long_format_pivot_else_branch_tz():
    """Line 561: long-format pivot, pdv has no tzinfo attr but pd.Timestamp(pdv) is tz-aware."""
    dl._coerce_to_datetime_scalar = no_tzinfo_coerce
    _counter['i'] = 0
    try:
        df = pd.DataFrame({
            'symbol': ['BTC', 'BTC', 'ETH', 'ETH'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02'],
            'close': [100.0, 101.0, 200.0, 201.0],
        })
        out = dl._detect_and_normalize_exchange_format(df.copy())
        assert out is not None
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce


def test_620_ohlcv_wide_else_branch_tz():
    """Line 620: OHLCV wide format, pdv has no tzinfo attr but pd.Timestamp(pdv) is tz-aware."""
    dl._coerce_to_datetime_scalar = no_tzinfo_coerce
    _counter['i'] = 0
    try:
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'close': [100.0, 101.0],
            'high': [101.0, 102.0],
        })
        out = dl._detect_and_normalize_exchange_format(df.copy())
        assert out is not None
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce


def test_679_date_col_promotion_else_branch_tz():
    """Line 679: date_col promotion, pdv has no tzinfo attr but pd.Timestamp(pdv) is tz-aware."""
    dl._coerce_to_datetime_scalar = no_tzinfo_coerce
    _counter['i'] = 0
    try:
        df = pd.DataFrame({
            'date': [1700000000000, 1700000001000],
            'BTC': [0.01, 0.02],
            'ETH': [0.03, 0.04],
        })
        out = dl._detect_and_normalize_exchange_format(df.copy())
        assert out is not None
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce


def test_953_normalize_asset_name_empty_token():
    """Line 953: empty token after strip is skipped."""
    from strategies.betting_against_beta.data_loader import _normalize_asset_name
    assert _normalize_asset_name("BTC  ETH") == "BTC ETH"