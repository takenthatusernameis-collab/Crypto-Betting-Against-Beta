import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_promote_with_open_time_epoch_ms():
    df = pd.DataFrame({"Open time": [1600000000000, 1600000060000], "Close": [100, 101]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_detect_coingecko_style():
    df = pd.DataFrame(
        {
            "snapped_at": ["2020-01-01T00:00:00Z", "2020-01-02T00:00:00Z"],
            "price": [10, 11],
            "market_cap": [1, 2],
        }
    )
    out = dl._detect_and_normalize_exchange_format(df)
    assert isinstance(out, pd.DataFrame)


def test_load_returns_from_dataframe(tmp_path):
    df = pd.DataFrame(
        {"date": pd.date_range("2020-01-01", periods=5), "BTC": [0.01, -0.01, 0.0, 0.02, -0.005]}
    )
    out = dl.load_returns(df)
    assert isinstance(out, pd.DataFrame)
    out2 = dl.load_prices(df.rename(columns={"BTC": "price"}))
    assert isinstance(out2, pd.DataFrame)


def test_validate_bad_benchmark():
    df = pd.DataFrame(
        {"date": pd.date_range("2020-01-01", periods=5), "BTC": [0.01, -0.01, 0.0, 0.02, -0.005]}
    )
    with pytest.raises(BABDataError):
        dl.validate_returns_dataframe(df, benchmark="ETH")
