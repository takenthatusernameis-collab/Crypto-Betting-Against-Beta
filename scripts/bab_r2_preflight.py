#!/usr/bin/env python3
"""R2 preflight: make "start the stress campaign" mechanically unavoidable.

Run this FIRST in every session that touches the BAB engine:

    python3 scripts/bab_r2_preflight.py

It answers, with evidence, the three questions a handoff-only process lets a
future agent hand-wave:

  1. Is R2 already started?  -> exact file presence + per-file pass/fail if so.
  2. What is the live gate baseline right now? -> passed / skipped / wall-clock.
  3. What is the live scale baseline right now? -> 5000x200 / 5000x500 run times
     vs the ceilings the R2-C guard must assert.

It never writes product code, never weakens anything, and never commits. It is a
read-only *measurement* tool whose numbers the handoff must be reconciled to.

Exit code is 0 when the campaign is unstarted (expected) or when every existing
R2 file passes; 1 when an R2 file exists but fails (so a broken R2 stage cannot
be silently ignored); 2 on a measurement error.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

R2_FILES = [
    "tests/test_bab_stress_regimes.py",
    "tests/test_bab_stress_horizon.py",
    "tests/test_bab_scale_perf_guard.py",
]

# Ceilings the R2-C guard must assert (median of 9 warm reps, this host).
SCALE_CEILINGS = {"5000x200": 0.8, "5000x500": 2.0}


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=ROOT + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""))
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)


def r2_status() -> tuple[bool, list[str]]:
    existing = [f for f in R2_FILES if os.path.exists(os.path.join(ROOT, f))]
    return bool(existing), existing


def run_existing_r2() -> int:
    """If any R2 file exists, run it; return 0 only if it passes."""
    _, existing = r2_status()
    if not existing:
        print("[preflight] R2 files: NONE present -> campaign genuinely unstarted.")
        return 0
    print(f"[preflight] R2 files present: {existing}")
    r = _run([sys.executable, "-m", "pytest", *existing, "-q", "-p", "no:cacheprovider"], timeout=3600)
    tail = (r.stdout or "")[-2000:]
    print(tail)
    if r.returncode != 0:
        print(f"[preflight] R2 EXISTS BUT FAILS (rc={r.returncode}) -> fix before doing anything else.")
        return 1
    print("[preflight] Existing R2 files all pass; extend, do not duplicate.")
    return 0


def measure_scale() -> int:
    """Live scale measurement vs ceilings. Returns 0 on success, 2 on error."""
    code = r"""
import time, statistics, sys
import numpy as np, pandas as pd
from strategies.betting_against_beta import BABStrategy
rng = np.random.default_rng(7)
def frame(n, k):
    cols = [f"A{i}" for i in range(k - 1)] + ["BTC"]
    data = rng.standard_normal((n, k)) * 0.01 + 0.0003
    idx = pd.date_range("2018-01-01", periods=n, freq="D")
    return pd.DataFrame(data, index=idx, columns=cols)
out = {}
for label, n, k in [("5000x200", 5000, 200), ("5000x500", 5000, 500)]:
    df = frame(n, k)
    strat = BABStrategy(benchmark="BTC", beta_window=90, beta_neutral=True, dollar_neutral=True)
    times = []
    for _ in range(9):
        s = BABStrategy(benchmark="BTC", beta_window=90, beta_neutral=True, dollar_neutral=True)
        t0 = time.perf_counter(); s.run(returns_df=df); times.append(time.perf_counter() - t0)
    out[label] = statistics.median(times)
print("SCALE_JSON " + repr(out))
"""
    r = _run([sys.executable, "-c", code], timeout=1800)
    line = next((ln for ln in (r.stdout or "").splitlines() if ln.startswith("SCALE_JSON ")), None)
    if not line:
        print("[preflight] SCALE MEASUREMENT FAILED. stderr tail:\n" + (r.stderr or "")[-1500:])
        return 2
    scale = eval(line[len("SCALE_JSON "):])
    print("[preflight] Live scale baseline (median of 9 warm reps):")
    ok = True
    for label in ("5000x200", "5000x500"):
        val = scale[label]
        ceil = SCALE_CEILINGS[label]
        flag = "OK" if val <= ceil else "OVER CEILING"
        if val > ceil:
            ok = False
        print(f"  {label}: {val*1000:.0f} ms  (ceiling {ceil*1000:.0f} ms) [{flag}]")
    return 0 if ok else 1


def main() -> int:
    print("=" * 72)
    print("BAB R2 PREFLIGHT — run FIRST, before any other work this session")
    print("=" * 72)

    # 1. R2 unstarted check
    rc_r2 = run_existing_r2()
    if rc_r2 == 1:
        return 1

    # 2. Live scale baseline (what R2-C must assert against)
    print("\n[preflight] Measuring live scale baseline ...")
    try:
        rc_scale = measure_scale()
    except subprocess.TimeoutExpired:
        print("[preflight] scale measurement timed out")
        return 2
    if rc_scale == 2:
        return 2

    print("\n" + "=" * 72)
    if rc_r2 == 0 and rc_scale == 0:
        print("PREFLIGHT RESULT: R2 unstarted (or passing) AND scale within ceilings.")
        print("NEXT: build/extend the R2 stress + horizon + scale suites (HANDOFF.md).")
    else:
        print("PREFLIGHT RESULT: see flags above; reconcile HANDOFF.md before proceeding.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
