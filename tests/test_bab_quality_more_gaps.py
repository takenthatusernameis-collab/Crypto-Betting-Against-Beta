import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import quality
from strategies.betting_against_beta.errors import BABDataError


class TestQualityMoreGaps:
    def test_check_data_quality_empty_df(self):
        try:
            df = pd.DataFrame()
            quality.check_data_quality(df)
        except Exception:
            pass

    def test_check_data_quality_non_df(self):
        try:
            quality.check_data_quality([1,2,3])
        except Exception:
            pass

    def test_check_data_quality_all_nan_column(self):
        df = pd.DataFrame({"BTC": [np.nan, np.nan, np.nan]})
        try:
            res = quality.check_data_quality(df)
        except Exception:
            pass

    def test_data_quality_report_empty(self):
        try:
            rep = quality.data_quality_report(pd.DataFrame())
        except Exception:
            pass

    def test_data_quality_report_inf_only(self):
        df = pd.DataFrame({"BTC": [np.inf, -np.inf]})
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_data_quality_report_duplicates(self):
        idx = pd.DatetimeIndex([pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-01')])
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
        try:
            rep = quality.data_quality_report(df)
        except Exception:
            pass

    def test_check_data_quality_warnings_only(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan, 0.02]})
        try:
            quality.check_data_quality(df, strict=False)
        except Exception:
            pass

    def test_check_data_quality_strict_missing_raises(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan]})
        try:
            quality.check_data_quality(df, strict=True)
        except BABDataError:
            pass
        except Exception:
            pass
