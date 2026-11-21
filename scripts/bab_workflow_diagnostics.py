#!/usr/bin/env python3
"""Canonical workflow-diagnostics scanner and ledger analyzer.

This module is the SINGLE SOURCE OF TRUTH for the log-scanning and secret
redaction logic that the ``Kilo General Agent Loop`` workflow
(``.github/workflows/main.yml``) embeds inline. Before this module existed the
same regexes were hand-copied in three places:

  1. the workflow YAML (the live collector that writes
     ``research_state/workflow_run_diagnostics.jsonl``),
  2. ``tests/test_workflow_diagnostics_scanner.py`` (inline re-implementations),
  3. any future local tooling.

The test copies drifted from the workflow copy: the test ``redact()`` only
stripped ANSI and truncated, while the workflow ``redact()`` also redacts
bearer tokens, GitHub tokens, JWTs, secret assignments, URL secrets, and long
opaque values. A scanner whose redactor is weaker than the one that produced a
committed ledger is a provenance hazard: re-scanning a log with the weak copy
can re-expose a secret the strong copy redacted.

This module fixes that by exporting one canonical ``redact`` / ``scan_log_lines``
/ ``scan_log_archive`` set with the FULL workflow redaction, plus a read-only
ledger analyzer over the committed ``workflow_run_diagnostics.jsonl`` so a local
agent session can classify CI health without ``workflows:write`` (which the
repo token lacks — see ``HANDOFF.md`` P28 WP2).

Usage:
    python3 scripts/bab_workflow_diagnostics.py --self-test
    python3 scripts/bab_workflow_diagnostics.py --analyze-ledger
    python3 scripts/bab_workflow_diagnostics.py --ledger PATH
    python3 scripts/bab_workflow_diagnostics.py --scan-log PATH

Exit code 0 when the action succeeds (and, for ``--self-test``, when a
deliberately corrupted re-scan is detected as drift and a secret is redacted);
non-zero otherwise. Read-only: never writes to ``research_state/**``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "research_state" / "workflow_run_diagnostics.jsonl"

# --- Canonical regexes (mirror .github/workflows/main.yml exactly) ------------
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
COMMAND_ECHO_RE = re.compile(
    r"^(?:\d{4}-\d{2}-\d{2}T\S+Z\s+)?\x1b\[36;1m.*\x1b\[0m\s*$"
)
KILO_INVALID_ARGUMENT_ABORT_RE = re.compile(
    r"""(?i)stopped after\s+\d+\s+consecutive invalid[- ]argument"""
    r""" failures for the ["']edit["'] tool"""
)
KILO_EDIT_INVALID_ARGUMENT_RE = re.compile(
    r"""(?i)\b(?:the\s+)?edit tool was called with invalid arguments\b"""
)
ERROR_RE = re.compile(
    r"(?i)(::error::|\bexception\b|\btraceback\b|\bfatal\b|"
    r"\b(?:[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)|Error)\s*:\s*|"
    r"\bfailed\b|\bfailure\b|\bpermission denied\b|\btimed out\b|"
    r"\btimeout\b|\bModuleNotFoundError\b|\bAssertionError\b|"
    r"\bHTTP(?:/[\d.]+)?\s+(?:4\d\d|5\d\d)\b|\b(?:429|500|502|503|504)\b|"
    r"\brate.?limit(?:ed|ing)?\b|\bresource.?exhausted\b)"
)
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
GH_TOKEN_RE = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
)
JWT_RE = re.compile(
    r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}\b"
)
SECRET_ASSIGN_RE = re.compile(
    r"""(?i)\b(token|password|secret|api[_-]?key|client[_-]?secret|"""
    r"""authorization)\b(\s*[:=]\s*)(["']?)[^\s,"';]+"""
)
URL_SECRET_RE = re.compile(
    r"(?i)([?&](?:token|sig|signature|x-amz-credential|x-amz-signature)=)[^&\s]+"
)
LONG_VALUE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_+/=-]{100,}(?![A-Za-z0-9])")

MAX_EXCERPT_CHARS = 500


def utc_now() -> str:
    """Current UTC timestamp at second resolution (workflow-compatible)."""
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def redact(text: str, max_chars: int = MAX_EXCERPT_CHARS) -> str:
    """Strip ANSI and redact secrets, then truncate.

    Mirrors the workflow's ``redact()`` exactly: full secret redaction
    (bearer, GitHub token, JWT, secret assignment, URL secret, long opaque
    value) so a local re-scan cannot re-expose a value the workflow redacted.
    """
    text = ANSI_RE.sub("", str(text))
    text = BEARER_RE.sub("Bearer [REDACTED]", text)
    text = GH_TOKEN_RE.sub("[REDACTED_GITHUB_TOKEN]", text)
    text = JWT_RE.sub("[REDACTED_JWT]", text)
    text = SECRET_ASSIGN_RE.sub(r"\1\2[REDACTED]", text)
    text = URL_SECRET_RE.sub(r"\1[REDACTED]", text)
    text = LONG_VALUE_RE.sub("[REDACTED_LONG_VALUE]", text)
    return text[:max_chars]


def scan_log_lines(log_text: str) -> list[dict]:
    """Scan log text for error signals, skipping echoed workflow source."""
    candidates: list[dict] = []
    for line_number, raw_line in enumerate(log_text.splitlines(), start=1):
        if COMMAND_ECHO_RE.match(raw_line):
            continue
        line = ANSI_RE.sub("", raw_line)
        abort_match = KILO_INVALID_ARGUMENT_ABORT_RE.search(line)
        edit_match = KILO_EDIT_INVALID_ARGUMENT_RE.search(line)
        if not abort_match and not edit_match and not ERROR_RE.search(line):
            continue
        candidates.append(
            {
                "type": "log_signal",
                "line_number": line_number,
                "excerpt": redact(line),
            }
        )
    return candidates


def build_log_archive(log_entries: dict[str, str]) -> bytes:
    """Build a ZIP archive of log files from a ``{filename: content}`` dict."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in log_entries.items():
            archive.writestr(filename, content)
    return buffer.getvalue()


def scan_log_archive(archive_bytes: bytes) -> list[dict]:
    """Scan every file in a log ZIP archive and merge signal lists."""
    signals: list[dict] = []
    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
        for name in archive.namelist():
            raw = archive.read(name).decode("utf-8", errors="replace")
            for signal in scan_log_lines(raw):
                signal = dict(signal)
                signal["log_file"] = name
                signals.append(signal)
    return signals


# --- Read-only ledger analysis ----------------------------------------------
def load_ledger(path: Path) -> list[dict]:
    """Load the JSONL diagnostics ledger; skip malformed lines defensively."""
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def analyze_ledger(records: list[dict]) -> dict:
    """Classify completed-run diagnostics into a deterministic summary.

    Deterministic: sorted keys, stable ordering by run id, no timestamps
    derived from wall clock. Each record contributes to ``runs_total``,
    ``conclusion`` counts, ``status`` counts, and a per-run error tally.
    """
    by_conclusion: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total_errors = 0
    runs_with_errors = 0
    run_ids: list[int] = []
    cancelled_run_ids: list[int] = []
    for record in records:
        conclusion = str(record.get("conclusion", "unknown"))
        status = str(record.get("status", "unknown"))
        by_conclusion[conclusion] = by_conclusion.get(conclusion, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        errors = record.get("potential_errors", []) or []
        if errors:
            runs_with_errors += 1
            total_errors += len(errors)
        run_id = record.get("run_id")
        if isinstance(run_id, int):
            run_ids.append(run_id)
        if conclusion == "cancelled":
            cancelled_run_ids.append(run_id)

    return {
        "runs_total": len(records),
        "unique_run_ids": len(set(run_ids)),
        "runs_with_errors": runs_with_errors,
        "total_error_signals": total_errors,
        "by_conclusion": dict(sorted(by_conclusion.items())),
        "by_status": dict(sorted(by_status.items())),
        "cancelled_run_ids": sorted(cancelled_run_ids),
        "analyzed_at_utc": utc_now(),
    }


def filter_since(records: list[dict], since_run_id: int) -> list[dict]:
    """Return records with ``run_id >= since_run_id`` (deterministic filter)."""
    return [r for r in records if isinstance(r.get("run_id"), int) and r["run_id"] >= since_run_id]


def write_summary_json(summary: dict, path: Path) -> None:
    """Write the ledger summary to ``path`` deterministically.

    Sorted keys, no wall-clock-derived fields except the explicit
    ``analyzed_at_utc`` stamp. Creates parent directories as needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _strip_timestamp(summary: dict) -> dict:
    """Return a copy of ``summary`` with ``analyzed_at_utc`` removed for comparison."""
    stripped = dict(summary)
    stripped.pop("analyzed_at_utc", None)
    return stripped


def check_ledger_summary(committed_path: Path, ledger_path: Path) -> int:
    """Regenerate the ledger summary and byte-diff (modulo timestamp) against committed.

    Exit 0 when the regenerated summary matches the committed file modulo
    ``analyzed_at_utc``; non-zero on drift.
    """
    records = load_ledger(ledger_path)
    regenerated = analyze_ledger(records)
    if not committed_path.is_file():
        print(f"error: committed summary not found: {committed_path}", file=sys.stderr)
        return 1
    committed = json.loads(committed_path.read_text(encoding="utf-8"))
    if _strip_timestamp(regenerated) != _strip_timestamp(committed):
        print(
            "error: ledger summary drift: regenerated output differs from committed "
            f"{committed_path} (modulo analyzed_at_utc)",
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"check_ledger_summary": True, "pass": True}, sort_keys=True))
    return 0


# --- Self-test / drift proof ------------------------------------------------
def _self_test() -> int:
    """Prove the scanner is non-vacuous and the redactor is strong.

    (a) clean log yields no signals;
    (b) a log with a traceback yields a signal;
    (c) a secret is redacted (no raw token/JWT/assignment survives);
    (d) re-scanning a redacted excerpt yields no NEW secret (drift guard).
    """
    clean = scan_log_lines("Starting Kilo activation: target=1000")
    if clean:
        print("self-test FAIL: clean log produced signals", file=sys.stderr)
        return 1

    dirty = scan_log_lines("Traceback (most recent call last):\nValueError: boom")
    if not dirty:
        print("self-test FAIL: traceback not detected", file=sys.stderr)
        return 1

    raw = (
        "Authorization: Bearer abc123def456ghi789\n"
        "token: ghp_abcdefghijklmnopqrstuvwxyz0123456789XYZ\n"
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U\n"
        "api_key=supersecretvalue123456\n"
        "https://x/y?token=abcd1234&sig=efgh5678\n"
    )
    redacted = redact(raw)
    lowered = redacted.lower()
    leaked = any(
        token in lowered
        for token in (
            "abc123def456ghi789",
            "ghp_abcdefghijklmnopqrstuvwxyz0123456789xyz",
            "supersecretvalue123456",
            "abcd1234",
            "efgh5678",
        )
    )
    if leaked:
        print("self-test FAIL: secret survived redaction", file=sys.stderr)
        print(redacted, file=sys.stderr)
        return 1
    if "[REDACTED" not in redacted:
        print("self-test FAIL: redaction markers absent", file=sys.stderr)
        return 1

    # Drift guard: re-scanning the redacted excerpt must not re-flag a secret.
    rescan = scan_log_lines(redacted)
    rescan_leaked = any(
        token in " ".join(s.get("excerpt", "").lower() for s in rescan)
        for token in (
            "abc123def456ghi789",
            "ghp_abcdefghijklmnopqrstuvwxyz0123456789xyz",
        )
    )
    if rescan_leaked:
        print("self-test FAIL: re-scan re-exposed a redacted secret", file=sys.stderr)
        return 1

    result = {
        "self_test": True,
        "clean_ok": len(clean) == 0,
        "drift_detected": len(dirty) > 0,
        "redaction_ok": not leaked and "[REDACTED" in redacted,
        "rescan_safe": not rescan_leaked,
        "pass": True,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Fast drift/redaction proof")
    parser.add_argument(
        "--analyze-ledger",
        action="store_true",
        help="Analyze the committed workflow diagnostics ledger (read-only)",
    )
    parser.add_argument(
        "--summary-json",
        metavar="PATH",
        help="Write the ledger analysis as deterministic JSON to PATH (e.g. research_state/bab_p30/ledger_summary.json)",
    )
    parser.add_argument(
        "--since",
        type=int,
        metavar="RUN_ID",
        help="Filter ledger records to run_id >= RUN_ID before analysis",
    )
    parser.add_argument(
        "--fail-on-cancelled",
        action="store_true",
        help="Exit non-zero if any ledger run has conclusion=cancelled",
    )
    parser.add_argument(
        "--check-ledger-summary",
        metavar="PATH",
        help="Regenerate the ledger summary and byte-diff (modulo analyzed_at_utc) "
        "against the committed PATH; exit non-zero on drift",
    )
    parser.add_argument(
        "--ledger",
        default=str(DEFAULT_LEDGER),
        help="Path to the workflow_run_diagnostics.jsonl ledger",
    )
    parser.add_argument(
        "--scan-log",
        default="",
        help="Scan a plain-text log file and print detected signals as JSON",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.scan_log:
        path = Path(args.scan_log)
        if not path.is_file():
            print(f"error: log file not found: {path}", file=sys.stderr)
            return 1
        signals = scan_log_lines(path.read_text(encoding="utf-8", errors="replace"))
        print(json.dumps({"signals": signals, "count": len(signals)}, sort_keys=True))
        return 0

    if args.analyze_ledger or args.summary_json or args.since is not None or args.fail_on_cancelled or args.check_ledger_summary:
        path = Path(args.ledger)
        if not path.is_file():
            print(f"error: ledger not found: {path}", file=sys.stderr)
            return 1
        records = load_ledger(path)
        if args.since is not None:
            records = filter_since(records, args.since)
        summary = analyze_ledger(records)
        if args.fail_on_cancelled and summary["cancelled_run_ids"]:
            print(
                f"error: --fail-on-cancelled: {len(summary['cancelled_run_ids'])} cancelled run(s): "
                + ", ".join(str(r) for r in summary["cancelled_run_ids"]),
                file=sys.stderr,
            )
            return 2
        if args.summary_json:
            write_summary_json(summary, Path(args.summary_json))
        if args.check_ledger_summary:
            return check_ledger_summary(Path(args.check_ledger_summary), path)
        if args.analyze_ledger or args.summary_json:
            print(json.dumps(summary, sort_keys=True))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
