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
    ".env",
    ".env.*",
    "coverage.xml",
    ".coverage",
    "kilo-session-*.log",
    "kilo-progress-*.log",
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


def has_meaningful_changes(base_sha: str, head_sha: str) -> bool:
    """Return True if there are meaningful (non-excluded) changes between commits."""
    changed = _git_diff_names(base_sha, head_sha)
    for path in changed:
        if not _is_excluded(path):
            return True
    return False


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
    args = parser.parse_args()

    if not has_meaningful_changes(args.base_sha, args.head_sha):
        return 1

    if args.verified_remote_sha is not None:
        if not verify_remote_sha(args.head_sha, args.verified_remote_sha):
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())