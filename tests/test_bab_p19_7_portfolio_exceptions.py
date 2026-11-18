"""P19-7: portfolio.py broad-except hardening (sites @ portfolio.py:38,120,169).

Class A (total/tolerant): _clean_signal_value unparseable-string branch returns 0.
Class B (surfacing): coercion/build failures must raise chained BABPortfolioError,
never degrade to an all-zero "no positions" book.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.portfolio as portfolio_mod
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import (
    BABPortfolioError,
    _clean_signal_value,
    construct_portfolio,
)


def test_portfolio_site38_class_a_unparseable_string_returns_zero():
    """Site 38: _clean_signal_value is total; unparseable strings -> neutral 0."""
    assert _clean_signal_value("abc") == 0
    assert _clean_signal_value("") == 0
    assert _clean_signal_value("  ") == 0
    assert _clean_signal_value("NaN-but-str") == 0
    # Happy-path contract unchanged.
    assert _clean_signal_value("1") == 1
    assert _clean_signal_value("-1") == -1
    assert _clean_signal_value("0") == 0
    assert _clean_signal_value(None) == 0


def test_portfolio_site120_class_b_coercion_failure_surfaces(monkeypatch):
    """Site 120: numeric coercion failure must raise chained BABPortfolioError."""
    signals = pd.DataFrame({"BTC": [1], "ETH": [-1]}, index=[pd.Timestamp("2024-01-01")])

    real_is_numeric = pd.api.types.is_numeric_dtype

    def boom_is_numeric(dtype):
        raise RuntimeError("dtype boom")

    monkeypatch.setattr(pd.api.types, "is_numeric_dtype", boom_is_numeric)
    with pytest.raises(BABPortfolioError, match="portfolio construction failed"):
        construct_portfolio(signals)

    # Happy path unaffected.
    monkeypatch.setattr(pd.api.types, "is_numeric_dtype", real_is_numeric)
    w = construct_portfolio(signals)
    assert isinstance(w, pd.DataFrame)
    assert np.isfinite(w.to_numpy(dtype=float)).all()


def test_portfolio_site169_class_b_outer_build_failure_surfaces(monkeypatch):
    """Site 169: unusable frame/build failure must raise, never all-zero fallback."""
    signals = pd.DataFrame({"BTC": [1], "ETH": [-1]}, index=[pd.Timestamp("2024-01-01")])

    def boom_isfinite(arr):
        raise RuntimeError("isfinite boom")

    monkeypatch.setattr(portfolio_mod.np, "isfinite", boom_isfinite)
    with pytest.raises(BABPortfolioError, match="portfolio construction failed"):
        construct_portfolio(signals)


def test_portfolio_happy_path_unchanged():
    signals = pd.DataFrame(
        {"BTC": [1, 1], "ETH": [-1, 0], "SOL": [0, -1]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    w = construct_portfolio(signals)
    assert list(w.columns) == ["BTC", "ETH", "SOL"]
    assert w.shape == signals.shape
    assert np.isfinite(w.to_numpy(dtype=float)).all()
    # Dollar-neutral default: row sums ~0 when both sides present.
    assert abs(float(w.iloc[0].sum())) < 1e-12
