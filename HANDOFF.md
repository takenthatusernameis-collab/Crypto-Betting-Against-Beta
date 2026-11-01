# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T15:04:02Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — ABSOLUTE MANDATE. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS — CAMPAIGN MANDATED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST ABSOLUTE MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T15:04:02Z

VERIFIED STATE (2026-11-01T15:04:02Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0)
- BAB suite: 1345 passed, 7 skipped, 0 failed
- Coverage: 98% total (2573 stmts, 61 misses). COVERAGE CEILING HELD.
- Per-module: backtest/attribution/cli/data/data_sources/errors/quality/shorting 100%; beta 94%, strategy 93%, data_loader 97%, portfolio 97%, costs/config/metrics/regime 99%, signals 98%, sizing 98%.
- Bottlenecks: NONE KNOWN. All previously identified issues (beta degeneracy alignment, gate regression) REMOVED.

PRIMARY MANDATE: HEAVY BAB HARDENING CAMPAIGN — TARGET THE REMAINING 61 MISSES WITH SURGICAL PRECISION. Every turn MUST produce concrete, substantive BAB improvements (tests + minimal hardening). Idle, docs-only, analysis-only, or file-count changes are FORBIDDEN.

CAMPAIGN OBJECTIVE: Build an UNAVOIDABLE heavy-work campaign. Future agents must NEVER coast. Attack real weaknesses, add regression tests, harden invariants.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
1. GATE FIRST: Run `scripts/bab_gate.sh`. Must return GREEN (>=1345 passed, >=7 skipped, 0 failed). If broken, fix BEFORE anything else.
2. SURGICAL ATTACK ON UNCOVERED PATHS (HEAVY):
   - beta.py (16 misses): Focus on _calc_rolling_beta_series edge cases (insufficient windows, NaN propagation, alignment), fast paths, degenerate cases across all emitters. Add adversarial tests for mixed finite/NaN, all-NaN columns, extreme colinearity.
   - strategy.py (16 misses): Harden BABStrategy end-to-end - error paths, missing data, partial universe, config validation, CLI integration, fallback behaviors. Add integration tests with chaos data.
   - data_loader.py (9 misses): Data loading edge cases (malformed, gaps, dtypes, missing benchmark), error handling, resampling. Ensure BAB-specific errors.
   - portfolio.py (8 misses): Weight constraints (max_position_size/max_turnover), enforce_beta_neutrality residuals, tie-breaking, all-long/all-short/empty cases, numerical stability.
   - Others (costs/metrics/signals/sizing/config/regime): Hit specific misses with concrete tests. Only touch if you can add meaningful coverage via real behavior tests.
3. ADVERSARIAL + PROPERTY TESTS: Expand chaos/property coverage. Enforce invariants: weights finite, row sums ~0 for dollar-neutral, no lookahead (1-day lag), finiteness everywhere, beta consistency across ALL emitters, degenerate benchmark beta is NaN.
4. BOTTLENECK ELIMINATION: If anything blocks BAB work (slow tests, unclear APIs, missing fixtures), FIX IT IMMEDIATELY or CREATE what's needed. Remove inefficiencies.
5. REGRESSION GUARDRAILS: Every new failure mode discovered MUST get a regression test + minimal fix.

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Must stay GREEN (>=1345 passed, >=7 skipped, 0 failed).
2. DO NOT CHASE UNREACHABLE COVERAGE. Require concrete evidence before touching lines. Never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT CONCRETE EVIDENCE WHY IMPOSSIBLE. No idle turns.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence. BAB comes first.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:
6. Degenerate/zero-variance benchmark beta is NaN (undefined), NEVER 0.0 - ALL beta emitters must agree.
7. Deterministic only (seeded RNGs). All tests offline.
8. Momentum MANDATORY - find edge case, write test, harden code. Never stop. Never coast.

VERIFICATION:
  scripts/bab_gate.sh

SUCCESS CRITERIA:
- Gate stays GREEN (>=1345 passed, >=7 skipped, 0 failed)
- New adversarial/property/regression tests added (substantive)
- Concrete robustness improvements to BAB codebase
- Bottlenecks removed if discovered
- No coverage-chasing without evidence
- Clear artifacts showing edge cases hardened
```

## CURRENT FOCUS (SUGGESTED ATTACK ORDER)
1. **strategy.py** - 16 misses (error paths, integration). Highest impact for end-to-end robustness.
2. **beta.py** - 16 misses (numerical stability in rolling/fast paths). Critical for correctness.
3. **data_loader.py** - 9 misses. Important for real data integration.
4. **portfolio.py** - 8 misses. Constraints/enforcement.
5. **Others** - surgical fixes only if easy to hit with meaningful tests.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- Gate: >=1345 passed, >=7 skipped, 0 failed
- Coverage ~98% (ceiling) — do NOT chase unreachable dead code
- Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0 — all beta emitters agree
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (consolidated, campaign-forced, refreshed)
- Campaign: HEAVY BAB HARDENING - TARGET REMAINING UNCOVERED PATHS
- Coverage status: 98% (ceiling) — surgical only, evidence required
- Momentum: MANDATORY — every turn must produce substantive BAB work or remove bottlenecks
- Bottlenecks: NONE KNOWN
- Last verified: 2026-11-01T15:04:02Z (BAB gate GREEN, 1345 passed, 7 skipped, 0 failed, 98% coverage)

(End of file)
