import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta, signals, portfolio, sizing, shorting, costs, attribution, config, strategy


def test_beta_functions():
    idx = pd.date_range("2023-01-01", periods=80)
    np.random.seed(123)
    mkt = pd.Series(np.random.randn(80)*0.01, index=idx)
    a = pd.Series(0.5*mkt + np.random.randn(80)*0.005, index=idx)
    rets = pd.DataFrame({"BTC": mkt, "ALT": a})
    b = beta.estimate_betas(rets, benchmark="BTC", window=30, min_observations=20)
    assert isinstance(b, pd.DataFrame)
    b2 = beta.rolling_beta(mkt, a, window=30, min_periods=20)
    assert isinstance(b2, pd.Series)


def test_signals_portfolio_sizing():
    idx = pd.date_range("2023-01-01", periods=10)
    betas = pd.DataFrame({"ETH": np.linspace(0.5, 2.0, 10)}, index=idx)
    sig = signals.generate_bab_signals(betas)
    assert isinstance(sig, pd.DataFrame)
    w = portfolio.construct_portfolio(sig)
    assert isinstance(w, pd.DataFrame)
    s = sizing.apply_position_sizing(sig)
    assert isinstance(s, pd.DataFrame)


def test_shorting_costs():
    idx = pd.date_range("2023-01-01", periods=5)
    weights = pd.DataFrame({"ETH": [-0.5, -0.4, -0.3, -0.2, -0.1]}, index=idx)
    sc = shorting.apply_shorting_constraints(weights)
    assert isinstance(sc, pd.DataFrame)
    tc = costs.compute_transaction_costs(weights.shift(1).fillna(0), weights)
    assert isinstance(tc, pd.DataFrame)


def test_attribution_config():
    idx = pd.date_range("2023-01-01", periods=5)
    rets = pd.DataFrame({"BTC": [0.01]*5, "ETH": [0.02]*5}, index=idx)
    backtest = rets.copy()
    backtest["ETH_weight"] = 0.5
    backtest["portfolio_return"] = backtest["ETH_weight"].shift(1).fillna(0) * backtest["ETH"]
    att = attribution.trade_attribution(backtest)
    assert isinstance(att, pd.DataFrame)
    cfg = config.BABConfig()
    assert cfg is not None


def test_strategy_run_small():
    idx = pd.date_range("2023-01-01", periods=80)
    np.random.seed(42)
    mkt = np.random.randn(80)*0.01
    alt = 0.8*mkt + np.random.randn(80)*0.005
    rets = pd.DataFrame({"BTC": mkt, "ETH": alt}, index=idx)
    strat = strategy.BABStrategy(config=config.BABConfig(benchmark="BTC", beta_window=30, min_observations=20))
    res = strat.run(rets)
    assert hasattr(res, "returns")
