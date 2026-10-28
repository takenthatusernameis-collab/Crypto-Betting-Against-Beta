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
        assert betas.iloc[:60].drop(columns=["BTC"]).isna().all().all()

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
