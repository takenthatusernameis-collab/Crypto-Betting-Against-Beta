# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T19:48:49Z

## TIMESTAMP
2026-10-31T19:48:49Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T19:48:49Z)
- Full suite: 1736 passed, 11 skipped, 2 failed. The 2 failures are pre-existing, non-BAB controller/infra tests in tests/test_controller_progress_accounting.py (workflow-file pattern assertions, environmental) — NOT BAB. Do not chase them unless they regress.
- BAB suite (tests/test_bab*.py + test_betting_against_beta*): 1332 passed, 5 skipped, 0 failed (FULLY GREEN)
- Coverage (BAB package): 97% total, 69 misses

Per-module coverage (stmts / miss / cover / missing lines):
- shorting.py: 164/0/100% — DONE
- sizing.py: 163/0/100% — DONE
- quality.py: 183/0/100% — DONE
- data.py: 15/0/100% — DONE
- attribution.py: 37/0/100% — DONE
- data_sources.py: 67/0/100% — DONE
- errors.py: 2/0/100% — DONE
- cli.py: 34/0/100% — DONE
- costs.py: 150/2/99% — misses 59-60 (dead `except Exception: pass` in `__setattr__`; provably unreachable under normal construction — document or leave, do not spin)
- backtest.py: 74/2/97% — misses 58-59 (except branch in weight cleaning)
- data_loader.py: 296/10/97% — misses 44, 192-193, 256, 311-313, 340-342
- beta.py: 286/14/95% — misses 124, 138, 140-141, 144-145, 166, 178, 181, 355-359
- config.py: 199/3/98% — misses 95-96, 113
- signals.py: 113/2/98% — misses 37, 75
- strategy.py: 198/3/98% — misses 181, 188-189
- portfolio.py: 223/13/94% — misses 39-40, 87-88, 155-160, 200-201, 275  <-- IMMEDIATE TARGET (most misses at 94%)
- regime.py: 186/12/94% — misses 111, 139-140, 175-177, 181-182, 185, 188, 190, 217
- metrics.py: 134/8/94% — misses 25, 42, 71, 97, 114, 126, 138, 161

## BOTTLENECKS REMOVED (THIS SESSION)
- Stale HANDOFF corrected: costs.py was listed as 68%/48 misses but is actually 99%/2 misses. Next agent must not re-attack costs.py; it is effectively done (only a dead except-branch remains).
- No blocked sessions. Gates green.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T19:48:49Z):
- Full suite: 1736 passed, 11 skipped, 2 failed (2 pre-existing non-BAB infra failures in test_controller_progress_accounting.py — DO NOT CHASE)
- BAB suite: 1332 passed, 5 skipped, 0 failed (FULLY GREEN)
- Coverage (BAB package): 97% total, 69 misses
- costs.py: 99% (2 misses: 59-60 dead except branch — effectively DONE, do not re-attack)
- portfolio.py: 94% (13 misses: 39-40, 87-88, 155-160, 200-201, 275) — IMMEDIATE TARGET, HIGHEST REMAINING IMPACT
- regime.py: 94% (12 misses)
- metrics.py: 94% (8 misses)
- backtest.py: 97% (2 misses: 58-59)
- beta.py: 95% (14 misses)
- config.py/signals.py/strategy.py: 98% (2-3 misses each)
- data_loader.py: 97% (10 misses)

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

FOCUS ORDER (STRICT):
1. portfolio.py (94%, 13 misses) — IMMEDIATE TARGET. HIGHEST REMAINING IMPACT (most misses at 94%).
2. regime.py (94%, 12 misses)
3. metrics.py (94%, 8 misses)
4. backtest.py (97%, 2 misses: 58-59)
5. beta.py (95%, 14 misses)
6. config.py / signals.py / strategy.py (98%, 2-3 misses)
7. costs.py (99%, 2 misses) — only if provably reachable with evidence; otherwise document as unreachable and skip
8. data_loader.py (97%, 10 misses)

HEAVY-WORK CAMPAIGN (MUST EXECUTE):
- ATTACK portfolio.py AGGRESSIVELY. Read strategies/betting_against_beta/portfolio.py end-to-end. Identify every uncovered branch/exception/path (lines 39-40, 87-88, 155-160, 200-201, 275).
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

DO HEAVY WORK ON portfolio.py NOW. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage toward 100% with zero regressions. shorting/sizing/quality/data/attribution/data_sources/errors/cli all at 100%. costs.py at 99% (effectively done). Next highest impact: portfolio.py (94%, 13 misses), then regime.py (94%, 12 misses), metrics.py (94%, 8 misses).

## EXACT NEXT STEPS (CHAINED)
1. IMMEDIATE (TURN 1): Confirm BAB gates green. Read portfolio.py fully; map misses 39-40, 87-88, 155-160, 200-201, 275 to testable branches.
2. ATTACK: Find uncovered branches in portfolio.py. Write failing TDD test hitting real uncovered path, add minimal test/logic to cover correctly.
3. ITERATE: Re-run coverage after each batch. Push portfolio.py up aggressively toward 100%.
4. DOCUMENT/ROTATE: If portfolio.py stalls with provable unreachable lines, document with evidence in HANDOFF.md and move to regime.py.
5. FINAL GATE: Before ending, BAB suite GREEN + full suite BAB portion 0 failures + BAB total coverage >= session start (or unreachable documented).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase

(End of file)
