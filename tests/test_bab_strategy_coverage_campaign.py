"""Coverage campaign for strategy.py - production-realistic paths.

Targets uncovered defensive/validation/exception branches without semantic
production changes (one minimal bug fix: np->_np in defensive clamp).
"""

from __future__ import annotations

import math
from dataclasses import replace
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.strategy import BABResult, BABStrategy, _apply_rebalance


def _returns(n: int = 90, seed: int = 7) -> pd.DataFrame:
    idx = pd.date_range("2023-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    mkt = rng.normal(0, 0.01, n)
    return pd.DataFrame(
        {
            "BTC": mkt,
            "ETH": 0.7 * mkt + rng.normal(0, 0.005, n),
            "SOL": 1.3 * mkt + rng.normal(0, 0.008, n),
            "ADA": 0.4 * mkt + rng.normal(0, 0.004, n),
        },
        index=idx,
    )


def _strategy(**overrides) -> BABStrategy:
    cfg = BABConfig(beta_window=20, min_observations=10, **overrides)
    return BABStrategy(cfg)


def _make_config_unfrozen(**kwargs) -> BABConfig:
    """Create a config then temporarily bypass freeze for defensive-path tests."""
    cfg = BABConfig(beta_window=20, min_observations=10, **kwargs)
    object.__setattr__(cfg, "_frozen", False)
    return cfg


# --- _apply_rebalance defensive ---


def test_apply_rebalance_none_and_empty():
    assert _apply_rebalance(None, "weekly") is None
    empty = pd.DataFrame()
    out = _apply_rebalance(empty, "weekly")
    assert out is empty


# --- run() validation / error wrapping ---


def test_run_empty_universe_from_resolver_raises_value_error():
    """strategy.py guards empty effective_universe after resolved_universe()."""
    df = _returns()
    cfg = _make_config_unfrozen()
    strat = BABStrategy(cfg)
    with mock.patch.object(cfg, "resolved_universe", return_value=[]):
        with pytest.raises(ValueError, match="No tradable assets remain"):
            strat.run(returns_df=df)


def test_run_beta_calculation_failure_wrapped():
    strat = _strategy()
    with mock.patch(
        "strategies.betting_against_beta.strategy.calculate_rolling_beta",
        side_effect=RuntimeError("beta boom"),
    ):
        with pytest.raises(BABDataError, match="beta calculation failed"):
            strat.run(returns_df=_returns())


def test_run_signal_generation_failure_wrapped():
    strat = _strategy()
    with mock.patch(
        "strategies.betting_against_beta.strategy.generate_bab_signals",
        side_effect=RuntimeError("signal boom"),
    ):
        with pytest.raises(BABDataError, match="signal generation failed"):
            strat.run(returns_df=_returns())


def test_run_rebalance_babdataerror_passthrough():
    strat = _strategy(rebalance_freq="weekly")
    with mock.patch(
        "strategies.betting_against_beta.strategy._apply_rebalance",
        side_effect=BABDataError("rebalance bad"),
    ):
        with pytest.raises(BABDataError, match="rebalance bad"):
            strat.run(returns_df=_returns())


def test_run_rebalance_generic_failure_wrapped():
    strat = _strategy(rebalance_freq="weekly")
    with mock.patch(
        "strategies.betting_against_beta.strategy._apply_rebalance",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(BABDataError, match="rebalance application failed"):
            strat.run(returns_df=_returns())


def test_run_portfolio_babdataerror_passthrough():
    strat = _strategy()
    with mock.patch(
        "strategies.betting_against_beta.strategy.construct_portfolio",
        side_effect=BABDataError("portfolio bad"),
    ):
        with pytest.raises(BABDataError, match="portfolio bad"):
            strat.run(returns_df=_returns())


def test_run_portfolio_generic_failure_wrapped():
    strat = _strategy()
    with mock.patch(
        "strategies.betting_against_beta.strategy.construct_portfolio",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(BABDataError, match="portfolio construction failed"):
            strat.run(returns_df=_returns())


def test_run_shorting_constraints_invalid_type():
    cfg = _make_config_unfrozen()
    object.__setattr__(cfg, "shorting_constraints", 12345)
    strat = BABStrategy(cfg)
    with pytest.raises(BABDataError, match="shorting_constraints must be"):
        strat.run(returns_df=_returns())


def test_run_shorting_constraints_generic_failure_wrapped():
    strat = _strategy(shorting_constraints={"max_short_leverage": 1.0})
    with mock.patch(
        "strategies.betting_against_beta.strategy.shorting.apply_shorting_constraints",
        side_effect=TypeError("short boom"),
    ):
        with pytest.raises(BABDataError, match="shorting_constraints failed"):
            strat.run(returns_df=_returns())


def test_run_position_sizer_invalid_type():
    cfg = _make_config_unfrozen()
    object.__setattr__(cfg, "position_sizer", 12345)
    strat = BABStrategy(cfg)
    with pytest.raises(BABDataError, match="position_sizer must be"):
        strat.run(returns_df=_returns())


def test_run_position_sizer_generic_failure_wrapped():
    strat = _strategy(position_sizer={"type": "equal"})
    with mock.patch(
        "strategies.betting_against_beta.strategy.sizing.apply_position_sizing",
        side_effect=ValueError("sizer boom"),
    ):
        with pytest.raises(BABDataError, match="position_sizer failed"):
            strat.run(returns_df=_returns())


def test_run_regime_filter_invalid_type_defensive():
    cfg = _make_config_unfrozen()
    object.__setattr__(cfg, "regime_filter", "yes")
    strat = BABStrategy(cfg)
    with pytest.raises(BABDataError, match="regime_filter must be a bool"):
        strat.run(returns_df=_returns())


def test_run_regime_filter_babdataerror_passthrough():
    strat = _strategy(regime_filter=True)
    with mock.patch(
        "strategies.betting_against_beta.regime.regime_scale_scalar",
        side_effect=BABDataError("regime bad"),
    ):
        with pytest.raises(BABDataError, match="regime bad"):
            strat.run(returns_df=_returns())


# --- report() defensive paths ---


def test_report_before_run_raises():
    with pytest.raises(RuntimeError, match="called before run"):
        BABStrategy().report()


def test_report_with_explicit_result_and_missing_backtest_columns():
    strat = _strategy()
    res = strat.run(returns_df=_returns())
    bad_bt = pd.DataFrame({"strategy_return": [0.01, -0.02, 0.005]}, index=res.backtest.index[:3])
    res2 = BABResult(
        config=res.config,
        returns=res.returns,
        betas=res.betas,
        signals=res.signals,
        weights=res.weights,
        backtest=bad_bt,
    )
    rep = strat.report(res2)
    assert isinstance(rep["metrics"], dict)
    assert all(math.isfinite(v) for v in rep["metrics"].values())


def test_report_backtest_no_return_column_uses_none():
    strat = _strategy()
    res = strat.run(returns_df=_returns())
    bad_bt = pd.DataFrame({"value": [1.0, 1.1]}, index=res.backtest.index[:2])
    res2 = BABResult(res.config, res.returns, res.betas, res.signals, res.weights, bad_bt)
    rep = strat.report(res2)
    assert rep["rebalances"] >= 0


def test_report_malformed_types_do_not_crash():
    strat = _strategy()
    res = strat.run(returns_df=_returns())
    malformed = BABResult(
        config=None,  # type: ignore[arg-type]
        returns="not a df",  # type: ignore[arg-type]
        betas=res.betas,
        signals=res.signals,
        weights="not a df",  # type: ignore[arg-type]
        backtest=None,  # type: ignore[arg-type]
    )
    rep = strat.report(malformed)
    assert rep["rebalances"] == 0
    assert rep["config"]["universe"] == []
    assert all(math.isfinite(v) for v in rep["metrics"].values())
    assert all(math.isfinite(v) for v in rep["attribution_totals"].values())


def test_report_weights_dropna_exception_path():
    strat = _strategy()
    res = strat.run(returns_df=_returns())

    class BadWeights(pd.DataFrame):
        @property
        def _constructor(self):
            return BadWeights

        def dropna(self, *a, **k):
            raise RuntimeError("dropna boom")

    bad_w = BadWeights(res.weights)
    res2 = BABResult(res.config, res.returns, res.betas, res.signals, bad_w, res.backtest)
    rep = strat.report(res2)
    assert rep["rebalances"] == 0


# --- tear_sheet / report_to_json defensive ---


def test_tear_sheet_formats_nonfinite_defensively():
    strat = _strategy()
    res = strat.run(returns_df=_returns())
    rep = strat.report(res)
    bad = dict(rep)
    bad["metrics"] = {**rep["metrics"], "sharpe_ratio": float("nan"), "max_drawdown": None}
    bad["attribution_totals"] = {**rep["attribution_totals"], "gross_return": "oops"}
    with mock.patch.object(strat, "report", return_value=bad):
        text = strat.tear_sheet(res)
    assert "BAB STRATEGY TEAR SHEET" in text
    assert "nan" not in text.lower() or "NaN" not in text


def test_report_to_json_sanitizes_nonfinite():
    payload = {
        "a": float("nan"),
        "b": float("inf"),
        "c": [1.0, float("-inf"), {"x": float("nan")}],
        "ok": 3,
    }
    out = BABStrategy.report_to_json(payload)
    assert "NaN" not in out
    assert "Infinity" not in out
    assert '"ok": 3' in out


# --- real paths ---


def test_run_with_beta_neutral_real_path():
    strat = _strategy(beta_neutral=True, beta_neutral_enforcement=True)
    res = strat.run(returns_df=_returns())
    assert np.isfinite(res.weights.to_numpy(dtype=float)).all()
    rep = strat.report(res)
    assert rep["rebalances"] > 0


def test_report_safe_metric_edge_cases_via_malformed_summary():
    strat = _strategy()
    res = strat.run(returns_df=_returns())
    # force metrics.summary to include None/bad values via monkeypatch
    bad_summary = {"a": None, "b": "x", "c": float("inf"), "d": 1.5}
    with mock.patch("strategies.betting_against_beta.strategy.metrics.summary", return_value=bad_summary):
        rep = strat.report(res)
    assert rep["metrics"]["a"] == 0.0
    assert rep["metrics"]["b"] == 0.0
    assert rep["metrics"]["c"] == 0.0
    assert rep["metrics"]["d"] == 1.5
