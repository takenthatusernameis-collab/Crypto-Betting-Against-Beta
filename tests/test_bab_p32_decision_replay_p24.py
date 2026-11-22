"""Acceptance tests for P32 WP0: p24_decision.md read-only byte-replay.

Contract (from HANDOFF.md P32 WP0):

* scripts/bab_replay_decisions.py regenerates docs/BAB_P24_DECISION.md
  byte-identically via generate_p24_decision.py's REPORT_PATH constant,
  redirected to a temp dir; never writes to a committed path.
* The REGISTRY includes p24_decision.md (module=generate_p24_decision,
  gen_dir=ROOT, kind=decision, output REPORT_PATH -> docs/BAB_P24_DECISION.md).
* --self-test proves the comparator is not vacuous: a clean tree replays OK and
  a deliberately corrupted committed copy is detected as drift.
* --subset p24_decision.md replays just p24; unknown names fail closed.
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
DOCS = REPO_ROOT / "docs"

EXPECTED_NAMES = {
    "p24_decision.md",
}

COMMITTED_FILES = [
    DOCS / "BAB_P24_DECISION.md",
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


def test_registry_includes_p24_decision():
    registry = _load_registry()
    names = {entry["name"] for entry in registry}
    assert "p24_decision.md" in names, f"p24_decision.md missing from REGISTRY: {names}"


def test_p24_registry_entry_shape():
    registry = _load_registry()
    entry = next(e for e in registry if e["name"] == "p24_decision.md")
    assert entry["module"] == "generate_p24_decision"
    assert entry["gen_dir"] == REPO_ROOT
    assert entry["kind"] == "decision"
    assert len(entry["outputs"]) == 1
    assert entry["outputs"][0]["constant"] == "REPORT_PATH"
    assert entry["outputs"][0]["committed"] == DOCS / "BAB_P24_DECISION.md"


def test_p24_registry_entry_has_committed_file():
    for entry in _load_registry():
        if entry["name"] == "p24_decision.md":
            for output in entry["outputs"]:
                assert output["committed"].is_file(), f"missing {output['committed']}"


def test_all_committed_p24_files_exist():
    for path in COMMITTED_FILES:
        assert path.is_file(), f"missing committed artifact {path}"


def test_list_prints_p24_name():
    r = _run("--list")
    assert r.returncode == 0, r.stderr
    printed = {line.strip() for line in r.stdout.splitlines() if line.strip()}
    assert "p24_decision.md" in printed


def test_self_test_passes():
    r = _run("--self-test")
    assert r.returncode == 0, f"self-test must exit 0: {r.stdout} {r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["self_test"] is True
    assert payload["clean_ok"] is True
    assert payload["drift_detected"] is True
    assert payload["pass"] is True


def test_subset_replay_byte_identical():
    r = _run("--subset", "p24_decision.md")
    assert r.returncode == 0, f"subset replay must exit 0: {r.stdout} {r.stderr}"
    assert "OK p24_decision.md" in r.stdout


def test_unknown_subset_fails_closed():
    r = _run("--subset", "does_not_exist")
    assert r.returncode != 0
    assert "NO MATCHING ARTIFACTS" in r.stdout


def test_replay_is_read_only_on_committed_artifacts():
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in COMMITTED_FILES}
    _run("--subset", "p24_decision.md")
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in COMMITTED_FILES}
    assert before == after, "replay must not modify committed docs files"


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
