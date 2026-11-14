# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T16:30:06Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `99202bd05b5ce18cd52ca351d79e833abe6db6a0` (`chore(kilo): checkpoint agent session`) — trust live `git log -1 --oneline` / `git status` if they differ.
- **Branch:** `main` (clean at snapshot)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T16:30:06Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Make the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline and a recorded performance guardrail.

### Verified baseline (2026-11-14T16:30:06Z, no code changes)
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** |
| Real-data smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (finite) |
| Prior snapshot (2026-11-14T15:53:40Z) | full suite | 5674 passed / 35 skipped / 0 failed; 5709 collected; deps numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, ruff 0.17.5 |

**No P0/P1 bottlenecks.** P0 controller progress, ruff debt, beta/quality/monkeypatch issues, and Kilo edit-arg failures are resolved — do not reopen. If a new blocker appears: capture evidence and move on.

---

### Priority 1 — Baseline: COMPLETE
Skip unless touched. Do not re-run the full 5k+ suite unless strategy/runtime behavior changes.

### Priority 2 — Real data fetch/update pipeline (CORE PRODUCT, MANDATORY, HEAVY — DO FIRST)
**Why:** Strategy is green but real-data is a static fixture, not a reproducible idempotent fetch/update workflow. This is the unavoidable product work.

**Build on:** `strategies/betting_against_beta/data_loader.py` (strict: datetime index, numeric, no dupes, benchmark present, tz→UTC naive, dedup, drop all-NaN), `scripts/generate_real_market_fixture.py`, `scripts/load_real_bab_example.py`, `tests/fixtures/real_market_prices.csv` contract (`date`, BTC benchmark, asset columns).

**Deliverables (all required):**
1. **Runnable fetch/update entrypoint** (e.g. `scripts/fetch_real_bab_prices.py` or documented mode extension) outputting data in the exact schema/contract consumed by `load_prices`/`load_returns` so `BABStrategy.run(returns_df=...)` and `scripts/load_real_bab_example.py --from-prices` work without adaptation.
2. **Configurable:** symbols/universe, benchmark, date range/window, output path (CLI flags, sensible defaults).
3. **Idempotent incremental updates:** append new rows only, dedupe by date, sort, validate continuity/schema, never corrupt existing history.
4. **Source & failure semantics:** document data source and licensing/ToS. On fetch failure or missing network/credentials, **fail loudly or use a documented deterministic offline fallback — no silent bad/partial data**. Prefer a public no-auth source if feasible; otherwise make the offline/deterministic path first-class and reproducible.
5. **Focused automated tests** (targeted, reasonable runtime): schema contract, dedupe/sort/idempotent append, date handling, validation/error paths.

**Done when:** documented command creates/updates real-format data reproducibly; tests prove contract; `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` prints finite `cumulative_return`.

### Priority 3 — Performance baseline & regression guard
Use `scripts/perf_bench.py` on a real-format dataset (fixture or generated). Record baseline (timings/memory) in-repo (JSON/doc) and add a lightweight deterministic regression guard (baseline + compare script with tolerance or CI-friendly check), least invasive.

**Done when:** baseline recorded with command used and a repeatable check exists.

### Priority 4 — Evidence refresh & handoff maintenance
- Run/record only commands relevant to your changes (env/versions if changed, `ruff check .`, targeted tests, real-data fetch/update smoke, perf check).
- Update **this file**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, and the next binding task.
- Keep `AGENT_HANDOFF.md` as a pointer only. Commit coherent, reviewable changes; do not amend unrelated history.

### Known non-issues (do not churn)
- Large test suite intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P2→P3→P4; document blockers with evidence and continue. 3. Leave repo coherent and refresh this handoff before stopping.

**Next Agent Mandatory:** Complete **Priority 2** before anything else. Report: `ruff check .`, targeted real-data pipeline test output, `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` smoke (finite `cumulative_return`), and perf baseline evidence when reached. No analysis-only handoff.
