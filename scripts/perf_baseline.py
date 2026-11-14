#!/usr/bin/env python3
"""Record or check a deterministic BAB performance baseline.

Baseline is recorded against a real-format price dataset (fixture by default)
using the same hot-path measurements as `scripts/perf_bench.py`.

Usage:
  # Record baseline
  python scripts/perf_baseline.py --record --dataset tests/fixtures/real_market_prices.csv \
      --output research_state/perf_baseline_real_fixture.json

  # Check against baseline (fails on regression beyond tolerance)
  python scripts/perf_baseline.py --check \
      --baseline research_state/perf_baseline_real_fixture.json \
      --dataset tests/fixtures/real_market_prices.csv
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy  # noqa: E402
from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402


def _time(fn, repeats: int) -> list[float]:
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return times


def measure(dataset: Path, repeats: int, warmup: int, benchmark: str) -> dict:
    returns = load_prices(dataset, benchmark=benchmark, min_rows=30)
    # warmup
    for _ in range(warmup):
        calculate_rolling_beta(returns, benchmark, window=90, min_obs=60)
        BABStrategy().run(returns_df=returns)
    beta_times = _time(
        lambda: calculate_rolling_beta(returns, benchmark, window=90, min_obs=60),
        repeats,
    )
    full_times = _time(lambda: BABStrategy().run(returns_df=returns), repeats)

    import tracemalloc

    tracemalloc.start()
    BABStrategy().run(returns_df=returns)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "dataset": str(dataset),
        "benchmark": benchmark,
        "shape": [int(returns.shape[0]), int(returns.shape[1])],
        "repeats": repeats,
        "warmup": warmup,
        "beta_ms_median": round(statistics.median(beta_times) * 1000, 4),
        "beta_ms_min": round(min(beta_times) * 1000, 4),
        "full_ms_median": round(statistics.median(full_times) * 1000, 4),
        "full_ms_min": round(min(full_times) * 1000, 4),
        "peak_tracemalloc_mb": round(peak / 1e6, 4),
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="tests/fixtures/real_market_prices.csv")
    p.add_argument("--benchmark", default="BTC")
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--warmup", type=int, default=1)
    p.add_argument("--record", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument(
        "--output", default="research_state/perf_baseline_real_fixture.json"
    )
    p.add_argument("--baseline", default=None)
    p.add_argument(
        "--time-tolerance",
        type=float,
        default=1.75,
        help="Allowed slowdown factor vs baseline median (default 1.75x for CI variance)",
    )
    p.add_argument(
        "--mem-tolerance-mb",
        type=float,
        default=20.0,
        help="Allowed absolute peak tracemalloc increase in MB",
    )
    args = p.parse_args(argv)

    if args.record == args.check:
        print("Specify exactly one of --record or --check", file=sys.stderr)
        return 2
    dataset = Path(args.dataset)
    if not dataset.exists():
        print(f"Dataset not found: {dataset}", file=sys.stderr)
        return 1

    metrics = measure(dataset, max(1, args.repeats), max(0, args.warmup), args.benchmark)
    if args.record:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "command": (
                "python scripts/perf_baseline.py --record "
                f"--dataset {dataset} --output {out} --repeats {args.repeats}"
            ),
            "metrics": metrics,
        }
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    baseline_path = Path(args.baseline or args.output)
    if not baseline_path.exists():
        print(f"Baseline not found: {baseline_path}", file=sys.stderr)
        return 1
    baseline = json.loads(baseline_path.read_text()).get("metrics", {})
    failures = []
    for key in ("beta_ms_median", "full_ms_median"):
        base = float(baseline.get(key, 0) or 0)
        cur = float(metrics.get(key, 0) or 0)
        limit = base * args.time_tolerance if base > 0 else float("inf")
        if base > 0 and cur > limit:
            failures.append(
                f"{key}: current {cur:.4f}ms > limit {limit:.4f}ms "
                f"(baseline {base:.4f}ms)"
            )
    base_mem = float(baseline.get("peak_tracemalloc_mb", 0) or 0)
    cur_mem = float(metrics.get("peak_tracemalloc_mb", 0) or 0)
    if cur_mem > base_mem + args.mem_tolerance_mb:
        failures.append(
            "peak_tracemalloc_mb: current "
            f"{cur_mem:.4f} > baseline+tol {base_mem + args.mem_tolerance_mb:.4f}"
        )
    print(
        json.dumps(
            {"current": metrics, "baseline": baseline, "failures": failures},
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
