"""P8: data freshness & staleness guard tests (validate_freshness)."""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import BABDataError, validate_freshness


def _frame(dates):
    return pd.DataFrame({"BTC": np.random.rand(len(dates))}, index=pd.DatetimeIndex(dates))


def test_freshness_passes_for_fresh_data():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    ref = pd.Timestamp("2024-01-10")
    assert (
        validate_freshness(_frame(dates), max_staleness_days=2, max_gap_days=7, reference_date=ref)
        is True
    )


def test_freshness_boundary_last_date_equals_reference():
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    ref = pd.Timestamp("2024-01-03")  # staleness == 0 <= 2
    assert validate_freshness(_frame(dates), max_staleness_days=2, reference_date=ref) is True


def test_freshness_fails_when_stale_beyond_max_staleness_days():
    dates = pd.date_range("2024-01-01", periods=5, freq="D")  # last = 2024-01-05
    ref = pd.Timestamp("2024-01-10")  # staleness == 5 days > 2
    with pytest.raises(BABDataError):
        validate_freshness(_frame(dates), max_staleness_days=2, reference_date=ref)


def test_freshness_fails_on_gap_beyond_max_gap_days():
    dates = pd.DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-10"])  # 8-day gap > 7
    ref = pd.Timestamp("2024-01-10")
    with pytest.raises(BABDataError):
        validate_freshness(
            pd.DataFrame({"BTC": [1.0, 2.0, 3.0]}, index=dates),
            max_gap_days=7,
            reference_date=ref,
        )


def test_freshness_gap_at_boundary_passes():
    dates = pd.DatetimeIndex(["2024-01-01", "2024-01-08"])  # exactly 7-day gap == max
    ref = pd.Timestamp("2024-01-08")
    assert validate_freshness(
        pd.DataFrame({"BTC": [1.0, 2.0]}, index=dates),
        max_gap_days=7,
        reference_date=ref,
    ) is True


def test_freshness_default_reference_now_passes_recent_data():
    today = pd.Timestamp.utcnow().normalize()
    dates = pd.date_range(today - pd.Timedelta(days=1), periods=2, freq="D")
    assert validate_freshness(_frame(dates), max_staleness_days=2, max_gap_days=7) is True


def test_freshness_default_reference_now_fails_stale_data():
    dates = pd.date_range("2020-01-01", periods=5, freq="D")  # years stale
    with pytest.raises(BABDataError):
        validate_freshness(_frame(dates), max_staleness_days=2)


def test_freshness_empty_or_short_data_passes():
    assert validate_freshness(pd.DataFrame(), max_staleness_days=2) is True
    single = pd.DataFrame({"BTC": [1.0]}, index=pd.DatetimeIndex(["2024-01-01"]))
    assert validate_freshness(single, max_staleness_days=2) is True
