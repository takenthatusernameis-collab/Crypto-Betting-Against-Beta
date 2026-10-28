# HANDOFF - 2026-10-28T11:33:16Z

## Timestamp
2026-10-28T11:33:16Z

## Purpose
**SINGLE DURABLE HANDOFF. START HERE.** Ignore all other `HANDOFF*.md` files unless you need historical context. `HANDOFF.md` (this file) is the source of truth for the next session. `HANDOFF_NEXT_SESSION.md` points to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the **Betting Against Beta (BAB)** crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. **BAB ALWAYS COMES FIRST. Infra only if it blocks BAB.**

## Bottlenecks Removed (THIS SESSION)
- **CI pattern-sync drift (NOW ACTUALLY FIXED — was falsely claimed fixed before)** — `.github/workflows/main.yml` `stage_safe_changes()` (line ~1163) and `checkpoint_has_project_changes` (line ~1240) were both missing the nested pattern `*/.github/workflows/*` that Python `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS` requires. Prior handoff claimed this was fixed but it was never applied (suite was 293 passed, 2 failed). Added `*/.github/workflows/*` to both case lists. Suite went from **293 passed, 2 failed** to **295 passed, 0 failed**. `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` now pass. **This bottleneck is removed; it no longer blocks progress.**

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)

**FOCUS CAMPAIGN: BAB MAINTENANCE & PERFORMANCE OPTIMIZATION (ENSURE CONTINUOUS HEAVY PROGRESS)**

Recon is complete: `python3 -m pytest -q` = **295 passed, 0 failed**; `git status` clean except `__pycache__/`; branch `main` @ HEAD. Bottleneck (CI pattern-sync) removed. Mission: continue hardening and optimizing BAB while maintaining 100% test pass rate. Never let tests become stale — add regression tests for any new edge cases discovered.

### Ground Truth (DO NOT RE-IMPLEMENT)
- Pipeline: `strategies/betting_against_beta/strategy.py`, `data_loader.py`, `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `metrics.py`, `config.py`, `errors.py`
- Guards/cost aliases already wired. All current tests green (295 passed, 0 failed).

### Heavy Campaign (Execute in order, TDD strictly)

#### PHASE 1: PERFORMANCE & SCALABILITY (IMMEDIATE)
- [ ] Profile rolling beta calculation on larger universes (100+ assets, 2000+ days)
- [ ] Optimize where possible without changing behavior
- [ ] Ensure numerical stability at scale
- [ ] Add performance regression tests

#### PHASE 2: ADDITIONAL EDGE CASES (HEAVY)
- [ ] Test with datetime vs integer indices
- [ ] Test with different rebalance frequencies
- [ ] Test with transaction costs on every period
- [ ] Test slippage interactions
- [ ] Verify weights sum correctly in all scenarios

#### PHASE 3: DATA QUALITY & LOADING (HEAVY)
- [ ] Stress test data_loader with various formats
- [ ] Test CSV/JSON loading paths
- [ ] Test with missing data patterns
- [ ] Ensure clear errors for all invalid cases

#### PHASE 4: METRICS & REPORTING (HEAVY)
- [ ] Verify all metrics computed correctly
- [ ] Test Sharpe, drawdown, turnover calculations
- [ ] Ensure no NaN in metrics on valid inputs

#### PHASE 5: INTEGRATION & REAL-WORLD SCENARIOS (HEAVY)
- [ ] Test with realistic crypto-like return distributions
- [ ] Test regime changes (high vol periods)
- [ ] Verify dollar-neutrality holds strictly
- [ ] Long-only mode edge cases

### Execution Rules (NON-NEGOTIABLE)
1. **START HERE** - Recon first: `python3 -m pytest -q` (expect 295 passed), `git status`, `git diff --stat`, `git log --oneline -5`. Read all core BAB files.
2. **TDD MANDATORY** - Write failing test → understand → minimal fix if broken → green.
3. **BAB FIRST** - Product focus over infra.
4. **NO COMMIT** unless explicitly asked.
5. **HEAVY WORK REQUIRED** - Do not stop at trivial fixes. Stress everything.
6. **VERIFY CONSTANTLY** - Run tests after each phase.
7. **FAIL LOUDLY** - Use `BABDataError` for data/constraint violations. No silent failures.

**GOAL**: Keep BAB bulletproof and performant. Every edge case must be tested and handled correctly.

## Current State
- Branch: main @ HEAD
- Tests: **295 passed, 0 failed** (CI pattern-sync bottleneck removed)
- Uncommitted: `.github/workflows/main.yml` (nested workflow pattern added to both case lists), `__pycache__/` dirs only

## Remaining Bottlenecks (TO REMOVE)
- None critical - continue with performance optimization and additional edge case coverage

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable
- No commit unless explicitly asked
- No NaN/inf in outputs on valid inputs; clear errors on invalid
- Minimal diffs, follow existing style

## NEXT ACTION
**IMMEDIATELY**: Run recon, read core files, start Phase 1 with performance profiling and optimization.