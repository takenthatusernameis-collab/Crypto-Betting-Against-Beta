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
