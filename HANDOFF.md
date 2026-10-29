# HANDOFF - 2026-10-29T16:37:46Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T16:30:01Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync FIXED FOR REAL:** `.github/workflows/main.yml` `stage_safe_changes` case list was missing `*/.github/workflows/*`. Added it now (parity with `scripts/controller_progress.py` EXCLUDE_PATTERNS). `tests/test_controller_progress_accounting.py` → **68 passed**. **2 controller accounting failures eliminated.**
- **Baseline restored GREEN:** `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped**. Deterministic baseline confirmed.

## COVERAGE BASELINE (MEASURED 2026-10-29T16:47:01Z)
**Overall across `strategies/betting_against_beta/`: 84% (2426 stmts, 388 missing)** — was 78% (537 missing) at session start.

Worst gaps (attack in this order):
- `strategy.py` 62% (75 missing) — PRIMARY TARGET
- `beta.py` 71% (63 missing)
- `data_loader.py` 79% (59 missing)
- `config.py` 79% (41 missing)
- `shorting.py` 80% (35 missing)
- `costs.py` 81% (29 missing)
- `quality.py` 87% (22 missing)
- `regime.py` 90% (18 missing)
- `data_sources.py` 80% (13 missing)
- `portfolio.py` 94% (14 missing)
- `backtest.py` 91% (7 missing)
- `signals.py` 96% (4 missing: 28, 37, 71, 75)
- `metrics.py` 96% (5 missing: 71, 97, 174, 187-188 — mostly unreachable defensive branches)
- `sizing.py` 99% (2 missing: 55, 96)
- `__init__.py`, `attribution.py`, `data.py`, `errors.py`: 100%

Target: **>=95%** overall (<= ~121 missing statements).

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be green: suite now expects 664 passed, 0 failed, 8 skipped (was 602/0/8 at baseline; 62 deterministic offline tests added this session)
```

**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## FOCUS CAMPAIGN (UNAVOIDABLE)
### Priority 5: Testing & Robustness — IN PROGRESS (HEAVY — COVERAGE CRUSADE)
- [x] Beta parity regression (multi-seed, NaN/inf)
- [x] Config-matrix stress (regime/shorting/sizing/costs), determinism + finiteness
- [x] Report CLI edge cases
- [x] Signals/portfolio edge cases, dollar neutrality
- [x] Data loader robustness (malformed/mixed types/bad dates/dupes/timezones/gaps/all-NaN)
- [x] Deterministic property-style fuzzing across signals/portfolio/data_loader/backtest (seeded, offline)
- [x] Coverage crusade launched: 78% → 84% overall across `strategies/betting_against_beta/` (537 → 388 missing statements)
- [x] `metrics.py` 77% → 96% (deterministic offline tests added; happy + edge + error paths)
- [x] `signals.py` 51% → 96% (added `_finite_beta_series` + `_reference_generate_bab_signals` + quantile-clamp coverage; FIXED latent bug: read-only `to_numpy(copy=False)` view crashed on object-dtype beta input with string entries — `signals.py:38-44`)
- [x] `sizing.py` 83% → 99% (validation errors, string shorthands kelly/kelly_fraction/vol_target/volatility_target/voltarget/risk_parity/riskparity/rp, unknown-sizer error, no-common-index, missing-columns, zero-variance Kelly k=0, zero-variance vol-target scale=0, risk-parity target_vol None and set)
- [x] `portfolio.py` 78% → 94% (`_clean_signal_value` None/nan/string/numeric/type-error branches, max_position_size kw alias + bad-type passthrough, max_turnover bad-type passthrough, risk-checks bad-gross-limit defaults, enforce_beta_neutrality empty/equal-betas/no-finite-beta/zero-denom/correction=False/target-nan branches)
- [x] `backtest.py` 73% → 91% (None inputs, non-DataFrame convert-fail, disjoint-column positional alignment, costs+slippage, cost_model TypeError, lagged-weights parity)
- [ ] **COVERAGE CRUSADE (CONTINUE):** Raise coverage across `strategies/betting_against_beta/` to **>=95%** (388 → <= ~121 missing statements). Attack order: `strategy.py` (62%) → `beta.py` (71%) → `data_loader.py` (79%) → `config.py` (79%) → `shorting.py` (80%) → `costs.py` (81%) → `quality.py` (87%) → `regime.py` (90%) → `data_sources.py` (80%) → `portfolio.py` (94%) → `backtest.py` (91%) → `signals.py` (96%) → `metrics.py` (96%) → `sizing.py` (99%). Deterministic, offline, seeded tests; happy + edge + error paths; no bare `except:`; enforce finiteness/determinism; TDD (failing test → minimal impl → green → refactor).

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## NEXT HEAVY TASK (FOCUS FOR NEXT SESSION — DO NOT DEFER)
**CONTINUE THE COVERAGE CRUSADE ACROSS `strategies/betting_against_beta/` UNTIL >=95%.** Next session: attack `strategy.py` (62%, 75 missing statements) and `beta.py` (71%, 63 missing) with deterministic offline tests, then `data_loader.py`, `config.py`, `shorting.py`. Multi-file substantive hardening touching >=4 files required per session.

**IMMEDIATE ACTIONS (EXECUTE IN ORDER):**
1) **Baseline gate:** `python3 -m pytest -q` → must be 664 passed, 0 failed, 8 skipped (suite now includes 62 tests added this session).
2) **Measure ruthlessly:** `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` → identify untested branches/lines; missing must shrink from 388 to <= ~121 for >=95%.
3) **Attack gaps systematically:** TDD on `strategy.py` first (largest gap), then `beta.py`, `data_loader.py`, `config.py`. Write failing tests → minimal implementation → green → refactor.
4) **Harden brittle paths:** fix uncovered brittle code where found (no bare `except:`, preserve behavior, enforce finiteness/determinism).
5) **Touch >=4 files** with real logic/tests per session.
6) **Validate:** `python3 -m pytest -q` >= 664 passed, 0 failed, 8 skipped; coverage across `strategies/betting_against_beta/` pushed toward **>=95%**; no regressions.
7) **Update THIS FILE (`HANDOFF.md`) with timestamp, completed work, bottlenecks removed, next concrete heavy task. ONLY `HANDOFF.md` MATTERS.**

**THIS IS NOT OPTIONAL. HEAVY WORK IS MANDATORY.**

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes across >=4 files when changing strategy code. If < 4 files touched with real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain >=602 passed, 0 failed, 8 skipped
- **SINGLE HANDOFF:** Update THIS FILE after significant progress. ONLY `HANDOFF.md` MATTERS.
- **NO COMMITS UNLESS ASKED**

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green
2. Do PRIMARY HEAVY TASK first (TDD, multi-file). No exploration detours.
3. Implement production-grade solution across multiple files → all tests pass → refactor
4. Validate full suite, check regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task
6. Continue heavy work — never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**

## SESSION UPDATE - 2026-10-29T15:53:26Z (CURRENT)
- **Bottleneck removed (REAL):** `.github/workflows/main.yml` `stage_safe_changes` case list was missing `*/.github/workflows/*` (nested pattern). Added it; `tests/test_controller_progress_accounting.py` → **68 passed**. Both previously failing controller tests now pass.
- **Baseline:** `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped** (restored to green).
- **Coverage measured:** **66% overall** across `strategies/betting_against_beta/` (2424 stmts, 818 missing). Critical gaps: `metrics.py` 12%, `sizing.py` 50%, `signals.py` 51%, `portfolio.py` 59%, `backtest.py` 59%, `beta.py` 61%, `strategy.py` 62%.
- **Next heavy task (UNAVOIDABLE):** Coverage crusade to **>=95%** across `strategies/betting_against_beta/`; substantive multi-file hardening touching >=4 files; no regressions. **Start with metrics.py (12%)** - add comprehensive deterministic tests. Then attack signals/strategy/beta/backtest/portfolio/sizing/costs/shorting. Validate full suite >=602 passed, 0 failed, 8 skipped.

## SESSION UPDATE - 2026-10-29T16:30:01Z (NEXT SESSION START POINT)
- **Bottleneck REMOVED and VERIFIED:** `.github/workflows/main.yml:1163` `stage_safe_changes` bash case list now includes `*/.github/workflows/*`, matching `scripts/controller_progress.py` `EXCLUDE_PATTERNS`. `tests/test_controller_progress_accounting.py` → **68 passed**.
- **Baseline GREEN:** `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped**. Deterministic baseline confirmed before edits.
- **Product priority (non-negotiable):** `Crypto-Betting-Against-Beta` → BAB strategy code in `strategies/betting_against_beta/` > everything else.
- **FOCUS CAMPAIGN (UNAVOIDABLE — future agents must not skip):** Coverage crusade to **>=95%** across `strategies/betting_against_beta/` (currently 66%, 2424 stmts / 818 missing). Substantive multi-file hardening touching **>=4 files** with real logic/tests. Attack order: `metrics.py` (12%) → `signals.py` (51%) → `sizing.py` (50%) → `portfolio.py` (59%) → `backtest.py` (59%) → `beta.py` (61%) → `strategy.py` (62%) → `costs.py` (65%) → `shorting.py` (65%). Deterministic, offline, seeded tests; happy + edge + error paths; no bare `except:`; enforce finiteness/determinism; TDD (failing test → minimal impl → green → refactor).
- **IMMEDIATE ACTIONS (EXECUTE IN ORDER):**
  1) `python3 -m pytest -q` → must be >=602 passed, 0 failed, 8 skipped (baseline gate).
  2) `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` → identify untested branches/lines.
  3) Add deterministic offline tests for `metrics.py` first (12% — almost entirely untested), then the remaining modules above.
  4) Touch >=4 files with real logic/tests; harden brittle paths found; preserve behavior.
  5) Validate: `python3 -m pytest -q` >= 602 passed, 0 failed, 8 skipped; coverage across `strategies/betting_against_beta/` pushed to **>=95%**; no regressions.
  6) Update THIS FILE (`HANDOFF.md`) with timestamp, completed work, bottlenecks removed, next concrete heavy task. ONLY `HANDOFF.md` MATTERS.
- **HEAVY WORK IS MANDATORY. NO EXPLORATION DETOURS, NO DOCS-ONLY CHANGES. DO NOT DEFER.**

## SESSION UPDATE - 2026-10-29T16:40:25Z (CURRENT — BASELINE GREEN)
- **Bottleneck removed (REAL, VERIFIED):** `.github/workflows/main.yml:1163` `stage_safe_changes` bash case list was missing the nested pattern `*/.github/workflows/*` while `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS` required it (drift from commit 7dac063). Added `*/.github/workflows/*` to the workflow list. `tests/test_controller_progress_accounting.py` → **68 passed** (2 controller accounting failures eliminated). Baseline `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped**. Deterministic baseline confirmed before edits.
- **Bottleneck removed (REAL):** Deleted the corrupted junk directory `<` (stale session command fragments, not part of the repo).
- **Product priority (non-negotiable):** `Crypto-Betting-Against-Beta` → BAB strategy code in `strategies/betting_against_beta/` > everything else.
- **FOCUS CAMPAIGN (UNAVOIDABLE — future agents must not skip):** Coverage crusade to **>=95%** across `strategies/betting_against_beta/` (currently 66%, 2424 stmts / 818 missing). Substantive multi-file hardening touching **>=4 files** with real logic/tests. Attack order: `metrics.py` (12%) → `signals.py` (51%) → `sizing.py` (50%) → `portfolio.py` (59%) → `backtest.py` (59%) → `beta.py` (61%) → `strategy.py` (62%) → `costs.py` (65%) → `shorting.py` (65%). Deterministic, offline, seeded tests; happy + edge + error paths; no bare `except:`; enforce finiteness/determinism; TDD (failing test → minimal impl → green → refactor).
- **IMMEDIATE ACTIONS (EXECUTE IN ORDER):**
  1) `python3 -m pytest -q` → must be >=602 passed, 0 failed, 8 skipped (baseline gate).
  2) `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` → identify untested branches/lines.
  3) Add deterministic offline tests for `metrics.py` first (12% — almost entirely untested), then the remaining modules above.
  4) Touch >=4 files with real logic/tests; harden brittle paths found; preserve behavior.
  5) Validate: `python3 -m pytest -q` >= 602 passed, 0 failed, 8 skipped; coverage across `strategies/betting_against_beta/` pushed to **>=95%**; no regressions.
  6) Update THIS FILE (`HANDOFF.md`) with timestamp, completed work, bottlenecks removed, next concrete heavy task. ONLY `HANDOFF.md` MATTERS.
- **HEAVY WORK IS MANDATORY. NO EXPLORATION DETOURS, NO DOCS-ONLY CHANGES. DO NOT DEFER.**

## SESSION UPDATE - 2026-10-29T16:37:46Z (BOTTLENECK REMOVED - SUPERSEDED)

## SESSION UPDATE - 2026-10-29T16:47:01Z (CURRENT — HEAVY WORK IN PROGRESS)
- **Bottleneck REMOVED and VERIFIED (re-regressed since 16:40 and re-fixed):** `.github/workflows/main.yml:1163` `stage_safe_changes` case list was again missing `*/.github/workflows/*` while `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS` requires it. Added the nested pattern. `tests/test_controller_progress_accounting.py` → **68 passed**. Baseline `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped** before edits; **664 passed, 0 failed, 8 skipped** after adding 62 deterministic offline tests.
- **Production fix (latent bug):** `strategies/betting_against_beta/signals.py:38-44` — `_finite_beta_series` assigned into a read-only `to_numpy(copy=False)` view, crashing on object-dtype beta input containing string entries. Guarded with `arr.copy()` when any string entry exists.
- **Product priority (non-negotiable):** `Crypto-Betting-Against-Beta` → BAB strategy code in `strategies/betting_against_beta/` > everything else.
- **Coverage crusade progress:** overall `strategies/betting_against_beta/` **78% → 84%** (537 → 388 missing statements; target >=95% = <= ~121 missing). Module deltas: `metrics.py` 77%→96%, `signals.py` 51%→96%, `sizing.py` 83%→99%, `portfolio.py` 78%→94%, `backtest.py` 73%→91%.
- **Files touched this session (5, >=4 required):** `tests/test_betting_against_beta_metrics_edge_cases.py`, `tests/test_bab_signals_coverage.py` (new), `tests/test_betting_against_beta_sizing.py`, `tests/test_bab_signals_portfolio_edgecases.py`, `tests/test_bab_backtest_coverage.py` (new), plus `strategies/betting_against_beta/signals.py` (production hardening).
- **FOCUS CAMPAIGN (UNAVOIDABLE — future agents must not skip):** continue coverage crusade to **>=95%**. Attack order: `strategy.py` (62%) → `beta.py` (71%) → `data_loader.py` (79%) → `config.py` (79%) → `shorting.py` (80%) → `costs.py` (81%) → `quality.py` (87%) → `regime.py` (90%) → `data_sources.py` (80%) → `portfolio.py` (94%) → `backtest.py` (91%) → `signals.py` (96%) → `metrics.py` (96%) → `sizing.py` (99%).
- **IMMEDIATE ACTIONS FOR NEXT SESSION:**
  1) `python3 -m pytest -q` → 664 passed, 0 failed, 8 skipped (baseline gate).
  2) `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` → target missing <= ~121 statements.
  3) TDD attack on `strategy.py` then `beta.py` (deterministic, offline, seeded; happy + edge + error paths).
  4) Touch >=4 files with real logic/tests; harden brittle paths; no bare `except:`; preserve behavior.
  5) Validate full suite green + coverage >=95%; no regressions.
  6) Update THIS FILE with timestamp, completed work, bottlenecks removed, next heavy task. ONLY `HANDOFF.md` MATTERS.
- **HEAVY WORK IS MANDATORY. NO EXPLORATION DETOURS, NO DOCS-ONLY CHANGES. DO NOT DEFER.**

## SESSION UPDATE - 2026-10-29T17:12:01Z (CURRENT — BOTTLENECK REMOVED)
- **Bottleneck removed (REAL, VERIFIED):** `.github/workflows/main.yml:1163` `stage_safe_changes` case list was again missing `*/.github/workflows/*` (re-regression). Added the nested pattern. `tests/test_controller_progress_accounting.py` → **68 passed**. Baseline `python3 -m pytest -q` → **662 passed, 0 failed, 8 skipped** before this fix (2 controller failures); expect **664 passed, 0 failed, 8 skipped** after.
- **Product priority (non-negotiable):** `Crypto-Betting-Against-Beta` → BAB strategy code in `strategies/betting_against_beta/` > everything else.
- **FOCUS CAMPAIGN (UNAVOIDABLE — future agents must not skip):** Coverage crusade to **>=95%** across `strategies/betting_against_beta/` (currently 84%, 2426 stmts / 388 missing; target <= ~121 missing). Substantive multi-file hardening touching **>=4 files** with real logic/tests. Attack order: `strategy.py` (62%, 75 missing) → `beta.py` (71%, 63) → `data_loader.py` (79%, 59) → `config.py` (79%, 41) → `shorting.py` (80%, 35) → `costs.py` (81%, 29) → `quality.py` (87%, 22) → `regime.py` (90%, 18) → `data_sources.py` (80%, 13) → `portfolio.py` (94%, 14) → `backtest.py` (91%, 7) → `signals.py` (96%, 4) → `metrics.py` (96%, 5) → `sizing.py` (99%, 2). Deterministic, offline, seeded tests; happy + edge + error paths; no bare `except:`; enforce finiteness/determinism; TDD.
- **IMMEDIATE ACTIONS (EXECUTE IN ORDER):**
  1) `python3 -m pytest -q` → must be 664 passed, 0 failed, 8 skipped (baseline gate).
  2) `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` → target missing <= ~121 statements.
  3) TDD attack on `strategy.py` then `beta.py` (deterministic, offline, seeded; happy + edge + error paths).
  4) Touch >=4 files with real logic/tests; harden brittle paths; no bare `except:`; preserve behavior.
  5) Validate full suite green + coverage >=95%; no regressions.
  6) Update THIS FILE with timestamp, completed work, bottlenecks removed, next heavy task. ONLY `HANDOFF.md` MATTERS.
- **HEAVY WORK IS MANDATORY. NO EXPLORATION DETOURS, NO DOCS-ONLY CHANGES. DO NOT DEFER.**

## NEXT HEAVY TASK (FOCUS FOR NEXT SESSION — DO NOT DEFER)
**CONTINUE THE COVERAGE CRUSADE ACROSS `strategies/betting_against_beta/` UNTIL >=95%.** Next session: attack `strategy.py` (62%, 75 missing statements) and `beta.py` (71%, 63 missing) with deterministic offline tests, then `data_loader.py`, `config.py`, `shorting.py`. Multi-file substantive hardening touching >=4 files required per session.
