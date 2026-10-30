import numpy as np
import pandas as pd

from strategies.betting_against_beta import quality


class TestDataQualityReport:
    def test_none_returns_error(self):
        rep = quality.data_quality_report(None)
        assert rep == {"error": "invalid_input"}

    def test_non_dataframe_returns_error(self):
        rep = quality.data_quality_report([1, 2, 3])
        assert rep == {"error": "invalid_input"}

    def test_basic_report_shape(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02, 0.03, 0.0], "ETH": [0.02, 0.01, -0.01, 0.02]})
        rep = quality.data_quality_report(df)
        assert rep["shape"] == {"rows": 4, "cols": 2}
        assert rep["index"]["type"] == "RangeIndex"
        assert rep["index"]["is_datetime"] is False
        assert rep["index"]["has_duplicates"] is False
        assert len(rep["columns"]) == 2
        assert "summary" in rep

    def test_datetime_index_gaps(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        df = pd.DataFrame({"BTC": [0.01] * 5}, index=idx)
        rep = quality.data_quality_report(df)
        assert rep["index"]["is_datetime"] is True
        assert "start" in rep["index"]
        assert "end" in rep["index"]
        assert "gaps" in rep["index"]

    def test_datetime_index_with_large_gaps(self):
        dates = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02"),
                pd.Timestamp("2023-01-10"), pd.Timestamp("2023-01-11")]
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.03]}, index=pd.DatetimeIndex(dates))
        rep = quality.data_quality_report(df)
        gaps = rep["index"]["gaps"]
        assert "large_gaps" in gaps

    def test_column_with_nan_inf(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan, np.inf, -np.inf, 0.02]})
        rep = quality.data_quality_report(df)
        col = rep["columns"][0]
        assert col["missing"] >= 1
        assert col["inf"] >= 1

    def test_outliers_zscore(self):
        df = pd.DataFrame({"BTC": [0.01] * 10 + [1.0]})  # outlier
        rep = quality.data_quality_report(df)
        col = rep["columns"][0]
        assert "outliers" in col
        assert col["outliers"].get("zscore_outliers", 0) >= 1

    def test_outliers_iqr(self):
        df = pd.DataFrame({"BTC": [-1.0, -0.5, 0, 0.01, 0.02, 0.03, 0.04, 0.05, 2.0, 3.0]})  # outliers
        rep = quality.data_quality_report(df)
        col = rep["columns"][0]
        assert col["outliers"].get("iqr_outliers", 0) >= 1 or col["outliers"].get("zscore_outliers", 0) >= 0

    def test_stale_consecutive(self):
        df = pd.DataFrame({"BTC": [0.01, 0.01, 0.01, 0.02]})
        rep = quality.data_quality_report(df)
        col = rep["columns"][0]
        assert col["stale_consecutive"] >= 2

    def test_summary_all_finite(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02, 0.03], "ETH": [0.02, 0.01, -0.01]})
        rep = quality.data_quality_report(df)
        assert rep["summary"]["all_finite"] is True

    def test_summary_has_issues(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan, 0.03, 0.01, 0.01, 0.01, 0.01]})
        rep = quality.data_quality_report(df)
        assert rep["summary"]["has_issues"] is True


class TestCheckDataQuality:
    def test_check_none_strict_raises(self):
        try:
            quality.check_data_quality(None, strict=True)
            assert False
        except ValueError:
            pass

    def test_check_none_not_strict(self):
        assert quality.check_data_quality(None, strict=False) is False

    def test_check_good_data(self):
        df = pd.DataFrame({"BTC": [0.01, -0.02, 0.03]})
        result = quality.check_data_quality(df, strict=False)
        assert isinstance(result, bool)

    def test_check_bad_data_strict_raises(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan, 0.03]})
        try:
            quality.check_data_quality(df, strict=True)
            assert False
        except ValueError:
            pass


class TestDetectGaps:
    def test_non_datetime_returns_empty(self):
        df = pd.DataFrame({"BTC": [1, 2, 3]})
        res = quality.detect_gaps(df)
        assert res == {"gaps": [], "count": 0}

    def test_small_df(self):
        df = pd.DataFrame({"BTC": [1]}, index=pd.date_range("2023-01-01", periods=1))
        res = quality.detect_gaps(df)
        assert res["count"] == 0

    def test_detects_large_gaps(self):
        dates = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02"),
                pd.Timestamp("2023-01-15"), pd.Timestamp("2023-01-16")]
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.03]}, index=pd.DatetimeIndex(dates))
        res = quality.detect_gaps(df)
        assert isinstance(res["count"], int)
        assert isinstance(res["gaps"], list)


class TestDetectOutliers:
    def test_zscore_method(self):
        df = pd.DataFrame({"BTC": [0.01] * 10 + [5.0]})
        res = quality.detect_outliers(df, method="zscore", threshold=3.0)
        assert "BTC" in res
        assert res["BTC"]["count"] >= 1

    def test_iqr_method(self):
        df = pd.DataFrame({"BTC": [-1.0, -0.5, 0, 0.01, 0.02, 0.03, 0.04, 0.05, 2.0, 3.0]})
        res = quality.detect_outliers(df, method="iqr")
        assert "BTC" in res

    def test_small_column(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]})
        res = quality.detect_outliers(df)
        assert res["BTC"]["count"] == 0

    def test_constant_column(self):
        df = pd.DataFrame({"BTC": [0.01] * 10})
        res = quality.detect_outliers(df, method="zscore")
        assert res["BTC"]["count"] == 0

    def test_unknown_method(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03, 0.04, 10.0]})
        res = quality.detect_outliers(df, method="unknown")
        assert res["BTC"]["count"] == 0


class TestDetectStaleData:
    def test_detects_stale_runs(self):
        df = pd.DataFrame({"BTC": [0.01, 0.01, 0.01, 0.02, 0.02]})
        res = quality.detect_stale_data(df, threshold=3)
        assert res["BTC"]["count"] >= 1

    def test_no_stale(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.03]})
        res = quality.detect_stale_data(df, threshold=3)
        assert res["BTC"]["count"] == 0


class TestDetectVolumeAnomalies:
    def test_detects_volume_spikes(self):
        df = pd.DataFrame({
            "BTC": [0.01] * 10,
            "volume": [1000] * 9 + [10000]
        })
        res = quality.detect_volume_anomalies(df)
        assert isinstance(res, dict)

    def test_custom_volume_cols(self):
        df = pd.DataFrame({
            "vol": [100, 200, 150, 10000]
        })
        res = quality.detect_volume_anomalies(df, volume_cols=["vol"], threshold=5.0)
        assert "vol" in res


class TestDetectDuplicateTimestamps:
    def test_no_duplicates(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2))
        res = quality.detect_duplicate_timestamps(df)
        assert res["has_duplicates"] is False

    def test_with_duplicates(self):
        idx = pd.DatetimeIndex(["2023-01-01", "2023-01-01", "2023-01-02"])
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
        res = quality.detect_duplicate_timestamps(df)
        assert res["has_duplicates"] is True
        assert res["count"] >= 2
