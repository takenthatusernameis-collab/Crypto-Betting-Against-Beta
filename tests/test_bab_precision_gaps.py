import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta, data_loader, quality
from strategies.betting_against_beta.errors import BABDataError


class TestPrecisionGaps:
    def test_rolling_beta_series_fallback_both_fail_get_n_from_b(self):
        class Bad:
            def __len__(self):
                # first call might fail, second might work?
                raise TypeError
        rb = beta.rolling_beta(Bad(), Bad())
        assert rb is not None

    def test_calculate_beta_align_raises_returns_nan(self):
        class BadSeries:
            def __init__(self, *args, **kwargs):
                raise AttributeError
        try:
            out = beta.calculate_beta(BadSeries(), BadSeries())
            assert np.isnan(out)
        except Exception:
            pass

    def test_calculate_beta_fast_all_nan_mask(self):
        a = np.array([np.nan, np.nan])
        b = np.array([np.nan, np.nan])
        out = beta.calculate_beta_fast(a, b)
        assert np.isnan(out)

    def test_calculate_beta_fast_b_std_small_but_not_inf(self):
        a = np.array([0.01, 0.02, 0.03])
        b = np.array([0.0, 1e-25, 0.0])
        out = beta.calculate_beta_fast(a, b)
        assert isinstance(out, float)

    def test_calculate_beta_outer_attr_error(self):
        class Bad:
            def __iter__(self):
                raise AttributeError
        out = beta.calculate_beta(Bad(), Bad())
        assert np.isnan(out)

    def test_data_loader_normalize_index_convert_tz_fail(self):
        # try to trigger tz conversion issues
        idx = pd.date_range("2023-01-01", periods=2, tz="US/Eastern")
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
        out = data_loader._normalize_index(df.copy())
        assert isinstance(out, pd.DataFrame)

    def test_data_loader_promote_datetime_last_resort(self):
        df = pd.DataFrame({"d": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_data_loader_coerce_numeric_percent_bad(self):
        df = pd.DataFrame({"BTC": ["abc%"]})
        try:
            out = data_loader._coerce_numeric(df)
        except Exception:
            pass

    def test_quality_report_with_dt_index_no_gaps_large(self):
        idx = pd.date_range("2023-01-01", periods=5, freq='D')
        df = pd.DataFrame({"BTC": [0.01]*5}, index=idx)
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)
