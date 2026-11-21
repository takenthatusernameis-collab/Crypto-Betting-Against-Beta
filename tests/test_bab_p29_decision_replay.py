"""Acceptance tests for P29 WP2: decision-doc + JSONL sidecar read-only replay.

Contract (from HANDOFF.md P29 WP2):

* scripts/bab_replay_decisions.py regenerates, byte-identically, the committed
  P25/P26/P27 decision docs, the P27 decision sidecar JSON, and the two P27
  paper JSONL sidecars, redirecting generator output constants to a temp dir;
  never writes to a committed path.
* The registry covers all six artifacts (p25_decision.md, p26_decision.md,
  p27_decision + p27_decision_sidecar.json, paper_orders.jsonl,
  paper_diagnostics.jsonl).
* --self-test proves the comparator is not vacuous: a clean tree replays OK and
  a deliberately corrupted committed copy is detected as drift.
* --subset replays a named subset; unknown names fail closed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPLAY = REPO_ROOT / "scripts" / "bab_replay_decisions.py"
RESEARCH = REPO_ROOT / "research_state"
DOCS = REPO_ROOT / "docs"

EXPECTED_NAMES = {
    "p25_decision.md",
    "p26_decision.md",
    "p27_decision",
    "paper_orders.jsonl",
    "paper_diagnostics.jsonl",
}

COMMITTED_FILES = [
    DOCS / "BAB_P25_DECISION.md",
    DOCS / "BAB_P26_DECISION.md",
    DOCS / "BAB_P27_DECISION.md",
    RESEARCH / "bab_p27" / "p27_decision_sidecar.json",
    RESEARCH / "bab_p27" / "paper_orders.jsonl",
    RESEARCH / "bab_p27" / "paper_diagnostics.jsonl",
]


def _run(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + (
        f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else ""
    )
    return subprocess.run(
        [sys.executable, str(REPLAY), *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def _load_registry():
    spec = importlib.util.spec_from_file_location("bab_replay_decisions", REPLAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.REGISTRY


def test_script_exists():
    assert REPLAY.is_file(), f"missing {REPLAY}"


def test_registry_covers_all_wp2_artifacts():
    registry = _load_registry()
    names = {entry["name"] for entry in registry}
    assert names == EXPECTED_NAMES, f"registry mismatch: {names ^ EXPECTED_NAMES}"


def test_registry_entries_have_committed_files():
    for entry in _load_registry():
        if entry["kind"] == "decision":
            for output in entry["outputs"]:
                assert output["committed"].is_file(), f"missing {output['committed']}"
        else:
            assert entry["committed"].is_file(), f"missing {entry['committed']}"


def test_all_committed_wp2_files_exist():
    for path in COMMITTED_FILES:
        assert path.is_file(), f"missing committed artifact {path}"


def test_list_prints_all_names():
    r = _run("--list")
    assert r.returncode == 0, r.stderr
    printed = {line.strip() for line in r.stdout.splitlines() if line.strip()}
    assert printed == EXPECTED_NAMES


def test_self_test_passes():
    r = _run("--self-test")
    assert r.returncode == 0, f"self-test must exit 0: {r.stdout} {r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["self_test"] is True
    assert payload["clean_ok"] is True
    assert payload["drift_detected"] is True
    assert payload["pass"] is True


def test_subset_replay_byte_identical():
    r = _run("--subset", "p25_decision.md")
    assert r.returncode == 0, f"subset replay must exit 0: {r.stdout} {r.stderr}"
    assert "OK p25_decision.md" in r.stdout


def test_unknown_subset_fails_closed():
    r = _run("--subset", "does_not_exist")
    assert r.returncode != 0
    assert "NO MATCHING ARTIFACTS" in r.stdout


def test_replay_is_read_only_on_committed_artifacts():
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in COMMITTED_FILES}
    _run("--subset", "p25_decision.md,p26_decision.md")
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in COMMITTED_FILES}
    assert before == after, "replay must not modify committed research_state/docs files"


def test_no_ruff_errors_on_new_files():
    result = _run("--self-test")
    assert result.returncode == 0
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(REPLAY), str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
