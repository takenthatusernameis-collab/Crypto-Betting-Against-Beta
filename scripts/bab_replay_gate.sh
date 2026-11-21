#!/usr/bin/env bash
# BAB full-artifact replay gate (P29 WP0).
#
# Proves every committed P25/P26/P27 JSON artifact is byte-reproducible from its
# generator, read-only, and that the comparator catches injected drift.
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

echo "== replay gate OK =="