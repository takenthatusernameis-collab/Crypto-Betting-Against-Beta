# HANDOFF - 2026-10-30T03:14:08Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T03:14:08Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen style Betting Against Beta for crypto markets)

GATE: python3 -m pytest -q MUST stay GREEN. Current state: 992 passed, 11 skipped. NO REGRESSIONS.
BOTTLENECKS: pattern-sync drift removed from working tree (`.github/workflows/main.yml` `stage_safe_changes` now includes `*/.github/workflows/*` to match `scripts/controller_progress.py` EXCLUDE_PATTERNS); controller suite 68/68 green. Full suite 992 passed / 11 skipped. Only THIS HANDOFF.md is the source of truth - ignore any other HANDOFF_*.md files. NOTE: workflow fix is in the working tree and NOT yet committed; do not commit unless explicitly asked.

CAMPAIGN: DRIVE BAB TO >=95% TOTAL COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

COVERAGE AFTER THIS SESSION (992 passed / 11 skipped, total 94%, was 92%):
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
12. sizing.py (100%) - maintain
13. attribution.py (100%) - maintain
14. strategy.py (97%, 5 uncovered) - 41-42, 181, 188-189 (mostly defensive/dead paths)
15. data_sources.py (94%, 4 uncovered) - 20, 47, 94-95 (20/47 need pyarrow/tables; not installed)

START ORDER BY COVERAGE GAPS (largest misses first): data_loader.py, beta.py, backtest.py, then portfolio.py/quality.py/regime.py/shorting.py/signals.py. Add real tests with assertions for uncovered logic. Heavy work required (>=4 files).

NEW CAMPAIGN TEST FILES ADDED THIS SESSION (59 tests, all green):
- tests/test_bab_data_loader_campaign.py
- tests/test_bab_beta_campaign.py
- tests/test_bab_strategy_campaign.py
- tests/test_bab_data_sources_campaign.py

RULES (MANDATORY):
- TDD: failing test -> minimal impl/fix -> green. Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints.
- Validate after changes: `python3 -m pytest tests/test_betting_against_beta*.py -q` stays green AND `python3 -m pytest -q` stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- Focus on BAB strategy. Do not touch infra/workflows unless they break the BAB test gate.
- Add real tests with assertions for uncovered logic. Heavy work required (>=4 files).
- If blocked, remove the blocker before moving scope. Do not document scope creep - fix gates first.
- Coverage target: >=95% total before declaring the campaign complete.

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Strategy:** Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- **Core Modules:** strategies/betting_against_beta/ (all modules)
- **ABSOLUTE PRIORITY:** `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- **Full Suite:** 992 passed, 11 skipped (GREEN)
- **BAB Tests:** all green
- **Bottlenecks:** pattern-sync drift between `scripts/controller_progress.py` (Python `EXCLUDE_PATTERNS`) and `.github/workflows/main.yml` (bash `stage_safe_changes`) fixed in working tree by adding `*/.github/workflows/*` to the workflow case list. Verified by `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync` (68 passed).
- **Handoff Source:** Single durable handoff enforced. All other HANDOFF_*.md files are deprecated.
- **Coverage:** total 94% (up from 92%); four largest-gap modules each gained 4-9 points.

## EXECUTION DIRECTIVES
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when working on strategy modules.
- **Quality over speed:** Correctness always wins. TDD discipline required.
- **Handoff discipline:** Only update THIS HANDOFF.md. Ignore older HANDOFF_*.md files.
- **No scope creep:** Only touch infra if it breaks the BAB gate.
- **Deterministic:** All tests must be deterministic/offline/seeded. No network calls.
- **Blocker removal:** If multiple sessions would be blocked/inefficient by a gate/infrastructure issue preventing BAB progress, fix that blocker first with minimal change, verify gates stay green, then resume BAB coverage campaign.
