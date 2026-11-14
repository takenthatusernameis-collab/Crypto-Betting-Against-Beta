# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T21:04:07Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `fbbac30` (`docs: refresh canonical handoff with binding P9 campaign`)
- **Branch:** `main`
- **Working tree:** clean at refresh (no uncommitted changes)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T21:04:07Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Evolve **Crypto Betting Against Beta (BAB)** from paper-trading scaffold to **production-grade live execution readiness** on real, updatable, reproducible market data while preserving the clean lint/test/perf baseline.

### Verified baseline (evidence at refresh, 2026-11-14T21:04:07Z UTC)

| Check | Command | Result |
|-------|---------|--------|
| Git | `git log -1 --oneline` / `git status --short` | `fbbac30` / clean |
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| P8 targeted | `python3 -m pytest -q tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py tests/test_betting_against_beta.py` | **99 passed** per P8 handoff record (re-run if touching these areas) |

**No P0–P8 bottlenecks.** P6 (public fetch hardening + `--metadata-out`), P7 (full-suite/gate/CLI parity), and P8 (paper-trading scaffold, freshness/staleness guards, per-rebalance diagnostics JSONL) are complete and committed. Offline deterministic default path unchanged; opt-in Coinbase public fetch unchanged. Large suite is intentional — iterate with targeted subsets when debugging, but do not regress full-suite/gate green.

### Priority 9 — Next focus campaign (MANDATORY, heavy lifting) — BINDING

Implement **live execution readiness** end-to-end. All items required; none optional.

1. **Live execution adapter scaffold (real broker integration):**
   - Add `LiveExecutionAdapter` implementing `ExecutionAdapter` in `strategies/betting_against_beta/execution.py` with configurable exchange connectors (CCXT-based for spot; extensible for futures). No implicit network calls; dry-run default.
   - Order lifecycle: submit → ack → partial/full fill → cancel/replace, with idempotency keys and retry/backoff for transient errors.
   - CLI: `--adapter live --exchange <name> --api-key-env <var> --api-secret-env <var>` (paper trading remains default/explicit safe path). Route orders respecting `max_participation`, `adv_usd`, and `slippage`; emit `Fill` records compatible with `ExecutionReport`.
   - Tests: `tests/test_bab_live_adapter.py` (submission, fill parsing, errors, idempotency; sandbox/testnet integration opt-in/gated by env var).

2. **Position & risk management overlay:**
   - Add production-grade `RiskManager` in `strategies/betting_against_beta/risk.py` consuming `ExecutionReport` + real-time/current prices: enforce per-asset, per-side, and portfolio-level limits (max gross, max net, max drawdown, max position age).
   - Integrate with `PaperExecutionEngine` and `LiveExecutionAdapter` via `pre_trade_check(order_batch, current_positions, risk_limits)` returning allowed/modified/rejected intents.
   - Kill-switch: on breach cancel open orders, flatten positions via configurable market orders, emit `RiskEvent` to audit log (preserve/extend existing drawdown kill-switch semantics without regressions).
   - Tests: `tests/test_bab_risk_manager.py` (limits, kill-switch, flattening, audit events).

3. **Real-time data feed & freshness SLA:**
   - Add `RealtimeFeed` abstract base + `CCXTFeed`/`WebSocketFeed` implementations in `strategies/betting_against_beta/data_sources.py`; normalize to `load_prices`/`load_returns` schema.
   - Enforce tick/bar freshness SLA (`max_staleness_seconds` default 30s, `max_gap_seconds` default 60s) integrated with `validate_freshness`; raise `BABDataError` on violation (no silent fallback).
   - Health check: expose `/health`-equivalent JSON (last tick, staleness, gap, connection status) and CLI `--health-check`.
   - Tests: `tests/test_bab_realtime_feed.py` (reconnect/backfill, SLA enforcement, schema validation; network gated).

4. **Verification, commit, and handoff refresh (required before stopping):**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q` → all pass (baseline + new tests)
   - `bash scripts/bab_gate.sh` → exit 0
   - Perf guardrail: `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Paper smoke: `python -m strategies.betting_against_beta.cli --paper-trading --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl` → exit 0, valid JSONL
   - Live adapter smoke (opt-in/dry-run, no implicit network): `python -m strategies.betting_against_beta.cli --adapter live --exchange paper --dry-run --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → exit 0, valid `ExecutionReport`
   - Commit with evidence in message/body as appropriate; report `git log -1 --oneline`, `git status --short`, ruff, full suite, gate, perf, paper smoke, live smoke.
   - **Refresh this handoff**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

**Acceptance:** P9 items implemented/tested, full suite + gate green, perf guardrail holds, paper + live (opt-in dry-run) smokes pass, committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite (>5k tests) is intentional; use targeted subsets while iterating but keep full suite/gate green.
- Pandas/numpy warnings in stress tests expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- `bab-example` console script requires `pip install -e .`; module CLI (`python -m strategies.betting_against_beta.cli`) is canonical.

### Protocol
1. Read this file fully. 2. Execute **P9** end-to-end (live adapter, risk overlay, realtime feed/SLA, verification, commit, handoff refresh). 3. Do not stop at analysis/research; land code + tests + evidence. 4. Refresh this handoff (UTC timestamp, HEAD, completed work with exact evidence, remaining gaps/risks, next binding task) before stopping. 5. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory (2026-11-14T21:04:07Z UTC):** Complete **Priority 9** before any other work. Deliver: `LiveExecutionAdapter` + CCXT-ready connector abstraction and order lifecycle/idempotency/retry in `execution.py`; CLI `--adapter live --exchange <name> --api-key-env <var> --api-secret-env <var>` with dry-run default and `ExecutionReport`-compatible fills; `RiskManager` with per-asset/side/portfolio limits, `pre_trade_check`, kill-switch flattening, and `RiskEvent` audit in `risk.py`; `RealtimeFeed`/`CCXTFeed`/`WebSocketFeed`, tick/bar SLA enforcement, `validate_freshness` integration, and `--health-check` in `data_sources.py`/CLI; tests `tests/test_bab_live_adapter.py`, `tests/test_bab_risk_manager.py`, `tests/test_bab_realtime_feed.py` (network/sandbox gated/opt-in). Report exact evidence for ruff, full pytest, gate, perf, paper smoke, live smoke, `git log -1 --oneline`, `git status --short`. No analysis-only handoff.
