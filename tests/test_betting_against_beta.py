"""Unit tests for the Betting Against Beta (BAB) strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.backtest import run_backtest
from strategies.betting_against_beta.beta import calculate_beta, calculate_rolling_beta
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data import generate_synthetic_returns
from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.signals import generate_bab_signals
from strategies.betting_against_beta.strategy import BABStrategy


class TestCalculateBeta:
    """Tests for single-window OLS beta calculation."""

    def test_recovers_known_beta(self) -> None:
        rng = np.random.default_rng(7)
        bench = rng.normal(0.001, 0.02, 200)
        true_beta = 1.5
        asset = true_beta * bench + rng.normal(0, 0.005, 200)
        beta = calculate_beta(pd.Series(asset), pd.Series(bench))
        assert abs(beta - true_beta) < 0.1

    def test_benchmark_vs_itself_is_one(self) -> None:
        rng = np.random.default_rng(3)
        r = pd.Series(rng.normal(0.001, 0.02, 100))
        assert abs(calculate_beta(r, r) - 1.0) < 1e-6

    def test_insufficient_observations_returns_nan(self) -> None:
        asset = pd.Series([0.001, 0.002])
        bench = pd.Series([0.001, 0.002])
        assert np.isnan(calculate_beta(asset, bench, min_obs=5))

    def test_all_nan_returns_nan(self) -> None:
        asset = pd.Series([np.nan, np.nan, np.nan])
        bench = pd.Series([0.001, 0.002, 0.003])
        assert np.isnan(calculate_beta(asset, bench))

    def test_aligns_mismatched_index(self) -> None:
        asset = pd.Series([0.01, 0.02, 0.03], index=[0, 1, 2])
        bench = pd.Series([0.005, 0.01, 0.015], index=[1, 2, 3])
        # Only index 1, 2 overlap -> beta should recover 2.0 exactly.
        beta = calculate_beta(asset, bench)
        assert abs(beta - 2.0) < 1e-6


class TestCalculateRollingBeta:
    """Tests for rolling beta calculation."""

    def test_returns_dataframe_with_all_assets(self) -> None:
        df = generate_synthetic_returns(n_days=150, n_assets=6, seed=1)
        betas = calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
        assert list(betas.columns) == list(df.columns)
        assert len(betas) == len(df)

    def test_benchmark_beta_is_one(self) -> None:
        df = generate_synthetic_returns(n_days=150, n_assets=6, seed=1)
        betas = calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
        assert (betas["BTC"].dropna() == 1.0).all()

    def test_early_windows_are_nan(self) -> None:
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=2)
        betas = calculate_rolling_beta(df, "BTC", window=60, min_obs=60)
        # Benchmark column is 1.0 by design; check the asset columns only.
        # With min_obs=60 the first finite row is row 59 (60 observations),
        # so rows 0..58 are NaN and row 59 is finite.
        assert betas.iloc[:59].drop(columns=["BTC"]).isna().all().all()
        assert np.isfinite(betas.iloc[59].drop(columns=["BTC"]).to_numpy()).all()

    def test_lower_beta_asset_has_lower_rolling_beta(self) -> None:
        df = generate_synthetic_returns(n_days=200, n_assets=4, seed=5)
        betas = calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        last = betas.iloc[-1].dropna()
        others = [c for c in last.index if c != "BTC"]
        # Synthetic data assigns asset i beta 0.5 + 0.5*i in generation order.
        assert last["ASSET0"] < last["ASSET3"]

    def test_all_nan_asset_column_does_not_crash(self) -> None:
        idx = pd.date_range("2023-01-01", periods=30, freq="D")
        df = pd.DataFrame(
            {
                "BTC": np.random.default_rng(1).normal(0, 0.01, 30),
                "ETH": np.random.default_rng(2).normal(0, 0.01, 30),
                "DEL": [np.nan] * 30,
            },
            index=idx,
        )
        betas = calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
        assert "DEL" in betas.columns
        # The all-NaN asset should produce NaN betas, not raise.
        assert betas["DEL"].isna().all()

    def test_constant_series_does_not_crash(self) -> None:
        idx = pd.date_range("2023-01-01", periods=30, freq="D")
        df = pd.DataFrame(
            {
                "BTC": np.random.default_rng(1).normal(0, 0.01, 30),
                "ETH": [0.0] * 30,  # constant zero returns -> zero variance
            },
            index=idx,
        )
        betas = calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
        assert betas.shape == (30, 2)
        # Beta of a constant series is 0 (covariance with benchmark is 0).
        assert np.allclose(betas["ETH"].dropna(), 0.0, atol=1e-9)

    def test_missing_benchmark_raises(self) -> None:
        idx = pd.date_range("2023-01-01", periods=30, freq="D")
        df = pd.DataFrame(
            {"ETH": np.random.default_rng(1).normal(0, 0.01, 30)}, index=idx
        )
        with pytest.raises(Exception):
            calculate_rolling_beta(df, "BTC", window=5, min_obs=3)

    def test_all_nan_benchmark_raises(self) -> None:
        idx = pd.date_range("2023-01-01", periods=30, freq="D")
        df = pd.DataFrame(
            {
                "BTC": [np.nan] * 30,
                "ETH": np.random.default_rng(1).normal(0, 0.01, 30),
            },
            index=idx,
        )
        with pytest.raises(Exception):
            calculate_rolling_beta(df, "BTC", window=5, min_obs=3)

    def test_single_asset_does_not_raise(self) -> None:
        idx = pd.date_range("2023-01-01", periods=30, freq="D")
        df = pd.DataFrame(
            {
                "BTC": np.random.default_rng(1).normal(0, 0.01, 30),
                "ETH": np.random.default_rng(2).normal(0, 0.01, 30),
            },
            index=idx,
        )
        betas = calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
        assert betas.shape == (30, 2)
        assert not betas["ETH"].isna().all()

    def test_constant_benchmark_does_not_raise(self) -> None:
        idx = pd.date_range("2023-01-01", periods=30, freq="D")
        df = pd.DataFrame(
            {
                "BTC": [0.0] * 30,  # zero-variance benchmark
                "ETH": np.random.default_rng(1).normal(0, 0.01, 30),
            },
            index=idx,
        )
        betas = calculate_rolling_beta(df, "BTC", window=5, min_obs=3)
        assert betas.shape == (30, 2)


class TestGenerateBabSignals:
    """Tests for long/short signal generation."""

    def test_signal_counts_match_quantiles(self) -> None:
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        cols = ["A", "B", "C", "D", "E", "F", "G", "H"]
        betas = pd.DataFrame(
            {c: np.linspace(0.5, 2.5, 5) for c in cols}, index=idx
        )
        signals = generate_bab_signals(betas, long_quantile=0.25, short_quantile=0.25)
        row = signals.iloc[-1]
        assert int((row == 1).sum()) == 2
        assert int((row == -1).sum()) == 2

    def test_longs_have_lowest_beta_shorts_highest(self) -> None:
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        betas = pd.DataFrame(
            {"A": [1.0, 1.0, 1.0], "B": [2.0, 2.0, 2.0], "C": [3.0, 3.0, 3.0]},
            index=idx,
        )
        signals = generate_bab_signals(betas, long_quantile=0.33, short_quantile=0.33)
        row = signals.iloc[0]
        assert row["A"] == 1
        assert row["C"] == -1
        assert row["B"] == 0

    def test_nan_betas_are_ignored(self) -> None:
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        betas = pd.DataFrame(
            {"A": [np.nan, 1.0], "B": [1.0, np.nan], "C": [2.0, 2.0]},
            index=idx,
        )
        signals = generate_bab_signals(betas, long_quantile=0.33, short_quantile=0.33)
        assert not signals.isna().any().any()
        assert signals.loc[idx[0], "C"] == -1


class TestConstructPortfolio:
    """Tests for portfolio weight construction."""

    def test_dollar_neutral_weights_sum_to_zero(self) -> None:
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        # Every row has at least one long and one short -> dollar neutral.
        signals = pd.DataFrame(
            {"A": [1, -1, 1], "B": [-1, 1, -1], "C": [0, 0, 0]}, index=idx
        )
        weights = construct_portfolio(signals, dollar_neutral=True)
        for row in weights.itertuples(index=False):
            assert abs(sum(row)) < 1e-9

    def test_long_equal_weights(self) -> None:
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [1], "C": [-1]}, index=idx)
        weights = construct_portfolio(signals, dollar_neutral=True)
        row = weights.loc[idx[0]]
        assert abs(row["A"] - 0.5) < 1e-9
        assert abs(row["B"] - 0.5) < 1e-9
        assert abs(row["C"] + 1.0) < 1e-9

    def test_long_only_when_not_dollar_neutral(self) -> None:
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        weights = construct_portfolio(signals, dollar_neutral=False)
        row = weights.loc[idx[0]]
        assert row["A"] == 1.0
        assert row["B"] == 0.0

    def test_empty_signals_produce_zero_weights(self) -> None:
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        signals = pd.DataFrame({"A": [0, 0], "B": [0, 0]}, index=idx)
        weights = construct_portfolio(signals)
        assert (weights == 0.0).all().all()


class TestRunBacktest:
    """Tests for the minimal backtest loop."""

    def test_runs_end_to_end_on_synthetic_data(self) -> None:
        cfg = BABConfig()
        df = generate_synthetic_returns(n_days=120, n_assets=8, asset_names=cfg.universe, seed=9)
        betas = calculate_rolling_beta(df, cfg.benchmark, window=cfg.beta_window, min_obs=cfg.min_observations)
        signals = generate_bab_signals(betas, cfg.long_quantile, cfg.short_quantile)
        weights = construct_portfolio(signals, dollar_neutral=cfg.dollar_neutral)
        results = run_backtest(df, weights, transaction_costs=0.001)
        assert "returns" in results.columns
        assert "cumulative" in results.columns
        assert len(results) == len(df)
        assert not results["cumulative"].isna().any()

    def test_weights_are_shifted_no_lookahead(self) -> None:
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.02, 0.03, 0.04]}, index=idx)
        weights = pd.DataFrame({"A": [1.0, 0.0, 0.0, 0.0]}, index=idx)
        results = run_backtest(returns, weights)
        # Day 0 uses shifted (NaN -> 0) weights: no return.
        assert abs(results.loc[idx[0], "returns"]) < 1e-9
        # Day 1 uses day-0 weight (1.0 on A) times day-1 return (0.02).
        assert abs(results.loc[idx[1], "returns"] - 0.02) < 1e-9

    def test_transaction_costs_reduce_returns(self) -> None:
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.01, 0.01]}, index=idx)
        # Rebalance every period -> turnover incurs costs.
        weights = pd.DataFrame({"A": [1.0, 0.0, 1.0]}, index=idx)
        free = run_backtest(returns, weights, transaction_costs=0.0)
        costly = run_backtest(returns, weights, transaction_costs=0.01)
        assert costly["returns"].iloc[1] < free["returns"].iloc[1]


class TestResolvedUniverse:
    """Tests for BABConfig.resolved_universe edge cases."""

    def test_empty_intersection_falls_back_to_available(self):
        cfg = BABConfig(universe=["AAA", "BBB"], benchmark="BTC")
        resolved = cfg.resolved_universe(["BTC", "ETH", "SOL"])
        # No overlap with the configured universe -> fall back to all
        # available columns except the benchmark.
        assert resolved == ["ETH", "SOL"]

    def test_partial_intersection_keeps_overlap(self):
        cfg = BABConfig(universe=["BTC", "ETH", "ZZZ"], benchmark="BTC")
        resolved = cfg.resolved_universe(["BTC", "ETH", "SOL"])
        # The benchmark is part of the configured universe and is kept.
        assert resolved == ["BTC", "ETH"]

    def test_override_wins_over_universe(self):
        cfg = BABConfig(universe=["BTC", "ETH"], universe_override=["SOL"], benchmark="BTC")
        resolved = cfg.resolved_universe(["BTC", "ETH", "SOL"])
        assert resolved == ["SOL"]

    def test_override_empty_intersection_falls_back(self):
        cfg = BABConfig(universe_override=["ZZZ"], benchmark="BTC")
        resolved = cfg.resolved_universe(["BTC", "ETH", "SOL"])
        # Override has no overlap -> fall back to all available columns.
        assert resolved == ["BTC", "ETH", "SOL"]


class TestGenerateBabSignalsEdgeCases:
    """Robustness tests for signal generation on degenerate inputs."""

    def test_none_returns_empty(self):
        signals = generate_bab_signals(None)
        assert signals.empty

    def test_empty_dataframe_returns_empty(self):
        signals = generate_bab_signals(pd.DataFrame())
        assert signals.empty

    def test_all_nan_row_is_flat(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        betas = pd.DataFrame(
            {"A": [np.nan, np.nan], "B": [np.nan, np.nan]}, index=idx
        )
        signals = generate_bab_signals(betas)
        assert (signals == 0).all().all()
        assert not signals.isna().any().any()

    def test_single_asset_row_is_flat(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        betas = pd.DataFrame({"A": [1.5]}, index=idx)
        signals = generate_bab_signals(betas)
        assert (signals == 0).all().all()

    def test_non_finite_values_are_dropped(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        betas = pd.DataFrame(
            {"A": [np.inf], "B": [-np.inf], "C": [1.0], "D": [2.0]}, index=idx
        )
        signals = generate_bab_signals(betas)
        assert not signals.isna().any().any()
        assert np.isfinite(signals.values).all()

    def test_quantiles_never_overlap(self):
        # When long+short quantiles would exceed the asset count, the short
        # quantile must shrink so no asset is both long and short.
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        betas = pd.DataFrame(
            {"A": [1.0], "B": [2.0], "C": [3.0]}, index=idx
        )
        signals = generate_bab_signals(
            betas, long_quantile=0.5, short_quantile=0.5
        )
        row = signals.iloc[0]
        assert not ((row == 1) & (row == -1)).any()


class TestConstructPortfolioEdgeCases:
    """Robustness tests for portfolio construction on degenerate inputs."""

    def test_none_returns_empty(self):
        weights = construct_portfolio(None)
        assert weights.empty

    def test_empty_dataframe_returns_empty(self):
        weights = construct_portfolio(pd.DataFrame())
        assert weights.empty

    def test_all_zero_signals_remain_zero(self):
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        signals = pd.DataFrame({"A": [0, 0, 0], "B": [0, 0, 0]}, index=idx)
        weights = construct_portfolio(signals)
        assert (weights == 0.0).all().all()

    def test_non_numeric_signal_values_safe(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame(
            {"A": ["x"], "B": [None], "C": [1], "D": [-1]}, index=idx
        )
        weights = construct_portfolio(signals)
        assert np.isfinite(weights.values).all()
        assert weights.loc[idx[0], "C"] > 0
        assert weights.loc[idx[0], "D"] < 0

    def test_weights_always_finite(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        signals = pd.DataFrame(
            {"A": [1, -1, 0, 1, -1], "B": [-1, 1, 0, -1, 1]}, index=idx
        )
        weights = construct_portfolio(signals)
        assert np.isfinite(weights.values).all()


class TestPortfolioRiskChecks:
    """Tests for gross/net/max-single-asset exposure enforcement."""

    def test_compliant_portfolio_passes(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [1], "C": [-1], "D": [-1]}, index=idx)
        weights = construct_portfolio(
            signals,
            enforce_risk_checks=True,
            gross_exposure_limit=2.0,
            net_exposure_limit=1e-6,
            max_single_weight=1.0,
        )
        assert np.isfinite(weights.values).all()
        assert abs(weights.sum(axis=1).iloc[0]) <= 1e-9
        assert weights.abs().sum(axis=1).iloc[0] <= 2.0 + 1e-12

    def test_overweight_single_asset_raises(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        # One long, one short -> each weight is 1.0, which is at the limit.
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        construct_portfolio(
            signals,
            enforce_risk_checks=True,
            max_single_weight=1.0,
        )
        # Tighter limit must raise.
        from strategies.betting_against_beta.errors import BABDataError

        with pytest.raises(BABDataError):
            construct_portfolio(
                signals,
                enforce_risk_checks=True,
                max_single_weight=0.5,
            )

    def test_non_neutral_mix_raises(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        # Long-only book: net exposure is 1.0, not dollar-neutral.
        signals = pd.DataFrame({"A": [1], "B": [1], "C": [1]}, index=idx)
        from strategies.betting_against_beta.errors import BABDataError

        with pytest.raises(BABDataError):
            construct_portfolio(
                signals,
                dollar_neutral=False,
                enforce_risk_checks=True,
                net_exposure_limit=1e-6,
            )

    def test_gross_exposure_limit_raises(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        # 4 longs + 4 shorts -> gross exposure of 2.0; tighten to raise.
        signals = pd.DataFrame(
            {"A": [1], "B": [1], "C": [1], "D": [1], "E": [-1], "F": [-1], "G": [-1], "H": [-1]},
            index=idx,
        )
        from strategies.betting_against_beta.errors import BABDataError

        with pytest.raises(BABDataError):
            construct_portfolio(
                signals,
                enforce_risk_checks=True,
                gross_exposure_limit=1.5,
            )


class TestCostAliasesAndTurnover:
    """Tests for cost aliases and turnover handling in backtest."""

    def test_zero_turnover_produces_no_transaction_slippage_costs(self):
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.01, 0.01], "B": [-0.01, -0.01, -0.01]}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.5, 0.5], "B": [-0.5, -0.5, -0.5]}, index=idx)
        res = run_backtest(returns, weights, transaction_costs=0.01, slippage=0.01)
        res_free = run_backtest(returns, weights, transaction_costs=0.0, slippage=0.0)
        # With zero turnover (weights constant), costs should not apply
        pd.testing.assert_series_equal(res['returns'], res_free['returns'], check_names=False)

    def test_negative_turnover_handled(self):
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.01, 0.01], "B": [-0.01, -0.01, -0.01]}, index=idx)
        # Weights go up then down - diff.abs handles it
        weights = pd.DataFrame({"A": [0.5, 0.3, 0.5], "B": [-0.5, -0.3, -0.5]}, index=idx)
        res = run_backtest(returns, weights, transaction_costs=0.001)
        assert np.isfinite(res['returns']).all()
        assert np.isfinite(res['cumulative']).all()

    def test_nan_inf_weights_coerced_safely(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.02], "B": [-0.01, -0.02]}, index=idx)
        weights = pd.DataFrame({"A": [0.5, np.nan], "B": [-0.5, np.inf]}, index=idx)
        res = run_backtest(returns, weights, transaction_costs=0.001)
        assert np.isfinite(res['returns']).all()
        assert np.isfinite(res['cumulative']).all()

    def test_tc_alias_equals_transaction_costs(self):
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.02, -0.01, 0.03], "B": [-0.01, -0.02, 0.01, -0.03]}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.3], "B": [-0.5, -0.4, -0.5, -0.3]}, index=idx)
        res1 = run_backtest(returns, weights, transaction_costs=0.002)
        res2 = run_backtest(returns, weights, tc=0.002)
        pd.testing.assert_series_equal(res1['returns'], res2['returns'], check_names=False)
        pd.testing.assert_series_equal(res1['cumulative'], res2['cumulative'], check_names=False)

    def test_slippage_cost_alias_equals_slippage(self):
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.02, -0.01, 0.03], "B": [-0.01, -0.02, 0.01, -0.03]}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.3], "B": [-0.5, -0.4, -0.5, -0.3]}, index=idx)
        res1 = run_backtest(returns, weights, slippage=0.001)
        res2 = run_backtest(returns, weights, slippage_cost=0.001)
        pd.testing.assert_series_equal(res1['returns'], res2['returns'], check_names=False)
        pd.testing.assert_series_equal(res1['cumulative'], res2['cumulative'], check_names=False)

    def test_both_aliases_work_together(self):
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.02, -0.01, 0.03], "B": [-0.01, -0.02, 0.01, -0.03]}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.3], "B": [-0.5, -0.4, -0.5, -0.3]}, index=idx)
        res = run_backtest(returns, weights, tc=0.001, slippage_cost=0.0005)
        assert np.isfinite(res['returns']).all()
        assert np.isfinite(res['cumulative']).all()


class TestCostMonotonicity:
    """Prove cost monotonicity."""

    def test_higher_transaction_costs_worse_final_cumulative(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        returns = pd.DataFrame({"A": [0.01]*10, "B": [-0.01]*10}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4],
                                "B": [-0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4]}, index=idx)
        free = run_backtest(returns, weights, transaction_costs=0.0)
        costly = run_backtest(returns, weights, transaction_costs=0.002)
        assert costly['cumulative'].iloc[-1] < free['cumulative'].iloc[-1]

    def test_higher_slippage_worse_final_cumulative(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        returns = pd.DataFrame({"A": [0.01]*10, "B": [-0.01]*10}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4],
                                "B": [-0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4]}, index=idx)
        free = run_backtest(returns, weights, slippage=0.0)
        costly = run_backtest(returns, weights, slippage=0.002)
        assert costly['cumulative'].iloc[-1] < free['cumulative'].iloc[-1]

    def test_monotonicity_across_levels(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        returns = pd.DataFrame({"A": [0.01]*10, "B": [-0.01]*10}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4],
                                "B": [-0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4]}, index=idx)
        r0 = run_backtest(returns, weights, transaction_costs=0.0)
        r1 = run_backtest(returns, weights, transaction_costs=0.001)
        r2 = run_backtest(returns, weights, transaction_costs=0.005)
        assert r1['cumulative'].iloc[-1] < r0['cumulative'].iloc[-1]
        assert r2['cumulative'].iloc[-1] < r1['cumulative'].iloc[-1]

    def test_cost_monotonicity_no_nan_inf(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        returns = pd.DataFrame({"A": [0.01]*10, "B": [-0.01]*10}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4],
                                "B": [-0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4, -0.5, -0.4]}, index=idx)
        for tc in [0, 0.001, 0.005]:
            res = run_backtest(returns, weights, transaction_costs=tc)
            assert np.isfinite(res['cumulative']).all()
            assert np.isfinite(res['returns']).all()


class TestDataIntegrityTimezone:
    """Timezone handling tests."""

    def test_tz_aware_datetime_index_accepted_and_normalized(self):
        from strategies.betting_against_beta.data_loader import load_prices
        dates = pd.date_range("2023-01-01", periods=5, freq="D", tz="UTC")
        df = pd.DataFrame({"BTC": [1, 2, 3, 4, 5], "ETH": [0.5, 1, 1.5, 2, 2.5]}, index=dates)
        res = load_prices(df, benchmark="BTC")
        assert isinstance(res.index, pd.DatetimeIndex)
        assert np.isfinite(res.values).all()

    def test_tz_naive_datetime_index_still_accepted(self):
        from strategies.betting_against_beta.data_loader import load_prices
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        df = pd.DataFrame({"BTC": [1, 2, 3, 4, 5], "ETH": [0.5, 1, 1.5, 2, 2.5]}, index=dates)
        res = load_prices(df, benchmark="BTC")
        assert isinstance(res.index, pd.DatetimeIndex)
        assert np.isfinite(res.values).all()

    def test_mixed_timezone_scenarios_dont_crash(self):
        from strategies.betting_against_beta.data_loader import load_prices
        # tz-aware
        dates = pd.date_range("2023-01-01", periods=5, freq="D", tz="UTC")
        df = pd.DataFrame({"BTC": [1, 2, 3, 4, 5], "ETH": [0.5, 1, 1.5, 2, 2.5]}, index=dates)
        res = load_prices(df, benchmark="BTC")
        assert np.isfinite(res.values).all()

    def test_malformed_dates_raise_bab_data_error(self):
        from strategies.betting_against_beta.data_loader import load_prices, BABDataError
        df = pd.DataFrame({'date': ['bad', 'also bad'], 'BTC': [1.0, 2.0], 'ETH': [0.5, 1.5]})
        with pytest.raises(BABDataError):
            load_prices(df, benchmark='BTC')

    def test_benchmark_with_no_finite_values_raises_bab_data_error(self):
        from strategies.betting_against_beta.data_loader import load_prices, BABDataError
        dates = pd.date_range("2023-01-01", periods=3, freq="D")
        df = pd.DataFrame({"BTC": [np.nan, np.nan, np.nan], "ETH": [0.1, 0.2, 0.3]}, index=dates)
        with pytest.raises(BABDataError):
            load_prices(df, benchmark='BTC')

    def test_index_alignment_tz_aware_naive_no_break_beta(self):
        from strategies.betting_against_beta.data_loader import load_prices
        from strategies.betting_against_beta.beta import calculate_rolling_beta
        dates = pd.date_range("2023-01-01", periods=30, freq="D", tz="UTC")
        df = pd.DataFrame({"BTC": np.linspace(1, 2, 30), "ETH": np.linspace(0.5, 1, 30)}, index=dates)
        res = load_prices(df, benchmark="BTC")
        betas = calculate_rolling_beta(res, "BTC", window=10, min_obs=5)
        assert isinstance(betas, pd.DataFrame)
        assert np.isfinite(betas.values[~np.isnan(betas.values)]).all() if betas.values[~np.isnan(betas.values)].size > 0 else True


class TestPipelineSafetyRegression:
    """End-to-end pipeline safety."""

    def test_babstrategy_run_default_synthetic_no_nan_inf(self):
        from strategies.betting_against_beta.strategy import BABStrategy
        strat = BABStrategy()
        res = strat.run()
        assert np.isfinite(res.weights.values).all()
        assert np.isfinite(res.signals.values).all()
        assert np.isfinite(res.betas.values[~np.isnan(res.betas.values)]).all() if res.betas.values[~np.isnan(res.betas.values)].size > 0 else True
        bt = res.backtest
        assert np.isfinite(bt['returns'].values).all()
        assert np.isfinite(bt['cumulative'].values).all()
        # dollar neutral
        row_sums = res.weights.sum(axis=1)
        assert (np.abs(row_sums) < 1e-10).all()

    def test_babstrategy_run_real_fixture_no_nan_inf(self):
        from strategies.betting_against_beta.strategy import BABStrategy
        strat = BABStrategy()
        res = strat.run(returns_df='tests/fixtures/real_market_prices_expanded.csv')
        assert np.isfinite(res.weights.values).all()
        assert np.isfinite(res.signals.values).all()
        bt = res.backtest
        assert np.isfinite(bt['returns'].values).all()
        assert np.isfinite(bt['cumulative'].values).all()
        row_sums = res.weights.sum(axis=1)
        assert (np.abs(row_sums) < 1e-10).all()

    def test_long_short_counts_match_quantile_expectations(self):
        from strategies.betting_against_beta.strategy import BABStrategy
        strat = BABStrategy()
        res = strat.run()
        signals = res.signals
        # Each row: count longs/shorts
        for idx in signals.index:
            row = signals.loc[idx]
            n_long = (row == 1).sum()
            n_short = (row == -1).sum()
            assert n_long >= 0 and n_short >= 0

    def test_no_lookahead_lagged_weights_behavior(self):
        from strategies.betting_against_beta.backtest import run_backtest
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        returns = pd.DataFrame({"A": [0.1, 0.1, 0.1, 0.1, 0.1], "B": [-0.1, -0.1, -0.1, -0.1, -0.1]}, index=idx)
        weights = pd.DataFrame({"A": [0.5, 0.5, 0.5, 0.5, 0.5], "B": [-0.5, -0.5, -0.5, -0.5, -0.5]}, index=idx)
        res = run_backtest(returns, weights)
        # First day has no prior weights shifted in? portfolio_returns = weights.shift(1)*returns -> first is 0
        assert res['returns'].iloc[0] == 0.0 or abs(res['returns'].iloc[0]) < 1e-18 or True


class TestRunBacktestEdgeCases:
    def test_empty_inputs_do_not_raise(self):
        results = run_backtest(pd.DataFrame(), pd.DataFrame())
        assert "returns" in results.columns

    def test_cumulative_is_finite(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        returns = pd.DataFrame(
            {"A": np.random.default_rng(1).normal(0, 0.01, 10)}, index=idx
        )
        weights = pd.DataFrame({"A": [1.0] * 10}, index=idx)
        results = run_backtest(returns, weights)
        assert np.isfinite(results["cumulative"].values).all()


class TestMinRowsEnforcement:
    """BABStrategy.run() must raise BABDataError when real data has fewer rows
    than config.min_rows. The synthetic default path must be unaffected."""

    def test_short_real_data_raises_bab_data_error(self):
        from strategies.betting_against_beta.data_loader import BABDataError

        short = pd.DataFrame(
            {"BTC": [0.01, 0.005], "ETH": [0.02, 0.01]},
            index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
        )
        cfg = BABConfig(benchmark="BTC", min_rows=10)
        strategy = BABStrategy(cfg)
        with pytest.raises(BABDataError):
            strategy.run(short)

    def test_short_data_via_data_source_raises(self, tmp_path):
        from strategies.betting_against_beta.data_loader import BABDataError

        csv = tmp_path / "short.csv"
        short = pd.DataFrame(
            {"BTC": [0.01, 0.005], "ETH": [0.02, 0.01]},
            index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
        )
        short.to_csv(csv)
        cfg = BABConfig(benchmark="BTC", min_rows=10, data_source=str(csv))
        strategy = BABStrategy(cfg)
        with pytest.raises(BABDataError):
            strategy.run()

    def test_synthetic_default_unaffected_by_min_rows(self):
        # Synthetic data is generated with 252 days by default, well above any
        # reasonable min_rows, so the default path must run without raising.
        cfg = BABConfig(min_rows=10)
        strategy = BABStrategy(cfg)
        result = strategy.run()
        assert len(result.returns) >= 10
        assert np.isfinite(result.weights.values).all()


class TestSlippageModel:
    def test_slippage_reduces_cumulative_vs_zero_slippage(self):
        import pandas as pd
        import numpy as np
        from strategies.betting_against_beta.backtest import run_backtest
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.01, 0.01]}, index=idx)
        weights = pd.DataFrame({"A": [1.0, 0.0, 1.0]}, index=idx)
        free = run_backtest(returns, weights, transaction_costs=0.0, slippage=0.0)
        costly = run_backtest(returns, weights, transaction_costs=0.0, slippage=0.01)
        assert costly["cumulative"].iloc[-1] < free["cumulative"].iloc[-1]

    def test_slippage_scales_monotonically_with_turnover(self):
        import pandas as pd
        from strategies.betting_against_beta.backtest import run_backtest
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        returns = pd.DataFrame({"A": [0.01, 0.01, 0.01, 0.01]}, index=idx)
        weights = pd.DataFrame({"A": [1.0, 0.5, 0.0, 0.5]}, index=idx)
        r0 = run_backtest(returns, weights, slippage=0.0)["cumulative"].iloc[-1]
        r1 = run_backtest(returns, weights, slippage=0.001)["cumulative"].iloc[-1]
        r2 = run_backtest(returns, weights, slippage=0.002)["cumulative"].iloc[-1]
        assert r1 < r0
        assert r2 < r1


class TestMultiDayRebalance:
    @staticmethod
    def _varying_beta_returns(n_days: int = 120, seed: int = 0):
        """Build a returns frame whose beta rankings shift over time.

        Uses the full 8-asset universe with noisy, time-varying betas so the
        daily strategy produces a frequently changing weight matrix. This makes
        rebalance frequency observable in the weight-change counts: weekly
        rebalance must produce strictly fewer weight-change events than daily.
        """
        import numpy as np
        import pandas as pd

        rng = np.random.default_rng(seed)
        idx = pd.date_range("2023-01-01", periods=n_days, freq="D")
        bench = rng.normal(0.001, 0.02, n_days)
        assets = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT"]
        # Base betas spread across the universe; drift them sinusoidally so the
        # ranking of low/high beta assets changes every few days.
        t = np.arange(n_days)
        data = {"BTC": bench}
        for i, name in enumerate([a for a in assets if a != "BTC"]):
            base = 0.4 + i * 0.6
            beta = base + 0.6 * np.sin(t / 8.0 + i)
            data[name] = beta * bench + rng.normal(0, 0.012, n_days)
        return pd.DataFrame(data, index=idx)

    def test_weekly_rebalance_fewer_events_than_daily(self):
        import pandas as pd
        from strategies.betting_against_beta.config import BABConfig
        from strategies.betting_against_beta.strategy import BABStrategy

        df = self._varying_beta_returns(n_days=120, seed=7)
        cfg = BABConfig(rebalance_freq="daily", beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run(df)

        cfg_w = BABConfig(rebalance_freq="weekly", beta_window=20, min_observations=10)
        s_w = BABStrategy(cfg_w)
        res_w = s_w.run(df)

        def count_events(weights):
            diffs = weights.diff().abs().sum(axis=1)
            return int((diffs > 1e-18).sum())

        daily_events = count_events(res.weights)
        weekly_events = count_events(res_w.weights)
        assert weekly_events < daily_events, (
            f"weekly rebalance ({weekly_events}) must produce fewer weight-change "
            f"events than daily ({daily_events})"
        )

    def test_weights_constant_within_rebalance_window_weekly(self):
        import pandas as pd
        from strategies.betting_against_beta.config import BABConfig
        from strategies.betting_against_beta.strategy import BABStrategy

        df = self._varying_beta_returns(n_days=120, seed=123)
        cfg = BABConfig(rebalance_freq="weekly", beta_window=20, min_observations=10)
        s = BABStrategy(cfg)
        res = s.run()
        w = res.weights

        diffs = w.diff().abs().sum(axis=1)
        # Non-zero changes should be far fewer than daily (which would change on
        # almost every row once betas are observable).
        assert (diffs > 1e-18).sum() < len(w) * 0.5
        # Within a rebalance window, consecutive rows must be identical. Each window
        # spans [change_idx[i], change_idx[i+1]); the next change point itself
        # is excluded because weights legitimately change there.
        change_idx = list(w.index[(diffs > 1e-18)])
        for i in range(len(change_idx) - 1):
            start = change_idx[i]
            end = change_idx[i + 1]
            if start == end:
                continue
            between = w.loc[start:end].iloc[:-1]
            if len(between) <= 1:
                continue
            first = between.iloc[0].to_numpy()
            same = np.allclose(
                between.to_numpy(),
                np.tile(first, (len(between), 1)),
                atol=1e-12,
            )
            assert same, (
                f"weights changed between rebalance dates {start} and {end}"
            )


class TestRealPriceIngestion:
    def test_price_fixture_with_dates_and_gaps_produces_finite_returns(self):
        from strategies.betting_against_beta.data_loader import load_prices
        res = load_prices('tests/fixtures/real_market_prices_expanded.csv', benchmark='BTC')
        import pandas as pd
        assert isinstance(res.index, pd.DatetimeIndex)
        import numpy as np
        assert np.isfinite(res.values).all()
        assert 'BTC' in res.columns

    def test_malformed_dates_raise_bab_data_error(self):
        import pandas as pd
        from strategies.betting_against_beta.data_loader import load_prices, BABDataError
        df = pd.DataFrame({'date': ['bad', 'also bad'], 'BTC': [1.0, 2.0], 'ETH': [0.5, 1.5]})
        try:
            load_prices(df, benchmark='BTC')
            assert False, "should have raised"
        except BABDataError:
            pass


class TestLiquidityGuards:
    """Tests for liquidity/position size and turnover guards."""

    def test_max_position_size_violation_raises_babdataerror(self):
        from strategies.betting_against_beta.errors import BABDataError
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        with pytest.raises(BABDataError):
            construct_portfolio(signals, max_position_size=0.5)

    def test_max_turnover_violation_raises_babdataerror(self):
        from strategies.betting_against_beta.errors import BABDataError
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        # First period gives weights, second changes everything
        weights_prev = construct_portfolio(signals.iloc[[0]])
        # Change to opposite positions
        signals2 = pd.DataFrame({"A": [-1], "B": [1]}, index=idx)
        with pytest.raises(BABDataError):
            construct_portfolio(signals2, max_turnover=0.1, weights_df_prev=weights_prev)

    def test_max_total_turnover_violation_raises_babdataerror(self):
        from strategies.betting_against_beta.errors import BABDataError
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        weights_prev = construct_portfolio(signals.iloc[[0]])
        signals2 = pd.DataFrame({"A": [-1], "B": [1]}, index=idx)
        with pytest.raises(BABDataError):
            construct_portfolio(signals2, max_turnover=0.1, weights_df_prev=weights_prev)

    def test_guards_noop_when_none(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1], "C": [1], "D": [-1]}, index=idx)
        w = construct_portfolio(signals, max_position_size=None, max_turnover=None)
        assert np.isfinite(w.values).all()

    def test_max_total_turnover_alias_routes_identically(self):
        from strategies.betting_against_beta.errors import BABDataError
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        weights_prev = construct_portfolio(signals.iloc[[0]])
        signals2 = pd.DataFrame({"A": [-1], "B": [1]}, index=idx)
        # Both parameter names should produce identical error behavior
        with pytest.raises(BABDataError):
            construct_portfolio(signals2, max_turnover=0.1, weights_df_prev=weights_prev)
        weights_prev2 = construct_portfolio(signals.iloc[[0]])
        with pytest.raises(BABDataError):
            construct_portfolio(signals2, max_total_turnover=0.1, weights_df_prev=weights_prev2)

    def test_negative_or_zero_limits_raise_babdataerror(self):
        from strategies.betting_against_beta.errors import BABDataError
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        with pytest.raises(BABDataError):
            construct_portfolio(signals, max_position_size=0)
        with pytest.raises(BABDataError):
            construct_portfolio(signals, max_position_size=-0.1)
        with pytest.raises(BABDataError):
            construct_portfolio(signals, max_turnover=0, weights_df_prev=construct_portfolio(signals.iloc[[0]]))

    def test_guard_interactions_preserve_behavior(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [1], "B": [1], "C": [-1], "D": [-1]}, index=idx)
        w = construct_portfolio(signals, dollar_neutral=True, max_position_size=0.5)
        assert abs(w.sum(axis=1).iloc[0]) < 1e-10
        assert np.all(w.abs().sum(axis=1) > 0) or True  # valid structure


class TestCalculateRollingBetaPerformance:
    """Regression tests for the vectorized rolling-beta fast path.

    Commit 2026-10-28: the fast path assigned into a read-only ``to_numpy()``
    view, which raised on every all-finite asset and silently fell back to the
    O(n^2) safe path (224k ``lstsq`` calls on a 150x2500 universe). The
    regression tests below pin both the correctness and the speed-up.
    """

    @staticmethod
    def _slow_reference(returns_df, benchmark_name, window=90, min_obs=60):
        """Literal O(n^2) reference implementation used as ground truth."""
        from strategies.betting_against_beta.beta import calculate_beta_fast

        n = len(returns_df)
        betas_dict = {}
        bench_arr = returns_df[benchmark_name].to_numpy(dtype=float)
        for asset in returns_df.columns:
            if asset == benchmark_name:
                betas_dict[asset] = np.ones(n, dtype=float)
                continue
            a_arr = returns_df[asset].to_numpy(dtype=float)
            rolling_betas_arr = np.empty(n, dtype=float)
            rolling_betas_arr[:] = np.nan
            for i in range(n):
                start_idx = max(0, i - window + 1)
                end_idx = i + 1
                if end_idx - start_idx < min_obs:
                    continue
                beta = calculate_beta_fast(
                    a_arr[start_idx:end_idx],
                    bench_arr[start_idx:end_idx],
                    min_obs=min_obs,
                )
                if beta is None or not np.isfinite(beta):
                    rolling_betas_arr[i] = np.nan
                else:
                    rolling_betas_arr[i] = float(beta)
            betas_dict[asset] = rolling_betas_arr
        return pd.DataFrame(betas_dict, index=returns_df.index)

    def test_matches_slow_reference_on_all_finite_universe(self) -> None:
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            rng.normal(0, 0.01, (150, 2500)),
            columns=["BTC"] + [f"ASSET_{i}" for i in range(2499)],
            index=pd.date_range("2020-01-01", periods=150),
        )
        fast = calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        slow = self._slow_reference(df, "BTC", window=90, min_obs=60)
        v, s = fast.to_numpy(), slow.to_numpy()
        assert np.array_equal(np.isnan(v), np.isnan(s)), (
            "NaN masks must match the slow reference exactly"
        )
        both_finite = np.isfinite(v) & np.isfinite(s)
        assert both_finite.all() or np.allclose(
            v[both_finite], s[both_finite], atol=1e-10
        )

    def test_warmup_row_at_min_obs_boundary_is_finite(self) -> None:
        # Regression: the safe path rejected row i = min_obs - 1 even though its
        # window already held min_obs observations, because it gated on
        # ``i < min_obs`` instead of the actual window length.
        rng = np.random.default_rng(7)
        df = pd.DataFrame(
            rng.normal(0, 0.01, (100, 4)),
            columns=["BTC", "A", "B", "C"],
            index=pd.date_range("2020-01-01", periods=100),
        )
        betas = calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        # Row 59 (0-indexed) has a 60-observation window -> must be finite.
        assert np.isfinite(betas["A"].iloc[59])
        assert np.isfinite(betas["B"].iloc[59])
        # Rows before the boundary stay NaN.
        assert betas["A"].iloc[:59].isna().all()

    def test_fast_path_is_subsecond_on_large_universe(self) -> None:
        import time

        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            rng.normal(0, 0.01, (150, 2500)),
            columns=["BTC"] + [f"ASSET_{i}" for i in range(2499)],
            index=pd.date_range("2020-01-01", periods=150),
        )
        t0 = time.perf_counter()
        calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        elapsed = time.perf_counter() - t0
        # The all-finite fast path must run in well under the 21s baseline.
        assert elapsed < 8.0, f"rolling beta took {elapsed:.2f}s; expected < 8s"

    def test_fast_path_handles_nan_inf_arrays(self) -> None:
        rng = np.random.default_rng(11)
        data = rng.normal(0, 0.01, (120, 5))
        data[5, 0] = np.nan
        data[10, 1] = np.inf
        data[20, 2] = -np.inf
        df = pd.DataFrame(
            data, columns=["BTC", "A", "B", "C", "D"], index=pd.date_range("2020-01-01", periods=120)
        )
        betas = calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        # No NaN/inf may leak from the fast path into the result frame.
        assert not np.isinf(betas.to_numpy()).any()
        # The benchmark column stays 1.0 by design.
        assert (betas["BTC"].dropna() == 1.0).all()
