#!/usr/bin/env python3
"""Read-only doc-consistency summary runner for P33 WP2.

Builds a deterministic manifest of every docs/*.md -> its guard class
(replay-gated / consistency-guarded / allow-listed) + guard status, and
byte-diffs it against a committed summary JSON via --check-doc-summary.

Mirrors scripts/bab_replay_decisions.py --summary-json / --check-doc-summary
(P32 WP2) and scripts/bab_workflow_diagnostics.py --summary-json /
--check-ledger-summary (P30 WP2).

Usage:
    python3 scripts/bab_doc_consistency_summary.py                    # print summary JSON
    python3 scripts/bab_doc_consistency_summary.py --summary-json PATH  # write summary
    python3 scripts/bab_doc_consistency_summary.py --check-doc-summary PATH  # verify

Exit 0 when the committed summary matches a fresh build; non-zero otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPLAY = REPO_ROOT / "scripts" / "bab_replay_decisions.py"
DOCS = REPO_ROOT / "docs"

SCHEMA = "bab_p33.doc_consistency_summary/1"

# Consistency-guarded docs -> guard test file.
CONSISTENCY_GUARDED: dict[str, str] = {
    "docs/BAB_RESEARCH_REPORT.md": "tests/test_bab_p20_report_consistency.py",
    "docs/BAB_SIGNAL_OR_NOISE.md": "tests/test_bab_p21_report_consistency.py",
    "docs/BAB_FIDELITY.md": "tests/test_bab_p33_fidelity_consistency.py",
}

# Allow-listed docs -> written reason.
ALLOW_LIST: dict[str, str] = {
    "docs/BAB_P22_DECISION.md": (
        "hand-authored P22 decision doc; no generate_p22_decision.py generator "
        "exists, so there is no byte-replay entry point to register"
    ),
    "docs/BAB_P23_DECISION.md": (
        "hand-authored P23 decision doc; no generate_p23_decision.py generator "
        "exists, so there is no byte-replay entry point to register"
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


def _build_summary() -> dict:
    replay_gated = _replay_gated_docs()
    entries: list[dict] = []
    for doc in sorted(p.name for p in DOCS.glob("*.md")):
        committed = f"docs/{doc}"
        if committed in replay_gated:
            guard_class = "replay-gated"
            guard_status = "registered in scripts/bab_replay_decisions.py REGISTRY"
        elif committed in CONSISTENCY_GUARDED:
            guard_class = "consistency-guarded"
            guard_status = CONSISTENCY_GUARDED[committed]
        elif committed in ALLOW_LIST:
            guard_class = "allow-listed"
            guard_status = ALLOW_LIST[committed]
        else:
            guard_class = "unclassified"
            guard_status = (
                "NOT classified — add to replay registry, consistency guard, "
                "or allow list"
            )
        entries.append({
            "committed": committed,
            "guard_class": guard_class,
            "guard_status": guard_status,
        })
    return {"schema": SCHEMA, "entries": entries}


def _dump_summary(summary: dict) -> str:
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _check_doc_summary(path: Path) -> bool:
    expected = _dump_summary(_build_summary()).encode("utf-8")
    if not path.is_file():
        print(f"MISSING doc consistency summary {path}")
        return False
    if path.read_bytes() != expected:
        print(f"DRIFT doc consistency summary: {path} differs from fresh build")
        return False
    print(f"OK doc consistency summary {path}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary-json",
        default="",
        help="Write the deterministic doc consistency summary JSON to PATH (P33 WP2)",
    )
    parser.add_argument(
        "--check-doc-summary",
        default="",
        help="Byte-diff the doc consistency summary at PATH vs a fresh build (P33 WP2)",
    )
    args = parser.parse_args(argv)

    if args.summary_json:
        out = Path(args.summary_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_dump_summary(_build_summary()), encoding="utf-8")
        print(f"WROTE doc consistency summary {out}")
        return 0

    if args.check_doc_summary:
        return 0 if _check_doc_summary(Path(args.check_doc_summary)) else 1

    # Default: print the summary JSON to stdout.
    print(_dump_summary(_build_summary()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
