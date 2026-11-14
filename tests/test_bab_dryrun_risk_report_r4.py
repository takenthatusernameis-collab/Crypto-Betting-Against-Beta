"""Tests for R4-A: dry-run / portfolio-risk report."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.strategy import BABStrategy

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")


def test_dry_run_valid_fixture_returns_required_keys():
    """Valid fixture -> required keys present and finite."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.dry_run(returns_df=REAL_PRICES)

    # Top-level required keys
    required_keys = {
        "config",
        "tradable_universe",
        "beta_window",
        "long_quantile",
        "short_quantile",
        "portfolio_risk",
        "data_health",
    }
    assert set(result.keys()) == required_keys

    # Config subsection
    cfg = result["config"]
    assert cfg["benchmark"] == "BTC"
    assert isinstance(cfg["universe"], list) and len(cfg["universe"]) > 0
    assert isinstance(cfg["beta_window"], int) and cfg["beta_window"] > 0
    assert 0.0 < cfg["long_quantile"] < 1.0
    assert 0.0 < cfg["short_quantile"] < 1.0
    assert isinstance(cfg["dollar_neutral"], bool)
    assert isinstance(cfg["rebalance_freq"], str)
    assert math.isfinite(cfg["transaction_costs"])
    assert math.isfinite(cfg["slippage"])

    # Tradable universe
    assert isinstance(result["tradable_universe"], list) and len(result["tradable_universe"]) > 0
    assert all(isinstance(u, str) for u in result["tradable_universe"])

    # Beta window / quantiles (redundant but present)
    assert isinstance(result["beta_window"], int) and result["beta_window"] > 0
    assert math.isfinite(result["long_quantile"]) and 0.0 < result["long_quantile"] < 1.0
    assert math.isfinite(result["short_quantile"]) and 0.0 < result["short_quantile"] < 1.0

    # Portfolio-risk summary
    pr = result["portfolio_risk"]
    for metric in ("gross_exposure", "net_exposure", "gross_leverage", "max_single_weight"):
        assert metric in pr
        assert "mean" in pr[metric] and "max" in pr[metric] and "min" in pr[metric]
        for stat in ("mean", "max", "min"):
            assert math.isfinite(pr[metric][stat])
    assert "estimated_turnover" in pr
    assert "mean" in pr["estimated_turnover"] and "max" in pr["estimated_turnover"]
    assert math.isfinite(pr["estimated_turnover"]["mean"])
    assert math.isfinite(pr["estimated_turnover"]["max"])
    assert "estimated_cost_drag" in pr
    assert math.isfinite(pr["estimated_cost_drag"])

    # Data-health
    dh = result["data_health"]
    assert isinstance(dh["rows"], int) and dh["rows"] > 0
    assert isinstance(dh["columns"], int) and dh["columns"] > 0
    assert isinstance(dh["nan_counts"], dict)
    assert isinstance(dh["total_nans"], int)
    assert isinstance(dh["benchmark_present"], bool)
    assert dh["benchmark"] == "BTC"
    assert dh["benchmark_present"] is True


def test_dry_run_json_round_trip_strict():
    """Result is strict-JSON serializable via json.dumps(allow_nan=False)."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.dry_run(returns_df=REAL_PRICES)

    # This must not raise
    json_str = json.dumps(result, allow_nan=False)
    assert isinstance(json_str, str)
    assert len(json_str) > 0

    # Round-trip
    parsed = json.loads(json_str)
    assert set(parsed.keys()) == set(result.keys())


def test_dry_run_no_trade_execution():
    """dry_run does not execute backtest (weights/backtest untouched)."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))

    # Call dry_run first
    result = strat.dry_run(returns_df=REAL_PRICES)

    # No backtest should be run; _last_result should remain None
    assert strat._last_result is None

    # Result should not contain backtest-related keys
    assert "backtest" not in result
    assert "weights" not in result
    assert "signals" not in result
    assert "betas" not in result
    assert "returns" not in result


def test_dry_run_invalid_config_raises():
    """Invalid config raises BABConfigError loudly."""
    # Invalid beta_window
    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", beta_window=0))

    # Invalid quantiles
    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", long_quantile=1.5))

    # Invalid transaction_costs
    with pytest.raises(BABConfigError):
        BABStrategy(config=BABConfig(benchmark="BTC", transaction_costs=-0.1))


def test_dry_run_invalid_data_raises():
    """Invalid data raises BABDataError loudly (no silent fallback)."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))

    # Non-existent file
    with pytest.raises(BABDataError):
        strat.dry_run(returns_df="/nonexistent/path.csv")

    # Empty DataFrame
    with pytest.raises((BABDataError, ValueError)):
        strat.dry_run(returns_df=pd.DataFrame())

    # DataFrame without benchmark
    df = pd.DataFrame(
        {"ETH": [0.01, 0.02], "SOL": [0.02, 0.01]}, index=pd.date_range("2023-01-01", periods=2)
    )
    with pytest.raises((BABDataError, ValueError)):
        strat.dry_run(returns_df=df)


def test_cli_dry_run_returns_zero_on_valid():
    """CLI --dry-run returns 0 on valid input."""
    from strategies.betting_against_beta.cli import main

    rc = main(["--dry-run", "--data", REAL_PRICES, "--benchmark", "BTC"])
    assert rc == 0


def test_cli_dry_run_returns_nonzero_on_invalid():
    """CLI --dry-run returns non-zero on invalid input."""
    from strategies.betting_against_beta.cli import main

    # Non-existent file
    rc = main(["--dry-run", "--data", "/nonexistent/path.csv", "--benchmark", "BTC"])
    assert rc != 0

    # Invalid quantile
    rc = main(["--dry-run", "--data", REAL_PRICES, "--benchmark", "BTC", "--long-quantile", "1.5"])
    assert rc != 0


def test_cli_dry_run_output_not_created():
    """CLI --dry-run with --output does not create the output file."""
    import os
    import tempfile

    from strategies.betting_against_beta.cli import main

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "out.json")
        rc = main(["--dry-run", "--data", REAL_PRICES, "--benchmark", "BTC", "--output", out_path])
        assert rc == 0
        assert not os.path.exists(out_path), "--output file should not be created in dry-run mode"
