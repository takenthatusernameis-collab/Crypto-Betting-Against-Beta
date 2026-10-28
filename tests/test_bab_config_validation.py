"""Tests for BABConfig range validation (Phase 4, task 10 of the focus campaign).

BABConfig must reject out-of-range windows, quantiles, costs, and seeds with a
clear ``BABConfigError`` rather than silently producing degenerate pipelines.
"""

from __future__ import annotations

import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError


class TestConfigRangeValidation:
    def test_default_config_is_valid(self):
        cfg = BABConfig()
        assert cfg.beta_window == 90
        assert cfg.min_observations == 60
        assert cfg.min_rows == 2

    def test_beta_window_must_be_positive_int(self):
        with pytest.raises(BABConfigError):
            BABConfig(beta_window=0)
        with pytest.raises(BABConfigError):
            BABConfig(beta_window=-5)
        with pytest.raises(BABConfigError):
            BABConfig(beta_window=90.5)

    def test_min_observations_must_be_positive_int(self):
        with pytest.raises(BABConfigError):
            BABConfig(min_observations=0)
        with pytest.raises(BABConfigError):
            BABConfig(min_observations=-1)

    def test_min_rows_must_be_positive_int(self):
        with pytest.raises(BABConfigError):
            BABConfig(min_rows=0)

    def test_synthetic_n_days_minimum(self):
        with pytest.raises(BABConfigError):
            BABConfig(synthetic_n_days=1)

    def test_quantiles_must_be_in_open_interval(self):
        with pytest.raises(BABConfigError):
            BABConfig(long_quantile=0.0)
        with pytest.raises(BABConfigError):
            BABConfig(long_quantile=1.0)
        with pytest.raises(BABConfigError):
            BABConfig(short_quantile=1.5)
        with pytest.raises(BABConfigError):
            BABConfig(short_quantile=-0.1)

    def test_costs_and_slippage_non_negative(self):
        with pytest.raises(BABConfigError):
            BABConfig(transaction_costs=-0.001)
        with pytest.raises(BABConfigError):
            BABConfig(slippage=-0.001)

    def test_optional_constraints_positive_when_set(self):
        with pytest.raises(BABConfigError):
            BABConfig(max_turnover=0.0)
        with pytest.raises(BABConfigError):
            BABConfig(max_position_size=-1.0)
        with pytest.raises(BABConfigError):
            BABConfig(max_total_turnover=0.0)
        with pytest.raises(BABConfigError):
            BABConfig(rolling_min_window=0)

    def test_benchmark_and_rebalance_freq_non_empty(self):
        with pytest.raises(BABConfigError):
            BABConfig(benchmark="")
        with pytest.raises(BABConfigError):
            BABConfig(rebalance_freq="")

    def test_explicit_valid_overrides_accepted(self):
        cfg = BABConfig(
            beta_window=30,
            min_observations=20,
            min_rows=10,
            long_quantile=0.25,
            short_quantile=0.25,
            transaction_costs=0.001,
            slippage=0.0005,
            synthetic_n_days=500,
            synthetic_seed=7,
            max_turnover=0.5,
            max_position_size=0.2,
        )
        assert cfg.beta_window == 30
        assert cfg.transaction_costs == 0.001

    def test_resolved_universe_intersects_with_columns(self):
        cfg = BABConfig(universe=["BTC", "ETH", "SOL"])
        assert cfg.resolved_universe(["BTC", "ETH", "SOL", "BNB"]) == ["BTC", "ETH", "SOL"]
        assert cfg.resolved_universe(["BTC", "ETH"]) == ["BTC", "ETH"]

    def test_resolved_universe_falls_back_to_available_excluding_benchmark(self):
        # When the configured universe has no overlap with available columns,
        # the fallback derives the tradable set from available columns,
        # excluding the benchmark.
        cfg = BABConfig(universe=["DOGE"], benchmark="BTC")
        assert cfg.resolved_universe(["BTC", "ETH", "SOL"]) == ["ETH", "SOL"]

    def test_resolved_universe_override_wins(self):
        cfg = BABConfig(universe_override=["BTC", "ETH"])
        assert cfg.resolved_universe(["BTC", "ETH", "SOL"]) == ["BTC", "ETH"]

    def test_resolved_universe_override_falls_back_to_available(self):
        cfg = BABConfig(universe_override=["BTC", "ETH"])
        assert cfg.resolved_universe(["SOL"]) == ["SOL"]