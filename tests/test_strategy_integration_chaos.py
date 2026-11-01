"""Strategy integration chaos tests."""
import numpy as np
import pandas as pd

from strategies.betting_against_beta import strategy
from strategies.betting_against_beta.data import generate_synthetic_returns


class TestStrategyIntegrationChaos:
    def test_run_with_corrupted_returns_no_crash(self):
        df = generate_synthetic_returns(n_days=200, seed=123)
        # Corrupt some values - just NaN, avoid inf which data_loader rejects strictly
        df2 = df.copy()
        df2.iloc[10, 0] = np.nan
        df2.iloc[20, 1] = np.nan
        s = strategy.BABStrategy()
        res = s.run(returns_df=df2)
        assert res is not None
        assert hasattr(res, 'backtest')

    def test_run_deterministic_with_seed(self):
        df = generate_synthetic_returns(n_days=150, seed=42)
        s1 = strategy.BABStrategy()
        r1 = s1.run(returns_df=df)
        s2 = strategy.BABStrategy()
        r2 = s2.run(returns_df=df)
        # Should be deterministic
        assert np.allclose(r1.backtest['returns'].fillna(0).values,
                          r2.backtest['returns'].fillna(0).values)
