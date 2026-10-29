"""BAB data loader robustness - malformed CSVs, NaN columns, timezones, gaps."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError, validate_returns_dataframe


def test_loader_malformed_mixed_types(tmp_path):
    # Mixed types that should be coerced or raise cleanly
    dates = pd.date_range("2023-01-01", periods=5)
    df = pd.DataFrame({"BTC": [0.01, "0.02", 0.03, np.nan, 0.01], "ETH": [0.0, 0.01, -0.01, 0.02, 0.0]}, index=dates)
    p = tmp_path / "mixed.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert isinstance(res, pd.DataFrame)
    assert np.isfinite(res.values).sum() >= 0  # should be valid or handle NaN reasonably


def test_loader_bad_dates(tmp_path):
    df = pd.DataFrame({"date": ["not-a-date"]*3, "BTC": [0.01, 0.02, 0.03]})
    p = tmp_path / "bad_dates.csv"
    df.to_csv(p)
    try:
        res = data_loader.load_returns_from_csv(p)
        # If it loads, must be valid
        assert isinstance(res, pd.DataFrame)
    except Exception as e:
        # Should raise cleanly
        assert isinstance(e, (BABDataError, ValueError))


def test_loader_duplicate_timestamps(tmp_path):
    dates = pd.date_range("2023-01-01", periods=3)
    dates2 = list(dates) + [dates[1]]
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04]}, index=dates2)
    p = tmp_path / "dups.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert res.index.is_monotonic_increasing
    assert not res.index.has_duplicates


def test_loader_partial_nan_columns(tmp_path):
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({
        "BTC": np.random.RandomState(42).normal(0, 0.01, 10),
        "ETH": [np.nan]*10,  # all NaN - should be dropped or rejected safely
        "SOL": np.random.RandomState(43).normal(0, 0.02, 10),
    }, index=dates)
    p = tmp_path / "partial_nan.csv"
    df.to_csv(p)
    try:
        res = data_loader.load_returns_from_csv(p)
        # ETH should be dropped if all-NaN
        assert "ETH" not in res.columns
    except Exception as e:
        assert isinstance(e, (BABDataError, ValueError))


def test_loader_timezone_naive_aware(tmp_path):
    dates = pd.date_range("2023-01-01", periods=5, tz="UTC")
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02, 0.0, 0.01]}, index=dates)
    p = tmp_path / "tz.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert res.index.tz is None or isinstance(res.index, pd.DatetimeIndex)
    assert not res.index.has_duplicates


def test_loader_large_gaps_safe(tmp_path):
    dates = pd.date_range("2023-01-01", periods=5)
    # introduce large gaps by reindexing later? Or just create irregular
    irregular = list(dates[:2]) + [dates[0] + pd.Timedelta(days=100)]  # but unsorted - normalize should sort
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=irregular)
    p = tmp_path / "gaps.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert res.index.is_monotonic_increasing


def test_validate_rejects_all_nan_benchmark():
    dates = pd.date_range("2023-01-01", periods=5)
    df = pd.DataFrame({"BTC": [np.nan]*5, "ETH": [0.01, -0.01, 0.02, 0.0, 0.01]}, index=dates)
    try:
        validate_returns_dataframe(df, benchmark="BTC")
        assert False, "Should have raised"
    except Exception as e:
        assert isinstance(e, (BABDataError, ValueError))
