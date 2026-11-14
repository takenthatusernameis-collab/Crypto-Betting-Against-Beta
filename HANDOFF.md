# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-14T23:56:58Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD (at refresh):** `2ae2191` (`chore(kilo): checkpoint agent session`)
- **Branch:** `main`
- **Working tree:** clean (at refresh)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T23:56:58Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new parallel handoff/session docs. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

Repo-prioritized mission: `Crypto-Betting-Against-Beta` = harden the Betting Against Beta (BAB) crypto strategy into an ops-ready live path without changing default offline/dry-run behavior, then ship a release-ready evidence bundle. Everything below is heavy, concrete work — future agents must not avoid it.

### Current verified state (2026-11-14T23:56:58Z UTC, this workspace)
- `python3 -m ruff check .` → **All checks passed**.
- `python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` → **98 passed, 1 warning** (`tests/test_bab_data_freshness.py` `Timestamp.utcnow` deprecation; non-blocking).
- Live/risk/realtime suite trio: **85 passed** (`24 + 32 + 29`).
- Paper smoke: `python3 -m strategies.betting_against_beta.cli --paper-trading --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl` → exit 0 (`Paper trading: 160 orders, 160 fills`, `paper_pnl=-0.384799 backtest_pnl=-0.6602645030669475 diff=0.275465`).
- Live dry-run smoke: `python3 -m strategies.betting_against_beta.cli --adapter live --exchange binance --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check` → exit 0; prints health (`connected False`, `dry_run True`, `testnet False`).
- Perf guardrail: `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`.
- Full suite and `bash scripts/bab_gate.sh` were invoked in prior sessions; re-run if your environment differs and record evidence (they are large; prefer targeted first, then full/gate before stopping).

### Bottlenecks removed (do not reopen unless regression)
1. **P9 RiskManager/realtime test blockers addressed** (risk defaults/semantics, kill-switch/flatten behavior, realtime deterministic `now`/timestamps/stubs). Treat current green trio as baseline; do not churn without a failing test or concrete bug.
2. **No parallel handoff files to reconcile**: only `HANDOFF.md` is canonical; `AGENT_HANDOFF.md` is pointer-only; `AGENT_TASK_2026-11-14.md` and `HANDOFF_TASK_20261114.md` are SUPERSEDED — do not edit.
3. Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
4. Ruff debt and P0 workflow bottlenecks resolved; `ruff check .` exits 0 and full suite is green.

### Next focus campaign (build the future — no analysis-only handoff)
**Goal:** harden P9 into “ops-ready” BAB live path without changing default offline/dry-run behavior, then produce a release-ready evidence bundle.

**Priority order (execute top-down; stop only when every checked item has evidence or is explicitly blocked with exact error):**

1. **Close verification gaps (if not already proven in your run):** run and record
   - `python3 -m pytest -q` (full)
   - `bash scripts/bab_gate.sh`
   If slow, run targeted slices first, but you must finish full + gate before final handoff refresh/commit claim.
2. **Live adapter operational hardening (code + tests as needed):** in `strategies/betting_against_beta/execution.py`/`cli.py`, ensure `LiveExecutionAdapter` path is safe-by-default (no implicit network), env-only creds, clear errors on missing deps/config, and `--health-check` output is strict JSON-serializable where practical (document any human-readable exceptions). Add/adjust tests only for real contracts.
3. **RiskManager integration completeness:** verify integration points with paper/live paths preserve default behavior; if gaps exist (e.g. pre-trade not wired in a live entrypoint), implement minimally and add focused tests. Do **not** weaken limits or add silent fallbacks.
4. **Realtime/SLA production posture:** confirm `data_sources.py` `RealtimeFeed`/`CCXTFeed`/`WebSocketFeed` semantics, deterministic testing hooks, and `validate_freshness`/CLI health behavior remain strict (`BABDataError` on violation). Add tests only for uncovered real failure modes.
5. **Docs + CLI discoverability:** update `README.md`/CLI help text only where needed to reflect current `--adapter live` dry-run health/smoke workflow and safety guarantees (no new docs files).
6. **Evidence + commit + handoff refresh (required):** when changes are made, commit with a clear message and report `git log -1 --oneline`, `git status --short`, ruff, targeted trio, full pytest, gate, perf, paper smoke, live smoke. Then refresh this `HANDOFF.md` (and `AGENT_HANDOFF.md` pointer timestamp/HEAD) with a new UTC timestamp and the next concrete task (or “done” state with remaining risks listed).

**Acceptance for this campaign:** any code changes are tested (ruff + targeted + full + gate as applicable), perf guardrail holds, paper + live dry-run smokes pass, docs/CLI accurate if touched, all evidence recorded, and this handoff updated to a new UTC timestamp with the next concrete task (or “done” state with remaining risks listed). No analysis-only stopping point.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate targeted, then finish full/gate before stopping.
- `Timestamp.utcnow` deprecation warning in `tests/test_bab_data_freshness.py` is non-blocking unless behavioral.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli` (`bab-example` may require editable install).

### Protocol
1. Read this file fully. 2. Execute the “Next focus campaign” top-down; prefer minimal, tested diffs. 3. Never stop at analysis. 4. Keep `AGENT_HANDOFF.md` as pointer only.
