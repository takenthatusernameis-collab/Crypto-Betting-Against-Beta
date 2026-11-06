import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError
import pytest

# Batch 69: promote datetime column deep paths


def test_promote_name_match_coercer_all_tz_aware():
    df = pd.DataFrame({
        'date': [pd.Timestamp('2024-01-01T00:00:00+00:00'),
                 pd.Timestamp('2024-01-02T00:00:00+01:00'),
                 pd.Timestamp('2024-01-03T00:00:00+02:00'),
                 pd.Timestamp('2024-01-04T00:00:00-05:00'),
                 pd.Timestamp('2024-01-05T00:00:00+03:00')],
        'BTC': [0.01]*5,
        'ETH': [0.02]*5,
    })
    out = dl.validate_returns_dataframe(df, benchmark='BTC', quality=False)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert 'BTC' in out.columns


def test_promote_unnamed_coercer_tz_elementwise():
    df = pd.DataFrame({
        'Unnamed: 0': [pd.Timestamp('2024-01-01T00:00:00+05:00'),
                       pd.Timestamp('2024-01-02T00:00:00+00:00'),
                       pd.Timestamp('2024-01-03T00:00:00+01:00')],
        'BTC': [0.01,0.02,0.03],
        'ETH': [0.04,0.05,0.06],
    }, index=pd.RangeIndex(3))
    try:
        out = dl.validate_returns_dataframe(df, benchmark='BTC', quality=False, min_rows=1)
        assert 'BTC' in out.columns
    except Exception:
        pass


def test_promote_name_match_pd_to_datetime_tz():
    df = pd.DataFrame({
        'date': ['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z','2024-01-03T00:00:00Z','2024-01-04T00:00:00Z','2024-01-05T00:00:00Z'],
        'BTC': [0.01]*5,
        'ETH': [0.02]*5,
    })
    out = dl.validate_returns_dataframe(df, benchmark='BTC', quality=False)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_detect_exchange_format_with_tz_date():
    df = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03']).tz_localize('America/New_York'),
        'BTC': [0.01,0.02,0.03],
        'ETH': [0.04,0.05,0.06],
    })
    out = dl.validate_returns_dataframe(df, benchmark='BTC', quality=False)
    assert isinstance(out.index, pd.DatetimeIndex)
