# HANDOFF - 2026-10-28T17:19:15Z

## Timestamp
2026-10-28T17:19:15Z

## Purpose
Single durable handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted changes** (see latest state). Tests: **249 passed, 0 failed** (as of last session).
- Bottlenecks removed in recent sessions (pattern sync, orphaned fixtures exercised, all-NaN column dropping, silent broad excepts eliminated, beta robustness, report JSON sanitization).

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: BAB Strategy Robustness & Production Readiness (HEAVY - complete end-to-end)

Recon (fast):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status
git diff --stat
python3 -m pytest -q
```

#### Phase 1: Data & Loading (must be deterministic)
1. **`strategies/betting_against_beta/data_loader.py`** - Harden `load_crypto_data`/coercion: mixed dtypes, string/inf/-inf, junk columns. Drop non-numeric or raise `BABDataError` with actionable message. Never silently coerce to all-NaN.
2. **`strategies/betting_against_beta/data.py`** - Ensure validation is strict and consistent with loader; add tests for partially numeric frames.
3. **Tests**: Add/strengthen `tests/test_bab_messy_data.py` for mixed types, duplicate dates, tz-aware, all-NaN columns, index gaps.

#### Phase 2: Beta Calculation (no crashes on messy crypto data)
4. **`strategies/betting_against_beta/beta.py`** - `calculate_rolling_beta` must handle: all-NaN asset/benchmark, constant series (zero variance), benchmark with NaNs, insufficient rows. Return NaN where undefined but **never raise uncaught exceptions**; raise `BABDataError` only when benchmark missing/invalid per contract.
5. **Tests**: Cover NaN-heavy windows, constant prices, single valid pair, benchmark gaps.

#### Phase 3: Signals & Portfolio (guarantee finite, sane outputs)
6. **`strategies/betting_against_beta/signals.py`** - Eliminate remaining broad `except Exception:` without logging/intent; only catch specific cases. Ensure signals finite.
7. **`strategies/betting_against_beta/portfolio.py`** - Guarantee finite weights (sum to ~1 or handle zero-signal case deterministically). No silent zeros from exceptions. Add tests for all-zero signals, single asset, ties.
8. **Tests**: Extend coverage for edge portfolios.

#### Phase 4: Strategy, Config, Backtest, Reports
9. **`strategies/betting_against_beta/strategy.py`** - Enforce `min_rows` strictly; `resolved_universe` intersection-empty must raise/behave per contract with clear errors.
10. **`strategies/betting_against_beta/config.py`** - Validate ranges (windows, min_rows) with helpful errors.
11. **`scripts/bab_backtest_report.py`** - Ensure JSON output has no NaN/inf (use `allow_nan=False` or sanitize). Round/truncate safely.
12. **Tests**: Strengthen `tests/test_bab_backtest_report.py`, add cases for degenerate backtests.

#### Phase 5: CI/Infra Sync + Verification
13. **Pattern sync**: Keep `EXCLUDE_PATTERNS` identical between `scripts/controller_progress.py` and `.github/workflows/main.yml`. Run `pytest -q tests/test_workflow_patterns.py tests/test_controller_exclude_patterns.py` (or equivalent). Fix drift immediately.
14. **Full verification**: `python3 -m pytest -q` - all must pass. No regressions.
15. **Handoff update**: Write new timestamped handoff (or update this file) with summary of changes/tests.

## ACCEPTANCE CRITERIA
- [ ] All Phase 1-5 tasks completed with tests
- [ ] No NaN/inf weights/signals/metrics on messy inputs
- [ ] Consistent `BABDataError` for invalid data (no silent broad excepts masking bugs)
- [ ] CI pattern sync tests pass
- [ ] `python3 -m pytest -q` all pass (>=249, no failures)
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- **Product-first**: BAB strategy above all else.
- **TDD**: Every new behavior needs a test.
- **Robust to crypto data**: Handle NaNs, constants, mixed dtypes, gaps.
- **Deterministic**: No randomness without seed; explicit errors over silent fallbacks.
- **Offline/testable**: No network calls.
- **Handoff discipline**: Leave single durable handoff updated.
- **No commits unless explicitly asked**: Working changes intentionally uncommitted for review.

## NOTES
- Use this as the single source of truth for the next session. Focus on making BAB crash-proof on realistic messy data. If you find other bottlenecks blocking heavy work, remove them while staying product-first.
