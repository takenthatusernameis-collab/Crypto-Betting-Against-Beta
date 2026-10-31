# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T23:35:59Z

## TIMESTAMP
2026-10-31T23:35:59Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T23:35:59Z)
- Full suite (BAB tests): 1309 passed, 5 skipped, 0 failed (FULLY GREEN)
- Coverage (BAB package): 98% total, 50 misses
- beta.py: 94% (16 misses) — 101-102, 124, 138, 140-141, 144-145, 166, 178, 181, 355-359 — HIGHEST LEVERAGE NEXT
- metrics.py: 96% (6 misses)
- portfolio.py: 96% (8 misses) — 39-40 proven unreachable
- data_loader.py: 97% (10 misses)
- config.py: 98% (3 misses)
- signals.py: 98% (2 misses)
- strategy.py: 98% (3 misses)
- costs.py: 99% (2 misses)

## BOTTLENECKS
- beta.py holds the biggest gap by far (16 misses). Focus relentlessly here first.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (2026-10-31T23:35:59Z):
- BAB suite: 1309 passed, 5 skipped, 0 failed (FULLY GREEN)
- BAB coverage: 98% | total misses 50
- beta.py: 94% | 16 misses [101-102, 124, 138, 140-141, 144-145, 166, 178, 181, 355-359] <- ATTACK NOW

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

FOCUS ORDER (STRICT):
1. beta.py (94%, 16 misses) — IMMEDIATE. No other module until provably stuck with evidence.
2. metrics.py (96%, 6 misses)
3. portfolio.py (96%, 8 misses) — only hitable if provably reachable; 39-40 documented unreachable
4. data_loader.py (97%, 10 misses)
5. config.py/signals.py/strategy.py (98%)
6. costs.py (99%) only if provably reachable

EXECUTION PROTOCOL (HEAVY WORK):
- Read strategies/betting_against_beta/beta.py end-to-end. Map every miss to code.
- TDD: write FAILING test first hitting a real uncovered branch. Make it pass with minimal change preserving semantics.
- After EVERY batch, re-run focused coverage. Track progress.
- For each miss:
  101-102: exception in alignment block when Series detected but dropna/iloc fail
  124: empty after finite mask in calculate_beta
  138: non-finite beta from lstsq -> return nan
  140-141: LinAlgError in lstsq -> nan
  144-145: re-raise BABDataError
  166: calculate_beta_fast empty after mask -> nan
  178: calculate_beta_fast non-finite beta -> return 0.0
  181: calculate_beta_fast LinAlgError -> return 0.0
  355-359: fallback except path in calculate_rolling_beta when conversion fails
- NO SPINNING. If stuck >2 focused attempts on a subpath, document evidence and move to next untested branch.
- Preserve: 1-day lag, dollar-neutral, quantiles/deciles, beta window>=60 default, ranking logic, finiteness, BAB-specific errors, no bare except:

VERIFICATION:
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob,sys,coverage
ROOT="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0,ROOT)
files=sorted(glob.glob(ROOT+"/tests/test_bab*.py"))+[ROOT+"/tests/test_betting_against_beta_costs.py",ROOT+"/tests/test_betting_against_beta.py"]
cov=coverage.Coverage(source=[ROOT+"/strategies/betting_against_beta"],data_file=None)
cov.start()
import pytest
rc=pytest.main(["-q","-p","no:cacheprovider"]+files)
cov.stop()
cov.report(show_missing=True,include=ROOT+"/strategies/betting_against_beta/*.py")
raise SystemExit(rc)
PYEOF
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py tests/test_betting_against_beta_costs.py tests/test_betting_against_beta.py 2>&1 | tail -2

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE ALL INVARIANTS. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> DOCUMENT EVIDENCE IN HANDOFF.md AND MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE. NO SPINNING.
- RUN GATES AFTER EVERY BATCH. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.
- END SESSION ONLY IF BAB COVERAGE HIGHER THAN START OR UNREACHABLE LINES EXPLICITLY DOCUMENTED WITH EVIDENCE.

DO HEAVY WORK ON beta.py NOW. NO DELAY.
```

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase
