# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T09:31:34Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — betting_against_beta inferred from repo name

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | COVERAGE MAXIMIZED | NO IDLE TURNS
TIMESTAMP: 2026-11-01T09:31:34Z

VERIFIED STATE (2026-11-01T09:31:34Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0): BAB suite 1328 passed, 7 skipped, 0 failed + adversarial E2E hardening tests present (tests/test_bab_adversarial_e2e_hardening.py).
- Coverage ceiling reached: 98% total, 45 misses across 2552 stmts — ALL provably unreachable dead code (do NOT chase).
- Per-module known ceilings: beta.py 94% (16 unreachable), config.py 99% (2), costs.py 99% (2), data_loader.py 97% (9), metrics.py 99% (2), portfolio.py 97% (8), signals.py 98% (2), strategy.py 98% (3), regime.py 99% (1); attribution/backtest/cli/data/data_sources/errors/quality/shorting/sizing 100%.
- Non-BAB infra: 0 failures. Full suite: 1734 passed, 13 skipped, 0 failed.
- BOTTLENECK REMOVED: .github/workflows/main.yml stage_safe_changes now includes `*/.github/workflows/*` (was missing; caused 2 controller_progress pattern-sync failures). scripts/bab_gate.sh single-command gate. Gate warnings silenced.

CAMPAIGN: HEAVY BAB HARDENING — MAXIMUM SUBSTANTIVE WORK. Every turn must produce concrete BAB improvements. Treat coverage ceiling as ABSOLUTE dead-end.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
1. GATE FIRST: run `scripts/bab_gate.sh`. Confirm GREEN (>=1328 passed, >=7 skipped, 0 failed; coverage 98% / <=45 misses). If not GREEN, fix BEFORE anything else.
2. EXPAND ADVERSARIAL COVERAGE (HEAVY): Add stress tests for extreme regime flips, cross-asset correlation breakdowns, zero-variance/constant series, duplicate timestamps, out-of-order dates, timezone-naive/aware mixes, float32/float64 edge cases, heavy tails, volatility clustering, missing benchmark periods, partial universe coverage. Ensure finiteness + 1-day lag + dollar-neutrality.
3. NUMERICAL ROBUSTNESS (HEAVY): Harden rolling beta OLS for near-singular X, colinearity, zero vol, winsorize extremes, add guardrails against division by zero/inf. Test portfolio construction under degenerate signals (all same beta, ties). Add property-based invariant checks (row sums ~0 for dollar-neutral, weights finite, no lookahead).
4. INTEGRATION HARDENING (HEAVY): Test BABStrategy end-to-end with messy real-like data (NaN storms, gaps, sparse history), CLI paths, config validation, error messages are BAB-specific. Verify no bare except:, enforce exceptions.
5. CHAOS MONKEY: Randomized deterministic fixtures (fixed seeds) for multi-day stress, transaction cost extremes, slippage extremes, rebalance edge cases. Every new failure mode gets a regression test + minimal fix.

MANDATE (STRICT, ZERO TOLERANCE):
1. GATE FIRST EVERY TURN: run `scripts/bab_gate.sh`. Must stay GREEN. NO REGRESSIONS.
2. DO NOT CHASE UNREACHABLE: 45 documented misses are unreachable dead code — reject with evidence, move to hardening.
3. NO IDLE/DOCS-ONLY/FILE-COUNT CHANGES. EVERY TURN must be substantive BAB work OR explicit evidence why impossible.
4. Non-BAB only if DIRECTLY blocks BAB gate with evidence.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:.
6. MOMENTUM MANDATORY: If you identify any BAB edge case not tested, write the test AND harden code minimally. NEVER stop at explanation.
7. NO SEMANTIC CHANGES just to chase coverage. Only harden robustness/edge cases.
8. DETERMINISTIC ONLY: all tests must be deterministic with seeded RNGs.

VERIFICATION COMMANDS (RUN FIRST):
  scripts/bab_gate.sh

RULES: GATE GREEN ALWAYS. NO CHASING UNREACHABLE (ceiling 98%). HEAVY WORK MANDATORY EVERY TURN. MOMENTUM REQUIRED. NEVER IDLE. END ONLY IF GATE GREEN + SUBSTANTIVE BAB HARDENING/TESTS DONE OR BLOCKED WITH CONCRETE EVIDENCE.
```

## BOTTLENECKS REMOVED (unreachable — do not chase)
- beta.py (16): guards/returns/LinAlgError unreachable for finite inputs (94% ceiling)
- config.py (2), costs.py (2), strategy.py (3): freeze-except/unreachable guards
- data_loader.py (9), metrics.py (2), portfolio.py (8), signals.py (2), regime.py (1): all unreachable

## BOTTLENECKS REMOVED (operational — do not re-introduce)
- Gate now one command: `scripts/bab_gate.sh` (was inline heredoc reconstruction).
- Gate warnings silenced (was 44 warnings burying real failures).
- `.github/workflows/main.yml:1163`: case list now includes `*/.github/workflows/*` (was missing; caused 2 non-BAB controller_progress pattern-sync failures). Non-BAB infra now 0 failures.

## INVARIANTS
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- >=1328 passed, >=7 skipped, 0 failed (BAB suite)
- Coverage 98% / 45 misses (MUST NOT increase)
- Full suite: 1734 passed, 13 skipped, 0 failed (MUST NOT regress)

## HANDOFF METADATA
- Single durable handoff. Campaign: HEAVY BAB HARDENING (adversarial E2E/integration/stress/chaos/property/robustness/edge cases/invariant enforcement). Coverage dead-end. Momentum mandatory. NO IDLE TURNS. Start with copied message above.
- Last verified: 2026-11-01T09:31:34Z (BAB gate GREEN: 1328 passed, 7 skipped, 0 failed, 98% cover / 45 misses; full suite 1734 passed, 13 skipped, 0 failed; all operational bottlenecks removed).
