# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).**
**Timestamp (UTC):** 2026-11-14T13:33:09Z
**Repo:** `Crypto-Betting-Against-Beta`
**HEAD at refresh:** `81ad095` (chore(kilo): checkpoint agent session) — trust live output over this file if they differ.
**Branch:** `main` (in sync with `origin/main` at refresh)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T13:33:09Z UTC) — BINDING

Execute the next focus campaign in order. Do not do probe archaeology, do not add parallel handoff/session docs, and do not re-verify already-green areas unless your change touches them.

### Campaign objective
Drive **real-data readiness and engineering hygiene** for the Crypto Betting Against Beta (BAB) strategy so future runs can ingest live/updated market data reproducibly, keep CI/lint clean, and expose performance baselines.

### Priority 1 — Lint baseline repair (bottleneck removal)
**Why:** `python -m ruff check .` currently reports **128 errors** (mostly `E501` line-length in tests; 1 unsafe fix available). A red lint baseline blocks disciplined progress and obscures real regressions.
- Fix violations with behavior-preserving edits (prefer wrapping/splitting strings/comments/assertions in tests; avoid changing test intent).
- Use `ruff check .` / targeted file fixes; apply `--unsafe-fixes` only if you have verified safety case-by-case (default: avoid unsafe).
- Do not weaken lint policy in `pyproject.toml` unless absolutely necessary and explicitly justified in commit/handoff update.
- **Done when:** `python -m ruff check .` exits 0 (or remaining issues are documented with evidence why they cannot be fixed safely in-repo).

### Priority 2 — Real data pipeline hardening (core product work)
**Why:** Strategy is mature in tests/synthetic paths, but operational real-data workflow is thin.
- Build on existing `strategies/betting_against_beta/data_loader.py`, `scripts/generate_real_market_fixture.py`, and `scripts/load_real_bab_example.py`.
- Implement a reproducible **fetch/update path** for real market prices/returns (e.g. extend generator or add `scripts/fetch_real_data.py`) that:
  - produces the same schema as `tests/fixtures/real_market_prices.csv` (`date` + BTC benchmark + asset columns),
  - supports configurable date range/window and output path,
  - supports incremental append/update without corrupting history (dedupe/sort/validate),
  - documents data source, licensing/ToS constraints, and failure modes (no silent bad data).
- Prefer public, no-auth sources where feasible; if network access/credentials are unavailable in CI/runtime, provide a deterministic offline fallback and clearly document it.
- Add/adjust tests for the new behavior (validation, idempotent updates, schema contract) without bloating runtime unnecessarily.
- **Done when:** there is a documented, runnable command to obtain/update real data into the expected format and automated tests cover the contract.

### Priority 3 — Performance baseline & regression guard
- Use `scripts/perf_bench.py` (and real fixture path) to establish a recorded baseline (latency/memory/cumulative_return or equivalent available metrics).
- Add a lightweight, deterministic way to detect regressions (script output artifact, checked-in baseline JSON with tolerance, or CI-friendly check) — choose the least invasive option that is reliable in this environment.
- **Done when:** baseline is captured/documented and a repeatable check exists for future agents.

### Priority 4 — Evidence refresh & handoff maintenance
- Run and record only the commands relevant to what you changed (lint, targeted tests, real-data script smoke, perf check).
- Update **this file** with: new UTC timestamp, new HEAD, what was completed, exact evidence/commands, remaining gaps, and the next binding task.
- Keep `AGENT_HANDOFF.md` as a pointer only (no competing directives).

## Verified baseline (at refresh)
- `python -m pytest tests/test_bab_data_loader_campaign_heavy.py -q` → **46 passed** (0.52s).
- `python -m pytest --co -q` → **5709 tests collected** (1.24s).
- `python -m ruff check .` → **128 errors** (lint cleanup required).
- Key assets present: `strategies/betting_against_beta/` (full BAB pipeline), `scripts/load_real_bab_example.py`, `scripts/generate_real_market_fixture.py`, `tests/fixtures/real_market_prices.csv`, `scripts/perf_bench.py`.
- No `workflow_diagnostics/` directory present at refresh.

## Known non-issues (do not churn)
- Large test suite is intentional; run targeted subsets while iterating.
- Pandas 4 / numpy warnings in stress tests are expected unless they indicate a real behavioral regression.
- Root contains historical probe/debug scripts (`probe_*.py`, `debug_*.py`, `ast_probe.py`) — ignore unless directly relevant; do not spend cycles on probe archaeology.

## Handoff protocol
1. Read this file fully before acting.
2. Execute priorities in order unless blocked by hard evidence; document any blocker with command output.
3. Leave the repo in a coherent, reviewable state and refresh this handoff before stopping.
