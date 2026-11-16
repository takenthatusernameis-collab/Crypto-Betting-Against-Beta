"""Characterization tests for P17-1: the data-quality gate must be
safe-by-default in the actual trading pipeline.

Each test below is RED on the pre-fix tree (lenient defaults 10000/3650/50,
un-wired ``BABStrategy``/CLI, ``load_prices`` hardcoding ``quality=False``)
and GREEN after the fix (defaults 20.0/7.0/3, pipeline enforces the gate).

These tests are the proof obligation for P17-1; do not weaken them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    load_prices,
    validate_returns_dataframe,
)
from strategies.betting_against_beta.strategy import BABStrategy


def _frozen(n: int = 8) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    live = np.linspace(0.02, 0.02 + 0.01 * n, n)
    return pd.DataFrame({"BTC": [0.01] * n, "ETH": live}, index=idx)


def _gappy() -> pd.DataFrame:
    idx = list(pd.date_range("2020-01-01", periods=5, freq="D"))
    idx[3] = idx[2] + pd.Timedelta(days=30)
    return pd.DataFrame(
        {"BTC": np.linspace(0.01, 0.05, 5), "ETH": np.linspace(0.02, 0.06, 5)},
        index=idx,
    )


class TestDefaultQualityRejectsImplausibleReturn:
    def test_default_rejects_100pct_return(self):
        df = _frozen()
        df.iloc[2, 0] = 100.0  # 10000% single-period return
        with pytest.raises(BABDataError, match="Implausible return"):
            validate_returns_dataframe(df, benchmark="ETH", quality=True)


class TestDefaultQualityRejectsGap:
    def test_default_rejects_30_day_gap(self):
        df = _gappy()
        with pytest.raises(BABDataError, match="Data gap too large"):
            validate_returns_dataframe(df, benchmark="ETH", quality=True)


class TestStrategyEnforcesGate:
    def test_strategy_run_rejects_frozen_input(self):
        # Default benchmark is BTC; the frozen column is BTC, so it would be
        # mistaken for the benchmark and slip through. Use ETH as benchmark so
        # the frozen BTC column is a tradable asset and must be rejected.
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            BABStrategy(returns_df=_frozen(), benchmark="ETH").run()


class TestLoadPricesEnforcesGate:
    def test_load_prices_rejects_absurd_return(self):
        prices = pd.DataFrame(
            {"BTC": [100.0, 100.0, 20000.0], "ETH": [10.0, 11.0, 12.0]},
            index=pd.date_range("2020-01-01", periods=3, freq="D"),
        )
        with pytest.raises(BABDataError, match="Implausible return"):
            load_prices(prices, benchmark="ETH")


class TestCliRejectsImplausibleData:
    def test_cli_dry_run_rejects_implausible_returns_csv(self, tmp_path: Path):
        csv = tmp_path / "bad.csv"
        idx = pd.date_range("2020-01-01", periods=8, freq="D")
        df = pd.DataFrame({"BTC": [0.01] * 8, "ETH": np.linspace(0.02, 0.03, 8)}, index=idx)
        df.iloc[2, 0] = 100.0
        df.index.name = "date"
        df.to_csv(csv)
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "strategies.betting_against_beta.cli",
                "--dry-run",
                "--data",
                str(csv),
                "--benchmark",
                "ETH",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0, "CLI must exit non-zero on implausible data"
        assert "INVALID" in proc.stdout or "Error" in proc.stdout

    def test_cli_dry_run_rejects_frozen_prices_csv(self, tmp_path: Path):
        csv = tmp_path / "frozen.csv"
        idx = pd.date_range("2020-01-01", periods=8, freq="D")
        df = pd.DataFrame(
            {"BTC": [100.0] * 8, "ETH": np.linspace(10.0, 11.0, 8)}, index=idx
        )
        df.index.name = "date"
        df.to_csv(csv)
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "strategies.betting_against_beta.cli",
                "--dry-run",
                "--data",
                str(csv),
                "--from-prices",
                "--benchmark",
                "ETH",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0, "CLI must exit non-zero on frozen price data"
        assert "INVALID" in proc.stdout or "Error" in proc.stdout


class TestCleanDataStillPasses:
    def test_clean_returns_pass_default_quality(self):
        idx = pd.date_range("2020-01-01", periods=30, freq="D")
        rng = np.random.default_rng(7)
        df = pd.DataFrame(
            {
                "BTC": rng.normal(0, 0.02, 30),
                "ETH": rng.normal(0, 0.02, 30),
                "MKT": rng.normal(0, 0.01, 30),
            },
            index=idx,
        )
        out = validate_returns_dataframe(df, benchmark="MKT", quality=True)
        assert list(out.columns) == ["BTC", "ETH", "MKT"]

    def test_clean_prices_pass_default_quality(self):
        idx = pd.date_range("2020-01-01", periods=30, freq="D")
        rng = np.random.default_rng(11)
        # Build prices as a stable geometric random walk starting from a
        # non-degenerate base so pct_change yields plausible daily returns.
        log_ret = rng.normal(0, 0.01, size=(30, 3))
        prices = pd.DataFrame(
            {
                "BTC": 10000.0 * np.exp(np.cumsum(log_ret[:, 0])),
                "ETH": 100.0 * np.exp(np.cumsum(log_ret[:, 1])),
                "MKT": 1000.0 * np.exp(np.cumsum(log_ret[:, 2])),
            },
            index=idx,
        )
        out = load_prices(prices, benchmark="MKT")
        assert "BTC" in out.columns