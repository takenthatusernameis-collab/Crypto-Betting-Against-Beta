# HANDOFF - 2026-10-28T12:19:47Z

## Timestamp
2026-10-28T12:19:47Z

## Purpose
**SINGLE DURABLE HANDOFF. START HERE.** Ignore all other `HANDOFF*.md` files unless you need historical context. This file is the source of truth for the next agentic work session.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the **Betting Against Beta (BAB)** crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest.
**BAB ALWAYS COMES FIRST. Infra only if it blocks BAB.**

## Current State (Ground Truth)
- Branch: `main` @ `9eba5e2`
- Tests: **295 passed, 0 failed** (`python3 -m pytest -q`)
- Working tree: clean except `__pycache__/` directories
- Bottlenecks: **NONE CRITICAL** — CI pattern-sync drift already fixed this session

## Bottlenecks Removed (THIS SESSION)
- **CI pattern-sync drift (FIXED)** — `.github/workflows/main.yml` `stage_safe_changes()` and `checkpoint_has_project_changes()` now include `*/.github/workflows/*` to match `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS`. Tests `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` pass. Suite: 293→295 passed, 0 failures.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)

**FOCUS CAMPAIGN: BAB HARDENING, ROBUSTNESS & PERFORMANCE (FORCE HEAVY CONTINUOUS PROGRESS)**

The strategy is green. The goal is to make it bulletproof for messy real crypto data, faster at scale, and impossible to silently fail. Do not coast — stress test everything.

### Recon (MANDATORY FIRST STEP)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q
git status
git diff --stat
git log --oneline -5
```

Read core BAB files to internalize behavior:
- `strategies/betting_against_beta/strategy.py`
- `strategies/betting_against_beta/data_loader.py`
- `strategies/betting_against_beta/beta.py`
- `strategies/betting_against_beta/signals.py`
- `strategies/betting_against_beta/portfolio.py`
- `strategies/betting_against_beta/backtest.py`
- `strategies/betting_against_beta/metrics.py`
- `strategies/betting_against_beta/config.py`
- `strategies/betting_against_beta/errors.py`

### Heavy Campaign (Execute in strict order, TDD mandatory)

#### PHASE 1: PERFORMANCE & SCALABILITY (IMMEDIATE - HEAVY)
- [ ] **Profile** rolling beta on large universes (100+ assets, 2000+ days). Identify hotspots.
- [ ] **Optimize** without changing behavior (vectorize where safe, avoid unnecessary copies).
- [ ] **Numerical stability** — check for overflow/underflow, conditioning issues.
- [ ] **Regression tests** — add performance-oriented tests that catch regressions.

#### PHASE 2: DATA LOADING & MESSY DATA (HEAVY)
- [ ] **Robust coercion** — mixed dtypes, strings, NaN/inf, object columns
- [ ] **All-NaN/delisted** — ensure `_drop_all_nan_columns` behaves correctly in all paths
- [ ] **Missing data patterns** — forward/backward fills, partial histories, leading/trailing NaNs
- [ ] **Clear errors** — every invalid case must raise `BABDataError` with actionable message
- [ ] **Stress tests** — use/create fixtures for messy CSV/JSON

#### PHASE 3: BETA, SIGNALS, PORTFOLIO ROBUSTNESS (HEAVY)
- [ ] **Beta edge cases** — all-NaN benchmark, constant benchmark, single asset, constant series
- [ ] **Signals** — all-zero betas, quantile ties, overlapping quantiles, single asset rows
- [ ] **Portfolio** — guarantee finite weights, dollar-neutrality holds strictly
- [ ] **No silent failures** — eliminate broad excepts, add finiteness guards everywhere
- [ ] **Tests** — cover every edge case discovered

#### PHASE 4: BACKTEST, METRICS & REPORTING (HEAVY)
- [ ] **Degenerate cases** — zero variance, all same returns, single period
- [ ] **Metrics** — Sharpe, drawdown, turnover must be finite and correct
- [ ] **Sanitization** — JSON reports must never emit NaN/inf
- [ ] **Long-only mode** — all edge cases
- [ ] **Transaction costs/slippage** — interactions must be correct

#### PHASE 5: INTEGRATION & REAL-WORLD STRESS (HEAVY)
- [ ] **Realistic distributions** — fat tails, skew, regime changes, high vol
- [ ] **Full pipeline** — data_loader → beta → signals → portfolio → backtest → metrics
- [ ] **Dollar-neutrality** — verify strictly across all scenarios
- [ ] **No NaN/inf propagation** — assert finiteness at every stage
- [ ] **Regression suite** — add tests for any bugs found

### Execution Rules (NON-NEGOTIABLE)
1. **START HERE** - Recon first. Do not skip.
2. **TDD MANDATORY** - Write failing test → understand root cause → minimal fix → green. Never "fix" without a test.
3. **BAB FIRST** - Product over infra. Only touch infra if it blocks BAB.
4. **NO COMMIT** unless explicitly asked by user.
5. **HEAVY WORK REQUIRED** - Trivial fixes are not enough. Stress, profile, harden.
6. **VERIFY CONSTANTLY** - Run `python3 -m pytest -q` after each meaningful change/phase.
7. **FAIL LOUDLY** - Use `BABDataError` for data/constraint violations. No silent failures or NaN propagation.
8. **MINIMAL DIFFS** - Follow existing style, don't refactor unrelated code.

### Acceptance Criteria
- [ ] All new edge cases have tests and pass
- [ ] No NaN/inf in weights/signals/metrics on any tested input
- [ ] `BABDataError` used consistently for invalid data
- [ ] `python3 -m pytest -q` = **295 passed, 0 failed** (or higher with new tests)
- [ ] Performance improved where measured without behavior change
- [ ] Handoff remains clean and actionable

## NEXT ACTION
**IMMEDIATELY**: Run recon, read all core BAB files, start **Phase 1** (performance profiling). Do not stop until you've found and addressed at least one concrete performance issue or added meaningful coverage. Keep going heavy.
