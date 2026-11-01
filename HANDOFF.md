# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T13:18:02Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — inferred from repository name. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
TIMESTAMP: 2026-11-01T13:18:02Z

VERIFIED STATE (2026-11-01T13:18:02Z):
- BAB gate GREEN (scripts/bab_gate.sh exit 0)
- BAB suite: 1338 passed, 7 skipped, 0 failed
- Coverage: 98% total (2593 stmts, 61 misses). COVERAGE CEILING REACHED.
- Per-module: backtest/attribution/cli/data/data_sources/errors/quality/shorting 100%; beta 94%, strategy 93%, data_loader 97%, portfolio 97%, costs/config/metrics/regime 99%, signals 98%, sizing 98%.
- Bottlenecks removed: .gitignore added (2026-11-01T12:13:00Z) — untracked __pycache__ noise now suppressed; tracked coverage artifacts already removed from git+fs; single-command gate (scripts/bab_gate.sh) intact; warnings silenced.
- Bottleneck removed this session (2026-11-01T13:18:00Z): gate was RED on entry — `calculate_beta_fast("abc","def")` returned `0.0` instead of NaN (beta.py:155), breaking `test_calculate_beta_fast_outer_typeerror`. Fixed `beta.py:155` to return `np.nan`, and updated 3 stale `== 0.0` assertions in `tests/test_bab_beta_coverage_extra.py:72`, `tests/test_bab_beta_extra_coverage.py:77`, `tests/test_bab_beta_fill_p0.py:76` to `np.isnan(...)`. Gate re-verified GREEN: 1338 passed, 7 skipped, 0 failed.

PRIMARY MANDATE: HEAVY BAB HARDENING. Every single turn MUST produce concrete, substantive BAB improvements (tests + minimal hardening). Idle, docs-only, or file-count changes are FORBIDDEN.

IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
1. GATE FIRST: Run `scripts/bab_gate.sh`. Must return GREEN (>=1338 passed, >=7 skipped, 0 failed). If anything is broken, fix it BEFORE any other work.
2. ATTACK REAL EDGE CASES (HEAVY): Focus on gaps that can actually break robustness:
   - Rolling beta numerical stability: near-singular / colinear windows, zero-variance benchmark (beta.py:calculate_beta_fast returns 0.0 for degenerate benchmark while calculate_beta returns np.nan — inconsistency to resolve), all-NaN columns, insufficient observations (<60).
   - Portfolio construction under degenerate signals/ties/all-same-beta, single-asset rows, max_position_size/max_turnover enforcement paths, enforce_beta_neutrality residual drift (portfolio.py:164-177).
   - Data quality storms: NaN/inf, duplicates, out-of-order, timezone mixes, gaps, empty columns, benchmark without finite values (data_loader.py).
   - Lookahead prevention (1-day lag in backtest.py/run_backtest), dollar-neutrality enforcement (portfolio.py:151-179), quantile/decile rank determinism (signals.py argsort stable sort).
3. ADVERSARIAL + PROPERTY TESTS: Add deterministic seeded tests for chaos cases (extreme costs/slippage/turnover, partial universe, missing benchmark periods, colinear assets). Enforce invariants: weights finite, row sums ~0 for dollar-neutral, no lookahead, finiteness everywhere.
4. INTEGRATION/CLI/ERRORS: Harden BABStrategy end-to-end, CLI paths, config validation. Replace broad except: with specific BAB exceptions. Ensure errors are BAB-specific and actionable.
5. REGRESSION GUARDRAILS: Every new failure mode discovered MUST get a regression test + minimal fix. Do not just explain.

NON-NEGOTIABLE RULES:
1. GATE FIRST EVERY TURN. Must remain GREEN (>=1338 passed, >=7 skipped, 0 failed).
2. DO NOT CHASE UNREACHABLE COVERAGE. The ~61 misses are mostly unreachable dead code - require evidence to touch, and never change semantics just to hit lines.
3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT EVIDENCE WHY IMPOSSIBLE. No idle turns.
4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence.
5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:.
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

## BOTTLENECKS REMOVED (this session)
- **Beta degeneracy consistency (2026-11-01T12:21:00Z).** `calculate_beta_fast` returned `0.0` for a zero-variance/degenerate benchmark while `calculate_beta`, `metrics.strategy_beta`, and the rolling path all returned `NaN`. A synthetic `0.0` is a real (low) beta estimate that the ranking treats as a valid signal, so degenerate windows silently corrupted long/short selection. All four emitters now return `NaN` for undefined beta: `beta.py:170-173` (`calculate_beta_fast`), `beta.py:128-130` (`calculate_beta`, already consistent), `beta.py:301-304` (`_finalize_betas` rolling fast path), `beta.py:243-246` (`_calc_rolling_beta_series` rolling fallback). Regression tests added in `tests/test_bab_beta_alignment_paths.py` (`test_calculate_beta_and_fast_agree_on_degenerate_benchmark`, `test_calculate_rolling_beta_degenerate_benchmark_is_nan`, `test_calculate_rolling_beta_and_fast_agree_on_degenerate_window`); 9 stale `== 0.0` assertions across 7 test files updated to `np.isnan(...)`.
- **Gate regression removed (2026-11-01T13:18:00Z).** Gate was RED on entry — `calculate_beta_fast` returned `0.0` on outer conversion errors (`beta.py:155`, `except (TypeError, ValueError, AttributeError): return 0.0`), breaking `test_calculate_beta_fast_outer_typeerror`. Fixed `beta.py:155` to return `np.nan` (undefined beta is NaN, never a synthetic 0.0). Also removed 3 missed stale `== 0.0` assertions: `tests/test_bab_beta_coverage_extra.py:72`, `tests/test_bab_beta_extra_coverage.py:77`, `tests/test_bab_beta_fill_p0.py:76` → `np.isnan(...)`. Gate re-verified GREEN: 1338 passed, 7 skipped, 0 failed.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- Gate: >=1338 passed, >=7 skipped, 0 failed
- Coverage ~98% (ceiling) — do NOT chase unreachable dead code
- **Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0** — all beta emitters agree
- No regressions

## HANDOFF METADATA
- Type: Single durable handoff (consolidated)
- Campaign: HEAVY BAB HARDENING (adversarial, property-based, chaos, integration, numerical robustness)
- Coverage status: Ceiling reached (98%)
- Momentum: MANDATORY — every turn must produce substantive BAB work
- Last verified: 2026-11-01T13:18:00Z (BAB gate GREEN, 1338 passed, 7 skipped, 0 failed, 98% coverage)

(End of file)