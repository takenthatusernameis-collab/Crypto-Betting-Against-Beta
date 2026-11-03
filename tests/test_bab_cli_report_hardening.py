"""Campaign C hardening tests for CLI and reporting paths.

Locks in the defensive behaviors added to ``cli.py`` and
``scripts/bab_backtest_report.py``: dry-run output validation, alias flags,
graceful JSON error payloads, and strict-finite serialization on adversarial
inputs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = REPO_ROOT / "strategies" / "betting_against_beta" / "cli.py"
REPORT = REPO_ROOT / "scripts" / "bab_backtest_report.py"

from strategies.betting_against_beta.cli import main as cli_main


def _env():
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    return env


def _run_cli(args):
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *args],
        capture_output=True, text=True, env=_env(), cwd=REPO_ROOT, timeout=120,
    )


def _run_report(args):
    return subprocess.run(
        [sys.executable, str(REPORT), *args],
        capture_output=True, text=True, env=_env(), cwd=REPO_ROOT, timeout=120,
    )


def _make_returns(tmp_path, n_days=200, seed=7):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n_days)
    df = pd.DataFrame(
        {"BTC": rng.normal(0.0, 0.01, n_days), "ETH": rng.normal(0.0, 0.015, n_days)},
        index=dates,
    )
    p = tmp_path / "rets.csv"
    df.to_csv(p)
    return p


class TestDryRunOutputValidation:
    """--dry-run must validate --output without writing."""

    def test_dry_run_rejects_unwritable_output(self, tmp_path):
        rc = cli_main([
            "--dry-run", "--synthetic",
            "--output", "/proc/cannot_write_here/out.json",
        ])
        assert rc == 1

    def test_dry_run_rejects_directory_output(self, tmp_path):
        rc = cli_main([
            "--dry-run", "--synthetic", "--output", str(tmp_path),
        ])
        assert rc == 1

    def test_dry_run_does_not_write_file(self, tmp_path):
        out = tmp_path / "out.json"
        rc = cli_main(["--dry-run", "--synthetic", "--output", str(out)])
        assert rc == 0
        assert not out.exists()

    def test_dry_run_valid_output_passes(self, tmp_path):
        out = tmp_path / "out.json"
        rc = cli_main(["--dry-run", "--synthetic", "--output", str(out)])
        assert rc == 0
        assert not out.exists()


class TestReportAliasFlags:
    """--returns and --returns-csv must behave like --data-source."""

    def test_returns_alias_synthetic(self):
        r = _run_report(["--returns", "synthetic", "--json"])
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "metrics" in data

    def test_returns_csv_alias(self, tmp_path):
        p = _make_returns(tmp_path)
        r = _run_report(["--returns-csv", str(p), "--benchmark", "BTC", "--json"])
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "metrics" in data

    def test_returns_alias_missing_file(self, tmp_path):
        r = _run_report(["--returns", str(tmp_path / "nope.csv"), "--json"])
        assert r.returncode != 0
        data = json.loads(r.stdout)
        assert "error" in data


class TestReportGracefulJsonErrors:
    """Bad config / data must still emit valid JSON with an error key."""

    def test_invalid_beta_window_json(self):
        r = _run_report(["--beta-window", "0", "--json"])
        assert r.returncode != 0
        data = json.loads(r.stdout)
        assert "error" in data
        assert "metrics" in data

    def test_invalid_quantile_json(self):
        r = _run_report(["--long-quantile", "2", "--json"])
        assert r.returncode != 0
        data = json.loads(r.stdout)
        assert "error" in data

    def test_empty_benchmark_json(self):
        r = _run_report(["--benchmark", "", "--json"])
        assert r.returncode != 0
        data = json.loads(r.stdout)
        assert "error" in data

    def test_all_nan_input_strict_json(self, tmp_path):
        dates = pd.date_range("2023-01-01", periods=10)
        df = pd.DataFrame({"BTC": [np.nan] * 10, "ETH": [np.nan] * 10}, index=dates)
        p = tmp_path / "nan.csv"
        df.to_csv(p)
        r = _run_report(["--data-source", str(p), "--benchmark", "BTC", "--json"])
        if r.returncode == 0:
            # Strict parse rejects NaN/Infinity/-Infinity tokens.
            json.loads(r.stdout, parse_constant=lambda t: pytest.fail(f"non-finite token: {t!r}"))
            for token in ("NaN", "Infinity", "-Infinity"):
                assert token not in r.stdout


class TestReportHumanReadableNoCrash:
    """Human-readable report must not crash on degenerate data."""

    def test_synthetic_human_readable(self):
        r = _run_report([])
        assert r.returncode == 0
        assert "BAB STRATEGY BACKTEST REPORT" in r.stdout

    def test_missing_file_human_readable(self, tmp_path):
        r = _run_report(["--data-source", str(tmp_path / "nope.csv")])
        assert r.returncode != 0


class TestCliUniverseValidation:
    """--universe must not silently swallow the flag value as an asset."""

    def test_universe_flag_consumed_correctly(self):
        rc = cli_main(["--universe", "BTC", "ETH", "--synthetic"])
        assert rc == 0

    def test_universe_only_flag_uses_synthetic(self):
        rc = cli_main(["--universe", "--synthetic"])
        assert rc == 0