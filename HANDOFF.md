# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T01:58:19Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD (at refresh):** `050c8bc` (`chore(kilo): checkpoint agent session`)
- **Branch:** `main`
- **Working tree:** clean at refresh; `python3 -m ruff check .` → All checks passed.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T01:58:19Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new parallel handoff/session docs. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

Repo-prioritized mission: `Crypto-Betting-Against-Beta` = keep the Betting Against Beta (BAB) crypto strategy ops-ready (live path dry-run-safe-by-default, default offline/dry-run behavior unchanged) and close remaining coverage/gate gaps to a release-ready state.

## Current verified state (as of 2026-11-15T01:30:13Z refresh; re-verify after changes)

- `python3 -m ruff check .` → clean (re-verified 2026-11-15T01:58:19Z).
- Targeted trio (`test_bab_live_adapter.py test_bab_risk_manager.py test_bab_realtime_feed.py test_bab_paper_trading.py test_bab_data_freshness.py test_bab_diagnostics.py`) → **104 passed, 1 warning** (`Timestamp.utcnow` deprecation; non-blocking).
- Full suite `python3 -m pytest -q` → **5831 collected**; gate `bash scripts/bab_gate.sh` → **5796 passed, 35 skipped, 0 failed**, coverage **TOTAL 90%**.
- Perf guardrail → `failures: []`. Paper smoke exit 0. Live dry-run smoke exit 0; `--health-check` prints strict JSON.
- Default offline/dry-run behavior unchanged; live execution safe-by-default (dry-run, env-only creds, no implicit network).

## Next focus campaign (P10: coverage & hygiene hardening) — HEAVY WORK, DO NOT DEFER

**Goal:** materially reduce coverage-risk in real failure paths while keeping the gate green and default behavior byte-identical.

### Priority order (execute top-down)

1. **Re-establish baseline evidence (mandatory first step)**
   - Run and record: `python3 -m ruff check .`, targeted trio above, then `python3 -m pytest -q` and `bash scripts/bab_gate.sh` (full suite is slow ~16 min; iterate targeted slices first but finish full+gate before claiming done). Capture pass/skip/fail counts, TOTAL coverage, and per-file coverage for `strategies/betting_against_beta/cli.py`, `data_sources.py`, `execution.py`.
2. **`cli.py` (was 77%) — real uncovered paths**
   - Add focused tests for genuine uncovered failure/edge modes (argument validation/conflict paths, adapter/mode error branches, I/O/output/health-check edge cases that are actually reachable). Exercise via CLI entrypoints/`main` as appropriate; no speculative tests, no behavior changes to default path.
3. **`data_sources.py` (was 78%) — fetch/parse/error hardening**
   - Add tests for real uncovered branches: retry/rate-limit/error handling, schema/parse failures, partial/missing data, source selection/validation paths consistent with README failure modes. Keep offline deterministic default unchanged; public API must remain explicit opt-in with loud failures.
4. **`execution.py` (was 81%) — adapter failure modes (dry-run safe)**
   - Add tests for uncovered `LiveExecutionAdapter`/paper/mock branches (error/rejection/fill/diagnostic paths, risk-gating edge cases, connector/health edge cases) using fakes/mocks only — **no real network, no credentials, no enabling real execution**.
5. **Deprecation hygiene**
   - In `tests/test_bab_data_freshness.py` (and any other occurrences), migrate `Timestamp.utcnow` → timezone-aware `pd.Timestamp.now("UTC")`/equivalent only if semantics remain identical; keep tests/warnings clean without behavior change.
6. **Final gate & handoff refresh**
   - Re-run ruff, targeted trio, full `pytest -q`, `bab_gate.sh`, perf guardrail, paper + live dry-run smokes. Update this file with new UTC timestamp, HEAD, exact evidence (counts/coverage deltas for the three files), and the next concrete campaign. Keep `AGENT_HANDOFF.md` as pointer only.

**Acceptance:** ruff clean; full pytest + `bab_gate.sh` green (0 failed); coverage improved on `cli.py`/`data_sources.py`/`execution.py` with no regression elsewhere; perf guardrail `failures: []`; paper + live dry-run smokes pass; default offline/dry-run behavior unchanged.

## Bottlenecks / constraints (do not reopen)

- **No parallel handoff files** — only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only. `AGENT_TASK_2026-11-14.md`, `HANDOFF_TASK_20261114.md` SUPERSEDED — do not edit.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- Large suite intentional; iterate targeted, finish full+gate before stopping/committing claims.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli`.
- Real (non-dry-run) live execution is out of scope; never enable without explicit opt-in and credential review.

## Protocol
1. Read this file fully. 2. Execute "Next focus campaign" top-down; minimal, tested diffs. 3. Never stop at analysis. 4. Keep `AGENT_HANDOFF.md` pointer only.
