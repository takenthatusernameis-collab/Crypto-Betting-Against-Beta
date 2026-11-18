"""P20 WP1 — the default book must actually be Betting Against Beta.

The repository is named ``Crypto-Betting-Against-Beta``. Before WP1 the shipped
default was dollar-neutral only: book beta measured ``-0.572`` (q=0.3) and
``-0.908`` (q=0.2) on the committed fixture, i.e. the strategy was net short the
market, not beta-neutral. WP1 flips ``BABConfig.beta_neutral`` to ``True`` and
freezes the corrected book inside weekly/monthly rebalance windows.

Measurement provenance (2026-11-18, ``tests/fixtures/real_market_prices.csv``,
398 rows, 10 bps costs, ``beta_window=90``, ``min_observations=60``):

* daily model beta ``max|sum_i w_i beta_i|`` observed <= 2.2e-04 across the six
  ``beta_window x quantile`` points -> gate ``<= 1e-3`` (the correction aborts at
  its ``beta_tolerance=1e-4`` default, so a tighter gate is infeasible);
* realized (OLS) strategy beta observed <= +0.121 -> grid gate ``<= 0.15`` and
  ``<= 0.07`` for the ``w in {90, 120}`` subset;
* weekly/monthly frozen books hold their weights byte-identically between
  rebalance dates and are beta-neutral *on rebalance rows only* — betas drift
  while the book is held, which is the intended behaviour;
* explicit ``beta_neutral=False`` reproduces the pre-WP1 numbers exactly.

The fixture is a deterministic synthetic random walk, not real market data.
Nothing here is evidence of real profitability.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.strategy as strategy_mod
from strategies.betting_against_beta import BABStrategy, metrics
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.portfolio import enforce_beta_neutrality

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")
EXP = str(REPO / "tests" / "fixtures" / "real_market_prices_expanded.csv")

DAILY_GRID = [(window, q) for window in (60, 90, 120) for q in (0.2, 0.3)]


@pytest.fixture(scope="module")
def prices():
    return load_prices(REAL, benchmark="BTC")


def _run(prices, *, window=90, q=0.3, beta_neutral=True, rebalance_freq="daily", **kwargs):
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=window,
        min_observations=60,
        long_quantile=q,
        short_quantile=q,
        transaction_costs=0.001,
        rebalance_freq=rebalance_freq,
        beta_neutral=beta_neutral,
        **kwargs,
    )
    return strat, strat.run(returns_df=prices)


def _model_beta(result):
    weights = result.weights
    betas = result.betas.reindex(columns=weights.columns).fillna(0.0)
    return (weights * betas).sum(axis=1)


def _dollar_sums(result):
    return result.weights.sum(axis=1).abs()


def test_default_config_is_beta_neutral():
    assert BABConfig().beta_neutral is True


def test_legacy_opt_out_book_is_beta_blind(prices):
    _, legacy = _run(prices, beta_neutral=False)
    assert float(_model_beta(legacy).abs().max()) > 0.5
    assert metrics.strategy_beta(legacy.backtest["returns"], prices["BTC"]) < -0.5


@pytest.mark.parametrize("window,q", DAILY_GRID)
def test_daily_default_book_is_beta_neutral(prices, window, q):
    _, result = _run(prices, window=window, q=q)

    assert float(_model_beta(result).abs().max()) <= 1e-3
    assert float(_dollar_sums(result).max()) <= 1e-9

    realized = metrics.strategy_beta(result.backtest["returns"], prices["BTC"])
    assert abs(realized) <= 0.15
    if window in (90, 120):
        assert abs(realized) <= 0.07


@pytest.mark.parametrize("freq", ["weekly", "monthly"])
def test_rebalance_windows_freeze_the_corrected_book(prices, freq):
    _strat, result = _run(prices, rebalance_freq=freq)
    weights = result.weights
    mask = strategy_mod._rebalance_mask(weights.index, freq)

    assert int(mask.sum()) > 1
    assert int(mask.sum()) < len(mask)
    held = weights.where(mask).ffill().fillna(0)
    pd.testing.assert_frame_equal(weights.loc[~mask], held.loc[~mask], check_exact=True)

    assert float(_model_beta(result)[mask].abs().max()) <= 1e-3
    assert float(_dollar_sums(result).max()) <= 1e-9


def test_opt_out_reproduces_pre_wp1_numbers(prices):
    _, legacy_03 = _run(prices, q=0.3, beta_neutral=False)
    _, legacy_02 = _run(prices, q=0.2, beta_neutral=False)

    wealth_03 = float(legacy_03.backtest["cumulative"].iloc[-1])
    wealth_02 = float(legacy_02.backtest["cumulative"].iloc[-1])
    assert wealth_03 == pytest.approx(0.31357452508222267, abs=1e-12)
    assert metrics.sharpe_ratio(legacy_03.backtest["returns"]) == pytest.approx(
        -1.4184443260935686, abs=1e-12
    )
    assert wealth_02 == pytest.approx(0.42144602011674975, abs=1e-12)
    assert metrics.sharpe_ratio(legacy_02.backtest["returns"]) == pytest.approx(
        -0.6804279949431549, abs=1e-12
    )


@pytest.mark.parametrize(
    "fixture,benchmark,golden",
    [
        (REAL, "BTC", 0.45632700835934265),
        (EXP, "BTC", 0.5311665101149625),
        (REAL, "ETH", 2.1986969529723432),
    ],
)
def test_opt_out_matches_campaign17_goldens(fixture, benchmark, golden):
    returns = load_prices(fixture, benchmark=benchmark)
    strat = BABStrategy(
        benchmark=benchmark,
        beta_window=252,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.001,
        beta_neutral=False,
    )
    result = strat.run(returns_df=returns)
    assert float(result.backtest["cumulative"].iloc[-1]) == pytest.approx(golden, abs=1e-12)


def _exact_beta_frame(n_days=220, seed=3):
    rng = np.random.default_rng(seed)
    index = pd.date_range("2023-01-01", periods=n_days, freq="D")
    benchmark = rng.normal(0.0, 0.02, n_days)
    return pd.DataFrame(
        {
            "BTC": benchmark,
            "A": 0.5 * benchmark,
            "B": 0.8 * benchmark,
            "C": 1.2 * benchmark,
            "D": 1.6 * benchmark,
        },
        index=index,
    )


def test_synthetic_frame_exact_neutrality_with_zero_tolerance():
    frame = _exact_beta_frame()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.0,
        beta_neutral=True,
        beta_tolerance=0.0,
    )
    result = strat.run(returns_df=frame)

    latest = result.betas.iloc[-1]
    assert latest["A"] == pytest.approx(0.5, abs=1e-12)
    assert latest["B"] == pytest.approx(0.8, abs=1e-12)
    assert latest["C"] == pytest.approx(1.2, abs=1e-12)
    assert latest["D"] == pytest.approx(1.6, abs=1e-12)
    assert float(_model_beta(result).abs().max()) <= 1e-9
    assert float(_dollar_sums(result).max()) <= 1e-12


def test_synthetic_frame_default_tolerance_is_within_gate():
    frame = _exact_beta_frame()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.0,
        beta_neutral=True,
    )
    result = strat.run(returns_df=frame)
    assert float(_model_beta(result).abs().max()) <= 1e-3


def test_correction_helper_keeps_dollar_neutrality():
    index = pd.date_range("2024-01-01", periods=3, freq="D")
    columns = ["A", "B", "C", "D"]
    weights = pd.DataFrame(
        [[0.5, 0.5, -0.5, -0.5], [-0.25, 0.75, 0.25, -0.75], [0.0, 0.0, 0.0, 0.0]],
        index=index,
        columns=columns,
    )
    betas = pd.DataFrame(
        [[0.5, 0.8, 1.2, 1.6]] * 3,
        index=index,
        columns=columns,
    )
    corrected = enforce_beta_neutrality(weights, betas, tolerance=0.0, correction=True)
    assert np.allclose(corrected.sum(axis=1).to_numpy(), 0.0, atol=1e-12)
    assert np.allclose((corrected * betas).sum(axis=1).to_numpy(), 0.0, atol=1e-9)
