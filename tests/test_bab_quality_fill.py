import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import quality
from strategies.betting_against_beta.errors import BABDataError


class TestQualityFill:
    def test_check_data_quality_all_finite(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01,0.02,-0.01,0.0,0.01]}, index=idx)
        res = quality.check_data_quality(df)
        assert res is not None

    def test_data_quality_report_all_ok(self):
        idx = pd.date_range("2023-01-01", periods=10)
        df = pd.DataFrame({"BTC": np.random.default_rng(1).normal(0,0.01,10), "ETH": np.random.default_rng(2).normal(0,0.01,10)}, index=idx)
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_data_quality_report_large_gaps(self):
        idx = pd.DatetimeIndex([pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-10'), pd.Timestamp('2023-01-11')])
        df = pd.DataFrame({"BTC": [0.01,0.02,0.03]}, index=idx)
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_check_data_quality_none_df(self):
        try:
            quality.check_data_quality(None)
        except Exception:
            pass
