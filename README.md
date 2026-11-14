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



### Real data (swap from synthetic)

```python
from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_returns, load_prices

# Load pre-computed daily returns (CSV/JSON/JSONL/Parquet/HDF5/Pickle)
returns_df = load_returns("returns.csv", benchmark="BTC")  # datetime index/col + numeric columns

# Or load prices and convert to returns
# returns_df = load_prices("prices.csv", benchmark="BTC")

strategy = BABStrategy(
    benchmark="BTC", beta_window=90, long_quantile=0.3, short_quantile=0.3, transaction_costs=0.001
)
result = strategy.run(returns_df=returns_df)
print(float(result.backtest["cumulative"].iloc[-1]))
```

### CLI

```bash
# Synthetic data (default)
python -m strategies.betting_against_beta.cli --synthetic

# From returns CSV
python -m strategies.betting_against_beta.cli --data returns.csv --benchmark BTC

# From prices CSV
python -m strategies.betting_against_beta.cli --data prices.csv --from-prices --benchmark BTC

# Dry-run: validate inputs and print resolved config without running
python -m strategies.betting_against_beta.cli --dry-run --data prices.csv --from-prices --benchmark BTC

# Version
python -m strategies.betting_against_beta.cli --version
```

Supported flags: `--data`, `--benchmark`, `--universe`, `--beta-window`, `--long-quantile`, `--short-quantile`, `--rebalance-freq`, `--transaction-costs`, `--slippage`, `--output`, `--synthetic`, `--from-prices`, `--dry-run`, `--version`.

Or use the installed `bab-example` console script:

```bash
bab-example prices.csv --from-prices --benchmark BTC
```

### Real-format fetch/update pipeline

```bash
# Default: deterministic offline generator (no network, reproducible)
python scripts/fetch_real_bab_prices.py --output data/real_bab_prices.csv \
  --universe BTC,ETH,SOL,BNB,XRP,ADA,AVAX,DOT,LINK --benchmark BTC \
  --start 2021-01-04 --end 2022-07-15 --print-metadata

# Deterministic local fixture copy/slice (no network)
python scripts/fetch_real_bab_prices.py --output data/real_bab_prices.csv \
  --source fixture --fixture-path tests/fixtures/real_market_prices.csv \
  --benchmark BTC --start 2021-01-04 --end 2022-07-15

# Explicit opt-in: no-auth public Coinbase Exchange daily candles (network)
# Requires explicit ToS/rate-limit acknowledgement; fails loudly on
# network/HTTP/rate-limit/invalid-source/parse errors (no silent fallback).
python scripts/fetch_real_bab_prices.py --output data/real_bab_prices.csv \
  --source coinbase-exchange-public --allow-public-api \
  --accept-terms "I accept the data provider Terms of Service and rate limits" \
  --benchmark BTC --universe BTC,ETH,SOL --quote-currency USD \
  --start 2024-01-01 --end 2024-06-30 --print-metadata
```

#### Metadata audit sidecar (`--metadata-out`)

Write a machine-readable JSON audit trail for reproducibility and CI/CD integration:

```bash
python scripts/fetch_real_bab_prices.py --output data/real_bab_prices.csv \
  --source coinbase-exchange-public --allow-public-api \
  --accept-terms "I accept the data provider Terms of Service and rate limits" \
  --benchmark BTC --universe BTC,ETH,SOL --quote-currency USD \
  --start 2024-01-01 --end 2024-06-30 \
  --metadata-out data/fetch_meta.json
```

The JSON sidecar contains:
- `tool`, `source`, `source_url_base` (for public API), `benchmark`, `universe`, `request_range`
- `request_settings`: `timeout_seconds`, `max_requests_per_second`, `max_retries`, `user_agent`
- `tos_acknowledged` (boolean only), `tos_flag_only` (true for public API; raw ToS text never persisted)
- `fetch_time_utc`, `mode` (`created`/`updated`/`failed`), `seed` (if set)
- `outcome`: on success — `ok:true`, `rows`, `date_coverage` (`first`/`last`/`unique_dates`), `columns`, `output`; on failure — `ok:false`, `error` context

#### Failure modes (public API path)

| Failure scenario | Behavior |
|------------------|----------|
| Missing `--allow-public-api` | Exits non-zero with clear message; no network request |
| Invalid/mismatched `--accept-terms` | Exits non-zero; exact ToS text required |
| Network unreachable / DNS failure | Exits non-zero after retries; no offline fallback |
| HTTP 429 rate limit | Retries with `Retry-After` backoff; fails after max retries |
| HTTP 5xx server errors | Retries with exponential backoff; fails after max retries |
| HTTP 404 / invalid product | Exits non-zero; symbol unavailable on public market |
| Non-JSON / invalid candle payload | Exits non-zero; `BABDataError` with parse context |
| Empty candle response (no data in window) | Exits non-zero; `BABDataError` |
| Partial symbol coverage (some symbols missing) | Exits non-zero; `BABDataError` — no silent partial alignment |
| Duplicate dates / non-monotonic output | Exits non-zero; schema validation failure |

- Offline `deterministic-offline` is the only default path and is idempotent/incrementally updatable.
- Public API fetching is never implicit: `--source coinbase-exchange-public` requires `--allow-public-api` and exact `--accept-terms`; requests are rate-limit paced and retried only for bounded transient/rate-limit cases, then fail loudly.
- Review provider Terms of Service, market-data policies, and rate limits before use; redistribution may be restricted. Output schema is `date,BTC,<assets...>` compatible with `load_prices()` / `--from-prices`.

### Assumptions
- Synthetic data by default; swap `returns_df` in `BABStrategy.run()` for real price/return data.
- Daily rebalance on close; no slippage model beyond optional transaction costs.
- NaN/insufficient-history observations produce flat (zero-weight) periods.
