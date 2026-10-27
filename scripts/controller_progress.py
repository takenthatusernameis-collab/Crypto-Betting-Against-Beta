#!/usr/bin/env python3
"""Controller progress accounting utility.

Determines whether changes between two Git commits represent meaningful
repository progress, excluding workflow definition files and marker-only
commits. Used by the Kilo agent loop controller to decide whether a
checkpoint should be credited as verified progress.

Usage:
    python3 scripts/controller_progress.py --base-sha <sha> --head-sha <sha> [--verified-remote-sha <sha>]
Exit code 0: meaningful progress detected (and remote SHA matches when provided)
Exit code 1: no meaningful progress, or remote SHA mismatch
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Pathspec patterns that are always excluded from meaningful progress.
# Both top-level and nested variants are listed so that vendored environments
# buried deeper in the tree (e.g. "subdir/.venv/x.py") are excluded too.
EXCLUDE_PATTERNS = [
    ".github/workflows/*",
    ".venv/*",
    "*/.venv/*",
    "venv/*",
    "*/venv/*",
    "node_modules/*",
    "*/node_modules/*",
    "__pycache__/*",
    "*/__pycache__/*",
    ".pytest_cache/*",
    "*/.pytest_cache/*",
    ".mypy_cache/*",
    "*/.mypy_cache/*",
    ".ruff_cache/*",
    "*/.ruff_cache/*",
    ".tox/*",
    "*/.tox/*",
    "*.pyc",
    "*.pyo",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    # SQLite write-ahead and shared-memory files.
    "*.sqlite-wal",
    "*.sqlite-shm",
    "*.sqlite3-wal",
    "*.sqlite3-shm",
    "*.db-wal",
    "*.db-shm",
    # Transient local artifacts.
    "*.tmp",
    ".env",
    ".env.*",
    "*/.env",
    "*/.env.*",
    "coverage.xml",
    "*/coverage.xml",
    ".coverage",
    "*/.coverage",
    "kilo-session-*.log",
    "*/kilo-session-*.log",
    "kilo-progress-*.log",
    "*/kilo-progress-*.log",
]


def _git_diff_names(base_sha: str, head_sha: str) -> list[str]:
    """Return changed file paths between two commits, as a flat list."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base_sha}..{head_sha}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return []
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def _is_excluded(path: str) -> bool:
    """Check if a path should be excluded from meaningful progress."""
    import fnmatch

    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


def list_meaningful_changes(base_sha: str, head_sha: str) -> list[str]:
    """Return the list of meaningful (non-excluded) changed file paths."""
    changed = _git_diff_names(base_sha, head_sha)
    return [path for path in changed if not _is_excluded(path)]


def has_meaningful_changes(base_sha: str, head_sha: str) -> bool:
    """Return True if there are meaningful (non-excluded) changes between commits."""
    return bool(list_meaningful_changes(base_sha, head_sha))


def verify_remote_sha(head_sha: str, verified_remote_sha: str) -> bool:
    """Return True if the verified remote SHA matches the local head SHA."""
    return head_sha == verified_remote_sha


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Determine whether Git changes represent meaningful controller progress."
    )
    parser.add_argument("--base-sha", required=True, help="Base commit SHA to compare against")
    parser.add_argument("--head-sha", required=True, help="Head commit SHA to compare")
    parser.add_argument(
        "--verified-remote-sha",
        default=None,
        help="Optional remote SHA to verify against the head SHA",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON object with the meaningful file list and verification result",
    )
    args = parser.parse_args()

    # Delegate the progress decision to has_meaningful_changes so callers can
    # stub the predicate; the file list is only materialized for JSON output.
    has_progress = has_meaningful_changes(args.base_sha, args.head_sha)
    remote_ok = True
    if args.verified_remote_sha is not None:
        remote_ok = verify_remote_sha(args.head_sha, args.verified_remote_sha)

    if args.json:
        meaningful = list_meaningful_changes(args.base_sha, args.head_sha)
        payload = {
            "base_sha": args.base_sha,
            "head_sha": args.head_sha,
            "meaningful_changes": meaningful,
            "has_meaningful_changes": has_progress,
            "verified_remote_sha": args.verified_remote_sha,
            "remote_sha_verified": remote_ok,
            "exit_code": 0 if (has_progress and remote_ok) else 1,
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return payload["exit_code"]

    if not has_progress:
        return 1

    if args.verified_remote_sha is not None and not remote_ok:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())