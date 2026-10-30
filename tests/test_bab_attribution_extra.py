"""Additional attribution edge cases."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import attribution


def test_trade_attribution_with_series_inputs():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame(index=idx)
    df["gross_return"] = pd.Series([0.01, 0.02, 0.03], index=idx)
    df["cost_drag"] = pd.Series([0.001, np.nan, 0.002], index=idx)
    df["slippage_drag"] = pd.Series([0.0005, 0.0005, np.nan], index=idx)
    out = attribution.trade_attribution(df)
    assert out["net_return"].iloc[0] == pytest.approx(0.01 - 0.001 - 0.0005)
    assert np.isfinite(out["net_return"]).all()


def test_trade_attribution_mismatched_alignment():
    idx = pd.date_range("2023-01-01", periods=4)
    df = pd.DataFrame(
        {
            "gross_return": [0.01, 0.02, 0.03, 0.04],
            "cost_drag": pd.Series([0.001, 0.002], index=idx[:2]),  # short
            "slippage_drag": [0.0001] * 4,
        },
        index=idx,
    )
    out = attribution.trade_attribution(df)
    assert len(out) == 4
    assert np.isfinite(out).all().all()


def test_trade_attribution_all_nan():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame(
        {
            "gross_return": [np.nan, np.nan, np.nan],
            "cost_drag": [np.nan, np.nan, np.nan],
            "slippage_drag": [np.nan, np.nan, np.nan],
        },
        index=idx,
    )
    out = attribution.trade_attribution(df)
    assert (out == 0.0).all().all()


def test_trade_attribution_with_returns_series_misaligned():
    idx = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame(
        {
            "gross_return": [0.01, 0.02, 0.03],
        },
        index=idx,
    )
    df["returns"] = pd.Series([0.005], index=[idx[0]])  # misaligned
    out = attribution.trade_attribution(df)
    assert len(out) == 3
    assert np.isfinite(out).all().all()


def test_attribution_totals_with_inf():
    idx = pd.date_range("2023-01-01", periods=3)
    att = pd.DataFrame(
        {
            "gross_return": [0.1, np.inf, 0.2],
            "cost_drag": [0.01, 0.0, 0.02],
            "slippage_drag": [0.001, 0.0, 0.002],
            "net_return": [0.089, np.inf, 0.178],
        },
        index=idx,
    )
    totals = attribution.attribution_totals(att)
    assert isinstance(totals["gross_return"], float)
    assert isinstance(totals["cost_share"], float)
    assert isinstance(totals["slippage_share"], float)


def test_attribution_totals_negative_gross():
    idx = pd.date_range("2023-01-01", periods=2)
    att = pd.DataFrame(
        {
            "gross_return": [-0.1, -0.2],
            "cost_drag": [0.01, 0.02],
            "slippage_drag": [0.001, 0.002],
            "net_return": [-0.111, -0.222],
        },
        index=idx,
    )
    totals = attribution.attribution_totals(att)
    # denom is abs(gross), so shares should be computed
    assert totals["cost_share"] >= 0
    assert totals["slippage_share"] >= 0
