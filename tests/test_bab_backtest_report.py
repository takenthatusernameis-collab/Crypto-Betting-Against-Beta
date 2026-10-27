"""Tests for the BAB backtest report CLI (scripts/bab_backtest_report.py).

Covers the --returns-csv alias, CSV/JSON/synthetic dispatch, and the
machine-readable --json output contract.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "bab_backtest_report.py"


def _make_returns(rows: int = 300, path: Path | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    idx = pd.date_range("2022-01-01", periods=rows, freq="D")
    bench = rng.normal(0.0005, 0.02, rows)
    data = {"BTC": bench}
    for i, a in enumerate(["ETH", "SOL", "BNB", "XRP", "ADA"]):
        data[a] = (0.5 + 0.5 * i) * bench + rng.normal(0, 0.01, rows)
    df = pd.DataFrame(data, index=idx)
    if path is not None:
        df.to_csv(path)
    return df


def _run(args: list[str]) -> subprocess.CompletedProcess:
    env = {"PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


class TestReportCli:
    def test_returns_csv_alias_loads_real_data(self, tmp_path: Path):
        csv = tmp_path / "returns.csv"
        _make_returns(path=csv)
        result = _run(["--returns-csv", str(csv), "--benchmark", "BTC", "--json"])
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["config"]["data_source"] == str(csv)
        assert payload["config"]["universe"] == ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA"]
        assert payload["rebalances"] == 300
        for key in (
            "sharpe_ratio",
            "annualized_volatility",
            "max_drawdown",
            "turnover",
            "strategy_beta",
            "total_return",
            "final_cumulative",
            "n_observations",
        ):
            assert key in payload["metrics"]

    def test_data_source_alias_still_works(self, tmp_path: Path):
        csv = tmp_path / "returns.csv"
        _make_returns(path=csv)
        result = _run(["--data-source", str(csv), "--benchmark", "BTC", "--json"])
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["config"]["data_source"] == str(csv)

    def test_returns_csv_missing_file_fails(self, tmp_path: Path):
        result = _run(["--returns-csv", str(tmp_path / "nope.csv"), "--json"])
        assert result.returncode != 0

    def test_synthetic_default_runs(self):
        result = _run(["--json"])
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["config"]["data_source"] is None
        assert payload["rebalances"] > 0

    def test_human_readable_report_prints_sections(self, tmp_path: Path):
        csv = tmp_path / "returns.csv"
        _make_returns(path=csv)
        result = _run(["--returns-csv", str(csv), "--benchmark", "BTC"])
        assert result.returncode == 0, result.stderr
        out = result.stdout
        assert "BAB STRATEGY BACKTEST REPORT" in out
        assert "Sharpe Ratio" in out
        assert "Max Drawdown" in out
        assert "Strategy Beta" in out

    def test_json_report_is_machine_readable(self):
        result = _run(["--json"])
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert isinstance(payload["rebalances"], int)
        assert isinstance(payload["metrics"], dict)