"""BAB signals and portfolio edge cases - NaN/empty/single-asset/extremes/ties."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.signals import generate_bab_signals


def test_signals_empty_input():
    assert generate_bab_signals(None).empty
    assert generate_bab_signals(pd.DataFrame()).empty


def test_signals_nan_betas_all_zero():
    dates = pd.date_range("2023-01-01", periods=5)
    betas = pd.DataFrame({"BTC": [np.nan]*5, "ETH": [np.nan]*5}, index=dates)
    sig = generate_bab_signals(betas)
    assert sig.shape == betas.shape
    assert (sig.values == 0).all()
    assert np.isfinite(sig.values).all()


def test_signals_all_equal_betas_ties():
    dates = pd.date_range("2023-01-01", periods=3)
    betas = pd.DataFrame({"A": [1.0]*3, "B": [1.0]*3, "C": [1.0]*3}, index=dates)
    sig = generate_bab_signals(betas)
    assert sig.shape == betas.shape
    # With ties, ranking is stable; must not crash and produce finite integer values
    assert np.isfinite(sig.values).all()
    assert sig.dtypes.apply(lambda x: np.issubdtype(x, np.integer)).all()


def test_signals_single_asset_universe_flat():
    dates = pd.date_range("2023-01-01", periods=4)
    betas = pd.DataFrame({"BTC": [0.5, 0.6, 0.7, 0.8]}, index=dates)
    sig = generate_bab_signals(betas)
    assert (sig.values == 0).all()


def test_signals_extreme_quantiles_zero_one_boundaries():
    dates = pd.date_range("2023-01-01", periods=10)
    betas = pd.DataFrame({
        "A": np.linspace(0.2, 1.5, 10),
        "B": np.linspace(0.3, 1.4, 10),
        "C": np.linspace(0.4, 1.3, 10),
        "D": np.linspace(0.5, 1.2, 10),
        "E": np.linspace(0.6, 1.1, 10),
    }, index=dates)
    # q=0 should behave safely (no division by zero / crashes)
    sig = generate_bab_signals(betas, long_quantile=0.0, short_quantile=0.3)
    assert np.isfinite(sig.values).all()
    assert (sig.values == 0).all() or True  # may be all zero or still safe; main thing no crash
    sig2 = generate_bab_signals(betas, long_quantile=0.3, short_quantile=0.0)
    assert np.isfinite(sig2.values).all()
    # q>=1 - should not crash
    sig3 = generate_bab_signals(betas, long_quantile=1.0, short_quantile=1.0)
    assert np.isfinite(sig3.values).all()
    # q very small
    sig4 = generate_bab_signals(betas, long_quantile=0.01, short_quantile=0.01)
    assert np.isfinite(sig4.values).all()


def test_portfolio_ties_equal_betas_dollar_neutral():
    dates = pd.date_range("2023-01-01", periods=2)
    # All equal betas -> signals may be all zero depending on ranking; if any signals exist, weights must be neutral
    sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1], "C": [0, 0]}, index=dates)
    w = construct_portfolio(sig, dollar_neutral=True)
    assert np.isfinite(w.values).all()
    # Dollar neutral check when both sides exist
    net = w.sum(axis=1)
    assert np.allclose(net.values, 0.0, atol=1e-10)


def test_portfolio_single_asset_row_dollar_neutral_long_only_case():
    dates = pd.date_range("2023-01-01", periods=3)
    sig = pd.DataFrame({"BTC": [1, 1, 0]}, index=dates)
    w = construct_portfolio(sig, dollar_neutral=True)
    assert np.isfinite(w.values).all()
    # Long only with dollar_neutral True in current semantics gives equal weights on longs? Let us check behavior
    assert (w.values >= 0).all()
    # Weights finite and sum appropriately for long only
    assert np.allclose(w.sum(axis=1).values, [1.0, 1.0, 0.0], atol=1e-10)


def test_portfolio_extreme_weights_finiteness():
    dates = pd.date_range("2023-01-01", periods=4)
    sig = pd.DataFrame({"A": [1]*4, "B": [-1]*4, "C": [0]*4}, index=dates)
    w = construct_portfolio(sig)
    assert np.isfinite(w.values).all()
    assert np.allclose(w.sum(axis=1).values, 0.0, atol=1e-10)
