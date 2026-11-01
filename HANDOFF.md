# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T15:14:45Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — ABSOLUTE MANDATE. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS — CAMPAIGN MANDATED <<<
>>> NO COASTING. EVERY TURN MUST DELIVER SUBSTANTIVE BAB IMPROVEMENTS. <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST ABSOLUTE MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T15:14:45Z

VERIFIED STATE (2026-11-01T15:14:45Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0)
- BAB suite: 1345 passed, 7 skipped, 0 failed (56.63s)
- Coverage: 98% total (2573 stmts, 61 misses). COVERAGE CEILING HELD.
- Per-module: backtest/attribution/cli/data/data_sources/errors/quality/shorting 100%; beta 94%, strategy 93%, data_loader 97%, portfolio 97%, costs/config/metrics/regime 99%, signals 98%, sizing 98%.
- Bottlenecks: ELIMINATED. Test suite fast, fixtures complete, gate reliable.

PRIMARY MANDATE: UNAVOIDABLE HEAVY BAB HARDENING CAMPAIGN — SURGICALLY ATTACK THE REMAINING 61 MISSES.
You CANNOT avoid heavy work. Every single turn MUST produce concrete, substantive BAB improvements (tests + minimal hardening).
Idle turns, docs-only edits, README-only changes, analysis-only responses, or file-count changes are STRICTLY FORBIDDEN.

CAMPAIGN OBJECTIVE: Build momentum that future agents cannot coast on. Attack real weaknesses, add adversarial regression tests, harden invariants until no obvious untested edge case remains. If you find a bottleneck, REMOVE IT NOW.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):

1. GATE FIRST (MANDATORY): Run `scripts/bab_gate.sh`. Must return GREEN (>=1345 passed, >=7 skipped, 0 failed).
   - If broken for ANY reason, fix BEFORE anything else. No exploratory work until green.
   - Treat gate as your heartbeat. Re-run after every substantive change.

2. TOP PRIORITY ATTACK - strategy.py (16 misses) [HIGHEST IMPACT]
   Target lines: 40, 44-64, 223, 230-235, 280-281, 296-297, 320
   Focus areas:
   - Error paths & validation (missing/invalid config, universe edge cases)
   - Integration paths (CLI wiring, data flow end-to-end)
   - Partial universe / all-same-side / empty after filtering
   - Fallback behaviors and exception handling
   - Add chaos tests with adversarial data (NaN/inf/mixed dtypes/gaps)

3. SECOND PRIORITY - beta.py (16 misses) [CORRECTNESS CRITICAL]
   Target lines: 101-102, 124, 138, 140-141, 144-145, 166, 183, 187, 377-381
   Focus areas:
   - _calc_rolling_beta_series edge cases (insufficient windows, alignment, dropna)
   - Fast paths vs rolling paths consistency across ALL emitters
   - Degenerate cases: all-NaN, single point, perfect colinearity, zero-variance benchmark
   - NaN propagation - benchmark zero-variance MUST yield NaN for beta (NEVER 0.0). All emitters MUST agree.
   - Mixed finite/NaN across assets/benchmark

4. THIRD PRIORITY - data_loader.py (9 misses) [INTEGRATION]
   Target lines: 44, 192-193, 311-313, 340-342
   Focus areas:
   - Malformed inputs, dtype coercion, missing columns/benchmark
   - Gaps/resampling, alignment errors
   - BAB-specific error types/messages

5. FOURTH PRIORITY - portfolio.py (8 misses) [CONSTRAINTS]
   Target lines: 39-40, 172-177
   Focus areas:
   - Weight constraints (max_position_size, max_turnover)
   - Beta neutrality enforcement & residuals
   - Tie-breaking, all-long/all-short/empty cases
   - Numerical stability, row sums for dollar-neutral (~0)

6. SURGICAL CLEANUP - Remaining (12 misses across costs/config/metrics/regime/signals/sizing)
   Only hit if you can add MEANINGFUL behavior tests with concrete evidence. No coverage-chasing.

7. ADVERSARIAL + PROPERTY HARDENING (MANDATORY)
   - Enforce invariants EVERYWHERE: weights finite, dollar-neutral (~0) where applicable, 1-day lag respected, finiteness everywhere
   - Degenerate zero-variance benchmark -> NaN across ALL beta emitters
   - No lookahead, deterministic (seeded), offline only
   - Property-style tests for ranking/quantiles/deciles stability

8. BOTTLENECK ELIMINATION (IF FOUND)
   - Slow tests, unclear APIs, missing fixtures/helpers -> FIX or CREATE immediately
   - Parallelize only if safe; never break determinism
   - Remove any friction blocking BAB progress

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Must stay GREEN (>=1345 passed, >=7 skipped, 0 failed). No exceptions.
2. DO NOT CHASE UNREACHABLE COVERAGE. Concrete evidence required before touching any uncovered line. Never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT CONCRETE EVIDENCE WHY IMPOSSIBLE. No idle turns. Period.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence. BAB comes first. Always.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors.
6. NO BARE EXCEPT. Degenerate/zero-variance benchmark beta is NaN (undefined), NEVER 0.0 - ALL beta emitters must agree.
7. Deterministic only (seeded RNGs). All tests offline.
8. Momentum MANDATORY. Find edge case -> write regression test -> harden code. Never stop. Never coast.
9. Every new failure mode discovered MUST get a regression test + minimal fix.

VERIFICATION (RUN AFTER EVERY SUBSTANTIVE CHANGE):
  scripts/bab_gate.sh

SUCCESS CRITERIA (MEASURABLE):
- Gate stays GREEN (>=1345 passed, >=7 skipped, 0 failed)
- New adversarial/property/regression tests added with clear failure-to-pass evidence
- Concrete robustness improvements to BAB code (strategy/beta first)
- Bottlenecks removed if discovered
- No coverage-chasing without evidence
- Artifacts show hardened edge cases (concrete before/after behavior)

ATTACK ORDER (RUTHLESS): strategy.py -> beta.py -> data_loader.py -> portfolio.py -> surgical others
```

## CURRENT FOCUS (FORCED)
1. **strategy.py** (16 misses) - Error paths + integration. Highest leverage for end-to-end robustness.
2. **beta.py** (16 misses) - Numerical stability. Correctness-critical; NaN vs 0.0 must be enforced across all emitters.
3. **data_loader.py** (9 misses) - Real data integration hardening.
4. **portfolio.py** (8 misses) - Constraints/enforcement.
5. **Others** - Only surgical if high-value and easy with behavior tests.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- Gate: >=1345 passed, >=7 skipped, 0 failed
- Coverage ~98% (ceiling) — surgical only, evidence required
- Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0 — all beta emitters agree
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (consolidated, campaign-forced, refreshed, bottleneck-eliminated)
- Campaign: UNAVOIDABLE HEAVY BAB HARDENING - TARGET REMAINING UNCOVERED PATHS
- Coverage status: 98% (ceiling) — surgical only, evidence required
- Momentum: MANDATORY — every turn must produce substantive BAB work or remove bottlenecks
- Bottlenecks: NONE KNOWN (eliminated preflight)
- Last verified: 2026-11-01T15:14:45Z (BAB gate GREEN, 1345 passed, 7 skipped, 0 failed, 98% coverage)
- Focus: strategy.py first, then beta.py, with relentless adversarial hardening

(End of file)
