#!/usr/bin/env python3
"""Split the complete test suite by module file and run each file to green.

Removes the full-suite-timeout sandbox excuse: instead of one giant run, every
test_*.py under tests/ is executed in its own process and its pass/skip/fail
count is recorded. A file is GREEN only when rc==0 and failures==0.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--ignore", action="append", default=[])
    ap.add_argument("--filter", dest="filter", default=None,
                    help="only run files whose basename contains this substring")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    root = Path(args.root)
    files = sorted(root.glob("tests/test_*.py"))
    if args.filter:
        files = [f for f in files if args.filter in f.name]

    green = red = 0
    red_files = []
    for f in files:
        cmd = [sys.executable, "-m", "pytest", "-q", str(f)]
        for ig in args.ignore:
            cmd += ["--ignore", str(root / ig)]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            red += 1
            red_files.append((f.name, "TIMEOUT"))
            print(f"RED   {f.name}  TIMEOUT")
            continue
        out = (r.stdout or "") + (r.stderr or "")
        # parse the pytest summary line: "N passed, M skipped, K deselected"
        summary = ""
        for line in out.splitlines():
            if "passed" in line and ("deselected" in line or "skipped" in line):
                summary = line.strip()
                break
        if r.returncode == 0:
            green += 1
            print(f"GREEN {f.name}  {summary}")
        else:
            red += 1
            red_files.append((f.name, f"rc={r.returncode}"))
            print(f"RED   {f.name}  {summary}  rc={r.returncode}")

    print("\n==== SUMMARY ====")
    print(f"files: {len(files)}  green: {green}  red: {red}")
    if red_files:
        print("RED FILES:")
        for name, why in red_files:
            print(f"  - {name}: {why}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
