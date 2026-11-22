"""Acceptance tests for P31 WP2: provenance-ledger regeneration-diff.

Contract (from HANDOFF.md P31 WP2):

* scripts/bab_replay_full.py --check-provenance regenerates the provenance
  audit from a fresh cross-process build into a temp path and byte-diffs it
  against the committed research_state/bab_p29/provenance_audit.json (modulo
  nothing — it must be fully deterministic).
* Never writes to a committed path.
* Wired into scripts/bab_replay_gate.sh.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPLAY = REPO_ROOT / "scripts" / "bab_replay_full.py"
PROVENANCE = REPO_ROOT / "research_state" / "bab_p29" / "provenance_audit.json"


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


def test_script_exists():
    assert REPLAY.is_file(), f"missing {REPLAY}"


def test_committed_provenance_exists():
    assert PROVENANCE.is_file(), f"missing committed {PROVENANCE}"


def test_check_provenance_exits_zero_and_is_read_only():
    before = PROVENANCE.read_bytes()
    r = _run("--check-provenance")
    after = PROVENANCE.read_bytes()
    assert r.returncode == 0, f"--check-provenance must exit 0: {r.stdout} {r.stderr}"
    assert before == after, "--check-provenance must not modify the committed audit"
    payload = json.loads(r.stdout)
    assert payload["check_provenance"] is True
    assert payload["pass"] is True


def test_no_ruff_errors_on_new_files():
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(REPLAY), str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
