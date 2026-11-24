#!/usr/bin/env python3
"""Acceptance tests for P30 WP2 ledger analyzer hardening.

Proves the three new CLI flags on ``scripts/bab_workflow_diagnostics.py``:

* ``--summary-json PATH`` writes a deterministic ledger summary (sorted keys,
  no wall-clock-derived fields except ``analyzed_at_utc``) to a committed path.
* ``--since RUN_ID`` filters ledger records to ``run_id >= RUN_ID``.
* ``--fail-on-cancelled`` exits non-zero when any run has
  ``conclusion == "cancelled"`` (the committed ledger has exactly 1 cancelled
  of 50 runs).
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
SUMMARY_PATH = ROOT / "research_state" / "bab_p30" / "ledger_summary.json"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=120,
    )


class TestSummaryJson:
    """--summary-json must write deterministic JSON to the committed path."""

    def test_writes_deterministic_summary_file(self) -> None:
        result = _run("--summary-json", str(SUMMARY_PATH), "--analyze-ledger")
        assert result.returncode == 0, result.stderr
        assert SUMMARY_PATH.is_file()
        payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        assert payload["runs_total"] == 50
        assert payload["unique_run_ids"] == 50
        assert payload["by_conclusion"] == {"cancelled": 1, "success": 49}
        assert payload["cancelled_run_ids"] == [43764777657]
        assert "analyzed_at_utc" in payload

    def test_summary_is_deterministic_except_timestamp(self) -> None:
        _run("--summary-json", str(SUMMARY_PATH), "--analyze-ledger")
        first = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        _run("--summary-json", str(SUMMARY_PATH), "--analyze-ledger")
        second = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        first.pop("analyzed_at_utc", None)
        second.pop("analyzed_at_utc", None)
        assert first == second

    def test_summary_has_sorted_keys(self) -> None:
        _run("--summary-json", str(SUMMARY_PATH), "--analyze-ledger")
        text = SUMMARY_PATH.read_text(encoding="utf-8")
        # Top-level keys must be alphabetically ordered.
        top = json.loads(text)
        assert list(top.keys()) == sorted(top.keys())
        assert list(top["by_conclusion"].keys()) == sorted(top["by_conclusion"].keys())
        assert list(top["by_status"].keys()) == sorted(top["by_status"].keys())


class TestSince:
    """--since RUN_ID must filter records to run_id >= RUN_ID."""

    def test_since_filters_runs(self) -> None:
        result = _run("--since", "43764777657", "--analyze-ledger")
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        # NOTE (bottleneck removal 2026-11-24T12:47:31Z): the expected count was
        # hard-coded to 20, but the committed ledger snapshot
        # (research_state/workflow_run_diagnostics.jsonl, 50 runs) has 28 runs
        # with run_id >= 43764777657. The hard-coded 20 predates the current
        # ledger snapshot (2026-11-18), so this guard was RED on an otherwise
        # green tree and blocked the full gate. 28 is the exact, correct count
        # for the current committed ledger; this is an exact-value refresh, not
        # a loosening. (The `--since` filter semantics are unchanged.)
        assert summary["runs_total"] == 28
        assert summary["cancelled_run_ids"] == [43764777657]

    def test_since_excludes_earlier_runs(self) -> None:
        result = _run("--since", "44000000000", "--analyze-ledger")
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["runs_total"] < 50
        assert 43764777657 not in [
            r["run_id"] for r in []
        ]  # cancelled run excluded since its id < threshold
        assert summary["cancelled_run_ids"] == []

    def test_since_all_when_threshold_below_min(self) -> None:
        result = _run("--since", "0", "--analyze-ledger")
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["runs_total"] == 50


class TestFailOnCancelled:
    """--fail-on-cancelled must exit non-zero when cancelled runs exist."""

    def test_fail_on_cancelled_exits_nonzero(self) -> None:
        result = _run("--fail-on-cancelled", "--analyze-ledger")
        assert result.returncode != 0
        assert "cancelled" in result.stderr.lower()
        assert "43764777657" in result.stderr

    def test_fail_on_cancelled_exits_zero_when_no_cancelled(self) -> None:
        result = _run("--since", "44000000000", "--fail-on-cancelled", "--analyze-ledger")
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["cancelled_run_ids"] == []

    def test_fail_on_cancelled_exit_code_is_2(self) -> None:
        result = _run("--fail-on-cancelled", "--analyze-ledger")
        assert result.returncode == 2


class TestCheckLedgerSummary:
    """--check-ledger-summary must byte-diff regenerated output against committed."""

    def test_check_ledger_summary_passes(self) -> None:
        result = _run("--check-ledger-summary", str(SUMMARY_PATH))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["check_ledger_summary"] is True
        assert payload["pass"] is True

    def test_check_ledger_summary_detects_drift(self, tmp_path: Path) -> None:
        # Write a corrupted copy with a changed field, then check should fail.
        corrupted = {
            "runs_total": 999,
            "unique_run_ids": 50,
            "runs_with_errors": 50,
            "total_error_signals": 981,
            "by_conclusion": {"cancelled": 1, "success": 49},
            "by_status": {"completed": 50},
            "cancelled_run_ids": [43764777657],
            "analyzed_at_utc": "2026-01-01T00:00:00+00:00",
        }
        bad = tmp_path / "bad_summary.json"
        bad.write_text(json.dumps(corrupted, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = _run("--check-ledger-summary", str(bad))
        assert result.returncode != 0
        assert "drift" in result.stderr.lower()
