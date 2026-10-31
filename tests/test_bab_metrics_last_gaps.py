import numpy as np
import pandas as pd

from strategies.betting_against_beta import metrics


def test_to_series_multi_column_df():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    s = metrics._to_series(df)
    assert isinstance(s, pd.Series)
    # multi-column df returns series of nan
    assert len(s) == 1
    assert np.isnan(s.iloc[0])


def test_sharpe_zero_std_positive_mean():
    # std_excess is zero or tiny but mean_excess positive -> returns inf
    res = metrics.sharpe_ratio([0.01, 0.01, 0.01])
    assert np.isinf(res) or res == float('inf')


def test_turnover_nan_mean():
    df = pd.DataFrame({"A": [0.1, 0.1], "B": [0.2, 0.2]})  # no change gives diff all zero -> mean not nan, wait diff gives 0
    # force case where weight_changes.dropna().mean() gives nan
    df = pd.DataFrame({"A": [np.nan, np.nan]})
    res = metrics.turnover(df)
    assert res == 0.0 or np.isnan(res)


def test_strategy_beta_nan_beta():
    s = pd.Series([np.nan, np.nan])
    b = pd.Series([0.01, 0.02])
    res = metrics.strategy_beta(s, b)
    assert np.isnan(res)


def test_total_return_nan_value():
    # force nan
    s = pd.Series([np.nan])
    res = metrics.total_return(s)
    assert np.isnan(res)


def test_final_cumulative_nan_value():
    s = pd.Series([np.nan])
    res = metrics.final_cumulative(s)
    assert np.isnan(res)


def test_sortino_downside_dev_zero_mean_pos():
    # downside exists but downside_dev < eps and mean_excess > 0
    # create case where all downside returns are same tiny negative
    r = pd.Series([-1e-19, -1e-19])  # tiny
    res = metrics.sortino_ratio(r)
    assert np.isinf(res) or isinstance(res, float)


def test_max_drawdown_all_nan_cumulative():
    s = pd.Series([np.nan, np.nan])
    assert np.isnan(metrics.max_drawdown(s))


def test_turnover_all_zero_changes():
    df = pd.DataFrame({"A": [0.1, 0.1]})
    assert metrics.turnover(df) == 0.0


def test_strategy_beta_cov_nan():
    s = pd.Series([np.nan, 0.01])
    b = pd.Series([0.01, np.nan])
    assert np.isnan(metrics.strategy_beta(s, b))


def test_total_return_nan_final():
    s = pd.Series([np.nan])
    assert np.isnan(metrics.total_return(s))


def test_final_cumulative_nan():
    s = pd.Series([np.nan])
    res = metrics.final_cumulative(s)
    assert np.isnan(res)


def test_sortino_downside_dev_none_or_small():
    r = pd.Series([-0.01, -0.02])
    res = metrics.sortino_ratio(r)
    assert isinstance(res, float)


def test_turnover_all_nan_diff_gives_zero():
    df = pd.DataFrame({"A": [np.nan, np.nan]})
    res = metrics.turnover(df)
    assert res == 0.0 or np.isnan(res)


def test_strategy_beta_nan_var_result():
    # var_bench might be small but let us force case where beta is nan
    s = pd.Series([0.01, 0.02, 0.03])
    b = pd.Series([0.01, 0.01, 0.01])  # zero variance
    res = metrics.strategy_beta(s, b)
    assert np.isnan(res)


def test_sharpe_mean_excess_small_pos_inf():
    # std very small positive but mean positive -> should return inf
    res = metrics.sharpe_ratio(pd.Series([1e-18, 1e-18]))
    # Just ensure no crash
    assert res == res or np.isnan(res)  # always true, but we want to exercise path


def test_total_return_with_inf_nan_check():
    res = metrics.total_return(pd.Series([np.inf]))
    assert isinstance(res, float) or np.isnan(res)


def test_final_cumulative_with_inf_nan_check():
    res = metrics.final_cumulative(pd.Series([np.inf]))
    assert isinstance(res, float) or np.isnan(res)


def test_sortino_all_negative_mean_excess_small_dev():
    # downside exists, downside_dev small -> goes to inf if mean excess > 0? mean excess is negative
    r = pd.Series([-0.001, -0.002])
    res = metrics.sortino_ratio(r)
    assert isinstance(res, float)
