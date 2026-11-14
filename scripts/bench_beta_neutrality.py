#!/usr/bin/env python3
"""Reproducible production-scale benchmark for the BAB hot path.

Usage:
    python3 scripts/bench_beta_neutrality.py
    python3 scripts/bench_beta_neutrality.py --sizes 2500x40,2500x120 --reps 35
    python3 scripts/bench_beta_neutrality.py --profile

Prints warm medians (milliseconds) for ``enforce_beta_neutrality``,
``construct_portfolio`` and ``run_backtest`` at production scale.  This is the
single command the next session should use for before/after evidence; it does
not modify the repository.
"""

from __future__ import annotations

import argparse
import cProfile
import io
import pstats
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402
from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.data import generate_synthetic_returns  # noqa: E402
from strategies.betting_against_beta.portfolio import (  # noqa: E402
    construct_portfolio,
    enforce_beta_neutrality,
)
from strategies.betting_against_beta.signals import generate_bab_signals  # noqa: E402


def warm_median(fn, reps: int, **kwargs) -> tuple[float, float, float]:
    """Return (median, min, max) milliseconds after one warm-up call."""
    fn(**kwargs)
    samples = []
    for _ in range(reps):
        start = time.perf_counter()
        fn(**kwargs)
        samples.append((time.perf_counter() - start) * 1e3)
    return statistics.median(samples), min(samples), max(samples)


def build_inputs(n_days: int, n_assets: int):
    returns = generate_synthetic_returns(n_days=n_days, n_assets=n_assets, seed=1234)
    beta = calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)
    signals = generate_bab_signals(beta, long_quantile=0.3, short_quantile=0.3)
    weights = construct_portfolio(signals)
    return returns, beta, signals, weights


def profile_beta_neutrality(weights, beta, reps: int) -> None:
    enforce_beta_neutrality(weights, beta)
    prof = cProfile.Profile()
    prof.enable()
    for _ in range(reps):
        enforce_beta_neutrality(weights, beta)
    prof.disable()
    stream = io.StringIO()
    pstats.Stats(prof, stream=stream).sort_stats("tottime").print_stats(12)
    print("\n=== cProfile enforce_beta_neutrality (top tottime) ===")
    print(stream.getvalue())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Production-scale BAB hot-path benchmark (warm medians).",
        epilog="Example: python3 scripts/bench_beta_neutrality.py --sizes 2500x120 --reps 35 --profile",
    )
    parser.add_argument("--sizes", default="2500x40,2500x50,2500x120")
    parser.add_argument("--reps", type=int, default=35)
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    sizes = []
    for token in args.sizes.split(","):
        token = token.strip()
        if not token:
            continue
        days, assets = token.lower().split("x")
        sizes.append((int(days), int(assets)))

    for n_days, n_assets in sizes:
        returns, beta, signals, weights = build_inputs(n_days, n_assets)
        med_b, lo_b, hi_b = warm_median(
            enforce_beta_neutrality, args.reps, weights=weights, betas=beta
        )
        med_p, _, _ = warm_median(construct_portfolio, args.reps, signals_df=signals)
        med_r, lo_r, hi_r = warm_median(
            run_backtest, args.reps, returns_df=returns, weights_df=weights
        )
        print(
            f"{n_days}x{n_assets}: enforce_beta_neutrality={med_b:.3f} ms "
            f"(min {lo_b:.3f}/max {hi_b:.3f}) | construct={med_p:.3f} ms | "
            f"run_backtest={med_r:.3f} ms (min {lo_r:.3f}/max {hi_r:.3f})"
        )
        if args.profile:
            profile_beta_neutrality(weights, beta, max(1, args.reps // 5))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
