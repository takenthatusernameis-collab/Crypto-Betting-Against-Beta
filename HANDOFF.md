# HANDOFF - 2026-10-29T05:10:24Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T05:10:24Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## COMPLETED THIS SESSION (2026-10-29T05:10:24Z)
- **Handoff refreshed:** Single durable handoff updated with unambiguous timestamped initial task forcing heavy multi-file optimization work. No blocking bottlenecks detected.
- **Baseline verified:** `python3 -m pytest -q` → **420 passed, 0 failed, 6 skipped** (GREEN)

## IMMEDIATE FIRST TASK FOR NEXT AGENT (EXECUTE NOW - NO DETOURS)

**MANDATORY SESSION START (IN ORDER):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be 420 passed, 0 failed, 6 skipped before edits
```

**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

### PRIMARY CAMPAIGN: Performance & Scalability (Priority 3) — AGGRESSIVE VECTORIZATION
Focus strictly on `strategies/betting_against_beta/`. Eliminate Python loops and redundant allocations in hot paths without changing numerical results.

#### CONCRETE HEAVY DELIVERABLES (MUST COMPLETE - MULTI-FILE)
1) **beta.py**: Vectorize rolling OLS/covariance, avoid repeated `reindex`, cache intermediates where safe, handle NaN/inf robustly
2) **signals.py**: Eliminate per-group Python loops, vectorize z-scores/ranks/deciles, use `.groupby` efficiently or pure vector ops
3) **portfolio.py**: Optimize construction/rebalancing, reduce copies, vectorize weight calc, preserve beta-neutral enforcement
4) **strategy.py**: Tighten orchestration, avoid redundant DataFrame copies between stages
5) **backtest.py**: Optimize rolling/apply paths, minimize allocations, preserve causal alignment

#### ACCEPTANCE CRITERIA (HARD REQUIREMENTS):
- `python3 -m pytest -q` → >=420 passed, 0 failed, 6 skipped (zero regressions)
- Substantive changes across **>=4 files** in `strategies/betting_against_beta/` with real logic (no renames/comments only)
- Measurable reduction in allocations/copies in hot paths (use efficient patterns: views, `to_numpy()`, vectorized ops)
- Numerical parity preserved (deterministic, offline, no network). Causal/no-lookahead intact.
- Production-grade error handling, match existing style
- Update THIS HANDOFF with new timestamp + concrete completed work + next heavy task before stopping

## CURRENT VERIFIED STATE
- **Branch:** main (HEAD)
- **Working tree:** clean of blocking changes (untracked `__pycache__/` ok)
- **Tests:** **420 passed, 0 failed, 6 skipped** (GREEN)
- **Bottlenecks:** **NONE**

## FOCUS CAMPAIGN (HEAVY WORK MANDATORY SEQUENCE)
### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders
- [ ] Expand `quality.py` test coverage
- [ ] Corporate actions assumptions documented + tests
- [x] Pluggable data sources exported
- [x] Efficient caching (`DataCache`)

### Priority 2: Strategy & Risk Management
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [x] Regime detection
- [x] Beta-neutral enforcement

### Priority 3: Performance & Scalability (NEXT - MANDATORY)
- [ ] Vectorize beta calculations, optimize rolling windows, memory efficiency, parallelization where safe, benchmarks

### Priority 4: Analytics & Reporting
- [ ] Extended metrics, attribution, tear sheets, rolling analytics, trade analytics

### Priority 5: Testing & Robustness
- [ ] Property-based tests (hypothesis), stress tests, integration, regression, fuzzing, coverage >95%

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes across >=4 files. If < 4 files touched with real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain >=420 passed, 0 failed
- **SINGLE HANDOFF:** Update THIS FILE after significant progress (timestamp + completed + next heavy task). ONLY `HANDOFF.md` MATTERS.
- **NO COMMITS UNLESS ASKED**

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green
2. Do PRIMARY HEAVY TASK first (TDD, multi-file). No exploration detours.
3. Implement production-grade solution across multiple files → all tests pass → refactor
4. Validate full suite, check regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task
6. Continue heavy work — never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
