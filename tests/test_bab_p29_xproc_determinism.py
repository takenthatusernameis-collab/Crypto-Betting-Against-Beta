"""Acceptance tests for P29 WP1: cross-process determinism + provenance ledger.

Contract (from HANDOFF.md P29 WP1):

* scripts/bab_replay_full.py --xproc rebuilds every committed P25/P26/P27 JSON
  artifact in a FRESH Python interpreter, twice, and asserts byte-identical JSON
  across processes and against the committed file. This is strictly stronger than
  WP0's in-process double-build and guards against PYTHONHASHSEED/global-state/
  wall-clock leakage.
* research_state/bab_p29/provenance_audit.json is emitted with one record per
  artifact: path, sha256, generator_module, seed, fixture_sha256, replay_ok.
  Deterministic (sorted keys, stable ordering) so it can be replay-checked later.
* Both are wired into scripts/bab_replay_gate.sh.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPLAY = REPO_ROOT / "scripts" / "bab_replay_full.py"
RESEARCH = REPO_ROOT / "research_state"
PROVENANCE = RESEARCH / "bab_p29" / "provenance_audit.json"

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

FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"


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


def _live_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for sub in ("bab_p25", "bab_p26", "bab_p27"):
        for path in sorted((RESEARCH / sub).iterdir()):
            if path.is_file() and path.suffix == ".json":
                hashes[str(path.relative_to(REPO_ROOT))] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
    return hashes


def _last_json_line(r: subprocess.CompletedProcess) -> dict:
    lines = [line for line in r.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_xproc_exits_zero_all_artifacts_ok():
    r = _run("--xproc")
    assert r.returncode == 0, f"xproc must exit 0: {r.stdout} {r.stderr}"
    payload = _last_json_line(r)
    assert payload["xproc"] is True
    assert payload["pass"] is True
    for name in EXPECTED_NAMES:
        assert f"XPROC OK {name}" in r.stdout, f"missing XPROC OK for {name}: {r.stdout}"


def test_provenance_ledger_exists():
    assert PROVENANCE.is_file(), f"missing {PROVENANCE}"


def test_provenance_ledger_covers_all_artifacts():
    audit = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert audit["schema"] == "bab_p29.provenance_audit/1"
    records = audit["artifacts"]
    assert len(records) == len(EXPECTED_NAMES), f"ledger has {len(records)} records"
    paths = {r["path"] for r in records}
    expected_paths = {
        "research_state/bab_p25/walk_forward_rank.json",
        "research_state/bab_p25/promotion_bakeoff.json",
        "research_state/bab_p26/signal_null_battery.json",
        "research_state/bab_p26/regime_stress.json",
        "research_state/bab_p26/rank_capacity.json",
        "research_state/bab_p27/execution_hardening.json",
        "research_state/bab_p27/risk_controls.json",
        "research_state/bab_p27/reconciliation_e2e.json",
    }
    assert paths == expected_paths, f"ledger paths mismatch: {paths ^ expected_paths}"
    for record in records:
        assert record["replay_ok"] is True, f"not replay_ok: {record}"
        assert record["generator_module"]
        assert record["seed"] is not None
        assert record["fixture_sha256"] == FIXTURE_SHA256


def test_provenance_ledger_hashes_match_live_files():
    audit = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    live = _live_hashes()
    for record in audit["artifacts"]:
        rel = record["path"]
        assert rel in live, f"ledger path not on disk: {rel}"
        assert record["sha256"] == live[rel], f"sha256 mismatch for {rel}"


def test_provenance_ledger_deterministic():
    first = PROVENANCE.read_bytes()
    audit = json.loads(first)
    # Re-serializing with sorted keys must reproduce identical bytes.
    reserialized = (json.dumps(audit, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    assert first == reserialized, "ledger is not deterministic (sorted keys)"


def test_no_ruff_errors_on_new_files():
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(REPLAY), str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
