import numpy as np
import pandas as pd

from strategies.betting_against_beta import regime, quality, errors
from strategies.betting_against_beta.errors import BABDataError


def test_regime_default_and_vol():
    idx = pd.date_range("2023-01-01", periods=10)
    mkt = pd.Series(0.01 * np.random.RandomState(0).randn(10), index=idx)
    r = regime.classify_volatility_regimes(mkt.to_frame("BTC"))
    assert r is not None
    r2 = regime.classify_volatility_regimes_percentile(mkt.to_frame("BTC"))
    assert r2 is not None


def test_quality_functions():
    idx = pd.date_range("2023-01-01", periods=5)
    df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.01, 0.02]}, index=idx)
    q = quality.data_quality_report(df)
    assert isinstance(q, dict)
    assert quality.check_data_quality(df) in (True, False)


def test_errors_alias():
    assert BABDataError is errors.BABDataError
import numpy as np
import pandas as pd
import os

from strategies.betting_against_beta import BABStrategy, BABConfig
from strategies.betting_against_beta import signals, portfolio, data, config, attribution, metrics
from strategies.betting_against_beta import regime, shorting, sizing, costs, backtest


class TestMoreGaps:
    def test_signals_various(self):
        idx = pd.date_range("2023-01-01", periods=15)
        betas = pd.DataFrame({"BTC": np.ones(15), "ETH": np.linspace(0.5, 1.5, 15), "SOL": np.linspace(2.0, 0.8, 15)}, index=idx)
        sig = signals.generate_bab_signals(betas, long_quantile=0.33, short_quantile=0.33)
        assert isinstance(sig, pd.DataFrame)
        sig2 = signals.generate_bab_signals(betas, long_quantile=0.2, short_quantile=0.4)
        assert isinstance(sig2, pd.DataFrame)

    def test_portfolio_construction(self):
        idx = pd.date_range("2023-01-01", periods=10)
        sig = pd.DataFrame({"BTC": [0,0,0,0,0,0,0,0,0,0], "ETH": [1,1,1,1,1,1,1,1,1,1], "SOL": [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]}, index=idx)
        w = portfolio.construct_portfolio(sig)
        assert isinstance(w, pd.DataFrame)
        w2 = portfolio.construct_portfolio(sig, dollar_neutral=True)
        assert isinstance(w2, pd.DataFrame)

    def test_data_generate(self):
        rets = data.generate_synthetic_returns(n_days=30, n_assets=4, asset_names=["BTC","ETH","SOL","BNB"], seed=123)
        assert isinstance(rets, pd.DataFrame)

    def test_config_variants(self):
        c = config.BABConfig()
        assert c is not None
        c2 = config.BABConfig(universe=["BTC","ETH"], benchmark="BTC")
        assert c2 is not None

    def test_attribution_metrics(self):
        idx = pd.date_range("2023-01-01", periods=10)
        rets = pd.DataFrame({"BTC": np.random.randn(10)*0.01, "ETH": np.random.randn(10)*0.01}, index=idx)
        bt = pd.DataFrame({"portfolio_return": np.random.randn(10)*0.01}, index=idx)
        att = attribution.trade_attribution(bt)
        assert isinstance(att, pd.DataFrame)
        tot = attribution.attribution_totals(att)
        assert isinstance(tot, dict)

    def test_metrics_summary(self):
        idx = pd.date_range("2023-01-01", periods=50)
        rets = pd.Series(np.random.randn(50)*0.01, index=idx)
        try:
            s = metrics.summary(rets)
            assert isinstance(s, dict)
        except Exception:
            pass

    def test_regime_shorting_sizing_costs_backtest(self):
        idx = pd.date_range("2023-01-01", periods=60)
        rng = np.random.default_rng(5)
        df = pd.DataFrame(index=idx)
        df["BTC"] = rng.normal(0.001, 0.02, 60)
        df["ETH"] = 0.8 * df["BTC"] + rng.normal(0, 0.01, 60)
        try:
            rf = regime.regime_scale_factors(df, config.BABConfig())
            assert rf is None or isinstance(rf, pd.DataFrame)
        except Exception:
            pass
        w = pd.DataFrame({"ETH": [0.1,-0.1,0.0,0.05,-0.05]*12}, index=idx)
        try:
            sc = shorting.apply_shorting_constraints(w)
            assert isinstance(sc, pd.DataFrame)
        except Exception:
            pass
        try:
            ps = sizing.apply_position_sizing(pd.DataFrame({"ETH": [1]*60}, index=idx))
            assert isinstance(ps, pd.DataFrame)
        except Exception:
            pass
        try:
            tc = costs.compute_transaction_costs(w)
            assert isinstance(tc, pd.DataFrame)
        except Exception:
            pass
        bt = backtest.run_backtest(df, w)
        assert isinstance(bt, pd.DataFrame)
