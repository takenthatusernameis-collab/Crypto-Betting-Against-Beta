from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import sizing
from strategies.betting_against_beta import quality
from strategies.betting_against_beta.errors import BABDataError


class TestSizingMore:
    def test_empty_signals(self):
        out = sizing.apply_position_sizing(pd.DataFrame())
        assert out.empty

    def test_none_signals(self):
        out = sizing.apply_position_sizing(None)
        assert isinstance(out, pd.DataFrame)

    def test_returns_none_path(self):
        dates = pd.date_range("2023-01-01", periods=5)
        signals = pd.DataFrame({"BTC": [1, -1, 0, 1, -1]}, index=dates)
        out = sizing.apply_position_sizing(signals, returns=None, sizer=None)
        assert isinstance(out, pd.DataFrame)
        assert out.shape == signals.shape

    def test_no_common_index(self):
        dates1 = pd.date_range("2023-01-01", periods=5)
        dates2 = pd.date_range("2024-01-01", periods=5)
        signals = pd.DataFrame({"BTC": [1, -1, 0, 1, -1]}, index=dates1)
        returns = pd.DataFrame({"BTC": [0.01, -0.01, 0.0, 0.01, -0.01]}, index=dates2)
        out = sizing.apply_position_sizing(signals, returns=returns, sizer="kelly")
        assert isinstance(out, pd.DataFrame)

    def test_missing_columns_filled(self):
        dates = pd.date_range("2023-01-01", periods=10)
        signals = pd.DataFrame({"BTC": [1]*5 + [-1]*5, "ETH": [0]*10}, index=dates)
        returns = pd.DataFrame({"BTC": np.random.default_rng(123).normal(0,0.01,10)}, index=dates)
        out = sizing.apply_position_sizing(signals, returns=returns, sizer="kelly")
        assert "ETH" in out.columns

    def test_risk_parity_without_target_vol(self):
        dates = pd.date_range("2023-01-01", periods=80)
        rng = np.random.default_rng(42)
        signals = pd.DataFrame({"BTC": rng.choice([1,-1,0],80), "ETH": rng.choice([1,-1,0],80)}, index=dates)
        returns = pd.DataFrame({"BTC": rng.normal(0,0.01,80), "ETH": rng.normal(0,0.012,80)}, index=dates)
        out = sizing.apply_position_sizing(signals, returns=returns, sizer="risk_parity")
        assert np.all(np.isfinite(out.values))

    def test_all_sizer_shorthands(self):
        dates = pd.date_range("2023-01-01", periods=80)
        rng = np.random.default_rng(7)
        signals = pd.DataFrame({"BTC": rng.choice([1,-1,0],80)}, index=dates)
        returns = pd.DataFrame({"BTC": rng.normal(0,0.01,80)}, index=dates)
        for name in ["kelly", "kelly_fraction", "vol_target", "volatility_target", "voltarget", "risk_parity", "riskparity", "rp"]:
            out = sizing.apply_position_sizing(signals, returns=returns, sizer=name)
            assert np.all(np.isfinite(out.values))

    def test_unknown_sizer_raises(self):
        dates = pd.date_range("2023-01-01", periods=5)
        signals = pd.DataFrame({"BTC": [1,-1,0,1,-1]}, index=dates)
        returns = pd.DataFrame({"BTC": [0.01,-0.01,0,0.01,-0.01]}, index=dates)
        with pytest.raises(sizing.BABSizingError):
            sizing.apply_position_sizing(signals, returns=returns, sizer="bad")

    def test_validation_errors(self):
        with pytest.raises(sizing.BABSizingError):
            sizing.KellySizer(lookback=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.KellySizer(max_leverage=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.KellySizer(fraction=-1)
        with pytest.raises(sizing.BABSizingError):
            sizing.VolatilityTargetSizer(target_vol=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.VolatilityTargetSizer(lookback=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.VolatilityTargetSizer(annualize=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.VolatilityTargetSizer(max_leverage=-1)
        with pytest.raises(sizing.BABSizingError):
            sizing.RiskParitySizer(lookback=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.RiskParitySizer(max_leverage=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.RiskParitySizer(target_vol=0)
        with pytest.raises(sizing.BABSizingError):
            sizing.RiskParitySizer(annualize=0)

    def test_frozen_sizers(self):
        k = sizing.KellySizer()
        with pytest.raises(AttributeError):
            k.lookback = 10


class TestQualityMore:
    def test_invalid_input(self):
        assert quality.data_quality_report(None)["error"] == "invalid_input"
        assert quality.data_quality_report("x")["error"] == "invalid_input"

    def test_non_datetime_index_gaps_dict(self):
        df = pd.DataFrame({"A": [1,2,3,4]}, index=[0,1,2,3])
        rep = quality.data_quality_report(df)
        assert rep["index"]["gaps"] == {"count": 0}

    def test_non_datetime_gaps_function(self):
        df = pd.DataFrame({"A": [1,2,3,4]})
        out = quality.detect_gaps(df)
        assert out == {"gaps": [], "count": 0}

    def test_gaps_with_zero_median(self):
        idx = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame({"A": [1,2,3]}, index=idx)
        # create zero gaps? not possible, but test function
        out = quality.detect_gaps(df)
        assert "gaps" in out

    def test_outliers_edges(self):
        df = pd.DataFrame({"A": [1.0, 1.0, 1.0]})  # < 3 finite? 3 values
        out = quality.detect_outliers(df, method="zscore")
        # constant std 0 gives empty
        assert out["A"]["count"] == 0
        df2 = pd.DataFrame({"A": [np.nan, np.nan, np.nan]})
        out2 = quality.detect_outliers(df2)
        assert out2["A"]["count"] == 0

    def test_stale_edges(self):
        df = pd.DataFrame({"A": [np.nan, 1.0, 1.0, 1.0]})
        out = quality.detect_stale_data(df, threshold=3)
        # run after nan? when see diff becomes break
        assert isinstance(out["A"]["count"], int)

    def test_volume_anomalies_edges(self):
        df = pd.DataFrame({"volume": [0, 0, 0, 0]})
        out = quality.detect_volume_anomalies(df)
        assert out.get("volume", {}).get("count", 0) == 0
        df2 = pd.DataFrame({"vol": [1,2,3,4]})
        out2 = quality.detect_volume_anomalies(df2)
        assert isinstance(out2.get("vol", {}).get("count", 0), int)

    def test_check_quality_strict(self):
        df = pd.DataFrame({"A": [1.0, np.nan]})
        assert quality.check_data_quality(df, strict=False) is False
        with pytest.raises(ValueError):
            quality.check_data_quality(df, strict=True)
        df_bad = "x"
        with pytest.raises(ValueError):
            quality.check_data_quality(df_bad, strict=True)
        assert quality.check_data_quality(df_bad, strict=False) is False

    def test_report_with_non_numeric_column(self):
        df = pd.DataFrame({"A": ["a", "b", "c"]})
        rep = quality.data_quality_report(df)
        assert "columns" in rep
