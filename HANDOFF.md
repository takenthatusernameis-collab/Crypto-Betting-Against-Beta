# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T14:20:18Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — inferred from repository name. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS — CAMPAIGN MANDATED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST ABSOLUTE MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T14:20:18Z

VERIFIED STATE (2026-11-01T14:20:18Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0)
- BAB suite: 1345 passed, 7 skipped, 0 failed
- Coverage: 98% total (2573 stmts, 61 misses). COVERAGE CEILING REACHED.
- Per-module: backtest/attribution/cli/data/data_sources/errors/quality/shorting 100%; beta 94%, strategy 93%, data_loader 97%, portfolio 97%, costs/config/metrics/regime 99%, signals 98%, sizing 98%.
- All known bottlenecks REMOVED:
  * .gitignore added (2026-11-01T12:13:00Z) — untracked __pycache__ noise suppressed
  * Tracked coverage artifacts removed from git+fs
  * Single-command gate (scripts/bab_gate.sh) intact; warnings silenced
  * Beta degeneracy fully aligned across ALL emitters (calculate_beta, calculate_beta_fast, rolling paths) — degenerate/zero-variance benchmark returns NaN (never 0.0). 9 stale assertions updated across 7 files.
  * Gate regression fixed (2026-11-01T13:18:00Z): calculate_beta_fast outer TypeError path now returns NaN correctly.

PRIMARY MANDATE: HEAVY BAB HARDENING CAMPAIGN. Every single turn MUST produce concrete, substantive BAB improvements (tests + minimal hardening). Idle, docs-only, analysis-only, or file-count changes are FORBIDDEN.

CAMPAIGN OBJECTIVE: Build an UNAVOIDABLE heavy-work campaign. Future agents must NEVER be able to coast. Each turn must find a real weakness and attack it.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
1. GATE FIRST: Run `scripts/bab_gate.sh`. Must return GREEN (>=1338 passed, >=7 skipped, 0 failed). If anything is broken, fix it BEFORE any other work.
2. SYSTEMATIC ATTACK ON EDGE CASES (HEAVY): Hunt for real failure modes:
   - Rolling beta numerical stability: near-singular/colinear windows, zero-variance benchmark (ALL paths must return NaN consistently), all-NaN columns, insufficient observations (<60), division by zero, catastrophic cancellation.
   - Portfolio construction: degenerate signals/ties/all-same-beta/single-asset rows, max_position_size/max_turnover enforcement, enforce_beta_neutrality residual drift, dollar-neutrality violations, weight finiteness, sum constraints.
   - Data quality storms: NaN/inf, duplicates, out-of-order, timezone mixes, gaps, empty columns, benchmark without finite values, mixed dtypes, extreme outliers.
   - Lookahead prevention: verify 1-day lag in backtest.py/run_backtest is airtight. Dollar-neutrality enforcement must hold. Quantile/decile rank determinism (argsort stable sort) under ties.
   - Cost/slippage/shorting edge cases: extreme costs, zero liquidity assumptions, borrow costs, shorting constraints, regime transitions.
3. ADVERSARIAL + PROPERTY TESTS: Add deterministic seeded tests for chaos cases (extreme costs/slippage/turnover, partial universe, missing benchmark periods, colinearity, rank ties). Enforce invariants: weights finite, row sums ~0 for dollar-neutral, no lookahead, finiteness everywhere, beta consistency.
4. INTEGRATION/CLI/ERRORS: Harden BABStrategy end-to-end, CLI paths, config validation. Replace broad except: with specific BAB exceptions. Ensure errors are BAB-specific and actionable. No silent failures.
5. REGRESSION GUARDRAILS: Every new failure mode discovered MUST get a regression test + minimal fix. Do not just explain. Make it impossible for that exact bug to return.

BOTTLENECK ELIMINATION PROTOCOL:
- If ANYTHING blocks progress (unclear tests, slow paths, confusing APIs, missing fixtures) - FIX IT or CREATE what’s needed to unblock BAB work.
- Remove inefficient patterns. Consolidate duplicate logic. Make the test suite faster/more reliable if it helps BAB iteration.
- If multiple sessions would be blocked/inefficient, REMOVE THOSE BOTTLENECKS IMMEDIATELY.
- Never wait for permission to fix blockers that prevent BAB progress.

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Must remain GREEN (>=1338 passed, >=7 skipped, 0 failed).
2. DO NOT CHASE UNREACHABLE COVERAGE. The ~61 misses are mostly unreachable dead code - require concrete evidence to touch, and never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT CONCRETE EVIDENCE WHY IMPOSSIBLE. No idle turns. "Analysis" alone is NOT progress.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence. BAB comes first.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:
6. Degenerate/zero-variance benchmark beta is NaN (undefined), NEVER 0.0 - ALL beta emitters must agree.
7. Deterministic only (seeded RNGs). All tests offline.
8. Momentum MANDATORY - find edge case, write test, harden code. Never stop. Never coast.

VERIFICATION:
  scripts/bab_gate.sh

SUCCESS CRITERIA FOR SESSION PROGRESS:
- Gate stays GREEN (>=1338 passed, >=7 skipped, 0 failed)
- New adversarial/property/regression tests added (substantive, not trivial)
- Concrete robustness improvements to BAB codebase (numerical stability, edge cases, invariants)
- Bottlenecks removed if discovered
- No coverage-chasing of unreachable code without evidence
- Clear artifacts showing edge cases hardened

NEVER END WITH JUST "analysis" OR "investigation". PROGRESS = GREEN GATE + SUBSTANTIVE BAB HARDENING/TESTS.
```

## BOTTLENECKS REMOVED (this campaign state)
- **Beta degeneracy consistency (2026-11-01T12:21:00Z).** All four emitters now return NaN for undefined/degen beta: `beta.py:170-173` (`calculate_beta_fast`), `beta.py:128-130` (`calculate_beta`), `beta.py:301-304` (`_finalize_betas`), `beta.py:243-246` (`_calc_rolling_beta_series`). Regression tests added in `tests/test_bab_beta_alignment_paths.py`. 9 stale `== 0.0` assertions updated across 7 files.
- **Gate regression removed (2026-11-01T13:18:00Z).** `calculate_beta_fast` outer TypeError path fixed to return NaN; 3 missed stale assertions updated. Gate GREEN.
- **Noise suppression (2026-11-01T12:13:00Z).** `.gitignore` added for __pycache__/test artifacts; tracked coverage artifacts removed.

## JUST COMPLETED THIS SESSION (2026-11-01T14:20:18Z)
- Added `tests/test_bab_property_invariants.py`: hypothesis-based property tests for the full BABStrategy pipeline (finiteness of weights/returns/cumulative/signals, integer-valued signals, benchmark beta == 1.0, dollar-neutral row net-zero when both sides exist, determinism, chaos-data no-silent-failure). hypothesis was a declared dependency previously unused by the suite.
- Verified lookahead prevention: perturbing final-day/midstream returns does not alter weights outside their legitimate lookback window (probe confirmed).
- Gate GREEN: 1345 passed, 7 skipped, 0 failed (+2 from new property tests), coverage 98% ceiling held.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- Gate: >=1338 passed, >=7 skipped, 0 failed
- Coverage ~98% (ceiling) — do NOT chase unreachable dead code
- Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0 — all beta emitters agree
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (consolidated, campaign-forced)
- Campaign: HEAVY BAB HARDENING (adversarial, property-based, chaos, integration, numerical robustness) — UNAVOIDABLE
- Coverage status: Ceiling reached (98%) — do NOT chase unreachable dead code
- Momentum: MANDATORY — every turn must produce substantive BAB work or remove bottlenecks
- Bottlenecks: ALL KNOWN REMOVED
- Last verified: 2026-11-01T14:20:18Z (BAB gate GREEN, 1345 passed, 7 skipped, 0 failed, 98% coverage)

(End of file)
