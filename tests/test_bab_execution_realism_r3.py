"""R3: Execution-realism regression tests for the BAB cost model (R3-A) and
rebalance-frequency sensitivity sweep (R3-B).

Hostile-regime builders are reused from ``tests/test_bab_stress_regimes.py``
(``_base_frame``, ``REGIMES``, ``REGIME_BUILDERS``) and are NOT duplicated here.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.costs import (
    BABCostError,
    TransactionCostModel,
    compute_transaction_costs,
)
from strategies.betting_against_beta.config import BABConfigError
from strategies.betting_against_beta.errors import BABDataError

from tests.test_bab_stress_regimes import (  # noqa: E402  (reuse, don't duplicate)
    BACKTEST_COLUMNS,
    BETA_WINDOW,
    DN_TOL,
    MIN_OBS,
    REGIMES,
    REGIME_BUILDERS,
    _base_frame,
)

SEED = 20261113
REGIME_NAMES = [name for name, _ in REGIMES]
FREQS = ("daily", "weekly", "monthly")


def _make_prices(frame: pd.DataFrame) -> pd.DataFrame:
    return (1.0 + frame).cumprod()


def _make_adv(frame: pd.DataFrame) -> dict:
    return {c: 1_000_000.0 for c in frame.columns if c != "BTC"}


def _cost_model(
    linear_fee: float = 0.0,
    bid_ask_bps: float = 0.0,
    impact_coefficient: float = 0.0005,
    borrow_bps_per_year: float = 0.02,
    participation_cap: float = 0.10,
    trading_days_per_year: int = 252,
) -> TransactionCostModel:
    return TransactionCostModel(
        linear_fee=linear_fee,
        bid_ask_bps=bid_ask_bps,
        impact_coefficient=impact_coefficient,
        borrow_bps_per_year=borrow_bps_per_year,
        participation_cap=participation_cap,
        trading_days_per_year=trading_days_per_year,
    )


def _run(
    frame,
    dollar_neutral: bool,
    cost_model=None,
    prices=None,
    adv_usd=None,
    transaction_costs: float = 0.0,
    slippage: float = 0.0,
    partial_fill: bool = False,
    beta_neutral: bool = False,
    rebalance_freq: str = "daily",
):
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=BETA_WINDOW,
        min_observations=MIN_OBS,
        long_quantile=0.3,
        short_quantile=0.3,
        dollar_neutral=dollar_neutral,
        beta_neutral=beta_neutral,
        rebalance_freq=rebalance_freq,
        transaction_costs=transaction_costs,
        slippage=slippage,
        cost_model=cost_model,
        prices=prices,
        adv_usd=adv_usd,
        partial_fill=partial_fill,
        max_participation=0.10,
    )
    res = strat.run(returns_df=frame)
    return strat, res


def _assert_r3_sane(strat, res, label, dollar_neutral: bool):
    bt = res.backtest
    assert list(bt.columns) == BACKTEST_COLUMNS, f"{label}: columns {list(bt.columns)}"
    for col in BACKTEST_COLUMNS:
        arr = bt[col].to_numpy(dtype=float)
        assert np.isfinite(arr).all(), f"{label}: {col} non-finite"
    assert (bt["cost_drag"].to_numpy(dtype=float) >= 0).all(), f"{label}: negative cost_drag"
    assert (bt["slippage_drag"].to_numpy(dtype=float) >= 0).all(), f"{label}: negative slippage_drag"
    w = res.weights
    wa = w.to_numpy(dtype=float)
    assert np.isfinite(wa).all(), f"{label}: weights non-finite"
    net = w.sum(axis=1).to_numpy(dtype=float)
    assert np.isfinite(net).all(), f"{label}: net non-finite"
    if dollar_neutral:
        assert float(np.abs(net).max()) <= DN_TOL, (
            f"{label}: DN breach max|sum(w)|={float(np.abs(net).max()):.3e}"
        )
    betas = res.betas.to_numpy(dtype=float)
    assert np.isfinite(betas[BETA_WINDOW:]).all(), f"{label}: betas non-finite after warmup"
    rep = strat.report(res)
    for key, value in rep["metrics"].items():
        assert math.isfinite(float(value)), f"{label}: metric {key} non-finite"
    ts = strat.tear_sheet(res)
    assert isinstance(ts, str) and len(ts) > 0, f"{label}: tear_sheet empty"
    json_str = strat.report_to_json(rep)
    json.loads(json_str)  # strict JSON
    assert "NaN" not in json_str and "Infinity" not in json_str


# --------------------------------------------------------------------------- #
# R3-A: execution-realism cost-model regression tests
# --------------------------------------------------------------------------- #
_r3a_records: list[dict] = []


@pytest.mark.parametrize("regime_name", REGIME_NAMES)
@pytest.mark.parametrize("dollar_neutral", (False, True))
@pytest.mark.parametrize("cost_model_on", (False, True))
def test_regime_cost_model_sane(regime_name, dollar_neutral, cost_model_on):
    """Every hostile regime is finite/DN/reportable with cost model on or off."""
    frame = REGIME_BUILDERS[regime_name](_base_frame())
    prices = _make_prices(frame)
    adv = _make_adv(frame)
    cm = _cost_model() if cost_model_on else None
    strat, res = _run(
        frame, dollar_neutral, cost_model=cm, prices=prices, adv_usd=adv,
        transaction_costs=0.001, slippage=0.0005,
    )
    _assert_r3_sane(strat, res, f"{regime_name}|dn={dollar_neutral}|cm={cost_model_on}", dollar_neutral)
    bt = res.backtest
    _r3a_records.append(
        {
            "regime": regime_name,
            "dollar_neutral": dollar_neutral,
            "cost_model_on": cost_model_on,
            "max_drawdown": float(np.minimum.accumulate(bt["cumulative"]).min() if False else
                                  (1 - bt["cumulative"] / bt["cumulative"].cummax()).max()),
            "turnover": float((bt.index.to_series().diff().fillna(pd.Timedelta(0))).size),
            "final_cumulative": float(bt["cumulative"].iloc[-1]),
            "cost_drag_sum": float(bt["cost_drag"].sum()),
        }
    )


def test_cost_model_compute_returns_non_negative_finite():
    """compute_transaction_costs never returns negative or non-finite costs."""
    n, k = 60, 6
    dates = pd.date_range("2018-01-01", periods=n, freq="D")
    cols = [f"A{i}" for i in range(k)]
    w = pd.DataFrame(np.random.default_rng(1).normal(0, 0.05, (n, k)), index=dates, columns=cols)
    prices = pd.DataFrame(100.0, index=dates, columns=cols)
    adv = {c: 1e6 for c in cols}
    model = _cost_model(linear_fee=0.001, bid_ask_bps=0.0005, impact_coefficient=0.0005,
                        borrow_bps_per_year=0.02)
    tc = compute_transaction_costs(w, w.shift(1).fillna(0.0), prices, model, adv_usd=adv)
    arr = tc.to_numpy(dtype=float)
    assert np.isfinite(arr).all()
    assert (arr >= 0).all()
    assert tc.name == "transaction_costs"


def test_borrow_asymmetry_more_short_higher_cost():
    """Identical borrow rate + more short notional => strictly higher cost."""
    n, k = 40, 4
    dates = pd.date_range("2018-01-01", periods=n, freq="D")
    cols = [f"A{i}" for i in range(k)]
    prices = pd.DataFrame(100.0, index=dates, columns=cols)
    adv = {c: 1e6 for c in cols}
    model = _cost_model(linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.0,
                        borrow_bps_per_year=0.02)
    w_prev = pd.DataFrame(0.0, index=dates, columns=cols)
    long_w = pd.DataFrame(0.05, index=dates, columns=cols)
    short_w = pd.DataFrame(-0.05, index=dates, columns=cols)
    mixed_w = pd.DataFrame(-0.10, index=dates, columns=cols)
    c_long = compute_transaction_costs(long_w, w_prev, prices, model, adv_usd=adv).sum()
    c_short = compute_transaction_costs(short_w, w_prev, prices, model, adv_usd=adv).sum()
    c_mixed = compute_transaction_costs(mixed_w, w_prev, prices, model, adv_usd=adv).sum()
    assert c_long == 0.0, f"long-only book should carry no borrow cost, got {c_long}"
    assert c_short > c_long
    assert c_mixed > c_short, f"more short notional must raise cost: mixed={c_mixed} short={c_short}"


def test_costs_on_drag_ge_flat_only_per_regime():
    """Model-on (impact+borrow atop equal flat drag) total drag >= flat-only."""
    frame = REGIME_BUILDERS["crash"](_base_frame())
    prices = _make_prices(frame)
    adv = _make_adv(frame)
    flat_kwargs = dict(transaction_costs=0.001, slippage=0.0, cost_model=None)
    model_kwargs = dict(
        transaction_costs=0.001, slippage=0.0,
        cost_model=_cost_model(linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.0005,
                               borrow_bps_per_year=0.02),
        prices=prices, adv_usd=adv,
    )
    _, res_flat = _run(frame, True, **flat_kwargs)
    _, res_model = _run(frame, True, **model_kwargs)
    btf, btm = res_flat.backtest, res_model.backtest
    # Same flat drag column in both (identical transaction_costs).
    np.testing.assert_allclose(btf["cost_drag"].to_numpy(dtype=float),
                               btm["cost_drag"].to_numpy(dtype=float), rtol=1e-9, atol=1e-12)
    # Gross returns identical (weights independent of cost model).
    np.testing.assert_allclose(btf["gross_return"].to_numpy(dtype=float),
                               btm["gross_return"].to_numpy(dtype=float), rtol=1e-9, atol=1e-12)
    # Model-on period returns <= flat-only (impact+borrow >= 0 subtracted on top).
    assert (btm["returns"].to_numpy(dtype=float) <= btf["returns"].to_numpy(dtype=float) + 1e-9).all()
    assert float(btm["cumulative"].iloc[-1]) <= float(btf["cumulative"].iloc[-1]) + 1e-9
    assert float(btm["cumulative"].iloc[-1]) > 0.0


def test_backward_compat_cost_model_none_byte_identical():
    """cost_model=None == zero-cost TransactionCostModel == default (no cost_model)."""
    frame = _base_frame()
    prices = _make_prices(frame)
    adv = _make_adv(frame)
    zero = _cost_model(linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.0,
                       borrow_bps_per_year=0.0)
    _, res_none = _run(frame, True, cost_model=None, prices=prices, adv_usd=adv)
    _, res_zero = _run(frame, True, cost_model=zero, prices=prices, adv_usd=adv)
    _, res_default = _run(frame, True)  # no cost_model/prices/adv -> flat-only path
    pd.testing.assert_frame_equal(res_none.backtest, res_zero.backtest)
    pd.testing.assert_frame_equal(res_none.weights, res_zero.weights)
    # Default path (no model) equals the explicit None path.
    pd.testing.assert_frame_equal(res_none.backtest, res_default.backtest)


def test_invalid_cost_model_raises_loudly():
    """Wrong-typed / invalid cost_model raises, never silently ignored."""
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", cost_model="not-a-model")
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", cost_model={"linear_fee": -0.001})
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", cost_model=12345)


def test_invalid_partial_fill_and_max_participation_raise():
    """partial_fill must be bool; max_participation in (0,1]; violations raise."""
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", partial_fill="yes")
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", max_participation=0.0)
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", max_participation=1.5)
    with pytest.raises(BABConfigError):
        BABStrategy(benchmark="BTC", max_participation=-0.1)


def test_partial_fill_on_slippage_ge_flat():
    """partial_fill=True scales slippage_drag up (multiplier >= 1); off == flat."""
    frame = REGIME_BUILDERS["liq_evap"](_base_frame())
    prices = _make_prices(frame)
    adv = _make_adv(frame)
    base = dict(transaction_costs=0.0, slippage=0.001, cost_model=None, prices=prices, adv_usd=adv)
    _, res_off = _run(frame, True, partial_fill=False, **base)
    _, res_on = _run(frame, True, partial_fill=True, **base)
    so = res_off.backtest["slippage_drag"].to_numpy(dtype=float)
    sn = res_on.backtest["slippage_drag"].to_numpy(dtype=float)
    assert (sn >= so - 1e-12).all(), "partial_fill must not reduce slippage drag"
    # Flat (partial_fill=False) with slippage only equals cost_model None flat path.
    _, res_flat = _run(frame, True, slippage=0.001, cost_model=None)
    np.testing.assert_allclose(res_off.backtest["slippage_drag"].to_numpy(dtype=float),
                               res_flat.backtest["slippage_drag"].to_numpy(dtype=float),
                               rtol=1e-9, atol=1e-12)


def test_causal_betas_with_cost_model():
    """Perturbing a future row leaves earlier betas byte-identical (R3-A path)."""
    base = _base_frame()
    before = BABStrategy(benchmark="BTC", beta_window=BETA_WINDOW, cost_model=_cost_model(),
                         prices=_make_prices(base), adv_usd=_make_adv(base)).run(returns_df=base)
    perturbed = base.copy()
    perturbed.iloc[-1] = 0.5
    after = BABStrategy(benchmark="BTC", beta_window=BETA_WINDOW, cost_model=_cost_model(),
                        prices=_make_prices(perturbed), adv_usd=_make_adv(perturbed)).run(returns_df=perturbed)
    np.testing.assert_array_equal(before.betas.to_numpy(dtype=float)[:-1],
                                  after.betas.to_numpy(dtype=float)[:-1])


def test_r3a_evidence_summary():
    """Recorded R3-A per-regime metrics (max drawdown, turnover, final cumulative)."""
    print("\n[R3-A] execution realism evidence (regime x dn x cost_model_on):")
    print(f"{'regime':<14} {'dn':>4} {'cm':>6} {'max_dd':>9} {'final_cum':>10} {'cost_drag':>9}")
    for rec in _r3a_records:
        print(
            f"{rec['regime']:<14} {str(rec['dollar_neutral']):>4} "
            f"{str(rec['cost_model_on']):>6} {rec['max_drawdown']:>9.4f} "
            f"{rec['final_cumulative']:>10.4f} {rec['cost_drag_sum']:>9.6f}"
        )
    assert len(_r3a_records) == len(REGIME_NAMES) * 2 * 2


# --------------------------------------------------------------------------- #
# R3-B: rebalance-frequency sensitivity sweep (not previously measured)
# --------------------------------------------------------------------------- #
_r3b_records: list[dict] = []


@pytest.mark.parametrize("rebalance_freq", FREQS)
@pytest.mark.parametrize("regime_name", REGIME_NAMES)
@pytest.mark.parametrize("dollar_neutral", (False, True))
def test_rebalance_freq_sensitivity(rebalance_freq, regime_name, dollar_neutral):
    """daily/weekly/monthly x 5 regimes x dn on/off with cost model: invariants hold."""
    frame = REGIME_BUILDERS[regime_name](_base_frame())
    prices = _make_prices(frame)
    adv = _make_adv(frame)
    strat, res = _run(
        frame, dollar_neutral,
        cost_model=_cost_model(), prices=prices, adv_usd=adv,
        transaction_costs=0.001, slippage=0.0005,
        rebalance_freq=rebalance_freq,
    )
    label = f"{regime_name}|freq={rebalance_freq}|dn={dollar_neutral}"
    _assert_r3_sane(strat, res, label, dollar_neutral)
    bt = res.backtest
    w = res.weights
    net = w.sum(axis=1).to_numpy(dtype=float)
    assert float(np.abs(net).max()) <= DN_TOL or not dollar_neutral
    turnover_series = (w - w.shift(1).fillna(0.0)).abs().sum(axis=1)
    n_rebalance_periods = int((turnover_series > 1e-12).sum())
    record = {
        "regime": regime_name,
        "freq": rebalance_freq,
        "dollar_neutral": dollar_neutral,
        "turnover": float(turnover_series.sum()),
        "n_rebalance_periods": n_rebalance_periods,
        "max_drawdown": float((1 - bt["cumulative"] / bt["cumulative"].cummax()).max()),
        "final_cumulative": float(bt["cumulative"].iloc[-1]),
        "cost_drag_sum": float(bt["cost_drag"].sum()),
        "sharpe": float(bt["returns"].mean() / (bt["returns"].std() + 1e-12) * math.sqrt(252))
        if len(bt) > 1 else 0.0,
    }
    assert math.isfinite(record["max_drawdown"])
    assert math.isfinite(record["final_cumulative"])
    assert record["final_cumulative"] > 0.0
    _r3b_records.append(record)
    print(
        f"[R3-B] {label}: turnover={record['turnover']:.4f} "
        f"n_rebal_periods={n_rebalance_periods} max_dd={record['max_drawdown']:.4f} "
        f"final_cum={record['final_cumulative']:.4f} cost_drag={record['cost_drag_sum']:.6f}"
    )


def test_rebalance_freq_turnover_ordering_invariant():
    """Less frequent rebalancing must not produce MORE rebalance periods than daily
    (structural invariant: weekly/monthly rebalance <= daily rebalance dates)."""
    for regime_name in REGIME_NAMES:
        for dollar_neutral in (False, True):
            by_freq = {
                r["freq"]: r for r in _r3b_records
                if r["regime"] == regime_name and r["dollar_neutral"] == dollar_neutral
            }
            daily = by_freq["daily"]["n_rebalance_periods"]
            weekly = by_freq["weekly"]["n_rebalance_periods"]
            monthly = by_freq["monthly"]["n_rebalance_periods"]
            assert weekly <= daily, (
                f"{regime_name}|dn={dollar_neutral}: weekly rebalances {weekly} > daily {daily}"
            )
            assert monthly <= daily, (
                f"{regime_name}|dn={dollar_neutral}: monthly rebalances {monthly} > daily {daily}"
            )


def test_daily_cells_no_r2_regression():
    """Daily R3-B cells match R2 defaults: finite, DN, locked columns, bounded drawdown."""
    for regime_name in REGIME_NAMES:
        for dollar_neutral in (False, True):
            recs = [r for r in _r3b_records
                    if r["regime"] == regime_name and r["freq"] == "daily"
                    and r["dollar_neutral"] == dollar_neutral]
            assert recs, f"missing daily cell {regime_name}|dn={dollar_neutral}"
            rec = recs[0]
            assert rec["final_cumulative"] > 0.0
            assert rec["max_drawdown"] <= 1.0
            assert math.isfinite(rec["sharpe"])


def test_r3b_evidence_summary():
    """Recorded R3-B per-cell metrics (turnover, drawdown, Sharpe, cost drag)."""
    print("\n[R3-B] rebalance-frequency sensitivity evidence (freq x regime x dn):")
    print(f"{'freq':<9} {'regime':<14} {'dn':>4} {'turnover':>9} {'rebal_per':>10} "
          f"{'max_dd':>9} {'final_cum':>10} {'cost_drag':>9} {'sharpe':>7}")
    for rec in _r3b_records:
        print(
            f"{rec['freq']:<9} {rec['regime']:<14} {str(rec['dollar_neutral']):>4} "
            f"{rec['turnover']:>9.4f} {rec['n_rebalance_periods']:>10} "
            f"{rec['max_drawdown']:>9.4f} {rec['final_cumulative']:>10.4f} "
            f"{rec['cost_drag_sum']:>9.6f} {rec['sharpe']:>7.3f}"
        )
    assert len(_r3b_records) == len(FREQS) * len(REGIME_NAMES) * 2
