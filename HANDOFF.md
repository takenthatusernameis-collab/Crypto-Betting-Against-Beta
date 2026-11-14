# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T23:16:18Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD (at refresh):** `c27551c` (`chore(kilo): checkpoint agent session`)
- **Branch:** `main`
- **Working tree:** clean at refresh

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T23:16:18Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective (Crypto Betting Against Beta)
Complete **P9: live execution readiness** end-to-end for the BAB strategy: deliver a working, tested `LiveExecutionAdapter` + `RiskManager` integration + realtime feed/freshness-SLA stack with CLI/smoke/perf/gate evidence, preserving clean lint and default offline/dry-run safety.

### Baseline (verified 2026-11-14T22:23:04Z UTC in prior handoff; re-run only what you touch/change)
- `python3 -m ruff check .` → **All checks passed**
- `python3 -m pytest -q tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` → **13 passed, 1 warning** (Pandas4 `Timestamp.utcnow` deprecation, non-blocking)
- `python3 -m pytest -q tests/test_bab_live_adapter.py` → **24 passed**
- **Blocking:** `python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py` → **20 failed, 65 passed**

Scaffolding present: `strategies/betting_against_beta/{execution.py,risk.py,data_sources.py,cli.py}` and tests `tests/test_bab_{live_adapter,risk_manager,realtime_feed}.py`. Inspect before rewriting.

### Remove bottlenecks first (mandatory, no deferral)

1. **`tests/test_bab_risk_manager.py` (2 failures):** align `RiskLimits` defaults/semantics and `apply_kill_switch`/flatten behavior with intended P9 contract (e.g. `max_net_exposure` default must not reject valid balanced positions; kill-switch trigger/flatten expectations must match). Fix implementation or make expectations deterministic/correct — do **not** weaken risk guarantees.
2. **`tests/test_bab_realtime_feed.py` (18 failures):** tests instantiate abstract `RealtimeFeed` (provide concrete/test stub implementing `connect`/`disconnect`/`fetch_latest`) and use fixed historical dates causing staleness failures under now-relative SLA logic. Make deterministic (inject/reference `now`, use relative timestamps, fix brittle regex where behavior is correct). Do **not** weaken SLA guarantees or add silent fallbacks.

### P9 execution plan (must complete, in order)

1. **Live execution adapter (`execution.py`, `cli.py`)**
   - Finish/harden `LiveExecutionAdapter` (CCXT-ready connector abstraction, spot baseline, extensible). No implicit network calls; dry-run default. Honor `--adapter live --exchange <name> --api-key-env/--api-secret-env/--api-password-env` and `--testnet` with env-only credentials.
   - Order lifecycle: submit → ack → partial/full fill → cancel/replace as applicable; deterministic idempotency keys; bounded retry/backoff for transient errors (no infinite loops).
   - Respect `max_participation`, `adv_usd`, slippage inputs; emit fills compatible with existing `ExecutionReport`/paper reconciliation expectations.
   - `--health-check` returns strict-JSON-safe status for live adapter/feed context where supported. Live smoke must run in dry-run/no-network mode.
   - `tests/test_bab_live_adapter.py` green; add/adjust only for real contract (submission, fill parsing, errors, idempotency, retries/backoff, dry-run).

2. **Position & risk management (`risk.py`, integration)**
   - Production-grade `RiskManager` consuming `ExecutionReport`/orders + positions/prices: enforce per-asset, per-side, portfolio limits (`max_gross`, `max_net`, `max_drawdown`, position age/daily turnover/concentration per `RiskLimits` contract).
   - `pre_trade_check(...)` returns allowed/modified/rejected intents with `RiskEvent` audit records.
   - Kill-switch: on breach support cancel-open/flatten semantics and emit `RiskEvent` audit trail; preserve/extend existing drawdown kill-switch without regressions.
   - Integrate with `PaperExecutionEngine` and `LiveExecutionAdapter` paths where applicable without changing default paper/backtest behavior unless explicitly configured.
   - `tests/test_bab_risk_manager.py` green with deterministic expectations.

3. **Real-time data feed & freshness SLA (`data_sources.py`, CLI)**
   - `RealtimeFeed` ABC + `CCXTFeed`/`WebSocketFeed`; normalize to `load_prices`/`load_returns`-compatible schema.
   - Enforce tick/bar freshness SLA (`max_staleness_seconds` default 30s, `max_gap_seconds` default 60s) via `validate_freshness`/feed checks; raise `BABDataError` on violation (no silent fallback).
   - Health: strict-JSON-safe payload (connected, last tick, staleness, gap, symbols/error) and CLI `--health-check` behavior.
   - `tests/test_bab_realtime_feed.py` green (deterministic timestamps/mocks; network gated/opt-in only).

4. **Verification, commit, handoff refresh (required before stopping)**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` → all pass
   - `python3 -m pytest -q` → all pass
   - `bash scripts/bab_gate.sh` → exit 0
   - `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Paper smoke: `python3 -m strategies.betting_against_beta.cli --paper-trading --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl` → exit 0, valid JSONL
   - Live dry-run smoke (no implicit network): `python3 -m strategies.betting_against_beta.cli --adapter live --exchange binance --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check` with dummy env vars as needed → exit 0, clear JSON-safe output (or document and implement the exact supported dry-run invocation that passes)
   - Commit with evidence; report `git log -1 --oneline`, `git status --short`, ruff, targeted/full pytest, gate, perf, paper smoke, live smoke.
   - Refresh this handoff with new UTC timestamp, HEAD, completed work with exact evidence, remaining gaps/risks, and next binding task.

**Acceptance:** P9 implemented/tested end-to-end (adapter + risk + realtime/SLA + CLI integration) with default offline/dry-run safety preserved, full suite + gate green, perf guardrail holds, paper + live dry-run smokes pass, committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate targeted, keep full/gate green before stopping.
- Pandas/numpy warnings and `Timestamp.utcnow` deprecation in `tests/test_bab_data_freshness.py` are non-blocking unless behavioral.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli` (`bab-example` needs editable install).

### Protocol
1. Read this file fully. 2. Execute P9 end-to-end (unblock, implement, verify, commit, refresh handoff). 3. Never stop at analysis/research. 4. Keep `AGENT_HANDOFF.md` as pointer only.
