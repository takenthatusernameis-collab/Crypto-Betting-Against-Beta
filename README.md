# Crypto-Betting-Against-Beta

Controller infrastructure plus an implementation of the **Betting Against Beta (BAB)** strategy for crypto.

## Betting Against Beta (Crypto)

A market-neutral strategy that goes long low-beta crypto assets and short high-beta assets, measured against a market benchmark (default BTC), following the Frazzini-Pedersen BAB approach.

### Approach
1. **Universe**: configurable list of liquid crypto assets (default: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT).
2. **Benchmark**: configurable (default BTC); beta of benchmark vs itself is 1.0.
3. **Beta estimation**: rolling OLS window (default 90 days, min 60 observations) of daily returns vs benchmark.
4. **Signal**: each period, rank assets by rolling beta; go long the lowest-beta quantile (default 30%) and short the highest-beta quantile (default 30%).
5. **Portfolio**: equal-weight long/short, **beta-neutral by default** — weights sum to zero *and* `Σ wᵢβᵢ ≈ 0` against the benchmark, with the corrected book frozen inside weekly/monthly rebalance windows. Measurements, before/after numbers, and the honesty caveats are in [`docs/BAB_FIDELITY.md`](docs/BAB_FIDELITY.md). An opt-in `weighting="rank"` path (Frazzini-Pedersen rank weighting with per-leg beta scaling; beta-neutral but not dollar-neutral) is documented in `docs/BAB_FIDELITY.md` §9; the shipped default remains equal-weight. Rank mode requires a wide beta cross-section and is **not empirically evaluable** on the committed 9-asset synthetic fixture, so no rank performance figure is published.
6. **Backtest**: one-day lagged weights (no lookahead), optional transaction costs.

### Module layout
```
strategies/betting_against_beta/
  config.py      # BABConfig: universe, benchmark, windows, quantiles
  data.py        # synthetic return generator (for tests / smoke runs)
  beta.py        # calculate_beta, calculate_rolling_beta
  signals.py     # generate_bab_signals (rank -> long/short)
  portfolio.py   # construct_portfolio (equal-weight dollar-neutral legs)
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

Supported flags: `--data`, `--benchmark`, `--universe`, `--beta-window`, `--long-quantile`, `--short-quantile`, `--rebalance-freq`, `--transaction-costs`, `--slippage`, `--output`, `--synthetic`, `--from-prices`, `--dry-run`, `--version`, `--adapter`, `--exchange`, `--api-key-env`, `--api-secret-env`, `--api-password-env`, `--testnet`, `--allow-live-execution`, `--accept-terms`, `--health-check`, `--reconcile`, `--reconcile-tolerance`, `--reconcile-max-mismatch`, `--fills`, `--paper-trading`, `--max-staleness-days`, `--max-gap-days`.

### Execution adapters (`--adapter`)

The CLI supports pluggable execution adapters. The default path (no `--adapter`) runs a backtest only and is byte-identical to the historical behavior.

| Adapter | Behavior | Network / credentials |
|---------|----------|-----------------------|
| `--adapter paper` | Deterministic paper-trading engine (orders/fills JSONL + diagnostics sidecar). | None, no network |
| `--adapter mock` | Injectable canned fills (`--fills JSON fixture`). | None, no network |
| `--adapter live` | Live execution via `LiveExecutionAdapter` (CCXT connector). **Dry-run by default**: no network, simulated fills, env-only API credentials. Real execution is never implicit. | Env vars only (`--api-key-env`/`--api-secret-env`), no network in dry-run |

Examples:

```bash
# Paper trading: emit timestamped orders/fills to JSONL plus diagnostics sidecar
python -m strategies.betting_against_beta.cli --paper-trading --data prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl

# Live adapter health check (dry-run by default; strict JSON output)
python -m strategies.betting_against_beta.cli --adapter live --exchange binance \
  --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check

# Safety: live adapter always runs dry-run unless explicitly configured otherwise;
# credentials are read only from environment variables, never from CLI args.
```

`--health-check` prints a single strict-JSON object (`mode`, `exchange`, `connected`, `dry_run`, `testnet`, `n_submitted`, `n_fills`, ...) suitable for machine consumption and CI gating.

### Reconciliation enforcement (`--reconcile`, `--reconcile-tolerance`, `--reconcile-max-mismatch`)

`--reconcile` runs the modeled-vs-executed cost reconciliation (R5-B) and fills-vs-backtest reconciliation (R5-C) after a run and emits a strict-JSON artifact alongside execution output. `--reconcile` alone is **emit-only / backward compatible**: it writes the artifact but never fails a run.

Two enforcement flags gate the artifact:

| Flag | Semantics |
|------|-----------|
| `--reconcile-tolerance <float>` | Max absolute modeled-vs-executed cost delta allowed when `--reconcile` is set. Drift strictly above this exits non-zero (exit 2) with a violation message. `None` (default) = emit only, no enforcement. |
| `--reconcile-max-mismatch <int>` | Max allowed mismatch count when `--reconcile` is set. More mismatches than this exits non-zero (exit 2). `None` (default) = emit only. |

A tolerance of exactly the observed drift passes; drift just above fails. Enforcement is deterministic and uses no network. `scripts/bab_reconcile_gate.sh` proves drift fails closed locally (drift exits 2, clean/emit-only exits 0), but **`.github/workflows/main.yml` does not yet invoke `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh`** — CI enforcement of the full BAB suite/coverage floor/reconciliation gate remains a tracked gap (see `HANDOFF.md` P19-1). Do not treat this as CI-enforced until the workflow ships and is observed RED/GREEN.

Example — enforce a tight cost tolerance and fail closed on drift:

```bash
python -m strategies.betting_against_beta.cli --synthetic --adapter paper --reconcile \
  --transaction-costs 0.01 --reconcile-tolerance 0.0 --output /tmp/reconcile.json
# exits 2 with "Reconciliation drift gate breached"
```

Example — tolerance above drift passes:

```bash
python -m strategies.betting_against_beta.cli --synthetic --adapter paper --reconcile \
  --transaction-costs 0.01 --reconcile-tolerance 0.5 --output /tmp/reconcile.json
# exits 0
```

### Live-execution safety (`--allow-live-execution`, `--accept-terms`)

The live adapter (`--adapter live`) is **dry-run by default**: no network, simulated fills, env-only API credentials. Real execution is never implicit.

To permit real (non-dry-run) live execution, both keys must be present:

| Flag | Requirement |
|------|-------------|
| `--allow-live-execution` | First key: explicit opt-in to permit non-dry-run live execution. |
| `--accept-terms` | Second key: must equal the exact token `I_UNDERSTAND_LIVE_TRADING`. Never echoed to logs or artifacts. |

Without both keys, `--adapter live` stays dry-run. With `--allow-live-execution` but a missing or inexact `--accept-terms`, the CLI exits non-zero (rc 2). The adapter enforces the exact terms string itself before any CCXT/network call.

```bash
# Health check (dry-run, safe in CI): strict JSON output, no network.
python -m strategies.betting_against_beta.cli --adapter live --exchange binance \
  --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check

# Real execution path (explicit two-key opt-in; still no network unless
# credentials and the exact accept_terms are supplied):
python -m strategies.betting_against_beta.cli --adapter live --exchange binance \
  --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET \
  --allow-live-execution --accept-terms I_UNDERSTAND_LIVE_TRADING \
  --data prices.csv --from-prices --benchmark BTC
```

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

### CI, gates, and safety (current state)

- **CI enforcement NOT yet shipped (P19-1, maintainer-only):** `.github/workflows/main.yml` contains only the `kilo` controller/diagnostics job. It does **not** invoke `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh`, and there is **no `bab-gate` job**. A prior attempt to add a `bab-gate` job (commit `b641b7a`, branch `kilo-p19-1-push`) was lost when its branch vanished; the push is structurally impossible for agents because the repo token lacks `workflows:write` permission. A maintainer must add the job via the GitHub web UI or a `workflows:write` PAT. Do not re-attempt the push from an agent session.
- **Local gates (verified 2026-11-18T14:19:40Z, HEAD `f98eaa1`):** `python3 -m ruff check .` clean; `bash scripts/bab_reconcile_gate.sh` **GREEN** (drift rc=2, clean rc=0, emit-only rc=0); `bash scripts/bab_gate.sh` **GREEN** → **6445 passed, 35 skipped, TOTAL 100%** (0 missed / 6562 statements). `scripts/bab_bootstrap.sh` installs missing test/runtime deps on fresh runners.
- **Binding next campaign:** Campaign **P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"** (walk-forward/OOS harness on the P35 wide-universe fixture plus Frazzini-Pedersen rank-weighted / beta-scaled construction on the 40-asset wide synthetic universe; fully offline, zero maintainer dependency). P20–P35 are COMPLETE and frozen; P36 is the sole agent-executable binding row. Execute the work packages in [`HANDOFF.md`](HANDOFF.md) — it is the single source of truth. Note: both `tests/fixtures/real_market_prices.csv` (9 assets) and `tests/fixtures/wide_bab_universe.csv` (40 assets) are deterministic synthetic random walks, **not** real market data — never present results on them as evidence of real profitability.
