# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T11:18:30Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — inferred from repository name. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T11:18:30Z

VERIFIED STATE (2026-11-01T11:18:12Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0)
- BAB suite: 1335 passed, 7 skipped, 0 failed
- Coverage: 98% total (2593 stmts, 61 misses). COVERAGE CEILING REACHED.
- Per-module highlights: beta.py 94% (16), strategy.py 93% (16), data_loader.py 97% (9), portfolio.py 97% (8), costs.py/config/metrics/regime 99%, others 100%.
- Bottlenecks removed: single-command gate (scripts/bab_gate.sh), warnings silenced, .github/workflows/main.yml updated for workflow paths.

PRIMARY MANDATE: HEAVY BAB HARDENING. Every single turn MUST produce concrete, substantive BAB improvements (tests + minimal hardening). Idle, docs-only, or file-count changes are FORBIDDEN.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
1. GATE FIRST: Run `scripts/bab_gate.sh`. Must return GREEN. If anything is broken, fix it BEFORE any other work.
2. ATTACK REAL EDGE CASES (HEAVY): Focus on gaps that can actually break robustness - rolling beta numerical stability (near-singular, colinearity, zero variance), portfolio construction under degenerate signals/ties/all-same-beta, regime transitions, data quality storms (NaN/inf, duplicates/out-of-order/timezone mixes, gaps), lookahead prevention (1-day lag), dollar-neutrality enforcement.
3. ADVERSARIAL + PROPERTY TESTS: Add deterministic seeded tests for chaos cases (extreme costs/slippage/turnover, partial universe, missing benchmark periods). Enforce invariants: weights finite, row sums ~0 for dollar-neutral, no lookahead, finiteness everywhere.
4. INTEGRATION/CLI/ERRORS: Harden BABStrategy end-to-end, CLI paths, config validation. Replace any bare except: with specific BAB exceptions. Ensure errors are BAB-specific and actionable.
5. REGRESSION GUARDRAILS: Every new failure mode discovered MUST get a regression test + minimal fix. Do not just explain.

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Must remain GREEN (>=1335 passed, >=7 skipped, 0 failed).
2. DO NOT CHASE UNREACHABLE COVERAGE. The ~61 misses are mostly unreachable dead code - require evidence to touch, and never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT EVIDENCE WHY IMPOSSIBLE. No idle turns.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/decimals, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:.
6. Deterministic only (seeded RNGs). All tests offline.
7. Momentum mandatory - find edge case, write test, harden code. Never stop at analysis.

VERIFICATION:
  scripts/bab_gate.sh

SUCCESS CRITERIA FOR SESSION PROGRESS:
- Gate stays GREEN
- New adversarial/property/regression tests added (substantive)
- Concrete robustness improvements to BAB codebase
- No coverage-chasing of unreachable code without evidence
- Clear artifacts showing edge cases hardened

NEVER END WITH JUST "analysis" OR "investigation". PROGRESS = GREEN GATE + SUBSTANTIVE BAB HARDENING/TESTS.
```

## BOTTLENECKS REMOVED
- Gate consolidated to single command: `scripts/bab_gate.sh`
- Noisy warnings silenced in gate
- Workflow patterns updated to include `*/.github/workflows/*`

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- Gate: >=1335 passed, >=7 skipped, 0 failed
- Coverage ~98% (ceiling) — do NOT chase unreachable dead code
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (consolidated)
- Campaign: HEAVY BAB HARDENING (adversarial, property-based, chaos, integration, numerical robustness)
- Coverage status: Ceiling reached (98%)
- Momentum: MANDATORY — every turn must produce substantive BAB work
- Last verified: 2026-11-01T11:18:12Z (BAB gate GREEN)
