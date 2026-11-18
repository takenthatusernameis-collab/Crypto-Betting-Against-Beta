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

# Wide synthetic cross-section: the committed 9-asset fixture is rank-flat
# under the WP2b guards (see docs/BAB_FIDELITY.md §9.1), so the rank
# invariants are proved on a universe with genuine beta dispersion.
WIDE_ASSETS = 40
WIDE_UNIVERSE = [f"A{i:02d}" for i in range(WIDE_ASSETS)]


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


def test_rank_flat_when_leg_beta_below_floor():
    """A leg too weak to invert is flattened, never rescaled."""
    idx = pd.date_range("2023-01-01", periods=1)
    signals = pd.DataFrame({"L": [1], "H": [-1]}, index=idx)
    betas = pd.DataFrame({"L": [0.05], "H": [1.5]}, index=idx)
    flat = construct_rank_weights(signals, betas)
    assert (flat.iloc[0] == 0.0).all()
    active = construct_rank_weights(signals, betas, min_leg_beta=0.01, max_gross=100.0)
    row = active.iloc[0]
    assert float(row["L"]) == pytest.approx(1.0 / 0.05, abs=1e-12)
    assert float(row["H"]) == pytest.approx(-1.0 / 1.5, abs=1e-12)
    assert float(row["L"] * 0.05) == pytest.approx(1.0, abs=1e-12)
    assert float(row["H"] * 1.5) == pytest.approx(-1.0, abs=1e-12)


def test_rank_flat_when_gross_exceeds_cap():
    """A row over the gross cap is flattened at the cap, never rescaled."""
    idx = pd.date_range("2023-01-01", periods=1)
    signals = pd.DataFrame({"L": [1], "H": [-1]}, index=idx)
    betas = pd.DataFrame({"L": [0.10], "H": [2.0]}, index=idx)
    capped = construct_rank_weights(signals, betas, min_leg_beta=0.05, max_gross=4.0)
    assert (capped.iloc[0] == 0.0).all()
    active = construct_rank_weights(signals, betas, min_leg_beta=0.05, max_gross=12.0)
    row = active.iloc[0]
    assert float(row["L"]) == pytest.approx(10.0, abs=1e-12)
    assert float(row["H"]) == pytest.approx(-0.5, abs=1e-12)
    assert float(row.abs().sum()) <= 12.0
    assert float(row["L"] * 0.10) == pytest.approx(1.0, abs=1e-12)
    assert float(row["H"] * 2.0) == pytest.approx(-1.0, abs=1e-12)


@pytest.mark.parametrize("freq", ["weekly", "monthly"])
def test_rank_book_is_beta_neutral_on_rebalance_rows(wide_returns, freq):
    """Rank invariant proved on a wide cross-section (fixture is rank-flat)."""
    _, result = _run_rank(
        wide_returns, rebalance_freq=freq, universe=WIDE_UNIVERSE
    )
    weights = result.weights
    mask = strategy_mod._rebalance_mask(weights.index, freq)
    assert int(mask.sum()) > 1
    assert int(mask.sum()) < len(mask)
    # Model beta is exactly zero (to floating noise) on rebalance rows.
    assert float(_model_beta(result)[mask].abs().max()) <= 1e-12
    # Frozen-hold identity between rebalance dates.
    held = weights.where(mask).ffill().fillna(0)
    pd.testing.assert_frame_equal(weights.loc[~mask], held.loc[~mask], check_exact=True)


def test_rank_beats_equal_on_leg_beta_scaling(wide_returns):
    """Rank legs are ±1 on a wide universe; equal legs are not."""
    _, rank_result = _run_rank(
        wide_returns, rebalance_freq="weekly", universe=WIDE_UNIVERSE
    )
    _, equal_result = _run_equal(
        wide_returns, rebalance_freq="weekly", universe=WIDE_UNIVERSE
    )
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


@pytest.mark.parametrize("freq", ["daily", "weekly", "monthly"])
def test_fixture_rank_is_flat_under_guard(prices, freq):
    """The 9-asset fixture cannot evaluate rank; the guard flattens every row."""
    _, result = _run_rank(prices, rebalance_freq=freq)
    assert float(result.weights.abs().to_numpy().sum()) == 0.0
    assert float(result.backtest["cumulative"].iloc[-1]) == pytest.approx(1.0, abs=1e-12)
    assert float(result.backtest["returns"].abs().max()) == 0.0


@pytest.mark.parametrize("value", [0, 1.5, "x", True, float("nan")])
def test_rank_min_leg_beta_config_validation(value):
    with pytest.raises(BABConfigError):
        BABConfig(rank_min_leg_beta=value)


@pytest.mark.parametrize("value", [0.5, 1000, "x", True, float("nan")])
def test_rank_max_gross_config_validation(value):
    with pytest.raises(BABConfigError):
        BABConfig(rank_max_gross=value)


def test_rank_guard_direct_validation_and_equal_ignores_them():
    idx = pd.date_range("2023-01-01", periods=1)
    sig = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
    bet = pd.DataFrame({"A": [0.5], "B": [1.5]}, index=idx)
    with pytest.raises(BABDataError):
        construct_portfolio(sig, weighting="rank", betas=bet, rank_min_leg_beta=0)
    with pytest.raises(BABDataError):
        construct_portfolio(sig, weighting="rank", betas=bet, rank_max_gross=0.5)
    # The equal branch must remain byte-identical and ignore rank-only valves.
    equal = construct_portfolio(
        sig,
        weighting="equal",
        betas=bet,
        rank_min_leg_beta=0,
        rank_max_gross=0.5,
    )
    assert not equal.empty


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


@pytest.fixture(scope="module")
def wide_returns():
    """Deterministic 40-asset return panel with true betas 0.35 ... 1.90."""
    rng = np.random.default_rng(7)
    n_days = 220
    index = pd.date_range("2024-01-01", periods=n_days, freq="B")
    benchmark = rng.normal(0.0, 0.01, n_days)
    data = {}
    for i in range(WIDE_ASSETS):
        true_beta = 0.35 + 1.55 * i / (WIDE_ASSETS - 1)
        data[f"A{i:02d}"] = true_beta * benchmark + rng.normal(0.0, 0.004, n_days)
    data["BTC"] = benchmark
    return pd.DataFrame(data, index=index)
