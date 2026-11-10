"""Campaign11 slice (k): missing-benchmark error reporting parity (returns path).

Evidence-first probe (2026-11-10, HEAD `dd39b0f`): a benchmark column absent from
the data must surface the *same* actionable message on both the returns path
(`--data <returns.csv>`) and the prices path (`--data <prices.csv> --from-prices`).
Prior to the fix the returns path raised a misleading "Implausible return
detected" error (the data-quality campaign runs before the benchmark-presence
check), while the prices path reported "Benchmark 'X' not found in columns: ...".

This module locks the parity contract end-to-end via the CLI so no future
reordering can silently reintroduce the confusing message.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL_PRICES = "tests/fixtures/real_market_prices.csv"


def _run_cli(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _combined(res: subprocess.CompletedProcess[str]) -> str:
    return (res.stdout + res.stderr).strip()


class TestMissingBenchmarkReportingParity:
    def test_returns_path_reports_benchmark_not_found(self, tmp_path: Path):
        # Benchmark absent from a returns fixture must NOT surface the generic
        # implausible-return message; it must name the benchmark and the columns.
        res = _run_cli([
            "--data", REAL_PRICES, "--benchmark", "ZZZ", "--output", str(tmp_path / "o.json"),
        ])
        assert res.returncode == 1, f"rc={res.returncode}\n{_combined(res)}"
        msg = _combined(res).lower()
        assert "benchmark" in msg
        assert "not found" in msg or "missing benchmark coverage" in msg
        assert "implausible return" not in msg
        assert "traceback" not in msg

    def test_prices_path_reports_benchmark_not_found(self, tmp_path: Path):
        res = _run_cli([
            "--data", REAL_PRICES, "--from-prices", "--benchmark", "ZZZ",
            "--output", str(tmp_path / "o.json"),
        ])
        assert res.returncode == 1, f"rc={res.returncode}\n{_combined(res)}"
        msg = _combined(res).lower()
        assert "benchmark" in msg
        assert "not found" in msg or "missing benchmark coverage" in msg
        assert "implausible return" not in msg
        assert "traceback" not in msg

    def test_missing_benchmark_dry_run_both_paths(self):
        # --dry-run must also report the same actionable message on both paths.
        for extra in ([], ["--from-prices"]):
            res = _run_cli([
                "--dry-run", "--data", REAL_PRICES, "--benchmark", "ZZZ", *extra,
            ])
            assert res.returncode == 1, f"rc={res.returncode}\n{_combined(res)}"
            msg = _combined(res).lower()
            assert "benchmark" in msg
            assert "not found" in msg or "missing benchmark coverage" in msg
            assert "implausible return" not in msg