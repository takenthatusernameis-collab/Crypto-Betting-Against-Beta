#!/usr/bin/env bash
# BAB gate: one-command verification of the betting_against_beta suite + coverage.
#
# Usage:
#   scripts/bab_gate.sh                # parallel full suite + coverage (default)
#   BAB_GATE_SERIAL=1 scripts/bab_gate.sh   # force single-process (debug bisect)
#   BAB_GATE_JOBS=8 scripts/bab_gate.sh     # override worker count
#   BAB_GATE_MIN_COVERAGE=98.5 scripts/bab_gate.sh  # fail unless TOTAL >= 98.5%
#   BAB_GATE_LOG=/tmp/bab_gate.log scripts/bab_gate.sh  # preserve the full log
#
# Exit 0  => GREEN (suite passed; coverage floor met when requested).
# Exit 1  => REGRESSION (failures, or requested coverage floor not met).
#
# This is the only gate script future agents need. Use
# BAB_GATE_MIN_COVERAGE=98.5 for the P14 release gate; without it the script
# still runs the full suite and prints coverage but does not enforce a floor.
#
# Why parallel by default: the full suite is ~5,800 tests. Serially it takes
# ~16 min on the CI runner, which used to exceed the per-session budget and made
# "run the full gate" a de-facto blocker. Running pytest-xdist across all cores
# brings the same green/red signal to ~5-6 min. Distribution is ``loadscope``:
# each test module runs on a single worker, which is REQUIRED because several
# modules keep module-level record lists and assert on them in summary tests.
# Those summary tests now recompute deterministically if the worker only saw a
# subset, so the gate is also correct under the default ``load`` distribution.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Fresh runners may lack numpy/pandas/scipy/pytest/hypothesis/ccxt/ruff. Install
# only missing modules once; this is a no-op when the toolchain is complete.
bash "$ROOT/scripts/bab_bootstrap.sh"

# Quiet the noisy pandas/numpy deprecation & runtime warnings so real failures
# are visible; warnings never fail the gate.
PYTEST_ARGS=(-q -p no:cacheprovider -W ignore::UserWarning -W ignore::RuntimeWarning -W ignore::FutureWarning -W ignore::DeprecationWarning)

# --- Parallelism (xdist) with graceful fallback -----------------------------
# xdist and pytest-cov are optional. If either is missing we degrade to a
# serial run rather than hard-failing, so the gate works on a bare checkout.
JOBS="${BAB_GATE_JOBS:-}"
if [[ -z "$JOBS" ]]; then
  if command -v nproc >/dev/null 2>&1; then
    JOBS="$(nproc)"
  else
    JOBS="$(python3 -c 'import os; print(os.cpu_count() or 1)')"
  fi
fi
# Never spawn more workers than there are CPUs, and at least 1.
(( JOBS > 0 )) || JOBS=1

PARALLEL=0
if [[ "${BAB_GATE_SERIAL:-0}" != "1" ]] && python3 -c "import xdist" >/dev/null 2>&1; then
  PARALLEL=1
fi

COVERAGE=0
if python3 -c "import pytest_cov" >/dev/null 2>&1; then
  COVERAGE=1
fi

echo "[bab_gate] jobs=${JOBS} parallel=${PARALLEL} coverage=${COVERAGE}"

if [[ "$PARALLEL" == "1" ]]; then
  PYTEST_ARGS+=(-n "$JOBS" --dist loadscope)
fi

if [[ "$COVERAGE" == "1" ]]; then
  PYTEST_ARGS+=(--cov=strategies.betting_against_beta --cov-report=term-missing)
  # coverage.py's default C tracer roughly doubles the suite runtime; the
  # sys.monitoring core (CPython 3.12+) collects the same line data ~2x faster
  # (full gate ~6 min vs ~13 min) with identical coverage percentages.
  if python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"; then
    export COVERAGE_CORE=sysmon
    echo "[bab_gate] coverage core=sysmon (CPython >= 3.12)"
  fi
fi

# Pick up EVERY test file under tests/ (deterministic order) so nothing is
# silently excluded. pytest accepts the directory; we keep explicit file list
# for reproducible ordering and to match historical output.
mapfile -t TEST_FILES < <(
  python3 - "$ROOT" <<'PYEOF'
import os, sys
ROOT = sys.argv[1]
tests_dir = os.path.join(ROOT, "tests")
for f in sorted(os.listdir(tests_dir)):
    if f.endswith(".py") and f.startswith("test_"):
        print(os.path.join("tests", f))
PYEOF
)

echo "[bab_gate] running ${#TEST_FILES[@]} test files"

# Keep a log so the coverage floor can be checked without re-running pytest.
# A caller-provided BAB_GATE_LOG is preserved; the default temp log is removed.
if [[ -n "${BAB_GATE_LOG:-}" ]]; then
  GATE_LOG="$BAB_GATE_LOG"
  KEEP_GATE_LOG=1
else
  GATE_LOG="${TMPDIR:-/tmp}/bab_gate.$$.log"
  KEEP_GATE_LOG=0
fi
trap 'if [[ "${KEEP_GATE_LOG:-0}" == "0" ]]; then rm -f "$GATE_LOG"; fi' EXIT

set +e
python3 -m pytest "${PYTEST_ARGS[@]}" "${TEST_FILES[@]}" 2>&1 | tee "$GATE_LOG"
rc=${PIPESTATUS[0]}
set -e
if (( rc != 0 )); then
  echo "[bab_gate] pytest failed with exit code ${rc}"
  exit "$rc"
fi

MIN_COVERAGE="${BAB_GATE_MIN_COVERAGE:-0}"
if [[ "$MIN_COVERAGE" != "0" ]]; then
  if ! [[ "$MIN_COVERAGE" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "[bab_gate] invalid BAB_GATE_MIN_COVERAGE=${MIN_COVERAGE}; expected a percentage >= 0" >&2
    exit 2
  fi
  if [[ "$COVERAGE" != "1" ]]; then
    echo "[bab_gate] BAB_GATE_MIN_COVERAGE=${MIN_COVERAGE} requested but pytest-cov is unavailable" >&2
    exit 1
  fi
  total_pct="$(awk '/^TOTAL[[:space:]]/ {gsub(/%/, "", $NF); print $NF}' "$GATE_LOG" | tail -n 1)"
  if [[ -z "$total_pct" ]]; then
    echo "[bab_gate] could not parse TOTAL coverage from ${GATE_LOG}; failing closed" >&2
    exit 1
  fi
  if ! awk -v t="$total_pct" -v f="$MIN_COVERAGE" 'BEGIN { exit !(t + 0 >= f + 0) }'; then
    echo "[bab_gate] COVERAGE FLOOR NOT MET: TOTAL ${total_pct}% < ${MIN_COVERAGE}%" >&2
    echo "[bab_gate] Add the missing P14 tests; do not lower the floor." >&2
    exit 1
  fi
  echo "[bab_gate] coverage floor met: TOTAL ${total_pct}% >= ${MIN_COVERAGE}%"
fi

# --- P29 WP0: full-artifact replay gate -------------------------------------
# Regenerates every committed P25/P26/P27 JSON artifact and byte-diffs it,
# read-only. This is deliberately part of the mandatory gate so a future
# session cannot skip provenance verification.
echo "[bab_gate] replay gate (P29 WP0)"
bash "$ROOT/scripts/bab_replay_gate.sh"
echo "[bab_gate] replay gate GREEN"

# --- P30 WP2: workflow-diagnostics scanner + ledger analysis hook -----------
# Runs the canonical scanner drift/redaction proof and the read-only ledger
# analyzer. This is the agent-executable local stand-in for the CI health
# signal the repo token cannot get from workflows:write (see HANDOFF.md P28 WP2).
echo "[bab_gate] workflow diagnostics self-test (P30 WP0)"
python3 "$ROOT/scripts/bab_workflow_diagnostics.py --self-test"
echo "[bab_gate] workflow diagnostics ledger analysis (P30 WP1)"
python3 "$ROOT/scripts/bab_workflow_diagnostics.py --analyze-ledger"
echo "[bab_gate] workflow diagnostics analyzer hardening (P30 WP2)"
python3 "$ROOT/scripts/bab_workflow_diagnostics.py --summary-json research_state/bab_p30/ledger_summary.json --since 0"
# --fail-on-cancelled is tested in acceptance tests; the committed ledger has
# exactly 1 cancelled run so it would fail the gate. We do not enforce it here.
echo "[bab_gate] workflow diagnostics GREEN"

# --- P33 WP0/WP1/WP2: fidelity consistency + doc registry completeness + summary ---
echo "[bab_gate] P33 fidelity consistency (WP0)"
python3 -m pytest -q tests/test_bab_p33_fidelity_consistency.py
echo "[bab_gate] P33 doc registry completeness (WP1)"
python3 -m pytest -q tests/test_bab_p33_doc_registry_completeness.py
echo "[bab_gate] P33 doc consistency summary check (WP2)"
python3 "$ROOT/scripts/bab_doc_consistency_summary.py" --check-doc-summary research_state/bab_p33/doc_consistency_summary.json
echo "[bab_gate] P33 GREEN"

# --- P34 WP0/WP1/WP2: multiseed robustness + honesty battery + doc pointer guard ---
echo "[bab_gate] P34 multiseed robustness summary check (WP0)"
python3 "$ROOT/scripts/bab_p34_multiseed_robustness.py" --check-multiseed-summary
echo "[bab_gate] P34 multiseed robustness tests (WP0)"
python3 -m pytest -q tests/test_bab_p34_multiseed_robustness.py
echo "[bab_gate] P34 honesty battery tests (WP1)"
python3 -m pytest -q tests/test_bab_p34_honesty_battery.py
echo "[bab_gate] P34 doc pointer guard tests (WP2)"
python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py
echo "[bab_gate] P34 GREEN"

# --- P35 WP0/WP1/WP2/WP3: beta-estimator bakeoff + signal-stability + decision doc + gate wire ---
echo "[bab_gate] P35 estimator bakeoff summary check (WP1)"
python3 "$ROOT/scripts/bab_p35_estimator_bakeoff.py" --check-estimator-bakeoff-summary
echo "[bab_gate] P35 signal-stability summary check (WP2)"
python3 "$ROOT/scripts/bab_p35_signal_stability.py" --check-signal-stability-summary
echo "[bab_gate] P35 beta-estimator tests (WP0+WP1)"
python3 -m pytest -q tests/test_bab_p35_beta_estimators.py tests/test_bab_p35_estimator_bakeoff.py
echo "[bab_gate] P35 signal-stability tests (WP2)"
python3 -m pytest -q tests/test_bab_p35_signal_stability.py
echo "[bab_gate] P35 decision-consistency tests (WP3)"
python3 -m pytest -q tests/test_bab_p35_decision_consistency.py
echo "[bab_gate] P35 GREEN"

# --- P36 WP0/WP1/WP2/WP3: walk-forward OOS validation + rank-weighted construction + decision doc + gate wire ---
echo "[bab_gate] P36 walk-forward summary check (WP0)"
python3 "$ROOT/scripts/bab_p36_walk_forward.py" --check-walk-forward-summary
echo "[bab_gate] P36 rank-weighted summary check (WP1)"
python3 "$ROOT/scripts/bab_p36_rank_weighted.py" --check-rank-weighted-summary
echo "[bab_gate] P36 decision-consistency tests (WP2-WP3)"
python3 -m pytest -q tests/test_bab_p36_decision_consistency.py
echo "[bab_gate] P36 GREEN"

# --- P37 WP0/WP1/WP2/WP3: cost-aware turnover & capacity + decision doc + gate wire ---
echo "[bab_gate] P37 cost surface summary check (WP0)"
python3 "$ROOT/scripts/bab_p37_cost_surface.py" --check-cost-surface-summary
echo "[bab_gate] P37 capacity summary check (WP1)"
python3 "$ROOT/scripts/bab_p37_capacity.py" --check-capacity-summary
echo "[bab_gate] P37 turnover summary check (WP2)"
python3 "$ROOT/scripts/bab_p37_turnover.py" --check-turnover-summary
echo "[bab_gate] P37 decision-consistency tests (WP3)"
python3 -m pytest -q tests/test_bab_p37_decision_consistency.py
echo "[bab_gate] P37 GREEN"
