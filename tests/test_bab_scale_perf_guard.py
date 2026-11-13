"""R2-C: Scale performance guard for the BAB engine.

Measures ``BABStrategy.run`` at 5000x200 and 5000x500 (beta_neutral=True),
median of 9 warm reps, warm. Asserts the live ceilings:

  5000x200 <= 0.8 s   5000x500 <= 2.0 s

The ceilings are asserted, not the medians: if the live baseline moves, the
guard still holds as long as runtime stays within ceiling. Fail loudly on an
order-of-magnitude scale regression so it is impossible to ignore.

This guard measures live every run (no hard-coded stale medians). Baseline
measured 2026-11-13T18:30:33Z on this host: 5000x200 ~306 ms, 5000x500 ~783 ms
(median of 9 warm reps).
"""

from __future__ import annotations

import statistics
import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy

SEED = 7
CEILINGS = {"5000x200": 0.8, "5000x500": 2.0}
REPS = 9


def _frame(n_days, n_assets):
    rng = np.random.default_rng(SEED)
    cols = [f"A{i}" for i in range(n_assets - 1)] + ["BTC"]
    data = rng.standard_normal((n_days, n_assets)) * 0.01 + 0.0003
    idx = pd.date_range("2018-01-01", periods=n_days, freq="D")
    return pd.DataFrame(data, index=idx, columns=cols)


def _time_run(df):
    s = BABStrategy(benchmark="BTC", beta_window=90, beta_neutral=True, dollar_neutral=True)
    t0 = time.perf_counter()
    s.run(returns_df=df)
    return time.perf_counter() - t0


_scale_records: list[dict] = []


@pytest.mark.parametrize("label,n_days,n_assets", [("5000x200", 5000, 200), ("5000x500", 5000, 500)])
def test_scale_perf_guard(label, n_days, n_assets):
    """``BABStrategy.run`` at scale stays under its hard ceiling."""
    df = _frame(n_days, n_assets)
    # One warmup rep (caches imports/JIT-adjacent paths), then 9 timed reps.
    _time_run(df)
    times = [_time_run(df) for _ in range(REPS)]
    times = np.asarray(times)
    median_s = float(np.median(times))
    ceiling = CEILINGS[label]

    _scale_records.append(
        {
            "label": label,
            "median_ms": median_s * 1000.0,
            "min_ms": float(times.min()) * 1000.0,
            "max_ms": float(times.max()) * 1000.0,
            "ceiling_ms": ceiling * 1000.0,
        }
    )

    print(
        f"[R2-C] {label}: median={median_s*1000:.1f}ms "
        f"min={times.min()*1000:.1f}ms max={times.max()*1000:.1f}ms "
        f"(ceiling {ceiling*1000:.0f}ms)"
    )
    assert median_s <= ceiling, (
        f"scale regression: {label} median {median_s*1000:.1f}ms exceeds ceiling "
        f"{ceiling*1000:.0f}ms"
    )


def test_scale_evidence_summary():
    """Recorded scale baselines vs ceilings."""
    print("\n[R2-C] scale performance guard evidence (median of 9 warm reps):")
    print(f"{'frame':<10} {'median_ms':>11} {'min_ms':>10} {'max_ms':>10} {'ceiling_ms':>12}")
    for rec in _scale_records:
        assert rec["median_ms"] <= rec["ceiling_ms"]
        print(
            f"{rec['label']:<10} {rec['median_ms']:>11.1f} {rec['min_ms']:>10.1f} "
            f"{rec['max_ms']:>10.1f} {rec['ceiling_ms']:>12.0f}"
        )
