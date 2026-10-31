# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T11:48:27Z

## TIMESTAMP
2026-10-31T11:48:27Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T11:48:27Z):
- data_loader.py: 95% (296 stmts, 14 miss) — PRIORITY #1 (>=95 achieved, push to >=97)
- quality.py: 89% (183 stmts, 21 miss) — PRIORITY #2 (push to >=93)
- beta.py: ~95% (already strong)
- BAB suite (tests/test_bab*.py): 1109 passed, 5 skipped, GREEN
- Full suite: 1582 passed, 11 skipped, 2 failed. ONLY the 2 pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are ALLOWED; everything else MUST pass.

MANDATE: MAXIMIZE BAB COVERAGE TO >=97% WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

TARGETS (NON-NEGOTIABLE):
- data_loader.py >= 97% (hit remaining real branches)
- quality.py >= 93% (hit remaining real branches)
- BAB TOTAL >= 97% with chain intact
- tests/test_bab*.py: 100% GREEN. Full suite: only the 2 pre-existing failures allowed.

EXACT UNCOVERED LINES (CLEAN MEASUREMENT - RUN VERIFICATION BELOW):
- data_loader.py (95%, 296 stmts, 14 miss): 44, 120-122, 140, 192-193, 256, 311-313, 340-342
- quality.py (89%, 183 stmts, 21 miss): 3-11, 47-48, 110, 124, 145, 187-188, 192, 211-212, 216, 245-246, 250, 259-262

ANALYSIS OF REMAINING (FOCUS REAL HITABLE):
- data_loader 44: _normalize_index path where after tz stripping still not DatetimeIndex -> raise BABDataError. Hard to construct but possible with custom index types.
- data_loader 120-122: _drop_all_nan_columns except (ValueError,TypeError) when to_numeric fails on weird objects - partial coverage exists, may need objects that throw differently.
- data_loader 140: _coerce_numeric inner try raises BABDataError (we re-raise) - need astype to raise BABDataError directly.
- data_loader 192-193: _coerce_numeric outer except fallback - need to trigger when inner paths don't catch.
- data_loader 256: benchmark all-NaN finite check - likely covered by existing tests; verify.
- data_loader 311-313, 340-342: parquet/hdf5 outer except catching OSError/ValueError after inner wrapper. Need to force those specific exception types.
- quality 3-11: imports/module setup - often unreachable in coverage of executed module; SKIP unless provably hittable.
- quality 47-48, 110, 124, 145, 187-188, 192, 211-212, 216, 245-246, 250, 259-262: real branches in data_quality_report/detect_outliers/etc - HIT THESE.

VERIFICATION METHOD (USE EXACTLY THIS — AVOIDS NUMPY C-EXTENSION ISSUES & FULL-COV TIMEOUTS):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob, sys, coverage, pytest
ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0, ROOT)
for mod, pat in [("data_loader", "tests/test_bab_data_loader*.py"), ("quality", "tests/test_bab_quality*.py")]:
    files = sorted(glob.glob(ROOT + "/" + pat))
    cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"], data_file=None)
    cov.start()
    rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
    cov.stop()
    print("="*60)
    print(f"COVERAGE: {mod}")
    cov.report(show_missing=True, include=ROOT + f"/strategies/betting_against_beta/{mod}.py")
    if rc != 0:
        sys.exit(rc)
PYEOF
# Gate 1: focused BAB module tests must stay green
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py
# Gate 2: spot-check full suite (only 2 pre-existing allowed)
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider 2>&1 | tail -15
```

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF A MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE WITH SAME RIGOR AND HEAVY WORK. NO SPINNING.
- RUN GATES AFTER CHANGES. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.

FOCUS ORDER (STRICT):
1. strategies/betting_against_beta/data_loader.py (push 95% -> >=97%)
2. strategies/betting_against_beta/quality.py (push 89% -> >=93%)
3. Any other BAB module if both stall on truly unreachable lines

BOTTLENECKS TO REMOVE:
- DO NOT run full `coverage run` on entire suite (numpy C-ext issues). USE the inline driver above.
- DO NOT run expensive full-suite coverage. Only gate with `pytest -q` as specified.
- AVOID broad refactors. Prefer targeted tests that exercise existing error/edge paths.
- DO NOT get distracted by controller/infra tests - only the 2 pre-existing failures are allowed.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. Prioritize data_loader.py then quality.py. Hit only real hitable branches. Every turn must produce substantive test/logic changes. Focus on the specific missing lines identified above.

## VERIFIED GATES (CURRENT - 2026-10-31T11:48:27Z)
- data_loader.py: 95% (14 misses: 44,120-122,140,192-193,256,311-313,340-342)
- quality.py: 89% (21 misses: 3-11,47-48,110,124,145,187-188,192,211-212,216,245-246,250,259-262)
- BAB suite (tests/test_bab*.py): 1109 passed, 5 skipped, GREEN
- Full suite: 1582 passed, 11 skipped, 2 failed (pre-existing workflow sync in test_controller_progress_accounting.py — ALLOWED)

## EXACT NEXT STEPS (CHAINED)
1. **IMMEDIATE (data_loader.py)**: Run the exact verification method. Target 120-122 first (drop_all_nan_columns except) with objects that make to_numeric throw in specific ways. Target 140/192-193 in _coerce_numeric with a DataFrame subclass that makes astype raise BABDataError or other edge cases. Target 311-313, 340-342 with mocks to force OSError/ValueError after inner try blocks.
2. **ITERATE**: After each batch, re-run focused coverage + BAB suite. If coverage flat after hitting obvious paths, explicitly call out unreachable vs missed and move to quality.py.
3. **quality.py**: Attack hitable branches (lines 47-48, 110, 124, 145, 187-188, 192, 211-212, 216, 245-246, 250, 259-262). Look up actual code at those lines and add precise tests. Skip 3-11 (imports) unless provably hittable.
4. **FINAL GATE**: Before ending session, run BAB suite (must be GREEN) and spot-check full suite (only 2 pre-existing allowed). Update this handoff only if genuinely new bottlenecks discovered and removed.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file)
