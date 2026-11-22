#!/usr/bin/env bash
# BAB full-artifact replay gate (P29 WP0 + WP1 + WP2).
#
# Proves every committed P25/P26/P27 JSON artifact (WP0), every committed artifact
# is byte-reproducible across processes (WP1), and every committed P25/P26/P27
# decision doc, the P27 decision sidecar JSON, and the two P27 paper JSONL
# sidecars are byte-reproducible from their generators (WP2), read-only, and that
# the comparator catches injected drift.
#
# Usage:  bash scripts/bab_replay_gate.sh
# Exit 0 => GREEN; non-zero => DRIFT or self-test failure.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

echo "== replay self-test (drift detection) =="
python3 scripts/bab_replay_full.py --self-test

echo "== full artifact replay (P25/P26/P27) =="
python3 scripts/bab_replay_full.py

echo "== cross-process determinism + provenance ledger (P29 WP1) =="
python3 scripts/bab_replay_full.py --xproc

echo "== provenance-ledger regeneration-diff vs committed (P31 WP2) =="
python3 scripts/bab_replay_full.py --check-provenance

echo "== decision-doc + JSONL sidecar replay (P29 WP2) =="
python3 scripts/bab_replay_decisions.py --self-test
python3 scripts/bab_replay_decisions.py

echo "== P30 ledger summary reproducibility replay =="
python3 scripts/bab_workflow_diagnostics.py --check-ledger-summary research_state/bab_p30/ledger_summary.json

echo "== replay gate OK =="