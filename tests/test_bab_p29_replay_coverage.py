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

# The full-artifact registry (scripts/bab_replay_full.py REGISTRY) grew from the
# 8 P25/P26/P27 artifacts covered at P29 WP0 to all 27 committed P20-P27 JSON
# artifacts after P31 WP0 added the 19 P20-P24 entries, then to 31 (dir, name)
# entries after P35 WP1/WP2 and P36 WP0/WP1 registered their four JSON-only
# summary artifacts (estimator_bakeoff_summary, signal_stability_summary,
# walk_forward_summary, rank_weighted_summary; json_only=True, no_xproc=True),
# then to 38 (dir, name) entries after P37/P38/P39 registered their seven
# JSON-only summary artifacts (cost_surface_summary, capacity_summary,
# turnover_summary, deflated_summary, tail_risk_summary, regime_summary,
# cross_fixture_summary; json_only=True, no_xproc=True). The registry is the
# single source of truth for "every committed JSON research artifact is
# replayed", so this exact set is the complete set of registry artifact names.
# ("charter" appears once each under bab_p22/bab_p23/bab_p24; --list prints the
# bare name, so the set of distinct names has 36 elements across the 38
# (dir, name) entries.) The assertion below stays an EXACT equality -- it is not
# loosened -- so a 37th artifact added to the registry still fails closed here,
# while tests/test_bab_p31_registry_completeness.py independently guards the
# "no committed JSON escapes replay" direction.
# NOTE (bottleneck removal 2026-11-22T19:41:19Z): this set was last extended at
# P31 and never updated for the P35/P36 json-only registrations, so the guard
# was RED on an otherwise-green tree (3 failures in this file) and blocked every
# session's full gate. Adding the four legitimately-registered json-only names
# restores the EXACT-equality contract without weakening it. This is guard
# maintenance, not test loosening.
# NOTE (bottleneck removal 2026-11-24T11:24:33Z): the same rot recurred for the
# P37/P38/P39 json-only summary registrations (cost_surface_summary,
# capacity_summary, turnover_summary, deflated_summary, tail_risk_summary,
# regime_summary, cross_fixture_summary), leaving this guard RED again on an
# otherwise-green tree and contributing to the full-gate failure set that
# blocked P39 WP0. Adding the seven legitimately-registered json-only names
# restores the EXACT-equality contract without weakening it. Guard maintenance,
# not test loosening.
EXPECTED_NAMES = {
    # P25 / P26 / P27 (P29 WP0 scope)
    "walk_forward_rank",
    "promotion_bakeoff",
    "signal_null_battery",
    "regime_stress",
    "rank_capacity",
    "execution_hardening",
    "risk_controls",
    "reconciliation_e2e",
    # P20 (P31 WP0)
    "sweep",
    "breakeven",
    "walk_forward",
    # P21 (P31 WP0)
    "universe",
    "cost_surface",
    "rank_eval",
    "significance",
    # P22 (P31 WP0)
    "null_battery",
    "impact_surface",
    "capacity",
    # P23 (P31 WP0)
    "beta_drift",
    "breadth_ladder",
    "short_haircut",
    # P24 (P31 WP0)
    "adapter_dryrun",
    "hysteresis",
    "regime_split",
    # shared name across bab_p22 / bab_p23 / bab_p24
    "charter",
    # P35 WP1/WP2 + P36 WP0/WP1 JSON-only summary artifacts (json_only=True,
    # no_xproc=True in bab_replay_full.py REGISTRY; no .md sidecar by design).
    "estimator_bakeoff_summary",
    "signal_stability_summary",
    "walk_forward_summary",
    "rank_weighted_summary",
    # P37 (WP0/WP1/WP2) + P38 (WP1/WP2) + P39 (WP1/WP2) JSON-only summary
    # artifacts (json_only=True, no_xproc=True in bab_replay_full.py REGISTRY;
    # no .md sidecar by design). Registered legitimately; added here to restore
    # the EXACT-equality contract (see the 2026-11-24 bottleneck-removal note).
    "cost_surface_summary",
    "capacity_summary",
    "turnover_summary",
    "deflated_summary",
    "tail_risk_summary",
    "regime_summary",
    "cross_fixture_summary",
    # P40 WP0 multi-fixture meta-analysis summary artifact (json_only=True,
    # no_xproc=True in bab_replay_full.py REGISTRY; no .md sidecar replayed
    # here -- the .md is rendered by build_summary() and pinned by
    # tests/test_bab_p40_meta_analysis.py).
    "meta_summary",
    # P41 WP2 stress summary artifact (json_only=True, no_xproc=True in
    # bab_replay_full.py REGISTRY; no .md sidecar replayed here -- the .md
    # is rendered by render_stress_markdown() and pinned by
    # tests/test_bab_p41_decision_consistency.py).
    "stress_summary",
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
        # JSON-only artifacts (P35/P36 summary JSONs) have no rendered .md
        # sidecar by design; the committed JSON is the authoritative artifact.
        if entry.get("json_only"):
            continue
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
