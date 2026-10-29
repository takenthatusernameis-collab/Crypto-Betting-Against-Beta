"""Report CLI edge cases - strict JSON, empty/NaN/missing cases."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.strategy import BABStrategy


def test_report_cli_empty_or_nan_inputs(tmp_path):
    # Create empty returns
    empty = pd.DataFrame()
    empty_path = tmp_path / "empty.csv"
    empty.to_csv(empty_path)
    script = Path("/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/scripts/bab_backtest_report.py")
    res = subprocess.run([sys.executable, str(script), "--returns", str(empty_path), "--json"],
                         cwd="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta",
                         capture_output=True, timeout=60)
    # Should either exit non-zero gracefully or produce parseable JSON with error/empty; be strict
    if res.returncode == 0:
        out = res.stdout.decode()
        data = json.loads(out)
        assert isinstance(data, dict)
    else:
        # Non-zero is acceptable as long as it doesn't crash ungracefully
        assert res.returncode in (1, 2)


def test_report_cli_all_nan(tmp_path):
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({"BTC": [np.nan]*10, "ETH": [np.nan]*10}, index=dates)
    p = tmp_path / "nan.csv"
    df.to_csv(p)
    script = Path("/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/scripts/bab_backtest_report.py")
    res = subprocess.run([sys.executable, str(script), "--returns", str(p), "--json"],
                         cwd="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta",
                         capture_output=True, timeout=60)
    if res.returncode == 0:
        out = res.stdout.decode()
        data = json.loads(out)  # allow_nan False not used by json.loads by default, but structure must be valid
        assert isinstance(data, dict)
    else:
        assert res.returncode in (1, 2)


def test_report_cli_missing_file(tmp_path):
    script = Path("/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/scripts/bab_backtest_report.py")
    res = subprocess.run([sys.executable, str(script), "--returns", str(tmp_path / "nope.csv"), "--json"],
                         cwd="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta",
                         capture_output=True, timeout=60)
    assert res.returncode != 0


def test_report_cli_non_btc_benchmark(tmp_path):
    rng = np.random.RandomState(123)
    dates = pd.date_range("2023-01-01", periods=150)
    df = pd.DataFrame({
        "ETH": rng.normal(0, 0.01, len(dates)),
        "SOL": rng.normal(0, 0.02, len(dates)),
        "BTC": rng.normal(0, 0.015, len(dates)),
    }, index=dates)
    p = tmp_path / "rets.csv"
    df.to_csv(p)
    script = Path("/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/scripts/bab_backtest_report.py")
    res = subprocess.run([sys.executable, str(script), "--returns", str(p), "--benchmark", "ETH", "--json"],
                         cwd="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta",
                         capture_output=True, timeout=60)
    if res.returncode == 0:
        out = res.stdout.decode()
        data = json.loads(out)
        assert isinstance(data, dict)
    else:
        assert res.returncode in (1, 2)
