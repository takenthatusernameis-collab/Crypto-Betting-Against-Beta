"""Campaign11: real-data CLI end-to-end regression (mandatory, HANDOFF item 2).

Locks in the repo's core real-data path (BAB real backtests):
  --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output <tmp>
  -> rc 0, finite allow_nan=False JSON, final_cumulative finite scalar, periods int,
     no traceback. Also locks dry-run validity for the same path.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REAL_PRICES = "tests/fixtures/real_market_prices.csv"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestRealDataCliEndToEndRegression:
    def test_real_data_from_prices_output_json_finite(self, tmp_path: Path):
        out = tmp_path / "out.json"
        res = _run_cli(
            [
                "--data",
                REAL_PRICES,
                "--from-prices",
                "--benchmark",
                "BTC",
                "--output",
                str(out),
            ]
        )
        assert res.returncode == 0, f"rc={res.returncode}\nstdout={res.stdout}\nstderr={res.stderr}"
        assert "Traceback" not in res.stdout
        assert "Traceback" not in res.stderr
        assert out.exists(), f"output file missing; stdout={res.stdout} stderr={res.stderr}"
        raw = out.read_text()
        # Strict JSON (no NaN/Infinity tokens) — allow_nan=False enforced by CLI; verify parse.
        payload = json.loads(raw)
        json.dumps(payload, allow_nan=False)
        for tok in ("NaN", "Infinity", "-Infinity"):
            assert tok not in raw
        fc = payload["final_cumulative"]
        assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
        assert math.isfinite(float(fc))
        periods = payload["periods"]
        assert isinstance(periods, int) and not isinstance(periods, bool)
        assert periods > 0
        assert payload["benchmark"] == "BTC"

    def test_real_data_from_prices_dry_run_valid(self):
        res = _run_cli(
            [
                "--dry-run",
                "--data",
                REAL_PRICES,
                "--from-prices",
                "--benchmark",
                "BTC",
            ]
        )
        assert res.returncode == 0, f"rc={res.returncode}\nstdout={res.stdout}\nstderr={res.stderr}"
        assert "Traceback" not in res.stdout
        assert "Traceback" not in res.stderr
        # Evidence: dry-run reports resolved/valid config path.
        combined = (res.stdout + res.stderr).lower()
        assert "valid" in combined or "resolved" in combined or "dry" in combined
