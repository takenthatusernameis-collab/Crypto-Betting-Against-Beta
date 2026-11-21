"""Acceptance tests for P29 WP0: full-artifact read-only replay coverage.

Contract (from HANDOFF.md P28/P29):

* scripts/bab_replay_full.py regenerates every committed P25/P26/P27 JSON
  artifact from its generator's pure build_*(fixture_path) into memory and
  byte-diffs it against the committed file, read-only on research_state/**.
* The registry covers all eight generated artifacts (P25 x2, P26 x3, P27 x3);
  JSONL sidecars and the P27 decision sidecar are intentionally out of scope
  (covered by P29 WP2).
* --self-test proves the comparator is not vacuous: a clean tree replays OK and
  a deliberately corrupted copy is detected as drift.
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
REPLAY = REPO_ROOT / "scripts" / "bab_replay_full.py"
RESEARCH = REPO_ROOT / "research_state"

EXPECTED_NAMES = {
    "walk_forward_rank",
    "promotion_bakeoff",
    "signal_null_battery",
    "regime_stress",
    "rank_capacity",
    "execution_hardening",
    "risk_controls",
    "reconciliation_e2e",
}


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
    spec = importlib.util.spec_from_file_location("bab_replay_full", REPLAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.REGISTRY


def _artifact_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for sub in ("bab_p25", "bab_p26", "bab_p27"):
        for path in sorted((RESEARCH / sub).iterdir()):
            if path.is_file():
                hashes[str(path.relative_to(REPO_ROOT))] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
    return hashes


def test_script_exists():
    assert REPLAY.is_file(), f"missing {REPLAY}"


def test_registry_covers_all_generated_artifacts():
    registry = _load_registry()
    names = {entry["name"] for entry in registry}
    assert names == EXPECTED_NAMES, f"registry mismatch: {names ^ EXPECTED_NAMES}"


def test_registry_entries_have_committed_files():
    for entry in _load_registry():
        cdir = RESEARCH / entry["dir"]
        assert (cdir / f"{entry['name']}.json").is_file(), entry["name"]
        assert (cdir / f"{entry['name']}.md").is_file(), entry["name"]


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
    r = _run("--subset", "risk_controls,reconciliation_e2e")
    assert r.returncode == 0, f"subset replay must exit 0: {r.stdout} {r.stderr}"
    assert "OK risk_controls.json" in r.stdout
    assert "OK reconciliation_e2e.json" in r.stdout


def test_unknown_subset_fails_closed():
    r = _run("--subset", "does_not_exist")
    assert r.returncode != 0
    assert "NO MATCHING ARTIFACTS" in r.stdout


def test_replay_is_read_only_on_committed_artifacts():
    before = _artifact_hashes()
    _run("--subset", "risk_controls,reconciliation_e2e")
    after = _artifact_hashes()
    assert before == after, "replay must not modify committed research_state files"


def test_no_ruff_errors_on_new_files():
    result = _run(
        "--self-test",
    )  # smoke: script imports and runs
    assert result.returncode == 0
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(REPLAY), str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
