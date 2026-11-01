"""Probe: real breakage on HANDOFF-named edge cases."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta, signals, portfolio, backtest, metrics
from strategies.betting_against_beta.errors import BABDataError

def probe(name, fn):
    try:
        fn()
        print(f"OK   {name}")
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__}: {e}")

# A. min_obs > window in calculate_rolling_beta (public API)
def t_rolling_min_obs_gt_window():
    df = pd.DataFrame({"BTC": np.random.RandomState(0).randn(100),
                       "ETH": np.random.RandomState(1).randn(100)})
    res = beta.calculate_rolling_beta(df, "BTC", window=30, min_obs=60)
    assert np.all(np.isnan(res["ETH"].to_numpy())), "min_obs>window should be all NaN"
probe("rolling min_obs > window", t_rolling_min_obs_gt_window)

# B. calculate_rolling_beta with min_obs > window via estimate_betas
def t_estimate_min_obs_gt_window():
    df = pd.DataFrame({"BTC": np.random.RandomState(0).randn(100),
                       "ETH": np.random.RandomState(1).randn(100)})
    res = beta.estimate_betas(df, benchmark="BTC", window=20, min_obs=100)
    assert isinstance(res, pd.DataFrame)
probe("estimate_betas min_obs > window", t_estimate_min_obs_gt_window)

# C. enforce_beta_neutrality residual drift: correction on all-short
def t_neutral_all_short():
    w = pd.DataFrame({"BTC": [0.0], "ETH": [-0.5], "SOL": [-0.5]})
    b = pd.DataFrame({"BTC": [1.0], "ETH": [0.8], "SOL": [1.2]})
    out = portfolio.enforce_beta_neutrality(w, b, correction=True)
    s = out.sum(axis=1).iloc[0]
    assert abs(s) < 1e-9, f"all-short neutrality broken: net={s}"
probe("neutrality all-short row", t_neutral_all_short)

# D. enforce_beta_neutrality residual drift: correction on all-long
def t_neutral_all_long():
    w = pd.DataFrame({"BTC": [0.5], "ETH": [0.5], "SOL": [0.0]})
    b = pd.DataFrame({"BTC": [1.0], "ETH": [0.8], "SOL": [1.2]})
    out = portfolio.enforce_beta_neutrality(w, b, correction=True)
    s = out.sum(axis=1).iloc[0]
    assert abs(s) < 1e-9, f"all-long neutrality broken: net={s}"
probe("neutrality all-long row", t_neutral_all_long)

# E. beta colinear assets (singular design matrix)
def t_beta_colinear():
    a = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    b = a * 2.0  # perfectly colinear
    out = beta.calculate_beta(a, b)
    assert np.isfinite(out), f"colinear beta should be finite, got {out}"
probe("beta colinear", t_beta_colinear)

# F. beta_fast with mixed finite/non-finite, min_obs boundary
def t_beta_fast_min_obs():
    a = [0.01, 0.02, 0.03, 0.04, 0.05]
    b = [0.01, 0.02, 0.03, 0.04, 0.05]
    out = beta.calculate_beta_fast(a, b, min_obs=5)
    assert np.isfinite(out), f"min_obs=5 with 5 obs should be finite, got {out}"
    out2 = beta.calculate_beta_fast(a, b, min_obs=6)
    assert np.isnan(out2), f"min_obs=6 with 5 obs should be NaN, got {out2}"
probe("beta_fast min_obs boundary", t_beta_fast_min_obs)

# G. metrics summary all-NaN
def t_metrics_all_nan():
    s = metrics.summary(pd.Series([np.nan, np.nan]))
    assert "sharpe_ratio" in s
probe("metrics all-NaN", t_metrics_all_nan)

# H. backtest with inf weights
def t_backtest_inf_weights():
    returns = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [-0.01, 0.03]})
    weights = pd.DataFrame({"BTC": [np.inf, 0.5], "ETH": [-0.5, -0.5]})
    bt = backtest.run_backtest(returns, weights)
    assert np.isfinite(bt["returns"].values).all(), "inf weights leaked"
probe("backtest inf weights", t_backtest_inf_weights)

# I. signals tie determinism
def t_signals_ties():
    df = pd.DataFrame({"BTC": [0.5, 0.5], "ETH": [0.5, 0.5], "SOL": [0.5, 0.5]})
    s1 = signals.generate_bab_signals(df)
    s2 = signals.generate_bab_signals(df)
    assert s1.values.tolist() == s2.values.tolist(), "signals not deterministic on ties"
probe("signals tie determinism", t_signals_ties)

# J. construct_portfolio dollar-neutral with only shorts (caller-provided)
def t_portfolio_dn_shorts_only():
    sig = pd.DataFrame({"BTC": [0], "ETH": [-1], "SOL": [-1]})
    w = portfolio.construct_portfolio(sig, dollar_neutral=True)
    s = w.sum(axis=1).iloc[0]
    assert abs(s) < 1e-9, f"shorts-only dn net={s} (should be 0)"
probe("portfolio dn shorts-only", t_portfolio_dn_shorts_only)

# K. construct_portfolio dollar-neutral with only longs
def t_portfolio_dn_longs_only():
    sig = pd.DataFrame({"BTC": [0], "ETH": [1], "SOL": [1]})
    w = portfolio.construct_portfolio(sig, dollar_neutral=True)
    s = w.sum(axis=1).iloc[0]
    assert abs(s) < 1e-9, f"longs-only dn net={s} (should be 0)"
probe("portfolio dn longs-only", t_portfolio_dn_longs_only)