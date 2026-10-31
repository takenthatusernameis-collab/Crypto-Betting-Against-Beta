"""Bottleneck branch coverage for quality.py.

Hits reachable uncovered branches left behind by the existing suite: gap
early return on a NaT index, unknown outlier method, volume anomaly short
and zero-median paths, and compute_quality on None / empty frame. Real
assertions only. Unreachable paths left alone per the no-spinning rule.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta.quality import (
    compute_quality,
    detect_gaps,
    detect_outliers,
    detect_volume_anomalies,
)


class TestDetectGaps:
    def test_nat_index_median_gap_na_early_return(self):
        # quality.py:131-132 median_gap NaN -> early return
        idx = pd.DatetimeIndex(["2024-01-01", pd.NaT, "2024-01-03"])
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]}, index=idx)
        res = detect_gaps(df)
        assert res == {"gaps": [], "count": 0}


class TestDetectOutliers:
    def test_unknown_method_returns_empty(self):
        # quality.py:185-188 else branch for unsupported method
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 100.0]})
        res = detect_outliers(df, method="bogus")
        assert res == {"a": {"outliers": [], "count": 0}}


class TestDetectVolumeAnomalies:
    def test_fewer_than_three_finite_early_return(self):
        # quality.py:229-231 fewer than 3 finite values
        df = pd.DataFrame({"volume": [1.0, np.nan]})
        res = detect_volume_anomalies(df)
        assert res == {"volume": {"anomalies": [], "count": 0}}

    def test_zero_median_early_return(self):
        # quality.py:233-235 median volume is zero
        df = pd.DataFrame({"volume": [0.0, 0.0, 0.0, 1.0]})
        res = detect_volume_anomalies(df)
        assert res == {"volume": {"anomalies": [], "count": 0}}


class TestComputeQuality:
    def test_none_returns_error_dataframe(self):
        # quality.py:265-266 invalid input -> error DataFrame
        res = compute_quality(None)
        assert isinstance(res, pd.DataFrame)
        assert res["error"].tolist() == ["invalid_input"]

    def test_empty_dataframe_returns_empty(self):
        # quality.py:288-289 no column results -> empty DataFrame
        df = pd.DataFrame()
        res = compute_quality(df)
        assert res.empty
