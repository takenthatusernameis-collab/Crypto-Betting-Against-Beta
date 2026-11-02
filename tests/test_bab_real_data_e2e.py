"""Real-data end-to-end integration tests for BAB strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices

FIXTURE_PRICES = "tests/fixtures/real_market_prices.csv"


def _dollar_neutral(weights: pd.DataFrame, tol: float = 1e-9) -> bool:
    """Return True if each row's weights sum to ~0 (dollar-neutral)."""
    row_sums = weights.sum(axis=1)
    return bool(np.all(np.isfinite(row_sums)) and np.all(np.abs(row_sums) < tol))


def test_real_data_e2e_finite_cumulative_and_dollar_neutral():
    """End-to-end: real price CSV -> returns -> BABStrategy.run -> finite cumulative + dollar-neutral."""
    returns_df = load_prices(FIXTURE_PRICES, benchmark="BTC", min_rows=30)

    strat = BABStrategy(
        benchmark="BTC",
        beta_window=90,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.001,
    )
    result = strat.run(returns_df=returns_df)

    cum = result.backtest["cumulative"]
    assert np.all(np.isfinite(cum)), "cumulative returns must be finite"
    final_cum = float(cum.iloc[-1])
    assert np.isfinite(final_cum), "final cumulative must be finite"

    weights = result.weights
    assert _dollar_neutral(weights), "portfolio must be dollar-neutral (weights sum to 0)"

    assert len(result.backtest) > 0, "backtest must produce rows"


def test_real_data_expanded_e2e():
    """Same end-to-end on the expanded fixture with a delisted column."""
    returns_df = load_prices(
        "tests/fixtures/real_market_prices_expanded.csv",
        benchmark="BTC",
        min_rows=30,
    )

    strat = BABStrategy(
        benchmark="BTC",
        beta_window=60,
        long_quantile=0.3,
        short_quantile=0.3,
    )
    result = strat.run(returns_df=returns_df)

    cum = result.backtest["cumulative"]
    assert np.all(np.isfinite(cum)), "cumulative returns must be finite"
    assert np.isfinite(float(cum.iloc[-1])), "final cumulative must be finite"

    assert _dollar_neutral(result.weights), "portfolio must be dollar-neutral"


def test_real_data_e2e_different_quantiles():
    """Real-data E2E with asymmetric quantiles still finite and dollar-neutral."""
    returns_df = load_prices(FIXTURE_PRICES, benchmark="BTC", min_rows=30)

    strat = BABStrategy(
        benchmark="BTC",
        beta_window=90,
        long_quantile=0.2,
        short_quantile=0.4,
        transaction_costs=0.0005,
    )
    result = strat.run(returns_df=returns_df)

    assert np.all(np.isfinite(result.backtest["cumulative"]))
    assert _dollar_neutral(result.weights)
