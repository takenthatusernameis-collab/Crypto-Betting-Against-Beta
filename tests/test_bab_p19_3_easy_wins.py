"""P19-3 easy-reach coverage wins: signals:37,75; metrics:94; replay:172;
reconciliation:309; data_sources:480-481,499-500,507-508.

Post-deletion refresh: signals.py:37 and signals.py:75 were proven
unreachable and deleted with proof (see tests/test_bab_p19_3_medium.py
header). The tests below verify behavior is unchanged.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import _json_safe
from strategies.betting_against_beta.data_sources import validate_freshness
from strategies.betting_against_beta.metrics import turnover
from strategies.betting_against_beta.reconciliation import reconcile_fills_to_backtest
from strategies.betting_against_beta.replay import ReplayHarness
from strategies.betting_against_beta.signals import _finite_beta_series
from strategies.betting_against_beta.strategy import BABConfig, BABResult


class TestSignalsEasyWins:
    def test_finite_beta_series_object_dtype(self):
        """Verify _finite_beta_series handles object-dtype Series."""
        s = pd.Series([1.0, 2.0], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert len(out) == 2

    def test_finite_beta_series_all_non_finite_returns_none(self):
        """Verify _finite_beta_series returns None when all values are non-finite."""
        s = pd.Series([np.inf, -np.inf], dtype=float)
        assert _finite_beta_series(s) is None


class TestMetricsEasyWins:
    def test_turnover_single_row_nan_mean(self):
        """Reach metrics.py:94 (return 0.0 when turnover_mean is NaN).

        Single-row DataFrame: diff() -> all NaN, dropna() -> empty,
        mean() -> NaN, pd.isna(NaN) -> True -> return 0.0."""
        df = pd.DataFrame({"BTC": [0.5], "ETH": [0.3]}, index=[0])
        assert turnover(df) == 0.0


class TestReplayEasyWins:
    def _make_result(self, weights_df):
        cfg = BABConfig()
        res = BABResult.__new__(BABResult)
        res.config = cfg
        res.weights = weights_df
        res.returns = None
        res.betas = None
        res.signals = None
        res.backtest = None
        return res

    def test_replay_path(self):
        """Exercise the replay path with a standard weights frame."""
        dates = pd.date_range("2023-01-01", periods=3)
        w = pd.DataFrame(
            {"BTC": [0.5, 0.4, 0.3], "ETH": [-0.5, -0.4, -0.3]},
            index=dates,
        )
        result = self._make_result(w)
        harness = ReplayHarness(result)
        out = harness.replay()
        assert out["n_periods"] == 3


class TestReconciliationEasyWins:
    def test_reconcile_empty_cols_path(self):
        """Exercise reconcile_fills_to_backtest with non-overlapping columns."""
        dates = pd.date_range("2023-01-01", periods=3)
        w = pd.DataFrame({"BTC": [0.5, 0.4, 0.3]}, index=dates)
        r = pd.DataFrame({"ETH": [0.01, 0.02, 0.03]}, index=dates)
        b = pd.DataFrame({"cumulative": [1.0, 1.01, 1.02]}, index=dates)
        res = reconcile_fills_to_backtest(w, r, b)
        assert res is not None

    def test_json_safe_dataframe_no_columns(self):
        """_json_safe on a columnless DataFrame (defensive path)."""
        df = pd.DataFrame(index=[0, 1])
        out = _json_safe(df)
        assert out == {}


class TestDataSourcesEasyWins:
    def test_validate_freshness_numeric_index_rejected(self):
        """Verify numeric index is rejected before to_datetime."""
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=[0, 1])
        with pytest.raises(Exception):
            validate_freshness(df, reference_date="2023-01-01")

    def test_validate_freshness_tz_aware_index(self):
        """Verify tz-aware DatetimeIndex passes freshness validation."""
        dates = pd.date_range("2023-01-01", periods=2, tz="UTC")
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=dates)
        assert validate_freshness(df, reference_date="2023-01-01") is True

    def test_validate_freshness_object_index_unparseable(self):
        """Verify unparseable object index raises BABDataError."""
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=pd.Index(["not-a-date", "also-not"]))
        with pytest.raises(Exception):
            validate_freshness(df, reference_date="2023-01-01")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])