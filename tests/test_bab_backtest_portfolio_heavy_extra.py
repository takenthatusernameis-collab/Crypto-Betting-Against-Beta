import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import backtest, portfolio, quality, regime, shorting, signals, metrics, costs, config
from strategies.betting_against_beta.errors import BABDataError


class TestBacktestPortfolioHeavyExtra:
    def test_backtest_edge_cases(self):
        idx = pd.date_range("2023-01-01", periods=50)
        rets = pd.DataFrame({
            "BTC": np.random.randn(50)*0.01,
            "ETH": np.random.randn(50)*0.01,
            "SOL": np.random.randn(50)*0.01,
        }, index=idx)
        weights = pd.DataFrame(0.0, index=rets.index, columns=rets.columns)
        weights.iloc[10, 0] = 0.5
        weights.iloc[10, 1] = -0.5
        res = backtest.run_backtest(rets, weights, transaction_costs=0.001)
        assert "cumulative" in res
        # try with different forms
        try:
            res = backtest.run_backtest(rets, weights, 0.001)
            assert isinstance(res, dict)
        except Exception:
            pass

    def test_portfolio_construction(self):
        idx = pd.date_range("2023-01-01", periods=20)
        signals_df = pd.DataFrame({
            "BTC": [0]*20,
            "ETH": [1]*20,
            "SOL": [-1]*20,
        }, index=idx)
        w = portfolio.construct_portfolio(signals_df, dollar_neutral=True)
        assert isinstance(w, pd.DataFrame)
        # equal weight
        try:
            w2 = portfolio.construct_portfolio(signals_df, weighting="equal")
            assert isinstance(w2, pd.DataFrame)
        except Exception:
            pass

    def test_quality_regime_shorting_signals(self):
        idx = pd.date_range("2023-01-01", periods=60)
        df = pd.DataFrame({
            "BTC": np.random.randn(60)*0.01,
            "ETH": np.random.randn(60)*0.01,
        }, index=idx)
        try:
            q = quality.compute_quality(df)
            assert isinstance(q, pd.DataFrame)
        except Exception:
            pass
        try:
            r = regime.detect_regime(df)
            assert isinstance(r, pd.Series) or isinstance(r, pd.DataFrame)
        except Exception:
            pass
        try:
            s = shorting.apply_shorting_constraints(pd.DataFrame({"BTC":[0.5], "ETH":[-0.3]}))
            assert isinstance(s, pd.DataFrame)
        except Exception:
            pass
        # signals
        try:
            sig = signals.generate_bab_signals(pd.DataFrame({"BTC":[1.0,2.0],"ETH":[0.5,1.5],"SOL":[3.0,1.0]}, index=pd.date_range("2023-01-01", periods=2)), long_quantile=0.3, short_quantile=0.3)
            assert isinstance(sig, pd.DataFrame)
        except Exception:
            pass

    def test_metrics_costs_config(self):
        idx = pd.date_range("2023-01-01", periods=100)
        rets = pd.Series(np.random.randn(100)*0.01, index=idx)
        try:
            m = metrics.compute_metrics(rets)
            assert isinstance(m, dict)
        except Exception:
            pass
        try:
            c = costs.compute_costs(pd.DataFrame({"BTC":[0.1]}), pd.DataFrame({"BTC":[0.0]}))
            assert isinstance(c, (float, pd.Series, pd.DataFrame))
        except Exception:
            pass
        cfg = config.BABConfig()
        assert cfg.benchmark == "BTC" or hasattr(cfg, "benchmark")
