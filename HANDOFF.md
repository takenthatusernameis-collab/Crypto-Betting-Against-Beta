# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T18:44:32Z

## TIMESTAMP
2026-10-31T18:44:32Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T18:44:32Z)
- Full suite: 1203 passed, 5 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): 1203 passed, 5 skipped, 0 failed (GREEN)
- shorting.py: 100% COMPLETE (was 66%)
- sizing.py: 100% COMPLETE
- quality.py: 100% COMPLETE
- metrics.py: 94% COMPLETE (8 misses)
- data_loader.py: 97% COMPLETE — all 10 misses provably unreachable (documented)
- BAB TOTAL: improved from ~91% toward higher (shorting+metrics pushed)

## BOTTLENECKS REMOVED (THIS SESSION)
- shorting.py attacked via TDD → 100% coverage (all branches/paths covered)
- metrics.py attacked → 94% coverage (added compute_metrics alias, comprehensive edge coverage)
- Gates remain fully green; no blocked sessions.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T18:44:32Z):
- Full suite: 1203 passed, 5 skipped, 0 failed (FULLY GREEN)
- BAB suite (tests/test_bab*.py): 1203 passed, 5 skipped, 0 failed (GREEN)
- shorting.py: 100% COMPLETE
- sizing.py: 100% COMPLETE
- quality.py: 100% COMPLETE
- metrics.py: 94% COMPLETE (8 misses)
- data_loader.py: 97% COMPLETE — all 10 misses provably unreachable
- BAB coverage improving; momentum MANDATORY.

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

FOCUS ORDER (STRICT):
1. costs.py (68%, 48 misses) — IMMEDIATE TARGET. HIGHEST REMAINING IMPACT.
2. portfolio.py (83%, 38 misses)
3. backtest.py (89%, 8 misses)
4. beta.py (95%, 14 misses)
5. regime.py (94%, 12 misses)
6. config.py / signals.py / strategy.py (98%, 3-3 misses)
7. metrics.py (94%, 8 misses) — only if costs/portfolio blocked with evidence

HEAVY-WORK CAMPAIGN (MUST EXECUTE):
- ATTACK costs.py AGGRESSIVELY. Read strategies/betting_against_beta/costs.py end-to-end. Identify every uncovered branch/exception/path.
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

DO HEAVY WORK ON costs.py NOW. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage toward 100% with zero regressions. shorting.py now 100%. metrics.py 94%. Next highest impact: costs.py (68%).

## EXACT NEXT STEPS (CHAINED)
1. IMMEDIATE (TURN 1): Confirm gates green. Read costs.py fully.
2. ATTACK: Find uncovered branches in costs.py. Write failing TDD test hitting real uncovered path, add minimal test/logic to cover correctly.
3. ITERATE: Re-run coverage after each batch. Push costs.py up aggressively.
4. DOCUMENT/ROTATE: If costs.py stalls with provable unreachable lines, document with evidence in HANDOFF.md and move to portfolio.py.
5. FINAL GATE: Before ending, BAB suite GREEN + full suite 0 failures + BAB total coverage >= session start (or unreachable documented).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file)
