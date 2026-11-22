"""Acceptance tests for P32 WP1: decision-doc registry completeness guard.

Contract (from HANDOFF.md P32 WP1):

* Every docs/BAB_P*_DECISION.md for which a generate_pXX_decision.py generator
  exists IS covered by the scripts/bab_replay_decisions.py REGISTRY (matched by
  generator module name).
* Hand-authored decision docs (P22/P23, no generator) are explicitly
  allow-listed with a written reason.
* This makes the "orphaned generated decision doc escapes replay" class
  structurally impossible to re-create: a newly added generate_pXX_decision.py
  whose output is not registered fails this test.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPLAY = REPO_ROOT / "scripts" / "bab_replay_decisions.py"
DOCS = REPO_ROOT / "docs"

# Hand-authored decision docs with no generate_pXX_decision.py generator.
# Each has a written reason why it cannot be byte-replayed by a generator and
# therefore is not (and must not be) registered. These are the only entries
# allowed to escape the REGISTRY.
ALLOW_LIST: dict[str, str] = {
    "docs/BAB_P22_DECISION.md": (
        "hand-authored P22 decision doc; no generate_p22_decision.py generator "
        "exists, so there is no byte-replay entry point to register"
    ),
    "docs/BAB_P23_DECISION.md": (
        "hand-authored P23 decision doc; no generate_p23_decision.py generator "
        "exists, so there is no byte-replay entry point to register"
    ),
}


def _load_registry():
    spec = importlib.util.spec_from_file_location("bab_replay_decisions", REPLAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.REGISTRY


def _decision_doc_paths() -> list[str]:
    return [str(p.relative_to(REPO_ROOT)) for p in sorted(DOCS.glob("BAB_P*_DECISION.md"))]


def _generator_exists(doc_name: str) -> bool:
    """True if a generate_pXX_decision.py generator exists for this doc."""
    parts = Path(doc_name).stem.split("_")
    if len(parts) != 3:
        return False
    pnum = parts[1]
    return (REPO_ROOT / f"generate_{pnum.lower()}_decision.py").is_file()


def _registry_decision_modules() -> set[str]:
    registry = _load_registry()
    return {
        entry["module"]
        for entry in registry
        if entry.get("kind") == "decision"
    }


def test_script_exists():
    assert REPLAY.is_file(), f"missing {REPLAY}"


def test_every_generated_decision_doc_is_in_registry():
    registry_modules = _registry_decision_modules()
    for doc in _decision_doc_paths():
        if _generator_exists(doc):
            pnum = Path(doc).stem.split("_")[1]
            expected_module = f"generate_{pnum.lower()}_decision"
            assert expected_module in registry_modules, (
                f"generated decision doc {doc} has a generator but '{expected_module}' "
                f"is not in the bab_replay_decisions.py REGISTRY decision modules: "
                f"{registry_modules}"
            )


def test_allow_listed_hand_authored_docs():
    registry_modules = _registry_decision_modules()
    for doc, reason in ALLOW_LIST.items():
        assert reason, f"allow-listed doc {doc} has no written reason"
        pnum = Path(doc).stem.split("_")[1]
        expected_module = f"generate_{pnum.lower()}_decision"
        assert expected_module not in registry_modules, (
            f"allow-listed doc {doc} ({expected_module}) is already in the REGISTRY; "
            "remove it from the allow list"
        )


def test_no_ruff_errors_on_new_files():
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
