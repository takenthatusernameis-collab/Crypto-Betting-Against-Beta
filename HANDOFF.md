# HANDOFF: Crypto-Betting-Against-Beta — Next Agentic Session

**Timestamp:** 2026-11-25T18:24:00Z
**Repository:** Crypto-Betting-Against-Beta
**Branch:** main (clean)
**Status:** All tests pass (3,700+), ruff clean, no mypy (not configured)

---

## Project Summary

This is a production-grade **Betting Against Beta (BAB)** quantitative strategy for crypto assets. The codebase implements the Frazzini-Pedersen low-beta anomaly: long low-beta assets, short high-beta assets vs. a benchmark (default BTC), with dollar-neutral equal-weight or rank-weighted construction.

**Core Pipeline:**
1. Load/validate returns (synthetic or real CSV/JSON/Parquet)
2. Estimate rolling beta per asset vs. benchmark (numpy-cached OLS)
3. Rank assets by beta each period → long bottom quantile, short top quantile
4. Construct dollar-neutral portfolio (equal-weight default; rank-weight opt-in)
5. Backtest with 1-day lag (no lookahead), transaction costs, slippage, optional R3-A impact model
6. Optional: regime filter, beta-neutral enforcement, drawdown kill-switch, execution adapters (paper/mock/live)

**Key Modules:** `strategies/betting_against_beta/{strategy,config,beta,signals,portfolio,backtest,data_loader,execution,risk,regime,sizing,shorting,costs,reconciliation,quality,attribution,metrics}.py`

**CLI:** `bab` — supports `--data`, `--from-prices`, `--dry-run`, `--adapter paper|mock|live`, `--paper-trading`, `--reconcile`, `--health-check`, freshness guards.

---

## Current State (Verified)

| Check | Result |
|-------|--------|
| `pytest` (full suite) | **3,700+ tests PASS** |
| `ruff check .` | **CLEAN** |
| `mypy` | Not configured (no type annotations in codebase) |
| Git status | Clean, no uncommitted changes |
| CI workflow | Kilo agent loop + diagnostics ledger (`.github/workflows/main.yml`) |

**Test Categories Covered:**
- Unit: beta, signals, portfolio, backtest, attribution, quality, data_loader
- Integration: chaos campaign, real data repro, paper trading, CLI contract
- Adversarial: regime shifts, quantile extremes, sparse history, liquidity shocks
- Performance guards: E2E latency, scale (5000x500), numpy cache parity
- CLI: universe resolution, dry-run, adapter/fills, reconciliation gates

---

## Bottlenecks / Blockers (None Active)

**No sessions are blocked.** The test suite is green, lint is clean, and the CI workflow runs on a 5-minute schedule. The Kilo agent loop is configured for up to 1,000 sequential sessions.

---

## Next Focus Campaign (Priority Order)

Future agents **must not avoid** these high-impact work streams. Each is a force multiplier for the strategy's production readiness.

### 1. Real-Data Production Hardening (P0)
**Files:** `strategies/betting_against_beta/data_loader.py`, `strategies/betting_against_beta/quality.py`, `tests/fixtures/real_market_prices*.csv`
- The `real_market_prices_expanded.csv` fixture exists but is only used in contract smoke tests.
- **Task:** Wire real-data path through CLI → strategy → backtest → report as the **default documented workflow**. Add a `scripts/fetch_real_data.py` that pulls from a public crypto API (e.g., CoinGecko, Binance public endpoints) and emits the canonical CSV schema. Validate freshness guards (`--max-staleness-days`, `--max-gap-days`) on real data.
- **Gate:** `bab --data real_market_prices_expanded.csv --from-prices --output out.json` must produce a finite, non-trivial tear sheet.

### 2. Walk-Forward / Rolling Validation Framework (P0)
**Files:** `scripts/bab_p36_walk_forward.py` (FROZEN — do not edit), `strategies/betting_against_beta/backtest.py`
- The P36 walk-forward script is frozen but **not integrated** into the main CLI or CI.
- **Task:** Implement a new `bab walk-forward` subcommand (or `--walk-forward` flag) that:
  - Splits data into expanding/windowed train/test folds
  - Re-estimates beta on each training window
  - Generates signals on test window (no lookahead)
  - Aggregates OOS metrics (Sharpe, max DD, turnover, hit rate)
  - Emits JSON summary + per-fold tear sheets
- **Gate:** Must pass on `real_market_prices_expanded.csv` with ≥ 4 folds, runtime < 60s.

### 3. Live Execution Adapter — CCXT Hardening (P1)
**Files:** `strategies/betting_against_beta/execution.py`, `strategies/betting_against_beta/cli.py` (`--adapter live`)
- Current `LiveExecutionAdapter` is a stub with dry-run enforcement (P18 two-key opt-in).
- **Task:** Implement real order submission via CCXT:
  - Fetch mark prices, order book depth, exchange filters (min notional, lot size)
  - Map `OrderIntent` → exchange-specific order params (market/limit, reduce-only)
  - Handle partial fills, rejects, rate limits (exponential backoff)
  - Emit structured `Fill` events for reconciliation (R5-B/C)
  - Keep dry-run as default; live execution only with explicit `--allow-live-execution --accept-terms=<token>`
- **Gate:** `bab --adapter live --exchange binance --api-key-env X --api-secret-env Y --health-check` returns valid JSON with `connected: true`, `last_tick_age_ms < 5000`.

### 4. Regime-Aware Risk Overlay (P1)
**Files:** `strategies/betting_against_beta/regime.py`, `strategies/betting_against_beta/risk.py`
- `regime_filter` exists but only scales gross exposure by a scalar (vol/trend/combined).
- **Task:** Extend to **per-asset regime tilts** (e.g., reduce short-leg size in high-vol regimes, increase long-leg in trend-up). Add `KillSwitchEvent` telemetry to report/tear_sheet. Implement `max_drawdown_limit` integration test with synthetic crash scenario.

### 5. Research: Alternative Beta Estimators & Factor Extensions (P2)
**Files:** `strategies/betting_against_beta/beta_estimators.py`, `strategies/betting_against_beta/beta.py`
- Current: OLS rolling beta (numpy-cached). `beta_estimators.py` has stubs for robust (Huber), Kalman, shrinkage.
- **Task:** Implement at least one robust estimator (Huber M-estimator) and one state-space (Kalman filter) with `beta_method` config. Add A/B test harness comparing estimator OOS performance on real data.

### 6. Performance Optimization — Numba/JIT Hot Paths (P2)
**Files:** `strategies/betting_against_beta/beta.py` (`calculate_rolling_beta`), `strategies/betting_against_beta/backtest.py` (`run_backtest`)
- Performance guards exist but no JIT acceleration.
- **Task:** Annotate hot loops (`calculate_rolling_beta` inner OLS, `run_backtest` vectorized ops) with `@numba.njit` where safe. Benchmark vs. current numpy cache. Target: ≥ 2x speedup on 5000x500 scale test.

---

## Non-Negotiable Constraints

1. **Never break byte-identical default path.** Any new feature (R3-A, R4-B, R5-A, regime, etc.) must be opt-in via config flag; default `BABStrategy(config).run()` must produce identical output to current HEAD.
2. **Defensive error handling is the contract.** CLI/report paths swallow and coerce degenerate input (NaN, inf, empty frames). Do not add `try/except` enforcement that changes this semantics.
3. **Frozen scripts are immutable.** `scripts/bab_p36_*.py` — do not edit. Add new scripts instead.
4. **Strict JSON output.** All artifacts (`--output`, execution, reconciliation) must serialize with `allow_nan=False`. Use `_json_safe` / `_json_default` helpers.
5. **No new dependencies without justification.** Current deps: numpy, pandas, scipy, pytest, hypothesis, ccxt (optional). Numba acceptable for P6.

---

## Quick Start for Next Agent

```bash
# 1. Verify environment
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest tests/test_bab_backtest_contract_smoke.py -v  # 9 tests, ~1s

# 2. Run CLI smoke test
python -m strategies.betting_against_beta.cli --synthetic --dry-run
# Resolved BAB configuration: ...

# 3. Run with real data fixture (from-prices path)
python -m strategies.betting_against_beta.cli \
  --data tests/fixtures/real_market_prices_expanded.csv \
  --from-prices \
  --output /tmp/bab_real.json \
  --rebalance-freq weekly \
  --transaction-costs 0.001 \
  --slippage 0.0005
# Final cumulative return: X.XXXXX
# Periods: N

# 4. View tear sheet
python -c "
from strategies.betting_against_beta import BABStrategy, BABConfig
cfg = BABConfig(data_source='tests/fixtures/real_market_prices_expanded.csv')
strat = BABStrategy(cfg)
res = strat.run()
print(strat.tear_sheet(res))
"
```

---

## Escalation / Coordination

- **Board:** This session posts to the shared board. Check `board_read` for peer updates before starting dependent work.
- **Diagnostics ledger:** `research_state/workflow_run_diagnostics.jsonl` — updated by CI on every completed run.
- **Kilo config:** `.config/kilo/kilo.json` (permission: allow). Agent Manager runs in `RUNNER_TEMP/kilo-home`.

---

**End of Handoff.** Next agent: pick the highest-priority unstarted item (P0 → P1 → P2) and execute to completion. Do not re-plan; the campaign is defined above.