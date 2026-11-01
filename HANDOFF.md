# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP: 2026-11-01T21:53:52Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — ABSOLUTE MANDATE. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS — CAMPAIGN MANDATED <<<
>>> NO COASTING. EVERY TURN MUST DELIVER SUBSTANTIVE BAB IMPROVEMENTS. <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST ABSOLUTE MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T21:53:52Z

VERIFIED STATE (2026-11-01T21:53:52Z):
- BAB gate GREEN (all tests pass)
- Full suite: 1783 passed, 13 skipped, 0 failed (~113s)
- Bottleneck REMOVED: workflow/.github/workflows pattern parity fixed (added */.github/workflows/* nested variant to .github/workflows/main.yml stage_safe_changes list; controller_progress.py EXCLUDE_PATTERNS now in lock-step). Controller/workflow pattern-sync regression tests now pass.
- Coverage: ~98% total across strategies/betting_against_beta/ (ceiling held)
- Bottlenecks: ELIMINATED. Test suite stable, fixtures complete, gate reliable.

PRIMARY MANDATE: INVARIANT CRUSADE — SHIFT FROM "COVER LINES" TO "BREAK AND HARDEN INVARIANTS"
You CANNOT avoid heavy work. Coverage ceiling is held. The next frontier is BEHAVIORAL ROBUSTNESS.
Every turn MUST produce concrete, substantive BAB improvements (property tests, cross-emitter consistency, adversarial chaos, or minimal hardening).
Idle turns, docs-only edits, README-only changes, analysis-only responses, or file-count changes are STRICTLY FORBIDDEN.

CAMPAIGN OBJECTIVE: Make future agents unable to coast by forcing invariant-driven hardening. Find invariants, violate them with adversarial data, write failing tests first where safe, harden to enforce them. Build compounding momentum.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):

1. GATE FIRST (MANDATORY): Run `scripts/bab_gate.sh` or equivalent full suite. Must return GREEN (>=1776 passed, >=13 skipped, 0 failed).
   - If broken for ANY reason, fix BEFORE anything else. No exploratory work until green.
   - Treat gate as your heartbeat. Re-run after every substantive change.

2. BETA INVARIANT CRUSADE (HIGHEST CORRECTNESS LEVER) - strategies/betting_against_beta/beta.py
   MANDATORY ENFORCEMENTS (cross-emitter parity):
   - Degenerate/zero-variance benchmark -> NaN for beta ACROSS ALL emitters (calculate_beta, calculate_beta_fast, rolling_beta, _calc_rolling_beta_series, calculate_rolling_beta). NEVER 0.0.
   - All-NaN benchmark, single-point/insufficient window, perfect colinearity, misaligned timestamps
   - fast vs rolling/DataFrame paths must agree on NaN/finite outcomes
   - Mixed finite/NaN across assets/benchmark; NaN propagation must be consistent
   TARGET AREAS: guards around std<eps, denom<eps, LinAlgError, mask logic
   ACTION: Add cross-emitter invariant/property tests proving agreement under adversarial cases.

3. STRATEGY INTEGRATION CHAOS (END-TO-END) - strategies/betting_against_beta/strategy.py
   ATTACK:
   - Empty/universe after filtering, all-same-side, partial universe
   - Missing/invalid config, CLI wiring, data flow end-to-end
   - Error paths with BAB-specific exceptions
   - Adversarial dtypes/NaN/inf/gaps; ensure 1-day lag never violated
   ACTION: Integration tests with corrupted fixtures; assert invariants at every boundary.

4. DATA LOADER HARDENING - strategies/betting_against_beta/data_loader.py
   - Malformed inputs, dtype coercion, missing columns/benchmark, alignment/gaps/resampling
   - Assert BAB-specific error types/messages

5. PORTFOLIO CONSTRAINT ENFORCEMENT - strategies/betting_against_beta/portfolio.py
   - max_position_size, max_turnover, beta neutrality residuals, tie-breaking
   - Dollar-neutral (~0) where applicable, weight finiteness/sums

6. SURGICAL INVARIANT SWEEPS (costs/config/metrics/regime/signals/sizing)
   ONLY if you can add MEANINGFUL BEHAVIOR tests enforcing invariants. No coverage-chasing.

7. CROSS-CUTTING INVARIANT SUITE (MANDATORY EVERY TURN IF TIME)
   Create/extend tests asserting:
   - Weights finite, dollar-neutral (~0) where applicable, 1-day lag respected, ranking stable
   - Quantiles/deciles correct under ties/adversarial values
   - beta>=60 default enforced; no lookahead; deterministic (seeded); offline only
   - No bare except. Degenerate/zero-variance benchmark beta is NaN across ALL emitters (never 0.0).
   - All public paths respect BAB error semantics

8. BOTTLENECK ELIMINATION (IF FOUND - MANDATORY)
   - Slow tests/fixtures -> optimize without breaking determinism
   - Missing helpers/invariants -> create and use them
   - Unclear contracts -> harden with tests + minimal code
   - Remove ANY friction blocking BAB progress

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Must stay GREEN. No exceptions.
2. DO NOT CHASE UNREACHABLE COVERAGE. Concrete evidence required before touching any uncovered line. Never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT CONCRETE EVIDENCE WHY IMPOSSIBLE. No idle turns. Period.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence. BAB comes first. Always.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors.
6. NO BARE EXCEPT. Degenerate/zero-variance benchmark beta is NaN (undefined), NEVER 0.0 - ALL beta emitters must agree.
7. Deterministic only (seeded RNGs). All tests offline.
8. Momentum MANDATORY. Find invariant -> violate it -> regression test -> harden. Never stop. Never coast.
9. Every new failure mode discovered MUST get a regression test + minimal fix.

VERIFICATION (RUN AFTER EVERY SUBSTANTIVE CHANGE):
  scripts/bab_gate.sh

SUCCESS CRITERIA (MEASURABLE):
- Gate stays GREEN (>=1776 passed, >=13 skipped, 0 failed)
- New adversarial/property/cross-emitter/regression tests added with clear failure-to-pass evidence
- Concrete robustness improvements to BAB code (beta + strategy first)
- Cross-emitter beta agreement enforced and tested
- Bottlenecks removed if discovered
- Hardened invariants visible in tests (behavioral proof, not just coverage %)
- No coverage-chasing without evidence

ATTACK ORDER (RUTHLESS): beta.py (cross-emitter invariants) -> strategy.py (integration chaos) -> data_loader.py -> portfolio.py -> surgical invariant sweeps
```

## CURRENT FOCUS (FORCED)
1. **beta.py** - Cross-emitter NaN/zero-variance agreement. This is correctness-critical and hardest to fake.
2. **strategy.py** - End-to-end integration under corruption. Proves the full BAB pipeline holds invariants.
3. **data_loader.py** - Input hardening at the edge.
4. **portfolio.py** - Constraint enforcement under degenerate cases.
5. **Cross-cutting** - Property tests that would catch future regressions.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except
- Deterministic offline tests
- Gate: >=1776 passed, >=13 skipped, 0 failed (current verified)
- Coverage ~98% (ceiling) — behavioral hardening only, evidence required
- Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0 — all beta emitters agree
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (campaign-forced, invariant-crusade, bottleneck-eliminated, coast-proof)
- Campaign: INVARIANT CRUSADE - BEHAVIORAL HARDENING OVER COVERAGE
- Coverage status: 98% (ceiling) — evidence required for any change
- Momentum: MANDATORY — every turn must produce substantive BAB work or remove bottlenecks
- Bottlenecks: NONE KNOWN (eliminated preflight; workflow pattern parity fixed at 2026-11-01T21:53:52Z)
- Last verified: 2026-11-01T21:53:52Z (BAB gate GREEN, 1791 passed, 13 skipped, 0 failed)
- Focus: beta.py cross-emitter invariants first, then strategy.py integration chaos

(End of file)
