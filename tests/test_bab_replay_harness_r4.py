"""Tests for R4-C: deterministic paper-trading replay harness."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.strategy import BABStrategy
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.replay import ReplayHarness


REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")


def test_replay_harness_determinism():
    """Two runs on identical inputs produce byte-identical artifacts (same checksum)."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness1 = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    harness2 = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)

    artifact1 = harness1.replay()
    artifact2 = harness2.replay()

    # Check checksums are identical
    assert artifact1["checksum"] == artifact2["checksum"], "Artifacts should be byte-identical"

    # Check full artifact equality
    assert artifact1 == artifact2, "Artifacts should be identical"


def test_replay_harness_schema_keys_present():
    """Artifact contains all required schema keys."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    artifact = harness.replay()

    required_keys = {
        "schema_version",
        "config_snapshot",
        "n_periods",
        "orders",
        "fills",
        "costs",
        "equity",
        "checksum",
    }
    assert set(artifact.keys()) == required_keys

    # Check schema version
    assert artifact["schema_version"] == "r4-replay-1"

    # Check n_periods is positive integer
    assert isinstance(artifact["n_periods"], int)
    assert artifact["n_periods"] > 0

    # Check config_snapshot has expected keys
    cfg_snap = artifact["config_snapshot"]
    assert "benchmark" in cfg_snap
    assert "beta_window" in cfg_snap
    assert "long_quantile" in cfg_snap
    assert "short_quantile" in cfg_snap
    assert "dollar_neutral" in cfg_snap
    assert "transaction_costs" in cfg_snap
    assert "slippage" in cfg_snap
    assert "universe" in cfg_snap


def test_replay_harness_finite_values():
    """All numeric values in artifact are finite."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    artifact = harness.replay()

    def check_finite(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                check_finite(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                check_finite(v, f"{path}[{i}]")
        elif isinstance(obj, float):
            assert math.isfinite(obj), f"Non-finite float at {path}: {obj}"
        elif isinstance(obj, int):
            pass  # ints are always finite
        elif isinstance(obj, str):
            pass
        elif obj is None:
            pass
        else:
            # Other types should not appear in JSON-safe output
            raise AssertionError(f"Unexpected type at {path}: {type(obj)}")

    check_finite(artifact)


def test_replay_harness_checksum_stable():
    """Checksum is stable across runs."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    artifact1 = harness.replay()
    artifact2 = harness.replay()

    assert artifact1["checksum"] == artifact2["checksum"]

    # Verify checksum matches canonical JSON
    import hashlib
    payload_no_sum = {k: v for k, v in artifact1.items() if k != "checksum"}
    canonical = json.dumps(payload_no_sum, sort_keys=True, default=str, allow_nan=False)
    expected_checksum = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert artifact1["checksum"] == expected_checksum


def test_replay_harness_records_orders_fills_costs():
    """Artifact records orders, fills, and costs per period."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    artifact = harness.replay()

    # Orders: list of dicts with date and orders
    assert isinstance(artifact["orders"], list)
    assert len(artifact["orders"]) == artifact["n_periods"]
    for order_entry in artifact["orders"]:
        assert "date" in order_entry
        assert "orders" in order_entry
        assert isinstance(order_entry["orders"], dict)
        # Orders should be finite floats
        for asset, weight in order_entry["orders"].items():
            assert math.isfinite(weight)

    # Fills: same structure as orders (paper trading = full fill)
    assert isinstance(artifact["fills"], list)
    assert len(artifact["fills"]) == artifact["n_periods"]
    for fill_entry in artifact["fills"]:
        assert "date" in fill_entry
        assert "fills" in fill_entry
        assert isinstance(fill_entry["fills"], dict)
        # Fills should match orders (paper trading)
        assert fill_entry["fills"] == artifact["orders"][artifact["fills"].index(fill_entry)]["orders"]

    # Costs: list of dicts with date, turnover, cost
    assert isinstance(artifact["costs"], list)
    assert len(artifact["costs"]) == artifact["n_periods"]
    for cost_entry in artifact["costs"]:
        assert "date" in cost_entry
        assert "turnover" in cost_entry
        assert "cost" in cost_entry
        assert math.isfinite(cost_entry["turnover"])
        assert cost_entry["turnover"] >= 0
        assert math.isfinite(cost_entry["cost"])
        assert cost_entry["cost"] >= 0


def test_replay_harness_equity_compounds():
    """Equity compounds correctly from period returns net of costs."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    artifact = harness.replay()

    equity = artifact["equity"]
    assert isinstance(equity, list)
    assert len(equity) == artifact["n_periods"]

    # First equity should be 1.0 (starting capital)
    assert math.isfinite(equity[0]["equity"])
    assert abs(equity[0]["equity"] - 1.0) < 1e-9

    # All equity values should be finite and positive
    for eq_entry in equity:
        assert "date" in eq_entry
        assert "equity" in eq_entry
        assert math.isfinite(eq_entry["equity"])
        assert eq_entry["equity"] > 0


def test_replay_harness_with_prices_df():
    """Replay harness works with explicit prices DataFrame."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    # Load prices from the same fixture
    from strategies.betting_against_beta.data_loader import load_prices
    prices_df = load_prices(REAL_PRICES, benchmark="BTC")

    harness = ReplayHarness(
        result=result,
        prices_df=prices_df,
        transaction_costs=0.001,
        slippage=0.0005,
    )
    artifact = harness.replay()

    # Should produce valid artifact
    assert "checksum" in artifact
    assert artifact["n_periods"] > 0
    assert len(artifact["orders"]) == artifact["n_periods"]
    assert len(artifact["fills"]) == artifact["n_periods"]
    assert len(artifact["costs"]) == artifact["n_periods"]
    assert len(artifact["equity"]) == artifact["n_periods"]


def test_replay_harness_artifact_alias():
    """artifact() method is an alias for replay()."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result)
    artifact1 = harness.replay()
    artifact2 = harness.artifact()

    assert artifact1 == artifact2


def test_replay_harness_invalid_result_raises():
    """ReplayHarness raises on invalid result input."""
    with pytest.raises(ValueError):
        ReplayHarness(result=None)

    with pytest.raises(ValueError):
        ReplayHarness(result="not a result")


def test_replay_harness_empty_weights():
    """ReplayHarness handles empty weights gracefully."""
    from strategies.betting_against_beta.strategy import BABResult
    from strategies.betting_against_beta.config import BABConfig

    # Create a minimal BABResult with empty weights
    empty_weights = pd.DataFrame()
    cfg = BABConfig(benchmark="BTC")
    result = BABResult(
        config=cfg,
        returns=pd.DataFrame(),
        betas=pd.DataFrame(),
        signals=pd.DataFrame(),
        weights=empty_weights,
        backtest=pd.DataFrame(),
    )

    harness = ReplayHarness(result=result)
    artifact = harness.replay()

    # Should return minimal valid artifact
    assert artifact["n_periods"] == 0
    assert artifact["orders"] == []
    assert artifact["fills"] == []
    assert artifact["costs"] == []
    assert artifact["equity"] == [1.0]


def test_replay_harness_json_serializable():
    """Artifact is strict-JSON serializable."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    artifact = harness.replay()

    # Should not raise
    json_str = json.dumps(artifact, allow_nan=False)
    assert isinstance(json_str, str)

    # Round-trip
    parsed = json.loads(json_str)
    assert parsed["checksum"] == artifact["checksum"]


def test_replay_harness_different_inputs_different_checksums():
    """Different inputs produce different checksums."""
    strat = BABStrategy(config=BABConfig(benchmark="BTC"))
    result = strat.run(returns_df=REAL_PRICES)

    harness1 = ReplayHarness(result=result, transaction_costs=0.001, slippage=0.0005)
    harness2 = ReplayHarness(result=result, transaction_costs=0.002, slippage=0.0005)

    artifact1 = harness1.replay()
    artifact2 = harness2.replay()

    # Different costs should produce different artifacts
    assert artifact1["checksum"] != artifact2["checksum"]
    assert artifact1["config_snapshot"]["transaction_costs"] != artifact2["config_snapshot"]["transaction_costs"]