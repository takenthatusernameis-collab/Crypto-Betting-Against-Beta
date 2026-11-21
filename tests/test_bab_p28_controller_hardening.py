"""Acceptance tests for P28 WP0: controller infrastructure hardening.

These tests assert the controller progress utility, the deterministic replay
harness, and the fixture-provenance preflight checks behave safely and
deterministically. P28 consumes P20-P27 artifacts read-only; no P20-P27 file is
edited here.

Contract (from HANDOFF.md P28 WP0):

* scripts/controller_progress.py — --json payload exit-code contract
  (exit 0 on meaningful changes + remote match, exit 1 otherwise), --self-test
  mode that synthesizes meaningful-vs-workflow-only commits in a temp repo and
  exits 0/1 without touching real git history, guards against empty/whitespace
  paths and non-ACMR diffs; EXCLUDE_PATTERNS semantics unchanged.
* scripts/bab_replay_harness.py — regenerates committed P27 WP0-WP2 JSON
  artifacts (execution_hardening.json, risk_controls.json, reconciliation_e2e.json)
  from each generator's pure build_*(fixture_path) into a temp dir and byte-diffs;
  fails non-zero on drift; read-only on committed P27 files.
* Preflight checks: fixture SHA256 equals a6d390fc…163b; synthetic-vs-real
  labelling present in P27 artifacts; nonfinite serialization guardrails
  (no NaN/Inf leaks into JSON).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTROLLER_SCRIPT = REPO_ROOT / "scripts" / "controller_progress.py"
REPLAY_HARNESS = REPO_ROOT / "scripts" / "bab_replay_harness.py"
ARTIFACT_DIR = REPO_ROOT / "research_state" / "bab_p27"
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
P25_WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"

REPLAY_GENS = [
    ("bab_execution_hardening", "build_execution_hardening", "execution_hardening.json"),
    ("bab_risk_controls", "build_risk_controls", "risk_controls.json"),
    ("bab_reconciliation_e2e", "build_reconciliation_e2e", "reconciliation_e2e.json"),
]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _strict_loads(text: str):
    """Parse JSON strictly, rejecting literal NaN/Infinity value tokens."""

    def _reject_constant(x: str):
        raise ValueError(f"non-strict JSON constant: {x}")

    return json.loads(text, parse_constant=_reject_constant)


def _run(cmd, **kwargs):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + (
        f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else ""
    )
    return subprocess.run(
        cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True, **kwargs
    )


# --------------------------------------------------------------------------- #
# Controller progress: --json exit-code contract
# --------------------------------------------------------------------------- #
def test_controller_script_exists():
    assert CONTROLLER_SCRIPT.is_file(), f"missing {CONTROLLER_SCRIPT}"


def test_controller_has_json_and_self_test_entry_points():
    mod = _load("controller_progress", CONTROLLER_SCRIPT)
    assert callable(getattr(mod, "main", None))
    assert callable(getattr(mod, "list_meaningful_changes", None))
    assert callable(getattr(mod, "_self_test", None))


def test_controller_json_exit_code_on_meaningful_changes():
    r = _run(
        [
            sys.executable,
            str(CONTROLLER_SCRIPT),
            "--base-sha",
            "15d0712",
            "--head-sha",
            "d7b5a62",
            "--json",
        ]
    )
    assert r.returncode == 0, f"expected exit 0 on meaningful changes: {r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["exit_code"] == 0
    assert payload["has_meaningful_changes"] is True
    assert payload["head_sha"] == "d7b5a62"
    assert payload["base_sha"] == "15d0712"
    assert isinstance(payload["meaningful_changes"], list)


def test_controller_json_exit_code_on_no_meaningful_changes():
    r = _run(
        [
            sys.executable,
            str(CONTROLLER_SCRIPT),
            "--base-sha",
            "d7b5a62",
            "--head-sha",
            "d7b5a62",
            "--json",
        ]
    )
    assert r.returncode == 1, f"expected exit 1 on no meaningful changes: {r.stdout}"
    payload = json.loads(r.stdout)
    assert payload["exit_code"] == 1
    assert payload["has_meaningful_changes"] is False
    assert payload["meaningful_changes"] == []


def test_controller_json_payload_is_strict_json():
    r = _run(
        [
            sys.executable,
            str(CONTROLLER_SCRIPT),
            "--base-sha",
            "15d0712",
            "--head-sha",
            "d7b5a62",
            "--json",
        ]
    )
    raw = r.stdout.encode("utf-8")
    _strict_loads(raw.decode("utf-8"))  # must parse; rejects NaN/Infinity tokens


def test_controller_self_test_exits_zero():
    r = _run([sys.executable, str(CONTROLLER_SCRIPT), "--self-test"])
    assert r.returncode == 0, f"self-test must exit 0: {r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["pass"] is True
    assert payload["meaningful_case"]  # real .py change flagged meaningful
    assert not payload["workflow_case"]  # workflow-only change not meaningful


# --------------------------------------------------------------------------- #
# Controller progress: list_meaningful_changes guards
# --------------------------------------------------------------------------- #
def test_list_meaningful_changes_excludes_workflows():
    mod = _load("controller_progress", CONTROLLER_SCRIPT)
    changes = mod.list_meaningful_changes("15d0712", "d7b5a62")
    assert all(
        not path.startswith(".github/workflows/") for path in changes
    ), "workflow files must remain excluded"


def test_exclude_patterns_unchanged():
    mod = _load("controller_progress", CONTROLLER_SCRIPT)
    assert ".github/workflows/*" in mod.EXCLUDE_PATTERNS
    assert "*/.github/workflows/*" in mod.EXCLUDE_PATTERNS


# --------------------------------------------------------------------------- #
# Replay harness: deterministic byte-diff vs committed P27 artifacts
# --------------------------------------------------------------------------- #
def test_replay_harness_script_exists():
    assert REPLAY_HARNESS.is_file(), f"missing {REPLAY_HARNESS}"


def test_replay_harness_byte_identical_all_artifacts():
    r = _run([sys.executable, str(REPLAY_HARNESS)])
    assert r.returncode == 0, f"replay harness must exit 0: {r.stderr}"
    for modname, _build, fname in REPLAY_GENS:
        assert f"OK {fname}" in r.stdout, f"{fname} must replay byte-identical"


def test_replay_harness_read_only_on_committed_files():
    before = {
        fname: (ARTIFACT_DIR / fname).read_bytes()
        for _m, _b, fname in REPLAY_GENS
        if (ARTIFACT_DIR / fname).is_file()
    }
    _run([sys.executable, str(REPLAY_HARNESS)])
    after = {
        fname: (ARTIFACT_DIR / fname).read_bytes()
        for _m, _b, fname in REPLAY_GENS
        if (ARTIFACT_DIR / fname).is_file()
    }
    assert before == after, "replay harness must not modify committed P27 artifacts"


# --------------------------------------------------------------------------- #
# Preflight: fixture provenance
# --------------------------------------------------------------------------- #
def test_fixture_sha256_matches_p25_wp0_provenance():
    actual = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    assert actual == P25_WP0_FIXTURE_SHA256


def test_p27_artifacts_synthetic_vs_real_labelled():
    for _m, _b, fname in REPLAY_GENS:
        path = ARTIFACT_DIR / fname
        assert path.is_file(), f"missing committed artifact {fname}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload.get("synthetic") is True, f"{fname} must be labelled synthetic"
        prov = payload.get("provenance", {})
        prov_text = json.dumps(prov, sort_keys=True)
        assert (
            "not real market" in prov_text or "synthetic" in prov_text
        ), f"{fname} provenance must label synthetic-vs-real"


# --------------------------------------------------------------------------- #
# Preflight: nonfinite serialization guardrails
# --------------------------------------------------------------------------- #
def test_p27_artifacts_no_nan_inf_leak():
    for _m, _b, fname in REPLAY_GENS:
        path = ARTIFACT_DIR / fname
        _strict_loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Ruff on new P28 files
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    result = _run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            str(CONTROLLER_SCRIPT),
            str(REPLAY_HARNESS),
            str(__file__),
        ]
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
