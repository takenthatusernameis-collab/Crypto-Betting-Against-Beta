"""Data loader edge cases: percent signs, mixed strings, unparseable dates.

Extends the existing robustness tests with deterministic, offline coverage of
the numeric coercion and index normalization paths.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import BABDataError, validate_returns_dataframe


def test_coerce_numeric_percent_signs(tmp_path):
    """Percent strings like '1.5%' should be coerced to 0.015."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({
        "BTC": ["1.0%", "-0.5%", "2.0%"],
        "ETH": ["0.0%", "0.5%", "-1.0%"],
    }, index=dates)
    p = tmp_path / "pct.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert np.isfinite(res.values).all()
    assert np.isclose(res.loc[dates[0], "BTC"], 0.01)
    assert np.isclose(res.loc[dates[1], "BTC"], -0.005)
    assert np.isclose(res.loc[dates[2], "ETH"], -0.01)


def test_coerce_numeric_mixed_string_numbers(tmp_path):
    """Numeric strings like '0.02' should be coerced to floats."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({
        "BTC": ["0.01", "0.02", "0.03"],
        "ETH": [0.0, -0.01, 0.02],
    }, index=dates)
    p = tmp_path / "str.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert np.isfinite(res.values).all()
    assert np.isclose(res.loc[dates[0], "BTC"], 0.01)


def test_coerce_numeric_unparseable_raises(tmp_path):
    """Truly unparseable strings must raise BABDataError."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({
        "BTC": ["0.01", "not_a_number", "0.03"],
        "ETH": [0.0, 0.01, 0.02],
    }, index=dates)
    p = tmp_path / "bad.csv"
    df.to_csv(p)
    try:
        data_loader.load_returns_from_csv(p)
        assert False, "Should have raised"
    except BABDataError:
        pass


def test_normalize_index_timezone_aware_utc(tmp_path):
    """Timezone-aware UTC index should be normalized to naive UTC."""
    dates = pd.date_range("2023-01-01", periods=3, tz="UTC")
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=dates)
    p = tmp_path / "tz.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert res.index.tz is None
    assert isinstance(res.index, pd.DatetimeIndex)
    assert res.index.is_monotonic_increasing


def test_normalize_index_timezone_aware_non_utc(tmp_path):
    """Non-UTC timezone should be converted to UTC and stripped."""
    dates = pd.date_range("2023-01-01", periods=3, tz="US/Eastern")
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02]}, index=dates)
    p = tmp_path / "tz2.csv"
    df.to_csv(p)
    res = data_loader.load_returns_from_csv(p)
    assert res.index.tz is None
    assert isinstance(res.index, pd.DatetimeIndex)


def test_normalize_index_unparseable_raises():
    """An index that cannot be parsed as datetime must raise."""
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["not_a_date", "also_not"])
    try:
        validate_returns_dataframe(df)
        assert False, "Should have raised"
    except BABDataError:
        pass


def test_validate_rejects_infinite_values():
    """Inf values must be rejected."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, np.inf, 0.02], "ETH": [0.0, 0.01, 0.02]}, index=dates)
    try:
        validate_returns_dataframe(df)
        assert False, "Should have raised"
    except BABDataError:
        pass


def test_validate_rejects_all_nan_after_drop():
    """If all columns are NaN, validation must raise."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [np.nan] * 3, "ETH": [np.nan] * 3}, index=dates)
    try:
        validate_returns_dataframe(df)
        assert False, "Should have raised"
    except BABDataError:
        pass


def test_validate_duplicate_columns_raises():
    """Duplicate column names after normalization must raise."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame([[0.01, 0.02]] * 3, columns=["BTC", "BTC"], index=dates)
    try:
        validate_returns_dataframe(df)
        assert False, "Should have raised"
    except BABDataError:
        pass


def test_validate_insufficient_rows():
    """Fewer rows than min_rows must raise."""
    dates = pd.date_range("2023-01-01", periods=1)
    df = pd.DataFrame({"BTC": [0.01], "ETH": [0.02]}, index=dates)
    try:
        validate_returns_dataframe(df, min_rows=5)
        assert False, "Should have raised"
    except BABDataError:
        pass


def test_load_returns_dispatch_csv(tmp_path):
    """load_returns dispatches by extension."""
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, -0.01, 0.02], "ETH": [0.0, 0.01, -0.02]}, index=dates)
    p = tmp_path / "dispatch.csv"
    df.to_csv(p)
    res = data_loader.load_returns(p)
    assert isinstance(res, pd.DataFrame)
    assert not res.empty


def test_load_returns_unsupported_extension():
    """Unsupported extensions must raise."""
    try:
        data_loader.load_returns("foo.xyz")
        assert False, "Should have raised"
    except BABDataError:
        pass