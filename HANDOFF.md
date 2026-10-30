# HANDOFF - 2026-10-30T09:38:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T09:38:00Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto: long low-beta, short high-beta vs BTC benchmark).

GATE: python3 -m pytest -q MUST stay GREEN. Last verified: 1012 passed, 11 skipped (GREEN). BAB tests (tests/test_betting_against_beta*.py) must pass.
BOTTLECKS: NONE. Controller/workflow drift fixed (stage_safe_changes synced to include */.github/workflows/*).

CURRENT COVERAGE (BAB modules, term-missing) - Coverage via tests/test_betting_against_beta*.py only:
- TOTAL BAB: 65% (2454 stmts / 857 miss). Need to drive to >=95%.
- beta.py          59%  (missing: 10-19,23-53,68-93,98,105-106,108,118,120-125,134,136-137,142,144,148,154,156-159,173,216,218,300-309)
- data_loader.py   70%  (large gaps: 37-41,44,47,64-65,72-73,86-87,107,117-119,149,...,479-484)
- backtest.py      73%  (20,23-26,28-31,49-53,58-59,69-70,77-78,102)
- quality.py       7%   (mostly untested)
- portfolio.py     54%  (17-40,70-71,87-88,155-160,178-179,200-201,204-205,212-213,260-346)
- regime.py        63%  (14,16,18,31,79,81-85,97,111,130,139-140,157-193,212,217,221,243-246,255,259,269-271,275-282)
- data_sources.py  42%  (mostly untested)
- signals 45%, strategy 53%, config 74%, shorting 95%, metrics 96%, sizing 99%, costs 99%, attribution 14%, cli 0%, data 100%, errors/__init__ 100%

MANDATORY CAMPAIGN (HEAVY WORK): Drive BAB total >=95%. Touch >=4 files with REAL LOGIC/TESTS. Do not do docs-only.

FOCUS ORDER:
1) beta.py (59%) - estimate_betas/rolling_beta branches, calculate_beta alignment/truncation/degenerate, calculate_beta_fast guards, _calc_rolling_beta_series edge cases
2) data_loader.py (70%) - many paths (CSV/JSON, coercion, tz, empty/single-asset, NA/inf, bad dates)
3) backtest.py (73%) - costs, cumulative, one-day lag edges
4) quality.py (7%) - entire module needs tests

EXECUTE IN ORDER:
1. MEASURE: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing to get exact current gaps/branches.
2. TDD PER GAP: For each uncovered line/branch in beta.py first, write DETERMINISTIC/OFFLINE/SEEDED tests with REAL ASSERTIONS (NaN/inf/zeros/mismatched shapes, ties, deciles/quantiles, one-day lag, dollar-neutral). Make them fail, fix minimal impl to be correct, go green.
3. REPEAT for data_loader.py, backtest.py, quality.py as needed to reach >=95% total BAB without regressing >=95% modules.
4. VERIFY: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py -q && PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q stay green. Report coverage delta per touched module + BAB total.
5. HANDOFF: ONLY update THIS HANDOFF.md at end if state materially changes. NO COMMITS unless explicitly asked.

STRICT RULES:
- Deterministic/offline/seeded only. No network.
- NO bare except:. Enforce finiteness (no NaN/inf).
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window constraints, rank logic.
- TDD: failing test -> minimal impl/fix -> green.
- BAB-first. Only touch infra/workflows if they break BAB gate.
- Real tests with assertions; >=4 files touched.
- Remove blockers before expanding scope.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core Modules: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB coverage (tests/test_betting_against_beta*.py): 65% total (target >=95%)
- Bottlenecks: NONE (workflow/controller drift resolved)
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work: >=4 files with real logic/tests per session when working on strategy modules.
- Quality over speed: correctness always wins. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
