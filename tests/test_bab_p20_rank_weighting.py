"""P20 WP2 — faithful Frazzini-Pedersen rank weighting (opt-in).

The repository is named ``Crypto-Betting-Against-Beta``. WP1 made the default
book beta-neutral, but construction is still equal-weight +/-1.0 per leg. WP2
adds an opt-in ``weighting="rank"`` path: assets are ranked by beta, extreme
ranks receive larger weight, and each leg is scaled by ``1/beta_leg`` so the
long leg carries beta +1 and the short leg beta -1. The book is beta-neutral
by construction and is NOT dollar-neutral; net exposure is funded by cash /
borrow.

Default ``weighting="equal"`` is unchanged (byte-identical). Rank is opt-in
only and is NOT promoted to the default (promotion requires WP3 OOS evidence).

The fixture is a deterministic synthetic random walk, not real market data.
Nothing here is evidence of real profitability.
"""

from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.strategy as strategy_mod
from strategies.betting_against_beta import BABStrategy, metrics
from strategies.betting_against_beta.config import BABConfig, BABConfigError
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import (
    construct_portfolio,
    construct_rank_weights,
)

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")

COLUMNS = ["A", "B", "C", "D"]
HAND_BETAS = pd.DataFrame(
    {c: [b] for c, b in zip(COLUMNS, [0.5, 0.8, 1.2, 1.6])},
    index=pd.date_range("2023-01-01", periods=1),
)
HAND_SIGNALS = pd.DataFrame(
    {"A": [1], "B": [1], "C": [-1], "D": [-1]},
    index=HAND_BETAS.index,
)

# Exact outputs of the rank algorithm on the 4-asset hand example:
# ranks [1, 2, 3, 4], m = 2.5 -> d = [3/4, 1/4], e = [1/4, 3/4],
# beta_L = 23/40, beta_H = 3/2.
EXPECTED_WEIGHTS = {
    "A": float(Fraction(30, 23)),
    "B": float(Fraction(10, 23)),
    "C": float(Fraction(-1, 6)),
    "D": float(Fraction(-1, 2)),
}
EXPECTED_NET_DOLLARS = float(Fraction(74, 69))  # 1/beta_L - 1/beta_H = 40/23 - 2/3


def _model_beta(result):
    weights = result.weights
    betas = result.betas.reindex(columns=weights.columns).fillna(0.0)
    return (weights * betas).sum(axis=1)


def _leg_betas(result):
    """Un-normalized leg beta sums: long leg -> +1, short leg -> -1 in rank."""
    weights = result.weights
    betas = result.betas.reindex(columns=weights.columns).fillna(0.0)
    weighted = weights * betas
    long_beta = weighted.where(weights > 0).sum(axis=1)
    short_beta = weighted.where(weights < 0).sum(axis=1)
    return long_beta, short_beta


def _run_rank(prices, **kwargs):
    cfg = dict(
        benchmark="BTC",
        beta_window=90,
        min_observations=60,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.001,
        weighting="rank",
    )
    cfg.update(kwargs)
    strat = BABStrategy(**cfg)
    return strat, strat.run(returns_df=prices)


def _run_equal(prices, **kwargs):
    cfg = dict(
        benchmark="BTC",
        beta_window=90,
        min_observations=60,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.001,
        weighting="equal",
    )
    cfg.update(kwargs)
    strat = BABStrategy(**cfg)
    return strat, strat.run(returns_df=prices)


def test_hand_computed_four_asset_rank_weights():
    weights = construct_rank_weights(HAND_SIGNALS, HAND_BETAS)
    assert isinstance(weights, pd.DataFrame)
    assert list(weights.columns) == COLUMNS
    row = weights.iloc[0]
    for col, expected in EXPECTED_WEIGHTS.items():
        assert float(row[col]) == pytest.approx(expected, abs=1e-12)
    # Leg betas: long leg +1, short leg -1, total beta 0, net dollars 74/69.
    betas = HAND_BETAS.reindex(columns=weights.columns).fillna(0.0)
    wb = (weights * betas).sum(axis=1).iloc[0]
    long_beta = float((weights.where(weights > 0) * betas).sum(axis=1).iloc[0])
    short_beta = float((weights.where(weights < 0) * betas).sum(axis=1).iloc[0])
    assert long_beta == pytest.approx(1.0, abs=1e-12)
    assert short_beta == pytest.approx(-1.0, abs=1e-12)
    assert wb == pytest.approx(0.0, abs=1e-12)
    assert float(weights.sum(axis=1).iloc[0]) == pytest.approx(EXPECTED_NET_DOLLARS, abs=1e-12)


@pytest.mark.parametrize("freq", ["weekly", "monthly"])
def test_rank_book_is_beta_neutral_on_rebalance_rows(prices, freq):
    _, result = _run_rank(prices, rebalance_freq=freq)
    weights = result.weights
    mask = strategy_mod._rebalance_mask(weights.index, freq)
    assert int(mask.sum()) > 1
    assert int(mask.sum()) < len(mask)
    # Model beta is exactly zero (to floating noise) on rebalance rows.
    assert float(_model_beta(result)[mask].abs().max()) <= 1e-12
    # Frozen-hold identity between rebalance dates.
    held = weights.where(mask).ffill().fillna(0)
    pd.testing.assert_frame_equal(weights.loc[~mask], held.loc[~mask], check_exact=True)


def test_rank_beats_equal_on_leg_beta_scaling(prices):
    _, rank_result = _run_rank(prices, rebalance_freq="weekly")
    _, equal_result = _run_equal(prices, rebalance_freq="weekly")
    mask = strategy_mod._rebalance_mask(rank_result.weights.index, "weekly")
    rank_long, rank_short = _leg_betas(rank_result)
    # Only rebalance rows with a non-flat book have defined leg betas (warmup
    # rows are flat because betas are NaN and no asset is eligible).
    active = mask & (rank_result.weights.abs().sum(axis=1) > 0)
    assert int(active.sum()) > 0
    assert float((rank_long[active] - 1.0).abs().max()) <= 1e-12
    assert float((rank_short[active] - (-1.0)).abs().max()) <= 1e-12
    eq_mask = strategy_mod._rebalance_mask(equal_result.weights.index, "weekly")
    eq_active = eq_mask & (equal_result.weights.abs().sum(axis=1) > 0)
    eq_long, _eq_short = _leg_betas(equal_result)
    assert int(eq_active.sum()) > 0
    # Equal-weight legs are not beta-scaled: leg beta deviates from +1.
    assert float((eq_long[eq_active] - 1.0).abs().max()) > 1e-6


def test_equal_weight_path_byte_identical(prices):
    _, explicit_equal = _run_equal(prices)
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=90,
        min_observations=60,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.001,
    )
    _, plain_default = strat, strat.run(returns_df=prices)
    pd.testing.assert_frame_equal(
        explicit_equal.weights, plain_default.weights, check_exact=True
    )
    assert float(explicit_equal.backtest["cumulative"].iloc[-1]) == pytest.approx(
        float(plain_default.backtest["cumulative"].iloc[-1]), abs=1e-12
    )


def test_rank_degenerate_rows_are_flat():
    index = pd.date_range("2023-01-01", periods=3)
    signals = pd.DataFrame(
        {"A": [1, 1, 1], "B": [-1, -1, -1]}, index=index, columns=["A", "B"]
    )
    # Row 0: non-finite betas -> flat. Row 1: all beta <= 0 -> flat.
    # Row 2: valid -> non-trivial rank weights.
    betas = pd.DataFrame(
        {
            "A": [np.inf, -1.0, 0.5],
            "B": [np.nan, -2.0, 1.6],
        },
        index=index,
        columns=["A", "B"],
    )
    weights = construct_rank_weights(signals, betas)
    assert weights.shape == (3, 2)
    assert (weights.iloc[0] == 0.0).all()
    assert (weights.iloc[1] == 0.0).all()
    # Empty long leg (all signals short) -> flat row, never raises.
    sig_short_only = pd.DataFrame({"A": [-1], "B": [-1]}, index=index[:1])
    assert (construct_rank_weights(sig_short_only, betas.iloc[:1]) == 0.0).all().all()
    # Empty signals frame -> empty frame, never raises.
    assert construct_rank_weights(
        pd.DataFrame(columns=["A", "B"]), pd.DataFrame(columns=["A", "B"])
    ).empty


def test_rank_no_lookahead():
    index = pd.date_range("2023-01-01", periods=10)
    betas = pd.DataFrame(
        {
            "A": np.linspace(0.5, 0.9, 10),
            "B": np.linspace(0.8, 1.1, 10),
            "C": np.linspace(1.2, 1.5, 10),
            "D": np.linspace(1.6, 1.9, 10),
        },
        index=index,
        columns=COLUMNS,
    )
    signals = pd.DataFrame(
        {
            "A": [1] * 10,
            "B": [1] * 10,
            "C": [-1] * 10,
            "D": [-1] * 10,
        },
        index=index,
        columns=COLUMNS,
    )
    full = construct_rank_weights(signals, betas)
    t = 5
    trunc = construct_rank_weights(signals.iloc[: t + 1], betas.iloc[: t + 1])
    pd.testing.assert_series_equal(full.iloc[t], trunc.iloc[-1], check_exact=True)


def test_invalid_weighting_surfaces():
    with pytest.raises(BABConfigError):
        BABConfig(weighting="bogus")
    idx = pd.date_range("2023-01-01", periods=2)
    sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=idx)
    bet = pd.DataFrame({"A": [0.5, 1.2], "B": [1.6, 0.8]}, index=idx)
    with pytest.raises(BABDataError):
        construct_portfolio(sig, weighting="bogus", betas=bet)


def test_construct_rank_weights_input_guards():
    """None / non-DataFrame / empty inputs return an empty frame, never raise."""
    idx = pd.date_range("2023-01-01", periods=1)
    sig = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
    bet = pd.DataFrame({"A": [0.5], "B": [1.5]}, index=idx)
    assert construct_rank_weights(None, bet).empty
    assert construct_rank_weights(sig, None).empty
    assert construct_rank_weights([1, -1], bet).empty
    assert construct_rank_weights(sig, [0.5, 1.5]).empty
    assert construct_rank_weights(pd.DataFrame(), bet).empty
    assert construct_rank_weights(sig, pd.DataFrame()).empty


def test_construct_rank_weights_non_numeric_signals_and_degenerate_rows():
    idx = pd.date_range("2023-01-01", periods=2)
    # Row 0: string signals exercise the non-numeric coercion path.
    # Row 1: a leg whose ranks average to the mean -> zero summed score -> flat.
    signals = pd.DataFrame(
        {"A": ["1", 1], "B": ["-1", -1], "C": ["1", 1]},
        index=idx,
        columns=["A", "B", "C"],
    )
    betas = pd.DataFrame(
        {"A": [0.5, 0.5], "B": [1.6, 0.9], "C": [0.8, 1.6]},
        index=idx,
        columns=["A", "B", "C"],
    )
    weights = construct_rank_weights(signals, betas)
    assert weights.shape == (2, 3)
    # Row 0: strings coerced to +1/+1/-1 -> non-trivial rank book.
    assert weights.iloc[0].abs().sum() > 0.0
    # Row 1: longs at ranks 1 and 3 average to the mean (m = 2), so the
    # long-leg score sums to zero and the documented contract is a flat row.
    assert (weights.iloc[1] == 0.0).all()


def test_dry_run_rank_book_freezes_in_rebalance_windows(prices):
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=90,
        min_observations=60,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=0.001,
        weighting="rank",
        rebalance_freq="weekly",
    )
    summary = strat.dry_run(returns_df=prices)
    assert "portfolio_risk" in summary
    assert summary["config"]["rebalance_freq"] == "weekly"
    assert np.isfinite(summary["portfolio_risk"]["gross_exposure"]["mean"])


@pytest.fixture(scope="module")
def prices():
    return load_prices(REAL, benchmark="BTC")
