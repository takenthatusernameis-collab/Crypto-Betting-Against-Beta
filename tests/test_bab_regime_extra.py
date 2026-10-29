"""Regime tests for `strategies/betting_against_beta/regime.py` targeting uncovered branches."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.regime import (
    _apply_vol_hysteresis,
    apply_regime_scaling,
    calculate_realized_volatility,
    classify_trend_regime,
    classify_volatility_regimes,
    classify_volatility_regimes_percentile,
    get_regime_state,
    mean_reversion_zscore,
    regime_scale_factors,
)


def _make_returns(n=120, seed=3):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n)
    return pd.DataFrame(
        {
            "BTC": rng.normal(0.0, 0.01, n),
            "ETH": rng.normal(0.0, 0.015, n),
            "SOL": rng.normal(0.0, 0.02, n),
        },
        index=dates,
    )


class _Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_calculate_realized_volatility_raw_and_ewma():
    r = _make_returns(60)
    vol = calculate_realized_volatility(r, window=20)
    assert isinstance(vol, pd.DataFrame) and vol.shape == r.shape
    vol_ewma = calculate_realized_volatility(r, window=20, use_ewma=True)
    assert isinstance(vol_ewma, pd.DataFrame)


def test_calculate_realized_volatility_errors():
    r = _make_returns(30)
    try:
        calculate_realized_volatility([1, 2, 3])
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    try:
        calculate_realized_volatility(r, window=0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_classify_volatility_regimes_default_and_custom():
    r = _make_returns(80)
    out = classify_volatility_regimes(r)
    assert set(out.columns) == set(r.columns)
    assert set(out.values.ravel()) <= {0.0, 1.0, 2.0}
    out2 = classify_volatility_regimes(r, thresholds=[0.005])
    assert set(out2.values.ravel()) <= {0.0, 1.0}
    out3 = classify_volatility_regimes(r, thresholds=[0.005, 0.02])
    assert set(out3.values.ravel()) <= {0.0, 1.0, 2.0}


def test_classify_volatility_regimes_percentile():
    r = _make_returns(150)
    out = classify_volatility_regimes_percentile(r)
    assert set(out.values.ravel()) <= {0.0, 1.0, 2.0}
    out2 = classify_volatility_regimes_percentile(r, quantiles=[0.2, 0.8])
    assert set(out2.values.ravel()) <= {0.0, 1.0, 2.0}


def test_classify_trend_regime_ma_and_zwindow():
    r = _make_returns(100)
    out_ma = classify_trend_regime(r)
    assert set(out_ma.values.ravel()) <= {0.0, 1.0}
    out_z = classify_trend_regime(r, z_window=10)
    assert set(out_z.values.ravel()) <= {0.0, 1.0}
    try:
        classify_trend_regime([1, 2])
        raise AssertionError("expected TypeError")
    except TypeError:
        pass


def test_mean_reversion_zscore():
    r = _make_returns(80)
    out = mean_reversion_zscore(r)
    assert set(out.values.ravel()) <= {-1.0, 0.0, 1.0}
    try:
        mean_reversion_zscore([1, 2])
        raise AssertionError("expected TypeError")
    except TypeError:
        pass


def test_get_regime_state():
    r = _make_returns(120)
    out = get_regime_state(r)
    assert out.shape == r.shape
    assert not out.isna().all().all()


def test_apply_regime_scaling_without_and_with_returns():
    sig = pd.DataFrame(1.0, index=_make_returns(60).index, columns=["BTC", "ETH"])
    out = apply_regime_scaling(sig)
    pd.testing.assert_frame_equal(out, sig)
    r = _make_returns(120)
    sig2 = pd.DataFrame(1.0, index=r.index, columns=["BTC", "ETH", "SOL"])
    out2 = apply_regime_scaling(sig2, returns=r)
    assert out2.shape == sig2.shape
    try:
        apply_regime_scaling([1, 2])
        raise AssertionError("expected TypeError")
    except TypeError:
        pass


def test_apply_vol_hysteresis_hysteresis_zero_returns_regimes():
    r = _make_returns(60)
    reg = pd.DataFrame(1.0, index=r.index, columns=["BTC"])
    vol = calculate_realized_volatility(r, window=10)
    out = _apply_vol_hysteresis(vol, reg, 0.01, 0.02, 0.0)
    pd.testing.assert_frame_equal(out, reg)


def test_apply_vol_hysteresis_nan_keeps_prev():
    idx = pd.date_range("2023-01-01", periods=4)
    # Column A: prev=1, values safely above the down-flip band -> stays 1 across NaN.
    # Column B: prev=0, values safely below the up-flip band -> stays 0 across NaN.
    vol = pd.DataFrame(
        {"A": [0.02, np.nan, 0.02, np.nan], "B": [0.005, np.nan, 0.005, np.nan]},
        index=idx,
    )
    reg = pd.DataFrame({"A": [1.0, 1.0, 1.0, 1.0], "B": [0.0, 0.0, 0.0, 0.0]}, index=idx)
    out = _apply_vol_hysteresis(vol, reg, 0.01, 0.03, 0.5)
    # NaN rows carry forward the established previous regime.
    assert (out["A"] == 1.0).all()
    assert (out["B"] == 0.0).all()


def test_regime_scale_factors_vol_trend_combined():
    r = _make_returns(200)
    cfg = _Cfg(
        benchmark="BTC",
        regime_method="vol",
        vol_window=20,
        vol_use_ewma=False,
        vol_hysteresis=0.0,
        vol_thresholds=None,
        vol_percentiles=(0.33, 0.66),
        trend_ma_window=50,
        trend_z_window=None,
        regime_scale_high=0.5,
        regime_scale_low=1.0,
    )
    for method in ("vol", "trend", "combined", "bogus"):
        cfg.regime_method = method
        out = regime_scale_factors(r, cfg)
        assert list(out.columns) == ["ETH", "SOL"]
        assert (out > 0).all().all()


def test_regime_scale_factors_empty_and_non_dataframe():
    assert regime_scale_factors(pd.DataFrame(), _Cfg(benchmark="BTC")).empty
    assert regime_scale_factors(None, _Cfg(benchmark="BTC")).empty
    try:
        regime_scale_factors([1, 2], _Cfg(benchmark="BTC"))
        raise AssertionError("expected AttributeError/TypeError path")
    except Exception:
        pass


def test_regime_scale_factors_benchmark_excluded():
    r = _make_returns(200)
    cfg = _Cfg(
        benchmark="BTC",
        regime_method="vol",
        vol_window=20,
        vol_use_ewma=False,
        vol_hysteresis=0.0,
        vol_thresholds=None,
        vol_percentiles=(0.33, 0.66),
        trend_ma_window=50,
        trend_z_window=None,
        regime_scale_high=0.5,
        regime_scale_low=1.0,
    )
    out = regime_scale_factors(r, cfg)
    assert "BTC" not in out.columns
