"""Coverage campaign 4 — strategy.py defensive finiteness passes (lines 379-385).

Targets the second (extra) finiteness guard after the first in-place clean.
Production-realistic intent: upstream components may yield non-finite values;
strategy.py must never surface NaN/inf weights.
"""

from __future__ import annotations

import numpy as _np
import pandas as pd
import pytest

import strategies.betting_against_beta.strategy as strategy_mod
from strategies.betting_against_beta.strategy import BABStrategy


def _base_returns(n: int = 80, seed: int = 7) -> pd.DataFrame:
    rng = _np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    btc = rng.normal(0.001, 0.02, n)
    return pd.DataFrame(
        {
            "BTC": btc,
            "ETH": btc * 1.1 + rng.normal(0, 0.01, n),
            "SOL": btc * 1.3 + rng.normal(0, 0.015, n),
            "ADA": btc * 0.8 + rng.normal(0, 0.012, n),
            "XRP": rng.normal(0.0005, 0.018, n),
        },
        index=dates,
    )


class _SecondPassNonFiniteFrame(pd.DataFrame):
    """DataFrame that reports non-finite on the second to_numpy(float) call."""

    _metadata = ["_to_numpy_calls"]

    @property
    def _constructor(self):
        return _SecondPassNonFiniteFrame

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_to_numpy_calls", 0)

    def to_numpy(self, dtype=None, copy=False, na_value=_np.nan):
        if dtype is float or dtype is _np.float64:
            n = object.__getattribute__(self, "_to_numpy_calls")
            object.__setattr__(self, "_to_numpy_calls", n + 1)
            arr = super().to_numpy(dtype=dtype, copy=True, na_value=na_value)
            if n == 0:
                arr = arr.copy()
                arr.flat[0] = _np.nan
                return arr
            if n == 1:
                arr = arr.copy()
                arr.flat[0] = _np.inf
                return arr
            return arr
        return super().to_numpy(dtype=dtype, copy=copy, na_value=na_value)


def test_run_second_finiteness_pass_cleans_weights(monkeypatch):
    """strategy.run never surfaces non-finite weights even when portfolio
    construction yields non-finite entries; the guard cleans them in place."""
    returns = _base_returns()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
    )
    real_construct = strategy_mod.construct_portfolio

    def _construct(*args, **kwargs):
        df = real_construct(*args, **kwargs).copy()
        df.iloc[0, 0] = _np.inf  # upstream yields non-finite
        return df

    monkeypatch.setattr(strategy_mod, "construct_portfolio", _construct)
    res = strat.run(returns_df=returns)
    assert _np.isfinite(res.weights.to_numpy(dtype=float)).all()
    assert not res.backtest.empty


class _ExplodingOnSecondFloatNumpy(pd.DataFrame):
    """First call returns NaN (triggers first clean), second raises (lines 381-383/384)."""

    _metadata = ["_to_numpy_calls"]

    @property
    def _constructor(self):
        return _ExplodingOnSecondFloatNumpy

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_to_numpy_calls", 0)

    def to_numpy(self, dtype=None, copy=False, na_value=_np.nan):
        if dtype is float or dtype is _np.float64:
            n = object.__getattribute__(self, "_to_numpy_calls")
            object.__setattr__(self, "_to_numpy_calls", n + 1)
            arr = super().to_numpy(dtype=dtype, copy=True, na_value=na_value)
            if n == 0:
                arr = arr.copy()
                arr.flat[0] = _np.nan
                return arr
            if n == 1:
                raise RuntimeError("simulated extra-pass failure")
            return arr
        return super().to_numpy(dtype=dtype, copy=copy, na_value=na_value)


def test_run_finiteness_guard_exception_falls_back(monkeypatch):
    """When the guard's to_numpy read fails, the defensive replace/fillna
    fallback keeps strategy.run returning finite weights and a backtest."""
    returns = _base_returns()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
    )
    real_construct = strategy_mod.construct_portfolio

    class _ToNumpyRaises(pd.DataFrame):
        def to_numpy(self, dtype=None, copy=False, na_value=_np.nan):
            if dtype is float or dtype is _np.float64:
                raise RuntimeError("simulated to_numpy failure")
            return super().to_numpy(dtype=dtype, copy=copy, na_value=na_value)

    def _construct(*args, **kwargs):
        return _ToNumpyRaises(real_construct(*args, **kwargs))

    monkeypatch.setattr(strategy_mod, "construct_portfolio", _construct)
    res = strat.run(returns_df=returns)
    assert res.weights is not None
    assert len(res.weights) == len(returns)
    assert _np.isfinite(res.weights.to_numpy(dtype=float)).all()
    assert not res.backtest.empty


class _ExplodingAllFloatNumpy(pd.DataFrame):
    """Raises on every float to_numpy and on replace/fillna to hit line 385."""

    @property
    def _constructor(self):
        return _ExplodingAllFloatNumpy

    def to_numpy(self, dtype=None, copy=False, na_value=_np.nan):
        if dtype is float or dtype is _np.float64:
            raise RuntimeError("to_numpy boom")
        return super().to_numpy(dtype=dtype, copy=copy, na_value=na_value)

    def replace(self, *args, **kwargs):
        raise RuntimeError("replace boom")

    def fillna(self, *args, **kwargs):
        raise RuntimeError("fillna boom")


def test_run_finiteness_fallback_double_failure_surfaces(monkeypatch):
    """Exercise strategy.py lines 381-385 including final pass.

    The double-failure path (to_numpy raises *and* replace/fillna raises) no
    longer silently swallows: it surfaces as ``BABDataError`` so a corrupt,
    non-finite frame cannot be passed into ``run_backtest`` and silently
    produce wrong P&L.
    """
    from strategies.betting_against_beta.errors import BABDataError

    returns = _base_returns()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
    )
    real_construct = strategy_mod.construct_portfolio

    def _construct(*args, **kwargs):
        return _ExplodingAllFloatNumpy(real_construct(*args, **kwargs))

    monkeypatch.setattr(strategy_mod, "construct_portfolio", _construct)
    with pytest.raises(BABDataError, match="weight finiteness cleanup failed"):
        strat.run(returns_df=returns)
