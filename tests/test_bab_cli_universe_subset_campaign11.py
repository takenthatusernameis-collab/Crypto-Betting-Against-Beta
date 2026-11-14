"""Campaign11: CLI/strategy --universe subset must affect backtest (regression).

Evidence (2026-11-09): `--universe ETH,SOL` on real fixtures produced identical
weights/final_cumulative to full universe; strategy resolved config.universe but
never subset returns, so beta/signals/weights ran on all data columns. Fixed by
subsetting returns to effective tradable universe + benchmark in strategy.run().
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data_loader import load_prices

REPO = Path(__file__).resolve().parents[1]
REAL = "tests/fixtures/real_market_prices.csv"
EXPANDED = "tests/fixtures/real_market_prices_expanded.csv"


def test_strategy_run_respects_universe_subset():
    df = load_prices(str(REPO / REAL), benchmark="BTC")
    full = BABStrategy(config=BABConfig(benchmark="BTC")).run(returns_df=df)
    sub = BABStrategy(config=BABConfig(universe=["ETH", "SOL"], benchmark="BTC")).run(returns_df=df)
    # weights should only contain benchmark + subset assets (no extra assets)
    assert set(sub.weights.columns) == {"BTC", "ETH", "SOL"}, list(sub.weights.columns)
    assert set(sub.weights.columns) != set(full.weights.columns)
    fc = float(sub.backtest["cumulative"].iloc[-1])
    assert math.isfinite(fc)
    assert fc != float(full.backtest["cumulative"].iloc[-1])


def test_strategy_universe_subset_expanded_fixture():
    df = load_prices(str(REPO / EXPANDED), benchmark="BTC")
    sub = BABStrategy(config=BABConfig(universe=["ETH", "SOL", "BNB"], benchmark="BTC")).run(
        returns_df=df
    )
    assert set(sub.weights.columns) == {"BTC", "ETH", "SOL", "BNB"}, list(sub.weights.columns)
    assert math.isfinite(float(sub.backtest["cumulative"].iloc[-1]))


def test_cli_universe_subset_real_data_json(tmp_path):
    out = tmp_path / "o.json"
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "strategies.betting_against_beta.cli",
            "--data",
            REAL,
            "--from-prices",
            "--benchmark",
            "BTC",
            "--universe",
            "ETH",
            "SOL",
            "--output",
            str(out),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"rc={r.returncode}\n{r.stderr}\n{r.stdout}"
    assert "Traceback" not in (r.stdout + r.stderr)
    d = json.loads(out.read_text())
    assert set(d["universe"]) == {"ETH", "SOL"}
    assert math.isfinite(float(d["final_cumulative"]))
    assert int(d["periods"]) > 0


def test_cli_universe_subset_expanded_dry_run_and_run(tmp_path):
    # dry-run valid
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "strategies.betting_against_beta.cli",
            "--dry-run",
            "--data",
            EXPANDED,
            "--from-prices",
            "--benchmark",
            "BTC",
            "--universe",
            "ETH",
            "SOL",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"rc={r.returncode}\n{r.stderr}\n{r.stdout}"
    assert "Traceback" not in (r.stdout + r.stderr)
    out = tmp_path / "o.json"
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "strategies.betting_against_beta.cli",
            "--data",
            EXPANDED,
            "--from-prices",
            "--benchmark",
            "BTC",
            "--universe",
            "ETH",
            "SOL",
            "--output",
            str(out),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"rc={r.returncode}\n{r.stderr}\n{r.stdout}"
    d = json.loads(out.read_text())
    assert set(d["universe"]) == {"ETH", "SOL"}
    assert math.isfinite(float(d["final_cumulative"]))
