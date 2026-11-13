"""R1-A: Causality / no-lookahead regression harness.

Proves the BAB engine has *no lookahead*: perturbing ``returns_df`` strictly
after a cut index ``t`` must leave every output up to and including ``t``
byte-for-byte identical (weights, betas, signals, backtest), while forcing
post-cut outputs to actually change (non-vacuous guard).

Parametrized over the real shipped fixtures plus a synthetic 2500x120 frame,
across beta_neutral / dollar_neutral / rebalance_freq / costs-slippage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices

REAL_FIXTURES = [
    "tests/fixtures/real_market_prices.csv",
    "tests/fixtures/real_market_prices_expanded.csv",
]

CUT = 200  # integer position; >= beta_window (90) so betas exist before the cut


def _synthetic_frame(n_days: int = 2500, n_assets: int = 120, seed: int = 1234) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    names = ["BTC"] + [f"A{i}" for i in range(1, n_assets)]
    dates = pd.bdate_range("2010-01-04", periods=n_days)
    data = rng.normal(0.0005, 0.02, (n_days, n_assets))
    return pd.DataFrame(data, index=dates, columns=names)


def _run(returns_df, **kw):
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=90,
        long_quantile=0.3,
        short_quantile=0.3,
        **kw,
    )
    return strat, strat.run(returns_df=returns_df)


def _perturb(returns_df: pd.DataFrame, t: int) -> pd.DataFrame:
    """Return a copy with returns strictly after ``t`` perturbed (scale + shock)."""
    out = returns_df.copy()
    tail = out.iloc[t + 1:]
    out.iloc[t + 1:] = tail * 1.5
    # idiosyncratic shock to one non-benchmark asset at t+1
    shock_col = out.columns[1] if out.columns[1] != out.columns[0] else out.columns[2]
    out.iloc[t + 1, out.columns.get_loc(shock_col)] += 0.5
    return out


def _check_no_lookahead(baseline, perturbed, t: int) -> None:
    """Assert pre-cut identity and post-cut change for every output frame."""
    for name, base, pert in [
        ("betas", baseline.betas, perturbed.betas),
        ("signals", baseline.signals, perturbed.signals),
        ("weights", baseline.weights, perturbed.weights),
        ("backtest", baseline.backtest, perturbed.backtest),
    ]:
        pre_b = base.iloc[: t + 1].to_numpy(dtype=float)
        pre_p = pert.iloc[: t + 1].to_numpy(dtype=float)
        assert np.array_equal(pre_b, pre_p, equal_nan=True), (
            f"{name} up to and including cut t={t} must be identical (lookahead leak)"
        )
        post_b = base.iloc[t + 1:].to_numpy(dtype=float)
        post_p = pert.iloc[t + 1:].to_numpy(dtype=float)
        assert not np.array_equal(post_b, post_p, equal_nan=True), (
            f"{name} after cut t={t} must change (vacuous pass guard)"
        )


@pytest.mark.parametrize("fixture", REAL_FIXTURES)
@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("dollar_neutral", [False, True])
@pytest.mark.parametrize("rebalance_freq", ["daily", "weekly", "monthly"])
@pytest.mark.parametrize("costs_on", [False, True])
def test_no_lookahead_real_fixture(fixture, beta_neutral, dollar_neutral, rebalance_freq, costs_on):
    returns_df = load_prices(fixture, benchmark="BTC", min_rows=30)
    t = min(CUT, len(returns_df) - 2)
    kw = dict(
        beta_neutral=beta_neutral,
        dollar_neutral=dollar_neutral,
        rebalance_freq=rebalance_freq,
        transaction_costs=0.001 if costs_on else 0.0,
        slippage=0.0005 if costs_on else 0.0,
    )
    _, base = _run(returns_df, **kw)
    _, pert = _run(_perturb(returns_df, t), **kw)
    _check_no_lookahead(base, pert, t)


@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("dollar_neutral", [False, True])
def test_no_lookahead_synthetic_2500x120(beta_neutral, dollar_neutral):
    """Bounded synthetic scale check (daily, no costs) to keep runtime low."""
    returns_df = _synthetic_frame()
    t = CUT
    kw = dict(beta_neutral=beta_neutral, dollar_neutral=dollar_neutral)
    _, base = _run(returns_df, **kw)
    _, pert = _run(_perturb(returns_df, t), **kw)
    _check_no_lookahead(base, pert, t)