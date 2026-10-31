# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T22:50:39Z

## TIMESTAMP
2026-10-31T22:50:39Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T22:50:39Z)
- Full suite: BAB suite 1312 passed, 5 skipped, 0 failed (FULLY GREEN)
- Coverage (BAB package): 98% total, 50 misses
- regime.py: 100% (0 misses) — DONE
- backtest.py: 100% (0 misses) — DONE
- attribution.py/data.py/cli.py/data_sources.py/errors.py/quality.py/shorting.py/sizing.py: 100% — DONE
- beta.py: 94% (16 misses) — 101-102, 124, 138, 140-141, 144-145, 166, 178, 181, 355-359 — HIGHEST LEVERAGE NEXT
- metrics.py: 96% (6 misses) — 25, 42, 97, 114, 126, 138
- portfolio.py: 96% (8 misses) — 39-40 (proven unreachable), 164-169
- data_loader.py: 97% (10 misses) — 44, 192-193, 256, 311-313, 340-342
- config.py: 98% (3 misses) — 95-96, 113
- signals.py: 98% (2 misses) — 37, 75
- strategy.py: 98% (3 misses) — 181, 188-189
- costs.py: 99% (2 misses) — 59-60

## BOTTLENECKS REMOVED (THIS SESSION)
- regime.py pushed to 100% (was 94%, 12 misses). backtest.py pushed to 100% (was 97%). BAB total coverage now 98% (50 misses, down from 64). Full BAB suite green.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T22:50:39Z):
- BAB suite: 1312 passed, 5 skipped, 0 failed (FULLY GREEN)
- Coverage (BAB package): 98% total, 50 misses
- beta.py: 94% (16 misses) — HIGHEST LEVERAGE NEXT (lowest %, most misses)
- metrics.py: 96% (6 misses)
- portfolio.py: 96% (8 misses, 39-40 proven unreachable)
- data_loader.py: 97% (10 misses)
- config.py/signals.py/strategy.py: 98% (2-3 misses each)
- costs.py: 99% (2 misses)

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

FOCUS ORDER (STRICT):
1. beta.py (94%, 16 misses: 101-102, 124, 138, 140-141, 144-145, 166, 178, 181, 355-359) — IMMEDIATE TARGET.
2. metrics.py (96%, 6 misses)
3. portfolio.py (96%, 8 misses) — only if 164-169 provably hitable; else document unreachable and skip
4. data_loader.py (97%, 10 misses)
5. config.py / signals.py / strategy.py (98%, 2-3 misses)
6. costs.py (99%, 2 misses) — only if provably reachable; else document unreachable

HEAVY-WORK CAMPAIGN (MUST EXECUTE):
- ATTACK beta.py AGGRESSIVELY. Read strategies/betting_against_beta/beta.py end-to-end. Map all 16 misses to testable branches.
- Write a FAILING test first (TDD). Add minimal assertions that hit real uncovered lines. Make it pass against correct existing behavior only.
- Re-run focused coverage after EVERY batch. If a branch is not safely hitable without changing semantics, prove it's unreachable and move on.
- NO SPINNING. If stuck >2 focused attempts on a subpath, document evidence and move to next untested branch/module.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.

VERIFICATION METHOD:
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob, sys, coverage
ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0, ROOT)
files = sorted(glob.glob(ROOT + "/tests/test_bab*.py")) + [ROOT + "/tests/test_betting_against_beta_costs.py", ROOT + "/tests/test_betting_against_beta.py"]
cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"], data_file=None)
cov.start()
import pytest
rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
cov.stop()
print("="*60)
print("COVERAGE: BAB package")
cov.report(show_missing=True, include=ROOT + "/strategies/betting_against_beta/*.py")
if rc != 0:
    sys.exit(rc)
PYEOF
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py tests/test_betting_against_beta_costs.py tests/test_betting_against_beta.py 2>&1 | tail -3

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE ALL INVARIANTS. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF A MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE WITH SAME RIGOR AND HEAVY WORK. NO SPINNING.
- RUN GATES AFTER EVERY BATCH. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.
- END SESSION ONLY IF BAB COVERAGE HIGHER THAN START OR UNREACHABLE LINES EXPLICITLY DOCUMENTED WITH EVIDENCE.

DO HEAVY WORK ON beta.py NOW. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage toward 100% with zero regressions. Highest leverage now beta.py (94%, 16 misses); then metrics.py, portfolio.py, data_loader.py.

## EXACT NEXT STEPS (CHAINED)
1. IMMEDIATE (TURN 1): Confirm BAB gates green. Read beta.py fully; map misses to testable branches.
2. ATTACK: Find uncovered branches in beta.py. Write failing TDD test hitting real uncovered path, add minimal test/logic to cover correctly.
3. ITERATE: Re-run coverage after each batch. Push beta.py up aggressively toward 100%.
4. DOCUMENT/ROTATE: If beta.py stalls with provable unreachable lines, document with evidence in HANDOFF.md and move to metrics.py.
5. FINAL GATE: Before ending, BAB suite GREEN + BAB total coverage >= session start (or unreachable documented).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase
filePath: /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/HANDOFF.md