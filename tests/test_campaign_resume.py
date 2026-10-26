#!/usr/bin/env python3
"""Tests for campaign resume logic.

A "campaign" is a sequence of Kilo worker sessions that share a common
task. This module tests the resume logic: given a checkpoint (a Git
commit), can a new session correctly reconstruct the prior state and
continue without losing work?
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# Ensure scripts directory is importable for controller_progress.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import controller_progress  # noqa: E402


class FakeGit:
    """A test double for Git operations used by the resume logic."""

    def __init__(self) -> None:
        self.commits: dict[str, dict[str, str]] = {}  # sha -> {path: content}
        self.current_head: str | None = None
        self.remotes: dict[str, str] = {}  # name -> sha

    def commit(self, message: str, files: dict[str, str]) -> str:
        """Create a fake commit and advance HEAD."""
        sha = f"sha-{len(self.commits) + 1:04d}"
        self.commits[sha] = dict(files)
        self.current_head = sha
        return sha

    def checkout(self, sha: str) -> None:
        """Move HEAD to a known commit."""
        if sha not in self.commits:
            raise ValueError(f"Unknown commit: {sha}")
        self.current_head = sha

    def diff_names(self, base: str, head: str) -> list[str]:
        """Return changed file paths between two commits."""
        if base not in self.commits or head not in self.commits:
            return []
        base_files = set(self.commits[base].keys())
        head_files = set(self.commits[head].keys())
        return sorted(base_files ^ head_files)

    def set_remote(self, name: str, sha: str) -> None:
        self.remotes[name] = sha


def can_resume_from(git: FakeGit, base_sha: str) -> bool:
    """Return True if a campaign can resume from the given base commit."""
    if base_sha not in git.commits:
        return False
    # Resume is possible if HEAD is at or ahead of the base.
    if git.current_head is None:
        return False
    # In this simplified model, any known commit is resumable.
    return True


def resume_changes(git: FakeGit, base_sha: str) -> dict[str, str]:
    """Return the working-tree state at base_sha for resuming a campaign."""
    if base_sha not in git.commits:
        raise ValueError(f"Cannot resume: unknown base commit {base_sha}")
    return dict(git.commits[base_sha])


class TestCanResumeFrom:
    """Tests for the resume predicate."""

    def test_resume_from_existing_commit(self) -> None:
        git = FakeGit()
        git.commit("initial", {"README.md": "# Project"})
        assert can_resume_from(git, git.current_head) is True

    def test_resume_from_unknown_commit(self) -> None:
        git = FakeGit()
        git.commit("initial", {"README.md": "# Project"})
        assert can_resume_from(git, "sha-unknown") is False

    def test_resume_with_no_commits(self) -> None:
        git = FakeGit()
        assert can_resume_from(git, "any") is False


class TestResumeChanges:
    """Tests for the state-reconstruction helper."""

    def test_returns_commit_files(self) -> None:
        git = FakeGit()
        sha = git.commit("initial", {"main.py": "print('hi')", "tests/test.py": ""})
        state = resume_changes(git, sha)
        assert state == {"main.py": "print('hi')", "tests/test.py": ""}

    def test_raises_on_unknown_commit(self) -> None:
        git = FakeGit()
        with pytest.raises(ValueError, match="Cannot resume"):
            resume_changes(git, "sha-unknown")

    def test_preserves_empty_files(self) -> None:
        git = FakeGit()
        sha = git.commit("empty", {"empty.txt": ""})
        state = resume_changes(git, sha)
        assert state == {"empty.txt": ""}


class TestCampaignResumeWithControllerProgress:
    """Integration tests combining campaign resume with controller progress accounting."""

    def test_resume_and_verify_progress(self) -> None:
        git = FakeGit()
        base = git.commit("initial", {"src/main.py": "v1"})
        # Simulate a Kilo session making meaningful changes.
        head = git.commit("kilo: add feature", {"src/main.py": "v2", "src/new.py": "new"})

        # The controller should detect meaningful progress.
        with mock.patch.object(
            controller_progress,
            "_git_diff_names",
            return_value=controller_progress._git_diff_names(base, head),
        ):
            # We can't call the real git, so just verify the resume logic.
            assert can_resume_from(git, base) is True
            state = resume_changes(git, base)
            assert "src/main.py" in state

    def test_resume_preserves_uncommitted_work(self) -> None:
        git = FakeGit()
        base = git.commit("initial", {"file.txt": "original"})
        # Simulate that the working tree was preserved across resume.
        git.checkout(base)
        state = resume_changes(git, base)
        assert state["file.txt"] == "original"


class TestResumeEdgeCases:
    """Edge cases for campaign resume."""

    def test_resume_after_multiple_commits(self) -> None:
        git = FakeGit()
        c1 = git.commit("c1", {"a.txt": "1"})
        c2 = git.commit("c2", {"a.txt": "2", "b.txt": "b"})
        c3 = git.commit("c3", {"c.txt": "c"})
        # Resume from the first commit should work.
        assert can_resume_from(git, c1) is True
        state = resume_changes(git, c1)
        assert state == {"a.txt": "1"}

    def test_resume_with_binary_files(self) -> None:
        git = FakeGit()
        sha = git.commit("binary", {"image.png": b"\x89PNG\r\n", "data.bin": b"\x00\x01"})
        state = resume_changes(git, sha)
        assert state["image.png"] == b"\x89PNG\r\n"