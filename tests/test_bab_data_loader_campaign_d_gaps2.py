import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_normalize_index_mixed_datetime_and_numeric():
    df = pd.DataFrame({"r": [0.01, 0.02]}, index=[pd.Timestamp("2020-01-01"), 1600000000000])
    out = dl._normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_unnamed_column_epoch():
    df = pd.DataFrame({"": [1600000000000, 1600000060000], "BTC": [100, 101]})
    out = dl._promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_coerce_to_datetime_scalar_dayfirst():
    # string that needs dayfirst
    v = dl._coerce_to_datetime_scalar("01/02/2020")
    assert not pd.isna(v)


def test_load_prices_from_json(tmp_path):
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "close": [10, 11, 12]})
    pj = tmp_path / "p.json"
    df.to_json(pj, orient="records", date_format="iso")
    out = dl.load_prices(pj)
    assert isinstance(out, pd.DataFrame)


def test_validate_empty_after_clean():
    df = pd.DataFrame(
        {"date": pd.date_range("2020-01-01", periods=3), "X": [np.nan, np.nan, np.nan]}
    )
    with pytest.raises(BABDataError):
        dl.validate_returns_dataframe(df)
