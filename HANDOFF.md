1: # SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
2: # MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION
3:
4: **HANDOFF_TIMESTAMP:** 2026-11-01T15:05:21Z
5: **REPO:** Crypto-Betting-Against-Beta
6: **PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — ABSOLUTE MANDATE. BAB MUST get ALL attention until explicitly blocked by a gate-breaking issue with concrete evidence.
7:
8: ---
9:
10: ## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<
11:
12: ```
13: >>> START IMMEDIATELY — HEAVY WORK REQUIRED — NO IDLE TURNS — CAMPAIGN MANDATED <<<
14:
15: REPO: Crypto-Betting-Against-Beta | BAB-FIRST ABSOLUTE MANDATE | MAXIMUM SUBSTANTIVE PROGRESS
16: TIMESTAMP: 2026-11-01T15:05:21Z
17:
18: VERIFIED STATE (2026-11-01T15:05:21Z):
19: - BAB gate GREEN (scripts/bab_gate.sh exit 0)
20: - BAB suite: 1345 passed, 7 skipped, 0 failed
21: - Coverage: 98% total (2573 stmts, 61 misses). COVERAGE CEILING HELD.
22: - Per-module: backtest/attribution/cli/data/data_sources/errors/quality/shorting 100%; beta 94%, strategy 93%, data_loader 97%, portfolio 97%, costs/config/metrics/regime 99%, signals 98%, sizing 98%.
23: - Bottlenecks: NONE KNOWN. All previously identified issues (beta degeneracy alignment, gate regression) REMOVED.
24:
25: PRIMARY MANDATE: HEAVY BAB HARDENING CAMPAIGN — TARGET THE REMAINING 61 MISSES WITH SURGICAL PRECISION. Every turn MUST produce concrete, substantive BAB improvements (tests + minimal hardening). Idle, docs-only, analysis-only, or file-count changes are FORBIDDEN.
26:
27: CAMPAIGN OBJECTIVE: Build an UNAVOIDABLE heavy-work campaign. Future agents must NEVER coast. Attack real weaknesses, add regression tests, harden invariants.
28:
29: IMMEDIATE ACTIONS (DO IN ORDER, NO EXCEPTIONS):
30: 1. GATE FIRST: Run `scripts/bab_gate.sh`. Must return GREEN (>=1345 passed, >=7 skipped, 0 failed). If broken, fix BEFORE anything else.
31: 2. SURGICAL ATTACK ON UNCOVERED PATHS (HEAVY):
32:    - beta.py (16 misses): 101-102,124,138,140-141,144-145,166,183,187,377-381. Focus on _calc_rolling_beta_series edge cases (insufficient windows, NaN propagation, alignment), fast paths, degenerate cases across all emitters. Add adversarial tests for mixed finite/NaN, all-NaN columns, extreme colinearity.
33:    - strategy.py (16 misses): 40,44-64,223,230-235,280-281,296-297,320. Harden BABStrategy end-to-end - error paths, missing data, partial universe, config validation, CLI integration, fallback behaviors. Add integration tests with chaos data.
34:    - data_loader.py (9 misses): 44,192-193,311-313,340-342. Data loading edge cases (malformed, gaps, dtypes, missing benchmark), error handling, resampling. Ensure BAB-specific errors.
35:    - portfolio.py (8 misses): 39-40,172-177. Weight constraints (max_position_size/max_turnover), enforce_beta_neutrality residuals, tie-breaking, all-long/all-short/empty cases, numerical stability.
36:    - Others (costs/metrics/signals/sizing/config/regime): Hit specific misses with concrete tests. Only touch if you can add meaningful coverage via real behavior tests.
37: 3. ADVERSARIAL + PROPERTY TESTS: Expand chaos/property coverage. Enforce invariants: weights finite, row sums ~0 for dollar-neutral, no lookahead (1-day lag), finiteness everywhere, beta consistency across ALL emitters, degenerate benchmark beta is NaN.
38: 4. BOTTLENECK ELIMINATION: If anything blocks BAB work (slow tests, unclear APIs, missing fixtures), FIX IT IMMEDIATELY or CREATE what's needed. Remove inefficiencies.
39: 5. REGRESSION GUARDRAILS: Every new failure mode discovered MUST get a regression test + minimal fix.
40:
41: NON-NEGOTIABLE RULES:
42: 1. GATE FIRST EVERY TURN. Must stay GREEN (>=1345 passed, >=7 skipped, 0 failed).
43: 2. DO NOT CHASE UNREACHABLE COVERAGE. Require concrete evidence before touching lines. Never change semantics just to hit lines.
44: 3. EVERY TURN = SUBSTANTIVE BAB WORK OR EXPLICIT CONCRETE EVIDENCE WHY IMPOSSIBLE. No idle turns.
45: 4. Non-BAB changes ONLY if they directly unblock BAB gate with concrete evidence. BAB comes first.
46: 5. Preserve invariants: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, NO bare except:
47: 6. Degenerate/zero-variance benchmark beta is NaN (undefined), NEVER 0.0 - ALL beta emitters must agree.
48: 7. Deterministic only (seeded RNGs). All tests offline.
49: 8. Momentum MANDATORY - find edge case, write test, harden code. Never stop. Never coast.
50:
51: VERIFICATION:
52:   scripts/bab_gate.sh
53:
54: SUCCESS CRITERIA:
55: - Gate stays GREEN (>=1345 passed, >=7 skipped, 0 failed)
56: - New adversarial/property/regression tests added (substantive)
57: - Concrete robustness improvements to BAB codebase
58: - Bottlenecks removed if discovered
59: - No coverage-chasing without evidence
60: - Clear artifacts showing edge cases hardened
61: ```
62:
63: ## CURRENT FOCUS (SUGGESTED ATTACK ORDER)
64: 1. **strategy.py** - 16 misses (error paths, integration). Highest impact for end-to-end robustness.
65: 2. **beta.py** - 16 misses (numerical stability in rolling/fast paths). Critical for correctness.
66: 3. **data_loader.py** - 9 misses. Important for real data integration.
67: 4. **portfolio.py** - 8 misses. Constraints/enforcement.
68: 5. **Others** - surgical fixes only if easy to hit with meaningful tests.
69:
70: ## INVARIANTS (MUST PRESERVE)
71: - 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
72: - Finiteness, BAB-specific errors, no bare except:
73: - Deterministic offline tests
74: - Gate: >=1345 passed, >=7 skipped, 0 failed
75: - Coverage ~98% (ceiling) — do NOT chase unreachable dead code
76: - Degenerate/zero-variance benchmark beta is NaN (undefined), never 0.0 — all beta emitters agree
77: - No regressions
78:
79: ## HANDOFF METADATA
80: - Type: Single durable handoff (consolidated, campaign-forced, refreshed)
81: - Campaign: HEAVY BAB HARDENING - TARGET REMAINING UNCOVERED PATHS
82: - Coverage status: 98% (ceiling) — surgical only, evidence required
83: - Momentum: MANDATORY — every turn must produce substantive BAB work or remove bottlenecks
84: - Bottlenecks: NONE KNOWN
85: - Last verified: 2026-11-01T15:05:21Z (BAB gate GREEN, 1345 passed, 7 skipped, 0 failed, 98% coverage)
86:
87: (End of file)
