# Crypto-Betting-Against-Beta

Controller infrastructure plus an implementation of the **Betting Against Beta (BAB)** strategy for crypto.

## Betting Against Beta (Crypto)

A market-neutral strategy that goes long low-beta crypto assets and short high-beta assets, measured against a market benchmark (default BTC), following the Frazzini-Pedersen BAB approach.

### Approach
1. **Universe**: configurable list of liquid crypto assets (default: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT).
2. **Benchmark**: configurable (default BTC); beta of benchmark vs itself is 1.0.
3. **Beta estimation**: rolling OLS window (default 90 days, min 60 observations) of daily returns vs benchmark.
4. **Signal**: each period, rank assets by rolling beta; go long the lowest-beta quantile (default 30%) and short the highest-beta quantile (default 30%).
5. **Portfolio**: equal-weight long/short, dollar-neutral by default (weights sum to zero).
6. **Backtest**: one-day lagged weights (no lookahead), optional transaction costs.

### Module layout
```
strategies/betting_against_beta/
  config.py      # BABConfig: universe, benchmark, windows, quantiles
  data.py        # synthetic return generator (for tests / smoke runs)
  beta.py        # calculate_beta, calculate_rolling_beta
  signals.py     # generate_bab_signals (rank -> long/short)
  portfolio.py   # construct_portfolio (equal-weight, dollar-neutral)
  backtest.py    # run_backtest (lagged weights, costs, cumulative)
  strategy.py    # BABStrategy: end-to-end entrypoint (run pipeline)
```

### Run
```bash
python3 - <<'EOF'
from strategies.betting_against_beta import BABStrategy

strategy = BABStrategy()  # default config, synthetic data
result = strategy.run()
print(result.backtest["cumulative"].iloc[-1])
EOF
```

### Tests
```bash
python3 -m pytest -q
```
All tests must pass. Strategy tests live in `tests/test_betting_against_beta.py`; controller/infra tests cover progress accounting, diagnostics scanning, nonfinite serialization, and campaign resume.

### Assumptions
- Synthetic data by default; swap `returns_df` in `BABStrategy.run()` for real price/return data.
- Daily rebalance on close; no slippage model beyond optional transaction costs.
- NaN/insufficient-history observations produce flat (zero-weight) periods.
