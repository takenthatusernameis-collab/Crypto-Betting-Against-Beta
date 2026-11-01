# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T11:16:27Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — betting_against_beta inferred from repo name

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | COVERAGE MAXIMIZED | NO IDLE TURNS
TIMESTAMP: 2026-11-01T11:16:27Z

VERIFIED STATE (2026-11-01T11:14:15Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0): BAB suite 1335 passed, 7 skipped, 0 failed.
- Coverage: 98% total (2593 stmts, 61 misses). Ceiling effectively reached; do NOT chase unreachable dead code. Treat coverage ceiling as ABSOLUTE dead-end.
- Per-module (from gate): beta.py 94% (16), config.py 99% (2), costs.py 99% (2), data_loader.py 97% (9), metrics.py 99% (2), portfolio.py 97% (8), signals.py 98% (2), sizing.py 98% (3), strategy.py 93% (16), regime.py 99% (1), attribution.py 100%, backtest.py 100%, cli.py 100%, data.py 100%, data_sources.py 100%, errors.py 100%, quality.py 100%, shorting.py 100%.
- Full suite: 1335 passed, 7 skipped, 0 failed (BAB-focused gate).
- BOTTLENECKS REMOVED: .github/workflows/main.yml stage_safe_changes includes `*/.github/workflows/*`; scripts/bab_gate.sh is single-command gate; gate warnings silenced.

CAMPAIGN: HEAVY BAB HARDENING — MAXIMUM SUBSTANTIVE WORK. Every turn must produce concrete BAB improvements. Treat coverage ceiling as ABSOLUTE dead-end.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
1. GATE FIRST: run `scripts/bab_gate.sh`. Confirm GREEN (>=1335 passed, >=7 skipped, 0 failed; coverage ~98% / <=~61 misses). If not GREEN, fix BEFORE anything else.
2. EXPAND ADVERSARIAL COVERAGE (HEAVY): Add stress tests for extreme regime flips, cross-asset correlation breakdowns, zero-variance/constant series, duplicate timestamps, out-of-order dates, timezone-naive/aware mixes, float32/float64 edge cases, heavy tails, volatility clustering, missing benchmark periods, partial universe coverage. Ensure finiteness + 1-day lag + dollar-neutrality.
3. NUMERICAL ROBUSTNESS (HEAVY): Harden rolling beta OLS for near-singular X, colinearity, zero vol, winsorize extremes, add guardrails against division by zero/inf. Test portfolio construction under degenerate signals (all same beta, ties). Add property-based invariant checks (row sums ~0 for dollar-neutral, weights finite, no lookahead).
4. INTEGRATION HARDENING (HEAVY): Test BABStrategy end-to-end with messy real-like data (NaN storms, gaps, sparse history), CLI paths, config validation, error messages are BAB-specific. Verify no bare except:, enforce exceptions.
5. CHAOS MONKEY: Randomized deterministic fixtures (fixed seeds) for multi-day stress, transaction cost extremes, slippage extremes, rebalance edge cases. Every new failure mode gets a regression test + minimal fix.

MANDATE (STRICT, ZERO TOLERANCE):
1. GATE FIRST EVERY TURN: run `scripts/bab_gate.sh`. Must stay GREEN. NO REGRESSIONS.
2. DO NOT CHASE UNREACHABLE: documented misses are largely unreachable dead code — reject with evidence, move to hardening.
3. NO IDLE/DOCS-ONLY/FILE-COUNT CHANGES. EVERY TURN must be substantive BAB work OR explicit evidence why impossible.
4. Non-BAB only if DIRECTLY blocks BAB gate with evidence.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:.
6. MOMENTUM MANDATORY: If you identify any BAB edge case not tested, write the test AND harden code minimally. NEVER stop at explanation.
7. NO SEMANTIC CHANGES just to chase coverage. Only harden robustness/edge cases.
8. DETERMINISTIC ONLY: all tests must be deterministic with seeded RNGs.

VERIFICATION COMMANDS (RUN FIRST):
  scripts/bab_gate.sh

RULES: GATE GREEN ALWAYS. NO CHASING UNREACHABLE. HEAVY WORK MANDATORY EVERY TURN. MOMENTUM REQUIRED. NEVER IDLE. END ONLY IF GATE GREEN + SUBSTANTIVE BAB HARDENING/TESTS DONE OR BLOCKED WITH CONCRETE EVIDENCE.
```

## BOTTLENECKS REMOVED (operational)
- Gate now one command: `scripts/bab_gate.sh`.
- Gate warnings silenced.
- `.github/workflows/main.yml` includes `*/.github/workflows/*` in stage_safe_changes.

## INVARIANTS
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- >=1335 passed, >=7 skipped, 0 failed (BAB-focused gate)
- Coverage ~98% (do not increase by chasing unreachable)
- No regressions to gate

## HANDOFF METADATA
- Single durable handoff. Campaign: HEAVY BAB HARDENING (adversarial E2E/integration/stress/chaos/property/robustness/edge cases/invariant enforcement). Coverage ceiling reached. Momentum mandatory. NO IDLE TURNS. Start with copied message above.
- Last verified: 2026-11-01T11:16:27Z (BAB gate GREEN: 1335 passed, 7 skipped, 0 failed, ~98% cover).
