"""R1-D: E2E performance guard for the BAB strategy.

Locks the end-to-end runtime of ``BABStrategy.run`` + ``report``/``tear_sheet``
at 2500x120 ``beta_neutral=True`` against a recorded ceiling. Baseline measured
this session: median 102.0 ms (min 95.0 / max 120.5, 9 reps). Ceiling set at
0.60 s to absorb machine noise while catching order-of-magnitude regressions.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy

N_DAYS, N_ASSETS = 2500, 120
RUN_CEILING_S = 0.60  # ~6x the measured median; catches order-of-magnitude regressions
REPORT_CEILING_S = 0.25
TEAR_SHEET_CEILING_S = 0.25
REPS = 9


def _synthetic_frame() -> pd.DataFrame:
    rng = np.random.default_rng(1234)
    names = ["BTC"] + [f"A{i}" for i in range(1, N_ASSETS)]
    dates = pd.bdate_range("2010-01-04", periods=N_DAYS)
    data = rng.normal(0.0005, 0.02, (N_DAYS, N_ASSETS))
    return pd.DataFrame(data, index=dates, columns=names)


def _timed_run() -> float:
    df = _synthetic_frame()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=90,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.0,
        beta_neutral=True,
        dollar_neutral=True,
    )
    t0 = time.perf_counter()
    res = strat.run(returns_df=df)
    run_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    rep = strat.report(res)
    report_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    ts = strat.tear_sheet(res)
    tear_s = time.perf_counter() - t0

    assert isinstance(ts, str) and len(ts) > 0
    assert isinstance(rep, dict) and "metrics" in rep
    return run_s, report_s, tear_s


def test_e2e_run_performance_guard():
    """``BABStrategy.run`` at 2500x120 beta_neutral=True stays under ceiling."""
    run_times = []
    report_times = []
    tear_times = []
    for _ in range(REPS):
        r, rp, t = _timed_run()
        run_times.append(r)
        report_times.append(rp)
        tear_times.append(t)

    run_times = np.asarray(run_times)
    report_times = np.asarray(report_times)
    tear_times = np.asarray(tear_times)

    median_run = float(np.median(run_times))
    median_report = float(np.median(report_times))
    median_tear = float(np.median(tear_times))

    # Record evidence alongside the assertion (printed by pytest -rA).
    print(
        f"\n[R1-D] run median={median_run * 1000:.1f}ms min={run_times.min() * 1000:.1f} "
        f"max={run_times.max() * 1000:.1f}ms (ceiling {RUN_CEILING_S * 1000:.0f}ms)"
    )
    print(
        f"[1-D] report median={median_report * 1000:.1f}ms "
        f"(ceiling {REPORT_CEILING_S * 1000:.0f}ms)"
    )
    print(
        f"[1-D] tear_sheet median={median_tear * 1000:.1f}ms "
        f"(ceiling {TEAR_SHEET_CEILING_S * 1000:.0f}ms)"
    )

    assert median_run < RUN_CEILING_S, (
        f"E2E run regressed: median {median_run * 1000:.1f}ms exceeds ceiling "
        f"{RUN_CEILING_S * 1000:.0f}ms"
    )
    assert median_report < REPORT_CEILING_S
    assert median_tear < TEAR_SHEET_CEILING_S
