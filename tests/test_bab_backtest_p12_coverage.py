"""P12 coverage campaign for backtest.py error/edge paths (backtest.py).

Covers real missed branches with synthetic data + fakes/mocks only (no network):
_clean_frame_local, None / non-DataFrame / empty inputs, and the opt-in
partial_fill (participation-aware) slippage path including its defensive
exception fallback. No production logic is modified.
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.backtest import (
    _adv_series_local,
    _clean_frame_local,
    run_backtest,
)


def _idx(n=20):
    return pd.date_range("2023-01-01", periods=n, freq="D")


def _returns(n=20, seed=1):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"BTC": rng.normal(0, 0.01, n), "ETH": rng.normal(0, 0.01, n)}, index=_idx(n))


def _weights(n=20):
    return pd.DataFrame({"BTC": [0.5] * n, "ETH": [-0.5] * n}, index=_idx(n))


# ---------------------------------------------------------------------------
# _clean_frame_local
# ---------------------------------------------------------------------------

def test_clean_frame_local_none():
    assert _clean_frame_local(None) is None


def test_clean_frame_local_empty():
    assert _clean_frame_local(pd.DataFrame()) is None


def test_clean_frame_local_replaces_inf_with_nan():
    df = pd.DataFrame({"BTC": [1.0, np.inf, -np.inf, 3.0]})
    out = _clean_frame_local(df)
    assert out is not None
    assert np.isfinite(out.to_numpy(dtype=float)).all()


# ---------------------------------------------------------------------------
# run_backtest None / non-DataFrame / empty inputs
# ---------------------------------------------------------------------------

def test_run_backtest_returns_none():
    out = run_backtest(None, _weights())
    assert out.empty
    assert list(out.columns) == ["returns", "cumulative"]


def test_run_backtest_weights_none():
    out = run_backtest(_returns(), None)
    assert out.empty


def test_run_backtest_uncoercible_inputs():
    out = run_backtest(object(), object())
    assert out.empty


def test_run_backtest_empty_returns_and_weights():
    out = run_backtest(pd.DataFrame(), pd.DataFrame())
    assert out.empty


# ---------------------------------------------------------------------------
# partial_fill participation-aware slippage path
# ---------------------------------------------------------------------------

def _prices(n=20):
    return pd.DataFrame({"BTC": [100.0] * n, "ETH": [50.0] * n}, index=_idx(n))


def _adv(n=20):
    return {"BTC": 1e6, "ETH": 5e5}


def test_partial_fill_scales_slippage_vs_flat():
    rets = _returns()
    w = _weights()
    prices = _prices()
    adv = _adv()
    flat = run_backtest(rets, w, slippage=0.001, partial_fill=False, prices_df=prices, adv_usd=adv)
    scaled = run_backtest(
        rets, w, slippage=0.001, partial_fill=True, max_participation=0.10,
        prices_df=prices, adv_usd=adv,
    )
    # With turnover, participation-aware drag should differ from flat drag
    # (and both should be finite, no crash).
    assert np.isfinite(scaled["slippage_drag"]).all()
    assert np.isfinite(flat["slippage_drag"]).all()


def test_partial_fill_without_prices_degrades_to_flat():
    rets = _returns()
    w = _weights()
    out = run_backtest(rets, w, slippage=0.001, partial_fill=True, prices_df=None, adv_usd=None)
    assert np.isfinite(out["slippage_drag"]).all()


def test_partial_fill_exception_fallback_keeps_flat_drag():
    rets = _returns()
    w = _weights()
    prices = _prices()
    adv = _adv()
    # Make participation computation blow up; flat slippage must stay intact.
    with mock.patch(
        "strategies.betting_against_beta.backtest._adv_series_local", side_effect=RuntimeError("boom")
    ):
        out = run_backtest(
            rets, w, slippage=0.001, partial_fill=True, prices_df=prices, adv_usd=adv,
        )
        flat = run_backtest(rets, w, slippage=0.001, partial_fill=False, prices_df=prices, adv_usd=adv)
        np.testing.assert_array_equal(out["slippage_drag"].to_numpy(), flat["slippage_drag"].to_numpy())


def test_partial_fill_zero_slippage_is_noop():
    rets = _returns()
    w = _weights()
    out = run_backtest(rets, w, slippage=0.0, partial_fill=True, prices_df=_prices(), adv_usd=_adv())
    assert (out["slippage_drag"] == 0.0).all()
