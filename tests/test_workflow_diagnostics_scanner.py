#!/usr/bin/env python3
"""Tests for the workflow diagnostics scanner logic.

These tests cover the diagnostic scanning functions used by the
Kilo General Agent Loop workflow to classify completed runs and
extract error signals from log archives.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from unittest import mock

import pytest


# Inline copies of the scanner functions from .github/workflows/main.yml
# so tests can run without depending on the full workflow file.

ANSI_RE = __import__("re").compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

ERROR_RE = __import__("re").compile(
    r"(?i)(::error::|\bexception\b|\btraceback\b|\bfatal\b|"
    r"\b(?:[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)|Error)\s*:\s*|"
    r"\bfailed\b|\bfailure\b|\bpermission denied\b|\btimed out\b|"
    r"\btimeout\b|\bModuleNotFoundError\b|\bAssertionError\b|"
    r"\bHTTP(?:/[\d.]+)?\s+(?:4\d\d|5\d\d)\b|\b(?:429|500|502|503|504)\b|"
    r"\brate.?limit(?:ed|ing)?\b|\bresource.?exhausted\b)"
)

COMMAND_ECHO_RE = __import__("re").compile(
    r"^(?:\d{4}-\d{2}-\d{2}T\S+Z\s+)?\x1b\[36;1m.*\x1b\[0m\s*$"
)


def redact(text: str, max_chars: int = 500) -> str:
    """Strip ANSI codes and truncate for safe log excerpts."""
    text = ANSI_RE.sub("", str(text))
    return text[:max_chars]


def scan_log_lines(log_text: str) -> list[dict]:
    """Scan log text for error signals, skipping echoed workflow source."""
    candidates = []
    for line_number, raw_line in enumerate(log_text.splitlines(), start=1):
        if COMMAND_ECHO_RE.match(raw_line):
            continue
        line = ANSI_RE.sub("", raw_line)
        if not ERROR_RE.search(line):
            continue
        candidates.append({
            "type": "log_signal",
            "line_number": line_number,
            "excerpt": redact(line),
        })
    return candidates


def build_log_archive(log_entries: dict[str, str]) -> bytes:
    """Build a ZIP archive of log files from a {filename: content} dict."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in log_entries.items():
            archive.writestr(filename, content)
    return buffer.getvalue()


class TestScanLogLines:
    """Tests for the log-line scanner."""

    def test_no_errors_returns_empty(self) -> None:
        assert scan_log_lines("All systems operational.\nNo issues found.\n") == []

    def test_detects_exception(self) -> None:
        log = "2024-01-01 ERROR: something failed\nTraceback (most recent call last):\n"
        results = scan_log_lines(log)
        assert len(results) == 2
        assert results[0]["line_number"] == 1
        assert "ERROR" in results[0]["excerpt"]

    def test_detects_failed(self) -> None:
        results = scan_log_lines("step failed with exit code 1\n")
        assert len(results) == 1
        assert "failed" in results[0]["excerpt"]

    def test_detects_http_500(self) -> None:
        results = scan_log_lines("GET /api HTTP/500\n")
        assert len(results) == 1
        assert "500" in results[0]["excerpt"]

    def test_detects_rate_limit(self) -> None:
        results = scan_log_lines("rate limit exceeded for user\n")
        assert len(results) == 1

    def test_skips_command_echo(self) -> None:
        # GitHub Actions echoes inline shell source in cyan ANSI.
        echo_line = "\x1b[36;1mset -Eeuo pipefail\x1b[0m"
        assert scan_log_lines(echo_line + "\n") == []

    def test_preserves_line_numbers(self) -> None:
        log = "line1\nline2\nexception: bad stuff\nline4\n"
        results = scan_log_lines(log)
        assert len(results) == 1
        assert results[0]["line_number"] == 3

    def test_truncates_long_excerpts(self) -> None:
        long_line = "exception: " + "x" * 1000
        results = scan_log_lines(long_line)
        assert len(results) == 1
        assert len(results[0]["excerpt"]) <= 500


class TestBuildLogArchive:
    """Tests for the log archive builder."""

    def test_creates_valid_zip(self) -> None:
        archive_bytes = build_log_archive({"a.txt": "hello", "b.txt": "world"})
        assert len(archive_bytes) > 0
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
            assert zf.namelist() == ["a.txt", "b.txt"]
            assert zf.read("a.txt") == b"hello"

    def test_empty_archive(self) -> None:
        archive_bytes = build_log_archive({})
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
            assert zf.namelist() == []


class TestRedact:
    """Tests for the redaction helper."""

    def test_strips_ansi(self) -> None:
        assert redact("\x1b[31mred text\x1b[0m") == "red text"

    def test_truncates(self) -> None:
        assert len(redact("x" * 1000)) <= 500

    def test_handles_non_string(self) -> None:
        # Should not raise on non-string input.
        result = redact(42)
        assert "42" in result


class TestErrorPatternClassification:
    """Tests for the ERROR_RE pattern."""

    @pytest.mark.parametrize("line", [
        "ModuleNotFoundError: No module named 'foo'",
        "AssertionError: expected True, got False",
        "Permission denied: cannot write to /root",
        "Request timed out after 30s",
        "HTTP/1.1 404 Not Found",
        "HTTP/2 503 Service Unavailable",
        "429 Too Many Requests",
        "500 Internal Server Error",
        "resource exhausted: api quota",
        "rate limiting applied",
    ])
    def test_matches_error(self, line: str) -> None:
        assert ERROR_RE.search(line) is not None, f"Expected match for: {line}"

    @pytest.mark.parametrize("line", [
        "All tests passed.",
        "INFO: processing complete",
        "Warning: deprecated function",
        "Debug: cache hit",
    ])
    def test_does_not_match_success(self, line: str) -> None:
        assert ERROR_RE.search(line) is None, f"Unexpected match for: {line}"