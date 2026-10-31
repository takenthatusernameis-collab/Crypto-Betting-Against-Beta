import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import regime
from strategies.betting_against_beta import config


def test_get_regime_state_raises_type_error():
    with pytest.raises(TypeError):
        regime.get_regime_state([1, 2, 3])


def test_apply_regime_scaling_exception_path():
    sig = pd.DataFrame({"A": [1.0, -1.0]}, index=pd.date_range("2023-01-01", periods=2))
    bad_returns = pd.DataFrame({"A": [np.nan, np.nan]}, index=sig.index)
    out = regime.apply_regime_scaling(sig, returns=bad_returns)
    assert isinstance(out, pd.DataFrame)
    assert out.equals(sig)


def test__apply_vol_hysteresis_nan_vol_uses_prev():
    vol = pd.DataFrame({"A": [0.01, np.nan, 0.005]}, index=range(3))
    reg = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=range(3))
    out = regime._apply_vol_hysteresis(vol, reg, 0.01, 0.02, 0.5)
    assert out.iloc[1, 0] == 1.0


def test__apply_vol_hysteresis_nonfinite_thresholds_use_prev():
    vol = pd.DataFrame({"A": [0.01, 0.015]}, index=range(2))
    reg = pd.DataFrame({"A": [1.0, 1.0]}, index=range(2))
    out = regime._apply_vol_hysteresis(vol, reg, np.nan, 0.02, 0.5)
    assert out.iloc[1, 0] == 1.0


def test__apply_vol_hysteresis_prev_none_initialization():
    vol = pd.DataFrame({"A": [0.01, 0.015]}, index=range(2))
    reg = pd.DataFrame({"A": [np.nan, 1.0]}, index=range(2))
    out = regime._apply_vol_hysteresis(vol, reg, 0.01, 0.02, 0.5)
    assert isinstance(out, pd.DataFrame)


def test__apply_vol_hysteresis_transitions_high_to_low_and_medium():
    vol = pd.DataFrame({"A": [0.03, 0.005]}, index=range(2))
    reg = pd.DataFrame({"A": [2.0, 2.0]}, index=range(2))
    out = regime._apply_vol_hysteresis(vol, reg, 0.01, 0.02, 0.5)
    assert out.iloc[1, 0] in (0, 1)


def test__apply_vol_hysteresis_transition_low_to_medium_high():
    vol = pd.DataFrame({"A": [0.005, 0.025]}, index=range(2))
    reg = pd.DataFrame({"A": [0.0, 0.0]}, index=range(2))
    out = regime._apply_vol_hysteresis(vol, reg, 0.01, 0.02, 0.5)
    assert out.iloc[1, 0] in (1, 2)


def test__apply_vol_hysteresis_medium_transitions():
    vol = pd.DataFrame({"A": [0.015, 0.03, 0.004]}, index=range(3))
    reg = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=range(3))
    out = regime._apply_vol_hysteresis(vol, reg, 0.01, 0.02, 0.5)
    assert out.iloc[1, 0] == 2
    vol2 = pd.DataFrame({"A": [0.015, 0.004]}, index=range(2))
    reg2 = pd.DataFrame({"A": [1.0, 1.0]}, index=range(2))
    out2 = regime._apply_vol_hysteresis(vol2, reg2, 0.01, 0.02, 0.5)
    assert out2.iloc[1, 0] == 0


def test_regime_scale_factors_all_columns_benchmark():
    idx = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({"BTC": np.random.RandomState(123).normal(0, 0.01, len(idx))}, index=idx)
    cfg = config.BABConfig(benchmark="BTC")
    out = regime.regime_scale_factors(df, cfg)
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ["BTC"]
