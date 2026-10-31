# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T08:04:03Z

## TIMESTAMP
2026-10-31T08:04:03Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

PRIORITY #1: strategies/betting_against_beta/beta.py | REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

CURRENT STATE (VERIFIED):
- beta.py: 94% (286 stmts, 16 miss) — ABSOLUTE BOTTLENECK
- BAB beta-focused suite (excl. perf): 355 passed, GREEN (~2.5s)
- Broad BAB suite: 1160 passed, 5 skipped, 0 failed — MUST STAY GREEN
- Full suite: 1566 passed, 11 skipped, 2 failed (ONLY pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are ALLOWED; everything else MUST pass)

TARGETS (NON-NEGOTIABLE):
- beta.py >= 95% (CRUSH remaining uncovered branches NOW)
- BAB TOTAL >= 97% (immediately after hitting >=95% on beta.py, attack next highest-leverage BAB module with no break)
- ZERO new regressions anywhere. BAB suite MUST remain fully green.

EXACT UNCOVERED LINES TO HIT (no guessing): 66-67, 114, 124, 144-145, 166, 182-185, 355-359

PRECISE FOCUS:
- rolling_beta fallthrough (66-67): force both _calc_rolling_beta_series paths to fail so we hit the final `except: return np.array([np.nan])` (n==0/final excepts).
- calculate_beta (114, 124, 144-145): cover y is None (114), empty after mask (124), and ensure BABDataError re-raise path (144-145) is exercised (e.g. None input).
- calculate_beta_fast (166, 182-185): empty after mask (166), nonfinite beta, LinAlgError, TypeError/ValueError/AttributeError inner and outer excepts.
- calculate_rolling_beta (355-359): force bad-asset path in outer except to raise BABDataError.

VERIFICATION BOTTLENECK ELIMINATED (USE THIS EXACT METHOD — DO NOT use `coverage run -m pytest`):
  cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
  PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'EOF'
  import glob, sys, coverage, pytest
  ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
  sys.path.insert(0, ROOT)
  files = sorted(f for f in (glob.glob(ROOT + "/tests/test_bab_beta*.py") + glob.glob(ROOT + "/tests/test_beta*.py")) if "perf" not in f)
  cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"])
  cov.start()
  rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
  cov.stop()
  cov.report(show_missing=True, include=ROOT + "/strategies/betting_against_beta/beta.py")
  sys.exit(rc)
  EOF

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF beta.py CANNOT HIT A BRANCH SAFELY IN THIS TURN, DO NOT SPIN — MOVE TO NEXT HIGHEST LEVERAGE BAB MODULE (data_loader.py or quality.py) WITH SAME RIGOR AND HEAVY WORK.
- RUN GATES AFTER CHANGES: focused beta coverage + BAB suite + (spot-check full suite if risky). NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. NO IDLE TURNS. NO EXCUSES.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. Crush beta.py first (biggest bottleneck), then immediately chain to next highest-leverage uncovered BAB modules (data_loader.py ~94%, quality.py ~95%) without breaking momentum. Every turn must produce substantive test/logic changes covering real branches.

## VERIFIED GATES (CURRENT)
- beta.py: 94% (286 stmts, 16 miss) — PRIMARY BOTTLENECK; missing: 66-67, 114, 124, 144-145, 166, 182-185, 355-359
- BAB beta-focused suite (bab/beta, excl. perf): 355 passed, GREEN in ~2.5s
- Broad BAB suite: 1160 passed, 5 skipped, 0 failed
- Full suite: 1566 passed, 11 skipped, 2 failed (unrelated workflow pattern sync in controller_progress - pre-existing, ALLOWED)
- BAB total coverage: ~96% overall; beta.py 94% — PRIMARY BOTTLENECK

## EXACT NEXT STEPS (CHAINED, NO STALLING)
1. **IMMEDIATE**: Run the WORKING coverage driver above on beta.py; confirm exact missing lines (66-67, 114, 124, 144-145, 166, 182-185, 355-359).
2. **HIT BRANCHES**: Cover each missing branch with precise tests/fixes:
   - rolling_beta fallthrough (66-67): construct objects where both _calc_rolling_beta_series paths fail so the n==0/final `except: return np.array([np.nan])` at 66-67 is reached.
   - calculate_beta (114, 124, 144-145): y is None (114), empty after mask (124), ensure BABDataError re-raise path (144-145) is covered (None input).
   - calculate_beta_fast (166, 182-185): empty after mask (166), nonfinite beta, LinAlgError, TypeError/ValueError/AttributeError inner and outer excepts.
   - calculate_rolling_beta (355-359): force bad asset path in outer except to raise BABDataError.
3. **GATE ON BETA**: Re-run focused coverage on beta.py until >= 95%. Do NOT move to docs/refactors.
4. **IMMEDIATE CHAIN**: Once beta.py >= 95%, run full BAB coverage scan and attack next highest-leverage module (likely data_loader.py or quality.py) hitting real uncovered branches with same rigor. Keep BAB suite green throughout.
5. **FINAL GATE**: Before ending session, run full BAB suite + spot-check full suite. Only the 2 pre-existing unrelated workflow sync failures may remain. All other tests must pass.

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST. Heavy substantive work every session - no idle passes.
- Change smallest set of files needed. File count is NOT a metric.
- VERIFICATION BOTTLENECK REMOVED: `coverage run -m pytest` is broken here (numpy C-extension double-import) and the full suite times out on perf tests. Use the inline coverage driver above (excludes perf tests, runs ~2.5s). Dependencies installed.
- If stall on beta.py (no new branch hitable safely), move to next highest leverage (data_loader.py/quality.py) with same rigor - NO SPINNING.
- Never leave gates red. If changes made, verify gates immediately.
- Momentum is mandatory: after completing a target, immediately pick the next highest-leverage uncovered BAB branch/module.
- No vanity work. Every change must cover uncovered logic or fix a real gap.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file - total 116 lines)
