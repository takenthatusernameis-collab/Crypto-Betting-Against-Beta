import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import config, regime


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


def test_regime_scale_factors_empty_returns():
    cfg = config.BABConfig()
    out = regime.regime_scale_factors(pd.DataFrame(), cfg)
    assert isinstance(out, pd.DataFrame)
    assert out.empty


def test_regime_scale_factors_non_dataframe():
    cfg = config.BABConfig()
    out = regime.regime_scale_factors([], cfg)
    assert isinstance(out, pd.DataFrame)
    assert out.empty


def test_regime_scale_factors_trend_method():
    idx = pd.date_range("2023-01-01", periods=100)
    np.random.seed(42)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.01, len(idx)),
            "B": np.random.normal(0, 0.01, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="trend")
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)
    assert out.shape == returns[["A", "B"]].shape


def test_regime_scale_factors_combined_method():
    idx = pd.date_range("2023-01-01", periods=100)
    np.random.seed(123)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.01, len(idx)),
            "B": np.random.normal(0, 0.01, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="combined")
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)
    assert out.shape == returns[["A", "B"]].shape


def test_regime_scale_factors_vol_thresholds():
    idx = pd.date_range("2023-01-01", periods=100)
    np.random.seed(5)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.01, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="vol", vol_thresholds=[0.005, 0.015])
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)


def test_regime_scale_factors_vol_thresholds_single():
    idx = pd.date_range("2023-01-01", periods=100)
    np.random.seed(7)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.01, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="vol", vol_thresholds=[0.01])
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)


def test_regime_scale_factors_with_hysteresis():
    idx = pd.date_range("2023-01-01", periods=150)
    np.random.seed(9)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.02, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="vol", vol_hysteresis=0.5)
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)


def test_regime_scale_factors_ewma():
    idx = pd.date_range("2023-01-01", periods=100)
    np.random.seed(11)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.01, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="vol", vol_use_ewma=True)
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)


def test_regime_scale_factors_trend_zwindow():
    idx = pd.date_range("2023-01-01", periods=100)
    np.random.seed(13)
    returns = pd.DataFrame(
        {
            "A": np.random.normal(0, 0.01, len(idx)),
        },
        index=idx,
    )
    cfg = config.BABConfig(regime_method="trend", trend_z_window=10)
    out = regime.regime_scale_factors(returns, cfg)
    assert isinstance(out, pd.DataFrame)


def test_regime_scale_factors_invalid_method():
    idx = pd.date_range("2023-01-01", periods=50)
    returns = pd.DataFrame({"A": np.random.normal(0, 0.01, len(idx))}, index=idx)

    class DummyCfg:
        regime_method = "invalid"
        benchmark = None
        vol_window = 20
        vol_use_ewma = False
        vol_hysteresis = 0.0
        vol_thresholds = None
        vol_percentiles = (0.33, 0.66)
        trend_ma_window = 50
        trend_z_window = None
        regime_scale_high = 0.5
        regime_scale_low = 1.0

    out = regime.regime_scale_factors(returns, DummyCfg())
    assert isinstance(out, pd.DataFrame)


def test_apply_regime_scaling_exception_in_classification():
    sig = pd.DataFrame({"A": [1.0, -1.0, 0.5]}, index=pd.date_range("2023-01-01", periods=3))

    # Force exception by passing returns that cause issues in classification
    class BadDF(pd.DataFrame):
        @property
        def columns(self):
            raise RuntimeError("boom")

    try:
        bad = BadDF({"A": [0.01, 0.02, 0.03]}, index=sig.index)
    except Exception:
        bad = pd.DataFrame({"A": [0.01, 0.02, 0.03]}, index=sig.index)
        # monkey patch
        bad.__class__ = type(
            "BadDF2",
            (pd.DataFrame,),
            {"columns": property(lambda self: (_ for _ in ()).throw(RuntimeError("boom")))},
        )
    from strategies.betting_against_beta.errors import BABDataError

    with pytest.raises(BABDataError, match="regime scaling failed"):
        regime.apply_regime_scaling(sig, returns=bad)


def test_apply_regime_scaling_returns_causes_exception():
    sig = pd.DataFrame({"A": [1.0, -1.0]}, index=pd.date_range("2023-01-01", periods=2))
    # returns with incompatible shape
    returns = pd.DataFrame({"B": [0.01, 0.02]}, index=sig.index)  # different column
    out = regime.apply_regime_scaling(sig, returns=returns)
    assert isinstance(out, pd.DataFrame)
    # Should not crash


def test__apply_vol_hysteresis_thresholds_nonfinite_after_init():
    vol = pd.DataFrame({"A": [0.01, 0.015, 0.02]}, index=range(3))
    reg = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=range(3))
    # First pass sets prev, second has non-finite threshold
    low_thr = pd.Series([0.01, np.nan, 0.01], index=range(3))
    high_thr = pd.Series([0.02, 0.02, 0.02], index=range(3))
    out = regime._apply_vol_hysteresis(vol, reg, low_thr, high_thr, 0.5)
    assert isinstance(out, pd.DataFrame)
    assert out.iloc[1, 0] == out.iloc[0, 0]  # should carry over prev
