# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T22:23:04Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `7113398` (`chore(kilo): checkpoint agent session`)
- **Branch:** `main`
- **Working tree:** clean at refresh (no uncommitted changes)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T22:23:04Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Complete **P9: live execution readiness** for the Crypto Betting Against Beta (BAB) strategy — land a working, tested live-adapter/risk/realtime-feed stack with CLI/smoke/perf/gate evidence, preserving the clean lint baseline and default offline/dry-run safety.

### Verified baseline (evidence at refresh, 2026-11-14T22:23:04Z UTC)

| Check | Command | Result |
|-------|---------|--------|
| Git | `git log -1 --oneline --decorate` / `git status --short` | `7113398 (HEAD -> main, origin/main) chore(kilo): checkpoint agent session` / clean |
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| P8/paper+freshness+diagnostics | `python3 -m pytest -q tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` | **13 passed, 1 warning** (Pandas4 `Timestamp.utcnow` deprecation in test; no behavioral failure) |
| P9 live-adapter tests | `python3 -m pytest -q tests/test_bab_live_adapter.py` | **24 passed** |
| P9 risk/realtime (combined) | `python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py` | **20 failed, 65 passed** — **blocking bottleneck** (see below) |

**Scaffolding present (inspect before rewriting):** `strategies/betting_against_beta/execution.py` includes `LiveExecutionAdapter`/`CCXTConnector`/order+fill lifecycle + idempotency/dry-run helpers; `risk.py` includes `RiskManager`/`RiskLimits`/`PreTradeCheckResult`/`RiskEvent`/kill-switch helpers; `data_sources.py` includes `RealtimeFeed` ABC, `CCXTFeed`, `WebSocketFeed`, `FeedHealth`, `validate_freshness`, `BABDataError`; `cli.py` includes `--adapter {paper,mock,live}`, `--exchange`, `--api-key-env/--api-secret-env/--api-password-env`, `--testnet`, `--health-check`, paper/freshness flags. Tests exist: `tests/test_bab_live_adapter.py`, `tests/test_bab_risk_manager.py`, `tests/test_bab_realtime_feed.py`.

### Blocking bottlenecks to remove first

1. **`tests/test_bab_risk_manager.py` failures (2):** e.g. `test_pre_trade_check_allowed` expects allowed but `RiskLimits.max_net_exposure` defaults to `0.0` (rejects balanced non-zero positions) — reconcile defaults/semantics with intended P9 behavior and tests; `test_apply_kill_switch_triggers` expectation mismatch vs `apply_kill_switch`/flattening behavior.
2. **`tests/test_bab_realtime_feed.py` failures (18):** tests instantiate abstract `RealtimeFeed` directly (needs concrete/test stub implementing `connect`/`disconnect`/`fetch_latest`) and `validate_freshness` tests use fixed historical dates causing staleness failures under current “now”-relative SLA logic — make tests deterministic and aligned with contract (inject/reference `now` or use relative timestamps; fix regex/expectations where behavior is correct). Do not weaken SLA guarantees.
3. **P9 contract gaps may remain after test fixes:** ensure end-to-end behavior matches P9 acceptance (live adapter CLI dry-run smoke, risk `pre_trade_check` integration path, realtime SLA enforcement + `--health-check` semantics, no implicit network). Treat failing/newly-required behavior as implementation work, not test deletion.

### Priority 9 — Complete live execution readiness (MANDATORY, heavy lifting) — BINDING

1. **Unblock and harden live execution adapter (`execution.py`, `cli.py`):**
   - Deliver/finish `LiveExecutionAdapter` implementing `ExecutionAdapter` with CCXT-ready connector abstraction (spot baseline, extensible). No implicit network calls; dry-run default. Honor `--adapter live --exchange <name> --api-key-env <var> --api-secret-env <var>` (and optional password/testnet) with safe credential handling from env only.
   - Order lifecycle: submit → ack → partial/full fill → cancel/replace semantics as applicable, deterministic idempotency keys, bounded retry/backoff for transient errors (no infinite loops).
   - Respect `max_participation`, `adv_usd`, and slippage inputs; emit fill records compatible with existing `ExecutionReport`/paper reconciliation expectations.
   - CLI: `--health-check` returns strict-JSON-safe status for live adapter/feed context where supported; live smoke must run in dry-run/no-network mode.
   - Tests: `tests/test_bab_live_adapter.py` green; add/adjust coverage only as needed for real contract (submission, fill parsing, errors, idempotency, retries/backoff behavior, dry-run).

2. **Position & risk management overlay (`risk.py`, integration):**
   - Production-grade `RiskManager` consuming `ExecutionReport`/orders + positions/prices: enforce per-asset, per-side, and portfolio limits (max gross, max net, max drawdown, max position age/daily turnover/concentration as specified by `RiskLimits` contract).
   - `pre_trade_check(order_batch, current_positions, risk_limits/cumulative context as implemented)` returns allowed/modified/rejected intents with `RiskEvent` audit records.
   - Kill-switch: on breach support cancel-open/flatten semantics and emit `RiskEvent` audit trail; preserve/extend existing drawdown kill-switch behavior without regressions.
   - Integrate with `PaperExecutionEngine` and `LiveExecutionAdapter` paths where applicable without changing default paper/backtest behavior unless explicitly configured.
   - Tests: `tests/test_bab_risk_manager.py` green with clear, deterministic expectations.

3. **Real-time data feed & freshness SLA (`data_sources.py`, CLI):**
   - `RealtimeFeed` abstract base + `CCXTFeed`/`WebSocketFeed` implementations; normalize to `load_prices`/`load_returns`-compatible schema.
   - Enforce tick/bar freshness SLA (`max_staleness_seconds` default 30s, `max_gap_seconds` default 60s) via `validate_freshness`/feed checks; raise `BABDataError` on violation (no silent fallback).
   - Health surface: strict-JSON-safe health payload (connected, last tick, staleness, gap, symbols/error) and CLI `--health-check` behavior as required.
   - Tests: `tests/test_bab_realtime_feed.py` green (deterministic timestamps/mocks; network gated/opt-in only).

4. **Verification, commit, and handoff refresh (required before stopping):**
   - `python3 -m ruff check .` → exit 0
   - Targeted: `python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` → all pass
   - `python3 -m pytest -q` → all pass (baseline + changes)
   - `bash scripts/bab_gate.sh` → exit 0
   - Perf guardrail: `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Paper smoke: `python3 -m strategies.betting_against_beta.cli --paper-trading --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl` → exit 0, valid JSONL
   - Live adapter dry-run smoke (no implicit network): `python3 -m strategies.betting_against_beta.cli --adapter live --exchange binance --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check` with dummy env vars set as needed for dry-run path → exit 0, valid/clear JSON-safe output (or document exact supported dry-run invocation and make it pass)
   - Commit with evidence in message/body as appropriate; report `git log -1 --oneline`, `git status --short`, ruff, targeted/full pytest, gate, perf, paper smoke, live smoke.
   - **Refresh this handoff**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

**Acceptance:** P9 implemented/tested end-to-end (adapter + risk + realtime/SLA + CLI integration) with default offline/dry-run safety preserved, full suite + gate green, perf guardrail holds, paper + live dry-run smokes pass, committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets but keep full suite/gate green before stopping.
- Pandas/numpy warnings in stress tests and the existing `Timestamp.utcnow` deprecation in `tests/test_bab_data_freshness.py` are non-blocking unless they become behavioral regressions.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- `bab-example` console script requires `pip install -e .`; module CLI (`python3 -m strategies.betting_against_beta.cli`) is canonical.

### Protocol
1. Read this file fully. 2. Execute **P9** end-to-end (remove bottlenecks, complete adapter/risk/feed, verify, commit, refresh handoff). 3. Do not stop at analysis/research; land code + tests + evidence. 4. Refresh this handoff (UTC timestamp, HEAD, completed work with exact evidence, remaining gaps/risks, next binding task) before stopping. 5. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory (2026-11-14T22:23:04Z UTC):** Fix the 20 failing P9 tests in `tests/test_bab_risk_manager.py` and `tests/test_bab_realtime_feed.py` by aligning implementation/contracts and making tests deterministic (no weakening of SLA/risk guarantees). Complete P9 live execution readiness in `execution.py`, `risk.py`, `data_sources.py`, and `cli.py` as specified, keep default paths safe/offline/dry-run. Deliver exact evidence for ruff, targeted+full pytest, gate, perf baseline check, paper smoke, and live dry-run smoke, then commit and refresh this handoff. No analysis-only handoff.
