# HANDOFF - 2026-10-30T02:36:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T02:36:00Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen style Betting Against Beta for crypto markets)

GATE: python3 -m pytest -q MUST stay GREEN. Current state: 926 passed, 8 skipped. NO REGRESSIONS.
BOTTLENECKS: ALL REMOVED. Pattern-sync drift fixed (`.github/workflows/main.yml` now includes `*/.github/workflows/*`); full suite green. Only THIS HANDOFF.md is the source of truth - ignore any other HANDOFF_*.md files.

CAMPAIGN: DRIVE BAB TO >=95% COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

START ORDER BY COVERAGE GAPS (largest misses first):
1. data_sources.py (79%, 14 uncovered) - offline/mock paths, error handling, edge cases
2. data_loader.py (80%, 56 uncovered) - robust parsing/coercion, gaps/missing cols, dates, dtypes
3. beta.py (83%, 40 uncovered) - rolling beta edge cases (NaN/inf/mismatched windows, min periods, alignment)
4. strategy.py (88%, 23 uncovered) - integration paths, defaults, edge cases, portfolio construction
5. quality.py (93%, 11 uncovered) - inspect and cover real logic paths
6. backtest.py (91%, 7 uncovered) - cost/slippage/turnover edge cases
7. portfolio.py (94%, 14 uncovered) - construction/rebalancing edge cases
8. regime.py (94%, 12 uncovered) - regime detection edge cases
9. shorting.py (95%, 9 uncovered) - shorting constraints
10. signals.py (96%, 4 uncovered) - signal generation edge cases
11. metrics.py (96%, 5 uncovered) - degenerate/NaN/inf cases (71,97,174,187-188)
12. config.py (98%, 3 uncovered) - validation
13. costs.py (99%, 2 uncovered) - finiteness/edge cases
14. sizing.py (100%) - maintain
15. attribution.py (100%) - maintain (defensive finiteness enforced)

RULES (MANDATORY):
- TDD: failing test -> minimal impl/fix -> green. Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints.
- Validate after changes: `python3 -m pytest tests/test_betting_against_beta*.py -q` stays green AND `python3 -m pytest -q` stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- Focus on BAB strategy. Do not touch infra/workflows unless they break the BAB test gate.
- Add real tests with assertions for uncovered logic. Heavy work required (>=4 files).
- If blocked, remove the blocker before moving scope. Do not document scope creep - fix gates first.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Strategy:** Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- **Core Modules:** strategies/betting_against_beta/ (all modules)
- **ABSOLUTE PRIORITY:** `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- **Full Suite:** 926 passed, 8 skipped (GREEN)
- **BAB Tests:** all green
- **Bottlenecks:** All removed. Pattern-sync drift between `scripts/controller_progress.py` (Python `EXCLUDE_PATTERNS`) and `.github/workflows/main.yml` (bash `stage_safe_changes`) was fixed by adding the missing `*/.github/workflows/*` pattern to the workflow. Verified by `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync`.
- **Handoff Source:** Single durable handoff enforced. All other HANDOFF_*.md files are deprecated.

## EXECUTION DIRECTIVES
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when working on strategy modules.
- **Quality over speed:** Correctness always wins. TDD discipline required.
- **Handoff discipline:** Only update THIS HANDOFF.md. Ignore older HANDOFF_*.md files.
- **No scope creep:** Only touch infra if it breaks the BAB gate.
- **Deterministic:** All tests must be deterministic/offline/seeded. No network calls.
- **Blocker removal:** If multiple sessions would be blocked/inefficient by a gate/infrastructure issue preventing BAB progress, fix that blocker first with minimal change, verify gates stay green, then resume BAB coverage campaign.
