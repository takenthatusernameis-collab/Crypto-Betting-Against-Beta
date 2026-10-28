# HANDOFF - 2026-10-28T03:24:06Z

## Timestamp
2026-10-28T03:24:06Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD (f0ff50b chore(kilo): checkpoint agent session). Working tree: **intentional uncommitted change** — `.github/workflows/main.yml` bottleneck fix (see below). Do not commit unless explicitly asked.
- Environment unblocked: `pytest`, `pandas`, `numpy` installed via `pip install -r requirements.txt`; `python3 -m pytest -q` runs locally.
- Suite: **258 passed, 0 failed**. Was red (256 passed, 2 failed) until the bottleneck fix below landed.

## BOTTLECK REMOVED (this session)
CI/infra pattern-sync guardrail was **claimed done in the prior handoff but never actually applied**: `*/.github/workflows/*` was missing from the `stage_safe_changes()` case list in `.github/workflows/main.yml`, so `test_nested_workflow_pattern_is_present_in_workflow` and `test_python_patterns_are_subset_of_workflow` failed and the suite was red. Added `*/.github/workflows/*` to the workflow case list, restoring lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS. All 4 pattern-sync tests now pass; suite 258 passed, 0 failed.

## CAMPAIGN COMPLETE: BAB Production Readiness — Real-Data Path, Transaction Costs & Report Observability
All 7 prior campaign items completed. Every behavior has a test.

## NEXT FOCUS CAMPAIGN (inferred from product name — BAB crypto strategy; no explicit directions given)
**Campaign: BAB Execution Realism & Real-Market Backtesting** — heavy, product-first work. Future agents must not skip these; each item is gated by tests written first (TDD), all tests must pass, and the handoff must be re-timestamped on completion.

1. **Slippage model** (`strategies/betting_against_beta/backtest.py`): apply a slippage cost on turnover (e.g. volatility/spread bps per unit traded) alongside transaction costs so execution realism is priced in. Test: slippage > 0 reduces cumulative vs zero-slippage on the same fixture; scales monotonically with turnover.
2. **Multi-day rebalance** (`strategies/betting_against_beta/strategy.py`, `config.py`): honor `rebalance_freq` (daily / weekly / monthly) — hold weights between rebalance dates instead of daily refresh. Test: weekly rebalance on identical inputs yields strictly fewer rebalance events than daily, and weights are constant within a rebalance window.
3. **Real price ingestion** (`strategies/betting_against_beta/data_loader.py`): new loader path accepting price CSVs/JSON with a date column → returns computation, date parsing, gap handling; prices are not returns. Test: price fixture with dates and gaps produces finite returns DataFrame with DatetimeIndex; malformed dates raise `BABDataError`.
4. **Portfolio-level risk checks** (`strategies/betting_against_beta/portfolio.py`): enforce gross exposure, net exposure (dollar-neutral deviation), and max single-asset weight limits at construction; raise on violation. Test: overweight single asset and non-neutral mix raise clear errors; compliant portfolio passes.
5. **Expanded real-market fixture** (`tests/fixtures/`): 8 crypto assets + BTC benchmark, ~400 daily rows, includes a delisted all-NaN column and a date gap, for reuse by items 1–4.
6. **Verify + handoff**: `python3 -m pytest -q` all pass; HANDOFF.md and HANDOFF_.md re-timestamped.

## ACCEPTANCE CRITERIA (next campaign — start all unchecked)
- [ ] `python3 -m pytest -q` all pass
- [ ] Slippage model test passes (cost reduces cumulative; scales with turnover)
- [ ] Multi-day rebalance test passes (weekly < daily rebalance events; constant weights in window)
- [ ] Real price ingestion test passes (dates parsed, gaps handled, BABDataError on bad dates)
- [ ] Portfolio risk checks pass (gross/net/max-weight enforcement with errors)
- [ ] Expanded real-market fixture added and used by the above tests
- [ ] Every new behavior has a test
- [ ] Handoff re-timestamped

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to `stage_safe_changes()` case list (bottleneck removal; restores lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS; suite now 258 passed, 0 failed).
