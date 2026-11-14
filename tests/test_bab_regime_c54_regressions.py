"""C54 Step 2 regressions: surfacing silent ``except Exception: pass`` in regime.py.

Locks in the behavior that regime-scaling failures now raise ``BABDataError``
instead of silently returning unscaled signals, and that valid-path scaling is
unchanged.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.regime import apply_regime_scaling


class _BadColumnsDF(pd.DataFrame):
    """DataFrame whose ``columns`` access raises, mimicking a corrupt frame."""

    @property
    def columns(self):
        raise RuntimeError("columns access failed")


def test_apply_regime_scaling_raises_babdataerror_on_classification_failure():
    sig = pd.DataFrame({"A": [1.0, -1.0, 0.5]}, index=pd.date_range("2023-01-01", periods=3))
    bad = _BadColumnsDF({"A": [0.01, 0.02, 0.03]}, index=sig.index)
    with pytest.raises(BABDataError, match="regime scaling failed"):
        apply_regime_scaling(sig, returns=bad)


def test_apply_regime_scaling_valid_path_with_returns_unchanged():
    sig = pd.DataFrame(1.0, index=pd.date_range("2023-01-01", periods=120), columns=["BTC", "ETH"])
    rng = np.random.default_rng(7)
    r = pd.DataFrame(
        {
            "BTC": rng.normal(0.0, 0.02, 120),
            "ETH": rng.normal(0.0, 0.03, 120),
        },
        index=sig.index,
    )
    out = apply_regime_scaling(sig, returns=r)
    assert isinstance(out, pd.DataFrame)
    assert out.shape == sig.shape
    assert list(out.columns) == list(sig.columns)


def test_apply_regime_scaling_without_returns_returns_unscaled():
    sig = pd.DataFrame(1.0, index=pd.date_range("2023-01-01", periods=60), columns=["BTC", "ETH"])
    out = apply_regime_scaling(sig)
    pd.testing.assert_frame_equal(out, sig)


def test_apply_regime_scaling_non_dataframe_signals_raises_typeerror():
    with pytest.raises(TypeError, match="signals must be a DataFrame"):
        apply_regime_scaling([1, 2, 3])
