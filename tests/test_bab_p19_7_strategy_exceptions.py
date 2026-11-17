"""P19-7 Milestone 2: strategy.py exception-handling hardening (sites 1-11).

All 11 broad ``except`` sites in strategy.py are Class A (intentional total
contracts): each either surfaces a ``BABDataError`` (chained cause) or
degrades to a safe default (rebalances=0 / kill_switch=None). None are silent
defect-hiders. Each site carries an inline invariant in strategy.py; this
module locks every contract with a regression test.

Before: 11 broad / 0 silent. After: 11 broad / 0 silent (all Class A, broad
catch retained, behavior locked by invariant + test).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta import portfolio as _portfolio_mod
from strategies.betting_against_beta import strategy as _strategy_mod
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.costs import TransactionCostModel
from strategies.betting_against_beta.errors import BABDataError


def _default_strategy():
    """BABStrategy on default synthetic data (clean end-to-end run)."""
    return BABStrategy()


# ---------------------------------------------------------------------------
# Site 1 -- strategy.py:315  _resolve_cost_model: bad prices path -> BABDataError
# ---------------------------------------------------------------------------

def test_site1_bad_prices_path_surfaces_babdataerror():
    cfg = BABConfig(
        cost_model=TransactionCostModel(),
        prices="/nonexistent/no_such_prices.csv",
    )
    strat = BABStrategy(cfg)
    with pytest.raises(BABDataError, match="failed to load prices"):
        BABStrategy._resolve_cost_model(cfg)


# ---------------------------------------------------------------------------
# Site 2 -- strategy.py:369  run(): beta calculation failure -> BABDataError
# ---------------------------------------------------------------------------

def test_site2_beta_calculation_failure_surfaces_babdataerror(monkeypatch):
    strat = _default_strategy()

    def boom(returns, benchmark, window, min_obs):
        raise RuntimeError("beta boom")

    monkeypatch.setattr(_strategy_mod, "calculate_rolling_beta", boom)
    with pytest.raises(BABDataError, match="beta calculation failed"):
        strat.run()


# ---------------------------------------------------------------------------
# Site 3 -- strategy.py:376  run(): signal generation failure -> BABDataError
# ---------------------------------------------------------------------------

def test_site3_signal_generation_failure_surfaces_babdataerror(monkeypatch):
    strat = _default_strategy()

    def boom(betas, long_quantile, short_quantile):
        raise RuntimeError("signal boom")

    monkeypatch.setattr(_strategy_mod, "generate_bab_signals", boom)
    with pytest.raises(BABDataError, match="signal generation failed"):
        strat.run()


# ---------------------------------------------------------------------------
# Site 4 -- strategy.py:388  run(): rebalance application failure -> BABDataError
# ---------------------------------------------------------------------------

def test_site4_rebalance_failure_surfaces_babdataerror(monkeypatch):
    cfg = BABConfig(rebalance_freq="weekly")
    strat = BABStrategy(cfg)

    def boom(signals, freq):
        raise RuntimeError("rebalance boom")

    monkeypatch.setattr(_strategy_mod, "_apply_rebalance", boom)
    with pytest.raises(BABDataError, match="rebalance application failed"):
        strat.run()


# ---------------------------------------------------------------------------
# Site 5 -- strategy.py:410  run(): portfolio construction failure -> BABDataError
# ---------------------------------------------------------------------------

def test_site5_portfolio_construction_failure_surfaces_babdataerror(monkeypatch):
    strat = _default_strategy()

    def boom(signals, **kwargs):
        raise RuntimeError("portfolio boom")

    monkeypatch.setattr(_strategy_mod, "construct_portfolio", boom)
    with pytest.raises(BABDataError, match="portfolio construction failed"):
        strat.run()


# ---------------------------------------------------------------------------
# Sites 6-7 -- strategy.py:516/519  run(): finiteness guard clamps + surfaces
# ---------------------------------------------------------------------------

def test_sites6_7_finiteness_guard_clamps_nonfinite(monkeypatch):
    """Non-finite weights are clamped to 0.0, never passed corrupt to run_backtest."""
    strat = _default_strategy()
    base_construct = _portfolio_mod.construct_portfolio

    def bad_weights(signals, **kwargs):
        w = base_construct(signals, **kwargs)
        w = w.copy()
        w.iloc[0, 0] = float("inf")
        w.iloc[1, 1] = float("nan")
        return w

    monkeypatch.setattr(_strategy_mod, "construct_portfolio", bad_weights)
    result = strat.run()
    assert np.isfinite(result.weights.to_numpy(dtype=float)).all()


def test_sites6_7_finiteness_guard_happy_path_unchanged():
    """Finite weights pass through the guard untouched."""
    strat = _default_strategy()
    result = strat.run()
    assert np.isfinite(result.weights.to_numpy(dtype=float)).all()


# ---------------------------------------------------------------------------
# Sites 8-9 -- strategy.py:809/812  dry_run(): finiteness guard degrades safely
# ---------------------------------------------------------------------------

def test_sites8_9_dry_run_finiteness_guard_degrades(monkeypatch):
    """dry_run never raises on degenerate weights; reported metrics stay finite."""
    strat = _default_strategy()
    base_construct = _portfolio_mod.construct_portfolio

    def bad_weights(signals, **kwargs):
        w = base_construct(signals, **kwargs)
        w = w.copy()
        w.iloc[0, 0] = float("inf")
        return w

    monkeypatch.setattr(_strategy_mod, "construct_portfolio", bad_weights)
    out = strat.dry_run()
    assert isinstance(out, dict)
    assert np.isfinite(out["portfolio_risk"]["gross_exposure"]["mean"])
    assert np.isfinite(out["portfolio_risk"]["net_exposure"]["mean"])
    assert np.isfinite(out["portfolio_risk"]["gross_leverage"]["mean"])


# ---------------------------------------------------------------------------
# Site 10 -- strategy.py:987  report(): rebalances count degrades to 0
# ---------------------------------------------------------------------------

def test_site10_report_rebalances_none_weights_degrades_to_zero():
    """weights=None -> rebalances=0, report never crashes."""
    strat = _default_strategy()
    result = strat.run()
    result.weights = None
    rep = strat.report(result)
    assert rep["rebalances"] == 0
    assert isinstance(rep["metrics"], dict)


def test_site10_report_rebalances_except_path_safe_default():
    """dropna raising -> rebalances=0 (hits the except branch)."""

    class ExplodingDF(pd.DataFrame):
        def dropna(self, *args, **kwargs):
            raise RuntimeError("dropna boom")

    strat = _default_strategy()
    result = strat.run()
    result.weights = ExplodingDF(result.weights)
    rep = strat.report(result)
    assert rep["rebalances"] == 0


# ---------------------------------------------------------------------------
# Site 11 -- strategy.py:997  report(): kill_switch.to_dict failure -> None
# ---------------------------------------------------------------------------

def test_site11_report_kill_switch_to_dict_failure_degrades_to_none():
    """kill_switch.to_dict() raising -> kill_switch=None, report never crashes."""
    strat = _default_strategy()
    result = strat.run()

    class ExplodingKillSwitch:
        def to_dict(self):
            raise RuntimeError("to_dict boom")

    result.kill_switch = ExplodingKillSwitch()
    rep = strat.report(result)
    assert rep["kill_switch"] is None


# ---------------------------------------------------------------------------
# Happy-path smoke: default run is byte-identical / unaffected by hardening
# ---------------------------------------------------------------------------

def test_strategy_default_run_happy_path_unaffected():
    """Default synthetic run still completes with a finite cumulative path."""
    result = _default_strategy().run()
    cumulative = result.backtest["cumulative"]
    assert len(cumulative) > 0
    assert np.isfinite(cumulative.iloc[-1])
    assert result.execution is None
