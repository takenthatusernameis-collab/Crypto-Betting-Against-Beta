"""P14-C: beta.py + backtest.py coverage push.

Targets the HANDOFF.md P14-C missed lines:
  beta.py  : calculate_beta_fast inner/outer TypeError/ValueError/AttributeError
             handlers (216-219); calculate_rolling_beta outer fallback rebuild
             (544-558).
  backtest : _adv_series_local Series/DataFrame/fallback branches (17-21);
             run_backtest partial_fill DataFrame-ADV alignment path (163).

beta.py lines 125, 150-151, 163, 170-171, 189, 435-436 are unreachable under
normal inputs (dead exception/ordering paths: BABDataError subclasses ValueError
and is swallowed by the earlier handler; _finalize_betas is always invoked with
a 2-D array). They are noted as such and do not block the per-module target.

Fakes/monkeypatches only — no network, no credentials.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.backtest import _adv_series_local, run_backtest
from strategies.betting_against_beta.data_loader import BABDataError


class _ListGetItemRaisesAttrError(pd.DataFrame):
    """DataFrame whose ``__getitem__`` raises AttributeError for list keys."""

    def __getitem__(self, key):
        if isinstance(key, list):
            raise AttributeError("list key access blocked")
        return super().__getitem__(key)


# ---------------------------------------------------------------------------
# beta.py: calculate_beta_fast inner/outer exception handlers (216-219)
# ---------------------------------------------------------------------------
def test_calculate_beta_fast_inner_valueerror_handler(monkeypatch):
    def fake_lstsq(X, y, rcond=None):
        raise ValueError("singular fit")

    monkeypatch.setattr(np.linalg, "lstsq", fake_lstsq)
    a = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    b = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    assert np.isnan(beta.calculate_beta_fast(a, b))


def test_calculate_beta_fast_outer_valueerror_handler(monkeypatch):
    def fake_column_stack(arrays):
        raise ValueError("blocked column stack")

    monkeypatch.setattr(np, "column_stack", fake_column_stack)
    a = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    b = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    assert np.isnan(beta.calculate_beta_fast(a, b))


# ---------------------------------------------------------------------------
# beta.py: calculate_rolling_beta outer fallback rebuild (544-558)
# ---------------------------------------------------------------------------
def test_calculate_rolling_beta_outer_fallback_rebuild():
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    rng = np.random.default_rng(7)
    df = _ListGetItemRaisesAttrError(
        {
            "BTC": rng.normal(0, 0.01, 120),
            "ETH": rng.normal(0, 0.01, 120),
        },
        index=idx,
    )
    out = beta.calculate_rolling_beta(df, "BTC", window=60, min_obs=30)
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ["BTC", "ETH"]
    assert (out["BTC"] == 1.0).all()


# ---------------------------------------------------------------------------
# backtest.py: _adv_series_local branches (17-21)
# ---------------------------------------------------------------------------
def test_adv_series_local_series_and_dataframe_and_fallback():
    s = pd.Series({"BTC": 1e6, "ETH": 2e6})
    out = _adv_series_local(s)
    assert isinstance(out, pd.Series)
    assert out["BTC"] == 1e6

    df = pd.DataFrame({"BTC": [1e6], "ETH": [2e6]})
    out = _adv_series_local(df)
    assert isinstance(out, pd.DataFrame)
    assert out["BTC"].iloc[0] == 1e6

    # Fallback: not None/dict/Series/DataFrame -> None (line 21)
    assert _adv_series_local([1, 2, 3]) is None  # type: ignore[arg-type]
    assert _adv_series_local(123) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# backtest.py: run_backtest partial_fill DataFrame-ADV path (163)
# ---------------------------------------------------------------------------
def test_run_backtest_partial_fill_dataframe_adv():
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    returns = pd.DataFrame(
        {
            "BTC": [0.01, 0.02, -0.01, 0.03, 0.01, -0.02],
            "ETH": [0.02, -0.01, 0.01, 0.02, -0.02, 0.01],
        },
        index=idx,
    )
    weights = pd.DataFrame(
        {
            "BTC": [0.5, -0.5, 0.5, -0.5, 0.5, -0.5],
            "ETH": [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5],
        },
        index=idx,
    )
    prices = pd.DataFrame(
        {
            "BTC": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
            "ETH": [50.0, 51.0, 52.0, 53.0, 54.0, 55.0],
        },
        index=idx,
    )
    adv = pd.DataFrame({"BTC": [1e6] * 6, "ETH": [1e6] * 6}, index=idx)
    res = run_backtest(
        returns,
        weights,
        partial_fill=True,
        slippage=0.001,
        prices_df=prices,
        adv_usd=adv,
    )
    assert isinstance(res, pd.DataFrame)
    assert "cumulative" in res.columns
    assert len(res) == 6
    assert float(res["cumulative"].iloc[-1]) > 0.0
