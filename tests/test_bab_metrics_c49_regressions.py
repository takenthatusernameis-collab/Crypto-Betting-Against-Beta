"""C49 regression tests: sharpe_ratio non-finite risk_free and
turnover_series non-numeric weight frames must be defensive, not crash."""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.metrics import sharpe_ratio, turnover_series


@pytest.mark.parametrize("rf", [float("nan"), float("inf"), float("-inf"), None])
def test_sharpe_ratio_non_finite_risk_free_returns_nan(rf):
    r = pd.Series([0.01, -0.02, 0.03, 0.0])
    result = sharpe_ratio(r, risk_free=rf)
    assert isinstance(result, float)
    assert np.isnan(result)


def test_sharpe_ratio_finite_risk_free_unchanged():
    r = pd.Series([0.01, -0.02, 0.03, 0.0])
    assert np.isfinite(sharpe_ratio(r, risk_free=0.02))


def test_turnover_series_non_numeric_frame_does_not_raise():
    w = pd.DataFrame({"a": ["x", "y"], "b": ["z", "w"]})
    result = turnover_series(w)
    assert isinstance(result, pd.Series)
    assert len(result) == len(w)
    assert np.isfinite(result.to_numpy(dtype=float)).all()


def test_turnover_series_numeric_frame_unchanged():
    w = pd.DataFrame({"a": [0.5, 0.2], "b": [-0.5, -0.2]})
    result = turnover_series(w)
    assert isinstance(result, pd.Series)
    # first period 0.0 (no prior weights), second period |Δa|+|Δb| = 0.6
    assert result.iloc[0] == 0.0
    assert abs(float(result.iloc[1]) - 0.6) < 1e-12
