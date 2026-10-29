# HANDOFF - 2026-10-29T07:05:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T07:05:00Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## COMPLETED THIS SESSION (2026-10-29T07:05:00Z)
- **Bottleneck removed:** `.github/workflows/main.yml` `stage_safe_changes` bash list was missing `*/.github/workflows/*` (present in Python `EXCLUDE_PATTERNS`), causing controller pattern-sync tests to fail. Added `*/.github/workflows/*` to the workflow list; `tests/test_controller_progress_accounting.py` → 68 passed.
- Baseline restored: `python3 -m pytest -q` → **420 passed, 0 failed, 6 skipped** before edits.
- **Heavy optimization (Priority 3) — multi-file vectorization, numerical parity preserved:**
  1. **portfolio.py**: Replaced per-row/per-cell `.at` loop with elementwise `.map(_clean_signal_value)` + numpy boolean masking for long/short equal-weight assignment (dollar-neutral / long-only / short-only branches preserved). Exact `_clean_signal_value` semantics kept (strings/None/NaN → 0).
  2. **backtest.py**: Single `weights.shift(1)` reused for both lagged returns and turnover (`w_shifted_filled`), removing a redundant `shift` allocation.
  3. **strategy.py**: Collapsed the double finiteness guard into a single defensive clamp; module-level `import numpy as _np`.
  4. **beta.py**: `_calc_rolling_beta_series` sliding-window loop fully vectorized via cumulative-sum array slicing (identical degenerate/NaN semantics).
- Baseline re-verified after edits: `python3 -m pytest -q` → **420 passed, 0 failed, 6 skipped** (zero regressions).

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
1) **beta.py**: Vectorize rolling OLS/covariance, avoid repeated `reindex`, cache intermediates where safe, handle NaN/inf robustly — DONE (rolling series loop vectorized; sizing hardened previously).
2) **signals.py**: Eliminate per-group Python loops, vectorize z-scores/ranks/deciles, use `.groupby` efficiently or pure vector ops — already vectorized; review `_finite_beta_series` `.apply(lambda)` for vector replacement.
3) **portfolio.py**: Optimize construction/rebalancing, reduce copies, vectorize weight calc, preserve beta-neutral enforcement — DONE (vectorized long/short assignment).
4) **strategy.py**: Tighten orchestration, avoid redundant DataFrame copies between stages — DONE (single finiteness pass); continue reducing `load_returns`/pipeline copies.
5) **backtest.py**: Optimize rolling/apply paths, minimize allocations, preserve causal alignment — DONE (single `shift` reuse); continue tightening cost-model path.

#### ACCEPTANCE CRITERIA (HARD REQUIREMENTS):
- `python3 -m pytest -q` → >=420 passed, 0 failed, 6 skipped (zero regressions)
- Substantive changes across **>=4 files** in `strategies/betting_against_beta/` with real logic (no renames/comments only) — **SATISFIED THIS SESSION** (portfolio.py, backtest.py, strategy.py, beta.py)
- Measurable reduction in allocations/copies in hot paths (use efficient patterns: views, `to_numpy()`, vectorized ops)
- Numerical parity preserved (deterministic, offline, no network). Causal/no-lookahead intact.
- Production-grade error handling, match existing style
- Update THIS HANDOFF with new timestamp + concrete completed work + next heavy task before stopping

## CURRENT VERIFIED STATE
- **Branch:** main (HEAD)
- **Working tree:** clean of blocking changes (untracked `__pycache__/` ok)
- **Tests:** **420 passed, 0 failed, 6 skipped** (GREEN)
- **Bottlenecks:** **NONE** (controller pattern-sync desync fixed)

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

### Priority 3: Performance & Scalability (IN PROGRESS)
- [x] Vectorize rolling beta calculations (cumulative sums)
- [x] Harden sizing for numerical stability
- [x] Optimize backtest hot paths / allocations (single shift reuse)
- [x] Optimize portfolio construction (vectorized long/short assignment)
- [x] Optimize strategy/pipeline copies and orchestration (single finiteness pass)
- [ ] Vectorize signals `_finite_beta_series` `.apply(lambda)` path
- [ ] Benchmark hot-path allocations pre/post and record improvement

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
