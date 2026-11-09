"""Coverage campaign 2: metrics.py — all metric functions.

_to_series coercion, sharpe std<EPS/inf branches, max_drawdown cumulative vs
returns heuristic, annualized_volatility 0.0 branch, strategy_beta zero-variance
benchmark, sortino no-downside inf/nan, summary/compute_metrics alias,
turnover/turnover_series None/empty, win_rate/total_return/final_cumulative.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.metrics import (
    EPS,
    annualized_volatility,
    compute_metrics,
    final_cumulative,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
    strategy_beta,
    summary,
    total_return,
    turnover,
    turnover_series,
    win_rate,
)


def test_to_series_none_empty():
    s = annualized_volatility.__globals__["_to_series"](None)
    assert len(s) == 0


def test_to_series_dataframe_single_column():
    _to_series = annualized_volatility.__globals__["_to_series"]
    df = pd.DataFrame({"x": [0.01, 0.02]})
    s = _to_series(df)
    assert isinstance(s, pd.Series) and len(s) == 2


def test_to_series_dataframe_multi_column_nan():
    _to_series = annualized_volatility.__globals__["_to_series"]
    df = pd.DataFrame({"x": [0.01], "y": [0.02]})
    s = _to_series(df)
    assert len(s) == 1 and np.isnan(s.iloc[0])


def test_sharpe_std_below_eps_inf_branch():
    r = pd.Series([0.01, 0.01, 0.01])
    assert sharpe_ratio(r) == np.inf


def test_sharpe_std_below_eps_neg_inf_branch():
    r = pd.Series([-0.01, -0.01, -0.01])
    assert sharpe_ratio(r) == -np.inf


def test_sharpe_std_below_eps_nan_branch():
    r = pd.Series([0.0, 0.0, 0.0])
    assert np.isnan(sharpe_ratio(r))


def test_sharpe_normal():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.001, 0.02, 100))
    s = sharpe_ratio(r)
    assert np.isfinite(s) and abs(s) < 100


def test_sharpe_single_element_nan():
    assert np.isnan(sharpe_ratio(pd.Series([0.01])))


def test_max_drawdown_cumulative_heuristic():
    path = pd.Series([1.0, 1.1, 0.9, 1.2, 0.8])
    dd = max_drawdown(path)
    assert dd < 0.0
    assert dd == pytest.approx((0.8 - 1.2) / 1.2)


def test_max_drawdown_returns_heuristic():
    rets = pd.Series([0.1, -0.5, 0.2])
    dd = max_drawdown(rets)
    assert dd <= 0.0


def test_max_drawdown_empty_nan():
    assert np.isnan(max_drawdown(pd.Series([], dtype=float)))


def test_annualized_volatility_zero_branch():
    r = pd.Series([0.01, 0.01, 0.01])
    assert annualized_volatility(r) == 0.0


def test_annualized_volatility_normal():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0.0, 0.02, 100))
    v = annualized_volatility(r)
    assert np.isfinite(v) and v > 0


def test_strategy_beta_zero_variance_benchmark():
    strat = pd.Series([0.01, 0.02, 0.03])
    bench = pd.Series([0.01, 0.01, 0.01])
    assert np.isnan(strategy_beta(strat, bench))


def test_strategy_beta_normal():
    bench = pd.Series([0.01, 0.02, 0.01, 0.03])
    strat = 2.0 * bench + pd.Series([0.001, -0.001, 0.001, -0.001])
    b = strategy_beta(strat, bench)
    assert np.isfinite(b) and b > 1.0


def test_sortino_no_downside_inf():
    r = pd.Series([0.01, 0.02, 0.01])
    assert sortino_ratio(r) == np.inf


def test_sortino_no_downside_nonpositive_mean_nan():
    r = pd.Series([0.0, 0.0, 0.0])
    assert np.isnan(sortino_ratio(r))


def test_sortino_normal():
    r = pd.Series([0.02, -0.01, 0.03, -0.005, 0.01])
    s = sortino_ratio(r)
    assert np.isfinite(s)


def test_summary_and_compute_metrics_alias():
    r = pd.Series([0.01, 0.02, -0.01, 0.03])
    w = pd.DataFrame({"BTC": [0.5, 0.5, 0.0, 0.0]})
    b = pd.Series([0.01, 0.01, 0.01, 0.01])
    s1 = summary(r, weights_df=w, benchmark_returns=b)
    s2 = compute_metrics(r, weights_df=w, benchmark_returns=b)
    assert s1 == s2
    assert set(s1.keys()) == {
        "sharpe_ratio",
        "annualized_volatility",
        "max_drawdown",
        "turnover",
        "strategy_beta",
        "total_return",
        "final_cumulative",
        "n_observations",
    }


def test_summary_none_weights_nan_turnover():
    r = pd.Series([0.01, 0.02])
    s = summary(r)
    assert np.isnan(s["turnover"])


def test_turnover_none_empty():
    assert np.isnan(turnover(None))
    assert np.isnan(turnover(pd.DataFrame()))


def test_turnover_normal():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    w = pd.DataFrame({"BTC": [0.5, 0.0, 0.5]}, index=idx)
    t = turnover(w)
    assert np.isfinite(t) and t > 0


def test_turnover_series_none_empty():
    assert len(turnover_series(None)) == 0
    assert len(turnover_series(pd.DataFrame())) == 0


def test_turnover_series_normal():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    w = pd.DataFrame({"BTC": [0.5, 0.0, 0.5]}, index=idx)
    ts = turnover_series(w)
    assert isinstance(ts, pd.Series)
    assert ts.iloc[0] == 0.0


def test_win_rate():
    r = pd.Series([0.01, -0.01, 0.02, 0.0])
    assert win_rate(r) == 0.5


def test_win_rate_empty_nan():
    assert np.isnan(win_rate(pd.Series([], dtype=float)))


def test_total_return():
    r = pd.Series([0.1, 0.1])
    assert total_return(r) == pytest.approx(1.1 * 1.1 - 1.0)


def test_total_return_empty_nan():
    assert np.isnan(total_return(pd.Series([], dtype=float)))


def test_final_cumulative():
    r = pd.Series([0.1, 0.1])
    assert final_cumulative(r) == pytest.approx(1.1 * 1.1)


def test_final_cumulative_empty_nan():
    assert np.isnan(final_cumulative(pd.Series([], dtype=float)))
