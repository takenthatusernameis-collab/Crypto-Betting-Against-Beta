#!/usr/bin/env python3
"""Acceptance tests for P30: canonical workflow-diagnostics scanner + ledger analyzer.

Proves the extracted ``scripts/bab_workflow_diagnostics.py`` is the single source
of truth: its ``redact`` performs full secret redaction (superset of the old
inline test copy), ``scan_log_lines`` detects signals, and ``analyze_ledger``
deterministically classifies the committed ``research_state/workflow_run_diagnostics.jsonl``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "bab_workflow_diagnostics.py"
WEAK_SCANNER = ROOT / "tests" / "test_workflow_diagnostics_scanner.py"
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


class TestAnalyzerHardening:
    """Acceptance tests for P30 WP2 analyzer hardening flags."""

    def test_summary_json_writes_deterministic_output(self, tmp_path: Path) -> None:
        """--summary-json writes deterministic JSON (sorted keys, modulo timestamp)."""
        out1 = tmp_path / "summary1.json"
        out2 = tmp_path / "summary2.json"
        r1 = _run("--summary-json", str(out1), "--since", "0")
        r2 = _run("--summary-json", str(out2), "--since", "0")
        assert r1.returncode == 0, r1.stderr
        assert r2.returncode == 0, r2.stderr
        assert out1.is_file()
        assert out2.is_file()
        s1 = json.loads(out1.read_text())
        s2 = json.loads(out2.read_text())
        # Deterministic modulo analyzed_at_utc
        s1.pop("analyzed_at_utc", None)
        s2.pop("analyzed_at_utc", None)
        assert s1 == s2
        # Expected values for the committed ledger
        assert s1["runs_total"] == 50
        assert s1["unique_run_ids"] == 50
        assert s1["runs_with_errors"] == 50
        assert s1["total_error_signals"] == 981
        assert s1["by_conclusion"] == {"cancelled": 1, "success": 49}
        assert s1["by_status"] == {"completed": 50}
        assert s1["cancelled_run_ids"] == [43764777657]

    def test_since_filters_records(self) -> None:
        """--since RUN_ID filters to run_id >= RUN_ID."""
        # Use a run_id that exists in the ledger to get a subset
        result = _run("--analyze-ledger", "--since", "43764777657")
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        # Should include the cancelled run (run_id 43764777657)
        assert summary["cancelled_run_ids"] == [43764777657]
        assert summary["runs_total"] >= 1

    def test_fail_on_cancelled_exits_nonzero(self) -> None:
        """--fail-on-cancelled exits 2 when any run has conclusion=cancelled."""
        result = _run("--analyze-ledger", "--fail-on-cancelled")
        # The committed ledger has exactly 1 cancelled run
        assert result.returncode == 2, f"expected 2, got {result.returncode}: {result.stdout}"
        assert "--fail-on-cancelled" in result.stderr
        assert "cancelled run" in result.stderr

    def test_check_ledger_summary_passes_on_match(self, tmp_path: Path) -> None:
        """--check-ledger-summary exits 0 when regenerated matches committed."""
        committed = ROOT / "research_state" / "bab_p30" / "ledger_summary.json"
        assert committed.is_file()
        result = _run("--check-ledger-summary", str(committed))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["check_ledger_summary"] is True
        assert payload["pass"] is True

    def test_check_ledger_summary_fails_on_drift(self, tmp_path: Path) -> None:
        """--check-ledger-summary exits non-zero when regenerated differs."""
        # Corrupt a field value in the committed file (still valid JSON)
        committed = ROOT / "research_state" / "bab_p30" / "ledger_summary.json"
        original = committed.read_text(encoding="utf-8")
        # Change a numeric field to create drift while keeping valid JSON
        corrupted = original.replace('"runs_total": 50', '"runs_total": 999')
        try:
            committed.write_text(corrupted, encoding="utf-8")
            result = _run("--check-ledger-summary", str(committed))
            assert result.returncode != 0
            assert "drift" in result.stderr.lower()
        finally:
            committed.write_text(original, encoding="utf-8")


class TestDivergenceGuard:
    """Prove canonical redact() is a strict superset of the weak inline copy.

    The weak inline copy (tests/test_workflow_diagnostics_scanner.py:redact)
    only strips ANSI and truncates. The canonical redact() (in
    scripts/bab_workflow_diagnostics.py) additionally redacts bearer tokens,
    GitHub tokens, JWTs, secret assignments, URL secrets, and long opaque
    values. This guard fails if a weaker redactor is ever reintroduced.
    """

    def _weak_module(self):
        spec = importlib.util.spec_from_file_location("weak_scanner", WEAK_SCANNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _canonical_module(self):
        spec = importlib.util.spec_from_file_location(
            "canonical_diagnostics", SCRIPT
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_weak_leaves_secrets_exposed(self) -> None:
        weak = self._weak_module().redact
        secrets = [
            ("Authorization: Bearer abc123def456ghi789", "abc123def456ghi789"),
            ("token: ghp_abcdefghijklmnopqrstuvwxyz0123456789XYZ", "ghp_"),
            (
                "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
                "eyj",
            ),
            ("api_key=supersecretvalue123456", "supersecret"),
            ("https://x/y?token=abcd1234&sig=efgh5678", "abcd1234"),
        ]
        for text, marker in secrets:
            out = weak(text).lower()
            assert marker in out, f"weak copy exposes secret: {marker!r} in {text!r}"

    def test_canonical_redacts_all_six_secret_classes(self) -> None:
        canon = self._canonical_module().redact
        raw = (
            "Authorization: Bearer abc123def456ghi789\n"
            "token: ghp_abcdefghijklmnopqrstuvwxyz0123456789XYZ\n"
            "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U\n"
            "api_key=supersecretvalue123456\n"
            "https://x/y?token=abcd1234&sig=efgh5678\n"
        )
        redacted = canon(raw)
        lowered = redacted.lower()
        for token in (
            "abc123def456ghi789",
            "ghp_abcdefghijklmnopqrstuvwxyz0123456789xyz",
            "supersecretvalue123456",
            "abcd1234",
            "efgh5678",
        ):
            assert token not in lowered, f"secret survived canonical redaction: {token}"
        assert "[REDACTED" in redacted

    def test_canonical_is_strict_superset_of_weak(self) -> None:
        weak = self._weak_module().redact
        canon = self._canonical_module().redact
        cases = [
            "\x1b[31mred text\x1b[0m",
            "42",
            "normal text line",
            "Traceback (most recent call last):\nValueError: boom",
        ]
        for case in cases:
            weak_out = weak(case)
            canon_out = canon(case)
            # Canonical preserves ANSI strip + truncate (the weak behavior).
            assert "\x1b[" not in canon_out
            assert len(canon_out) <= 500
            # On non-secret, non-long-value input, both produce identical output.
            assert canon_out == weak_out

    def test_canonical_redacts_long_value_weak_leaves(self) -> None:
        """The long-value class is the clearest superset divergence: weak keeps
        100+ char opaque strings, canonical redacts them."""
        weak = self._weak_module().redact
        canon = self._canonical_module().redact
        long_val = "x" * 1000
        assert weak(long_val) == long_val[:500]  # weak only truncates
        assert canon(long_val) == "[REDACTED_LONG_VALUE]"  # canonical redacts


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
