"""Coverage campaign 2: costs.py — compute_transaction_costs + helpers.

Impact term (adv as dict/Series/DataFrame, impact_coefficient=0 skip,
participation_cap clip, borrow daily_borrow>0, fixed_fee_per_trade>0,
zero-turnover, None weights/prices), TransactionCostModel validation errors,
_adv_series/_clean_frame normalization, apply_costs DataFrame/Series/None
branches, Series-return contract (no caller-stack inspection).
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.costs import (
    BABCostError,
    TransactionCostModel,
    _adv_series,
    _clean_frame,
    apply_costs,
    compute_transaction_costs,
)


def test_zero_cost_default_model():
    weights = pd.DataFrame(
        {"BTC": [0.5, -0.5], "ETH": [-0.5, 0.5]},
        index=pd.date_range("2023-01-01", periods=2, freq="D"),
    )
    costs = compute_transaction_costs(weights)
    assert isinstance(costs, pd.Series)
    assert costs.name == "transaction_costs"
    assert list(costs.index) == list(weights.index)
    assert (costs == 0.0).all()


def test_none_weights():
    out = compute_transaction_costs(None)
    assert isinstance(out, pd.Series)
    assert len(out) == 0


def test_empty_weights():
    weights = pd.DataFrame(columns=["BTC", "ETH"])
    out = compute_transaction_costs(weights)
    assert isinstance(out, pd.Series)
    assert (out == 0.0).all()


def test_zero_turnover():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.5, 0.5], "ETH": [-0.5, -0.5, -0.5]}, index=idx
    )
    costs = compute_transaction_costs(weights)
    assert (costs == 0.0).all()


def test_impact_adv_dict():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.0], "ETH": [-0.5, 0.0]}, index=idx
    )
    prices = pd.DataFrame(
        {"BTC": [40000.0, 40000.0], "ETH": [2500.0, 2500.0]}, index=idx
    )
    model = TransactionCostModel(impact_coefficient=0.0005, adv_usd={"BTC": 1e9, "ETH": 1e8})
    costs = compute_transaction_costs(weights, prices=prices, model=model)
    assert (costs > 0).any()


def test_impact_adv_series():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.0], "ETH": [-0.5, 0.0]}, index=idx
    )
    prices = pd.DataFrame(
        {"BTC": [40000.0, 40000.0], "ETH": [2500.0, 2500.0]}, index=idx
    )
    adv = pd.Series({"BTC": 1e9, "ETH": 1e8})
    model = TransactionCostModel(impact_coefficient=0.0005)
    costs = compute_transaction_costs(
        weights, weights_prev=None, prices=prices, model=model, adv_usd=adv
    )
    assert (costs > 0).any()


def test_impact_adv_dataframe():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.0], "ETH": [-0.5, 0.0]}, index=idx
    )
    prices = pd.DataFrame(
        {"BTC": [40000.0, 40000.0], "ETH": [2500.0, 2500.0]}, index=idx
    )
    adv = pd.DataFrame(
        {"BTC": [1e9, 1e9], "ETH": [1e8, 1e8]}, index=idx
    )
    model = TransactionCostModel(impact_coefficient=0.0005)
    costs = compute_transaction_costs(
        weights, weights_prev=None, prices=prices, model=model, adv_usd=adv
    )
    assert (costs > 0).any()


def test_impact_coefficient_zero_skips_impact():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.0], "ETH": [-0.5, 0.0]}, index=idx
    )
    prices = pd.DataFrame(
        {"BTC": [40000.0, 40000.0], "ETH": [2500.0, 2500.0]}, index=idx
    )
    model = TransactionCostModel(impact_coefficient=0.0, adv_usd={"BTC": 1e6})
    costs = compute_transaction_costs(weights, prices=prices, model=model)
    assert (costs >= 0).all()


def test_participation_cap_clip():
    idx = pd.date_range("2023-01-01", periods=1, freq="D")
    weights = pd.DataFrame({"BTC": [0.9]}, index=idx)
    prices = pd.DataFrame({"BTC": [40000.0]}, index=idx)
    uncapped = compute_transaction_costs(
        weights, prices=prices,
        model=TransactionCostModel(
            impact_coefficient=0.5, participation_cap=1.0, adv_usd={"BTC": 1.0}
        ),
    )
    capped = compute_transaction_costs(
        weights, prices=prices,
        model=TransactionCostModel(
            impact_coefficient=0.5, participation_cap=0.01, adv_usd={"BTC": 1.0}
        ),
    )
    assert float(capped.iloc[0]) <= float(uncapped.iloc[0])


def test_borrow_daily_borrow_gt_zero():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [-0.5, -0.5], "ETH": [0.5, 0.5]}, index=idx
    )
    model = TransactionCostModel(borrow_bps_per_year=0.10)
    costs = compute_transaction_costs(weights, model=model)
    assert (costs > 0).all()


def test_fixed_fee_per_trade_gt_zero():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.0], "ETH": [-0.5, 0.0]}, index=idx
    )
    model = TransactionCostModel(fixed_fee_per_trade=0.001)
    costs = compute_transaction_costs(weights, model=model)
    assert float(costs.iloc[0]) > 0.0
    assert float(costs.iloc[1]) == 0.0  # zero turnover period


def test_none_prices():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame(
        {"BTC": [0.5, 0.0], "ETH": [-0.5, 0.0]}, index=idx
    )
    model = TransactionCostModel(
        linear_fee=0.001, borrow_bps_per_year=0.0,
        impact_coefficient=0.0005, adv_usd={"BTC": 1e6}
    )
    costs = compute_transaction_costs(weights, prices=None, model=model)
    assert (costs >= 0).all()
    assert float(costs.iloc[0]) == pytest.approx(0.0015)
    assert float(costs.iloc[1]) == 0.0


def test_validation_errors():
    with pytest.raises(BABCostError):
        TransactionCostModel(linear_fee=-0.01)
    with pytest.raises(BABCostError):
        TransactionCostModel(participation_cap=0.0)
    with pytest.raises(BABCostError):
        TransactionCostModel(participation_cap=1.5)
    with pytest.raises(BABCostError):
        TransactionCostModel(trading_days_per_year=0)
    with pytest.raises(BABCostError):
        TransactionCostModel(linear_fee=True)  # bool rejected


def test_frozen_model_cannot_mutate():
    model = TransactionCostModel()
    with pytest.raises(AttributeError):
        model.linear_fee = 0.05


def test_adv_series_none():
    assert _adv_series(None) is None


def test_adv_series_dict_series_dataframe():
    assert isinstance(_adv_series({"BTC": 1e9}), pd.Series)
    assert isinstance(_adv_series(pd.Series({"BTC": 1e9})), pd.Series)
    assert isinstance(_adv_series(pd.DataFrame({"BTC": [1e9]})), pd.DataFrame)


def test_clean_frame_none_empty_inf():
    assert _clean_frame(None) is None
    assert _clean_frame(pd.DataFrame()) is None
    df = pd.DataFrame({"BTC": [1.0, np.inf, -np.inf, np.nan]})
    cleaned = _clean_frame(df)
    assert cleaned is not None
    assert not np.isinf(cleaned["BTC"]).any()


def test_apply_costs_series():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    returns = pd.Series([0.01, 0.02, -0.01], index=idx)
    tc = pd.Series([0.001, 0.001, 0.001], index=idx, name="transaction_costs")
    out = apply_costs(returns, transaction_costs=tc)
    expected = returns - tc
    pd.testing.assert_series_equal(out, expected)


def test_apply_costs_dataframe_portfolio_return_column():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    returns = pd.DataFrame(
        {"portfolio_return": [0.01, 0.02, -0.01], "BTC": [0.0, 0.0, 0.0]},
        index=idx,
    )
    tc = pd.Series([0.001, 0.001, 0.001], index=idx)
    out = apply_costs(returns, transaction_costs=tc)
    assert out["portfolio_return"].iloc[0] == pytest.approx(0.009)


def test_apply_costs_dataframe_single_column():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    returns = pd.DataFrame({"x": [0.01, 0.02]}, index=idx)
    tc = pd.Series([0.001, 0.001], index=idx)
    out = apply_costs(returns, transaction_costs=tc)
    assert out["x"].iloc[0] == pytest.approx(0.009)


def test_apply_costs_none_weights_computes_tc():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    returns = pd.Series([0.01, 0.02], index=idx)
    weights = pd.DataFrame({"BTC": [0.5, 0.0]}, index=idx)
    out = apply_costs(returns, weights=weights)
    assert len(out) == 2


def test_apply_costs_none_transaction_costs_zeros():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    returns = pd.Series([0.01, 0.02], index=idx)
    out = apply_costs(returns)
    pd.testing.assert_series_equal(out, returns)


def test_series_return_contract_no_stack_inspection():
    idx = pd.date_range("2023-01-01", periods=2, freq="D")
    weights = pd.DataFrame({"BTC": [0.5, 0.0]}, index=idx)
    out = compute_transaction_costs(weights)
    assert isinstance(out, pd.Series)
    assert out.name == "transaction_costs"
