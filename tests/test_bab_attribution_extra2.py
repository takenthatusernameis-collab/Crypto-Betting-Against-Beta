"""More attribution edge cases."""
from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import attribution


def test_trade_attribution_returns_from_series():
    idx = pd.date_range("2023-01-01", periods=4)
    backtest = pd.DataFrame({
        "returns": pd.Series([0.01, 0.02, np.nan, 0.04], index=idx)
    }, index=idx)
    out = attribution.trade_attribution(backtest)
    assert len(out) == 4
    assert np.isfinite(out["net_return"]).all()


def test_trade_attribution_with_list_like_columns():
    idx = pd.date_range("2023-01-01", periods=3)
    backtest = pd.DataFrame(index=idx)
    backtest["gross_return"] = [0.1, 0.2, 0.3]
    backtest["cost_drag"] = [0.01, 0.02, np.inf]
    backtest["slippage_drag"] = [-0.001, 0.001, 0.001]  # negative slips? fillna handles
    out = attribution.trade_attribution(backtest)
    assert np.isfinite(out).all().all()


def test_attribution_totals_series_input():
    res = attribution.attribution_totals(pd.Series([1,2,3]))
    assert res["gross_return"] == 0.0


def test_attribution_totals_dict_input():
    res = attribution.attribution_totals({"a": 1})
    assert res["net_return"] == 0.0
