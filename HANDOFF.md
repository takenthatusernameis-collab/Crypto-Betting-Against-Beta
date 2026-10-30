# HANDOFF - 2026-10-30T03:34:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T03:34:00Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen style Betting Against Beta for crypto markets)

GATE: python3 -m pytest -q MUST stay GREEN. Current state: 992 passed, 11 skipped (990 passed + 2 fixed controller tests = 992 passed). NO REGRESSIONS.
BOTTLENECKS REMOVED: pattern-sync drift fixed - `.github/workflows/main.yml` stage_safe_changes now includes `*/.github/workflows/*` matching `scripts/controller_progress.py` EXCLUDE_PATTERNS. Controller suite 68/68 green. Full suite green. Only THIS HANDOFF.md is source of truth - ignore any other HANDOFF_*.md files. Workflow change is in working tree (not committed).

CAMPAIGN: DRIVE BAB TO >=95% TOTAL COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

CURRENT COVERAGE GAPS (by uncovered lines, focus largest first):
1. data_loader.py (89%, 31 uncovered) - 37-41 tz path, 44, 64-65, 72-73, 107, 117-119, 159, 178-179, 183-184, 221-222, 247, 302-304, 321, 331-333, 357-358
2. beta.py (88%, 28 uncovered) - 27, 52-53, 71, 73, 75, 77, 80, 82, 85-86, 98, 105-106, 108, 118, 120-121, 124-125, 142, 154, 156-159, 301, 309
3. backtest.py (91%, 7 uncovered) - 53, 58-59, 69-70, 77-78
4. portfolio.py (94%, 14 uncovered) - 29, 39-40, 87-88, 155-160, 200-201, 275
5. quality.py (93%, 11 uncovered) - 30, 47-48, 132, 187-188, 211-212, 245-246, 259
6. regime.py (94%, 12 uncovered) - 111, 139-140, 175-177, 181-182, 185, 188, 190, 217
7. shorting.py (95%, 9 uncovered) - 46, 53-54, 137-143
8. signals.py (96%, 4 uncovered) - 28, 37, 71, 75
9. metrics.py (96%, 5 uncovered) - 71, 97, 174, 187-188
10. config.py (98%, 3 uncovered) - 95-96, 113
11. costs.py (99%, 2 uncovered) - 59-60
12. strategy.py (97%, 5 uncovered) - 41-42, 181, 188-189

FOCUS ORDER: data_loader.py -> beta.py -> backtest.py -> portfolio.py/quality.py/regime.py/shorting.py -> others. Add real tests with assertions for uncovered branches/paths. Heavy work required (>=4 files). Do not stop until >=95% total coverage.

EXISTING CAMPAIGN TESTS (keep passing):
- tests/test_bab_data_loader_campaign.py
- tests/test_bab_beta_campaign.py
- tests/test_bab_strategy_campaign.py
- tests/test_bab_data_sources_campaign.py

RULES (MANDATORY):
- TDD: failing test -> minimal impl/fix -> green. Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints, rank/decile logic.
- Validate after changes: `python3 -m pytest tests/test_betting_against_beta*.py -q` stays green AND `python3 -m pytest -q` stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- Focus on BAB strategy. Do not touch infra/workflows unless they break the BAB test gate.
- Add real tests with assertions for uncovered logic. Heavy work required (>=4 files).
- If blocked, remove the blocker before moving scope. Do not document scope creep - fix gates first.
- Coverage target: >=95% total before declaring the campaign complete. Report coverage delta per batch.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Strategy:** Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- **Core Modules:** strategies/betting_against_beta/ (all modules)
- **ABSOLUTE PRIORITY:** `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- **Full Suite:** 992 passed, 11 skipped (GREEN)
- **BAB Tests:** all green
- **Bottlenecks:** Removed - pattern-sync fixed in `.github/workflows/main.yml` (added `*/.github/workflows/*`). Controller tests all pass (68/68).
- **Handoff Source:** Single durable handoff enforced. All other HANDOFF_*.md files are deprecated.
- **Coverage:** 94% total (campaign in progress)

## EXECUTION DIRECTIVES
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when working on strategy modules.
- **Quality over speed:** Correctness always wins. TDD discipline required.
- **Handoff discipline:** Only update THIS HANDOFF.md. Ignore older HANDOFF_*.md files.
- **No scope creep:** Only touch infra if it breaks the BAB gate.
- **Deterministic:** All tests must be deterministic/offline/seeded. No network calls.
- **Blocker removal:** If multiple sessions would be blocked/inefficient by a gate/infrastructure issue preventing BAB progress, fix that blocker first with minimal change, verify gates stay green, then resume BAB coverage campaign.
