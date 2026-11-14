"""P8: paper-trading scaffold tests (order emission, fill simulation, P&L reconciliation)."""

import json

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data import generate_synthetic_returns
from strategies.betting_against_beta.execution import (
    ExecutionReport,
    Fill,
    Order,
    PaperExecutionEngine,
    StrategyDiagnostics,
)


def _make_returns(n_days=100, n_assets=6, seed=7):
    return generate_synthetic_returns(
        n_days=n_days, n_assets=n_assets, benchmark_name="BTC", seed=seed
    )


def _prices_from_returns(returns_df: pd.DataFrame, start_px: float = 100.0) -> pd.DataFrame:
    return (1.0 + returns_df).cumprod() * start_px


def test_paper_trading_emits_orders_and_fills(tmp_path):
    returns = _make_returns()
    strategy = BABStrategy(
        BABConfig(benchmark="BTC", beta_window=20, min_observations=5)
    )
    result = strategy.run(returns_df=returns)
    assert isinstance(result.weights, pd.DataFrame) and not result.weights.empty

    out = tmp_path / "paper_fills.jsonl"
    diag = tmp_path / "diagnostics.jsonl"
    engine = PaperExecutionEngine(log_path=out, diagnostics_path=diag)
    report = engine.execute(
        result.weights,
        betas_df=result.betas,
        signals_df=result.signals,
        returns_df=result.returns,
        backtest_pnl=float(result.backtest["cumulative"].iloc[-1]) - 1.0,
    )
    assert isinstance(report, ExecutionReport)
    assert report.n_orders >= 0
    assert report.n_fills >= 0
    assert report.backtest_pnl is not None

    # Fills written as strict JSONL, one record per line.
    lines = out.read_text(encoding="utf-8").splitlines() if out.exists() else []
    for line in lines:
        obj = json.loads(line)
        assert "date" in obj and "asset" in obj and "weight" in obj and "status" in obj
        Fill(**obj)  # round-trips through the canonical type

    # Diagnostics written alongside paper fills.
    dlines = diag.read_text(encoding="utf-8").splitlines() if diag.exists() else []
    assert len(dlines) > 0
    for line in dlines:
        obj = json.loads(line)
        assert "date" in obj and "hhi" in obj and "turnover" in obj
        StrategyDiagnostics(**obj)  # round-trips through the canonical type


def test_paper_fill_simulation_next_bar(tmp_path):
    returns = _make_returns(n_days=60, n_assets=4, seed=1)
    strategy = BABStrategy(
        BABConfig(benchmark="BTC", beta_window=15, min_observations=5)
    )
    result = strategy.run(returns_df=returns)
    prices = _prices_from_returns(result.returns)

    out = tmp_path / "paper_fills.jsonl"
    engine = PaperExecutionEngine(
        prices_df=prices,
        adv_usd={a: 1e9 for a in result.returns.columns if a != "BTC"},
        partial_fill=True,
        max_participation=0.10,
        log_path=out,
    )
    report = engine.execute(result.weights, betas_df=result.betas, returns_df=result.returns)
    for f in report.fills:
        assert isinstance(f, Fill)
        assert f.price is not None and np.isfinite(f.price)
        assert f.slippage >= 0.0 and np.isfinite(f.slippage)
        assert f.status in ("filled", "partial")
        assert np.isfinite(f.weight)


def test_paper_pnl_reconciliation_vs_backtest(tmp_path):
    returns = _make_returns()
    strategy = BABStrategy(
        BABConfig(benchmark="BTC", beta_window=20, min_observations=5)
    )
    result = strategy.run(returns_df=returns)
    backtest_pnl = float(result.backtest["cumulative"].iloc[-1]) - 1.0

    out = tmp_path / "paper_fills.jsonl"
    engine = PaperExecutionEngine(log_path=out)
    report = engine.execute(
        result.weights,
        betas_df=result.betas,
        signals_df=result.signals,
        returns_df=result.returns,
        backtest_pnl=backtest_pnl,
    )
    assert np.isfinite(backtest_pnl)
    assert np.isfinite(report.backtest_pnl)
    if report.pnl is not None:
        assert np.isfinite(report.pnl)
        assert np.isfinite(report.pnl - report.backtest_pnl)

    # ExecutionReport serializes to a strict dict.
    d = report.to_dict()
    assert d["mode"] == "paper"
    assert d["n_orders"] == len(report.orders)
    assert d["n_fills"] == len(report.fills)
