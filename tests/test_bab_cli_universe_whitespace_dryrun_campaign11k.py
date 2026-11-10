"""Campaign11 slice (k): CLI universe whitespace-normalization + dry-run deep-output invariants.

Evidence-first, non-duplicative (probed 2026-11-10 @ HEAD 6ae6381, clean):
  - padded valid tokens (`' ETH '`, `'SOL '`) are stripped and de-duplicated;
    existing `universe_edge` covers duplicates of identical tokens but not
    padding/mixed whitespace, and `universe_explicit_contract` covers
    whitespace-only rejection — this locks the *successful normalization* path.
  - benchmark token duplicated inside an explicit universe is de-duplicated
    alongside others; strict-finite output.
  - `--dry-run` with a deep/non-existent `--output` parent validates the path
    (parents may be created by validation) but writes no output file and prints
    resolved config; strict success, no Traceback.

No production edits. No assertions weakened. All cases probed green before test.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = "tests/fixtures/real_market_prices.csv"


def _run_cli(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _assert_strict_finite(payload: dict) -> None:
    raw = json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and not isinstance(payload, bool)
    assert payload["periods"] > 0


class TestCliUniverseWhitespaceNormalization:
    def test_padded_valid_tokens_stripped_and_finite(self, tmp_path: Path):
        out = tmp_path / "ws.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", " ETH ", "SOL ", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        d = json.loads(out.read_text())
        _assert_strict_finite(d)
        assert d["universe"] == ["ETH", "SOL"]

    def test_padded_duplicate_tokens_deduped(self, tmp_path: Path):
        out = tmp_path / "wsdup.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", " ETH", "ETH ", " SOL ", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        d = json.loads(out.read_text())
        _assert_strict_finite(d)
        assert d["universe"] == ["ETH", "SOL"]

    def test_benchmark_duplicated_in_universe_deduped(self, tmp_path: Path):
        out = tmp_path / "bdup.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "BTC", "ETH", "BTC", "SOL", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        d = json.loads(out.read_text())
        _assert_strict_finite(d)
        # Benchmark remains in the user-requested universe list (it is a valid
        # tradable token in this fixture and de-duplication preserves first seen).
        assert d["universe"] == ["BTC", "ETH", "SOL"]


class TestCliDryRunDeepOutput:
    def test_dry_run_deep_output_validates_no_write(self, tmp_path: Path):
        out = tmp_path / "deep" / "nested" / "out.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "ETH", "SOL",
            "--output", str(out), "--dry-run",
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        # Dry-run must not write the backtest output file.
        assert not out.exists(), f"dry-run unexpectedly wrote {out}"
        assert "Resolved BAB configuration" in res.stdout
        assert "benchmark" in res.stdout.lower()

    def test_dry_run_reports_explicit_universe(self, tmp_path: Path):
        out = tmp_path / "x" / "o.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "ETH", "SOL", "--output", str(out), "--dry-run",
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "ETH" in res.stdout and "SOL" in res.stdout
        assert not out.exists()
