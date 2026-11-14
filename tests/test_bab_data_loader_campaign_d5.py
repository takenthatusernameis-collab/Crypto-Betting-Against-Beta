"""Campaign D5 hardening tests for data_loader.py: coercer, quality campaign,
promotion, exchange detection, and normalize_index error paths.

Targets uncovered branches across _coerce_numeric, _run_data_quality_campaign,
_promote_datetime_column, _detect_and_normalize_exchange_format, and
_normalize_index (unparseable -> BABDataError). No public API changes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    _coerce_to_datetime_scalar,
    _detect_and_normalize_exchange_format,
    _normalize_index,
    _promote_datetime_column,
    _run_data_quality_campaign,
)

# ---------------------------------------------------------------------------
# _coerce_numeric
# ---------------------------------------------------------------------------


def test_coerce_numeric_non_dataframe_raises_babdataerror():
    with pytest.raises(BABDataError):
        _coerce_numeric([1, 2, 3])


def test_coerce_numeric_uncoercible_garbage_raises():
    df = pd.DataFrame(
        {"BTC": ["garbage", "also-bad"]}, index=pd.date_range("2023-01-01", periods=2)
    )
    with pytest.raises(BABDataError, match="Non-numeric"):
        _coerce_numeric(df)


def test_coerce_numeric_mixed_numeric_and_garbage_raises():
    df = pd.DataFrame({"BTC": [0.01, "not-a-number"]}, index=pd.date_range("2023-01-01", periods=2))
    with pytest.raises(BABDataError, match="Non-numeric"):
        _coerce_numeric(df)


def test_coerce_numeric_commas_and_units_stripped():
    df = pd.DataFrame(
        {"BTC": ["1,234.5", "2,500.25"]}, index=pd.date_range("2023-01-01", periods=2)
    )
    out = _coerce_numeric(df)
    assert out["BTC"].iloc[0] == pytest.approx(1234.5)
    assert out["BTC"].iloc[1] == pytest.approx(2500.25)


def test_coerce_numeric_inf_and_nan_preserved():
    df = pd.DataFrame(
        {"BTC": [0.01, float("inf"), float("nan")]}, index=pd.date_range("2023-01-01", periods=3)
    )
    out = _coerce_numeric(df)
    assert np.isinf(out["BTC"].iloc[1])
    assert np.isnan(out["BTC"].iloc[2])


def test_coerce_numeric_already_float_passthrough():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
    out = _coerce_numeric(df)
    assert out["BTC"].dtype == np.float64


# ---------------------------------------------------------------------------
# _run_data_quality_campaign
# ---------------------------------------------------------------------------


def test_quality_none_raises():
    with pytest.raises(BABDataError, match="None"):
        _run_data_quality_campaign(None)


def test_quality_empty_raises():
    with pytest.raises(BABDataError, match="empty"):
        _run_data_quality_campaign(pd.DataFrame())


def test_quality_not_dataframe_raises():
    with pytest.raises(BABDataError, match="None"):
        _run_data_quality_campaign([1, 2, 3])


def test_quality_duplicate_timestamps_raises():
    idx = pd.DatetimeIndex(["2023-01-01", "2023-01-01", "2023-01-02"])
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    with pytest.raises(BABDataError, match="Duplicate"):
        _run_data_quality_campaign(df)


def test_quality_duplicate_timestamps_allowed_drops():
    idx = pd.DatetimeIndex(["2023-01-01", "2023-01-01", "2023-01-02"])
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    out = _run_data_quality_campaign(df, allow_duplicate_timestamps=True)
    assert len(out) == 2


def test_quality_implausible_return_raises():
    df = pd.DataFrame({"BTC": [0.01, 50000.0]}, index=pd.date_range("2023-01-01", periods=2))
    with pytest.raises(BABDataError, match="Implausible"):
        _run_data_quality_campaign(df, max_return_abs=100.0)


def test_quality_large_gap_raises():
    idx = pd.DatetimeIndex(["2023-01-01", "2023-02-01"])
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
    with pytest.raises(BABDataError, match="gap too large"):
        _run_data_quality_campaign(df, max_gap_days=5.0)


def test_quality_min_finite_fraction_raises():
    df = pd.DataFrame({"BTC": [0.01, np.nan, np.nan]}, index=pd.date_range("2023-01-01", periods=3))
    with pytest.raises(BABDataError, match="insufficient finite"):
        _run_data_quality_campaign(df, min_finite_fraction=0.9)


def test_quality_stale_run_raises():
    arr = [0.01] * 60
    df = pd.DataFrame({"BTC": arr}, index=pd.date_range("2023-01-01", periods=60))
    with pytest.raises(BABDataError, match="Stale"):
        _run_data_quality_campaign(df, stale_run_threshold=50)


def test_quality_stale_run_below_threshold_passes():
    arr = [0.01] * 10
    df = pd.DataFrame({"BTC": arr}, index=pd.date_range("2023-01-01", periods=10))
    out = _run_data_quality_campaign(df, stale_run_threshold=50)
    assert len(out) == 10


def test_quality_all_nan_column_passes_lenient():
    df = pd.DataFrame({"BTC": [np.nan, np.nan]}, index=pd.date_range("2023-01-01", periods=2))
    # min_finite_fraction defaults to 0.0, so all-NaN is leniently allowed.
    out = _run_data_quality_campaign(df)
    assert len(out) == 2


# ---------------------------------------------------------------------------
# _promote_datetime_column
# ---------------------------------------------------------------------------


def test_promote_datetime_column_already_datetimeindex_passthrough():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)


def test_promote_datetime_column_unnamed_column_promotes():
    df = pd.DataFrame({"": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert "BTC" in out.columns


def test_promote_datetime_column_no_date_column_returns_unchanged():
    df = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [0.05, 0.06]})
    out = _promote_datetime_column(df)
    assert list(out.columns) == ["BTC", "ETH"]


def test_promote_datetime_column_tz_aware_index_normalized():
    idx = pd.date_range("2023-01-01", periods=3, tz="US/Eastern")
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    out = _promote_datetime_column(df)
    assert out.index.tz is None


# ---------------------------------------------------------------------------
# _detect_and_normalize_exchange_format
# ---------------------------------------------------------------------------


def test_exchange_format_empty_returns_unchanged():
    df = pd.DataFrame()
    out = _detect_and_normalize_exchange_format(df)
    assert out.empty


def test_exchange_format_non_dataframe_returns_unchanged():
    out = _detect_and_normalize_exchange_format([1, 2, 3])
    assert out == [1, 2, 3]


# ---------------------------------------------------------------------------
# _normalize_index error paths
# ---------------------------------------------------------------------------


def test_normalize_index_unparseable_raises_babdataerror():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["not-a-date", "also-not-a-date"])
    with pytest.raises(BABDataError, match="could not be parsed"):
        _normalize_index(df)


def test_normalize_index_mixed_unparseable_raises():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["2023-01-01", "garbage"])
    with pytest.raises(BABDataError):
        _normalize_index(df)


# ---------------------------------------------------------------------------
# _coerce_to_datetime_scalar additional edge cases
# ---------------------------------------------------------------------------


def test_coerce_scalar_bool_treated_as_int():
    # bool is a subclass of int; True == 1 second epoch.
    out = _coerce_to_datetime_scalar(True)
    assert isinstance(out, pd.Timestamp)


def test_coerce_scalar_list_coerced_elementwise():
    # A list falls through to pd.to_datetime elementwise parsing.
    out = _coerce_to_datetime_scalar(["2023-01-01", "2023-01-02"])
    assert isinstance(out, pd.DatetimeIndex)
