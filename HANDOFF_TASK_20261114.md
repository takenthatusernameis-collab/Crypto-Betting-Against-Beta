# Agentic Work Session Handoff — 2026-11-14T14:29:40Z

## Project Context
**Repository:** `Crypto-Betting-Against-Beta`
**Core Mission:** Implement and harden the **Betting Against Beta (BAB)** market-neutral strategy for crypto — long low-beta assets, short high-beta assets vs. BTC benchmark (Frazzini-Pedersen approach).

## Current State Summary
- **Tests:** 5,709 collected, core suites passing (signals, metrics, backtest contract, strategy regressions, CLI parity)
- **CI Workflow:** Scheduled every 5 min + push to `main`; runs controller tests → diagnostics scan → Kilo agent loop (1000 sessions, 355 min cutoff)
- **Known CI Failures (recurring):**
  1. `test_controller_progress_accounting.py::TestStageSafeChangesPatternSync` — Python `EXCLUDE_PATTERNS` missing `*/.github/workflows/*` from workflow's `stage_safe_changes` list
  2. Kilo `edit` tool invalid-argument aborts (3 consecutive → turn aborted)
  3. PR branch `fix/bab-beta-data-edgecases-20261030` had beta edge-case test failures (mixed timezones, `gross_return` KeyError, `monkeypatch` NameError, quality score bound)

## Immediate Bottlenecks to Remove
| Priority | Bottleneck | Action Required |
|----------|------------|-----------------|
| **P0** | CI `stage_safe_changes` pattern mismatch | Add `*/.github/workflows/*` to `stage_safe_changes` in workflow YAML (line ~62) OR remove from Python `EXCLUDE_PATTERNS` in `scripts/controller_progress.py` |
| **P0** | Kilo `edit` tool invalid-argument loops | Ensure all `edit` calls include `filePath`, `oldString`, `newString`; add pre-flight validation in agent prompt |
| **P1** | Beta edge-case test failures on PR branch | Fix mixed timezone handling in beta calculation; ensure `gross_return` column exists in backtest output; import `monkeypatch` in test files; clamp quality score to `[0.3, 0.4]` range |

## Next Focus Campaign — Heavy Work That Cannot Be Avoided
The next agent **must** execute the following campaign to unblock significant progress:

### Phase 1: CI Stabilization (Do First — 30 min max)
1. **Fix workflow pattern sync** — Edit `.github/workflows/main.yml` to include `*/.github/workflows/*` in `stage_safe_changes` (or update Python side). Verify `test_controller_progress_accounting.py` passes locally.
2. **Harden Kilo edit calls** — Add a wrapper/validator that asserts required fields before every `edit` tool call. Document in AGENTS.md.

### Phase 2: Beta Calculation Robustness (Core Strategy — 2–4 hrs)
3. **Timezone-safe beta** — In `strategies/betting_against_beta/beta.py`, ensure all datetime indices are `tz-aware UTC` before OLS; add `utc=True` to `pd.to_datetime` calls.
4. **Backtest column guarantee** — In `backtest.py`, guarantee `gross_return` column exists even on empty/edge-case frames.
5. **Quality score bounds** — In `quality.py`, clamp combined penalty to `[0.3, 0.4]` so `test_quality_score_penalties_are_bounded_and_combined` passes.

### Phase 3: Test Coverage Closure (Mandatory — 1–2 hrs)
6. **Run full test suite with `pytest -x --tb=short`** — Target 0 failures, 0 errors. If any test fails, write a minimal fix (TDD: failing test → understand → fix → green).
7. **Add missing `monkeypatch` imports** in any test file using it (`test_bab_data_loader_edgecases.py`, `test_bab_quality.py`).

### Phase 4: Real-Data Pipeline Hardening (High Value — 2–3 hrs)
8. **End-to-end real data test** — Use `scripts/generate_real_market_fixture.py` → `scripts/load_real_bab_example.py` → CLI `--from-prices` → verify JSON output finite keys, determinism, parity with in-process run.
9. **Execution adapter (R5-A) smoke test** — Instantiate paper adapter, run strategy with `execution_adapter`, verify `execution_payload` populated with intents/fills.

## Success Criteria for This Campaign
- ✅ All 5,709 tests pass (`pytest -q` exits 0)
- ✅ CI workflow `main.yml` passes on push (no pattern-sync failures)
- ✅ Kilo agent runs ≥10 sessions without `edit` invalid-argument abort
- ✅ Real-data CLI produces finite JSON with `cumulative`, `sharpe_ratio`, `max_drawdown`
- ✅ `BABStrategy.run(execution_adapter=...)` returns non-None `execution` payload

## Files to Touch First
```
.github/workflows/main.yml                    # P0 pattern sync
scripts/controller_progress.py                # P0 EXCLUDE_PATTERNS (if workflow not changed)
strategies/betting_against_beta/beta.py       # P1 timezone safety
strategies/betting_against_beta/backtest.py   # P1 gross_return guarantee
strategies/betting_against_beta/quality.py    # P1 quality score clamp
tests/test_bab_data_loader_edgecases.py       # P1 monkeypatch import
tests/test_bab_quality.py                     # P1 monkeypatch import + bound test
```

## Anti-Patterns to Avoid
- ❌ Do NOT skip failing tests — fix them or delete if obsolete
- ❌ Do NOT add workaround comments — fix root cause
- ❌ Do NOT commit without running `ruff check` and `pytest -q`
- ❌ Do NOT create new test files unless covering a new feature; extend existing

## Escalation
If any Phase 1 task takes >45 min, **stop and report** — the pattern sync is a 5-line fix. If Phase 2 reveals deeper beta math issues, open a GitHub issue with minimal repro and move to Phase 3/4 in parallel.

---

**Next Agent Mandate:** Execute Phase 1 → Phase 2 → Phase 3 → Phase 4 sequentially. No shortcuts. Report completion with `pytest -q` output and CI green status.