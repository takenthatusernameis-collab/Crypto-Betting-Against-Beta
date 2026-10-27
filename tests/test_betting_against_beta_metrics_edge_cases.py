"""Edge-case tests for BAB metrics robustness."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import metrics


class TestSharpeEdgeCases:
    def test_none_returns_nan(self):
        assert np.isnan(metrics.sharpe_ratio(None))

    def test_empty_returns_nan(self):
        assert np.isnan(metrics.sharpe_ratio(pd.Series([], dtype="float64")))

    def test_single_obs_nan(self):
        assert np.isnan(metrics.sharpe_ratio(pd.Series([0.01])))

    def test_constant_positive_returns_inf(self):
        r = pd.Series([0.001] * 50)
        sr = metrics.sharpe_ratio(r)
        assert sr == np.inf

    def test_constant_negative_returns_neg_inf(self):
        r = pd.Series([-0.001] * 50)
        sr = metrics.sharpe_ratio(r)
        assert sr == -np.inf

    def test_dataframe_single_column_supported(self):
        df = pd.DataFrame({"a": [0.001, 0.002, 0.003]})
        sr = metrics.sharpe_ratio(df)
        assert isinstance(sr, float)


class TestMaxDrawdownEdgeCases:
    def test_none_returns_nan(self):
        assert np.isnan(metrics.max_drawdown(None))

    def test_empty_returns_nan(self):
        assert np.isnan(metrics.max_drawdown(pd.Series([], dtype="float64")))

    def test_returns_series_interpreted_correctly(self):
        # Losses should produce a drawdown even though the series is not cumulative.
        r = pd.Series([-0.1, -0.1, -0.1])
        dd = metrics.max_drawdown(r)
        assert dd <= 0
        assert not np.isnan(dd)

    def test_zero_drawdown(self):
        cum = pd.Series([1.0, 1.1, 1.2])
        dd = metrics.max_drawdown(cum)
        assert dd == 0.0

    def test_single_value_no_drawdown(self):
        assert metrics.max_drawdown(pd.Series([1.0])) == 0.0


class TestVolatilityEdgeCases:
    def test_none_returns_nan(self):
        assert np.isnan(metrics.annualized_volatility(None))

    def test_empty_returns_nan(self):
        assert np.isnan(metrics.annualized_volatility(pd.Series([], dtype="float64")))

    def test_constant_returns_zero_vol(self):
        r = pd.Series([0.001] * 50)
        assert metrics.annualized_volatility(r) == 0.0

    def test_single_obs_nan(self):
        assert np.isnan(metrics.annualized_volatility(pd.Series([0.01])))


class TestTurnoverEdgeCases:
    def test_none_returns_nan(self):
        assert np.isnan(metrics.turnover(None))

    def test_empty_dataframe_nan(self):
        assert np.isnan(metrics.turnover(pd.DataFrame()))

    def test_single_row_zero_turnover(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        w = pd.DataFrame({"A": [0.5], "B": [-0.5]}, index=idx)
        assert metrics.turnover(w) == 0.0


class TestStrategyBetaEdgeCases:
    def test_none_inputs_nan(self):
        assert np.isnan(metrics.strategy_beta(None, pd.Series([1.0, 2.0])))
        assert np.isnan(metrics.strategy_beta(pd.Series([1.0, 2.0]), None))

    def test_short_series_nan(self):
        assert np.isnan(metrics.strategy_beta(pd.Series([1.0]), pd.Series([1.0])))

    def test_zero_variance_benchmark_nan(self):
        bench = pd.Series([0.0, 0.0, 0.0])
        strat = pd.Series([0.01, 0.02, 0.03])
        assert np.isnan(metrics.strategy_beta(strat, bench))


class TestSummaryEdgeCases:
    def test_summary_handles_none_inputs(self):
        s = metrics.summary(None)
        for k in ("sharpe_ratio", "annualized_volatility", "max_drawdown", "turnover",
                  "strategy_beta", "total_return", "final_cumulative", "n_observations"):
            assert k in s
        assert s["n_observations"] == 0

    def test_summary_includes_observations(self):
        r = pd.Series(np.random.default_rng(5).normal(0, 0.01, 100))
        s = metrics.summary(r)
        assert s["n_observations"] == 100

    def test_summary_total_return_known_path(self):
        r = pd.Series([0.1, 0.1])
        s = metrics.summary(r)
        assert abs(s["total_return"] - ((1.1 * 1.1) - 1.0)) < 1e-9
        assert abs(s["final_cumulative"] - 1.21) < 1e-9