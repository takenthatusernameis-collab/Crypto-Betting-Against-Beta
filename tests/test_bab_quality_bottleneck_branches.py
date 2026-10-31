"""Bottleneck branch coverage for quality.py.

Hits reachable uncovered branches left behind by the existing suite. Real
assertions on return values only. Unreachable paths (3-11 imports) left alone.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import quality as Q


def _idx(n=10):
    return pd.date_range("2020-01-01", periods=n)


class TestCheckDataQualityStrict:
    def test_strict_raises_on_missing(self):
        # quality.py:110-111 check_data_quality strict + has_issues -> ValueError
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=_idx(3))
        df.loc[df.index[0], "BTC"] = np.nan
        with pytest.raises(ValueError):
            Q.check_data_quality(df, strict=True)

    def test_non_strict_returns_bool(self):
        # quality.py:110-111 non-strict path returns bool
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=_idx(3))
        assert isinstance(Q.check_data_quality(df), bool)


class TestDetectGaps:
    def test_non_datetime_index(self):
        # quality.py:124-125 non-DatetimeIndex short-circuit
        df = pd.DataFrame({"BTC": [1, 2, 3]})
        assert Q.detect_gaps(df) == {"gaps": [], "count": 0}


class TestDetectOutliers:
    def test_bogus_method(self):
        # quality.py:145 else branch -> empty results
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04]}, index=_idx(4))
        res = Q.detect_outliers(df, method="bogus")
        assert res["BTC"] == {"outliers": [], "count": 0}

    def test_exception_fallback(self):
        # quality.py:187-188 bare except -> empty results
        df = pd.DataFrame({"BTC": [1, 2, 3]})
        res = Q.detect_outliers(df)
        assert res["BTC"]["count"] == 0


class TestDetectStaleData:
    def test_exception_fallback(self):
        # quality.py:192 bare except -> empty results
        df = pd.DataFrame({"BTC": [1, 2, 3]})
        res = Q.detect_stale_data(df)
        assert res["BTC"] == {"stale_runs": [], "count": 0}


class TestDetectVolumeAnomalies:
    def test_exception_fallback(self):
        # quality.py:211-212 bare except -> empty results
        df = pd.DataFrame({"BTC": [1, 2, 3]})
        res = Q.detect_volume_anomalies(df)
        assert res == {}

    def test_missing_volume_cols(self):
        # quality.py:216-217 col not in df.columns -> continue
        df = pd.DataFrame({"BTC": [1, 2, 3]})
        res = Q.detect_volume_anomalies(df, volume_cols=["nope"])
        assert res == {}


class TestDetectDuplicateTimestamps:
    def test_duplicates_present(self):
        # quality.py:245-246 has_duplicates True -> duplicates listed
        df = pd.DataFrame(
            {"BTC": [1, 2, 3]},
            index=pd.DatetimeIndex(["2020-01-01", "2020-01-01", "2020-01-02"]),
        )
        res = Q.detect_duplicate_timestamps(df)
        assert res["has_duplicates"] is True
        assert res["count"] == 2

    def test_no_has_duplicates_attr(self):
        # quality.py:250 fallback when index lacks has_duplicates
        df = pd.DataFrame({"BTC": [1, 2, 3]}, index=[0, 1, 2])
        res = Q.detect_duplicate_timestamps(df)
        assert res == {"has_duplicates": False, "count": 0}


class TestComputeQuality:
    def test_error_report(self):
        # quality.py:259-262 compute_quality on error report -> DataFrame
        out = Q.compute_quality(None)
        assert list(out.columns) == ["error"]
        assert out.iloc[0, 0] == "invalid_input"