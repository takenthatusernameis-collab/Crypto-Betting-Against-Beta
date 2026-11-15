#!/usr/bin/env bash
# BAB quick preflight: fast inner-loop feedback for agents.
#
# Usage:  scripts/bab_quick.sh [extra pytest args...]
#
# Runs, in order, the checks that catch ~95% of real regressions in seconds:
#   1. ruff (lint)                        ~1s
#   2. targeted trio (live/risk/feed/...)  ~2s
#   3. fast smoke: strategy + cli + costs  ~5s
#
# This is the loop to run while iterating. Run scripts/bab_gate.sh (full,
# parallel, with coverage) before claiming done.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Fresh runners may lack numpy/pandas/scipy/pytest/hypothesis/ccxt/ruff. Install
# only missing modules once; this is a no-op when the toolchain is complete.
bash "$ROOT/scripts/bab_bootstrap.sh"

QARGS=(-q -p no:cacheprovider -W ignore::UserWarning -W ignore::RuntimeWarning -W ignore::FutureWarning -W ignore::DeprecationWarning)

echo "== ruff =="
python3 -m ruff check .

echo "== targeted trio =="
python3 -m pytest "${QARGS[@]}" \
  tests/test_bab_live_adapter.py \
  tests/test_bab_risk_manager.py \
  tests/test_bab_realtime_feed.py \
  tests/test_bab_paper_trading.py \
  tests/test_bab_data_freshness.py \
  tests/test_bab_diagnostics.py

echo "== smoke (strategy/cli/costs) =="
python3 -m pytest "${QARGS[@]}" \
  tests/test_betting_against_beta.py \
  tests/test_bab_cli.py \
  tests/test_betting_against_beta_costs.py \
  tests/test_bab_stress_regimes.py \
  "$@"

echo "== quick preflight OK =="
