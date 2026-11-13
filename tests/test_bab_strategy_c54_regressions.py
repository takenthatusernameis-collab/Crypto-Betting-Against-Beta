"""C54 Step 2 regression suite — strategy.py silent-`pass` conversion.

Target: ``strategy.py`` line 396 (now ~400).  The double-failure path of the
weight finiteness guard — ``to_numpy`` raises *and* the ``replace``/``fillna``
fallback raises — previously ended in a bare ``except Exception: pass``,
passing a corrupt, non-finite weights frame into ``run_backtest`` and silently
producing wrong P&L.  It now raises ``BABDataError`` with both exceptions
chained.

Valid-path behaviour is unchanged: ordinary runs produce finite weights and a
non-empty backtest.
"""
from __future__ import annotations

import numpy as _np
import pandas as pd
import pytest

import strategies.betting_against_beta.strategy as strategy_mod
from strategies.betting_against_beta.errors import BABDataError
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


class _ExplodingAllFloatNumpy(pd.DataFrame):
    """Raises on every float ``to_numpy`` and on ``replace``/``fillna``."""

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


def test_double_finiteness_failure_surfaces_babdataerror(monkeypatch):
    """Invalid path: both cleanup attempts fail -> BABDataError, not silence."""
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


def test_single_finiteness_failure_still_falls_back(monkeypatch):
    """Valid-ish path: outer guard fails but the replace/fillna fallback works.

    The outer try (lines 381-393) raises; the inner fallback (394-395)
    succeeds, so run_backtest receives a finite frame and no error surfaces.
    """
    returns = _base_returns()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
    )

    class _ExplodingOuterOnly(pd.DataFrame):
        """Raises on the first float ``to_numpy`` (outer guard), then normal."""

        _metadata = ["_to_numpy_calls"]

        @property
        def _constructor(self):
            return _ExplodingOuterOnly

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            object.__setattr__(self, "_to_numpy_calls", 0)

        def to_numpy(self, dtype=None, copy=False, na_value=_np.nan):
            if dtype is float or dtype is _np.float64:
                n = object.__getattribute__(self, "_to_numpy_calls")
                object.__setattr__(self, "_to_numpy_calls", n + 1)
                if n == 0:
                    raise RuntimeError("outer to_numpy boom")
                return super().to_numpy(dtype=dtype, copy=True, na_value=na_value)
            return super().to_numpy(dtype=dtype, copy=copy, na_value=na_value)

    real_construct = strategy_mod.construct_portfolio

    def _construct(*args, **kwargs):
        return _ExplodingOuterOnly(real_construct(*args, **kwargs))

    monkeypatch.setattr(strategy_mod, "construct_portfolio", _construct)
    res = strat.run(returns_df=returns)
    assert res is not None
    assert _np.isfinite(res.weights.to_numpy(dtype=float)).all()
    assert not res.backtest.empty


def test_clean_run_unchanged(monkeypatch):
    """Valid path: ordinary run produces finite weights and a non-empty backtest."""
    returns = _base_returns()
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=20,
        min_observations=10,
        long_quantile=0.3,
        short_quantile=0.3,
    )
    res = strat.run(returns_df=returns)
    assert _np.isfinite(res.weights.to_numpy(dtype=float)).all()
    assert not res.backtest.empty
    assert res.backtest["cumulative"].iloc[-1] > 0