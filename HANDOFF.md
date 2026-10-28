# HANDOFF - 2026-10-28T11:17:16Z

## Timestamp
2026-10-28T11:17:16Z

## Purpose
**SINGLE DURABLE HANDOFF. START HERE.** Ignore all other `HANDOFF*.md` files unless you need historical context. `HANDOFF.md` (this file) is the source of truth for the next session. `HANDOFF_NEXT_SESSION.md` points to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the **Betting Against Beta (BAB)** crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. **BAB ALWAYS COMES FIRST. Infra only if it blocks BAB.**

## Bottlenecks Removed (THIS SESSION)
- **CI pattern-sync drift (was regressed, now fixed)** — `.github/workflows/main.yml` `stage_safe_changes()` was missing the nested pattern `*/.github/workflows/*` that Python `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS` requires. The prior handoff claimed this was fixed but it was never applied (suite was 293 passed, 2 failed). Added `*/.github/workflows/*` to the `stage_safe_changes` case list (line ~1163) and to the `checkpoint_has_project_changes` case list (line ~1241). Suite went from **293 passed, 2 failed** to **295 passed, 0 failed**. `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` now pass. **This bottleneck is removed; it no longer blocks progress.**

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)

**FOCUS CAMPAIGN: HARDEN BAB END-TO-END WITH STRESS TESTS & IMPLEMENTATION ROBUSTNESS (NO SHORTCUTS)**

Recon is complete: `python3 -m pytest -q` = **295 passed, 0 failed**; `git status` clean except `__pycache__/`; branch `main` @ HEAD; bottleneck (CI pattern-sync) removed. Your mission: stress-test the BAB implementation under adversarial conditions, harden edge cases, and make failures loud with `BABDataError`. Prove correctness with heavy TDD — if something breaks under stress, fix it minimally and add regression tests.

### Ground Truth (DO NOT RE-IMPLEMENT)
- Pipeline: `strategies/betting_against_beta/strategy.py`, `data_loader.py`, `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `metrics.py`, `config.py`, `errors.py`
- Guards/cost aliases already wired. All current tests green (295 passed, 0 failed).

### Heavy Campaign (Execute in order, TDD strictly)

#### PHASE 1: BETA CALCULATION STRESS (IMMEDIATE - HEAVY)
Create/extend tests for rolling beta robustness:
- [ ] Constant prices / zero variance -> should not produce NaN/inf or division by zero crashes
- [ ] Single asset / insufficient history -> handle gracefully per existing logic, no silent corruption
- [ ] Large gaps/missing data -> finite outputs where possible, clear `BABDataError` if invalid per contract
- [ ] Outliers/extreme moves -> numerical stability (no inf/nan)
- [ ] Window/min_obs edge cases covered with property-style assertions

#### PHASE 2: SIGNAL GENERATION ROBUSTNESS (HEAVY)
Harden `signals.py`:
- [ ] All-equal betas / ties in ranking -> deterministic, no crashes
- [ ] All assets on one side of median -> correct long/short split or explicit handling
- [ ] NaN betas propagate safely without corrupting full universe
- [ ] Negative/zero betas handled correctly
- [ ] Quantile construction matches BAB logic (low beta long, high beta short)

#### PHASE 3: PORTFOLIO CONSTRUCTION ADVERSARIAL (HEAVY)
Adversarial tests for `construct_portfolio`:
- [ ] All-zero signals -> all-zero weights, finite
- [ ] Mixed valid/invalid signals -> sanitized correctly
- [ ] Extremely unbalanced long/short counts
- [ ] Rebalancing with large turnover + guards interact correctly
- [ ] Max position size enforcement with actual violations
- [ ] Dollar-neutrality preserved under constraints

#### PHASE 4: BACKTEST NUMERICAL INTEGRITY (HEAVY)
Stress `run_backtest`:
- [ ] Large date ranges (1000+ periods) remain finite and performant enough
- [ ] Weights with extreme values (but finite) handled correctly
- [ ] Transaction costs applied correctly on first trade (shifted weights)
- [ ] No lookahead violations - verify with shifted weight scenarios
- [ ] Returns alignment correct across all index types

#### PHASE 5: END-TO-END INTEGRATION STRESS (HEAVY)
Full pipeline under stress:
- [ ] Corrupted fixtures handled with clear errors
- [ ] Multiple runs produce deterministic results
- [ ] Strategy handles missing columns/extra columns gracefully
- [ ] Benchmark missing -> appropriate `BABDataError`
- [ ] Results reproducible across calls

### Execution Rules (NON-NEGOTIABLE)
1. **START HERE** - Recon first: `python3 -m pytest -q` (expect 295 passed), `git status`, `git diff --stat`, `git log --oneline -5`. Read all core BAB files.
2. **TDD MANDATORY** - Write failing test → understand → minimal fix if broken → green.
3. **BAB FIRST** - Product focus over infra.
4. **NO COMMIT** unless explicitly asked.
5. **HEAVY WORK REQUIRED** - Do not stop at trivial fixes. Stress everything.
6. **VERIFY CONSTANTLY** - Run tests after each phase.
7. **FAIL LOUDLY** - Use `BABDataError` for data/constraint violations. No silent failures.

**GOAL**: Make BAB bulletproof under adversarial conditions. Every edge case must be tested and handled correctly.

## Current State
- Branch: main @ HEAD
- Tests: **295 passed, 0 failed**
- CI: Pattern sync fixed (suite green)
- Uncommitted: `.github/workflows/main.yml` (nested workflow pattern added), `__pycache__/` dirs only

## Remaining Bottlenecks (TO REMOVE)
- **Adversarial robustness gaps** - Need stress testing and hardening (PHASES 1-5 above)

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable
- No commit unless explicitly asked
- No NaN/inf in outputs on valid inputs; clear errors on invalid
- Minimal diffs, follow existing style

## NEXT ACTION
**IMMEDIATELY**: Run recon, read core files, start Phase 1 with adversarial beta tests.
