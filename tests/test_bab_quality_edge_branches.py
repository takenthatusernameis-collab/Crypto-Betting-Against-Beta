"""Targeted edge-branch coverage for quality.py (P0, 92%).

Hits gap/duplicate/stale/inf/empty-report branches the existing suite does
not reach. Real assertions on report structure and quality scores only.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import quality


class TestDataQualityReport:
    def test_datetime_index_median_gap_nan(self):
        # DatetimeIndex with NaT -> median gap NaT -> gaps count/large 0 (quality.py:30)
        idx = pd.DatetimeIndex(["2024-01-01", pd.NaT, "2024-01-03"])
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]}, index=idx)
        report = quality.data_quality_report(df)
        assert report["index"]["gaps"] == {"count": 0, "large_gaps": 0}

    def test_column_to_numeric_failure(self):
        # Unparseable object column -> all-NaN fallback arr (quality.py:47-48)
        df = pd.DataFrame({"a": ["x", "y", "z"]})
        report = quality.data_quality_report(df)
        assert report["columns"][0]["missing"] == 3
        assert report["columns"][0]["min"] is None

    def test_inf_penalty_applied(self):
        # Column with inf -> missing_pct penalty then inf penalty (quality.py:275)
        df = pd.DataFrame({"a": [1.0, 2.0, np.inf]})
        report = quality.data_quality_report(df)
        assert report["columns"][0]["inf"] == 1
        q = quality.compute_quality(df)
        assert q.loc[q["column"] == "a", "quality_score"].iloc[0] < 1.0

    def test_stale_penalty_applied(self):
        # >5% consecutive equal values -> stale penalty (quality.py:279)
        df = pd.DataFrame({"a": [1.0, 1.0, 1.0, 1.0, 2.0]})
        q = quality.compute_quality(df)
        assert q.loc[q["column"] == "a", "quality_score"].iloc[0] < 1.0

    def test_empty_dataframe_returns_empty_frame(self):
        # No columns -> empty results -> empty DataFrame (quality.py:289)
        df = pd.DataFrame()
        q = quality.compute_quality(df)
        assert q.empty


class TestDetectGaps:
    def test_duplicate_timestamps_median_gap_zero(self):
        # All diffs zero -> median 0 -> early empty return (quality.py:132)
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-01", "2024-01-01"])
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]}, index=idx)
        assert quality.detect_gaps(df) == {"gaps": [], "count": 0}

    def test_non_datetime_index(self):
        df = pd.DataFrame({"a": [1.0, 2.0]}, index=[0, 1])
        assert quality.detect_gaps(df) == {"gaps": [], "count": 0}


class TestDetectDuplicateTimestamps:
    def test_index_without_has_duplicates(self):
        # RangeIndex lacks has_duplicates -> early return (quality.py:259)
        df = pd.DataFrame({"a": [1.0, 2.0]}, index=pd.RangeIndex(2))
        assert quality.detect_duplicate_timestamps(df) == {"has_duplicates": False, "count": 0}

    def test_duplicate_timestamps_reported(self):
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-01", "2024-01-02"])
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]}, index=idx)
        res = quality.detect_duplicate_timestamps(df)
        assert res["has_duplicates"] is True
        assert res["count"] == 2


class TestDetectStaleData:
    def test_stale_run_at_end_recorded(self):
        # Terminal run meeting threshold appended (quality.py:209)
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 3.0, 3.0]})
        res = quality.detect_stale_data(df, threshold=3)
        assert res["a"]["count"] == 1
        assert res["a"]["stale_runs"][0]["length"] == 3

    def test_no_stale(self):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
        res = quality.detect_stale_data(df, threshold=3)
        assert res["a"]["count"] == 0
