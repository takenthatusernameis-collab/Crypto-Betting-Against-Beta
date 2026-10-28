# HANDOFF - 2026-10-28T18:17:00Z (updated 2026-10-28T18:17:00Z)

## Timestamp
2026-10-28T18:17:00Z

## Purpose
**SINGLE DURABLE HANDOFF.** Start here. Ignore all older HANDOFF_*.md files unless you need historical context for a specific bug.

## Project Name Priority (NON-NEGOTIABLE)
**Repository:** `Crypto-Betting-Against-Beta`
**Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default).
**Hierarchy:** **BAB STRATEGY CODE > EVERYTHING ELSE.** Infrastructure/agent scaffolding exists only to support building the BAB strategy. If infra blocks BAB, fix it first. Otherwise ignore it.

## Current State (Verified)
- **Branch:** main @ `93bab9f`
- **Working tree:** clean (uncommitted workflow fix from prior session)
- **Tests:** **348 passed, 0 failed** (verified 2026-10-28T18:10:52Z)
- **Bottleneck removed (this session):** `.github/workflows/main.yml` `stage_safe_changes` was missing `*/.github/workflows/*` — caused 2 pattern-sync test failures. Added pattern at line ~1163. Suite genuinely green.
- **Prior campaign:** "BAB Strategy Robustness & Production Readiness" complete (5 phases). Remaining: eliminate silent broad `except Exception:` blocks so bugs surface loudly.

## Changes Made This Session (uncommitted)
1. `.github/workflows/main.yml` — Added `*/.github/workflows/*|` to `stage_safe_changes` case list (matches Python `EXCLUDE_PATTERNS`). Restored green suite.

---

## *** MANDATORY INITIAL TASK FOR NEXT AGENTIC SESSION — DO NOT SKIP ***

**FOCUS: HEAVY WORK. NO EXCUSES. BAB FIRST.**

You are continuing work on **Crypto-Betting-Against-Beta**. Your entire session must drive the BAB strategy forward. Infra changes only if they block the BAB campaign.

### STEP 0: VERIFY GREEN STATE (REQUIRED BEFORE ANY EDIT)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status
git diff --stat
python3 -m pytest -q  # MUST show 348 passed, 0 failed
```
If not green → fix blocker first. Do not proceed.

### FOCUS CAMPAIGN: BAB SILENT-ERROR ERADICATION (INCOMPLETE - HEAVY WORK AHEAD)

**Methodology (TDD, NO SHORTCUTS):** For each item below, write a failing test that proves the error is silently swallowed → make it surface loudly (narrow exception types, log+re-raise, or raise specific BAB exception) → implement → verify green. Do **not** batch. Do **not** skip. Campaign remains incomplete until **ALL** items are done.

#### 1) `strategies/betting_against_beta/beta.py` — Eliminate silent broad `except Exception:`
- ~line 34: Series alignment fallback in `calculate_beta` → catch specific types, re-raise unexpected
- ~line 65: `np.linalg.lstsq` in `calculate_beta` → catch `np.linalg.LinAlgError` only; re-raise others
- ~line 67: outer `calculate_beta` → narrow/remove; unexpected errors MUST propagate
- ~line 99: `calculate_beta_fast` lstsq → catch `np.linalg.LinAlgError` only
- ~line 100: `calculate_beta_fast` outer → narrow
- ~line 166: rolling window `calculate_beta_fast` call → narrow
- ~line 245: fallback path window call → narrow
**Contract:** Degenerate/insufficient data may return documented finite sentinels (e.g. 0.0/NaN) **only** for expected, documented cases. Bugs must NOT be masked.

#### 2) `strategies/betting_against_beta/portfolio.py` — Eliminate silent broad `except Exception:`
- ~lines 75, 118, 144, 148, 156 in `construct_portfolio`
**Rule:** `BABPortfolioError`/`BABDataError` MUST propagate. Unexpected errors must be logged and re-raised, **never** swallowed with `pass`.

#### 3) `strategies/betting_against_beta/strategy.py` — Eliminate silent broad `except Exception:`
- ~line 189 (weights finiteness guard) → narrow to specific exceptions or log+re-raise

#### 4) `strategies/betting_against_beta/backtest.py` — Eliminate silent broad `except Exception:`
- ~lines 22, 26 (DataFrame coercion), ~line 50 (weights cleaning) → narrow to specific exceptions or log+re-raise

#### 5) `strategies/betting_against_beta/data_loader.py` — Eliminate silent broad `except Exception:`
- ~line 27: `_normalize_index` currently catches `(ValueError, TypeError, Exception)` — **DROP `Exception`**
- ~line 201: `validate_returns_dataframe` catches broad `Exception` and re-raises as `BABDataError` → narrow to `(ValueError, TypeError, pd.errors.ParserError)`, let unexpected errors propagate

#### 6) `tests/test_bab_messy_data.py` — Add tz-aware fixture
Add a tz-aware fixture exercising `_normalize_index` timezone conversion. Cover tz-aware inputs and gaps. Must pass.

#### 7) `strategies/betting_against_beta/config.py` — Config immutability
`BABConfig` mutates `self.universe` in `__post_init__`; `strategy.py:151` also mutates `cfg.universe` post-validation. Freeze config after validation to prevent downstream mutation. **If** you cannot do this cleanly without breaking existing behavior/tests, explicitly document rationale and tradeoffs in this handoff with concrete next steps — do not silently defer without explanation.

### ACCEPTANCE CRITERIA (ALL MANDATORY)
- [ ] **Every** broad `except Exception:` in `beta.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `data_loader.py` narrowed to specific types or log+re-raise
- [ ] New regression tests prove each previously-silent path now surfaces errors loudly (TDD)
- [ ] tz-aware fixture added to `tests/test_bab_messy_data.py` and passing
- [ ] `BABConfig` post-validation immutability enforced **OR** explicitly deferred with detailed rationale in updated handoff
- [ ] `python3 -m pytest -q` → **348 passed, 0 failed** (no regressions)
- [ ] Update this handoff (`HANDOFF.md`, symlink `HANDOFF_NEXT_SESSION.md`) with new timestamp and concrete progress

### CONSTRAINTS
- **Product-first:** BAB strategy code in `strategies/betting_against_beta/` has highest priority
- **TDD:** Failing test first → implementation → green
- **Crypto-robust:** Handle NaN, inf, constants, mixed dtypes, gaps; prefer explicit errors over silent coercion
- **Deterministic:** No randomness without seed
- **Offline/testable:** No network calls
- **Handoff discipline:** Keep **single durable handoff** updated with timestamp
- **No commits unless explicitly asked:** Leave changes uncommitted for review

**START IMMEDIATELY WITH STEP 0. DO HEAVY WORK. NO WANDERING.**
