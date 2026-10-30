# HANDOFF - 2026-10-30T02:35:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T02:35:00Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen style Betting Against Beta for crypto markets)
GATE: python3 -m pytest -q MUST stay GREEN. Current state: 926 passed, 8 skipped. NO REGRESSIONS.
BOTTLENECKS: ALL REMOVED. Pattern-sync drift fixed (`.github/workflows/main.yml` now includes `*/.github/workflows/*`); full suite green.

CAMPAIGN: DRIVE BAB TO >=95% COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

START ORDER BY COVERAGE GAPS (largest misses first):
1. data_sources.py (79%, 14 uncovered) - offline/mock paths, error handling, edge cases
2. beta.py (83%, 40 uncovered) - rolling beta edge cases (NaN/inf/mismatched windows, min periods)
3. data_loader.py (80%, 56 uncovered) - robust parsing/coercion, gaps/missing cols, dates
4. strategy.py (88%, 23 uncovered) - integration paths, defaults, edge cases
5. backtest.py (91%, 7 uncovered) - cost/slippage/turnover edge cases
6. portfolio.py (94%, 14 uncovered) - construction/rebalancing edge cases
7. regime.py (94%, 12 uncovered) - regime detection edge cases
8. shorting.py (95%, 9 uncovered) - shorting constraints
9. signals.py (96%, 4 uncovered) - signal generation edge cases
10. metrics.py (96%, 5 uncovered) - degenerate/NaN/inf cases (71,97,174,187-188)
11. config.py (98%, 3 uncovered) - validation
12. costs.py (99%, 2 uncovered) - finiteness/edge cases
13. sizing.py (100%) - maintain
14. quality.py (93%, 11 uncovered) - inspect and cover real logic
15. attribution.py (100%) - maintain (defensive finiteness enforced)

RULES (MANDATORY):
- TDD: failing test -> minimal impl/fix -> green. Deterministic/offline/seeded only.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints.
- Validate after changes: `python3 -m pytest tests/test_betting_against_beta*.py -q` stays green AND `python3 -m pytest -q` stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- Focus on BAB strategy. Do not touch infra/workflows unless they break the BAB test gate.
- Add real tests with assertions for uncovered logic. Heavy work required.
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

## EXECUTION DIRECTIVES
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when working on strategy modules.
- **Quality over speed:** Correctness always wins. TDD discipline required.
- **Handoff discipline:** Only update THIS HANDOFF.md. Ignore older HANDOFF_*.md files.
- **No scope creep:** Only touch infra if it breaks the BAB gate.
- **Deterministic:** All tests must be deterministic/offline/seeded. No network calls.