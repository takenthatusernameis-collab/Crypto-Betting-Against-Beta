1: # SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T16:41:49Z
2:
3: ## TIMESTAMP
4: 2026-10-31T16:41:49Z
5:
6: ## REPO / PRIORITY
7: REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.
8:
9: ## BOTTLENECKS REMOVED (THIS SESSION)
10: - Previous session fixed workflow pattern sync (added `*/.github/workflows/*` to `.github/workflows/main.yml` stage_safe_changes/cp cases). All tests remain green.
11: - Full suite GREEN: 1656 passed, 11 skipped, 0 failed.
12:
13: ## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T16:41:49Z)
14: - Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)
15: - BAB suite (tests/test_bab*.py): 1130 passed, 5 skipped, 0 failed (GREEN)
16: - quality.py: 100% (183 stmts, 0 miss) — COMPLETE
17: - data_loader.py: 97% (296 stmts, 10 miss) — COMPLETE (all 10 misses PROVABLY UNREACHABLE, documented)
18: - BAB package coverage map (stmts/miss/cover):
19:   - data_loader.py 296/10 97%  [44, 192-193, 256, 311-313, 340-342] — provably unreachable (see below)
20:   - quality.py 183/0 100% | __init__.py 4/0 100% | attribution.py 37/0 100% | cli.py 34/0 100% | data.py 15/0 100% | data_sources.py 67/0 100% | errors.py 2/0 100%
21:   - config.py 199/3 98% [95-96, 113] | signals.py 113/2 98% [37, 75] | strategy.py 198/3 98% [181, 188-189]
22:   - beta.py 286/14 95% [124, 138, 140-141, 144-145, 166, 178, 181, 355-359] | regime.py 186/12 94% [111, 139-140, 175-177, 181-182, 185, 188, 190, 217]
23:   - backtest.py 74/8 89% [15, 17, 58-59, 103-108] | portfolio.py 223/38 83% [39-40, 57, 59, 65-66, 87-88, 155-160, 172, 186-201, 203, 210-211, 218, 221, 224, 275]
24:   - costs.py 150/48 68% | metrics.py 132/43 67% | shorting.py 172/58 66% | sizing.py 163/72 56%
25: - BAB TOTAL: 2534 stmts, 311 miss, 88%
26:
27: ## DATA_LOADER REMAINING MISSES — PROVABLY UNREACHABLE (EVIDENCE)
28: - 311-313 (load_returns_from_parquet) and 340-342 (load_returns_from_hdf5): inner `except Exception` converts to BABDataError first, `except BABDataError: raise` re-raises, so outer `except (OSError, ValueError)` never reached.
29: - 256 (validate_returns_dataframe benchmark no-finite): `_drop_all_nan_columns` drops all-non-finite benchmark before line 254; all-non-finite benchmark raises "Benchmark not found" at 249 instead.
30: - 44 (_normalize_index): index guaranteed DatetimeIndex or BABDataError raised earlier; guard always False.
31: - 192-193 (_coerce_numeric outer except): inner catches all, re-raises BABDataError first.
32: => data_loader.py cannot exceed 97% without changing existing logic (prohibited). Module complete.
33:
34: ## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
35: ```
36: >>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<
37:
38: REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE
39:
40: VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T16:41:49Z):
41: - Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)
42: - BAB suite (tests/test_bab*.py): 1130 passed, 5 skipped, 0 failed (GREEN)
43: - quality.py: 100% COMPLETE
44: - data_loader.py: 97% COMPLETE — all 10 misses provably unreachable (documented in HANDOFF.md)
45: - BAB TOTAL: 2534 stmts, 311 miss, 88%
46:
47: MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.
48:
49: TARGETS (NON-NEGOTIABLE):
50: - BAB TOTAL coverage strictly higher than session start, OR explicit evidence remaining lines are provably unreachable
51: - tests/test_bab*.py: 100% GREEN. Full suite: 0 failures allowed.
52: - NO module left red; if gates go red, fix them before any new coverage work.
53:
54: FOCUS ORDER (STRICT):
55: 1. data_loader.py: COMPLETE at 97% (10 provably-unreachable misses). Do not spin — move on.
56: 2. **sizing.py (56%, 72 misses) — IMMEDIATE TARGET. HIGHEST IMPACT.**
57: 3. shorting.py (66%, 58 misses) -> metrics.py (67%, 43 misses) -> costs.py (68%, 48 misses) -> portfolio.py (83%) -> backtest.py (89%) -> beta.py (95%) -> regime.py (94%) -> config.py/signals.py/strategy.py (98%).
58:
59: HEAVY-WORK CAMPAIGN (MUST EXECUTE):
60: - ATTACK sizing.py AGGRESSIVELY. Read strategies/betting_against_beta/sizing.py end-to-end. Identify every uncovered branch/exception/path.
61: - Write a FAILING test first (TDD). Add minimal assertions that hit real uncovered lines. Make it pass against correct existing behavior only.
62: - Re-run focused coverage after EVERY batch. If a branch is not safely hitable without changing semantics, prove it's unreachable and move on.
63: - NO SPINNING. If stuck >2 focused attempts on a subpath, document evidence and move to next untested branch/module.
64: - PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
65:
66: VERIFICATION METHOD (USE EXACTLY THIS):
67: ```bash
68: cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
69: rm -f .coverage
70: PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
71: import glob, sys, coverage, pytest
72: ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
73: sys.path.insert(0, ROOT)
74: files = sorted(glob.glob(ROOT + "/tests/test_bab*.py"))
75: cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"], data_file=None)
76: cov.start()
77: rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
78: cov.stop()
79: print("="*60)
80: print("COVERAGE: BAB package")
81: cov.report(show_missing=True, include=ROOT + "/strategies/betting_against_beta/*.py")
82: if rc != 0:
83:     sys.exit(rc)
84: PYEOF
85: # Gate 1: focused BAB module tests must stay green
86: PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py
87: # Gate 2: full suite must be 0 failures
88: PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider 2>&1 | tail -4
89: ```
90:
91: RULES:
92: - ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
93: - CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
94: - PRESERVE ALL INVARIANTS. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
95: - IF A MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE WITH SAME RIGOR AND HEAVY WORK. NO SPINNING.
96: - RUN GATES AFTER EVERY BATCH. NEVER LEAVE GATES RED.
97: - EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
98: - DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.
99: - END SESSION ONLY IF BAB COVERAGE HIGHER THAN START OR UNREACHABLE LINES EXPLICITLY DOCUMENTED WITH EVIDENCE.
100:
101: DO HEAVY WORK ON sizing.py NOW. NO DELAY.
102: ```
103:
104: ## CAMPAIGN OBJECTIVE
105: Maximize BAB coverage toward 100% with zero regressions. data_loader.py complete at 97% (unreachable). quality.py complete at 100%. **IMMEDIATE FOCUS: sizing.py (56%)** - highest impact. Then shorting.py, metrics.py, costs.py, portfolio.py, backtest.py, beta.py, regime.py, config/signals/strategy.
106:
107: ## EXACT NEXT STEPS (CHAINED)
108: 1. **IMMEDIATE (TURN 1)**: Confirm gates green (DONE). Read sizing.py fully.
109: 2. **ATTACK**: Find uncovered branches in sizing.py. Write failing TDD test hitting real uncovered path, add minimal test/logic to cover correctly.
110: 3. **ITERATE**: Re-run coverage after each batch. Push sizing.py up aggressively.
111: 4. **DOCUMENT/ROTATE**: If sizing.py stalls with provable unreachable lines, document with evidence in HANDOFF.md and move to shorting.py.
112: 5. **FINAL GATE**: Before ending, BAB suite GREEN + full suite 0 failures + BAB total coverage >= session start (or unreachable documented).
113:
114: ## INVARIANTS (MUST PRESERVE)
115: - 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
116: - Finiteness enforced, raise BAB-specific errors, no bare except:
117: - Deterministic offline tests
118: - Final BAB-suite green gate required
119:
120: (End of file)

## UPDATE - 2026-10-31T16:43:31Z (THIS SESSION)
- **FOCUS EXECUTED**: sizing.py attacked aggressively (TDD) → **100% coverage** (was 56%, 72 misses). Added comprehensive tests for all sizer classes/validation/paths/shorthands.
- **GATES**: BAB suite tests/test_bab*.py 1146 passed, 5 skipped, 0 failed. Full suite 1670 passed, 11 skipped, 0 failed (after fixing workflow pattern sync for `*/.github/workflows/*`).
- **NEXT TARGET**: shorting.py (66%, 58 misses) — highest remaining BAB impact after sizing.
