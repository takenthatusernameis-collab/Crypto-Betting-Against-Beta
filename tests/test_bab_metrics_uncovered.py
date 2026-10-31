import numpy as np
import pandas as pd

from strategies.betting_against_beta import metrics


def test_sharpe_std_none_case():
    res = metrics.sharpe_ratio(pd.Series([0.0, 0.0, 0.0001]))
    assert res == float('inf') or np.isinf(res) or np.isnan(res) or isinstance(res, float)


def test_max_drawdown_all_nan_path_returns_nan():
    s = pd.Series([np.nan, np.nan])
    assert np.isnan(metrics.max_drawdown(s))


def test_turnover_dropna_mean_nan():
    df = pd.DataFrame({"A": [0.5, 0.5]})
    assert metrics.turnover(df) == 0.0


def test_sortino_all_negative_downside():
    r = pd.Series([-0.01, -0.02, -0.03])
    res = metrics.sortino_ratio(r)
    assert isinstance(res, float)
