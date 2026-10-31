"""More precision hits for quality."""
from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import quality


def test_data_quality_report_conversion_error():
    class Weird:
        pass
    df = pd.DataFrame({"WEIRD": [Weird(), Weird(), Weird()]}, index=pd.date_range("2023-01-01", periods=3))
    report = quality.data_quality_report(df)
    assert "columns" in report


def test_check_data_quality_strict_error_branch():
    try:
        quality.check_data_quality(None, strict=True)
    except ValueError:
        pass


def test_detect_gaps_zero_median_case():
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=pd.to_datetime(["2023-01-01", "2023-01-01", "2023-01-01"]))
    res = quality.detect_gaps(df)
    assert isinstance(res, dict)


def test_detect_outliers_method_unknown():
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04, 10.0]})
    res = quality.detect_outliers(df, method="mad")
    assert "BTC" in res


def test_detect_outliers_exception_path():
    class Weird:
        pass
    df = pd.DataFrame({"WEIRD": [Weird(), Weird(), Weird()]})
    res = quality.detect_outliers(df)
    assert "WEIRD" in res


def test_detect_stale_data_long_run():
    df = pd.DataFrame({"BTC": [0.01] * 10})
    res = quality.detect_stale_data(df, threshold=3)
    assert res["BTC"]["count"] >= 1


def test_detect_volume_anomalies_exception():
    class Weird:
        pass
    df = pd.DataFrame({"volume": [Weird()] * 5})
    res = quality.detect_volume_anomalies(df)
    assert isinstance(res, dict)


def test_detect_duplicate_timestamps_no_attr():
    df = pd.DataFrame({"BTC": [0.01, 0.02]})
    df.index = [0, 1]
    res = quality.detect_duplicate_timestamps(df)
    assert res["has_duplicates"] is False


def test_compute_quality_with_outliers_and_stale():
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({"BTC": [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, -0.01, 0.03, 0.5]}, index=dates)
    res = quality.compute_quality(df)
    assert isinstance(res, pd.DataFrame)
