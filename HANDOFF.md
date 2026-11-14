# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).**
**Timestamp (UTC):** 2026-11-14T15:52:23Z
**Repo:** `Crypto-Betting-Against-Beta`
**HEAD:** `8fd0812d994559b976509bc233029b5cdab2789e` (`chore(kilo): checkpoint agent session`) — trust live `git log --oneline -3` / `git status` over this file if they differ.
**Branch:** `main` (clean working tree)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T15:52:23Z UTC) — BINDING

Execute this campaign in order. Do **not** do probe/debug archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), do **not** create parallel handoff/session/task docs, and do **not** re-verify already-green areas unless your change touches them. If a step is blocked, produce concrete evidence (exact command + output summary) and continue with the next unblocked priority; never stop at analysis.

### Campaign objective
Make the Betting Against Beta (BAB) crypto strategy **operational on real, updatable market data** with a clean lint/test baseline and a recorded performance guardrail.

---

### Status snapshot (2026-11-14T15:52:23Z, pre-change) — all green

| Check | Command | Result |
|-------|---------|--------|
| Deps | `python3 -m pip show numpy pandas scipy pytest ruff` | numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, ruff 0.17.5 — all installed |
| Lint baseline | `python3 -m ruff check .` | **All checks passed** (0 errors; was 128 debt, now cleared) |
| Collection | `python3 -m pytest --co -q` | **5709 collected** |
| Full suite | `python3 -m pytest -q -p no:cacheprovider` | **5674 passed, 35 skipped, 0 failed** (9m32s) |
| Controller progress (P0) | `python3 -m pytest tests/test_controller_progress_accounting.py -q` | **69 passed** (workflow `stage_safe_changes` is in lock-step with Python `EXCLUDE_PATTERNS`; no pattern mismatch) |
| Git | `git status --porcelain` | clean; HEAD `fedcd89` on `main`, up to date with `origin/main` |

### Bottlenecks removed (do not reopen)
- **P0 CI `stage_safe_changes` pattern sync** — resolved; `test_controller_progress_accounting.py` passes (69/69). Workflow bash case list and Python `EXCLUDE_PATTERNS` are in lock-step.
- **Kilo `edit` invalid-argument loops** — no active failures; keep every `edit` call well-formed (`filePath` + `oldString` + `newString`), small and verifiable.
- **Ruff debt (128 errors)** — cleared; `ruff check .` exits 0. Do not regress policy.
- **Beta edge-case / quality-score / `monkeypatch` failures** on the old PR branch — resolved; full suite is 0 failures.

**No remaining P0/P1 bottlenecks.** If you find one, record exact command + output, then continue with the next priority.

---

### Priority 1 — Environment & quality baseline — COMPLETE (baseline above)
Skip unless a change touches lint/config. Do not re-run the full suite unless modifying strategy code.

### Priority 2 — Real data fetch/update pipeline (CORE PRODUCT WORK — NEXT)

**Why:** Strategy logic is mature and green, but the real-data workflow is still a static fixture, not a reproducible, idempotent fetch/update pipeline. This is the heavy, unavoidable work.

Build on `strategies/betting_against_beta/data_loader.py` (strict validator: datetime index, numeric columns, no duplicates, benchmark present, tz->UTC naive, dedup, drop all-NaN), `scripts/generate_real_market_fixture.py`, `scripts/load_real_bab_example.py`, and fixture contract in `tests/fixtures/real_market_prices.csv` (`date` + BTC benchmark + asset columns; loader-compatible schema).

Implement a runnable **fetch/update** entrypoint (e.g. `scripts/fetch_real_bab_prices.py` and/or extend the generator with a documented mode) that:
1. Outputs price/returns data in the same schema/contract consumed by `load_prices`/`load_returns` (so `BABStrategy.run(returns_df=...)` and `scripts/load_real_bab_example.py --from-prices` consume it without adaptation).
2. Accepts configurable symbols/universe, benchmark, date range/window, and output path (CLI flags, sensible defaults).
3. Performs **idempotent incremental updates**: append new rows, dedupe by date, sort, validate continuity/schema, never corrupt existing history.
4. Documents the data source and licensing/ToS constraints; on fetch failure or missing network/credentials, **fails loudly or provides a documented deterministic offline fallback — no silent bad/partial data**.
5. Prefers a public, no-auth source if feasible in this environment; if unavailable, makes the offline/deterministic path first-class and explicitly documented so runs remain reproducible.

Add focused automated tests for: schema contract, dedupe/sort/idempotent append, date handling, and validation/error paths (runtime reasonable; targeted loader/script tests, not the whole 5k+ suite).

**Done when:** a documented command can create/update real-format data reproducibly and tests prove the contract; `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` runs and prints a finite `cumulative_return`.

### Priority 3 — Performance baseline & regression guard

Use `scripts/perf_bench.py` (and a real-format dataset path, fixture or generated) to capture a baseline (timings/memory). Add a lightweight deterministic regression guard (checked-in baseline JSON + compare script with tolerance, or CI-friendly check) — least invasive, reliable in this environment.

**Done when:** baseline is recorded in-repo/docs with command used and a repeatable check exists.

### Priority 4 — Evidence refresh & handoff maintenance

- Run and record only commands relevant to your changes (env/versions, lint, targeted tests/collection, real-data fetch/update smoke, perf check).
- Update **this file**: new UTC timestamp, new HEAD, completed work, exact evidence, remaining gaps/risks, and the next binding task.
- Keep `AGENT_HANDOFF.md` as a pointer only. Commit coherent, reviewable changes; do not amend unrelated history.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests are expected unless they indicate behavioral regression.
- Historical `probe_*.py` / `debug_*.py` / `ast_probe.py` in root: ignore unless directly required.

### Handoff protocol
1. Read this file fully before acting.
2. Execute priorities in order; document blockers with command evidence and continue where possible.
3. Leave repo coherent and refresh this handoff before stopping.

**Next Agent Mandatory:** Priority 2 (real data fetch/update pipeline) is the heavy, unavoidable work and must be executed before Priority 3 or 4 — do not skip or defer it. Report completion with `ruff check .`, targeted real-data pipeline test output, `scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` smoke output (finite `cumulative_return`), and perf baseline evidence.
