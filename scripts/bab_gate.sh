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
# ROOT is computed at the top of this script (relative to $0), so the gate
# works from any working directory and on any machine, not just this sandbox.
python3 - "$ROOT" <<'PYEOF'
import os, sys
ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

# coverage is an optional dependency; if it is missing we still run the suite
# (just without the coverage report) so the gate never hard-fails on a missing
# package.  Install it with:  pip install coverage
try:
    import coverage
    have_coverage = True
except ImportError:
    have_coverage = False

import pytest

# Pick up EVERY test file under tests/.  The previous glob of test_bab*.py
# silently excluded ~15 files / 412 tests, hiding real regressions from the
# gate (5 failures were invisible to it).  Order is deterministic so output is
# reproducible across runs.
tests_dir = os.path.join(ROOT, "tests")
files = sorted(
    os.path.join(tests_dir, f)
    for f in os.listdir(tests_dir)
    if f.endswith(".py") and f.startswith("test_")
)

common_args = ["-q", "-p", "no:cacheprovider",
               "-W", "ignore::UserWarning",
               "-W", "ignore::RuntimeWarning",
               "-W", "ignore::FutureWarning",
               "-W", "ignore::DeprecationWarning"]

if have_coverage:
    cov = coverage.Coverage(source=[os.path.join(ROOT, "strategies", "betting_against_beta")],
                            data_file=None)
    cov.start()
    rc = pytest.main(common_args + files)
    cov.stop()
    cov.report(show_missing=True)
else:
    print("coverage not installed - running suite without coverage report", file=sys.stderr)
    rc = pytest.main(common_args + files)
raise SystemExit(rc)
PYEOF