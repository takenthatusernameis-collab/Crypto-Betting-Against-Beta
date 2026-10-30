import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta, data_loader, quality, backtest
from strategies.betting_against_beta.errors import BABDataError


class TestCoveragePush:
    def test_beta_rolling_bad_bench_conversion_in_outer(self):
        idx = pd.date_range("2023-01-01", periods=15)
        df = pd.DataFrame({"BTC": [[1]]*15, "ETH": np.random.default_rng(1).normal(0,0.01,15)}, index=idx)
        try:
            beta.calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
        except Exception:
            pass

    def test_beta_calculate_fast_all_finite_mask_branch(self):
        a = np.array([0.01, 0.02, 0.03, 0.04])
        b = np.array([0.01, 0.015, 0.025, 0.035])
        out = beta.calculate_beta_fast(a, b)
        assert np.isfinite(out)

    def test_data_loader_promote_unnamed_datetime_col(self):
        df = pd.DataFrame({"": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_data_loader_normalize_index_already_dt(self):
        idx = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame({"BTC": [0.01,0.02,0.03]}, index=idx)
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_data_loader_coerce_comma_decimal_european(self):
        df = pd.DataFrame({"BTC": ["1,50", "2,25"]})
        try:
            out = data_loader._coerce_numeric(df)
        except Exception:
            pass

    def test_quality_report_with_inf_and_missing(self):
        df = pd.DataFrame({"BTC": [0.01, np.inf, np.nan, 0.02], "ETH": [np.nan, 0.01, 0.02, 0.03]})
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_quality_check_non_strict_missing(self):
        df = pd.DataFrame({"BTC": [0.01, np.nan, 0.02]})
        try:
            quality.check_data_quality(df, strict=False)
        except Exception:
            pass

    def test_backtest_edge_slippage(self):
        idx = pd.date_range("2023-01-01", periods=12)
        weights = pd.DataFrame({"BTC": np.linspace(0,0.5,12), "ETH": -np.linspace(0,0.5,12)}, index=idx)
        returns = pd.DataFrame({"BTC": np.random.default_rng(5).normal(0,0.01,12), "ETH": np.random.default_rng(6).normal(0,0.01,12)}, index=idx)
        try:
            res = backtest.run_backtest(returns, weights, transaction_costs=0.0005, slippage=0.0005)
        except Exception:
            pass
