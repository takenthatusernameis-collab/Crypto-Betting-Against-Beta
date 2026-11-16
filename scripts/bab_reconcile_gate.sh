#!/usr/bin/env bash
# scripts/bab_reconcile_gate.sh
#
# Deterministic CI reconciliation/live-safety enforcement gate (P18-3).
# Proves the reconciliation drift gate is fail-closed: intentional drift must
# exit non-zero (rc=2), while a clean/no-drift case exits zero. Uses only
# synthetic data and temp files — no network, no credentials, reproducible.
#
# Usage:
#   scripts/bab_reconcile_gate.sh          # run the full gate
#   BAB_RECONCILE_LOG=/tmp/reconcile.log   # preserve the full log
#
# Exit 0 => GREEN (drift fails closed, clean passes).
# Exit 1 => REGRESSION (enforcement is missing or bypassed).
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

bash "$ROOT/scripts/bab_bootstrap.sh" >/dev/null 2>&1 || true

if [[ -n "${BAB_RECONCILE_LOG:-}" ]]; then
  GATE_LOG="$BAB_RECONCILE_LOG"
  KEEP_GATE_LOG=1
else
  GATE_LOG="${TMPDIR:-/tmp}/bab_reconcile_gate.$$.log"
  KEEP_GATE_LOG=0
fi
trap 'if [[ "${KEEP_GATE_LOG:-0}" == "0" ]]; then rm -f "$GATE_LOG"; fi' EXIT

fail=0
note() { echo "[bab_reconcile_gate] $*"; }

run_case() {
  local name="$1" expected_rc="$2"
  shift 2
  local out rc
  out="$(mktemp)"
  set +e
  python3 -m strategies.betting_against_beta.cli "$@" --output "$out" >"$GATE_LOG.case" 2>&1
  rc=$?
  set -e
  if [[ "$rc" -eq "$expected_rc" ]]; then
    note "PASS $name: rc=$rc (expected $expected_rc)"
  else
    note "FAIL $name: rc=$rc (expected $expected_rc)"
    cat "$GATE_LOG.case" >&2 || true
    rm -f "$out" "$GATE_LOG.case"
    fail=1
    return 1
  fi
  rm -f "$out" "$GATE_LOG.case"
}

# --- Case 1: intentional drift must fail closed (rc=2) ---------------------
# Paper adapter emits fills with cost; --transaction-costs 0.01 vs a zero
# modeled cost produces a delta_max_abs above tolerance 0.0 -> enforcement
# trips and exits non-zero.
run_case "drift-fail-closed (tolerance=0.0, transaction-costs=0.01)" 2 \
  --synthetic --adapter paper --reconcile \
  --transaction-costs 0.01 --reconcile-tolerance 0.0

# --- Case 2: tolerance above drift must pass (rc=0) ------------------------
run_case "clean-passes (tolerance=0.5, transaction-costs=0.01)" 0 \
  --synthetic --adapter paper --reconcile \
  --transaction-costs 0.01 --reconcile-tolerance 0.5

# --- Case 3: --reconcile alone stays emit-only / backward compatible (rc=0) --
run_case "reconcile-emit-only (no tolerance)" 0 \
  --synthetic --adapter paper --reconcile

if [[ "$fail" -ne 0 ]]; then
  note "GATE RED: reconciliation enforcement is missing or bypassed."
  exit 1
fi
note "GATE GREEN: drift fails closed (rc=2); clean and emit-only pass (rc=0)."
exit 0
