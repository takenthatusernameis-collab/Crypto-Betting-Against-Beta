# HANDOFF - 2026-10-28T18:10:52Z (updated 2026-10-28T18:10:52Z)

## Timestamp
2026-10-28T18:10:52Z

## Purpose
Single durable handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD @ 93bab9f. Working tree: clean after the uncommitted change below. Tests: **348 passed, 0 failed** (verified 2026-10-28T18:10:52Z).
- **BOTTLENECK REMOVED (this session)**: `.github/workflows/main.yml` `stage_safe_changes` case list was missing `*/.github/workflows/*`. The prior handoff claimed this fix was applied and the suite was green; that was false — `git diff` was empty and 2 tests were failing (`test_python_patterns_are_subset_of_workflow`, `test_nested_workflow_pattern_is_present_in_workflow`). Added the pattern immediately after `.github/workflows/*` at line 1163. Suite is now genuinely green (348, 0).
- **PRIOR CAMPAIGN COMPLETE**: All 5 phases of "BAB Strategy Robustness & Production Readiness" executed with tests. Prior bottlenecks removed: pattern sync drift, JSON NaN emission, config range validation. Remaining work is hygiene: narrowing silent broad `except Exception:` so future bugs surface loudly instead of being coerced to zero.

## Changes Made This Session (uncommitted, infra-first because it blocked the BAB campaign's green suite)
1. **`.github/workflows/main.yml`** — Prepended `*/.github/workflows/*|` to the bash `stage_safe_changes` case list at line 1163, matching Python `EXCLUDE_PATTERNS`. Fixes 2 failing pattern-sync tests; suite now 348 passed, 0 failed.

## INITIAL TASK FOR NEXT SESSION — READ FIRST

### Focus Campaign: BAB Silent-Error Eradication (HIGH - do not defer)

Product-first: every item below is in the BAB strategy package (`strategies/betting_against_beta/`), not infra. Each item is gated by TDD: write a failing test that proves an error currently swallowed silently now surfaces loudly (specific exception or log+re-raise), then implement, then green suite. Do not skip items; the campaign is not complete until every listed site is narrowed and tested.

1. **`strategies/betting_against_beta/beta.py`** — narrow silent broad `except Exception:`:
   - line 34 (Series alignment fallback in `calculate_beta`) → catch specific types, re-raise unexpected.
   - line 65 (`np.linalg.lstsq` in `calculate_beta`) → catch `np.linalg.LinAlgError` only; re-raise others.
   - line 67 (outer `calculate_beta`) → narrow or remove; unexpected errors must propagate.
   - line 99 (`calculate_beta_fast` lstsq) → catch `np.linalg.LinAlgError` only.
   - line 100 (`calculate_beta_fast` outer) → narrow.
   - line 166 (rolling window `calculate_beta_fast` call) → narrow.
   - line 245 (fallback path window call) → narrow.
   - Contract: degenerate/insufficient data returns documented finite sentinels (0.0 / nan) only for expected cases; bugs must not be masked.

2. **`strategies/betting_against_beta/portfolio.py`** — narrow silent broad `except Exception:`:
   - lines 75, 118, 144, 148, 156 in `construct_portfolio` → `BABPortfolioError`/`BABDataError` must propagate; unexpected errors logged and re-raised, not swallowed with `pass`.

3. **`strategies/betting_against_beta/strategy.py`** — line 189 (weights finiteness guard) — narrow `except Exception:`.

4. **`strategies/betting_against_beta/backtest.py`** — lines 22, 26 (DataFrame coercion), 50 (weights clean) — narrow `except Exception:`.

5. **`strategies/betting_against_beta/data_loader.py`** — line 27 (`_normalize_index` catches `(ValueError, TypeError, Exception)` — drop `Exception`), line 201 (`validate_returns_dataframe` catches broad `Exception` re-raising as `BABDataError`) — narrow to `(ValueError, TypeError, pd.errors.ParserError)` and let unexpected errors propagate.

6. **Add tz-aware fixture** — `tests/test_bab_messy_data.py` covers tz-naive gaps; add a tz-aware fixture exercising `_normalize_index` timezone conversion.

7. **Config `__post_init__` immutability** — `BABConfig` mutates `self.universe` in `__post_init__`; freeze after validation to prevent downstream mutation (strategy.py:151 mutates `cfg.universe` after validation).

### Recon (run first)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status
git diff --stat
python3 -m pytest -q   # expect 348 passed, 0 failed
```

## ACCEPTANCE CRITERIA FOR CAMPAIGN COMPLETION
- [ ] Every broad `except Exception:` in beta.py/portfolio.py/strategy.py/backtest.py/data_loader.py narrowed to specific types or log+re-raise.
- [ ] New regression tests prove each previously-silent path now surfaces errors loudly; suite stays green.
- [ ] tz-aware fixture added and passing.
- [ ] `BABConfig` post-validation immutability enforced (or explicitly deferred with rationale in handoff).
- [ ] `python3 -m pytest -q` all pass (348, 0 failures).
- [ ] Handoff updated with new timestamp.

## CONSTRAINTS
- **Product-first**: BAB strategy above all else; infra only when it blocks BAB.
- **TDD**: Every new behavior needs a failing test first, then implementation, then green suite.
- **Robust to crypto data**: Handle NaNS, constants, mixed dtypes, gaps; explicit errors over silent fallbacks.
- **Deterministic**: No randomness without seed.
- **Offline/testable**: No network calls.
- **Handoff discipline**: Leave single durable handoff (`HANDOFF.md`, target of `HANDOFF_NEXT_SESSION.md`) updated at end of session.
- **No commits unless explicitly asked**: Working changes intentionally uncommitted for review.