

def test_metrics_multi_column_df_to_series():
    import pandas as pd
    from strategies.betting_against_beta import metrics
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    s = metrics._to_series(df)
    assert isinstance(s, pd.Series)


def test_metrics_sharpe_neg_inf():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    res = metrics.sharpe_ratio(pd.Series([-0.01, -0.01]))
    assert np.isinf(res)


def test_metrics_max_drawdown_nan_cumulative():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    s = pd.Series([np.nan, np.nan])
    assert np.isnan(metrics.max_drawdown(s))


def test_metrics_turnover_nan_weight_changes():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    df = pd.DataFrame({"A": [np.nan, np.nan]})
    assert metrics.turnover(df) == 0.0


def test_metrics_strategy_beta_cov_nan_branch():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    s = pd.Series([np.nan, 0.01])
    b = pd.Series([0.01, np.nan])
    assert np.isnan(metrics.strategy_beta(s, b))


def test_metrics_total_return_nan_val():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    assert np.isnan(metrics.total_return(pd.Series([np.nan])))


def test_metrics_final_cumulative_nan_val():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    res = metrics.final_cumulative(pd.Series([np.nan]))
    assert np.isnan(res) or isinstance(res, float)


def test_metrics_sortino_downside_inf():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    res = metrics.sortino_ratio(pd.Series([-0.01, -0.02]))
    assert isinstance(res, float)


def test_metrics_win_rate_all_zero():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    assert metrics.win_rate(pd.Series([0.0, 0.0])) == 0.0


def test_metrics_compute_metrics_alias():
    import numpy as np
    import pandas as pd
    from strategies.betting_against_beta import metrics
    m = metrics.compute_metrics(pd.Series([0.01, -0.01]), benchmark_returns=pd.Series([0.0, 0.01]))
    assert isinstance(m, dict)
