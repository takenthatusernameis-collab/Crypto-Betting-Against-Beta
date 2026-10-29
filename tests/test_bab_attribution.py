"""Attribution tests for `strategies/betting_against_beta/attribution.py`."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.attribution import (
    ATTRIBUTION_COLUMNS,
    attribution_totals,
    trade_attribution,
)


def _frame(n=10):
    idx = pd.date_range("2023-01-01", periods=n)
    return pd.DataFrame(
        {
            "gross_return": [0.001 * i for i in range(n)],
            "cost_drag": [0.0001 * i for i in range(n)],
            "slippage_drag": [0.00005 * i for i in range(n)],
        },
        index=idx,
    )


def test_trade_attribution_basic():
    df = _frame()
    out = trade_attribution(df)
    assert list(out.columns) == ATTRIBUTION_COLUMNS
    assert len(out) == n if (n := len(df)) else True
    expected_net = (
        df["gross_return"] - df["cost_drag"] - df["slippage_drag"]
    )
    pd.testing.assert_series_equal(out["net_return"], expected_net, check_names=False)


def test_trade_attribution_uses_returns_column():
    df = _frame()
    df["returns"] = [0.005] * len(df)
    out = trade_attribution(df)
    assert (out["net_return"] == 0.005).all()


def test_trade_attribution_missing_cost_columns_treated_as_zero():
    idx = pd.date_range("2023-01-01", periods=5)
    df = pd.DataFrame({"gross_return": [0.01] * 5}, index=idx)
    out = trade_attribution(df)
    assert (out["cost_drag"] == 0.0).all()
    assert (out["slippage_drag"] == 0.0).all()
    assert (out["net_return"] == 0.01).all()


def test_trade_attribution_none_and_empty():
    assert trade_attribution(None).empty
    assert trade_attribution(pd.DataFrame()).empty
    out = trade_attribution(None)
    assert list(out.columns) == ATTRIBUTION_COLUMNS


def test_trade_attribution_non_dataframe():
    out = trade_attribution([1, 2, 3])
    assert out.empty


def test_trade_attribution_nan_filled():
    idx = pd.date_range("2023-01-01", periods=4)
    df = pd.DataFrame(
        {
            "gross_return": [0.01, np.nan, 0.03, 0.04],
            "cost_drag": [0.0, np.nan, 0.0, 0.0],
        },
        index=idx,
    )
    out = trade_attribution(df)
    assert out["net_return"].notna().all()
    assert (out.columns == ATTRIBUTION_COLUMNS).all()


def test_attribution_totals_basic():
    df = _frame()
    att = trade_attribution(df)
    totals = attribution_totals(att)
    assert set(totals) == {
        "gross_return",
        "cost_drag",
        "slippage_drag",
        "net_return",
        "cost_share",
        "slippage_share",
    }
    assert totals["gross_return"] == float(df["gross_return"].sum())
    assert totals["net_return"] == float(att["net_return"].sum())


def test_attribution_totals_zero_gross_guard():
    idx = pd.date_range("2023-01-01", periods=3)
    att = pd.DataFrame(
        {
            "gross_return": [0.0, 0.0, 0.0],
            "cost_drag": [0.1, 0.2, 0.3],
            "slippage_drag": [0.0, 0.0, 0.0],
            "net_return": [-0.1, -0.2, -0.3],
        },
        index=idx,
    )
    totals = attribution_totals(att)
    assert totals["cost_share"] == 0.0
    assert totals["slippage_share"] == 0.0


def test_attribution_totals_missing_columns():
    idx = pd.date_range("2023-01-01", periods=3)
    att = pd.DataFrame({"gross_return": [0.1, 0.2, 0.3]}, index=idx)
    totals = attribution_totals(att)
    assert totals["cost_drag"] == 0.0
    assert totals["slippage_drag"] == 0.0
    assert totals["net_return"] == pytest.approx(0.6)


def test_attribution_totals_none_and_empty():
    assert attribution_totals(None)["gross_return"] == 0.0
    assert attribution_totals(pd.DataFrame())["gross_return"] == 0.0
    assert attribution_totals(None)["net_return"] == 0.0
