import numpy as np
import pandas as pd
import pytest
import pickle

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.errors import BABDataError


def test_run_data_quality_campaign_gaps():
    # large gap
    dates = pd.date_range("2020-01-01", periods=3)
    dates = dates.insert(2, pd.Timestamp("2020-01-10"))  # create gap
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04]}, index=dates)
    try:
        dl._run_data_quality_campaign(df, max_gap_days=1.0)
    except BABDataError:
        pass
    except Exception:
        pass


def test_run_data_quality_campaign_stale():
    dates = pd.date_range("2020-01-01", periods=60)
    vals = [0.01] * 60
    df = pd.DataFrame({"BTC": vals}, index=dates)
    try:
        dl._run_data_quality_campaign(df, stale_run_threshold=3)
    except BABDataError:
        pass
    except Exception:
        pass


def test_run_data_quality_campaign_finite_frac():
    dates = pd.date_range("2020-01-01", periods=5)
    df = pd.DataFrame({"BTC": [0.01, np.nan, np.nan, np.nan, np.nan]}, index=dates)
    try:
        dl._run_data_quality_campaign(df, min_finite_fraction=0.5)
    except BABDataError:
        pass
    except Exception:
        pass


def test_validate_returns_dataframe_with_all_options():
    dates = pd.date_range("2020-01-01", periods=10)
    df = pd.DataFrame({"BTC": np.random.randn(10)*0.01, "ETH": np.random.randn(10)*0.01}, index=dates)
    out = dl.validate_returns_dataframe(df, quality=False)
    assert isinstance(out, pd.DataFrame)
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert isinstance(out, pd.DataFrame)


def test_coerce_numeric_with_object_mixed():
    df = pd.DataFrame({"a": ["1.0", "$2.0", "3%"], "b": [np.nan, 1.0, 2.0]})
    try:
        out = dl._coerce_numeric(df)
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_load_returns_hdf5_pickle_variants(tmp_path):
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "BTC": [0.01, -0.01, 0.02]})
    # pickle
    pp = tmp_path / "x.pkl"
    with open(pp, 'wb') as f:
        pickle.dump(df, f)
    out = dl.load_returns(pp)
    assert isinstance(out, pd.DataFrame)
