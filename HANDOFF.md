# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T09:58:12Z

## TIMESTAMP
2026-10-31T09:58:12Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T09:58:12Z):
- beta.py: 97% (dead/unreachable misses only — do not spin)
- data_loader.py: 91% (293 stmts, 26 miss) — PRIORITY #1
- quality.py: 88% (183 stmts, 22 miss) — PRIORITY #2
- BAB suite (tests/test_bab*.py): 1058 passed, 5 skipped, GREEN
- Full suite: 1582 passed, 11 skipped, 2 failed. ONLY the 2 pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are ALLOWED; everything else MUST pass.

MANDATE: MAXIMIZE BAB COVERAGE TO >=97% WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

TARGETS (NON-NEGOTIABLE):
- data_loader.py >= 95% (attack hitable uncovered branches with precise tests/minimal defensive fixes)
- quality.py >= 93% (cover real hitable branches)
- BAB TOTAL >= 97% with chain intact
- tests/test_bab*.py: 100% GREEN. Full suite: only the 2 pre-existing failures allowed.

EXACT UNCOVERED LINES (CLEAN MEASUREMENT):
- data_loader.py (91%, 293 stmts, 26 miss): 37-41, 44, 64-65, 117-119, 133, 137, 142, 189-190, 227-228, 253, 308-310, 327, 337-339
- quality.py (88%, 183 stmts, 22 miss): 3-11, 47-48, 110, 124, 145, 187-188, 192, 211-212, 216, 245-246, 250, 259-262, 277

NOTE: many are imports/defs/exception hard-paths or unreachable (e.g. data_loader 253, quality 3-11 def/imports, quality 259-262). DO NOT SPIN. HIT REAL HITABLE BRANCHES (coercion/normalization/NaN/empty/exception paths that can be triggered safely via public APIs). If after 2-3 focused attempts a line is provably unreachable with no safe test, SKIP IT and move to next highest-leverage.

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
1. strategies/betting_against_beta/data_loader.py (biggest immediate lift)
2. strategies/betting_against_beta/quality.py
3. Any other BAB module if both stall on truly unreachable lines

BOTTLENECKS TO REMOVE:
- DO NOT run full `coverage run` on entire suite (numpy C-ext issues). USE the inline driver above.
- DO NOT run expensive full-suite coverage. Only gate with `pytest -q` as specified.
- AVOID broad refactors. Prefer targeted tests that exercise existing error/edge paths.
- DO NOT get distracted by controller/infra tests - only the 2 pre-existing failures are allowed.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. Prioritize data_loader.py then quality.py. Hit only real hitable branches. Every turn must produce substantive test/logic changes. Previous sessions added bottleneck/coverage tests pushing BAB suite to 1058 passed.

## VERIFIED GATES (CURRENT)
- beta.py: 97% (dead misses only)
- data_loader.py: 91% (293 stmts, 26 miss)
- quality.py: 88% (183 stmts, 22 miss)
- BAB suite (tests/test_bab*.py): 1058 passed, 5 skipped, GREEN
- Full suite: 1582 passed, 11 skipped, 2 failed (pre-existing workflow sync in test_controller_progress_accounting.py — ALLOWED)

## EXACT NEXT STEPS (CHAINED)
1. **IMMEDIATE (data_loader.py)**: Run the exact verification method. Map each miss to public API paths (coerce/normalize/load helpers, exception paths). Add 1-3 precise tests targeting real branches first.
2. **ITERATE**: After each batch, re-run focused coverage + BAB suite. If coverage of data_loader flat after hitting obvious paths, explicitly call out unreachable vs missed and move to quality.py.
3. **quality.py**: Attack hitable branches (validation/filters/edge cases). Keep changes minimal.
4. **FINAL GATE**: Before ending session, run BAB suite (must be GREEN) and spot-check full suite (only 2 pre-existing allowed). Update this handoff only if genuinely new bottlenecks discovered and removed.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file)
