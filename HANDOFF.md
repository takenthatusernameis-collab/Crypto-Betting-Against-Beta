# HANDOFF - 2026-10-28T15:03:32Z

## Timestamp
2026-10-28T15:03:32Z

## Purpose
**SINGLE DURABLE HANDOFF. START HERE.** Ignore all other `HANDOFF*.md` files unless you need historical context. This file is the sole source of truth for the next agentic work session.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the **Betting Against Beta (BAB)** crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest.
**BAB ALWAYS COMES FIRST. Touch infra ONLY if it directly blocks BAB execution or tests.**

## Current State (Ground Truth)
- Branch: `main` @ `7c855cc` (HEAD; origin/main in sync)
- Tests: **324 passed, 0 failed** (`python3 -m pytest -q`)
- Working tree: clean (only untracked `__pycache__/` dirs)
- Bottlenecks: **NONE CRITICAL**

## Bottlenecks Removed (HISTORICAL)
- **CI pattern-sync drift** — `.github/workflows/main.yml` `stage_safe_changes()` now matches `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS` (added `*/.github/workflows/*`).
- **Delisted/all-NaN columns** — `_drop_all_nan_columns()` added to `data_loader.py`.
- **Silent broad excepts** — removed from `signals.py` and `portfolio.py` with explicit finiteness guards.
- **Beta NaN propagation** — `calculate_rolling_beta` fails loudly on all-NaN benchmark via `BABDataError`.
- **Report sanitization** — `scripts/bab_backtest_report.py` coerces NaN/inf to 0.0.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)

**FOCUS CAMPAIGN: BAB HARDENING, ROBUSTNESS & PERFORMANCE (FORCE HEAVY CONTINUOUS PROGRESS)**

Strategy is green at 324 passed. Make it bulletproof for real, messy crypto data and faster at scale. Do not coast. Every phase must produce tests and measurable hardening.

### MANDATORY RECON (DO FIRST)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q
git status
git diff --stat
git log --oneline -5
```

Read: `strategies/betting_against_beta/strategy.py`, `data_loader.py`, `data.py`, `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `metrics.py`, `config.py`, `errors.py`, `scripts/bab_backtest_report.py`

### HEAVY CAMPAIGN

#### PHASE 1: PERFORMANCE & SCALABILITY
- [ ] Profile `calculate_rolling_beta` on synthetic 150x2500 universe with cProfile/timeit (before/after).
- [ ] Optimize hotspots (groupby/apply/rolling/copies/dtypes). Preserve NaN semantics and numerical results within tolerance.
- [ ] Add guards for degenerate windows/conditioning.
- [ ] Add regression tests (shape/dtype/index/values). No suite slowdown without justification.

#### PHASE 2: DATA LOADING & MESSY DATA
- [ ] Harden coercion for mixed dtypes/strings (N/A, commas). Fail loudly with `BABDataError` if unparseable; no silent zeroing.
- [ ] Expand `_drop_all_nan_columns` coverage (partial/all-NaN, benchmark-all-NaN).
- [ ] Handle leading/trailing NaNs, sparse histories, duplicates (dates/cols). Test behavior.
- [ ] Actionable `BABDataError` messages (names/counts/shapes).
- [ ] Stress fixtures (duplicates, mixed tz/index, non-numeric, inf). Extend loader/messy tests; use `tests/fixtures/real_data_defects.csv`.

#### PHASE 3: BETA, SIGNALS, PORTFOLIO
- [ ] Beta edges: all-NaN benchmark, constant benchmark, single asset, constant series, insufficient obs. Raise only when contract violated.
- [ ] Signals: all-zero betas, ties, overlaps, single-asset/empty. Deterministic tie-breaking/policy; shrink short set on overlap.
- [ ] Portfolio: finite weights, strict dollar-neutrality (|sum| < 1e-12), no NaN/inf; add finiteness audit.
- [ ] Eliminate remaining broad excepts; add tests for all classes.

#### PHASE 4: BACKTEST, METRICS & REPORTING
- [ ] Degenerate: zero variance, all same, single period, no tradable periods.
- [ ] Metrics finite; zero-vol must not produce NaN/inf.
- [ ] JSON sanitizer must hold for all cases (extend tests).
- [ ] Costs/slippage/no-lookahead/lagged weights correct.
- [ ] Long-only edge cases covered.

#### PHASE 5: INTEGRATION & REAL-WORLD STRESS
- [ ] Fat tails/skew/regime changes/high vol/gaps/correlated shocks.
- [ ] Full pipeline end-to-end assertions.
- [ ] Strict dollar-neutrality across all scenarios.
- [ ] Finiteness audits at every stage.
- [ ] Add tests for every bug found; keep all green.

### RULES (NON-NEGOTIABLE)
1. Start with recon. 2. TDD mandatory. 3. BAB first. 4. No commit unless explicitly asked. 5. Heavy work required. 6. Verify with `python3 -m pytest -q` after each phase/change. 7. Fail loudly with `BABDataError`. No silent NaN/inf. 8. Minimal diffs. 9. Exhaustive testing.

### ACCEPTANCE CRITERIA
- [ ] >=1 concrete perf improvement in `beta.py` with timings OR major stress coverage added
- [ ] All new edge cases tested and passing
- [ ] No NaN/inf in weights/signals/metrics
- [ ] Consistent `BABDataError` with actionable messages
- [ ] `python3 -m pytest -q` >= 324 passed, 0 failed
- [ ] |sum(weights)| < 1e-12 in all new tests
- [ ] Handoff clean and actionable

## NEXT ACTION
**IMMEDIATELY**: Run recon, read core BAB files, start Phase 1 (profile `calculate_rolling_beta`). Find and fix at least one concrete issue OR add heavy stress coverage before Phase 2. Do not stop.

(End of file)
