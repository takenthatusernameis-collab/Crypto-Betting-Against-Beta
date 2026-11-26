"""Acceptance tests for P33 WP1: document-layer completeness guard.

Contract (from HANDOFF.md P33 WP1):

* Enumerate every ``docs/*.md`` and classify each as exactly one of:
  (a) replay-gated (decision/kickoff present in
      ``scripts/bab_replay_decisions.py`` REGISTRY),
  (b) consistency-guarded (BAB_RESEARCH_REPORT.md ->
      tests/test_bab_p20_report_consistency.py;
      BAB_SIGNAL_OR_NOISE.md -> tests/test_bab_p21_report_consistency.py;
      BAB_FIDELITY.md -> tests/test_bab_p33_fidelity_consistency.py),
  (c) explicitly allow-listed with a written reason
      (e.g. COVERAGE_NOTES.md, and hand-authored BAB_P22_DECISION.md /
      BAB_P23_DECISION.md).
* A newly added ``docs/*.md`` that escapes all three classes fails this test --
  mirroring the P31 registry-completeness guard and the P32 decision-doc
  completeness guard. This makes "a new narrative doc ships with no guard"
  structurally impossible.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPLAY = REPO_ROOT / "scripts" / "bab_replay_decisions.py"
DOCS = REPO_ROOT / "docs"

# --- (a) replay-gated docs: committed in scripts/bab_replay_decisions.py REGISTRY ---
# Loaded dynamically so the guard stays in sync with the registry.

# --- (b) consistency-guarded docs: each maps to its guard test file ---
CONSISTENCY_GUARDED: dict[str, str] = {
    "docs/BAB_RESEARCH_REPORT.md": (
        "tests/test_bab_p20_report_consistency.py (P20 WP4 report consistency)"
    ),
    "docs/BAB_SIGNAL_OR_NOISE.md": (
        "tests/test_bab_p21_report_consistency.py (P21 WP3 report consistency)"
    ),
    "docs/BAB_FIDELITY.md": (
        "tests/test_bab_p33_fidelity_consistency.py (P33 WP0 fidelity consistency)"
    ),
}

# --- (c) explicitly allow-listed docs with written reasons ---
ALLOW_LIST: dict[str, str] = {
    "docs/BAB_P22_DECISION.md": (
        "hand-authored P22 decision doc; no generate_p22_decision.py generator "
        "exists, so there is no byte-replay entry point to register"
    ),
    "docs/BAB_P23_DECISION.md": (
        "hand-authored P23 decision doc; no generate_p23_decision.py generator "
        "exists, so there is no byte-replay entry point to register"
    ),
    "docs/BAB_P41_KICKOFF.md": (
        "hand-authored P41 binding campaign charter (non-Gaussian & regime-switching "
        "stress battery); it is a forward-looking kickoff/charter, not a generated "
        "decision doc, so it has no byte-replay entry point. P41 WP3 registers the "
        "generated BAB_P41_DECISION.md in the replay registry; this KICKOFF stays "
        "allow-listed with this written reason"
    ),
    "docs/BAB_P42_KICKOFF.md": (
        "hand-authored P42 binding campaign charter (planted-alpha detectability "
        "frontier & minimum detectable effect); it is a forward-looking kickoff/charter, "
        "not a generated decision doc, so it has no byte-replay entry point. P42 WP3 "
        "will register the generated BAB_P42_DECISION.md in the replay registry; this "
        "KICKOFF stays allow-listed with this written reason"
    ),
    "docs/COVERAGE_NOTES.md": (
        "hand-authored coverage notes; no deterministic generator or report "
        "consistency test exists for it; intentionally outside the replay and "
        "consistency-guarded classes"
    ),
}


def _load_registry():
    spec = importlib.util.spec_from_file_location("bab_replay_decisions", REPLAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.REGISTRY


def _replay_gated_docs() -> set[str]:
    """Docs whose committed path is covered by the replay-decisions REGISTRY."""
    registry = _load_registry()
    docs: set[str] = set()
    for entry in registry:
        if entry.get("kind") not in ("decision", "kickoff"):
            continue
        committed = entry.get("committed")
        if committed is not None:
            docs.add(str(Path(committed).relative_to(REPO_ROOT)))
        for output in entry.get("outputs", []):
            committed = output.get("committed")
            if committed is not None:
                docs.add(str(Path(committed).relative_to(REPO_ROOT)))
    return docs


def _doc_paths() -> list[str]:
    return sorted(str(p.relative_to(REPO_ROOT)) for p in DOCS.glob("*.md"))


def test_docs_dir_exists():
    assert DOCS.is_dir(), f"missing {DOCS}"


def test_every_doc_is_classified():
    replay_gated = _replay_gated_docs()
    classified = set(replay_gated) | set(CONSISTENCY_GUARDED) | set(ALLOW_LIST)
    actual = set(_doc_paths())
    unclassified = sorted(actual - classified)
    assert not unclassified, (
        "docs/*.md entries not classified as replay-gated, consistency-guarded, "
        f"or allow-listed: {unclassified}. Classify them in this test or add "
        "them to the replay registry."
    )


def test_no_doc_is_double_classified():
    replay_gated = _replay_gated_docs()
    classified = set(replay_gated) | set(CONSISTENCY_GUARDED) | set(ALLOW_LIST)
    actual = set(_doc_paths())
    overlap = sorted((set(replay_gated) & set(CONSISTENCY_GUARDED))
                     | (set(replay_gated) & set(ALLOW_LIST))
                     | (set(CONSISTENCY_GUARDED) & set(ALLOW_LIST)))
    assert not overlap, (
        f"docs classified in more than one class: {overlap}. Each docs/*.md "
        "must be in exactly one class."
    )


def test_allow_list_is_precise():
    replay_gated = _replay_gated_docs()
    consistency_guarded = set(CONSISTENCY_GUARDED)
    actual = set(_doc_paths())
    for path, reason in ALLOW_LIST.items():
        assert path in actual, f"allow-listed path does not exist: {path}"
        assert reason, f"allow-listed path {path} has no written reason"
        assert path not in replay_gated, (
            f"allow-listed path {path} is already replay-gated; remove from allow list"
        )
        assert path not in consistency_guarded, (
            f"allow-listed path {path} is already consistency-guarded; "
            "remove from allow list"
        )


def test_consistency_guarded_docs_exist():
    for path in CONSISTENCY_GUARDED:
        assert (REPO_ROOT / path).is_file(), f"consistency-guarded doc missing: {path}"
        guard_test = CONSISTENCY_GUARDED[path].split(" ")[0]
        assert (REPO_ROOT / guard_test).is_file(), (
            f"guard test missing for {path}: {guard_test}"
        )


def test_no_ruff_errors_on_new_files():
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
