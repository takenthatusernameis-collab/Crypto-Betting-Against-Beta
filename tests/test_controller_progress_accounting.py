#!/usr/bin/env python3
"""Tests for scripts/controller_progress.py — controller progress accounting."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# Ensure the scripts directory is importable.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import controller_progress  # noqa: E402


class TestIsExcluded:
    """Tests for the path exclusion logic."""

    @pytest.mark.parametrize(
        "path,expected",
        [
            (".github/workflows/main.yml", True),
            ("src/main.py", False),
            (".venv/lib/python.py", True),
            ("venv/something.py", True),
            ("node_modules/foo/index.js", True),
            ("__pycache__/cache.pyc", True),
            (".pytest_cache/v/cache.txt", True),
            (".mypy_cache/info.json", True),
            (".ruff_cache/lock.txt", True),
            ("src/app.py", False),
            ("README.md", False),
            (".env", True),
            (".env.local", True),
            ("coverage.xml", True),
            (".coverage", True),
            ("kilo-session-123.log", True),
            ("kilo-progress-456.log", True),
            ("*.pyc", True),
            ("*.pyo", True),
            ("*.sqlite", True),
            ("*.sqlite3", True),
            ("*.db", True),
            ("*.sqlite-wal", True),
            ("*.sqlite-shm", True),
            ("*.sqlite3-wal", True),
            ("*.sqlite3-shm", True),
            ("*.db-wal", True),
            ("*.db-shm", True),
            ("*.tmp", True),
            # Nested variants must also be excluded.
            ("subdir/.venv/lib/python.py", True),
            ("subdir/venv/bin/python", True),
            ("subdir/node_modules/foo/index.js", True),
            ("subdir/__pycache__/cache.pyc", True),
            ("subdir/.pytest_cache/v/cache.txt", True),
            ("subdir/.mypy_cache/info.json", True),
            ("subdir/.ruff_cache/lock.txt", True),
            ("subdir/.tox/py312/bin/python", True),
            # Nested workflow files must be excluded too; fnmatch does not cross
            # directory separators, so the nested-variant pattern is required.
            ("subdir/.github/workflows/main.yml", True),
            ("subdir/.github/workflows/nested/file.yml", True),
            ("a/b/c/.github/workflows/ci.yml", True),
            # Nested variants for env, coverage, and SQLite WAL/SHM files.
            ("subdir/.env", True),
            ("subdir/.env.local", True),
            ("subdir/coverage.xml", True),
            ("subdir/.coverage", True),
            ("subdir/kilo-session-123.log", True),
            ("subdir/kilo-progress-456.log", True),
            ("main.db-wal", True),
            ("main.sqlite3-shm", True),
            ("subdir/data.db-wal", True),
            ("subdir/cache.db-shm", True),
            ("subdir/x.tmp", True),
        ],
    )
    def test_exclusion(self, path: str, expected: bool) -> None:
        assert controller_progress._is_excluded(path) is expected


class TestGitDiffNames:
    """Tests for the git diff wrapper."""

    def test_returns_list_of_changed_files(self) -> None:
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "file1.py\nfile2.py\n\n"
        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            files = controller_progress._git_diff_names("abc123", "def456")
            assert files == ["file1.py", "file2.py"]
            mock_run.assert_called_once()

    def test_returns_empty_on_error(self) -> None:
        mock_result = mock.Mock()
        mock_result.returncode = 128
        mock_result.stdout = ""
        with mock.patch("subprocess.run", return_value=mock_result):
            assert controller_progress._git_diff_names("bad", "worse") == []

    def test_returns_empty_on_timeout(self) -> None:
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=30)):
            assert controller_progress._git_diff_names("a", "b") == []


class TestHasMeaningfulChanges:
    """Tests for the meaningful-changes predicate."""

    def test_no_changes_means_no_progress(self) -> None:
        with mock.patch.object(controller_progress, "_git_diff_names", return_value=[]):
            assert controller_progress.has_meaningful_changes("a", "b") is False

    def test_only_excluded_changes_means_no_progress(self) -> None:
        with mock.patch.object(
            controller_progress,
            "_git_diff_names",
            return_value=[".github/workflows/main.yml", ".venv/x.py"],
        ):
            assert controller_progress.has_meaningful_changes("a", "b") is False

    def test_mixed_changes_means_progress(self) -> None:
        with mock.patch.object(
            controller_progress,
            "_git_diff_names",
            return_value=["src/main.py", ".github/workflows/main.yml"],
        ):
            assert controller_progress.has_meaningful_changes("a", "b") is True

    def test_only_meaningful_changes_means_progress(self) -> None:
        with mock.patch.object(
            controller_progress,
            "_git_diff_names",
            return_value=["src/app.py", "tests/test_foo.py"],
        ):
            assert controller_progress.has_meaningful_changes("a", "b") is True


class TestVerifyRemoteSha:
    """Tests for the remote SHA verification helper."""

    def test_matching_shas(self) -> None:
        assert controller_progress.verify_remote_sha("abc", "abc") is True

    def test_mismatching_shas(self) -> None:
        assert controller_progress.verify_remote_sha("abc", "def") is False


class TestMain:
    """Tests for the CLI entry point."""

    def test_no_meaningful_changes_exits_1(self) -> None:
        sys.argv = ["controller_progress.py", "--base-sha", "a", "--head-sha", "b"]
        with mock.patch.object(controller_progress, "has_meaningful_changes", return_value=False):
            assert controller_progress.main() == 1

    def test_meaningful_changes_without_remote_sha_exits_0(self) -> None:
        sys.argv = ["controller_progress.py", "--base-sha", "a", "--head-sha", "b"]
        with mock.patch.object(controller_progress, "has_meaningful_changes", return_value=True):
            assert controller_progress.main() == 0

    def test_meaningful_changes_with_matching_remote_sha_exits_0(self) -> None:
        sys.argv = [
            "controller_progress.py",
            "--base-sha", "a",
            "--head-sha", "b",
            "--verified-remote-sha", "b",
        ]
        with mock.patch.object(controller_progress, "has_meaningful_changes", return_value=True):
            assert controller_progress.main() == 0

    def test_meaningful_changes_with_mismatching_remote_sha_exits_1(self) -> None:
        sys.argv = [
            "controller_progress.py",
            "--base-sha", "a",
            "--head-sha", "b",
            "--verified-remote-sha", "c",
        ]
        with mock.patch.object(controller_progress, "has_meaningful_changes", return_value=True):
            assert controller_progress.main() == 1


class TestStageSafeChangesPatternSync:
    """Regression tests ensuring the workflow's bash stage_safe_changes exclusion
    list stays in lock-step with the Python EXCLUDE_PATTERNS list.

    The two lists live in different files (`.github/workflows/main.yml` and
    `scripts/controller_progress.py`) and are maintained by hand. Drift means
    a path that the controller refuses to credit as progress gets staged into a
    checkpoint commit (or vice versa), silently corrupting progress accounting.
    """

    WORKFLOW_PATH = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "main.yml"

    @classmethod
    def _workflow_patterns(cls) -> set[str]:
        text = cls.WORKFLOW_PATH.read_text(encoding="utf-8")
        start = text.index('case "$changed_path" in')
        header = text[start : text.index(")", start)]
        body = header.split('case "$changed_path" in', 1)[1].strip()
        return {token.strip() for token in body.split("|") if token.strip()}

    def test_python_patterns_are_subset_of_workflow(self) -> None:
        workflow = self._workflow_patterns()
        missing = set(controller_progress.EXCLUDE_PATTERNS) - workflow
        assert not missing, (
            "Python EXCLUDE_PATTERNS has patterns missing from the workflow's "
            f"stage_safe_changes list: {sorted(missing)}"
        )

    def test_workflow_patterns_are_subset_of_python(self) -> None:
        python = set(controller_progress.EXCLUDE_PATTERNS)
        extra = self._workflow_patterns() - python
        assert not extra, (
            "The workflow's stage_safe_changes list has patterns missing from "
            f"Python EXCLUDE_PATTERNS: {sorted(extra)}"
        )

    def test_nested_workflow_pattern_is_present_in_workflow(self) -> None:
        # Regression for commit 7dac063: the nested-variant pattern was added to
        # Python but not to the bash list, so a vendored workflow file under a
        # subdirectory was staged as meaningful progress.
        assert "*/.github/workflows/*" in self._workflow_patterns()

    def test_nested_kilo_progress_log_pattern_is_present_in_workflow(self) -> None:
        assert "*/kilo-progress-*.log" in self._workflow_patterns()
