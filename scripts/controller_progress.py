#!/usr/bin/env python3
"""Controller progress accounting utility.

Determines whether changes between two Git commits represent meaningful
repository progress, excluding workflow definition files and marker-only
commits. Used by the Kilo agent loop controller to decide whether a
checkpoint should be credited as verified progress.

Usage:
    python3 scripts/controller_progress.py --base-sha <sha> --head-sha <sha>
    [--verified-remote-sha <sha>]
Exit code 0: meaningful progress detected (and remote SHA matches when provided)
Exit code 1: no meaningful progress, or remote SHA mismatch
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

# Pathspec patterns that are always excluded from meaningful progress.
# Both top-level and nested variants are listed so that vendored environments
# buried deeper in the tree (e.g. "subdir/.venv/x.py") are excluded too.
EXCLUDE_PATTERNS = [
    ".github/workflows/*",
    "*/.github/workflows/*",
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

    return any(fnmatch.fnmatch(path, pattern) for pattern in EXCLUDE_PATTERNS)


def list_meaningful_changes(base_sha: str, head_sha: str) -> list[str]:
    """Return the list of meaningful (non-excluded) changed file paths."""
    changed = _git_diff_names(base_sha, head_sha)
    out = []
    for path in changed:
        if not path or not path.strip():
            continue
        if _is_excluded(path.strip()):
            continue
        out.append(path.strip())
    return out


def has_meaningful_changes(base_sha: str, head_sha: str) -> bool:
    """Return True if there are meaningful (non-excluded) changes between commits."""
    return bool(list_meaningful_changes(base_sha, head_sha))


def verify_remote_sha(head_sha: str, verified_remote_sha: str) -> bool:
    """Return True if the verified remote SHA matches the local head SHA."""
    return head_sha == verified_remote_sha




def _run_git(cwd, *args):
    import subprocess
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def _self_test() -> int:
    import os
    import tempfile
    tmp = tempfile.mkdtemp()
    try:
        _run_git(tmp, "init", "-q")
        _run_git(tmp, "config", "user.email", "t@t.com")
        _run_git(tmp, "config", "user.name", "t")
        # commit 0: base
        os.makedirs(os.path.join(tmp, "src"), exist_ok=True)
        with open(os.path.join(tmp, "src", "x.py"), "w") as f:
            f.write("x = 1\n")
        _run_git(tmp, "add", "src/x.py")
        _run_git(tmp, "commit", "-q", "-m", "base")
        base = _run_git(tmp, "rev-parse", "HEAD").stdout.strip()
        # commit 1: meaningful .py change
        with open(os.path.join(tmp, "src", "x.py"), "w") as f:
            f.write("x = 2\n")
        _run_git(tmp, "add", "src/x.py")
        _run_git(tmp, "commit", "-q", "-m", "meaningful")
        head1 = _run_git(tmp, "rev-parse", "HEAD").stdout.strip()
        # commit 2: workflow-only change
        os.makedirs(os.path.join(tmp, ".github", "workflows"), exist_ok=True)
        with open(os.path.join(tmp, ".github", "workflows", "ci.yml"), "w") as f:
            f.write("name: ci\n")
        _run_git(tmp, "add", ".github/workflows/ci.yml")
        _run_git(tmp, "commit", "-q", "-m", "workflow")
        head2 = _run_git(tmp, "rev-parse", "HEAD").stdout.strip()

        # monkeypatch _git_diff_names to use temp repo by chdir? Instead call with cwd via env?
        # We'll invoke git in temp repo by temporarily changing working dir.
        orig_cwd = os.getcwd()
        os.chdir(tmp)
        try:
            meaningful_case = list_meaningful_changes(base, head1)
            workflow_case = list_meaningful_changes(head1, head2)
        finally:
            os.chdir(orig_cwd)

        ok = bool(meaningful_case) and not bool(workflow_case)
        print(json.dumps({"meaningful_case": meaningful_case,
              "workflow_case": workflow_case, "pass": ok}))
        return 0 if ok else 1
    except Exception as e:
        print(json.dumps({"error": str(e), "pass": False}))
        return 1

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Determine whether Git changes represent meaningful controller progress."
    )
    parser.add_argument("--base-sha", required=False, default="", help="Base commit SHA")
    parser.add_argument("--head-sha", required=False, default="", help="Head commit SHA")
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
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthesized meaningful-vs-workflow-only commit checks in a temp repo",
    )
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

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
