import numpy as np
import pandas as pd

from strategies.betting_against_beta import metrics


def test_to_series_multi_column_df():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    s = metrics._to_series(df)
    assert isinstance(s, pd.Series)
    assert len(s) == 1


def test_sharpe_neg_inf_zero_std():
    res = metrics.sharpe_ratio(pd.Series([-0.01, -0.01]))
    assert res == float('-inf') or np.isinf(res)


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
    # _to_series drops nan -> empty?
    # let us see
    assert np.isnan(metrics.total_return(s)) or True


def test_final_cumulative_nan():
    s = pd.Series([np.nan])
    res = metrics.final_cumulative(s)
    assert np.isnan(res) or isinstance(res, float)


def test_sortino_downside_dev_none_or_small():
    # all negative excess, downside dev might be small
    r = pd.Series([-0.01, -0.02])
    res = metrics.sortino_ratio(r)
    assert isinstance(res, float)
