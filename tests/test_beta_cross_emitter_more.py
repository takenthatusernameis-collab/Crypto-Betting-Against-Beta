"""More cross-emitter invariant tests."""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta


class TestBetaCrossEmitterMore:
    def test_zero_var_bench_all_paths_nan_consistent(self):
        bench = np.full(65, 0.007)
        np.random.seed(5)
        asset = np.random.randn(65) * 0.015
        # calculate_beta
        assert np.isnan(beta.calculate_beta(asset, bench))
        assert np.isnan(beta.calculate_beta_fast(asset, bench))
        # rolling single series
        s = beta.rolling_beta(pd.Series(asset), pd.Series(bench), window=25, min_obs=10)
        assert np.all(np.isnan(s))
        # dataframe
        df = pd.DataFrame({"BTC": bench, "ETH": asset, "LTC": 0.5 * asset})
        r = beta.calculate_rolling_beta(df, "BTC", window=25, min_obs=10)
        assert np.all(np.isnan(r["ETH"].values))
        assert np.all(np.isnan(r["LTC"].values))
