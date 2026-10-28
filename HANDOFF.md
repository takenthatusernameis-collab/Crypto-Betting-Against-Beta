# HANDOFF - 2026-10-28T05:24:48Z

## Timestamp
2026-10-28T05:24:48Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**START: BAB EXECUTION REALISM & REAL-MARKET BACKTESTING (TDD, MANDATORY)**

You have no explicit external directions. Treat this as your sole objective. Do not pivot to docs/infra polish unless it directly unblocks the items below. The suite is green (268 passed, 0 failed). The CI/pattern-sync bottleneck was just removed (uncommitted change to `.github/workflows/main.yml`).

**Immediate mandate:** Implement the heavy campaign below with strict TDD. Write a failing test FIRST for every behavior, then implement, then green suite. Every new behavior must have a test. No behavior ships without a test. All tests must pass. Re-timestamp this handoff on completion. Do not commit unless explicitly asked.

## Current State
- Branch main @ HEAD (5963f23 chore(kilo): checkpoint agent session). Working tree: **intentional uncommitted change** — `.github/workflows/main.yml` bottleneck fix (added `*/.github/workflows/*` to `stage_safe_changes()` case list; restores lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS).
- Environment: `pytest`, `pandas`, `numpy` installed via `requirements.txt`; `python3 -m pytest -q` runs locally.
- Suite: **268 passed, 0 failed** (was red: 2 pattern-sync failures until bottleneck fix).
- Campaign infrastructure already present: slippage param in `backtest.py`/`config.py`/`strategy.py`; `rebalance_freq` holding in `strategy.py`; `load_prices` in `data_loader.py`; risk-check params in `portfolio.py`. Expanded fixture `tests/fixtures/real_market_prices_expanded.csv` exists (BTC + 8 crypto + DELISTED, 400 rows). MISSING: tests for all of the above.

## BOTTLENECKS REMOVED
- **CI/pattern-sync**: `.github/workflows/main.yml` `stage_safe_changes()` case list was missing `*/.github/workflows/*` (present in `scripts/controller_progress.py` EXCLUDE_PATTERNS). This failed `test_nested_workflow_pattern_is_present_in_workflow` and `test_python_patterns_are_subset_of_workflow`. Added `*/.github/workflows/*` to the case list. Suite now green (268 passed, 0 failed). Change is intentionally uncommitted.

## NEXT FOCUS CAMPAIGN (BAB Execution Realism & Real-Market Backtesting) — HEAVY WORK REQUIRED, CANNOT BE SKIPPED
Do not stop at scaffolding. Each item below is gated: a failing test must exist before the implementation, and the item is not done until its test passes and the suite is green.

### 1) Slippage model (TEST FIRST — no test, no implementation)
- **File:** `strategies/betting_against_beta/backtest.py` (slippage param exists; wire/confirm it is priced on turnover alongside transaction costs).
- **Req:** Apply slippage cost on turnover (bps per unit traded) alongside transaction costs.
- **Test:** Slippage > 0 reduces cumulative vs zero-slippage on same fixture; scales monotonically with turnover. Slippage must be priced in execution.

### 2) Multi-day rebalance (TEST FIRST)
- **Files:** `strategies/betting_against_beta/strategy.py`, `strategies/betting_against_beta/config.py`
- **Req:** Honor `rebalance_freq` (daily / weekly / monthly). Hold weights between rebalance dates instead of daily refresh.
- **Test:** Weekly rebalance on identical inputs yields strictly fewer rebalance events than daily; weights constant within a rebalance window.

### 3) Real price ingestion (TEST FIRST)
- **File:** `strategies/betting_against_beta/data_loader.py`
- **Req:** Loader path accepting price CSVs/JSON with a date column → returns computation. Prices (not returns). Handle date parsing and gaps.
- **Test:** Price fixture with dates and gaps produces finite returns DataFrame with DatetimeIndex; malformed dates raise `BABDataError`.

### 4) Portfolio-level risk checks (TEST FIRST)
- **File:** `strategies/betting_against_beta/portfolio.py`
- **Req:** Enforce gross exposure, net exposure (dollar-neutral deviation), and max single-asset weight limits at construction; raise on violation.
- **Test:** Overweight single asset and non-neutral mix raise clear errors; compliant portfolio passes.

### 5) Expanded real-market fixture
- **Dir:** `tests/fixtures/`
- **Req:** 8 crypto assets + BTC benchmark, ~400 daily rows, include a delisted all-NaN column and a date gap, for reuse by 1–4. (`real_market_prices_expanded.csv` exists — confirm/reuse; extend if gaps/delisted column incomplete.)

### 6) Verify + handoff
- Run `python3 -m pytest -q` until all pass.
- Re-timestamp HANDOFF.md (and ensure HANDOFF_NEXT_SESSION.md points to it).
- Update this file with final state if needed.

## ACCEPTANCE CRITERIA (must all be checked — none optional)
- [ ] `python3 -m pytest -q` all pass
- [ ] Slippage model test passes (cost reduces cumulative; scales with turnover) — test written first
- [ ] Multi-day rebalance test passes (weekly < daily rebalance events; constant weights in window) — test written first
- [ ] Real price ingestion test passes (dates parsed, gaps handled, `BABDataError` on bad dates) — test written first
- [ ] Portfolio risk checks pass (gross/net/max-weight enforcement with errors) — test written first
- [ ] Expanded real-market fixture added/confirmed and used by the above tests
- [ ] Every new behavior has a test (no test = no merge)
- [ ] Handoff re-timestamped to completion time

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.
- Do not get distracted by infra/docs unless directly blocking BAB campaign items.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to `stage_safe_changes()` case list (bottleneck removal; restores lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS; suite now 268 passed, 0 failed).
