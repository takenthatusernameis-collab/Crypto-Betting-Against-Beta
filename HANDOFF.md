# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T16:35:40Z

## TIMESTAMP
2026-10-31T16:35:40Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## BOTTLENECKS REMOVED (THIS SESSION)
- Fixed workflow pattern sync: added `*/.github/workflows/*` to `.github/workflows/main.yml` stage_safe_changes case list (line 1163) and to the checkpoint project-changes case (line 1240), so it matches `scripts/controller_progress.py:28` EXCLUDE_PATTERNS. Both `TestStageSafeChangesPatternSync` tests now pass.
- Full suite GREEN again: 1656 passed, 11 skipped, 0 failed.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T16:35:40Z)
- Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): 1130 passed, 5 skipped, 0 failed (GREEN)
- quality.py: 100% (183 stmts, 0 miss) — COMPLETE
- data_loader.py: 97% (296 stmts, 10 miss) — COMPLETE (all 10 misses PROVABLY UNREACHABLE, documented below)
- BAB package coverage map (stmts/miss/cover):
  - data_loader.py 296/10 97%  [44, 192-193, 256, 311-313, 340-342] — provably unreachable (see FOCUS ANALYSIS)
  - quality.py 183/0 100% | __init__.py 4/0 100% | attribution.py 37/0 100% | cli.py 34/0 100% | data.py 15/0 100% | data_sources.py 67/0 100% | errors.py 2/0 100%
  - config.py 199/3 98% [95-96, 113] | signals.py 113/2 98% [37, 75] | strategy.py 198/3 98% [181, 188-189]
  - beta.py 286/14 95% [124, 138, 140-141, 144-145, 166, 178, 181, 355-359] | regime.py 186/12 94% [111, 139-140, 175-177, 181-182, 185, 188, 190, 217]
  - backtest.py 74/8 89% [15, 17, 58-59, 103-108] | portfolio.py 223/38 83% [39-40, 57, 59, 65-66, 87-88, 155-160, 172, 186-201, 203, 210-211, 218, 221, 224, 275]
  - costs.py 150/48 68% | metrics.py 132/43 67% | shorting.py 172/58 66% | sizing.py 163/72 56%
- BAB TOTAL: 2534 stmts, 311 miss, 88%

## DATA_LOADER REMAINING MISSES — PROVABLY UNREACHABLE (EVIDENCE)
- 311-313 (load_returns_from_parquet) and 340-342 (load_returns_from_hdf5): inner `except Exception` converts OSError/ValueError to BABDataError first, then `except BABDataError: raise` re-raises, so the outer `except (OSError, ValueError)` is never reached.
- 256 (validate_returns_dataframe benchmark no-finite): `_drop_all_nan_columns` (line 242) drops every column with no finite values before line 254; an all-non-finite benchmark raises "Benchmark not found" at line 249 instead, so line 256 is never reached.
- 44 (_normalize_index): after line 25-31 the index is guaranteed DatetimeIndex (or BABDataError raised earlier); line 34-41 preserves DatetimeIndex; line 43 guard is always False.
- 192-193 (_coerce_numeric outer except): inner `except Exception` catches all coercion failures and re-raises BABDataError first, so the outer `except (ValueError, TypeError, AttributeError)` is never reached.
=> data_loader.py cannot exceed 97% without changing existing logic (prohibited: minimal changes only). Module is complete; do not spin here.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T16:35:40Z):
- Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): 1130 passed, 5 skipped, 0 failed (GREEN)
- quality.py: 100% COMPLETE
- data_loader.py: 97% COMPLETE — all 10 misses provably unreachable (documented in HANDOFF.md FOCUS ANALYSIS)
- BAB TOTAL: 2534 stmts, 311 miss, 88%

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

TARGETS (NON-NEGOTIABLE):
- BAB TOTAL coverage strictly higher than session start, OR explicit evidence remaining lines are provably unreachable
- tests/test_bab*.py: 100% GREEN. Full suite: 0 failures allowed.
- NO module left red; if gates go red, fix them before any new coverage work.

FOCUS ORDER (STRICT):
1. data_loader.py: COMPLETE at 97% (10 provably-unreachable misses documented). Do not spin — move on.
2. sizing.py (56%, 72 misses) — highest-impact gap; attack next with same rigor.
3. shorting.py (66%, 58 misses) -> metrics.py (67%, 43 misses) -> costs.py (68%, 48 misses) -> portfolio.py (83%) -> backtest.py (89%) -> beta.py (95%) -> regime.py (94%) -> config.py/signals.py/strategy.py (98%).

VERIFICATION METHOD (USE EXACTLY THIS):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob, sys, coverage, pytest
ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0, ROOT)
files = sorted(glob.glob(ROOT + "/tests/test_bab*.py"))
cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"], data_file=None)
cov.start()
rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
cov.stop()
print("="*60)
print("COVERAGE: BAB package")
cov.report(show_missing=True, include=ROOT + "/strategies/betting_against_beta/*.py")
if rc != 0:
    sys.exit(rc)
PYEOF
# Gate 1: focused BAB module tests must stay green
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py
# Gate 2: full suite must be 0 failures
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider 2>&1 | tail -4
```

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF A MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE WITH SAME RIGOR AND HEAVY WORK. NO SPINNING.
- RUN GATES AFTER CHANGES. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.

HEAVY-WORK FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID THIS):
- Each session must end with BAB coverage strictly higher than it started, OR explicit evidence that remaining lines are provably unreachable (documented in this handoff).
- No session may end with gates red. If gates go red, the very next turn fixes them before any new coverage work.
- Write a failing test first (TDD), then the minimal test/logic to make it green against existing correct behavior. Never add assertions-free tests.
- Re-run focused coverage + BAB suite after EVERY batch. If coverage is flat after hitting obvious paths, explicitly call out unreachable vs missed and move to the next module.
- Target lowest-coverage BAB modules first (sizing.py 56%, shorting.py 66%, metrics.py 67%, costs.py 68%).

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage toward 100% with zero regressions. data_loader.py complete at 97% (unreachable misses documented). quality.py complete at 100%. Next focus: sizing.py (56%) then shorting.py, metrics.py, costs.py, portfolio.py, backtest.py, beta.py, regime.py, config.py/signals.py/strategy.py.

## VERIFIED GATES (CURRENT - 2026-10-31T16:35:40Z)
- data_loader.py: 97% (10 misses, all provably unreachable — documented)
- quality.py: 100%
- BAB suite (tests/test_bab*.py): GREEN (1130 passed, 5 skipped)
- Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)

## EXACT NEXT STEPS (CHAINED)
1. **IMMEDIATE**: Confirm gates green (full suite 0 failures, BAB suite green) — DONE this session.
2. **NEXT MODULE**: Run the verification method focused on sizing.py. Write a failing TDD test for an uncovered sizing branch, add minimal logic/test, re-run coverage + gates. Repeat until sizing.py rises, then move down the focus order.
3. **DOCUMENT**: If any sizing.py lines are provably unreachable after focused attempts, document with evidence in this handoff and move to shorting.py.
4. **FINAL GATE**: Before ending session, run BAB suite (must be GREEN) and full suite (0 failures).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required
