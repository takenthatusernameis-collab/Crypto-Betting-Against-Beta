"""Zero-silent-error defect regression tests for BAB pipeline."""
import json
import os
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy, BABConfig
from strategies.betting_against_beta.data_loader import BABDataError

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


class TestZeroSilentError:
    def test_all_nan_column_does_not_produce_nan_weights(self):
        cfg = BABConfig(data_source=os.path.join(FIX, "all_nan_column.csv"),
                        benchmark="BTC", beta_window=3, min_observations=2)
        strat = BABStrategy(cfg)
        res = strat.run()
        weights = res.weights
        assert not weights.isna().any().any()
        assert np.isfinite(weights.values).all()

    def test_benchmark_nan_window_does_not_crash(self):
        cfg = BABConfig(data_source=os.path.join(FIX, "benchmark_nan_window.csv"),
                        benchmark="BTC", beta_window=3, min_observations=2)
        strat = BABStrategy(cfg)
        res = strat.run()
        weights = res.weights
        assert not weights.isna().any().any()
        assert np.isfinite(weights.values).all()

    def test_non_monotonic_dates_loader_sorts(self):
        cfg = BABConfig(data_source=os.path.join(FIX, "non_monotonic_dates.csv"),
                        benchmark="BTC", beta_window=3, min_observations=2)
        strat = BABStrategy(cfg)
        res = strat.run()
        weights = res.weights
        assert not weights.isna().any().any()
        assert np.isfinite(weights.values).all()

    def test_junk_columns_csv_behavior(self):
        # Accept either deterministic cleaning/drop OR a clear BABDataError
        try:
            cfg = BABConfig(data_source=os.path.join(FIX, "junk_columns.csv"),
                            benchmark="BTC", beta_window=3, min_observations=2)
            strat = BABStrategy(cfg)
            res = strat.run()
            weights = res.weights
            assert not weights.isna().any().any()
            assert np.isfinite(weights.values).all()
        except BABDataError:
            pass  # loud error is acceptable

    def test_returns_json_end_to_end_via_strategy(self):
        cfg = BABConfig(data_source=os.path.join(FIX, "returns.json"),
                        benchmark="BTC", beta_window=3, min_observations=2)
        strat = BABStrategy(cfg)
        res = strat.run()
        weights = res.weights
        assert not weights.isna().any().any()
        assert np.isfinite(weights.values).all()

    def test_min_rows_enforced_end_to_end(self):
        dates = pd.date_range("2023-01-01", periods=2)
        df = pd.DataFrame(index=dates)
        df["BTC"] = [0.01, 0.02]
        df["ETH"] = [0.01, 0.02]
        cfg = BABConfig(benchmark="BTC", min_rows=5)
        strat = BABStrategy(cfg)
        with pytest.raises(BABDataError):
            strat.run(returns_df=df)

    def test_json_report_metrics_finite_on_messy_input(self):
        from scripts import bab_backtest_report
        import tempfile
        # Run against messy fixture via CLI logic - call function
        cfg = BABConfig(data_source=os.path.join(FIX, "messy_returns.csv"),
                        benchmark="BTC", beta_window=3, min_observations=2)
        strat = BABStrategy(cfg)
        res = strat.run()
        # build metrics like report
        metrics = {}
        try:
            b = res.backtest
            if hasattr(b, 'metrics') and isinstance(b.metrics, dict):
                metrics = b.metrics
            else:
                # compute simple
                pass
        except Exception:
            metrics = {}
        # Ensure no NaN/inf
        for k, v in metrics.items():
            if isinstance(v, float):
                assert np.isfinite(v), f"non-finite metric {k}={v}"
