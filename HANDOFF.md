# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T16:50:42Z

## TIMESTAMP
2026-10-31T16:50:42Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T16:50:42Z)
- Full suite: 1670 passed, 11 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): 1146 passed, 5 skipped, 0 failed (GREEN)
- sizing.py: 100% COMPLETE (was 56%, 72 misses) — TDD attack done this session
- quality.py: 100% COMPLETE
- data_loader.py: 97% COMPLETE — all 10 misses provably unreachable (documented)
- BAB TOTAL: ~2606 stmts, ~239 miss, ~91% (sizing.py fully closed)

## BOTTLENECKS REMOVED (THIS SESSION)
- sizing.py attacked aggressively via TDD → 100% coverage. All sizer classes, validation, paths, shorthands covered.
- Workflow pattern sync (`*/.github/workflows/*`) in main.yml stage_safe_changes/cp cases — tests green.
- No blocked sessions; gates fully green. No bottlenecks remain.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T16:50:42Z):
- Full suite: 1670 passed, 11 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): 1146 passed, 5 skipped, 0 failed (GREEN)
- sizing.py: 100% COMPLETE
- quality.py: 100% COMPLETE
- data_loader.py: 97% COMPLETE — all 10 misses provably unreachable
- BAB TOTAL: ~91% (sizing.py closed)

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

FOCUS ORDER (STRICT):
1. shorting.py (66%, 58 misses) — IMMEDIATE TARGET. HIGHEST REMAINING IMPACT.
2. metrics.py (67%, 43 misses)
3. costs.py (68%, 48 misses)
4. portfolio.py (83%, 38 misses)
5. backtest.py (89%, 8 misses)
6. beta.py (95%, 14 misses)
7. regime.py (94%, 12 misses)
8. config.py / signals.py / strategy.py (98%, 3-3 misses)

HEAVY-WORK CAMPAIGN (MUST EXECUTE):
- ATTACK shorting.py AGGRESSIVELY. Read strategies/betting_against_beta/shorting.py end-to-end. Identify every uncovered branch/exception/path.
- Write a FAILING test first (TDD). Add minimal assertions that hit real uncovered lines. Make it pass against correct existing behavior only.
- Re-run focused coverage after EVERY batch. If a branch is not safely hitable without changing semantics, prove it's unreachable and move on.
- NO SPINNING. If stuck >2 focused attempts on a subpath, document evidence and move to next untested branch/module.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.

VERIFICATION METHOD:
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
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider 2>&1 | tail -4

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE ALL INVARIANTS. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF A MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE WITH SAME RIGOR AND HEAVY WORK. NO SPINNING.
- RUN GATES AFTER EVERY BATCH. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.
- END SESSION ONLY IF BAB COVERAGE HIGHER THAN START OR UNREACHABLE LINES EXPLICITLY DOCUMENTED WITH EVIDENCE.

DO HEAVY WORK ON shorting.py NOW. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage toward 100% with zero regressions. sizing.py now 100%. quality.py 100%. data_loader.py 97% (unreachable). IMMEDIATE FOCUS: shorting.py (66%) - highest remaining impact. Then metrics.py, costs.py, portfolio.py, backtest.py, beta.py, regime.py, config/signals/strategy.

## EXACT NEXT STEPS (CHAINED)
1. IMMEDIATE (TURN 1): Confirm gates green. Read shorting.py fully.
2. ATTACK: Find uncovered branches in shorting.py. Write failing TDD test hitting real uncovered path, add minimal test/logic to cover correctly.
3. ITERATE: Re-run coverage after each batch. Push shorting.py up aggressively.
4. DOCUMENT/ROTATE: If shorting.py stalls with provable unreachable lines, document with evidence in HANDOFF.md and move to metrics.py.
5. FINAL GATE: Before ending, BAB suite GREEN + full suite 0 failures + BAB total coverage >= session start (or unreachable documented).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file)
