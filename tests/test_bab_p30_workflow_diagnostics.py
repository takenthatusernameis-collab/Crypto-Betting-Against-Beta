#!/usr/bin/env python3
"""Acceptance tests for P30: canonical workflow-diagnostics scanner + ledger analyzer.

Proves the extracted ``scripts/bab_workflow_diagnostics.py`` is the single source
of truth: its ``redact`` performs full secret redaction (superset of the old
inline test copy), ``scan_log_lines`` detects signals, and ``analyze_ledger``
deterministically classifies the committed ``research_state/workflow_run_diagnostics.jsonl``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "bab_workflow_diagnostics.py"
LEDGER = ROOT / "research_state" / "workflow_run_diagnostics.jsonl"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=120,
    )


class TestSelfTest:
    """The --self-test drift/redaction proof must pass and be non-vacuous."""

    def test_self_test_exit_zero(self) -> None:
        result = _run("--self-test")
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["self_test"] is True
        assert payload["pass"] is True

    def test_self_test_flags_redaction(self) -> None:
        result = _run("--self-test")
        payload = json.loads(result.stdout)
        assert payload["redaction_ok"] is True
        assert payload["rescan_safe"] is True
        assert payload["drift_detected"] is True


class TestRedaction:
    """redact() must redact every secret class the workflow redactor handles."""

    def test_bearer_redacted(self) -> None:
        result = _run("--scan-log", _write_log("Authorization: Bearer abc123def456ghi789\n"))
        assert result.returncode == 0, result.stderr
        assert "abc123def456ghi789" not in result.stdout

    def test_github_token_redacted(self) -> None:
        token = "ghp_abcdefghijklmnopqrstuvwxyz0123456789XYZ"
        result = _run("--scan-log", _write_log(f"token: {token}\n"))
        assert result.returncode == 0, result.stderr
        assert token not in result.stdout

    def test_secret_assignment_redacted(self) -> None:
        result = _run("--scan-log", _write_log("api_key=supersecretvalue123456\n"))
        assert result.returncode == 0, result.stderr
        assert "supersecretvalue123456" not in result.stdout


class TestScanLog:
    """scan_log_lines must detect signals and skip echoed source."""

    def test_clean_log_no_signals(self) -> None:
        path = _write_log("Starting Kilo activation: target=1000\n")
        result = _run("--scan-log", str(path))
        payload = json.loads(result.stdout)
        assert payload["count"] == 0

    def test_traceback_detected(self) -> None:
        path = _write_log("Traceback (most recent call last):\nValueError: boom\n")
        result = _run("--scan-log", str(path))
        payload = json.loads(result.stdout)
        assert payload["count"] >= 1
        assert payload["signals"][0]["line_number"] == 1

    def test_command_echo_skipped(self) -> None:
        echo = "\x1b[36;1mpytest -q\x1b[0m\n"
        path = _write_log(echo + "Error: real failure\n")
        result = _run("--scan-log", str(path))
        payload = json.loads(result.stdout)
        # Only the real failure line (line 2), not the echoed command (line 1).
        assert all(s["line_number"] != 1 for s in payload["signals"])


class TestLedgerAnalyzer:
    """analyze_ledger must deterministically classify the committed ledger."""

    def test_ledger_exists_and_nonempty(self) -> None:
        assert LEDGER.is_file()
        assert LEDGER.stat().st_size > 0

    def test_analyze_exit_zero(self) -> None:
        result = _run("--analyze-ledger")
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["runs_total"] >= 1
        assert summary["unique_run_ids"] >= 1

    def test_analyze_is_deterministic_except_timestamp(self) -> None:
        first = json.loads(_run("--analyze-ledger").stdout)
        second = json.loads(_run("--analyze-ledger").stdout)
        first.pop("analyzed_at_utc", None)
        second.pop("analyzed_at_utc", None)
        assert first == second

    def test_conclusion_counts_sum_to_total(self) -> None:
        summary = json.loads(_run("--analyze-ledger").stdout)
        assert sum(summary["by_conclusion"].values()) == summary["runs_total"]


def _write_log(content: str) -> str:
    import tempfile

    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False, encoding="utf-8"
    )
    handle.write(content)
    handle.close()
    return handle.name


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
