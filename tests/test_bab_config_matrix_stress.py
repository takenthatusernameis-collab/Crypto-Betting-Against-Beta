"""Config-matrix stress tests across key strategy options."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.strategy import BABStrategy
from strategies.betting_against_beta import sizing


def test_matrix_regime_shorting_sizing_costs_deterministic():
    rng = np.random.RandomState(2026)
    dates = pd.date_range("2022-01-01", periods=300)
    n = len(dates)
    bench = rng.normal(0, 0.01, n)
    rets = {
        "BTC": bench,
        "ETH": rng.normal(0, 0.015, n) + 0.9 * bench,
        "SOL": rng.normal(0, 0.02, n) + 1.2 * bench,
        "BNB": rng.normal(0, 0.018, n) + 0.7 * bench,
        "XRP": rng.normal(0, 0.016, n) + 0.5 * bench,
        "ADA": rng.normal(0, 0.017, n) + 0.6 * bench,
    }
    returns_df = pd.DataFrame(rets, index=dates)

    regime_opts = [False, True]
    short_opts = [None, 0.5]
    sizer_opts = [None, sizing.VolatilityTargetSizer(target_vol=0.1)]
    cost_opts = [0.0, 0.001, 0.002]

    for regime in regime_opts:
        for short in short_opts:
            for ps in sizer_opts:
                for cost in cost_opts:
                    kwargs = {
                        "regime_filter": regime,
                        "transaction_costs": cost,
                    }
                    if ps is not None:
                        kwargs["position_sizer"] = ps
                    if short is not None:
                        try:
                            from strategies.betting_against_beta import shorting
                            kwargs["shorting_constraints"] = shorting.ShortingConstraints(max_short_leverage=short)
                        except Exception:
                            pass
                    strat = BABStrategy(config=BABConfig(**kwargs))
                    res1 = strat.run(returns_df=returns_df)
                    res2 = strat.run(returns_df=returns_df)
                    w1 = res1.weights
                    w2 = res2.weights
                    assert (w1 - w2).abs().sum().sum() == 0.0
                    assert np.isfinite(w1.values).all()
                    bt = res1.backtest
                    assert np.isfinite(bt["returns"]).all()
                    assert np.isfinite(bt["cumulative"]).all()
