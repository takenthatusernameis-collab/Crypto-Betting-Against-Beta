#!/usr/bin/env python3
"""R4 live-readiness preflight: makes the next focus campaign mechanically unavoidable.

Run this FIRST in every session that touches BAB live-readiness:

    PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py

It answers, with evidence, the question a handoff-only process lets a future
agent hand-wave: *is R4 actually shipped?*

  1. R4-A dry-run / portfolio-risk report present?  (product capability + tests)
  2. R4-B drawdown-limit kill switch present?       (product capability + tests)
  3. R4-C deterministic paper-trading replay present? (product capability + tests)
  4. If all three are present: do the R4 tests pass, and does the R2/R3
     regression baseline still pass (no regression from the R4 work)?

Exit code:
  0  R4-A/B/C present AND their tests pass AND R2/R3 baseline green.
  1  One or more R4 capabilities missing (prints an itemized TODO) OR a suite fails.
  2  Measurement/execution error.

It never writes product code, never weakens anything, and never commits.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "strategies", "betting_against_beta")
TESTS = os.path.join(ROOT, "tests")

# R2/R3 regression baseline that must stay green while R4 lands.
BASELINE_FILES = [
    "tests/test_bab_stress_regimes.py",
    "tests/test_bab_stress_horizon.py",
    "tests/test_bab_scale_perf_guard.py",
    "tests/test_bab_execution_realism_r3.py",
]

# Each capability: (label, product symbol regexes, expected test filename).
CAPABILITIES = [
    (
        "R4-A dry-run / portfolio-risk report",
        [r"def\s+dry_run\s*\(", r"def\s+(portfolio_risk|risk_report|risk_summary)\s*\("],
        "tests/test_bab_dryrun_risk_report_r4.py",
    ),
    (
        "R4-B drawdown-limit kill switch",
        [r"max_drawdown_limit", r"kill_switch"],
        "tests/test_bab_drawdown_kill_switch_r4.py",
    ),
    (
        "R4-C deterministic paper-trading replay harness",
        [r"class\s+ReplayHarness", r"def\s+replay\b", r"replay_harness"],
        "tests/test_bab_replay_harness_r4.py",
    ),
]


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _product_text() -> str:
    chunks = []
    if os.path.isdir(PKG):
        chunks.extend(
            _read(os.path.join(PKG, name))
            for name in sorted(os.listdir(PKG))
            if name.endswith(".py")
        )
    return "\n".join(chunks)


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)


def check_capabilities() -> tuple[list[str], list[str], list[str]]:
    """Return (missing, present_products, present_tests)."""
    product = _product_text()
    missing: list[str] = []
    present_products: list[str] = []
    present_tests: list[str] = []
    for label, symbols, expected_test in CAPABILITIES:
        prod_ok = any(re.search(sym, product) for sym in symbols)
        test_ok = os.path.exists(os.path.join(ROOT, expected_test))
        if prod_ok:
            present_products.append(label)
        if test_ok:
            present_tests.append(label)
        if not prod_ok or not test_ok:
            bits = []
            if not prod_ok:
                bits.append(f"product capability (no symbol matching any of {symbols})")
            if not test_ok:
                bits.append(f"missing test file {expected_test}")
            missing.append(f"  - {label}: {'; '.join(bits)}")
    return missing, present_products, present_tests


def main() -> int:
    print("=" * 72)
    print("BAB R4 PREFLIGHT — run FIRST, before any live-readiness work")
    print("=" * 72)

    missing, present_products, present_tests = check_capabilities()
    if present_products:
        print("[r4] product capabilities detected:")
        for label in present_products:
            print(f"    + {label}")
    if present_tests:
        print("[r4] R4 test files detected:")
        for label in present_tests:
            print(f"    + {label}")

    if missing:
        print("\n[r4] R4 NOT SHIPPED. Remaining work (itemized):")
        for line in missing:
            print(line)
        print("\n[r4] Implement all three R4 capabilities + tests, then re-run this")
        print("     preflight. Do not report R4 complete while any item remains.")
        return 1

    # All capabilities present -> run R4 tests, then R2/R3 baseline.
    r4_tests = [c[2] for c in CAPABILITIES]
    print("\n[r4] Running R4 test suites ...")
    r = _run(
        [sys.executable, "-m", "pytest", *r4_tests, "-q", "-p", "no:cacheprovider"], timeout=3600
    )
    print((r.stdout or "")[-2500:])
    if r.returncode != 0:
        print(f"[r4] R4 TESTS FAIL (rc={r.returncode}) -> fix before anything else.")
        return 1

    existing_baseline = [f for f in BASELINE_FILES if os.path.exists(os.path.join(ROOT, f))]
    print(f"\n[r4] Running R2/R3 baseline: {existing_baseline}")
    r = _run(
        [sys.executable, "-m", "pytest", *existing_baseline, "-q", "-p", "no:cacheprovider"],
        timeout=3600,
    )
    print((r.stdout or "")[-2500:])
    if r.returncode != 0:
        print(f"[r4] R2/R3 BASELINE REGRESSED (rc={r.returncode}) -> fix before anything else.")
        return 1

    print("\n" + "=" * 72)
    print("R4 PREFLIGHT RESULT: R4-A/B/C present + green; R2/R3 baseline green.")
    print('Next: run full gate (PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh),')
    print("then refresh HANDOFF.md with evidence. Commit nothing unless requested.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
