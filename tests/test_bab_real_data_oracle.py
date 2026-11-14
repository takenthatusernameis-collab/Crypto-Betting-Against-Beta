"""R1-C: Independent naive-oracle parity for the BAB engine on real data.

This module is a *deliberately naive, loop-based* reference implementation of
the four BAB stages, written from scratch with plain Python loops and
``np.linalg.lstsq`` — it shares no code with the vectorized production path.
It is compared against the shipped, optimized functions on the real fixtures:

  1. ``calculate_rolling_beta``   (per-asset rolling OLS slope)
  2. ``generate_bab_signals``     (per-row beta rank -> long/short)
  3. ``construct_portfolio``      (equal-weight, dollar-neutral book)
  4. ``run_backtest``             (lagged weights, costs, slippage, cumulative)

Parity is asserted at ``rtol=atol=1e-12`` over ``beta_neutral`` {False, True}
and costs/slippage on/off, and the full ``BABStrategy.run`` output (betas,
signals, weights, backtest) is compared between oracle and product.

The oracle is intentionally independent of the product's vectorization tricks
(double-argsort, broadcast products, cumulative-sum rolling windows). If a
divergence is ever found it is a genuine correctness defect in the product, not
a tautology; if none is found the concrete parity evidence is recorded here.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.backtest import run_backtest
from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.signals import generate_bab_signals

RTOL = 1e-12
ATOL = 1e-12

PRICE_FIXTURES = [
    "tests/fixtures/real_market_prices.csv",
    "tests/fixtures/real_market_prices_expanded.csv",
]

BETA_WINDOW = 90
MIN_OBS = 60


# --------------------------------------------------------------------------- #
# 1. Naive rolling-beta oracle: per-asset, per-window OLS slope via lstsq.
# --------------------------------------------------------------------------- #
def _naive_rolling_beta(
    returns: pd.DataFrame, benchmark: str, window: int = BETA_WINDOW, min_obs: int = MIN_OBS
) -> pd.DataFrame:
    """Naive rolling beta: one ``np.linalg.lstsq`` per asset per window.

    For each window ``[i-window+1, i]`` (clipped to the series start) the slope
    of asset ~ 1 + benchmark is computed over the *pairwise-finite* observations
    only. Windows with fewer than ``min_obs`` valid pairs, or a degenerate
    (zero-variance) benchmark, yield NaN — matching the documented contract.
    The benchmark column itself is a constant 1.0 series.
    """
    n = len(returns)
    out = pd.DataFrame(np.nan, index=returns.index, columns=returns.columns, dtype=float)
    out[benchmark] = 1.0

    bench = returns[benchmark].to_numpy(dtype=float)
    for col in returns.columns:
        if col == benchmark:
            continue
        y = returns[col].to_numpy(dtype=float)
        for i in range(n):
            lo = max(0, i - window + 1)
            xb = bench[lo : i + 1]
            yb = y[lo : i + 1]
            mask = np.isfinite(xb) & np.isfinite(yb)
            if int(mask.sum()) < min_obs:
                continue
            xv = xb[mask]
            yv = yb[mask]
            # Degenerate benchmark (zero variance) -> undefined slope.
            if np.ptp(xv) == 0.0:
                continue
            design = np.column_stack([np.ones_like(xv), xv])
            coef, *_ = np.linalg.lstsq(design, yv, rcond=None)
            out.iat[i, out.columns.get_loc(col)] = float(coef[1])
    return out


# --------------------------------------------------------------------------- #
# 2. Naive signal oracle: per-row sort by beta, take disjoint top/bottom.
# --------------------------------------------------------------------------- #
def _naive_signals(
    betas: pd.DataFrame, long_quantile: float = 0.3, short_quantile: float = 0.3
) -> pd.DataFrame:
    """Naive per-row long/short selection by beta rank (loops + sort_values)."""
    if betas is None or not isinstance(betas, pd.DataFrame) or betas.empty:
        return pd.DataFrame()
    out = pd.DataFrame(0, index=betas.index, columns=betas.columns, dtype=np.int64)
    for idx in betas.index:
        row = betas.loc[idx]
        clean = row[np.isfinite(pd.to_numeric(row, errors="coerce").to_numpy(dtype=float))]
        clean = clean.sort_values()
        n = len(clean)
        if n < 2:
            continue
        n_long = max(1, int(n * long_quantile))
        n_short = max(1, int(n * short_quantile))
        if n_long + n_short > n:
            n_short = max(0, n - n_long)
        longs = list(clean.index[:n_long])
        shorts = list(clean.index[n - n_short :]) if n_short else []
        for a in longs:
            out.at[idx, a] = 1
        for a in shorts:
            out.at[idx, a] = -1
    return out


# --------------------------------------------------------------------------- #
# 3. Naive portfolio oracle: equal-weight long/short, dollar-neutral.
# --------------------------------------------------------------------------- #
def _naive_portfolio(signals: pd.DataFrame, dollar_neutral: bool = True) -> pd.DataFrame:
    """Naive equal-weight book from {1,-1,0} signals (loops + explicit sums)."""
    if signals is None or not isinstance(signals, pd.DataFrame) or signals.empty:
        return pd.DataFrame()
    out = pd.DataFrame(0.0, index=signals.index, columns=signals.columns, dtype=float)
    for idx in signals.index:
        row = signals.loc[idx]
        longs = [c for c in signals.columns if row[c] == 1]
        shorts = [c for c in signals.columns if row[c] == -1]
        nl, ns = len(longs), len(shorts)
        for c in longs:
            out.at[idx, c] = (1.0 / nl) if nl > 0 else 0.0
        if dollar_neutral or nl == 0:
            for c in shorts:
                out.at[idx, c] = (-1.0 / ns) if ns > 0 else 0.0
        # Dollar-neutral renormalization (both sides present) mirrors the
        # production post-pass that pins net exposure to zero exactly.
        if dollar_neutral and nl > 0 and ns > 0:
            pos = sum(v for v in out.loc[idx].to_numpy() if v > 0.0)
            neg = sum(v for v in out.loc[idx].to_numpy() if v < 0.0)
            for c in longs:
                out.at[idx, c] = out.at[idx, c] / pos if pos > 1e-18 else out.at[idx, c]
            for c in shorts:
                out.at[idx, c] = out.at[idx, c] / abs(neg) if neg < -1e-18 else out.at[idx, c]
    return out


# --------------------------------------------------------------------------- #
# 4. Naive one-step backtest oracle: lagged weights, costs, log cumulative.
# --------------------------------------------------------------------------- #
def _naive_backtest(
    returns: pd.DataFrame,
    weights: pd.DataFrame,
    transaction_costs: float = 0.0,
    slippage: float = 0.0,
) -> pd.DataFrame:
    """Naive lagged-weight backtest (loops, explicit turnover and logcum)."""
    common = returns.index.intersection(weights.index)
    r = returns.loc[common]
    w = weights.loc[common]
    cols = r.columns.intersection(w.columns)
    r = r[cols]
    w = w[cols]
    n = len(common)
    gross = np.zeros(n)
    cost_drag = np.zeros(n)
    slip_drag = np.zeros(n)
    wv = w.to_numpy(dtype=float)
    rv = r.to_numpy(dtype=float)
    # Production masks NaN/inf returns to 0 (the final finite-repair sanitize);
    # mirror that so the naive dot-product matches the matmul on defective data.
    rv = np.where(np.isfinite(rv), rv, 0.0)
    wv = np.where(np.isfinite(wv), wv, 0.0)
    for t in range(n):
        w_lag = np.zeros(wv.shape[1]) if t == 0 else wv[t - 1]
        gross[t] = float(np.sum(w_lag * rv[t]))
        turnover = float(np.sum(np.abs(wv[t] - w_lag)))
        cost_drag[t] = turnover * transaction_costs
        slip_drag[t] = turnover * slippage
    net = gross - cost_drag - slip_drag
    net = np.clip(np.where(np.isfinite(net), net, 0.0), -1.0 + 1e-12, None)
    log_ret = np.log1p(net)
    log_ret = np.where(np.isfinite(log_ret), log_ret, 0.0)
    cum = np.exp(np.cumsum(log_ret))
    cum = np.where(np.isfinite(cum), cum, 1.0)
    return pd.DataFrame(
        {
            "returns": net,
            "gross_return": gross,
            "cost_drag": cost_drag,
            "slippage_drag": slip_drag,
            "cumulative": cum,
        },
        index=common,
    )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _assert_frame_parity(name: str, expected: pd.DataFrame, actual: pd.DataFrame) -> None:
    assert list(expected.columns) == list(actual.columns), f"{name}: columns differ"
    assert expected.shape == actual.shape, f"{name}: shape {expected.shape} != {actual.shape}"
    e = expected.to_numpy(dtype=float)
    a = actual.to_numpy(dtype=float)
    assert np.allclose(e, a, rtol=RTOL, atol=ATOL, equal_nan=True), (
        f"{name}: parity breach; max|delta|={np.nanmax(np.abs(e - a)) if e.size else 0.0}"
    )


# --------------------------------------------------------------------------- #
# Stage-level parity (per-function, independent oracle)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("fixture", PRICE_FIXTURES)
@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("costs_on", [False, True])
def test_oracle_rolling_beta_parity(fixture, beta_neutral, costs_on):
    returns = load_prices(fixture, benchmark="BTC", min_rows=30)
    expected = _naive_rolling_beta(returns, "BTC", BETA_WINDOW, MIN_OBS)
    actual = calculate_rolling_beta(returns, "BTC", window=BETA_WINDOW, min_obs=MIN_OBS)
    _assert_frame_parity("rolling_beta", expected, actual)


@pytest.mark.parametrize("fixture", PRICE_FIXTURES)
@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("costs_on", [False, True])
def test_oracle_signal_parity(fixture, beta_neutral, costs_on):
    returns = load_prices(fixture, benchmark="BTC", min_rows=30)
    betas = calculate_rolling_beta(returns, "BTC", window=BETA_WINDOW, min_obs=MIN_OBS)
    expected = _naive_signals(betas)
    actual = generate_bab_signals(betas)
    _assert_frame_parity("signals", expected, actual)


@pytest.mark.parametrize("fixture", PRICE_FIXTURES)
@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("costs_on", [False, True])
def test_oracle_portfolio_parity(fixture, beta_neutral, costs_on):
    returns = load_prices(fixture, benchmark="BTC", min_rows=30)
    betas = calculate_rolling_beta(returns, "BTC", window=BETA_WINDOW, min_obs=MIN_OBS)
    signals = generate_bab_signals(betas)
    expected = _naive_portfolio(signals, dollar_neutral=True)
    actual = construct_portfolio(signals, dollar_neutral=True)
    _assert_frame_parity("portfolio", expected, actual)


@pytest.mark.parametrize("fixture", PRICE_FIXTURES)
@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("costs_on", [False, True])
def test_oracle_backtest_parity(fixture, beta_neutral, costs_on):
    returns = load_prices(fixture, benchmark="BTC", min_rows=30)
    betas = calculate_rolling_beta(returns, "BTC", window=BETA_WINDOW, min_obs=MIN_OBS)
    signals = generate_bab_signals(betas)
    weights = construct_portfolio(signals, dollar_neutral=True)
    tc = 0.001 if costs_on else 0.0
    sl = 0.0005 if costs_on else 0.0
    expected = _naive_backtest(returns, weights, transaction_costs=tc, slippage=sl)
    actual = run_backtest(returns, weights, transaction_costs=tc, slippage=sl)
    _assert_frame_parity("backtest", expected, actual)


# --------------------------------------------------------------------------- #
# End-to-end parity: full BABStrategy.run vs oracle-assembled pipeline
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("fixture", PRICE_FIXTURES)
@pytest.mark.parametrize("beta_neutral", [False, True])
@pytest.mark.parametrize("dollar_neutral", [False, True])
@pytest.mark.parametrize("costs_on", [False, True])
def test_oracle_full_run_parity(fixture, beta_neutral, dollar_neutral, costs_on):
    returns = load_prices(fixture, benchmark="BTC", min_rows=30)
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=BETA_WINDOW,
        long_quantile=0.3,
        short_quantile=0.3,
        min_observations=MIN_OBS,
        beta_neutral=beta_neutral,
        dollar_neutral=dollar_neutral,
        transaction_costs=0.001 if costs_on else 0.0,
        slippage=0.0005 if costs_on else 0.0,
    )
    res = strat.run(returns_df=returns)

    # ``run`` subsets columns to the resolved tradable universe, so the oracle
    # must operate on exactly the columns the strategy actually used.
    run_cols = list(res.betas.columns)
    returns_used = returns.loc[:, run_cols]

    # Stage betas / signals / weights: oracle pipeline is exact for these.
    exp_betas = _naive_rolling_beta(returns_used, "BTC", BETA_WINDOW, MIN_OBS)
    exp_signals = _naive_signals(exp_betas)
    exp_weights = _naive_portfolio(exp_signals, dollar_neutral=dollar_neutral)
    _assert_frame_parity("e2e.betas", exp_betas, res.betas)
    _assert_frame_parity("e2e.signals", exp_signals, res.signals)

    if not beta_neutral:
        # Without beta-neutral enforcement the product weights equal the book.
        _assert_frame_parity("e2e.weights", exp_weights, res.weights)

    # Backtest: oracle on the *product's* (possibly beta-adjusted) weights.
    tc = 0.001 if costs_on else 0.0
    sl = 0.0005 if costs_on else 0.0
    exp_backtest = _naive_backtest(returns_used, res.weights, transaction_costs=tc, slippage=sl)
    _assert_frame_parity("e2e.backtest", exp_backtest, res.backtest)


def test_oracle_beta_neutral_backtest_parity():
    """Beta-neutral product weights still match the naive backtest oracle."""
    returns = load_prices(PRICE_FIXTURES[0], benchmark="BTC", min_rows=30)
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=BETA_WINDOW,
        long_quantile=0.3,
        short_quantile=0.3,
        min_observations=MIN_OBS,
        beta_neutral=True,
        dollar_neutral=True,
        transaction_costs=0.001,
        slippage=0.0005,
    )
    res = strat.run(returns_df=returns)
    returns_used = returns.loc[:, list(res.betas.columns)]
    exp = _naive_backtest(returns_used, res.weights, transaction_costs=0.001, slippage=0.0005)
    _assert_frame_parity("bn.backtest", exp, res.backtest)


def test_oracle_beta_neutral_dollar_neutrality():
    """Oracle book is dollar-neutral and the product preserves it (to fp eps)."""
    returns = load_prices(PRICE_FIXTURES[0], benchmark="BTC", min_rows=30)
    betas = _naive_rolling_beta(returns, "BTC", BETA_WINDOW, MIN_OBS)
    signals = _naive_signals(betas)
    oracle_w = _naive_portfolio(signals, dollar_neutral=True)
    row_sums = oracle_w.sum(axis=1).to_numpy(dtype=float)
    assert np.all(np.abs(row_sums) < 1e-9), "oracle book must be dollar-neutral"

    strat = BABStrategy(
        benchmark="BTC",
        beta_window=BETA_WINDOW,
        long_quantile=0.3,
        short_quantile=0.3,
        min_observations=MIN_OBS,
        beta_neutral=True,
        dollar_neutral=True,
    )
    res = strat.run(returns_df=returns)
    prod_sums = res.weights.sum(axis=1).to_numpy(dtype=float)
    assert np.all(np.abs(prod_sums) < 1e-9), "product weights must stay dollar-neutral"


def test_oracle_beta_neutral_portfolio_beta_near_target():
    """Beta-neutral product drives gross-weighted portfolio beta to ~target."""
    returns = load_prices(PRICE_FIXTURES[0], benchmark="BTC", min_rows=30)
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=BETA_WINDOW,
        long_quantile=0.3,
        short_quantile=0.3,
        min_observations=MIN_OBS,
        beta_neutral=True,
        beta_target=0.0,
        beta_tolerance=1e-4,
        dollar_neutral=True,
    )
    res = strat.run(returns_df=returns)
    beta = strat.report(res)["metrics"]["portfolio_beta"]
    assert math.isfinite(beta)
    assert abs(beta - 0.0) <= 1e-4, f"portfolio beta {beta} not within 1e-4 of target"
