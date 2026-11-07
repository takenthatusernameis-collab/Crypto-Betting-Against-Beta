"""Campaign C: console-script entry point and adversarial CLI hardening.

Locks in defensive behavior for the ``bab-example`` console script
(``scripts/load_real_bab_example.py``) and the module CLI against malformed
backtest frames, missing files, and degenerate data.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CONSOLE_SCRIPT = REPO_ROOT / "scripts" / "load_real_bab_example.py"
CLI_MODULE = REPO_ROOT / "strategies" / "betting_against_beta" / "cli.py"

from strategies.betting_against_beta.cli import main as cli_main


def _env():
    import os as _os
    env = dict(_os.environ)
    # Preserve the full inherited PYTHONPATH (repo root + any dependency
    # install dirs such as pylib) so subprocesses can import pandas/numpy/scipy.
    env["PYTHONPATH"] = _os.pathsep.join(
        p for p in (str(REPO_ROOT), _os.environ.get("PYTHONPATH", "")) if p
    )
    return env


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


def _run_console(args, cwd=REPO_ROOT):
    return subprocess.run(
        [sys.executable, str(CONSOLE_SCRIPT), *args],
        capture_output=True, text=True, env=_env(), cwd=cwd, timeout=120,
    )


class TestConsoleScriptBehavior:
    def test_console_synthetic_via_returns(self, tmp_path):
        p = _make_returns(tmp_path)
        r = _run_console([str(p), "--benchmark", "BTC"])
        assert r.returncode == 0
        assert "cumulative_return=" in r.stdout
        assert "periods=" in r.stdout

    def test_console_from_prices(self, tmp_path):
        rng = np.random.RandomState(7)
        dates = pd.date_range("2023-01-01", periods=200)
        base = 100.0 + np.cumsum(rng.normal(0.0, 1.0, 200))
        df = pd.DataFrame(
            {
                "BTC": base,
                "ETH": base * 0.8 + rng.normal(0.0, 0.5, 200),
            },
            index=dates,
        )
        p = tmp_path / "prices.csv"
        df.to_csv(p)
        r = _run_console([str(p), "--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 0
        assert "cumulative_return=" in r.stdout

    def test_console_missing_file_exits_nonzero(self, tmp_path):
        r = _run_console([str(tmp_path / "nope.csv")])
        assert r.returncode != 0

    def test_console_benchmark_mismatch(self, tmp_path):
        p = _make_returns(tmp_path)
        r = _run_console([str(p), "--benchmark", "NOTPRESENT"])
        assert r.returncode != 0

    def test_console_invalid_quantile(self, tmp_path):
        p = _make_returns(tmp_path)
        r = _run_console([str(p), "--quantile", "5.0"])
        assert r.returncode != 0


class TestCliAdversarialPaths:
    def test_cli_output_to_nested_missing_dir(self, tmp_path):
        out = tmp_path / "nested" / "deep" / "out.json"
        rc = cli_main(["--synthetic", "--output", str(out)])
        assert rc == 0
        assert out.exists()
        data = json.loads(out.read_text())
        assert isinstance(data["final_cumulative"], float)

    def test_cli_output_unwritable_path(self, tmp_path):
        rc = cli_main(["--synthetic", "--output", "/proc/cannot_write_here/out.json"])
        assert rc == 1

    def test_cli_output_directory_target(self, tmp_path):
        rc = cli_main(["--synthetic", "--output", str(tmp_path)])
        assert rc == 1

    def test_cli_bad_beta_window(self):
        rc = cli_main(["--synthetic", "--beta-window", "0"])
        assert rc == 1

    def test_cli_bad_quantile(self):
        rc = cli_main(["--synthetic", "--long-quantile", "2.0"])
        assert rc == 1

    def test_cli_empty_benchmark(self):
        rc = cli_main(["--synthetic", "--benchmark", ""])
        assert rc == 1

    def test_cli_nonexistent_data_file(self, tmp_path):
        rc = cli_main(["--data", str(tmp_path / "nope.csv"), "--benchmark", "BTC"])
        assert rc == 1

    def test_cli_dry_run_does_not_write(self, tmp_path):
        out = tmp_path / "out.json"
        rc = cli_main(["--dry-run", "--synthetic", "--output", str(out)])
        assert rc == 0
        assert not out.exists()

    def test_cli_output_json_is_strict(self, tmp_path):
        out = tmp_path / "out.json"
        rc = cli_main(["--synthetic", "--output", str(out)])
        assert rc == 0
        raw = out.read_text()
        # Strict parse rejects NaN/Infinity/-Infinity tokens.
        json.loads(raw, parse_constant=lambda t: pytest.fail(f"non-finite token: {t!r}"))
        for token in ("NaN", "Infinity", "-Infinity"):
            assert token not in raw

    def test_cli_universe_only_flag(self):
        rc = cli_main(["--universe", "--synthetic"])
        assert rc == 0

    def test_cli_universe_consumed_correctly(self):
        rc = cli_main(["--universe", "BTC", "ETH", "--synthetic"])
        assert rc == 0

    def test_cli_rebalance_weekly(self, tmp_path):
        p = _make_returns(tmp_path)
        rc = cli_main(["--data", str(p), "--rebalance-freq", "weekly"])
        assert rc == 0

    def test_cli_rebalance_invalid_freq(self):
        rc = cli_main(["--synthetic", "--rebalance-freq", "hourly"])
        # Unknown freq falls back to daily (no crash); assert non-crashing.
        assert rc == 0

    def test_cli_synthetic_default(self):
        rc = cli_main([])
        assert rc == 0