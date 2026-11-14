"""P8: signal quality / regime observability diagnostics tests (schema + invariants)."""

import json

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data import generate_synthetic_returns
from strategies.betting_against_beta.execution import PaperExecutionEngine, StrategyDiagnostics


def test_diagnostics_schema_and_invariants(tmp_path):
    returns = generate_synthetic_returns(
        n_days=120, n_assets=6, benchmark_name="BTC", seed=11
    )
    strategy = BABStrategy(
        BABConfig(benchmark="BTC", beta_window=20, min_observations=5)
    )
    result = strategy.run(returns_df=returns)
    assert isinstance(result.betas, pd.DataFrame) and not result.betas.empty

    out = tmp_path / "paper_fills.jsonl"
    diag = tmp_path / "diagnostics.jsonl"
    engine = PaperExecutionEngine(log_path=out, diagnostics_path=diag)
    report = engine.execute(
        result.weights, betas_df=result.betas, signals_df=result.signals,
        returns_df=result.returns,
    )
    assert len(report.diagnostics) > 0
    n_assets = len(result.weights.columns)

    for d in report.diagnostics:
        assert isinstance(d, StrategyDiagnostics)
        dd = d.to_dict()
        for key in (
            "date",
            "beta_mean",
            "beta_median",
            "beta_std",
            "beta_min",
            "beta_max",
            "long_beta_boundary",
            "short_beta_boundary",
            "long_assets",
            "short_assets",
            "n_long",
            "n_short",
            "turnover",
            "hhi",
            "beta_neutrality_error",
        ):
            assert key in dd, f"missing diagnostic key: {key}"

        # Invariants.
        assert 0.0 <= d.hhi <= 1.0, f"HHI out of bounds: {d.hhi}"
        assert d.beta_neutrality_error is not None and d.beta_neutrality_error >= 0.0
        assert d.n_long >= 0 and d.n_short >= 0
        assert d.n_long + d.n_short <= n_assets
        assert set(d.long_assets).isdisjoint(d.short_assets)
        assert d.turnover is not None and d.turnover >= 0.0

        # Beta stats, when present, are finite and ordered.
        if d.beta_mean is not None:
            assert np.isfinite(d.beta_mean)
            assert np.isfinite(d.beta_median)
            assert d.beta_min <= d.beta_max
            assert d.long_beta_boundary <= d.short_beta_boundary

    # JSONL sidecar is strict JSON, one diagnostic per line.
    dlines = diag.read_text(encoding="utf-8").splitlines()
    assert len(dlines) == len(report.diagnostics)
    for line, d in zip(dlines, report.diagnostics):
        obj = json.loads(line)
        assert obj["date"] == d.date
        assert abs(obj["hhi"] - d.hhi) < 1e-12


def test_diagnostics_beta_neutrality_near_zero_for_dollar_neutral(tmp_path):
    returns = generate_synthetic_returns(
        n_days=100, n_assets=8, benchmark_name="BTC", seed=5
    )
    strategy = BABStrategy(
        BABConfig(benchmark="BTC", beta_window=20, min_observations=5, dollar_neutral=True)
    )
    result = strategy.run(returns_df=returns)
    engine = PaperExecutionEngine()
    report = engine.execute(
        result.weights, betas_df=result.betas, returns_df=result.returns
    )
    # Dollar-neutral portfolio beta (weighted by long/short) should be small.
    errors = [
        d.beta_neutrality_error
        for d in report.diagnostics
        if d.beta_neutrality_error is not None
    ]
    assert len(errors) > 0
    assert np.median(errors) < 0.5, f"portfolio beta not neutral enough: median={np.median(errors)}"
