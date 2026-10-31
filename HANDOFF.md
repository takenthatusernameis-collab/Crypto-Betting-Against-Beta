# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T08:16:52Z

## TIMESTAMP
2026-10-31T08:16:52Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

STATUS SUMMARY (VERIFIED THIS SESSION):
- beta.py: 94% -> 97% (286 stmts, 9 miss). BOTTLENECK CRUSHED.
  Remaining misses 124, 144-145, 166, 355-359 are DEAD/UNREACHABLE code:
  * 124 (len(y)==0) short-circuited by earlier empty-mask return at 118-119.
  * 144-145 (except BABDataError: raise) unreachable: the BABDataError raise is at line 75, OUTSIDE the try.
  * 166 (len(a_m)==0) unreachable: np.any(mask) True guarantees a_m non-empty.
  * 355-359 (calculate_rolling_beta outer except) unreachable: the outer except wraps only lines 295-344 and every conversion-error spot inside is caught by inner tries (295-310, 327-333) or re-raised at 345-346.
  DO NOT SPIN on these. beta.py >= 95% target is MET (97%).
- BAB beta-focused suite (excl. perf): 372 passed, GREEN (~2.5s).
- Broad BAB suite: green (included in full suite below).
- Full suite: 1563 passed, 11 skipped, 2 failed. ONLY the 2 pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are ALLOWED; everything else MUST pass.

PRIORITY #1: strategies/betting_against_beta/data_loader.py | BAB-FIRST MANDATE
PRIORITY #2: strategies/betting_against_beta/quality.py | BAB-FIRST MANDATE

TARGETS (NON-NEGOTIABLE):
- data_loader.py: attack its exact uncovered branches (below) with precise tests, no regressions.
- quality.py: attack its exact uncovered branches (below) with precise tests, no regressions.
- BAB TOTAL >= 97% (chain data_loader -> quality with no break in momentum).
- ZERO new regressions anywhere. BAB suite MUST remain fully green.

EXACT UNCOVERED LINES TO HIT (no guessing):
- data_loader.py (90%, 287 stmts, 30 miss): 37-41, 44, 64-65, 72-73, 107, 117-119, 183-184, 221-222, 247, 276-277, 302-304, 321, 331-333, 357-358
- quality.py (87%, 183 stmts, 24 miss): 3-11, 47-48, 110, 124, 132, 145, 187-188, 192, 211-212, 216, 245-246, 250, 259-262, 266, 277

VERIFICATION METHOD (USE THIS EXACT METHOD — DO NOT use `coverage run -m pytest`):
  cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
  PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'EOF'
  import glob, sys, coverage, pytest
  ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
  sys.path.insert(0, ROOT)
  for mod, pat in [("data_loader", "tests/test_bab_data_loader*.py"), ("quality", "tests/test_bab_quality*.py")]:
      files = sorted(glob.glob(ROOT + "/" + pat))
      cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"])
      cov.start()
      rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
      cov.stop()
      cov.report(show_missing=True, include=ROOT + f"/strategies/betting_against_beta/{mod}.py")
      if rc != 0: sys.exit(rc)
  EOF

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF a module stalls (no new branch hitable safely), move to the next highest-leverage BAB module WITH SAME RIGOR AND HEAVY WORK — NO SPINNING.
- RUN GATES AFTER CHANGES: focused module coverage + BAB suite + (spot-check full suite if risky). NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. NO IDLE TURNS. NO EXCUSES.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. beta.py is DONE at 97% (remaining misses are dead code). Chain immediately to data_loader.py (90%) then quality.py (87%), hitting real uncovered branches with the same rigor. Every turn must produce substantive test/logic changes covering real branches.

## VERIFIED GATES (CURRENT)
- beta.py: 97% (286 stmts, 9 miss: 124, 144-145, 166, 355-359 — all dead/unreachable, do not spin).
- BAB beta-focused suite (bab/beta, excl. perf): 372 passed, GREEN.
- Broad BAB suite: green.
- Full suite: 1563 passed, 11 skipped, 2 failed (pre-existing unrelated workflow sync in controller_progress - pre-existing, ALLOWED).
- data_loader.py: 90% (287 stmts, 30 miss) — NEXT TARGET.
- quality.py: 87% (183 stmts, 24 miss) — FOLLOW-ON TARGET.

## EXACT NEXT STEPS (CHAINED, NO STALLING)
1. **IMMEDIATE**: Run the verification method above on data_loader.py; confirm the exact missing lines (37-41, 44, 64-65, 72-73, 107, 117-119, 183-184, 221-222, 247, 276-277, 302-304, 321, 331-333, 357-358).
2. **HIT BRANCHES**: Cover each missing branch with precise tests/fixes; keep BAB suite green.
3. **GATE ON DATA_LOADER**: Re-run focused coverage until meaningfully improved. Do NOT move to docs/refactors.
4. **IMMEDIATE CHAIN**: Once data_loader is driven up, run full BAB coverage scan and attack quality.py hitting its exact uncovered branches (3-11, 47-48, 110, 124, 132, 145, 187-188, 192, 211-212, 216, 245-246, 250, 259-262, 266, 277) with same rigor.
5. **FINAL GATE**: Before ending session, run full BAB suite + spot-check full suite. Only the 2 pre-existing unrelated workflow sync failures may remain. All other tests must pass.

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST. Heavy substantive work every session - no idle passes.
- Change smallest set of files needed. File count is NOT a metric.
- VERIFICATION BOTTLENECK REMOVED: `coverage run -m pytest` is broken here (numpy C-extension double-import) and the full suite times out on perf tests. Use the inline coverage driver above (excludes perf tests). Dependencies installed.
- If stall on a module (no new branch hitable safely), move to next highest leverage (data_loader/quality) with same rigor - NO SPINNING.
- Never leave gates red. If changes made, verify gates immediately.
- Momentum is mandatory: after completing a target, immediately pick the next highest-leverage uncovered BAB branch/module.
- No vanity work. Every change must cover uncovered logic or fix a real gap.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file)
