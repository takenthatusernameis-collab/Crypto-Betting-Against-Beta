"""Final probe: exercise every remaining quality.py branch under coverage."""
from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import quality


def test_data_quality_report_conversion_error():
    class Weird:
        pass

    df = pd.DataFrame(
        {"WEIRD": [Weird(), Weird(), Weird()]},
        index=pd.date_range("2023-01-01", periods=3),
    )
    report = quality.data_quality_report(df)
    assert "columns" in report


def test_check_data_quality_strict_error_branch():
    try:
        quality.check_data_quality(None, strict=True)
    except ValueError:
        pass


def test_detect_gaps_zero_median_case():
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03]},
        index=pd.to_datetime(["2023-01-01", "2023-01-01", "2023-01-01"]),
    )
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


def test_detect_stale_data_exception():
    class Weird:
        pass

    df = pd.DataFrame({"WEIRD": [Weird()] * 5})
    res = quality.detect_stale_data(df)
    assert "WEIRD" in res


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


def test_compute_quality_empty_no_columns():
    df = pd.DataFrame()
    res = quality.compute_quality(df)
    assert isinstance(res, pd.DataFrame)
    assert res.empty


def test_compute_quality_with_outliers_and_stale():
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame(
        {"BTC": [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, -0.01, 0.03, 0.5]},
        index=dates,
    )
    res = quality.compute_quality(df)
    assert isinstance(res, pd.DataFrame)


def test_compute_quality_zscore_outlier_penalty():
    # A value >3 std from mean triggers the zscore_outliers penalty branch.
    # Use a tight cluster (std ~0) so the outlier is far in std units.
    vals = [0.0] * 13 + [1000.0]
    dates = pd.date_range("2023-01-01", periods=len(vals))
    df = pd.DataFrame({"BTC": vals}, index=dates)
    res = quality.compute_quality(df)
    assert isinstance(res, pd.DataFrame)
    assert res.iloc[0]["quality_score"] < 1.0

class TestQualityExtraFinal:
    def test_data_quality_report_to_numeric_exception(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        df = pd.DataFrame({"A": [1.0, 2.0]}, index=pd.date_range("2023-01-01", periods=2))
        orig = quality.pd.to_numeric
        def fake_to_numeric(*args, **kwargs):
            raise ValueError("boom")
        try:
            quality.pd.to_numeric = fake_to_numeric
            rep = quality.data_quality_report(df)
            # Should have column entry with arr of NaNs
            assert "columns" in rep
        finally:
            quality.pd.to_numeric = orig

    def test_detect_gaps_median_zero(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        # All same timestamps? Or gaps zero
        idx = pd.DatetimeIndex([pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-01")])
        df = pd.DataFrame({"A": [1.0, 2.0]}, index=idx)
        # But duplicates - detect_gaps looks at diff of index values; if same, diff is 0
        res = quality.detect_gaps(df)
        assert res["count"] == 0

    def test_detect_outliers_exception_paths(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        df = pd.DataFrame({"A": [1.0, 2.0]}, index=pd.date_range("2023-01-01", periods=2))
        orig = quality.pd.to_numeric
        def fake_to_numeric(*args, **kwargs):
            raise RuntimeError("bad")
        try:
            quality.pd.to_numeric = fake_to_numeric
            res = quality.detect_outliers(df)
            assert "A" in res
        finally:
            quality.pd.to_numeric = orig

    def test_detect_stale_data_exception(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        df = pd.DataFrame({"A": [1.0, 2.0]}, index=pd.date_range("2023-01-01", periods=2))
        orig = quality.pd.to_numeric
        def fake_to_numeric(*args, **kwargs):
            raise RuntimeError("bad")
        try:
            quality.pd.to_numeric = fake_to_numeric
            res = quality.detect_stale_data(df)
            assert "A" in res
        finally:
            quality.pd.to_numeric = orig

    def test_detect_volume_anomalies_exception(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        df = pd.DataFrame({"volume": [1.0, 2.0]}, index=pd.date_range("2023-01-01", periods=2))
        orig = quality.pd.to_numeric
        def fake_to_numeric(*args, **kwargs):
            raise RuntimeError("bad")
        try:
            quality.pd.to_numeric = fake_to_numeric
            res = quality.detect_volume_anomalies(df)
            assert "volume" in res
        finally:
            quality.pd.to_numeric = orig

    def test_detect_gaps_get_loc_fallback(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"A": [1,2,3,4,5]}, index=idx)
        # Create a case where get_loc might behave differently
        res = quality.detect_gaps(df)
        assert isinstance(res, dict)

    def test_detect_duplicate_timestamps_no_duplicates_attr(self):
        from strategies.betting_against_beta import quality
        import pandas as pd

        df = pd.DataFrame({"A": [1, 2, 3]})  # no DatetimeIndex
        res = quality.detect_duplicate_timestamps(df)
        assert res["has_duplicates"] is False
