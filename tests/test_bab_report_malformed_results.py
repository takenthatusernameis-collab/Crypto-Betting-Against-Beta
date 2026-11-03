"""Campaign C hardening: report/tear_sheet must never crash on malformed results.

Exercises ``BABStrategy.report()`` and ``tear_sheet()`` against adversarial
BABResult-like objects: None backtest, empty frames, missing benchmark column,
weights=None, and results whose metrics are NaN/inf. Every path must return a
finite, JSON-safe structure or raise only the documented RuntimeError.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.strategy import BABResult, BABConfig


def _make_result(**overrides):
    """Build a minimal BABResult with sensible defaults; override fields."""
    cfg = BABConfig(benchmark="BTC", universe=["BTC", "ETH"])
    returns = pd.DataFrame(
        {"BTC": [0.01, -0.02, 0.03], "ETH": [0.02, 0.01, -0.04]},
        index=pd.date_range("2023-01-01", periods=3),
    )
    weights = pd.DataFrame(
        {"BTC": [0.5, -0.5, 0.5], "ETH": [-0.5, 0.5, -0.5]},
        index=returns.index,
    )
    backtest = pd.DataFrame(
        {
            "returns": [0.01, -0.02, 0.03],
            "gross_return": [0.01, -0.02, 0.03],
            "cost_drag": [0.0, 0.0, 0.0],
            "slippage_drag": [0.0, 0.0, 0.0],
            "cumulative": [1.01, 0.99, 1.02],
        },
        index=returns.index,
    )
    defaults = dict(
        config=cfg,
        returns=returns,
        betas=pd.DataFrame(index=returns.index, columns=returns.columns, data=1.0),
        signals=pd.DataFrame(index=returns.index, columns=returns.columns, data=0.0),
        weights=weights,
        backtest=backtest,
    )
    defaults.update(overrides)
    return BABResult(**defaults)


class TestReportMalformedResults:
    def test_report_none_backtest(self):
        res = _make_result(backtest=None)
        rep = BABStrategy().report(res)
        assert isinstance(rep, dict)
        assert "metrics" in rep and "attribution" in rep
        assert all(math.isfinite(v) for v in rep["metrics"].values())
        assert all(math.isfinite(v) for v in rep["attribution_totals"].values())

    def test_report_empty_backtest(self):
        res = _make_result(backtest=pd.DataFrame(), weights=pd.DataFrame())
        rep = BABStrategy().report(res)
        assert isinstance(rep, dict)
        assert rep["rebalances"] == 0
        assert all(math.isfinite(v) for v in rep["metrics"].values())

    def test_report_missing_benchmark_column(self):
        # Benchmark absent from returns frame -> beta falls back to nan -> 0.0
        res = _make_result(returns=pd.DataFrame({"ETH": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2)))
        rep = BABStrategy().report(res)
        assert math.isfinite(rep["metrics"]["strategy_beta"])

    def test_report_weights_none(self):
        res = _make_result(weights=None)
        rep = BABStrategy().report(res)
        assert rep["rebalances"] == 0
        assert math.isfinite(rep["metrics"]["turnover"])

    def test_report_nan_inf_metrics(self):
        res = _make_result(
            backtest=pd.DataFrame(
                {
                    "returns": [np.inf, np.nan, -np.inf],
                    "cumulative": [np.nan, np.inf, 1.0],
                },
                index=pd.date_range("2023-01-01", periods=3),
            )
        )
        rep = BABStrategy().report(res)
        assert all(math.isfinite(v) for v in rep["metrics"].values())
        assert all(math.isfinite(v) for v in rep["attribution_totals"].values())

    def test_report_json_safe(self):
        res = _make_result()
        rep = BABStrategy().report(res)
        payload = BABStrategy.report_to_json(rep)
        # Must parse strictly (no NaN/Infinity tokens).
        data = json.loads(payload, parse_constant=lambda t: pytest.fail(f"non-finite token: {t!r}"))
        assert isinstance(data, dict)
        assert "metrics" in data

    def test_tear_sheet_no_crash_on_nan(self):
        res = _make_result(
            backtest=pd.DataFrame(
                {"returns": [np.nan, np.nan, np.nan], "cumulative": [np.nan, np.nan, np.nan]},
                index=pd.date_range("2023-01-01", periods=3),
            )
        )
        text = BABStrategy().tear_sheet(res)
        assert isinstance(text, str)
        assert "BAB STRATEGY TEAR SHEET" in text

    def test_tear_sheet_no_crash_on_empty(self):
        res = _make_result(backtest=pd.DataFrame(), weights=pd.DataFrame())
        text = BABStrategy().tear_sheet(res)
        assert "BAB STRATEGY TEAR SHEET" in text

    def test_report_before_run_raises(self):
        with pytest.raises(RuntimeError):
            BABStrategy().report()