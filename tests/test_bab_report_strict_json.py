"""Tests for strict JSON output in scripts/bab_backtest_report.py.

The report's --json payload must be parseable by a strict JSON parser
(``allow_nan=False``). ``json.dumps`` with the default ``allow_nan=True``
emits bare ``NaN`` / ``Infinity`` / ``-Infinity`` tokens, which are not valid
JSON per RFC 8259. This regression test guards against that drift.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "bab_backtest_report.py"
MESSY_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "real_data_defects.csv"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    import os
    import sys

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


def _strict_parse(text: str) -> dict:
    """Parse JSON with strict RFC 8259 rules (no NaN/Infinity tokens)."""
    return json.loads(text, parse_constant=_reject_nonfinite)


def _reject_nonfinite(token: str):
    raise ValueError(f"non-finite JSON token emitted: {token!r}")


class TestStrictJsonOutput:
    def test_json_payload_is_strictly_parseable_on_messy_data(self):
        result = _run([
            "--data-source", str(MESSY_FIXTURE),
            "--benchmark", "BTC",
            "--beta-window", "3",
            "--min-observations", "2",
            "--json",
        ])
        assert result.returncode == 0, result.stderr
        # Strict parse rejects NaN/Infinity/-Infinity tokens.
        payload = _strict_parse(result.stdout)
        assert "metrics" in payload
        assert "config" in payload

    def test_json_payload_is_strictly_parseable_on_degenerate_data(self):
        DEGENERATE = REPO_ROOT / "tests" / "fixtures" / "degenerate_metrics.csv"
        result = _run([
            "--data-source", str(DEGENERATE),
            "--benchmark", "BTC",
            "--beta-window", "3",
            "--min-observations", "2",
            "--json",
        ])
        assert result.returncode == 0, result.stderr
        payload = _strict_parse(result.stdout)
        assert "metrics" in payload

    def test_json_payload_is_strictly_parseable_on_synthetic(self):
        result = _run(["--json"])
        assert result.returncode == 0, result.stderr
        payload = _strict_parse(result.stdout)
        assert "metrics" in payload

    def test_allow_nan_false_on_raw_output(self):
        """The raw stdout must not contain bare NaN/Infinity tokens."""
        result = _run([
            "--data-source", str(MESSY_FIXTURE),
            "--benchmark", "BTC",
            "--beta-window", "3",
            "--min-observations", "2",
            "--json",
        ])
        assert result.returncode == 0, result.stderr
        # A strict dump with allow_nan=False would raise; verify the literal
        # tokens are absent from the output text.
        for token in ("NaN", "Infinity", "-Infinity"):
            assert token not in result.stdout, f"non-finite token {token!r} emitted"


class TestSanitizeMetricsContract:
    def test_sanitize_metrics_replaces_nonfinite(self):
        from scripts import bab_backtest_report

        sanitized = bab_backtest_report._sanitize_metrics({
            "sharpe_ratio": float("nan"),
            "final_cumulative": float("inf"),
            "max_drawdown": float("-inf"),
            "n_observations": 100,
            "total_return": 0.05,
        })
        assert sanitized["sharpe_ratio"] == 0.0
        assert sanitized["final_cumulative"] == 0.0
        assert sanitized["max_drawdown"] == 0.0
        assert sanitized["n_observations"] == 100
        assert sanitized["total_return"] == 0.05

    def test_dumps_json_rejects_nonfinite(self):
        from scripts import bab_backtest_report

        # Should not raise even if a nonfinite value sneaks into the payload.
        out = bab_backtest_report._dumps_json({"a": float("nan"), "b": 1.0})
        parsed = json.loads(out)
        assert parsed == {"a": 0.0, "b": 1.0}