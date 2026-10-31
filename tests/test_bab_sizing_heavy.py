"""Heavy coverage tests for sizing."""
import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import sizing, signals
from strategies.betting_against_beta.sizing import (
    BABSizingError,
    KellySizer,
    VolatilityTargetSizer,
    RiskParitySizer,
)


class TestSizerValidationFull:
    def test_kelly_validation(self):
        with pytest.raises(BABSizingError):
            KellySizer(lookback=0)
        with pytest.raises(BABSizingError):
            KellySizer(max_leverage=0)
        with pytest.raises(BABSizingError):
            KellySizer(fraction=-0.1)
        # valid
        k = KellySizer()
        assert k.fraction == 1.0

    def test_vol_target_validation(self):
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(target_vol=0)
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(target_vol=-1)
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(lookback=0)
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(annualize=0)
        with pytest.raises(BABSizingError):
            VolatilityTargetSizer(max_leverage=0)
        v = VolatilityTargetSizer()
        assert v.max_leverage == 2.0

    def test_risk_parity_validation(self):
        with pytest.raises(BABSizingError):
            RiskParitySizer(lookback=0)
        with pytest.raises(BABSizingError):
            RiskParitySizer(max_leverage=0)
        with pytest.raises(BABSizingError):
            RiskParitySizer(target_vol=0)
        with pytest.raises(BABSizingError):
            RiskParitySizer(target_vol=-1)
        with pytest.raises(BABSizingError):
            RiskParitySizer(annualize=0)
        r = RiskParitySizer(target_vol=0.1)
        assert r.target_vol == 0.1

    def test_base_sizer_frozen(self):
        k = KellySizer()
        with pytest.raises(AttributeError):
            k.lookback = 10
        # internal ok
        object.__setattr__(k, "_x", 1)
        k._x = 2  # starts with _ so allowed
        assert k._x == 2


class TestApplySizingBranches:
    def test_string_shorthands(self):
        idx = pd.date_range("2020-01-01", periods=80)
        sig = signals.generate_bab_signals(pd.DataFrame({"BTC": np.ones(80), "ETH": np.arange(80)}, index=idx))
        rets = pd.DataFrame(np.random.RandomState(123).normal(0, 0.01, (80, sig.shape[1])), index=idx, columns=sig.columns)
        for s in ["kelly", "KELLY_FRACTION", "vol_target", "volatility_target", "voltarget", "risk_parity", "riskparity", "rp"]:
            out = sizing.apply_position_sizing(sig, returns=rets, sizer=s)
            assert isinstance(out, pd.DataFrame)
            assert out.shape == sig.shape
        with pytest.raises(BABSizingError):
            sizing.apply_position_sizing(sig, returns=rets, sizer="bad")

    def test_no_returns_returns_base_finite(self):
        idx = pd.date_range("2020-01-01", periods=10)
        sig = pd.DataFrame({"A": [1, -1, 0, 1, -1, 0, 1, -1, 0, 0]}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=None, sizer=KellySizer())
        assert isinstance(out, pd.DataFrame)
        assert out.shape == sig.shape

    def test_common_idx_empty(self):
        idx = pd.date_range("2020-01-01", periods=10)
        idx2 = pd.date_range("2021-01-01", periods=10)
        sig = pd.DataFrame({"A": [1] * 10}, index=idx)
        rets = pd.DataFrame({"A": [0.01] * 10}, index=idx2)
        out = sizing.apply_position_sizing(sig, returns=rets)
        assert isinstance(out, pd.DataFrame)

    def test_missing_column_filled(self):
        idx = pd.date_range("2020-01-01", periods=80)
        sig = pd.DataFrame({"A": np.ones(80), "B": -np.ones(80)}, index=idx)
        rets = pd.DataFrame({"A": np.random.RandomState(1).normal(0, 0.01, 80)}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=VolatilityTargetSizer())
        assert isinstance(out, pd.DataFrame)
        assert "B" in out.columns

    def test_kelly_path(self):
        idx = pd.date_range("2020-01-01", periods=100)
        sig = pd.DataFrame({"A": np.ones(100), "B": -np.ones(100)}, index=idx)
        rng = np.random.RandomState(42)
        rets = pd.DataFrame({"A": rng.normal(0.001, 0.02, 100), "B": rng.normal(-0.0005, 0.015, 100)}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=KellySizer(lookback=30, fraction=0.5, max_leverage=1.0))
        assert isinstance(out, pd.DataFrame)
        assert (np.isfinite(out.values)).all()

    def test_kelly_zero_var(self):
        idx = pd.date_range("2020-01-01", periods=80)
        sig = pd.DataFrame({"A": np.ones(80), "B": -np.ones(80)}, index=idx)
        # constant returns
        rets = pd.DataFrame({"A": np.ones(80) * 0.01, "B": np.ones(80) * -0.01}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=KellySizer(lookback=60))
        assert isinstance(out, pd.DataFrame)

    def test_vol_target_path(self):
        idx = pd.date_range("2020-01-01", periods=90)
        sig = pd.DataFrame({"A": np.ones(90)}, index=idx)
        rng = np.random.RandomState(7)
        rets = pd.DataFrame({"A": rng.normal(0, 0.02, 90)}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=VolatilityTargetSizer(target_vol=0.1, lookback=30, annualize=252))
        assert isinstance(out, pd.DataFrame)

    def test_vol_target_zero_var(self):
        idx = pd.date_range("2020-01-01", periods=80)
        sig = pd.DataFrame({"A": np.ones(80), "B": -np.ones(80)}, index=idx)
        rets = pd.DataFrame({"A": np.zeros(80), "B": np.zeros(80)}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=VolatilityTargetSizer(lookback=60))
        assert isinstance(out, pd.DataFrame)

    def test_risk_parity_basic(self):
        idx = pd.date_range("2020-01-01", periods=90)
        sig = pd.DataFrame({"A": np.ones(90), "B": -np.ones(90)}, index=idx)
        rng = np.random.RandomState(9)
        rets = pd.DataFrame({"A": rng.normal(0, 0.01, 90), "B": rng.normal(0, 0.02, 90)}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=RiskParitySizer(lookback=30))
        assert isinstance(out, pd.DataFrame)

    def test_risk_parity_with_target_vol(self):
        idx = pd.date_range("2020-01-01", periods=90)
        sig = pd.DataFrame({"A": np.ones(90), "B": -np.ones(90)}, index=idx)
        rng = np.random.RandomState(11)
        rets = pd.DataFrame({"A": rng.normal(0, 0.01, 90), "B": rng.normal(0, 0.015, 90)}, index=idx)
        out = sizing.apply_position_sizing(sig, returns=rets, sizer=RiskParitySizer(lookback=30, target_vol=0.1, annualize=252))
        assert isinstance(out, pd.DataFrame)
        out2 = sizing.apply_position_sizing(sig, returns=rets, sizer=RiskParitySizer(lookback=30, target_vol=0.1))
        assert isinstance(out2, pd.DataFrame)
