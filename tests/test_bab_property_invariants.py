"""Property-based invariants for the BAB strategy pipeline (hypothesis).

Deterministic and offline. Asserts finiteness, dollar-neutrality when both sides
exist, the benchmark-beta == 1.0 invariant, and determinism across randomized
data and configs. These are regression guardrails: any future change that breaks
an invariant fails here. hypothesis is a declared dependency that was previously
unused by the test suite.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from hypothesis import HealthCheck, given, settings, strategies as st

from strategies.betting_against_beta import BABStrategy, BABConfig


@st.composite
def _returns_frame(draw):
    n_days = draw(st.integers(min_value=60, max_value=220))
    n_assets = draw(st.integers(min_value=3, max_value=9))
    seed = draw(st.integers(min_value=0, max_value=10_000))
    inject_nan = draw(st.booleans())
    nan_frac = draw(st.floats(min_value=0.0, max_value=0.06))
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n_days, freq="D")
    bench = rng.normal(0.0005, 0.02, n_days)
    cols = ["BTC"] + [f"A{i:02d}" for i in range(n_assets - 1)]
    data = {"BTC": bench}
    for c in cols[1:]:
        data[c] = rng.normal(0.0004, 0.025, n_days)
    df = pd.DataFrame(data, index=idx)
    if inject_nan:
        df = df.mask(rng.random(df.shape) < nan_frac)
    return df


@st.composite
def _config(draw):
    return BABConfig(
        benchmark="BTC",
        beta_window=draw(st.integers(min_value=30, max_value=120)),
        min_observations=draw(st.integers(min_value=20, max_value=60)),
        long_quantile=draw(st.floats(min_value=0.05, max_value=0.5)),
        short_quantile=draw(st.floats(min_value=0.05, max_value=0.5)),
        dollar_neutral=draw(st.booleans()),
        transaction_costs=draw(st.floats(min_value=0.0, max_value=0.005)),
        slippage=draw(st.floats(min_value=0.0, max_value=0.002)),
        rebalance_freq=draw(st.sampled_from(["daily", "weekly", "monthly"])),
        synthetic_seed=42,
    )


_prop_settings = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=(HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.large_base_example),
)


@_prop_settings
@given(df=_returns_frame(), cfg=_config())
def test_pipeline_finiteness_and_invariants(df, cfg):
    res = BABStrategy(cfg).run(returns_df=df)
    w = res.weights
    bt = res.backtest
    sig = res.signals

    # Finiteness everywhere.
    assert np.isfinite(w.values).all(), "weights must be finite"
    assert np.isfinite(bt["returns"].values).all(), "backtest returns must be finite"
    assert np.isfinite(bt["cumulative"].values).all(), "cumulative must be finite"
    assert np.isfinite(sig.values).all(), "signals must be finite"
    assert (sig.values.astype(float) % 1 == 0).all(), "signals must be integer-valued"

    # Benchmark carries beta exactly 1.0 wherever finite.
    bb = res.betas["BTC"].to_numpy(dtype=float)
    valid = bb[np.isfinite(bb)]
    if len(valid):
        assert np.allclose(valid, 1.0, atol=1e-9), "benchmark beta must be exactly 1.0"

    # Dollar neutrality: whenever a row holds both long and short weight, net
    # exposure is zero to machine precision.
    if cfg.dollar_neutral:
        for row in w.values:
            pos = row[row > 0]
            neg = row[row < 0]
            if len(pos) and len(neg):
                assert np.allclose(row.sum(), 0.0, atol=1e-9), "dollar-neutral row must net to zero"

    # Determinism: identical input must produce identical output.
    res2 = BABStrategy(cfg).run(returns_df=df)
    assert w.values.tolist() == res2.weights.values.tolist(), "weights must be deterministic"
    assert bt["returns"].values.tolist() == res2.backtest["returns"].values.tolist(), "returns must be deterministic"


@_prop_settings
@given(df=_returns_frame(), cfg=_config())
def test_no_silent_failures_on_chaos_data(df, cfg):
    """Chaos data (NaNs, short history, tight quantiles) never raises silently;
    it either runs cleanly with finite output or degrades to flat zero weights."""
    res = BABStrategy(cfg).run(returns_df=df)
    w = res.weights
    bt = res.backtest
    assert np.isfinite(w.values).all()
    assert np.isfinite(bt["returns"].values).all()
    assert np.isfinite(bt["cumulative"].values).all()
    # Backtest length matches aligned input length.
    assert len(bt) == len(w)
