# HANDOFF - 2026-10-30T01:40:10Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T01:40:10Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen style Betting Against Beta for crypto markets)
GATE: python3 -m pytest -q MUST stay GREEN. Current state: 916 passed, 8 skipped. NO REGRESSIONS.

CAMPAIGN: DRIVE BAB TO >=95% COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

START ORDER BY COVERAGE GAPS (largest misses first):
1. attribution.py (17% coverage, 25/30 uncovered) - trade_attribution/attribution_totals robustness for zeros/NaN/mismatched shapes/alignment
2. data_sources.py (42%, 39 uncovered) - offline/mock paths, error handling, edge cases
3. signals.py (45%, 62 uncovered) - signal generation edge cases
4. portfolio.py (54%, 103 uncovered) - construction/rebalancing edge cases
5. strategy.py (53%, 93 uncovered) - integration paths
6. beta.py (59%, 96 uncovered) - rolling beta edge cases (NaN/inf/mismatched windows)
7. regime.py (63%, 69 uncovered) - regime detection edge cases
8. data_loader.py (70%, 85 uncovered) - data loading edge cases
9. backtest.py (73%, 20 uncovered) - backtest edge cases
10. config.py (74%, 52 uncovered) - config validation

CLOSE SMALL GAPS NEXT:
- metrics.py (96%, 5 uncovered: 71,97,174,187-188) - degenerate/NaN/inf cases
- shorting.py (95%, 9 uncovered) - shorting constraints
- sizing.py (98%, 4 uncovered: 55,96,113-114) - bounds/finiteness
- costs.py (99%, 2 uncovered: 59-60) - finiteness/edge cases
- quality.py (7% currently) - lots of uncovered code, but needs careful inspection

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
- **Full Suite:** 916 passed, 8 skipped (GREEN)
- **BAB Tests:** 285 passed, 6 skipped (GREEN)
- **Overall BAB Coverage:** ~65% (2447 stmts, 850 miss)
- **Bottlenecks:** All removed - workflow pattern sync fixed, suite gate restored

## BOTTLENECKS REMOVED
- **Workflow/controller pattern sync:** Fixed `.github/workflows/main.yml` stage_safe_changes to include `*/.github/workflows/*` matching `scripts/controller_progress.py` EXCLUDE_PATTERNS. All controller-progress tests pass (68/68).
- **Suite gate restored:** Full suite green.

## EXECUTION DIRECTIVES
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when working on strategy modules.
- **Quality over speed:** Correctness always wins. TDD discipline required.
- **Handoff discipline:** Only update THIS HANDOFF.md. Ignore older HANDOFF_*.md files.
- **No scope creep:** Only touch infra if it breaks the BAB gate.
- **Deterministic:** All tests must be deterministic/offline/seeded. No network calls.
