#!/usr/bin/env bash
# BAB toolchain bootstrap.
#
# Fresh CI runners do not always have the project's Python dependencies
# preinstalled. Repeated sessions have been blocked by ModuleNotFoundError for
# numpy/pandas/scipy/pytest/hypothesis/ccxt and by a missing ruff. This script
# detects missing imports once and installs only what is absent, then re-checks.
#
# It is a no-op when the toolchain is complete, so it is safe to call from
# scripts/bab_quick.sh and scripts/bab_gate.sh on every run.
#
# Escape hatches:
#   BAB_SKIP_ENV_BOOTSTRAP=1  # skip the check/install entirely
#   CI=true                   # allow --break-system-packages on PEP-668 hosts
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${BAB_SKIP_ENV_BOOTSTRAP:-0}" == "1" ]]; then
  echo "[bab_bootstrap] skipped (BAB_SKIP_ENV_BOOTSTRAP=1)"
  exit 0
fi

missing_modules() {
  python3 - <<'PY'
import importlib.util

modules = [
    "numpy",
    "pandas",
    "scipy",
    "pytest",
    "pytest_cov",
    "xdist",
    "hypothesis",
    "coverage",
    "ccxt",
    "ruff",
]
missing = [name for name in modules if importlib.util.find_spec(name) is None]
print(" ".join(missing))
PY
}

missing="$(missing_modules)"
if [[ -z "${missing//[[:space:]]/}" ]]; then
  exit 0
fi

echo "[bab_bootstrap] missing Python modules: ${missing}"
echo "[bab_bootstrap] installing project test/runtime dependencies (requirements.txt + ruff)"

PIP_ARGS=(--disable-pip-version-check --no-input --quiet -r requirements.txt ruff)
if ! python3 -m pip install "${PIP_ARGS[@]}"; then
  if [[ "${CI:-}" == "true" ]]; then
    echo "[bab_bootstrap] first pip attempt failed; retrying with --break-system-packages (CI)"
    python3 -m pip install "${PIP_ARGS[@]}" --break-system-packages
  else
    echo "[bab_bootstrap] dependency installation failed; install manually with:" >&2
    echo "  python3 -m pip install -r requirements.txt ruff" >&2
    exit 1
  fi
fi

missing_after="$(missing_modules)"
if [[ -n "${missing_after//[[:space:]]/}" ]]; then
  echo "[bab_bootstrap] toolchain still incomplete after install: ${missing_after}" >&2
  exit 1
fi

echo "[bab_bootstrap] toolchain ready"
