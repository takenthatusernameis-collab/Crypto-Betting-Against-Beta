"""Performance & regression tests for portfolio construction.

Guards ``construct_portfolio`` against silent slowdowns while asserting that
the weights produced remain numerically equivalent to the reference row-wise
semantics for representative and edge cases.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.signals import generate_bab_signals
from strategies.betting_against_beta.data import generate_synthetic_returns


def _time_it(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - start


def _reference_construct(signals_df, dollar_neutral=True):
    """Simple row-wise reference mirroring documented portfolio semantics."""
    if signals_df is None or not isinstance(signals_df, pd.DataFrame) or signals_df.empty:
        return pd.DataFrame()
    idx = signals_df.index
    cols = signals_df.columns
    w = pd.DataFrame(0.0, index=idx, columns=cols, dtype=float)
    for i in idx:
        row = signals_df.loc[i]
        longs = []
        shorts = []
        for c in cols:
            v = row[c]
            try:
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    iv = 0
                else:
                    iv = int(float(v))
            except Exception:
                iv = 0
            if iv == 1:
                longs.append(c)
            elif iv == -1:
                shorts.append(c)
        if longs:
            lw = 1.0 / len(longs)
            for c in longs:
                w.at[i, c] = lw
        if shorts and (dollar_neutral or not longs):
            sw = -1.0 / len(shorts)
            for c in shorts:
                w.at[i, c] = sw
        if dollar_neutral and longs and shorts:
            roww = w.loc[i]
            lsum = float(roww[roww > 0].sum())
            ssum = float(roww[roww < 0].sum())
            if lsum > 1e-18:
                roww[roww > 0] = roww[roww > 0] / lsum
            if ssum < -1e-18:
                roww[roww < 0] = roww[roww < 0] / (-ssum)
            w.loc[i] = roww
            net = float(w.loc[i].sum())
            if abs(net) > 1e-12:
                roww = w.loc[i]
                lsum = float(roww[roww > 0].sum())
                if lsum > 1e-18:
                    roww[roww > 0] = roww[roww > 0] * (1.0 - net) / lsum
                w.loc[i] = roww
    return w


class TestConstructPortfolioPerformance:
    N_DAYS = 2000
    N_ASSETS = 120

    @pytest.fixture(scope="class")
    def signals(self):
        returns = generate_synthetic_returns(
            n_days=self.N_DAYS, n_assets=self.N_ASSETS, seed=1234
        )
        beta = calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)
        return generate_bab_signals(beta, long_quantile=0.3, short_quantile=0.3)

    def test_values_match_reference_oracle(self, signals):
        got = construct_portfolio(signals, dollar_neutral=True)
        expected = _reference_construct(signals, dollar_neutral=True)
        pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)

    def test_values_match_reference_non_dollar_neutral(self, signals):
        got = construct_portfolio(signals, dollar_neutral=False)
        expected = _reference_construct(signals, dollar_neutral=False)
        pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)

    def test_large_universe_completes_in_reasonable_time(self, signals):
        _, elapsed = _time_it(construct_portfolio, signals, dollar_neutral=True)
        assert elapsed < 30.0, (
            f"construct_portfolio took {elapsed:.2f}s for "
            f"{signals.shape}; performance regression"
        )

    def test_portfolio_stage_perf_ceiling(self):
        """Per-stage non-regression ceiling for the portfolio build.

        Generous bound (well above the measured few-ms single-call cost and far
        above CI noise) so it stays stable on shared runners while guarding
        against a catastrophic slowdown of ``construct_portfolio``.  Measures the
        broadcast-product build at 2500x120 (the production hot path) and only
        the build itself (no beta/signal recomputation).
        """
        returns = generate_synthetic_returns(n_days=2500, n_assets=120, seed=1234)
        beta = calculate_rolling_beta(returns, "BTC", window=90, min_obs=60)
        signals = generate_bab_signals(beta, long_quantile=0.3, short_quantile=0.3)
        construct_portfolio(signals)  # warm
        _, elapsed = _time_it(construct_portfolio, signals, dollar_neutral=True)
        assert elapsed < 1.0, (
            f"construct_portfolio took {elapsed:.3f}s on {signals.shape}; "
            "portfolio-stage perf regression"
        )


class TestConstructPortfolioEdgeCases:
    def test_mixed_and_non_numeric_signals_equivalence(self):
        idx = pd.date_range("2024-01-01", periods=6, freq="D")
        signals = pd.DataFrame(
            {
                "A": [1, -1, 0, "1", None, np.nan],
                "B": [-1, 1, 1, "0", "x", 1.0],
                "C": [0, 0, -1, "-1", 2, -1.0],
                "D": [1, np.nan, 1, "bad", "1.0", 0],
            },
            index=idx,
        )
        got = construct_portfolio(signals, dollar_neutral=True)
        expected = _reference_construct(signals, dollar_neutral=True)
        pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)

    def test_all_long_or_all_short_rows(self):
        idx = pd.date_range("2024-01-01", periods=3, freq="D")
        signals = pd.DataFrame(
            {"A": [1, -1, 0], "B": [1, -1, 0], "C": [1, -1, 0]},
            index=idx,
        )
        got = construct_portfolio(signals, dollar_neutral=True)
        expected = _reference_construct(signals, dollar_neutral=True)
        pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)
        assert np.allclose(got.loc[idx[0]].sum(), 1.0)
        assert np.allclose(got.loc[idx[1]].sum(), -1.0)
