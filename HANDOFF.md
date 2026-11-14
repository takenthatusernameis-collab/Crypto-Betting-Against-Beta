# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T21:01:26Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `86243be` (`chore(kilo): checkpoint agent session`)
- **Branch:** `main`
- **Working tree:** clean (verified 2026-11-14T21:01:26Z)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T21:01:26Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Completed — Priority 6 (public fetch hardening) — evidence at HEAD `fc6faa0`
P6 (resilience/coverage tests, `--metadata-out` JSON audit sidecar, README docs, verification, commit, handoff refresh) is DONE. Implementation landed in `scripts/fetch_real_bab_prices.py` + `tests/test_fetch_real_bab_prices.py` + `README.md` (post `8cdeaf1`); final lint blocker fixed in `fc6faa0`.

### Completed — Priority 7 (full-suite regression + gate verification) — evidence at HEAD `5ed5088`
P7 (full pytest suite, `scripts/bab_gate.sh`, CLI entrypoint parity, verification, handoff refresh) is DONE. All acceptance criteria met.

### Completed — Priority 8 (live/near-real-time execution readiness) — evidence at HEAD `f4ab467`
P8 (paper-trading scaffold, data freshness/staleness guards, signal diagnostics, verification, commit, handoff refresh) is DONE. All acceptance criteria met.

| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) @ 2026-11-14T21:01:26Z |
| P8 targeted tests | `python3 -m pytest -q tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py tests/test_betting_against_beta.py` | **99 passed** (18.21s) @ 2026-11-14T21:01:26Z |
| Full suite | `python3 -m pytest -q` | **Large suite (>10 min)** — iterate targeted subsets when debugging; do not regress full-suite green |
| Git state | `git log -1 --oneline` / `git status --short` | `86243be` / clean tree @ 2026-11-14T21:01:26Z |

**No P0/P1/P2/P3/P4/P5/P6/P7/P8 bottlenecks.** Offline deterministic default path unchanged. P5 opt-in public Coinbase fetch complete. P6 complete. P7 complete. P8 complete and verified.

### P8 Implementation Summary (commits 341d86a, 5f2dfe2, a83d86c, f4ab467)

**1. Paper-trading scaffold (dry-run execution path):**
- Added `PaperExecutionEngine` in `strategies/betting_against_beta/execution.py:724` consuming `BABStrategy` weights, emitting timestamped orders/fills to JSONL, computing per-rebalance `StrategyDiagnostics`, and reconciling paper P&L vs backtest.
- Canonical types: `Order`, `Fill`, `StrategyDiagnostics`, `ExecutionReport` (lines 572-700).
- CLI flag `--paper-trading --output paper_fills.jsonl` on `strategies.betting_against_beta.cli` (lines 391-398, 641-685).
- Unit tests: `tests/test_bab_paper_trading.py` covering order emission, fill simulation (next-bar open, participation-cap + sqrt-impact slippage), P&L reconciliation vs backtest.

**2. Data freshness & staleness guards:**
- Extended `data_loader.py` with `validate_freshness(max_staleness_days=2, max_gap_days=7)` raising `BABDataError` on stale/missing data (line 2715).
- Added `--max-staleness-days` / `--max-gap-days` to CLI (lines 400-416) and `fetch_real_bab_prices.py` (lines 756-772); fail loudly on violations (no silent fallback).
- Tests: `tests/test_bab_data_freshness.py` covering fresh, stale, gap, and boundary cases.

**3. Signal quality / regime observability:**
- `StrategyDiagnostics` emitted per rebalance: beta distribution stats, quantile boundaries, long/short roster, turnover, concentration (HHI), beta-neutrality error (lines 630-672).
- Persisted to `diagnostics.jsonl` alongside paper fills; included in `ExecutionReport` (lines 675-700, 852-856).
- Tests: `tests/test_bab_diagnostics.py` verifying schema and invariants (beta-neutrality ~0 with `beta_neutral=True`, HHI bounds).

### Priority 9 — Next focus campaign (MANDATORY, heavy lifting) — BINDING

Extend the BAB strategy with **production-grade live execution readiness** while preserving the green baseline. All items required; none optional.

1. **Live execution adapter scaffold (real broker integration):**
   - Add `LiveExecutionAdapter` implementing `ExecutionAdapter` protocol (in `execution.py`) with configurable exchange connectors (CCXT-based for spot, extendable for futures).
   - Implement order lifecycle: submit → ack → partial/full fill → cancel/replace, with idempotency keys and retry/backoff for transient errors.
   - CLI flag `--adapter live --exchange <name> --api-key-env <var> --api-secret-env <var>`; dry-run by default (`--paper-trading`); never implicit network calls.
   - Order routing: respect `max_participation`, `adv_usd`, and `slippage` from config; emit `Fill` records compatible with `ExecutionReport`.
   - Unit tests: `tests/test_bab_live_adapter.py` covering order submission, fill parsing, error handling, idempotency; integration test against a sandbox/testnet (opt-in, gated by env var).

2. **Position & risk management overlay:**
   - Add `RiskManager` class in `risk.py` consuming `ExecutionReport` + real-time prices; enforce per-asset, per-side, and portfolio-level limits (max gross, max net, max drawdown, max position age).
   - Integrate with `PaperExecutionEngine` and `LiveExecutionAdapter` via a `pre_trade_check(order_batch, current_positions, risk_limits)` hook returning allowed/modified/rejected intents.
   - Kill-switch: on breach, cancel all open orders, flatten positions via market orders (configurable), emit `RiskEvent` to audit log.
   - Tests: `tests/test_bab_risk_manager.py` covering limit enforcement, kill-switch trigger, flattening logic.

3. **Real-time data feed & freshness SLA:**
   - Extend `data_sources.py` with `RealtimeFeed` abstract base + `CCXTFeed`/`WebSocketFeed` implementations; normalize to `load_prices`/`load_returns` schema.
   - Enforce freshness SLA: `max_staleness_seconds` (default 30s), `max_gap_seconds` (default 60s) on tick/bar level; raise `BABDataError` on violation; integrate with `validate_freshness`.
   - Health endpoint: `/health` JSON with last tick timestamp, staleness, gap, connection status; expose via CLI `--health-check`.
   - Tests: `tests/test_bab_realtime_feed.py` covering reconnection, backfill, SLA enforcement, schema validation.

4. **Verification + commit + refresh handoff (required before stopping):**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q` → all pass (baseline + new tests)
   - `bash scripts/bab_gate.sh` → exit 0
   - `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Paper trading smoke: `python -m strategies.betting_against_beta.cli --paper-trading --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl` → exit 0, valid JSONL
   - Live adapter smoke (opt-in): `python -m strategies.betting_against_beta.cli --adapter live --exchange paper --dry-run --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → exit 0, valid `ExecutionReport`
   - Commit with evidence (`git log -1 --oneline`, `git status --short`, ruff, full suite, gate, perf, paper smoke, live smoke).
   - **Refresh this handoff**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

**Acceptance:** P9 items implemented/tested, full suite + gate green, perf guardrail holds, paper trading smoke passes, live adapter smoke passes (opt-in), committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets only when debugging, but do not regress full-suite green.
- Pandas/numpy warnings in stress tests are expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- `bab-example` console script requires `pip install -e .` — not a blocker; module CLI works.

### Protocol
1. Read this file fully. 2. Execute P9 (live execution adapter, risk management, real-time feed, verification, commit, handoff refresh). 3. Refresh this handoff before stopping. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory (2026-11-14T21:01:26Z UTC):** Complete **Priority 9** end-to-end (live execution adapter scaffold, risk management overlay, real-time data feed, verification, commit, handoff refresh) before any new feature work. Do not stop at analysis. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, full pytest output, gate output, paper trading smoke, live adapter smoke (opt-in), perf evidence.