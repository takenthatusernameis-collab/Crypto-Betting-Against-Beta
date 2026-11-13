"""Oracle-equivalence and performance guard for beta-neutrality enforcement.

``enforce_beta_neutrality`` is the dominant production hot spot when
``beta_neutral=True``. A vectorized implementation is shipped; the reference
implementation below is the row-wise semantics that any rewrite must reproduce
within 1e-12.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.data import generate_synthetic_returns
from strategies.betting_against_beta.portfolio import (
    construct_portfolio,
    enforce_beta_neutrality,
)
from strategies.betting_against_beta.signals import generate_bab_signals


def _reference_enforce(
    weights,
    betas,
    target_beta=0.0,
    tolerance=1e-4,
    max_drift=1e-4,
    returns=None,
    benchmark_returns=None,
    tracking_error_tolerance=None,
    tracking_error_limit=None,
    enable_tracking_error_monitoring=False,
    correction=True,
):
    """Row-wise oracle mirroring the documented enforcement semantics."""
    if weights is None or betas is None:
        return weights
    if not isinstance(weights, pd.DataFrame) or weights.empty:
        return weights
    if not isinstance(betas, pd.DataFrame) or betas.empty:
        return weights

    common_cols = weights.columns.intersection(betas.columns)
    if len(common_cols) == 0:
        return weights
    common_idx = weights.index.intersection(betas.index)
    if len(common_idx) == 0:
        return weights

    w = weights.loc[common_idx, common_cols].astype(float).copy()
    b = betas.loc[common_idx, common_cols].astype(float).copy()
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    b = b.replace([np.inf, -np.inf], np.nan)

    out = w.copy()
    cols = list(out.columns)
    w_arr = out.to_numpy(dtype=float, copy=True)
    b_arr = b.to_numpy(dtype=float)

    tol = float(tolerance) if tolerance is not None else 1e-4
    drift = float(max_drift) if max_drift is not None else tol
    if not np.isfinite(tol) or tol < 0:
        tol = 1e-4
    if not np.isfinite(drift) or drift < 0:
        drift = tol
    target = float(target_beta) if target_beta is not None else 0.0
    if not np.isfinite(target):
        target = 0.0

    for i in range(len(common_idx)):
        row_b = b_arr[i]
        finite = np.isfinite(row_b)
        if not np.any(finite):
            continue
        b_f = row_b[finite]
        b_mean = float(np.sum(b_f)) / len(b_f)
        centered = b_f - b_mean
        s2_centered = float(np.sum(centered * centered))
        if s2_centered < 1e-18:
            continue
        for _ in range(50):
            row_w = w_arr[i]
            w_f = row_w[finite]
            denom = np.abs(w_f).sum()
            if denom < 1e-18:
                break
            port_beta = float(np.sum(w_f * b_f) / denom)
            if abs(port_beta - target) <= tol:
                break
            if not correction:
                break
            residual = target - port_beta
            alpha = residual / s2_centered
            delta = alpha * centered
            new_w = w_f + delta
            new_w = np.where(np.isfinite(new_w), new_w, 0.0)
            w_arr[i, finite] = new_w

    out = pd.DataFrame(w_arr, index=common_idx, columns=cols)
    out = out.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


def _random_case(seed, n_rows, n_assets, n_finite_beta=1.0, n_nonfinite_beta=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n_rows, freq="D")
    cols = [f"A{i}" for i in range(n_assets)]
    weights = pd.DataFrame(rng.normal(0.0, 0.2, size=(n_rows, n_assets)), index=dates, columns=cols)
    betas = pd.DataFrame(rng.normal(0.8, 0.4, size=(n_rows, n_assets)), index=dates, columns=cols)
    # Sprinkle non-finite values into weights and betas.
    if n_rows and n_assets:
        wv = weights.to_numpy(copy=True)
        wv[rng.random(wv.shape) < 0.05] = np.nan
        wv[rng.random(wv.shape) < 0.02] = np.inf
        weights = pd.DataFrame(wv, index=dates, columns=cols)
        bv = betas.to_numpy(copy=True)
        bv[rng.random(bv.shape) < (1.0 - n_finite_beta)] = np.nan
        for _ in range(n_nonfinite_beta):
            bv[rng.integers(0, n_rows), rng.integers(0, n_assets)] = np.inf
        betas = pd.DataFrame(bv, index=dates, columns=cols)
    return weights, betas


@pytest.mark.parametrize(
    "seed,n_rows,n_assets,target,tol,correction",
    [
        (1, 1, 1, 0.0, 1e-4, True),
        (2, 4, 3, 0.0, 1e-6, True),
        (3, 12, 6, 0.25, 1e-4, True),
        (4, 25, 9, -0.1, 1e-3, True),
        (5, 25, 9, 0.0, 1e-4, False),
        (6, 40, 12, 0.5, 1e-8, True),
        (7, 1, 7, 0.0, 1e-4, True),  # single row
        (8, 9, 1, 0.0, 1e-4, True),  # single column
    ],
)
def test_reference_oracle_matches(seed, n_rows, n_assets, target, tol, correction):
    weights, betas = _random_case(seed, n_rows, n_assets)
    got = enforce_beta_neutrality(
        weights, betas, target_beta=target, tolerance=tol, correction=correction
    )
    expected = _reference_enforce(
        weights, betas, target_beta=target, tolerance=tol, correction=correction
    )
    pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("seed", [101, 202, 303, 404, 505])
def test_randomized_nan_inf_oracle(seed):
    """Randomized NaN/inf/tie-heavy cases must match oracle at 1e-12."""
    rng = np.random.default_rng(seed)
    n_rows = int(rng.integers(2, 40))
    n_assets = int(rng.integers(2, 20))
    weights, betas = _random_case(seed, n_rows, n_assets, n_finite_beta=0.6, n_nonfinite_beta=6)
    # Force some rows to all-equal beta / zero weights / all-nan beta.
    if n_rows >= 3:
        betas.iloc[0, :] = 0.7  # tie/all-equal-beta
        weights.iloc[1, :] = 0.0  # zero-row
        betas.iloc[2, :] = np.nan  # all-NaN-beta
    got = enforce_beta_neutrality(weights, betas, target_beta=0.0, tolerance=1e-4)
    expected = _reference_enforce(weights, betas, target_beta=0.0, tolerance=1e-4)
    pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)
    assert got.index.equals(weights.index.intersection(betas.index))
    assert got.columns.equals(weights.columns.intersection(betas.columns))


def test_reference_oracle_handles_degenerate_frames():
    dates = pd.date_range("2024-01-01", periods=5)
    cols = ["A", "B", "C"]

    # All betas equal -> no adjustment (s2_centered == 0).
    betas = pd.DataFrame(0.5, index=dates, columns=cols)
    weights = pd.DataFrame(
        [[0.5, -0.5, 0.0]] * len(dates), index=dates, columns=cols
    )
    pd.testing.assert_frame_equal(
        enforce_beta_neutrality(weights, betas, tolerance=1e-4),
        _reference_enforce(weights, betas, tolerance=1e-4),
    )

    # Zero weights -> no adjustment.
    zero = pd.DataFrame(0.0, index=dates, columns=cols)
    pd.testing.assert_frame_equal(
        enforce_beta_neutrality(zero, betas + 0.1, tolerance=1e-4),
        _reference_enforce(zero, betas + 0.1, tolerance=1e-4),
    )

    # All-NaN beta row -> unchanged.
    nan_betas = betas.copy()
    nan_betas.iloc[:, :] = np.nan
    pd.testing.assert_frame_equal(
        enforce_beta_neutrality(weights, nan_betas),
        _reference_enforce(weights, nan_betas),
    )


def test_correction_false_noop_and_shapes():
    """Explicit correction=False must be a no-op and preserve aligned shape."""
    dates = pd.date_range("2024-01-01", periods=6)
    cols = ["A", "B", "C"]
    rng = np.random.default_rng(77)
    weights = pd.DataFrame(rng.normal(0, 0.3, size=(6, 3)), index=dates, columns=cols)
    betas = pd.DataFrame(rng.normal(1.0, 0.5, size=(6, 3)), index=dates, columns=cols)
    got = enforce_beta_neutrality(weights, betas, correction=False)
    expected = _reference_enforce(weights, betas, correction=False)
    pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)
    assert got.index.equals(dates)
    assert list(got.columns) == cols


def test_reference_oracle_handles_misaligned_frames():
    rng = np.random.default_rng(11)
    w_dates = pd.date_range("2024-01-01", periods=8)
    b_dates = pd.date_range("2024-01-03", periods=8)
    weights = pd.DataFrame(
        rng.normal(0, 0.2, size=(8, 4)), index=w_dates, columns=["A", "B", "C", "D"]
    )
    betas = pd.DataFrame(
        rng.normal(0.8, 0.4, size=(8, 4)), index=b_dates, columns=["B", "C", "D", "E"]
    )
    got = enforce_beta_neutrality(weights, betas)
    expected = _reference_enforce(weights, betas)
    pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)
    assert list(got.columns) == ["B", "C", "D"]


def test_single_row_column_and_alignment_oracle():
    # single row
    w = pd.DataFrame([[0.5, -0.5, 0.0]], index=[0], columns=["A", "B", "C"])
    b = pd.DataFrame([[1.2, 0.8, 1.0]], index=[0], columns=["A", "B", "C"])
    pd.testing.assert_frame_equal(
        enforce_beta_neutrality(w, b), _reference_enforce(w, b), rtol=1e-12, atol=1e-12
    )
    # single column
    w = pd.DataFrame([[0.5], [-0.2], [0.1]], index=[0, 1, 2], columns=["A"])
    b = pd.DataFrame([[1.1], [0.9], [1.3]], index=[0, 1, 2], columns=["A"])
    pd.testing.assert_frame_equal(
        enforce_beta_neutrality(w, b), _reference_enforce(w, b), rtol=1e-12, atol=1e-12
    )


def test_enforce_beta_neutrality_perf_ceiling():
    """Non-regression ceiling for the dominant beta-neutral hot spot.

    Measured warm median at HEAD (python 3.12, numpy 2.5.4, pandas 3.1.1):
      2500x40  ~21.7 ms, 2500x50 ~20.9 ms, 2500x120 ~63.7 ms.
    Bound tightened from 1.5 s to 0.25 s with margin for shared runners.
    """
    returns = generate_synthetic_returns(n_days=2500, n_assets=120, seed=1234)
    beta = calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)
    signals = generate_bab_signals(beta, long_quantile=0.3, short_quantile=0.3)
    weights = construct_portfolio(signals)

    enforce_beta_neutrality(weights, beta)  # warm
    start = time.perf_counter()
    enforce_beta_neutrality(weights, beta)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.25, (
        f"enforce_beta_neutrality took {elapsed:.3f}s at {weights.shape}; "
        "beta-neutral perf regression (expected < 0.25 s on this workload)"
    )