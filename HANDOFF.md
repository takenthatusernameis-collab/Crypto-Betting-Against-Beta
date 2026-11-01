# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP: 2026-11-01T23:55:44Z**
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — ABSOLUTE MANDATE. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.
**STATUS:** GATE-VERIFIED (per prior state). RE-VERIFY ON START. BOTTLENECKS: NONE IDENTIFIED. COASTING: FORBIDDEN.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS — CAMPAIGN MANDATED <<<
>>> NO COASTING. EVERY TURN MUST DELIVER SUBSTANTIVE BAB IMPROVEMENTS. <<<
>>> BAB-FIRST ABSOLUTE MANDATE. ZERO TOLERANCE FOR DOCS-ONLY/ANALYSIS-ONLY TURNS. <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T23:55:44Z

CONTEXT: Betting Against Beta (BAB) strategy in crypto. Coverage is near ceiling (~98%). The frontier is BEHAVIORAL ROBUSTNESS under adversarial/corrupted inputs. You cannot avoid heavy work.

VERIFICATION ON START (MANDATORY):
- Run `scripts/bab_gate.sh` FIRST. Must be GREEN (>=1792 passed, >=13 skipped, 0 failed).
- If gate is broken for ANY reason -> fix before ANY exploratory work. Treat as heartbeat and re-run after substantive changes.

PRIMARY CAMPAIGN: INVARIANT CRUSADE — BREAK IT TO HARDEN IT
Find invariants. Violate them with adversarial data. Write a failing test first where safe. Harden minimally to enforce. Repeat.

ATTACK ORDER (RUTHLESS, NO DEVIATION):
1. strategies/betting_against_beta/beta.py (CROSS-EMITTER INVARIANTS - HIGHEST LEVER)
   - Degenerate/zero-variance benchmark -> NaN for beta ACROSS ALL emitters (calculate_beta, calculate_beta_fast, rolling_beta, _calc_rolling_beta_series, calculate_rolling_beta). NEVER 0.0.
   - All-NaN benchmark, single-point/insufficient window, perfect colinearity, misaligned timestamps, mixed finite/NaN
   - fast vs rolling/DataFrame paths MUST agree on NaN/finite outcomes
   - Guards: std<eps, denom<eps, LinAlgError, mask logic. No bare except.
   ACTION: Add cross-emitter invariant/property tests under adversarial cases.

2. strategies/betting_against_beta/strategy.py (END-TO-END INTEGRATION CHAOS)
   - Empty/universe after filtering, all-same-side, partial universe, missing/invalid config, CLI wiring
   - Adversarial dtypes/NaN/inf/gaps; assert 1-day lag NEVER violated
   - Error paths with BAB-specific exceptions; integration tests with corrupted fixtures
   ACTION: Prove pipeline holds invariants at every boundary.

3. strategies/betting_against_beta/data_loader.py (INPUT HARDENING)
   - Malformed inputs, dtype coercion, missing columns/benchmark, alignment/gaps/resampling
   - Assert BAB-specific error types/messages

4. strategies/betting_against_beta/portfolio.py (CONSTRAINT ENFORCEMENT)
   - max_position_size, max_turnover, beta neutrality residuals, tie-breaking
   - Dollar-neutral (~0) where applicable, weight finiteness/sums

5. SURGICAL SWEEPS (costs/config/metrics/regime/signals/sizing)
   ONLY if you can add MEANINGFUL BEHAVIOR tests enforcing invariants. Evidence required. No coverage-chasing.

6. CROSS-CUTTING INVARIANT SUITE (EVERY TURN IF TIME)
   Enforce: weights finite, dollar-neutral (~0) where applicable, 1-day lag respected, ranking stable
   Quantiles/deciles correct under ties/adversarial values; beta>=60 default enforced
   No lookahead; deterministic (seeded); offline only; no bare except
   Degenerate/zero-variance benchmark beta is NaN across ALL emitters (never 0.0)
   All public paths respect BAB error semantics

BOTTLENECK ELIMINATION (MANDATORY IF FOUND):
- Slow tests/fixtures -> optimize without breaking determinism
- Missing helpers/invariants -> create and use them
- Unclear contracts -> harden with tests + minimal code
- Workflow/CI pattern sync issues -> fix in lock-step (scripts/workflows) if they block gate
- ANY friction blocking BAB progress -> remove it

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Stay GREEN.
2. DO NOT CHASE UNREACHABLE COVERAGE. Concrete evidence required before touching any uncovered line. Never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT CONCRETE EVIDENCE WHY IMPOSSIBLE. No idle turns.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence. BAB comes first.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors.
6. NO BARE EXCEPT. Degenerate/zero-variance benchmark beta is NaN (undefined), NEVER 0.0 — ALL beta emitters must agree.
7. Deterministic only (seeded RNGs). All tests offline.
8. Momentum MANDATORY. Find invariant -> violate it -> regression test -> harden. Never stop.
9. Every new failure mode discovered MUST get a regression test + minimal fix.

VERIFICATION AFTER EVERY SUBSTANTIVE CHANGE:
  scripts/bab_gate.sh

SUCCESS CRITERIA:
- Gate stays GREEN (>=1792 passed, >=13 skipped, 0 failed)
- New adversarial/property/cross-emitter/regression tests added with clear failure-to-pass evidence
- Concrete robustness improvements to BAB code (beta + strategy first)
- Cross-emitter beta agreement enforced and tested
- Bottlenecks removed if discovered
- Hardened invariants visible in tests (behavioral proof)
- No coverage-chasing without evidence
```

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except
- Deterministic offline tests
- Gate target: >=1792 passed, >=13 skipped, 0 failed
- Coverage ~98% (ceiling) — behavioral hardening only, evidence required
- Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0 — all beta emitters agree
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (campaign-forced, invariant-crusade, bottleneck-eliminated, coast-proof)
- Campaign: INVARIANT CRUSADE - BEHAVIORAL HARDENING OVER COVERAGE
- Coverage status: 98% (ceiling) — evidence required for any change
- Momentum: MANDATORY — every turn must produce substantive BAB work or remove bottlenecks
- Bottlenecks: NONE KNOWN (workflow pattern parity previously fixed; verify on start)
- Last verified: 2026-11-01T23:09:14Z (prior) | Refreshed: 2026-11-01T23:55:44Z
- Focus: beta.py cross-emitter invariants first, then strategy.py integration chaos

(End of file)
