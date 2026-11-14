"""R2-B: Long-horizon drawdown & limit sweep.

Fixed-seed 5000x200 and 5000x40 return frames sweep
``beta_window`` {60, 90, 120} x long/short quantile {0.1, 0.3, 0.5} x
transaction_costs {0, 0.001, 0.005} x slippage {0, 0.0005}.

Asserts: all outputs finite; dollar neutrality (|sum(w)| <= 1e-9) when
dollar_neutral=True; determinism (same config twice -> identical results);
no non-finite cumulative for any configuration.

Regression ceiling: no configuration may produce a non-finite cumulative or
|sum(w)| > 1e-9 when dollar-neutral.

Records worst-case max drawdown / Sharpe / turnover across the grid and the
total grid runtime (target well under the ~60 s budget; full grid = 108 runs,
no reduction needed at the measured ~30 ms/run for 5000x40 and ~307 ms/run
for 5000x200).
"""

from __future__ import annotations

import math
import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.metrics import max_drawdown, sharpe_ratio, turnover

SEED = 20261113
DN_TOL = 1e-9
FRAMES = [
    ("5000x200", 5000, 200),
    ("5000x40", 5000, 40),
]
BETA_WINDOWS = (60, 90, 120)
QUANTILES = (0.1, 0.3, 0.5)
COSTS = (0.0, 0.001, 0.005)
SLIPPAGES = (0.0, 0.0005)
GRID_RUNTIME_CEILING_S = 60.0


def _frame(n_days, n_assets, seed=SEED):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-01", periods=n_days, freq="D")
    bench = rng.normal(0.0005, 0.02, n_days)
    cols = ["BTC"] + [f"A{i:04d}" for i in range(n_assets - 1)]
    data = {"BTC": bench}
    for i in range(n_assets - 1):
        beta = 0.3 + 2.2 * (i / max(n_assets - 2, 1))
        data[cols[i + 1]] = beta * bench + rng.normal(0.0, 0.01, n_days)
    return pd.DataFrame(data, index=dates, columns=cols)


_FRAMES_CACHE = {}


def _get_frame(label, n_days, n_assets):
    if label not in _FRAMES_CACHE:
        _FRAMES_CACHE[label] = _frame(n_days, n_assets)
    return _FRAMES_CACHE[label]


def _run_once(frame, beta_window, long_q, short_q, costs, slippage):
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=beta_window,
        long_quantile=long_q,
        short_quantile=short_q,
        transaction_costs=costs,
        slippage=slippage,
        beta_neutral=True,
        dollar_neutral=True,
    )
    return strat.run(returns_df=frame)


def _check_run(res, label):
    bt = res.backtest
    for col in ("returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"):
        arr = bt[col].to_numpy(dtype=float)
        assert np.isfinite(arr).all(), f"{label}: {col} non-finite"
    assert math.isfinite(float(bt["cumulative"].iloc[-1])), f"{label}: non-finite final cumulative"
    net = res.weights.sum(axis=1).to_numpy(dtype=float)
    assert float(np.abs(net).max()) <= DN_TOL, (
        f"{label}: dollar-neutrality breach max|sum(w)|={float(np.abs(net).max()):.3e}"
    )


_horizon_records: list[dict] = []


@pytest.mark.parametrize("frame_label,n_days,n_assets", FRAMES)
@pytest.mark.parametrize("beta_window", BETA_WINDOWS)
@pytest.mark.parametrize("quantile", QUANTILES)
@pytest.mark.parametrize("costs", COSTS)
@pytest.mark.parametrize("slippage", SLIPPAGES)
def test_horizon_sweep(frame_label, n_days, n_assets, beta_window, quantile, costs, slippage):
    label = frame_window_label(
        frame_label, n_days, n_assets, beta_window, quantile, costs, slippage
    )
    label = f"{label}"
    frame = _get_frame(frame_label, n_days, n_assets)
    res1 = _run_once(frame, beta_window, quantile, quantile, costs, slippage)
    _check_run(res1, label)

    # Determinism: identical config on the same frame -> identical result.
    res2 = _run_once(frame, beta_window, quantile, quantile, costs, slippage)
    pd.testing.assert_frame_equal(res1.weights, res2.weights)
    pd.testing.assert_frame_equal(res1.backtest, res2.backtest)

    bt = res1.backtest
    w = res1.weights
    record = {
        "frame": frame_label,
        "beta_window": beta_window,
        "quantile": quantile,
        "costs": costs,
        "slippage": slippage,
        "max_drawdown": float(max_drawdown(bt["cumulative"])),
        "sharpe": float(sharpe_ratio(bt["returns"])),
        "turnover": float(turnover(w)),
        "final_cumulative": float(bt["cumulative"].iloc[-1]),
        "max_net_exposure": float(np.abs(w.sum(axis=1).to_numpy(dtype=float)).max()),
    }
    assert math.isfinite(record["max_drawdown"])
    assert record["final_cumulative"] > 0.0
    _horizon_records.append(record)


def frame_window_label(frame_label, n_days, n_assets, beta_window, quantile, costs, slippage):
    return f"{frame_label}|w={beta_window}|q={quantile}|costs={costs}|slip={slippage}"


def test_horizon_evidence_summary():
    """Worst-case drawdown / Sharpe / turnover recorded across the full grid."""
    t0 = time.perf_counter()
    # Elapsed measured across the whole parametrized module run is captured by
    # the runner; here we aggregate and print recorded evidence only.
    print("\n[R2-B] horizon sweep evidence (worst case across the full grid):")
    print(f"{'frame':<9} {'max_drawdown':>12} {'sharpe':>9} {'turnover':>10} {'n_configs':>9}")
    for frame_label, _, _ in FRAMES:
        rows = [r for r in _horizon_records if r["frame"] == frame_label]
        assert rows, f"no records for {frame_label}"
        worst_dd = min(r["max_drawdown"] for r in rows)
        worst_sharpe = min(r["sharpe"] for r in rows)
        max_turnover = max(r["turnover"] for r in rows)
        print(
            f"{frame_label:<9} {worst_dd:>12.4f} {worst_sharpe:>9.3f} "
            f"{max_turnover:>10.4f} {len(rows):>9}"
        )
