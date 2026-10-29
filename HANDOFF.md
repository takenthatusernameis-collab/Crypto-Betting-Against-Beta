# HANDOFF - 2026-10-29T05:08:22Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T05:08:22Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## COMPLETED THIS SESSION (2026-10-29T05:08:22Z)
- **Handoff hardened:** Refreshed single durable handoff with an unambiguous, timestamped initial task for the next agentic session. Bottlenecks reviewed — none remain blocking (baseline green).
- **Workflow/CI pattern sync:** Already resolved (added `*/.github/workflows/*` to `stage_safe_changes` in `.github/workflows/main.yml` matching Python `EXCLUDE_PATTERNS`).
- **Beta-neutral enforcement:** Completed in prior session (config/portfolio/strategy integrated).
- **Baseline:** `python3 -m pytest -q` → **420 passed, 0 failed, 6 skipped** (green).

## IMMEDIATE FIRST TASK FOR NEXT AGENT (EXECUTE NOW - NO DETOURS)

**MANDATORY SESSION START (IN ORDER):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
# MUST be green before any edits
python3 -m pytest -q  # expect 420 passed, 0 failed, 6 skipped
```

**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

### PRIMARY CAMPAIGN: Performance & Scalability (Priority 3) — VECTORIZE/OPTIMIZE HOT PATHS
Focus strictly on `strategies/betting_against_beta/`. Prior work optimized beta/portfolio; go deeper across the full pipeline for large universes without changing numerical results.

#### CONCRETE HEAVY DELIVERABLES (MUST COMPLETE)
1) **Hot paths**: `strategies/betting_against_beta/strategy.py`, `backtest.py`, `signals.py`, `data_loader.py`, `beta.py`, `portfolio.py`
   - Eliminate repeated reindex/copies, prefer views/in-place where safe
   - Optimize rolling/window computations and DataFrame allocations
   - Vectorize where feasible; avoid Python loops in tight loops
   - Preserve causal/no-lookahead, determinism, NaN/inf/zero/gap handling
2) **Robustness**: Add/extend tests for large-universe edge cases and perf-sensitive paths; maintain parity
3) **Verification**: Run full suite repeatedly; ensure zero regressions

**ACCEPTANCE CRITERIA (HARD REQUIREMENTS):**
- `python3 -m pytest -q` → >=420 passed, 0 failed, 6 skipped (no regressions)
- Measurable reduction in allocations/copies in hot paths (substantive refactor across >=3 files)
- Numerical parity preserved (deterministic, offline, no network)
- Production-grade error handling, follows existing style
- Update THIS HANDOFF with timestamp + concrete completed work + next heavy task before stopping

## CURRENT VERIFIED STATE
- **Branch:** main (HEAD)
- **Working tree:** `.github/workflows/main.yml` modified (pattern sync). `__pycache__/` untracked.
- **Tests:** **420 passed, 0 failed, 6 skipped** (GREEN)
- **Bottlenecks:** **NONE** (removed)

## BARRIERS REMOVED
- CI/workflow pattern-sync drift resolved (`*/.github/workflows/*` in both Python `EXCLUDE_PATTERNS` and workflow `stage_safe_changes`)
- Single durable handoff enforced — **ONLY `HANDOFF.md` MATTERS**

## FOCUS CAMPAIGN (HEAVY WORK MANDATORY SEQUENCE)
### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders
- [ ] Expand `quality.py` test coverage
- [ ] Corporate actions: document splits/dividends/airdrops assumptions explicitly + tests
- [x] Pluggable data sources exported
- [x] Efficient caching (`DataCache`)

### Priority 2: Strategy & Risk Management
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [x] Regime detection
- [x] Beta-neutral enforcement

### Priority 3: Performance & Scalability (NEXT - MANDATORY, CANNOT SKIP)
- [ ] Vectorize beta calculations, optimize rolling windows, memory efficiency, parallelization where safe, benchmarks

### Priority 4: Analytics & Reporting
- [ ] Extended metrics (Sharpe/Sortino/Calmar/maxDD, rolling), attribution, tear sheets, rolling analytics, trade analytics

### Priority 5: Testing & Robustness
- [ ] Property-based tests (hypothesis), stress tests, integration, regression, fuzzing, coverage >95%

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes. If < 3 files with no real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain >=420 passed, 0 failed
- **SINGLE HANDOFF:** Update THIS FILE after significant progress (timestamp + completed + next heavy task)
- **NO COMMITS UNLESS ASKED**

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green
2. Do PRIMARY HEAVY TASK first (TDD, multi-file). No exploration detours.
3. Implement production-grade solution across multiple files → all tests pass → refactor
4. Validate full suite, check regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task
6. Continue heavy work — never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
