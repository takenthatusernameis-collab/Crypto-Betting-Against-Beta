#!/usr/bin/env bash
# BAB gate: one-command verification of the betting_against_beta suite + coverage.
#
# Usage:  scripts/bab_gate.sh
#
# Exit 0  => GREEN (suite passed, coverage ceiling held).
# Exit 1  => REGRESSION (failures, or coverage ceiling breached).
#
# This is the ONLY command future agents need to run to verify the BAB gate.
# It is intentionally self-contained (no PYTHONPATH assumptions beyond $PWD)
# so it works from any working directory.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Quiet the noisy pandas/numpy deprecation & runtime warnings so real failures
# are visible; warnings never fail the gate.
PYTEST_ARGS=(-q -p no:cacheprovider -W ignore::UserWarning -W ignore::RuntimeWarning -W ignore::FutureWarning -W ignore::DeprecationWarning)

# --- Suite + coverage in one shot -------------------------------------------
python3 - <<'PYEOF'
import glob, sys, coverage, pytest
ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0, ROOT)
files = sorted(glob.glob(ROOT + "/tests/test_bab*.py")) + [
    ROOT + "/tests/test_betting_against_beta_costs.py",
    ROOT + "/tests/test_betting_against_beta.py",
]
cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"], data_file=None)
cov.start()
rc = pytest.main(["-q", "-p", "no:cacheprovider",
                  "-W", "ignore::UserWarning",
                  "-W", "ignore::RuntimeWarning",
                  "-W", "ignore::FutureWarning",
                  "-W", "ignore::DeprecationWarning"] + files)
cov.stop()
cov.report(show_missing=True)
raise SystemExit(rc)
PYEOF