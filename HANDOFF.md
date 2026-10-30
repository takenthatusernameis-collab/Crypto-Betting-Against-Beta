# HANDOFF - 2026-10-30T06:32:33Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T06:32:33Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto).

GATE: python3 -m pytest -q MUST stay GREEN.
- BAB: 285 passed, 6 skipped (tests/test_betting_against_beta*.py)
- Full: 1012 passed, 11 skipped

CURRENT BOTTLENECKS: NONE VISIBLE. If any infra/test harness blocks BAB, REMOVE IT FIRST (verify gates green) before changing BAB scope.

MANDATORY CAMPAIGN (HEAVY WORK):
DRIVE BAB TO >=95% TOTAL COVERAGE. THIS SESSION MUST TOUCH >=4 FILES WITH REAL LOGIC/TESTS.
FOCUS ORDER (highest ROI): data_loader.py, beta.py, portfolio.py, backtest.py, sizing.py, signals.py, metrics.py, costs.py, quality.py, regime.py, shorting.py, data_sources.py, strategy.py, attribution.py.

TASKS (DO IN ORDER):
1. IDENTIFY UNTESTED/LOW-COVERAGE: Run targeted coverage on BAB modules to find lowest coverage (e.g. pytest with coverage) or scan for untested branches. Pick >=2 modules with largest gaps.
2. HEAVY TDD: For each gap, write DETERMINISTIC/OFFLINE/SEEDED tests with REAL ASSERTIONS covering NaN/inf/zeros/mismatched shapes, tz/dates, coercion/NA, rolling stats edge cases, deciles/quantiles, one-day lag, dollar-neutral, rank/decile logic, beta window constraints. Fix minimal implementation if needed to handle edge cases correctly.
3. VERIFY: python3 -m pytest tests/test_betting_against_beta*.py -q stays green AND python3 -m pytest -q stays green. Report coverage delta.
4. HANDOFF DISCIPLINE: ONLY update THIS HANDOFF.md at end if state materially changes. NO COMMITS unless explicitly asked.

STRICT RULES:
- Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf).
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window constraints, rank logic.
- TDD: failing test -> minimal impl/fix -> green.
- Focus BAB. Only touch infra/workflows if they break BAB gate.
- Add real tests with assertions; no docs-only changes. Heavy work required (>=4 files).
- If blocked, remove blocker before moving scope.

START NOW: Identify lowest-coverage BAB modules and begin heavy coverage work.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- Core Modules: strategies/betting_against_beta/ (all modules)
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB Tests: 285 passed, 6 skipped (GREEN)
- Bottlenecks: None observed. Infrastructure previously fixed (pattern-sync in `.github/workflows/main.yml`).
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work: >= 4 files with real logic/tests per session when working on strategy modules.
- Quality over speed: correctness always wins. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they block BAB progress, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
