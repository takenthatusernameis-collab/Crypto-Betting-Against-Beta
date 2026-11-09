"""Coverage campaign 2 for regime.py residual branches.

Targets regime_scale_scalar() lines 301-315: causal per-date scalar scale
factor (import inside function, empty-factors early return, min-per-date
reduction, finiteness repair, [0,1] clamp, name).
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd

from strategies.betting_against_beta.regime import regime_scale_scalar


def _cfg(**overrides):
    base = dict(
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
    base.update(overrides)
    return SimpleNamespace(**base)


def _returns(periods: int = 120, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=periods, freq="D")
    return pd.DataFrame(
        {
            "BTC": rng.normal(0.0004, 0.02, periods),
            "ETH": rng.normal(0.0006, 0.03, periods),
            "SOL": rng.normal(0.0008, 0.05, periods),
        },
        index=idx,
    )


def test_regime_scale_scalar_normal_path_is_finite_and_bounded():
    cfg = _cfg()
    scalar = regime_scale_scalar(_returns(), cfg)
    assert isinstance(scalar, pd.Series)
    assert len(scalar) == 120
    arr = scalar.to_numpy(dtype=float)
    assert np.all(np.isfinite(arr))
    assert (arr >= 0.0).all() and (arr <= 1.0).all()
    assert scalar.name == "regime_scale"


def test_regime_scale_scalar_empty_factors_returns_empty_series():
    """Non-DataFrame input -> regime_scale_factors empty -> early return (lines 303-305)."""
    cfg = _cfg()
    scalar = regime_scale_scalar(None, cfg)
    assert isinstance(scalar, pd.Series)
    assert len(scalar) == 0
