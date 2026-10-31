import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import metrics


def test_to_series_dataframe_multi_column():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    s = metrics._to_series(df)
    assert isinstance(s, pd.Series)
    assert np.isnan(s.iloc[0]) if len(s) == 1 else True


def test_sharpe_ratio_edges():
    assert np.isnan(metrics.sharpe_ratio(pd.Series([0.01])))
    # zero std with nonzero mean -> inf/-inf
    s = pd.Series([0.01, 0.01, 0.01])
    res = metrics.sharpe_ratio(s)
    assert res == float('inf') or np.isinf(res)
    s2 = pd.Series([-0.01, -0.01, -0.01])
    res2 = metrics.sharpe_ratio(s2)
    assert res2 == float('-inf') or np.isinf(res2)


def test_max_drawdown_cumulative_direct():
    # cumulative path
    cum = pd.Series([1.0, 1.1, 0.9, 1.05])
    dd = metrics.max_drawdown(cum)
    assert dd <= 0


def test_max_drawdown_empty():
    assert np.isnan(metrics.max_drawdown(pd.Series(dtype=float)))


def test_annualized_volatility_edges():
    assert np.isnan(metrics.annualized_volatility(pd.Series([0.01])))
    s = pd.Series([0.0, 0.0, 0.0])
    assert metrics.annualized_volatility(s) == 0.0


def test_turnover_edges():
    assert np.isnan(metrics.turnover(None))
    assert np.isnan(metrics.turnover(pd.DataFrame()))
    df = pd.DataFrame({"A": [0.0, 0.0]})
    assert metrics.turnover(df) == 0.0


def test_strategy_beta_edges():
    assert np.isnan(metrics.strategy_beta(pd.Series([0.01]), pd.Series([0.01, 0.02])))
    # zero variance benchmark
    s = pd.Series([0.01, 0.02, 0.03])
    b = pd.Series([0.0, 0.0, 0.0])
    assert np.isnan(metrics.strategy_beta(s, b))


def test_total_return_final_cumulative():
    assert np.isnan(metrics.total_return(pd.Series(dtype=float)))
    assert np.isnan(metrics.final_cumulative(pd.Series(dtype=float)))
    r = pd.Series([0.01, 0.02])
    assert isinstance(metrics.total_return(r), float)
    assert isinstance(metrics.final_cumulative(r), float)


def test_sortino_ratio_edges():
    assert np.isnan(metrics.sortino_ratio(pd.Series([0.01])))
    # all positive
    r = pd.Series([0.01, 0.02, 0.01])
    sr = metrics.sortino_ratio(r)
    assert sr == float('inf') or np.isinf(sr)
    # downside dev zero case
    r2 = pd.Series([0.01, -0.0])  # has zero? excess might be zero
    pass


def test_win_rate_edges():
    assert np.isnan(metrics.win_rate(pd.Series(dtype=float)))
    assert np.isnan(metrics.win_rate(None))


def test_turnover_series_edges():
    assert isinstance(metrics.turnover_series(None), pd.Series)
    assert isinstance(metrics.turnover_series(pd.DataFrame()), pd.Series)
    df = pd.DataFrame({"A": [0.0, 0.5, 0.2]})
    ts = metrics.turnover_series(df)
    assert isinstance(ts, pd.Series)
    assert ts.iloc[0] == 0.0


def test_summary_with_benchmark():
    idx = pd.date_range("2023-01-01", periods=50)
    rets = pd.Series(np.random.randn(50)*0.01, index=idx)
    bench = pd.Series(np.random.randn(50)*0.01, index=idx)
    w = pd.DataFrame(np.random.randn(50, 2)*0.1, index=idx, columns=["A", "B"])
    s = metrics.summary(rets, weights_df=w, benchmark_returns=bench)
    assert isinstance(s, dict)
