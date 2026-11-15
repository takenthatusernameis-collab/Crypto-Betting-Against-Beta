# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T00:46:04Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD (at refresh):** `ac7b9e9` (`feat(p9): harden live execution adapter and wire optional pre-trade risk gating`)
- **Branch:** `main`
- **Working tree:** clean (at refresh)

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T00:46:04Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new parallel handoff/session docs. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

Repo-prioritized mission: `Crypto-Betting-Against-Beta` = harden the Betting Against Beta (BAB) crypto strategy into an ops-ready live path without changing default offline/dry-run behavior, then ship a release-ready evidence bundle.

## Campaign status: COMPLETE (all six priorities done, evidence recorded)

The P9 "ops-ready live path" campaign is complete. Default offline/dry-run behavior is unchanged; live execution is safe-by-default (dry-run, env-only creds, no implicit network).

### Current verified state (2026-11-15T00:46:04Z UTC, this workspace)
- `python3 -m ruff check .` → **All checks passed**.
- Targeted trio (`test_bab_live_adapter.py test_bab_risk_manager.py test_bab_realtime_feed.py test_bab_paper_trading.py test_bab_data_freshness.py test_bab_diagnostics.py`) → **98 passed, 1 warning** (`Timestamp.utcnow` deprecation; non-blocking).
- Full suite `python3 -m pytest -q` → **5790 passed, 35 skipped, 0 failed** (~16 min).
- `bash scripts/bab_gate.sh` → **5796 passed, 35 skipped, 0 failed**, coverage **TOTAL 90%**.
- Perf guardrail → `failures: []`.
- Paper smoke → exit 0 (`Paper trading: 160 orders, 160 fills`, `paper_pnl=-0.384799 backtest_pnl=-0.6602645030669475 diff=0.275465`).
- Live dry-run smoke → exit 0; `--health-check` now prints one strict JSON object (`{"mode": "live", "exchange": "binance", "connected": false, "dry_run": true, ...}`).

### What changed (commit `ac7b9e9`, 4 files, +264/-11)
1. `strategies/betting_against_beta/execution.py` — `LiveExecutionAdapter` gained optional, opt-in `RiskManager` pre-trade gating (`risk_manager`/`current_positions`/`cumulative` constructor args). Off by default → default path byte-identical, no risk checks, no silent fallbacks. When wired, breached assets yield explicit `status="rejected"` fills; portfolio-level breach / kill-switch rejects the whole batch. Safe-by-default: `dry_run=True`, env-only credentials, lazy `ccxt` import (no implicit network).
2. `strategies/betting_against_beta/cli.py` — `--health-check` now emits a single strict-JSON object (machine-parseable, CI-gateable) instead of human-readable lines; human-readable text reserved for the `--adapter live` requirement error path.
3. `tests/test_bab_live_adapter.py` — added `TestLiveExecutionAdapterRiskGating` (no-risk-manager passthrough, asset-position-limit rejection, portfolio gross-exposure whole-batch rejection, kill-switch rejects all) and `TestLiveExecutionAdapterHealthJSON` + `test_cli_health_check_emits_strict_json` (adapter dict and CLI output strict-JSON-safe).
4. `README.md` — documented `--adapter paper/mock/live`, env-only credentials, dry-run default, and `--health-check` strict JSON output (no new docs files).

### Bottlenecks removed (do not reopen unless regression)
1. **P9 RiskManager/realtime test blockers addressed** — baseline green; do not churn without a failing test or concrete bug.
2. **No parallel handoff files** — only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only; `AGENT_TASK_2026-11-14.md` and `HANDOFF_TASK_20261114.md` SUPERSEDED — do not edit.
3. Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
4. Ruff debt and P0 workflow bottlenecks resolved; `ruff check .` exits 0.

## Next focus campaign (maintain the green gate)

**Goal:** keep the BAB live path ops-ready and the gate green; do not regress default offline/dry-run behavior.

**Remaining risks / next concrete work (do not avoid):**
1. **Gate before any claim:** any future change must re-run `python3 -m pytest -q` (full) and `bash scripts/bab_gate.sh` and pass before a completion/commit claim. Full suite is large (~16 min); iterate targeted slices first, then finish full + gate.
2. **Coverage-risk modules:** total coverage 90% but `cli.py` 77%, `data_sources.py` 78%, `execution.py` 81% are below the ceiling. Add focused tests only for real, uncovered failure modes — do not add coverage for coverage's sake.
3. **`Timestamp.utcnow` deprecation** in `tests/test_bab_data_freshness.py:58` — non-blocking unless behavioral; consider migrating to `Timestamp.now("UTC")` only if it breaks.
4. **Real (non-dry-run) live execution** is intentionally untested (requires network/credentials) and out of scope; the live path remains dry-run-safe-by-default. Do not enable real execution without explicit opt-in and credential handling review.

**Acceptance:** ruff clean, full pytest + gate green, perf guardrail holds, paper + live dry-run smokes pass, docs/CLI accurate, handoff at a new UTC timestamp with this task (done state + risks above) or the next concrete task.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate targeted, then finish full/gate before stopping.
- `Timestamp.utcnow` deprecation warning in `tests/test_bab_data_freshness.py` is non-blocking unless behavioral.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli` (`bab-example` may require editable install).

### Protocol
1. Read this file fully. 2. Execute the “Next focus campaign” top-down; prefer minimal, tested diffs. 3. Never stop at analysis. 4. Keep `AGENT_HANDOFF.md` as pointer only.
