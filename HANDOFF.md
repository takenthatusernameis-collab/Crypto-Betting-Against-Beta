# HANDOFF - 2026-10-28T18:15:50Z (updated 2026-10-28T18:15:50Z)

## Timestamp
2026-10-28T18:15:50Z

## Purpose
Single durable handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: **BAB comes first, infra second**.

## Current State
- Branch main @ HEAD @ 93bab9f. Working tree: clean after the uncommitted change below. Tests: **348 passed, 0 failed** (verified 2026-10-28T18:10:52Z).
- **BOTTLENECK REMOVED (this session)**: `.github/workflows/main.yml` `stage_safe_changes` case list was missing `*/.github/workflows/*`. The prior handoff claimed this fix was applied and the suite was green; that was false — `git diff` was empty and 2 tests were failing (`test_python_patterns_are_subset_of_workflow`, `test_nested_workflow_pattern_is_present_in_workflow`). Added the pattern immediately after `.github/workflows/*` at line 1163. Suite is now genuinely green (348, 0).
- **PRIOR CAMPAIGN COMPLETE**: All 5 phases of "BAB Strategy Robustness & Production Readiness" executed with tests. Prior bottlenecks removed: pattern sync drift, JSON NaN emission, config range validation. Remaining work is hygiene: narrowing silent broad `except Exception:` so future bugs surface loudly instead of being coerced to zero.

## Changes Made This Session (uncommitted, infra-first because it blocked the BAB campaign's green suite)
1. **`.github/workflows/main.yml`** — Prepended `*/.github/workflows/*|` to the bash `stage_safe_changes` case list at line 1163, matching Python `EXCLUDE_PATTERNS`. Fixes 2 failing pattern-sync tests; suite now 348 passed, 0 failed.

---

## *** INITIAL TASK FOR NEXT SESSION — START HERE IMMEDIATELY ***

**PRODUCT FIRST. NO EXCUSES. HEAVY WORK REQUIRED.**

You are working on **Crypto-Betting-Against-Beta**. The core product is the BAB (Betting Against Beta) crypto strategy. Every action must prioritize BAB strategy code in `strategies/betting_against_beta/`. Infra only when blocking BAB.

### MANDATORY FIRST ACTION (do this before anything else)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status
git diff --stat
python3 -m pytest -q   # MUST be 348 passed, 0 failed
```
If tests are not green, fix the blocker first. Do not proceed otherwise.

### FOCUS CAMPAIGN: BAB Silent-Error Eradication (CRITICAL - DO NOT DEFER)

**Rule:** TDD for every item. Write a failing test proving error is silently swallowed → make it surface loudly (specific exception or log+re-raise) → implement → verify green. Do not batch. Do not skip. Campaign is INCOMPLETE until all items done.

#### 1) `strategies/betting_against_beta/beta.py` - Eliminate silent broad `except Exception:`
- Line ~34 (Series alignment fallback in `calculate_beta`) → catch specific types, re-raise unexpected
- Line ~65 (`np.linalg.lstsq` in `calculate_beta`) → catch `np.linalg.LinAlgError` only; re-raise others
- Line ~67 (outer `calculate_beta`) → narrow or remove; unexpected errors MUST propagate
- Line ~99 (`calculate_beta_fast` lstsq) → catch `np.linalg.LinAlgError` only
- Line ~100 (`calculate_beta_fast` outer) → narrow
- Line ~166 (rolling window `calculate_beta_fast` call) → narrow
- Line ~245 (fallback path window call) → narrow
**Contract:** Degenerate/insufficient data returns documented finite sentinels (0.0/nan) ONLY for expected cases. Bugs must NOT be masked.

#### 2) `strategies/betting_against_beta/portfolio.py` - Eliminate silent broad `except Exception:`
- Lines ~75, 118, 144, 148, 156 in `construct_portfolio` → `BABPortfolioError`/`BABDataError` MUST propagate. Unexpected errors logged and re-raised, NOT swallowed with `pass`.

#### 3) `strategies/betting_against_beta/strategy.py` - Eliminate silent broad `except Exception:`
- Line ~189 (weights finiteness guard) → narrow `except Exception:`

#### 4) `strategies/betting_against_beta/backtest.py` - Eliminate silent broad `except Exception:`
- Lines ~22, 26 (DataFrame coercion), ~50 (weights clean) → narrow `except Exception:`

#### 5) `strategies/betting_against_beta/data_loader.py` - Eliminate silent broad `except Exception:`
- Line ~27 (`_normalize_index` catches `(ValueError, TypeError, Exception)` — DROP `Exception`)
- Line ~201 (`validate_returns_dataframe` catches broad `Exception` re-raising as `BABDataError`) → narrow to `(ValueError, TypeError, pd.errors.ParserError)`, let unexpected errors propagate

#### 6) `tests/test_bab_messy_data.py` - Add tz-aware fixture
Add tz-aware fixture exercising `_normalize_index` timezone conversion. Cover tz-aware inputs/gaps.

#### 7) `strategies/betting_against_beta/config.py` - Config immutability
`BABConfig` mutates `self.universe` in `__post_init__`; freeze after validation to prevent downstream mutation (strategy.py:151 mutates `cfg.universe` after validation). Implement or explicitly defer with detailed rationale in handoff.

### ACCEPTANCE CRITERIA (MUST ALL BE MET)
- [ ] Every broad `except Exception:` in beta.py/portfolio.py/strategy.py/backtest.py/data_loader.py narrowed to specific types or log+re-raise
- [ ] New regression tests prove each previously-silent path now surfaces errors loudly
- [ ] tz-aware fixture added and passing
- [ ] `BABConfig` post-validation immutability enforced (or explicitly deferred with rationale)
- [ ] `python3 -m pytest -q` all pass (348, 0 failures) - no regressions
- [ ] Update this handoff (`HANDOFF.md`, symlink `HANDOFF_NEXT_SESSION.md`) with new timestamp at end

### CONSTRAINTS
- **Product-first:** BAB strategy above all else; infra only when it blocks BAB
- **TDD:** Failing test first → implementation → green
- **Robust to crypto data:** Handle NaNs, constants, mixed dtypes, gaps; explicit errors over silent fallbacks
- **Deterministic:** No randomness without seed
- **Offline/testable:** No network calls
- **Handoff discipline:** Leave single durable handoff updated with timestamp
- **No commits unless explicitly asked:** Changes uncommitted for review
