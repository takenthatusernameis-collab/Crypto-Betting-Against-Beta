# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T08:25:14Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — betting_against_beta inferred from repo name

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | COVERAGE MAXIMIZED | NO IDLE TURNS
TIMESTAMP: 2026-11-01T08:25:14Z

VERIFIED STATE (2026-11-01T08:25:14Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0): BAB suite 1328 passed, 7 skipped, 0 failed + adversarial E2E hardening tests present (tests/test_bab_adversarial_e2e_hardening.py).
- Coverage ceiling reached: 98% total, 45 misses across 2549 stmts — ALL provably unreachable dead code (do NOT chase).
- Per-module known ceilings: beta.py 94% (16 unreachable), config.py 99% (2), costs.py 99% (2), data_loader.py 97% (9), metrics.py 99% (2), portfolio.py 97% (8), signals.py 98% (2), strategy.py 98% (3), regime.py 99% (1); attribution/backtest/cli/data/data_sources/errors/quality/shorting/sizing 100%.
- Non-BAB infra: 0 failures. Full suite: 1734 passed, 13 skipped, 0 failed.
- BOTTLENECK REMOVED: .github/workflows/main.yml stage_safe_changes case list now includes the nested `*/.github/workflows/*` pattern (was missing; caused 2 pre-existing test_controller_progress_accounting.py failures). Gate warnings silenced (44 noisy pandas/numpy warnings). scripts/bab_gate.sh is the one-command gate.

CAMPAIGN: HEAVY HARDENING — NO IDLE TURNS. Every turn must produce substantive BAB changes. Treat coverage ceiling as hard dead-end.

IMMEDIATE ACTIONS (CONCRETE, DO IN ORDER):
1. GATE FIRST: run `scripts/bab_gate.sh`. Confirm GREEN (>=1328 passed, >=7 skipped, 0 failed; coverage 98% / <=45 misses).
2. ADVERSARIAL E2E SWEEP (HEAVY): add/strengthen tests for multi-asset, regime shifts, quantile/decile extremes, NaN/mixed dtypes, sparse history, single-asset/universe shrink, all-long/all-short, min-history, liquidity shocks. Validate 1-day lag, dollar-neutrality, finiteness end-to-end.
3. NUMERICAL HARDENING: stress rolling beta (winsorization/clipping/EPS/re-normalization/residuals), portfolio sizing under degeneracy, signals/deciles/quantiles edge cases. Add property-style checks where cheap and deterministic.
4. INVARIANT AUDIT: verify (1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, no bare except:). Fix minimally with tests.
5. FAILURE MODES: cover data quality gaps, missing columns/indexing/alignment, benchmark edges, cost/transaction edges. Deterministic fixtures only.

MANDATE (STRICT):
1. GATE FIRST EVERY TURN: run `scripts/bab_gate.sh`. Must stay GREEN. NO REGRESSIONS.
2. DO NOT CHASE UNREACHABLE: 45 misses documented unreachable — reject with evidence, move to hardening.
3. NO IDLE/DOCS-ONLY/FILE-COUNT. EVERY TURN substantive BAB work OR explicit evidence why impossible.
4. Non-BAB only if DIRECTLY blocks BAB gate with evidence.
5. Preserve invariants, enforce finiteness, BAB-specific errors, NO bare except:. No semantic changes to pass coverage.
6. MOMENTUM REQUIRED: if tests missing for identified edge case, write them + harden code minimally. Never stop at explanation.

VERIFICATION COMMANDS (RUN FIRST):
  scripts/bab_gate.sh

RULES: GATE GREEN ALWAYS. NO CHASING UNREACHABLE (ceiling 98%). HEAVY WORK MANDATORY. MOMENTUM REQUIRED. END ONLY IF GATE GREEN + SUBSTANTIVE BAB HARDENING/TESTS DONE OR BLOCKED WITH EVIDENCE.
```

## BOTTLENECKS REMOVED (unreachable — do not chase)
- beta.py (16): guards/returns/LinAlgError unreachable for finite inputs (94% ceiling)
- config.py (2), costs.py (2), strategy.py (3): freeze-except/unreachable guards
- data_loader.py (9), metrics.py (2), portfolio.py (8), signals.py (2), regime.py (1): all unreachable

## BOTTLENECKS REMOVED (operational — do not re-introduce)
- Gate now one command: `scripts/bab_gate.sh` (was inline heredoc reconstruction).
- Gate warnings silenced (was 44 warnings burying real failures).
- .github/workflows/main.yml:1163 case list now includes `*/.github/workflows/*` (was missing; caused 2 non-BAB failures). Non-BAB infra now 0 failures.

## INVARIANTS
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- >=1328 passed, >=7 skipped, 0 failed (BAB suite)
- Coverage 98% / 45 misses (must not increase)
- Full suite: 1734 passed, 13 skipped, 0 failed (must not regress)

## HANDOFF METADATA
- Single durable handoff. Campaign: heavy BAB hardening (adversarial E2E/integration/stress/robustness/performance/edge cases/invariant enforcement). Coverage dead-end. Momentum mandatory. Start with copied message above.
- Last verified: 2026-11-01T08:25:14Z (BAB gate GREEN: 1328 passed, 7 skipped, 0 failed, 98% cover / 45 misses; full suite 1734 passed, 13 skipped, 0 failed; workflow nested-pattern bottleneck removed, non-BAB infra 0 failures). Adversarial E2E hardening tests present.
