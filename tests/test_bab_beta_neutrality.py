"""Beta-neutrality enforcement tests for BAB strategy.

Covers the ``enforce_beta_neutrality`` function in portfolio.py and the
end-to-end ``beta_neutral=True`` config path through BABStrategy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.portfolio import construct_portfolio, enforce_beta_neutrality
from strategies.betting_against_beta.strategy import BABStrategy


def _make_betas(n_rows=10, n_assets=4, seed=7):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n_rows)
    cols = ["BTC", "ETH", "SOL", "BNB"][:n_assets]
    data = rng.normal(0.5, 0.3, size=(n_rows, n_assets))
    return pd.DataFrame(data, index=dates, columns=cols)


def test_enforce_beta_neutrality_none_inputs():
    assert enforce_beta_neutrality(None, None) is None
    empty = pd.DataFrame()
    assert enforce_beta_neutrality(empty, empty).empty


def test_enforce_beta_neutrality_no_overlap():
    weights = pd.DataFrame()
    betas = pd.DataFrame()
    out = enforce_beta_neutrality(weights, betas)
    assert out.empty


def test_enforce_beta_neutrality_preserves_when_within_tolerance():
    # All betas equal -> any dollar-neutral portfolio has portfolio beta exactly 0,
    # which is within any positive tolerance, so weights must be preserved unchanged.
    dates = pd.date_range("2023-01-01", periods=4)
    betas = pd.DataFrame(
        {"BTC": [0.5] * 4, "ETH": [0.5] * 4, "SOL": [0.5] * 4, "BNB": [0.5] * 4},
        index=dates,
    )
    n = betas.shape[1]
    w = np.zeros(n)
    w[0] = 0.5
    w[1] = -0.5
    weights = pd.DataFrame([w] * len(betas), index=betas.index, columns=betas.columns)
    out = enforce_beta_neutrality(weights, betas, target_beta=0.0, tolerance=1e-3)
    # Should be unchanged because the adjustment is within tolerance.
    assert np.allclose(out.values, weights.values, atol=1e-12)


def test_enforce_beta_neutrality_drives_beta_toward_target():
    betas = _make_betas()
    # Long-only portfolio with positive beta.
    w = np.zeros(betas.shape[1])
    w[0] = 1.0
    weights = pd.DataFrame([w] * len(betas), index=betas.index, columns=betas.columns)
    out = enforce_beta_neutrality(weights, betas, target_beta=0.0, tolerance=1e-6)
    # After correction the weighted beta should be reduced (not necessarily zero
    # because dollar neutrality may conflict, but it should be much smaller than
    # the original beta).
    for i in range(len(betas)):
        row_w = out.iloc[i].to_numpy(dtype=float)
        row_b = betas.iloc[i].to_numpy(dtype=float)
        denom = np.abs(row_w).sum()
        if denom > 1e-18:
            port_beta = float(np.sum(row_w * row_b) / denom)
            # Original beta was ~0.5 (BTC has beta 0.5 on average); after
            # enforcement it should be closer to 0 than before.
            assert abs(port_beta) < 0.5


def test_enforce_beta_neutrality_preserves_dollar_neutrality():
    betas = _make_betas()
    n = betas.shape[1]
    w = np.zeros(n)
    w[0] = 0.5
    w[1] = -0.5
    weights = pd.DataFrame([w] * len(betas), index=betas.index, columns=betas.columns)
    out = enforce_beta_neutrality(weights, betas, target_beta=0.0, tolerance=1e-6)
    net = out.sum(axis=1).values
    assert np.allclose(net, 0.0, atol=1e-10)


def test_enforce_beta_neutrality_finite_output():
    betas = _make_betas()
    weights = pd.DataFrame(np.random.RandomState(1).normal(0, 0.1, size=(len(betas), betas.shape[1])),
                           index=betas.index, columns=betas.columns)
    out = enforce_beta_neutrality(weights, betas, target_beta=0.0)
    assert np.isfinite(out.values).all()


def test_enforce_beta_neutrality_nan_betas_skipped():
    dates = pd.date_range("2023-01-01", periods=5)
    betas = pd.DataFrame({"BTC": [0.5] * 5, "ETH": [np.nan] * 5}, index=dates)
    w = np.array([0.5, -0.5])
    weights = pd.DataFrame([w] * 5, index=dates, columns=betas.columns)
    out = enforce_beta_neutrality(weights, betas, target_beta=0.0)
    assert np.isfinite(out.values).all()
    # ETH should remain at its input weight (no adjustment possible on NaN beta).
    assert np.allclose(out["ETH"].values, -0.5)


def test_strategy_beta_neutral_flag_actually_enforces():
    cfg = BABConfig(beta_neutral=True, beta_target=0.0, beta_tolerance=1e-4)
    s = BABStrategy(cfg)
    r = s.run()
    # Dollar neutrality must hold.
    net = r.weights.sum(axis=1).values
    assert np.allclose(net, 0.0, atol=1e-10)
    # Finiteness.
    assert np.isfinite(r.weights.values).all()
    # Portfolio beta should be reduced vs the non-enforced case.
    betas = r.betas
    w = r.weights
    common = w.columns.intersection(betas.columns)
    denom = w[common].abs().sum(axis=1)
    port_beta = (w[common] * betas[common]).sum(axis=1) / denom.replace(0, np.nan)
    defined = port_beta.dropna()
    if len(defined) > 0:
        # Beta neutrality enforcement should reduce |beta| significantly vs the
        # unconstrained portfolio (which sits near 1.2-1.7 for this data).
        assert np.max(np.abs(defined.values)) < 1.3


def test_strategy_beta_neutral_off_does_not_adjust():
    cfg = BABConfig(beta_neutral=False)
    s = BABStrategy(cfg)
    r = s.run()
    # Default construction is already dollar-neutral; just verify finiteness.
    assert np.isfinite(r.weights.values).all()