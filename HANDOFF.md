# HANDOFF - 2026-10-28T13:22:30Z

## Timestamp
2026-10-28T13:22:30Z

## Purpose
**SINGLE DURABLE HANDOFF. START HERE.** Ignore all other `HANDOFF*.md` files unless you need historical context. This file is the source of truth for the next agentic work session.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the **Betting Against Beta (BAB)** crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest.
**BAB ALWAYS COMES FIRST. Infra only if it blocks BAB.**

## Current State (Ground Truth)
- Branch: `main` @ `7a29016` (latest checkpoint)
- Tests: **295 passed, 0 failed** (`python3 -m pytest -q`)
- Working tree: clean (CI pattern-sync drift fixed in this session)
- Bottlenecks: **NONE CRITICAL**

## Bottlenecks Removed (THIS SESSION)
- **CI pattern-sync drift (FIXED)** — `.github/workflows/main.yml` `stage_safe_changes()` now includes `*/.github/workflows/*` matching `scripts/controller_progress.py:28`. Controller progress tests green; full suite restored to 295 passed.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)

**FOCUS CAMPAIGN: BAB HARDENING, ROBUSTNESS & PERFORMANCE (FORCE HEAVY CONTINUOUS PROGRESS)**

Strategy is green (295 passed). Make it bulletproof for messy real crypto data, faster at scale, and impossible to silently fail. Do not coast — stress test everything. Heavy work required.

### Recon (MANDATORY FIRST STEP)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q
git status
git diff --stat
git log --oneline -5
```

Read core BAB files:
- `strategies/betting_against_beta/strategy.py`
- `strategies/betting_against_beta/data_loader.py`
- `strategies/betting_against_beta/data.py`
- `strategies/betting_against_beta/beta.py`
- `strategies/betting_against_beta/signals.py`
- `strategies/betting_against_beta/portfolio.py`
- `strategies/betting_against_beta/backtest.py`
- `strategies/betting_against_beta/metrics.py`
- `strategies/betting_against_beta/config.py`
- `strategies/betting_against_beta/errors.py`

### Heavy Campaign (Execute in strict order, TDD mandatory)

#### PHASE 1: PERFORMANCE & SCALABILITY (IMMEDIATE - HEAVY)
- [ ] **Profile** rolling beta on large universes (100+ assets, 2000+ days). Identify hotspots in `beta.py` (loops/copies/groupby/apply). Capture timings before/after.
- [ ] **Optimize** without changing behavior (vectorize where safe, avoid unnecessary copies, reduce allocations). Preserve dtype/NaN semantics.
- [ ] **Numerical stability** — check conditioning (collinearity, near-constant series), overflow/underflow. Add guards where needed.
- [ ] **Regression tests** — add performance-oriented tests that catch regressions (shape/dtype/values unchanged). Must not slow suite meaningfully without justification.

#### PHASE 2: DATA LOADING & MESSY DATA (HEAVY)
- [ ] **Robust coercion** — mixed dtypes, strings, NaN/inf, object columns. Coerce to numeric safely.
- [ ] **All-NaN/delisted** — ensure `_drop_all_nan_columns` behaves correctly in all paths. Cover partial/all-NaN cases.
- [ ] **Missing data patterns** — forward/backward fills, partial histories, leading/trailing NaNs. Define correct behavior or fail loudly.
- [ ] **Clear errors** — every invalid case must raise `BABDataError` with actionable message. No silent coercion to zero.
- [ ] **Stress tests** — create fixtures for messy CSV/JSON (duplicates, mixed tz/index, non-numeric, inf). Extend `tests/test_betting_against_beta_data_loader.py` and `tests/test_bab_messy_data.py`.

#### PHASE 3: BETA, SIGNALS, PORTFOLIO ROBUSTNESS (HEAVY)
- [ ] **Beta edge cases** — all-NaN benchmark, constant benchmark, single asset, constant series, insufficient observations. Return finite/defined values or raise `BABDataError` as appropriate.
- [ ] **Signals** — all-zero betas, quantile ties, overlapping quantiles, single asset rows, empty universe. Deterministic tie-breaking or explicit policy + tests.
- [ ] **Portfolio** — guarantee finite weights, dollar-neutrality holds strictly (sum to 0 within float tolerance), no NaN/inf propagation.
- [ ] **No silent failures** — eliminate broad excepts, add finiteness guards everywhere. Fail loudly with `BABDataError` where contract violated.
- [ ] **Tests** — cover every edge case discovered. No "pass by zeroing everything".

#### PHASE 4: BACKTEST, METRICS & REPORTING (HEAVY)
- [ ] **Degenerate cases** — zero variance, all same returns, single period, no tradable periods.
- [ ] **Metrics** — Sharpe, drawdown, turnover must be finite and correct. Define behavior for zero-vol; never return NaN/inf.
- [ ] **Sanitization** — JSON reports must never emit NaN/inf (check `scripts/bab_backtest_report.py` and serialization paths).
- [ ] **Long-only mode** — all edge cases covered.
- [ ] **Transaction costs/slippage** — interactions must be correct, no lookahead, weights lagged correctly.

#### PHASE 5: INTEGRATION & REAL-WORLD STRESS (HEAVY)
- [ ] **Realistic distributions** — fat tails, skew, regime changes, high vol, gaps, correlated shocks.
- [ ] **Full pipeline** — data_loader → beta → signals → portfolio → backtest → metrics. End-to-end stress.
- [ ] **Dollar-neutrality** — verify strictly across all scenarios (assert |sum weights| < eps).
- [ ] **No NaN/inf propagation** — assert finiteness at every stage (add assertions/tests).
- [ ] **Regression suite** — add tests for any bugs found. Keep all existing tests green.

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
- [ ] `python3 -m pytest -q` = **>= 295 passed, 0 failed** (grow coverage, never regress)
- [ ] Performance improved where measured without behavior change (document findings)
- [ ] Handoff remains clean and actionable

## NEXT ACTION
**IMMEDIATELY**: Run recon, read all core BAB files, start **Phase 1** (performance profiling of `calculate_rolling_beta`). Find and address at least one concrete performance issue OR add meaningful stress coverage before moving to next phase. Do not stop. Keep going heavy.
