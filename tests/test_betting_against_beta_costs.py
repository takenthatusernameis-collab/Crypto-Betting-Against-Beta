"""Transaction cost model tests (TDD): failing-first suite for `costs.py`.

Covers the P2 transaction-cost item:
  * linear fee + bid-ask on turnover
  * square-root market impact scaled by ADV/liquidity (participation cap)
  * short borrow costs annualized, charged pro-rata per day on short notional
  * wiring into `run_backtest`: costs reduce cumulative vs zero-cost and scale
    with turnover; no NaN/inf leakage; deterministic.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.backtest import run_backtest
from strategies.betting_against_beta.costs import (
    BABCostError,
    TransactionCostModel,
    compute_transaction_costs,
)


class TestTransactionCostModelValidation:
    def test_negative_linear_fee_raises(self):
        with pytest.raises(BABCostError):
            TransactionCostModel(linear_fee=-0.001)

    def test_negative_bid_ask_raises(self):
        with pytest.raises(BABCostError):
            TransactionCostModel(bid_ask_bps=-1.0)

    def test_negative_impact_coefficient_raises(self):
        with pytest.raises(BABCostError):
            TransactionCostModel(impact_coefficient=-0.0001)

    def test_negative_borrow_raises(self):
        with pytest.raises(BABCostError):
            TransactionCostModel(borrow_bps_per_year=-0.01)

    def test_participation_cap_out_of_range_raises(self):
        with pytest.raises(BABCostError):
            TransactionCostModel(participation_cap=0.0)
        with pytest.raises(BABCostError):
            TransactionCostModel(participation_cap=1.5)

    def test_defaults_are_valid_and_non_negative(self):
        model = TransactionCostModel()
        assert model.linear_fee >= 0
        assert model.bid_ask_bps >= 0
        assert model.impact_coefficient >= 0
        assert model.borrow_bps_per_year >= 0
        assert 0 < model.participation_cap <= 1

    def test_freeze_prevents_mutation(self):
        model = TransactionCostModel()
        with pytest.raises(AttributeError):
            model.linear_fee = 0.005


class TestComputeTransactionCosts:
    def test_flat_weights_zero_cost(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        # Long-only flat book: no trades after day 0, no shorts -> zero cost
        # after day 0 (no borrow on longs).
        weights = pd.DataFrame({"A": [0.5] * 5, "B": [0.5] * 5}, index=idx)
        prices = pd.DataFrame({"A": [100.0] * 5, "B": [100.0] * 5}, index=idx)
        model = TransactionCostModel()
        prev = weights.shift(1).fillna(0.0)
        costs = compute_transaction_costs(weights, prev, prices, model)
        # Day 0 trades from zero into the book; later periods are flat.
        assert np.isclose(costs.iloc[1:].sum(), 0.0)
        assert np.isfinite(costs).all()
        assert (costs >= 0).all()

    def test_costs_scale_linearly_with_turnover(self):
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 4}, index=idx)
        model = TransactionCostModel(linear_fee=0.001, bid_ask_bps=0.0, impact_coefficient=0.0, borrow_bps_per_year=0.0)
        w_small = pd.DataFrame({"A": [0.1, 0.0, 0.0, 0.0]}, index=idx)
        w_big = pd.DataFrame({"A": [0.2, 0.0, 0.0, 0.0]}, index=idx)
        prev = pd.DataFrame(0.0, index=idx, columns=["A"])
        c_small = compute_transaction_costs(w_small, prev, prices, model).iloc[0]
        c_big = compute_transaction_costs(w_big, prev, prices, model).iloc[0]
        assert c_big > c_small > 0
        assert np.isclose(c_big, 2 * c_small)

    def test_sqrt_impact_is_sublinear_in_trade_size(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 2}, index=idx)
        adv = {"A": 1_000_000.0}
        model = TransactionCostModel(
            linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.01,
            borrow_bps_per_year=0.0, participation_cap=1.0,
        )
        prev = pd.DataFrame(0.0, index=idx, columns=["A"])
        w_small = pd.DataFrame({"A": [0.1, 0.0]}, index=idx)  # $10k on $1M ADV -> 1% participation
        w_big = pd.DataFrame({"A": [0.4, 0.0]}, index=idx)  # $40k -> 4% participation
        c_small = compute_transaction_costs(w_small, prev, prices, model, adv_usd=adv).iloc[0]
        c_big = compute_transaction_costs(w_big, prev, prices, model, adv_usd=adv).iloc[0]
        # Sqrt impact: total cost grows as size^1.5, so impact per unit notional
        # at 4x participation must be exactly 2x (sqrt(4)).
        assert c_big > c_small > 0
        rate_small = c_small / 0.1
        rate_big = c_big / 0.4
        assert np.isclose(rate_big, 2.0 * rate_small)

    def test_impact_respects_participation_cap(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 2}, index=idx)
        adv = {"A": 1_000.0}  # tiny ADV -> huge participation, must be capped
        model = TransactionCostModel(
            linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.01,
            borrow_bps_per_year=0.0, participation_cap=0.10,
        )
        prev = pd.DataFrame(0.0, index=idx, columns=["A"])
        w_big = pd.DataFrame({"A": [0.9, 0.0]}, index=idx)  # $90k vs $1k ADV -> capped
        costs = compute_transaction_costs(w_big, prev, prices, model, adv_usd=adv)
        assert np.isfinite(costs).all()
        assert costs.iloc[0] > 0

    def test_missing_adv_skips_impact_but_charges_linear(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 2}, index=idx)
        model = TransactionCostModel(linear_fee=0.001, impact_coefficient=0.05)
        prev = pd.DataFrame(0.0, index=idx, columns=["A"])
        w = pd.DataFrame({"A": [0.5, 0.0]}, index=idx)
        costs = compute_transaction_costs(w, prev, prices, model)  # no adv
        assert costs.iloc[0] > 0  # linear fee still applies
        assert np.isfinite(costs).all()

    def test_borrow_charged_on_shorts_only(self):
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 3, "B": [100.0] * 3}, index=idx)
        model = TransactionCostModel(
            linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.0,
            borrow_bps_per_year=0.0252,  # ~0.01% per day at 252 days
        )
        prev = pd.DataFrame(0.0, index=idx, columns=["A", "B"])
        w_long_only = pd.DataFrame({"A": [0.5, 0.5, 0.5], "B": [0.0, 0.0, 0.0]}, index=idx)
        w_short = pd.DataFrame({"A": [0.0, 0.0, 0.0], "B": [-0.5, -0.5, -0.5]}, index=idx)
        c_long = compute_transaction_costs(w_long_only, prev, prices, model)
        c_short = compute_transaction_costs(w_short, prev, prices, model)
        assert np.isclose(c_long.sum(), 0.0)  # no borrow on longs
        expected_daily = 0.5 * 0.0252 / 252
        assert np.allclose(c_short.to_numpy().flatten(), expected_daily)

    def test_borrow_scales_with_short_notional(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 2}, index=idx)
        model = TransactionCostModel(borrow_bps_per_year=0.0252)
        prev = pd.DataFrame(0.0, index=idx, columns=["A"])
        w_small = pd.DataFrame({"A": [-0.1, -0.1]}, index=idx)
        w_big = pd.DataFrame({"A": [-0.5, -0.5]}, index=idx)
        c_small = compute_transaction_costs(w_small, prev, prices, model).iloc[0]
        c_big = compute_transaction_costs(w_big, prev, prices, model).iloc[0]
        assert np.isclose(c_big, 5 * c_small)

    def test_non_finite_weights_coerced_no_leakage(self):
        idx = pd.date_range("2023-01-01", periods=3, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 3}, index=idx)
        model = TransactionCostModel(linear_fee=0.001)
        prev = pd.DataFrame({"A": [0.0, np.nan, 0.0]}, index=idx)
        w = pd.DataFrame({"A": [0.5, np.inf, 0.5]}, index=idx)
        costs = compute_transaction_costs(w, prev, prices, model)
        assert np.isfinite(costs).all()

    def test_unknown_asset_no_price_skips_impact_still_charges_turnover(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 2}, index=idx)  # B has no price
        model = TransactionCostModel(linear_fee=0.001, impact_coefficient=0.01)
        prev = pd.DataFrame(0.0, index=idx, columns=["A", "B"])
        w = pd.DataFrame({"A": [0.0, 0.0], "B": [0.5, 0.0]}, index=idx)
        costs = compute_transaction_costs(w, prev, prices, model, adv_usd={"B": 1_000_000.0})
        assert costs.iloc[0] > 0  # linear fee on B's turnover
        assert np.isfinite(costs).all()

    def test_empty_input_returns_empty(self):
        weights = pd.DataFrame()
        prev = pd.DataFrame()
        prices = pd.DataFrame()
        model = TransactionCostModel()
        costs = compute_transaction_costs(weights, prev, prices, model)
        assert costs.empty


class TestCostsWiredIntoBacktest:
    def test_cost_model_reduces_cumulative_vs_zero_cost(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        returns = pd.DataFrame({"A": [0.01] * 10, "B": [-0.01] * 10}, index=idx)
        weights = pd.DataFrame(
            {"A": [0.5, 0.4] * 5, "B": [-0.5, -0.4] * 5}, index=idx
        )
        prices = pd.DataFrame({"A": [100.0] * 10, "B": [100.0] * 10}, index=idx)
        model = TransactionCostModel(linear_fee=0.001, bid_ask_bps=0.0005)
        free = run_backtest(returns, weights)
        costly = run_backtest(returns, weights, cost_model=model, prices_df=prices)
        assert costly["cumulative"].iloc[-1] < free["cumulative"].iloc[-1]
        assert np.isfinite(costly["cumulative"]).all()

    def test_costs_scale_with_turnover_in_backtest(self):
        idx = pd.date_range("2023-01-01", periods=8, freq="D")
        returns = pd.DataFrame({"A": [0.01] * 8}, index=idx)
        prices = pd.DataFrame({"A": [100.0] * 8}, index=idx)
        model = TransactionCostModel(linear_fee=0.002)
        w_low = pd.DataFrame({"A": [0.5] * 8}, index=idx)  # no turnover after day 0
        w_high = pd.DataFrame({"A": [1.0, 0.0] * 4}, index=idx)  # turnover every day
        free = run_backtest(returns, w_low)
        low = run_backtest(returns, w_low, cost_model=model, prices_df=prices)
        high = run_backtest(returns, w_high, cost_model=model, prices_df=prices)
        assert high["cumulative"].iloc[-1] < low["cumulative"].iloc[-1] <= free["cumulative"].iloc[-1]

    def test_costs_reduce_every_period_with_turnover(self):
        idx = pd.date_range("2023-01-01", periods=4, freq="D")
        returns = pd.DataFrame({"A": [0.05, 0.05, 0.05, 0.05]}, index=idx)
        weights = pd.DataFrame({"A": [1.0, 0.0, 1.0, 0.0]}, index=idx)
        prices = pd.DataFrame({"A": [100.0] * 4}, index=idx)
        model = TransactionCostModel(linear_fee=0.001)
        res = run_backtest(returns, weights, cost_model=model, prices_df=prices)
        # Day 0: weight goes 0 -> 1 (after shift, day-0 portfolio return uses zero weights anyway);
        # costs apply to weight changes from day 0 onward.
        assert np.isfinite(res["returns"]).all()
        assert np.isfinite(res["cumulative"]).all()


class TestCostsDeterminismAndEdgeCases:
    def test_deterministic_repeat_call(self):
        idx = pd.date_range("2023-01-01", periods=5, freq="D")
        prices = pd.DataFrame({"A": [100.0] * 5}, index=idx)
        model = TransactionCostModel(linear_fee=0.001, impact_coefficient=0.01)
        prev = pd.DataFrame(0.0, index=idx, columns=["A"])
        w = pd.DataFrame({"A": [0.25, -0.25, 0.25, -0.25, 0.25]}, index=idx)
        adv = {"A": 500_000.0}
        c1 = compute_transaction_costs(w, prev, prices, model, adv_usd=adv)
        c2 = compute_transaction_costs(w, prev, prices, model, adv_usd=adv)
        pd.testing.assert_series_equal(c1, c2)

    def test_single_asset_no_columns(self):
        idx = pd.date_range("2023-01-01", periods=2, freq="D")
        model = TransactionCostModel()
        costs = compute_transaction_costs(
            pd.DataFrame(index=idx), pd.DataFrame(index=idx),
            pd.DataFrame(index=idx), model,
        )
        assert costs.empty or len(costs) == 2
        assert np.isfinite(costs).all()
