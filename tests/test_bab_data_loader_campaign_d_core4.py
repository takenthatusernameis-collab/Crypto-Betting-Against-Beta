import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_normalize_index_non_numeric_object_with_dates():
    df = pd.DataFrame({"ret": [0.01, 0.02]}, index=["2020-01-01", "2020-01-02"])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_coerce_to_datetime_scalar_large_ns_us():
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000000000))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000000))
    assert not pd.isna(dl._coerce_to_datetime_scalar(1600000000000.5))


def test_promote_long_format_pivot():
    df = pd.DataFrame({
        "symbol": ["BTC", "BTC", "ETH", "ETH"],
        "date": ["2020-01-01", "2020-01-02", "2020-01-01", "2020-01-02"],
        "close": [100, 101, 10, 11]
    })
    out = dl._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_strip_units_euro_decimal():
    v = dl._strip_units_and_parse("1.000,50")
    assert abs(v - 1000.5) < 1e-9


def test_validate_quality_campaign(tmp_path):
    dates = pd.date_range("2020-01-01", periods=5)
    df = pd.DataFrame({"BTC": [0.01,0.02,-0.01,0.0,0.01]}, index=dates)
    out = dl.validate_returns_dataframe(df)
    assert isinstance(out, pd.DataFrame)
