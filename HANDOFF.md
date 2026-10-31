# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T15:07:00Z

## TIMESTAMP
2026-10-31T15:07:00Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## BOTTLENECKS REMOVED (THIS SESSION)
- Fixed workflow pattern sync: added `*/.github/workflows/*` to .github/workflows/main.yml stage_safe_changes (was missing). Both controller progress accounting tests now pass.
- Full suite GREEN again: 1656 passed, 11 skipped, 0 failed.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T15:07:00Z)
- Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): All passing
- quality.py: 100% (183 stmts, 0 miss) — COMPLETE
- data_loader.py: 88% (296 stmts, 37 miss) — PRIMARY TARGET (need >=97%)

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T15:07:00Z):
- Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)
- quality.py: 100% COMPLETE
- data_loader.py: 88% (37 misses) — PRIMARY TARGET

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

TARGETS (NON-NEGOTIABLE):
- data_loader.py >= 97% (reduce misses from 37 to <= 9)
- BAB TOTAL >= 97% with chain intact
- tests/test_bab*.py: 100% GREEN. Full suite: 0 failures allowed.

DATA_LOADER MISSING LINES (RUN VERIFICATION BEFORE CLAIMING PROGRESS):
strategies/betting_against_beta/data_loader.py: 8-23, 44, 51, 94, 103, 130, 192-196, 256, 269, 291, 311-316, 340-345, 371, 404, 413, 447, 463, 500-504, 509

FOCUS ANALYSIS (data_loader.py) - PRIORITIZE HIGHEST LEVERAGE:
- 8-23: Module docstring/imports/setup - likely SKIP unless provably hittable
- 44: _normalize_index - after tz/localize still not DatetimeIndex -> raise BABDataError
- 51: validate_returns_dataframe early path
- 94: load_prices_csv parsing branch
- 103: load_prices_csv another path
- 130: load_prices_json/other loader path
- 192-196: _coerce_numeric outer except (ValueError, TypeError, AttributeError) fallback with multiple except handlers
- 256: validate_returns_dataframe benchmark all-NaN finite check
- 269, 291: other validation branches
- 311-316: parquet/hdf5 outer except (OSError, ValueError) - inner converts Exception->BABDataError first so may be partially unreachable; verify
- 340-345: similar parquet/hdf5 exception paths
- 371, 404, 413, 447, 463: various loader/validator branches
- 500-504, 509: end paths

VERIFICATION METHOD (USE EXACTLY THIS):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob, sys, coverage, pytest
ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0, ROOT)
for mod, pat in [("data_loader", "tests/test_bab_data_loader*.py")]:
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

FOCUS ORDER (STRICT):
1. strategies/betting_against_beta/data_loader.py (88% -> >=97%) - Attack 44, 192-196, 256 first as highest leverage. Document 311-316/340-345 if provably unreachable.
2. Any other BAB module with lower coverage if data_loader stalls on truly unreachable lines.

HEAVY-WORK FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID THIS):
- Each session must end with coverage strictly higher than it started, OR explicit evidence that remaining lines are provably unreachable (documented in this handoff).
- No session may end with gates red. If gates go red, the very next turn fixes them before any new coverage work.
- Write a failing test first (TDD), then the minimal test/logic to make it green against existing correct behavior. Never add assertions-free tests.
- Re-run focused coverage + BAB suite after EVERY batch. If coverage is flat after hitting obvious paths, explicitly call out unreachable vs missed and move to the next module.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. quality.py is complete (100%). Focus all efforts on data_loader.py to push from 88% to >=97%. Hit only real hitable branches.

## VERIFIED GATES (CURRENT - 2026-10-31T15:07:00Z)
- data_loader.py: 88% (37 misses)
- quality.py: 100%
- BAB suite (tests/test_bab*.py): GREEN
- Full suite: 1656 passed, 11 skipped, 0 failed (FULLY GREEN)

## EXACT NEXT STEPS (CHAINED)
1. **IMMEDIATE (data_loader.py)**: Run the exact verification method. Focus on lines 44, 192-196, 256 first. Understand _normalize_index, _coerce_numeric, and validate_returns_dataframe paths.
2. **ITERATE**: After each batch, re-run focused coverage + BAB suite. For exception handling paths, trace whether inner exceptions get converted first (making outer except unreachable).
3. **DOCUMENT**: If any lines are provably unreachable after reasonable attempts, document with evidence and move to next target.
4. **FINAL GATE**: Before ending session, run BAB suite (must be GREEN) and full suite (0 failures).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required
