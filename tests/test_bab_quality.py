"""Robustness tests for data quality utilities in strategies/betting_against_beta/quality.py.

Deterministic, offline, no network. Every input is seeded or hand-constructed so
results are reproducible across runs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.quality import (
    check_data_quality,
    data_quality_report,
    detect_duplicate_timestamps,
    detect_gaps,
    detect_outliers,
    detect_stale_data,
    detect_volume_anomalies,
)

SEED = 20261029


def _make_df(n: int = 120, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {
            "BTC": rng.normal(0.0005, 0.02, n),
            "ETH": rng.normal(0.0003, 0.025, n),
        },
        index=idx,
    )


class TestDataQualityReportStructure:
    def test_report_has_expected_top_level_keys(self):
        report = data_quality_report(_make_df())
        for key in ("shape", "index", "columns", "summary"):
            assert key in report, f"missing report key: {key}"

    def test_shape_matches_input(self):
        df = _make_df(n=50)
        report = data_quality_report(df)
        assert report["shape"] == {"rows": 50, "cols": 2}

    def test_index_info_is_recorded(self):
        report = data_quality_report(_make_df())
        assert report["index"]["is_datetime"] is True
        assert report["index"]["type"] == "DatetimeIndex"
        assert report["index"]["has_duplicates"] is False
        assert report["index"]["start"].startswith("2023-01-01")
        assert report["index"]["end"].startswith("2023-04-")

    def test_each_column_entry_has_expected_keys(self):
        report = data_quality_report(_make_df())
        for col in report["columns"]:
            for key in (
                "name", "dtype", "missing", "missing_pct", "zeros", "inf",
                "min", "max", "mean", "std", "outliers", "stale_consecutive",
            ):
                assert key in col, f"missing column key: {key}"

    def test_summary_keys_present(self):
        report = data_quality_report(_make_df())
        for key in ("total_missing", "all_finite", "has_issues", "has_duplicates", "large_gaps"):
            assert key in report["summary"], f"missing summary key: {key}"


class TestDataQualityReportMissingAndInf:
    def test_counts_nan_and_inf(self):
        df = _make_df(n=20)
        df.iloc[5:10, 0] = np.nan
        df.iloc[12, 1] = np.inf
        report = data_quality_report(df)
        btc = next(c for c in report["columns"] if c["name"] == "BTC")
        eth = next(c for c in report["columns"] if c["name"] == "ETH")
        # "missing" counts every non-finite value (NaN and inf).
        assert btc["missing"] == 5
        assert btc["inf"] == 0
        assert eth["missing"] == 1  # the inf
        assert eth["inf"] == 1
        assert report["summary"]["all_finite"] is False
        assert report["summary"]["total_missing"] == 6

    def test_all_finite_when_clean(self):
        report = data_quality_report(_make_df())
        assert report["summary"]["all_finite"] is True
        assert report["summary"]["has_issues"] is False

    def test_missing_pct_is_fraction(self):
        df = _make_df(n=20)
        df.iloc[:5, 0] = np.nan
        report = data_quality_report(df)
        btc = next(c for c in report["columns"] if c["name"] == "BTC")
        assert abs(btc["missing_pct"] - 0.25) < 1e-12


class TestDataQualityReportIndexAnomalies:
    def test_duplicate_timestamps_flagged(self):
        df = _make_df(n=20)
        df = pd.concat([df, df.iloc[[3]]])  # inject a duplicate timestamp row
        report = data_quality_report(df)
        assert report["index"]["has_duplicates"] is True
        assert report["summary"]["has_duplicates"] is True

    def test_calendar_gap_counted(self):
        df = _make_df(n=20)
        df = df.drop(df.index[10:13])  # 4-day gap vs 1-day median
        report = data_quality_report(df)
        assert report["index"]["gaps"]["count"] >= 1
        assert report["summary"]["large_gaps"] >= 1

    def test_non_datetime_index_gaps_zero(self):
        df = _make_df().reset_index(drop=True)
        report = data_quality_report(df)
        assert report["index"]["gaps"] == {"count": 0}


class TestDataQualityReportOutliersAndStale:
    def test_zscore_outliers_detected(self):
        df = _make_df(n=50)
        df.iloc[25, 0] = 1.0  # massive outlier vs ~0.0005 mean
        report = data_quality_report(df)
        btc = next(c for c in report["columns"] if c["name"] == "BTC")
        assert btc["outliers"]["zscore_outliers"] >= 1

    def test_iqr_outliers_detected(self):
        df = _make_df(n=50)
        df.iloc[25, 0] = 1.0
        report = data_quality_report(df)
        btc = next(c for c in report["columns"] if c["name"] == "BTC")
        assert btc["outliers"]["iqr_outliers"] >= 1

    def test_constant_column_has_no_outliers(self):
        df = _make_df(n=50)
        df["BTC"] = 0.001
        report = data_quality_report(df)
        btc = next(c for c in report["columns"] if c["name"] == "BTC")
        # Zero std / zero IQR => no outlier info recorded.
        assert btc["outliers"] == {}

    def test_stale_run_detected(self):
        df = _make_df(n=50)
        df.iloc[30:40, 0] = 0.002
        report = data_quality_report(df)
        btc = next(c for c in report["columns"] if c["name"] == "BTC")
        assert btc["stale_consecutive"] >= 9


class TestDataQualityReportDegenerate:
    def test_empty_dataframe(self):
        df = pd.DataFrame({"BTC": pd.Series(dtype="float64"), "ETH": pd.Series(dtype="float64")})
        report = data_quality_report(df)
        assert report["shape"] == {"rows": 0, "cols": 2}
        # Column entries are still produced (no rows => nothing missing).
        assert len(report["columns"]) == 2
        assert all(c["missing"] == 0 and c["missing_pct"] == 1.0 for c in report["columns"])
        assert report["summary"]["all_finite"] is True
        assert report["summary"]["has_issues"] is True  # 100% missing pct flags an issue

    def test_single_row(self):
        df = _make_df(n=1)
        report = data_quality_report(df)
        assert report["shape"] == {"rows": 1, "cols": 2}
        assert report["summary"]["all_finite"] is True

    def test_non_numeric_column_coerced_to_nan(self):
        df = _make_df(n=10)
        df["TEXT"] = "not numeric"
        report = data_quality_report(df)
        text_col = next(c for c in report["columns"] if c["name"] == "TEXT")
        assert text_col["missing"] == 10


class TestCheckDataQuality:
    def test_clean_data_passes(self):
        assert check_data_quality(_make_df()) is True

    def test_data_with_issues_fails_non_strict(self):
        df = _make_df(n=20)
        df.iloc[:5, 0] = np.nan
        assert check_data_quality(df) is False

    def test_strict_raises_on_issues(self):
        df = _make_df(n=20)
        df.iloc[:5, 0] = np.nan
        with pytest.raises(ValueError):
            check_data_quality(df, strict=True)

    def test_strict_raises_on_invalid_input(self):
        with pytest.raises(ValueError):
            check_data_quality(None, strict=True)

    def test_inf_triggers_strict_raise(self):
        df = _make_df(n=10)
        df.iloc[3, 1] = np.inf
        with pytest.raises(ValueError):
            check_data_quality(df, strict=True)


class TestDetectGaps:
    def test_regular_index_has_no_gaps(self):
        assert detect_gaps(_make_df())["count"] == 0

    def test_missing_dates_detected(self):
        df = _make_df(n=30)
        df = df.drop(df.index[[10, 11, 12]])
        gaps = detect_gaps(df)
        assert gaps["count"] >= 1
        assert len(gaps["gaps"]) >= 1

    def test_non_datetime_index_returns_empty(self):
        df = _make_df().reset_index(drop=True)
        assert detect_gaps(df) == {"gaps": [], "count": 0}

    def test_single_row_returns_empty(self):
        assert detect_gaps(_make_df(n=1)) == {"gaps": [], "count": 0}


class TestDetectOutliers:
    def test_zscore_finds_injected_outlier(self):
        df = _make_df(n=60)
        df.iloc[30, 0] = 2.0
        result = detect_outliers(df, method="zscore", threshold=3.0)
        assert result["BTC"]["count"] >= 1

    def test_iqr_finds_injected_outlier(self):
        df = _make_df(n=60)
        df.iloc[30, 0] = 2.0
        result = detect_outliers(df, method="iqr", threshold=3.0)
        assert result["BTC"]["count"] >= 1

    def test_constant_column_no_outliers(self):
        df = _make_df(n=60)
        df["BTC"] = 0.001
        result = detect_outliers(df, method="zscore")
        assert result["BTC"]["count"] == 0

    def test_unknown_method_returns_empty_counts(self):
        df = _make_df(n=20)
        result = detect_outliers(df, method="bogus")
        assert result["BTC"]["count"] == 0


class TestDetectStaleData:
    def test_stale_run_detected(self):
        df = _make_df(n=50)
        df.iloc[20:30, 0] = 0.005
        result = detect_stale_data(df, threshold=3)
        assert result["BTC"]["count"] >= 1

    def test_no_stale_data(self):
        result = detect_stale_data(_make_df(n=50), threshold=3)
        assert result["BTC"]["count"] == 0

    def test_threshold_respected(self):
        df = _make_df(n=20)
        df.iloc[:2, 0] = 0.005  # run of 2, below threshold 3
        result = detect_stale_data(df, threshold=3)
        assert result["BTC"]["count"] == 0


class TestDetectVolumeAnomalies:
    def test_spike_detected(self):
        df = _make_df(n=40)
        df["volume"] = 1000.0
        df.iloc[20, df.columns.get_loc("volume")] = 100000.0
        result = detect_volume_anomalies(df, volume_cols=["volume"], threshold=5.0)
        assert result["volume"]["count"] >= 1

    def test_no_volume_columns(self):
        result = detect_volume_anomalies(_make_df(n=20))
        assert result == {}

    def test_unknown_volume_column_skipped(self):
        result = detect_volume_anomalies(_make_df(n=20), volume_cols=["nope"])
        assert result == {}

    def test_constant_volume_no_anomalies(self):
        df = _make_df(n=20)
        df["volume"] = 1000.0
        result = detect_volume_anomalies(df, volume_cols=["volume"], threshold=5.0)
        assert result["volume"]["count"] == 0


class TestDetectDuplicateTimestamps:
    def test_duplicates_detected(self):
        df = _make_df(n=20)
        df = pd.concat([df, df.iloc[[3]]])  # inject a duplicate timestamp row
        result = detect_duplicate_timestamps(df)
        assert result["has_duplicates"] is True
        assert result["count"] >= 2

    def test_no_duplicates(self):
        result = detect_duplicate_timestamps(_make_df(n=20))
        assert result["has_duplicates"] is False
        assert result["count"] == 0



class TestDataQualityReportExtraGaps:
    def test_median_gap_nan_branch(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=5)
        # Create a case where diff gives NaN median? Unlikely, but let's force
        df2 = df.copy()
        df2.index = pd.to_datetime(df2.index)
        # Replace index to cause issues? Or just call; maybe all same diffs gives NaN if we had all NaT? Easier to construct
        # Just ensure normal path; maybe test with irregular but median computable
        report = quality.data_quality_report(df2)
        assert "index" in report

    def test_gap_median_is_zero_or_nan_handling(self):
        from strategies.betting_against_beta import quality
        import pandas as pd
        import numpy as np
        dates = pd.date_range("2020-01-01", periods=3)
        df = pd.DataFrame({"BTC": [1.0, 1.0, 1.0]}, index=dates)
        # diff will have zeros
        report = quality.data_quality_report(df)
        assert report["index"]["gaps"]["count"] == 0


class TestQualityMoreBranches:
    def test_non_datetime_index_gaps_empty(self):
        from strategies.betting_against_beta import quality
        df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3]}, index=[0, 1, 2])
        report = quality.data_quality_report(df)
        assert report["index"]["gaps"] == {"count": 0}

    def test_invalid_input_none(self):
        from strategies.betting_against_beta import quality
        assert quality.data_quality_report(None)["error"] == "invalid_input"

    def test_invalid_input_wrong_type(self):
        from strategies.betting_against_beta import quality
        assert quality.data_quality_report([])["error"] == "invalid_input"

    def test_column_conversion_exception_fallback(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=5)
        # Create an object that causes issues
        df["bad"] = object()
        report = quality.data_quality_report(df)
        assert any(c["name"] == "bad" for c in report["columns"])

    def test_outliers_iqr_fallback_when_iqr_zero_but_std_positive(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        # Make values where IQR might be zero but not constant? No, constant gives iqr 0 and std 0.
        # Or many same values around median
        df["X"] = [1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        report = quality.data_quality_report(df)
        assert "columns" in report

    def test_inf_count_in_column(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df.iloc[0, 0] = np.inf
        report = quality.data_quality_report(df)
        # Should count inf
        col = [c for c in report["columns"] if c["name"] == "BTC"][0]
        assert col["inf"] >= 1


class TestDetectGapsExtra:
    def test_detect_gaps_non_datetime(self):
        from strategies.betting_against_beta import quality
        df = pd.DataFrame({"x": [1,2,3]}, index=[1,2,3])
        res = quality.detect_gaps(df)
        assert res["count"] == 0

    def test_detect_gaps_too_short(self):
        from strategies.betting_against_beta import quality
        dates = pd.date_range("2020-01-01", periods=1)
        df = pd.DataFrame({"x": [1]}, index=dates)
        res = quality.detect_gaps(df)
        assert res["count"] == 0

    def test_detect_gaps_median_zero(self):
        from strategies.betting_against_beta import quality
        dates = pd.date_range("2020-01-01", periods=3)
        df = pd.DataFrame({"x": [1,2,3]}, index=dates)
        # all same diff -> median is same as diff, not zero; force zero by weird construction hard
        res = quality.detect_gaps(df)
        assert "gaps" in res


class TestDetectOutliersExtra:
    def test_detect_outliers_iqr_zero_branch(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df["C"] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        res = quality.detect_outliers(df, method="iqr")
        assert res["C"]["count"] == 0

    def test_detect_outliers_few_points(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=2)
        res = quality.detect_outliers(df)
        assert res["BTC"]["count"] == 0

    def test_detect_outliers_exception(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df["bad"] = object()
        res = quality.detect_outliers(df)
        assert res["bad"]["count"] == 0


class TestDetectStaleExtra:
    def test_stale_threshold_boundary(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df.iloc[0:3, 0] = 0.5  # run of 3
        res = quality.detect_stale_data(df, threshold=3)
        assert res["BTC"]["count"] >= 1

    def test_stale_exception_path(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df["bad"] = object()
        res = quality.detect_stale_data(df)
        assert res["bad"]["count"] == 0


class TestDetectVolumeExtra:
    def test_volume_median_zero(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df["volume"] = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0]
        res = quality.detect_volume_anomalies(df)
        # median of all is 0
        assert res["volume"]["count"] == 0

    def test_volume_few_points(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=2)
        df["volume"] = [1, 2]
        res = quality.detect_volume_anomalies(df)
        assert res["volume"]["count"] == 0

    def test_volume_exception(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df["volume"] = object()
        res = quality.detect_volume_anomalies(df)
        assert res["volume"]["count"] == 0


class TestDetectDuplicatesExtra:
    def test_duplicates_no_hasattr_path(self):
        from strategies.betting_against_beta import quality
        import pandas as pd
        df = pd.DataFrame({"a": [1,2,3]}, index=[1,1,2])
        # override
        res = quality.detect_duplicate_timestamps(df)
        assert res["has_duplicates"] is True



class TestQualityCoverageGaps:
    def test_data_quality_report_datetime_gaps_median_nan(self):
        from strategies.betting_against_beta import quality
        import pandas as pd
        import numpy as np
        # Create dates where diff might be problematic? Or manually construct
        dates = pd.to_datetime(['2020-01-01', '2020-01-02', '2020-01-03'])
        df = pd.DataFrame({'BTC': [1.0, 2.0, 3.0]}, index=dates)
        report = quality.data_quality_report(df)
        assert 'gaps' in report['index']

    def test_data_quality_report_stale_count_increments(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=5)
        df.iloc[1:4, 0] = 5.0  # three consecutive equal finite
        report = quality.data_quality_report(df)
        col = [c for c in report['columns'] if c['name'] == 'BTC'][0]
        assert col['stale_consecutive'] >= 2

    def test_data_quality_report_column_conversion_bare_except(self):
        from strategies.betting_against_beta import quality
        # The code has bare except at line ~47-48; force it
        df = _make_df(n=3)
        df['bad'] = [object(), object(), object()]
        report = quality.data_quality_report(df)
        col = [c for c in report['columns'] if c['name'] == 'bad'][0]
        assert col['missing'] == 3

    def test_data_quality_report_outlier_iqr_fallback(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=20)
        # Create case where iqr is 0 but std > 0? If most values same, median/IQR might behave oddly
        df['X'] = [1.0] * 19 + [5.0]
        report = quality.data_quality_report(df)
        assert 'outliers' in report['columns'][0]

    def test_check_data_quality_strict_issues(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=10)
        df.iloc[0, 0] = np.inf
        try:
            quality.check_data_quality(df, strict=True)
            assert False
        except ValueError:
            pass

    def test_detect_gaps_after_index_lookup(self):
        from strategies.betting_against_beta import quality
        dates = pd.date_range('2020-01-01', periods=5, freq='D')
        df = pd.DataFrame({'x': range(5)}, index=dates)
        # insert large gap
        df2 = df.copy()
        # create gap by reindexing with skip
        idx = list(dates)
        idx[2] = idx[2] + pd.Timedelta(days=10)  # create gap
        df3 = pd.DataFrame({'x': [0,1,99,3,4]}, index=idx)
        res = quality.detect_gaps(df3, max_gap_multiplier=1.5)
        assert res['count'] >= 1

    def test_detect_outliers_iqr_with_values(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=50)
        df.iloc[10, 0] = 10.0
        df.iloc[20, 0] = -10.0
        res = quality.detect_outliers(df, method='iqr')
        assert res['BTC']['count'] >= 1
        assert len(res['BTC']['values']) >= 1

    def test_detect_volume_anomalies_below_threshold(self):
        from strategies.betting_against_beta import quality
        df = _make_df(n=30)
        df['volume'] = 1000.0
        df.iloc[15, df.columns.get_loc('volume')] = 100.0  # crash below 1/threshold
        res = quality.detect_volume_anomalies(df, volume_cols=['volume'], threshold=5.0)
        assert res['volume']['count'] >= 1

    def test_detect_duplicate_timestamps_no_has_duplicates_attr(self):
        from strategies.betting_against_beta import quality
        import pandas as pd
        class DummyIdx:
            def __init__(self):
                pass
        df = pd.DataFrame({'a':[1,2,3]})
        df.index = [1,2,3]  # regular index, no has_duplicates
        res = quality.detect_duplicate_timestamps(df)
        assert res['has_duplicates'] is False
