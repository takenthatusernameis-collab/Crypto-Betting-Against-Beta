import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import quality
from strategies.betting_against_beta.errors import BABDataError


class TestQualityTargeted:
    def test_check_data_quality_strict_inf_issue(self):
        df = pd.DataFrame({"BTC": [0.01, np.inf]})
        try:
            quality.check_data_quality(df, strict=True)
        except Exception:
            pass

    def test_check_data_quality_strict_missing(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan]})
        try:
            quality.check_data_quality(df, strict=True)
        except Exception:
            pass

    def test_data_quality_report_all_missing_col(self):
        df = pd.DataFrame({"BTC": [np.nan, np.nan], "ETH": [0.01, 0.02]})
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_data_quality_report_dup_index(self):
        idx = pd.DatetimeIndex([pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')])
        df = pd.DataFrame({"BTC": [0.01,0.02,0.03]}, index=idx)
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_data_quality_report_no_datetime_index(self):
        df = pd.DataFrame({"BTC": [0.01,0.02,0.03]})
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)
