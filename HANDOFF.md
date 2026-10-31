# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T08:55:30Z

## TIMESTAMP
2026-10-31T08:55:30Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

STATUS SUMMARY (VERIFIED THIS SESSION):
- beta.py: 97% (286 stmts, 9 miss: 124, 144-145, 166, 355-359 — dead/unreachable, do not spin).
- data_loader.py: 90% (293 stmts, 33 miss) — improved from prior; remaining gaps in tz normalization edge cases, promote/set_index fallbacks, _drop_all_nan_columns exception paths, _coerce_numeric edge paths, validate/load error branches. Many are hard to hit without invasive changes; focus on real hitable branches.
- quality.py: 98% (183 stmts, 4 miss: 132, 259, 266, 277) — near complete.
- BAB beta-focused suite: 1048 passed, 5 skipped, GREEN.
- Full suite: 1572 passed, 11 skipped, 2 failed. ONLY the 2 pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are ALLOWED; everything else MUST pass.

PRIORITY #1: strategies/betting_against_beta/data_loader.py | BAB-FIRST MANDATE
PRIORITY #2: strategies/betting_against_beta/quality.py | BAB-FIRST MANDATE (already high; only polish if trivial)

TARGETS (NON-NEGOTIABLE):
- data_loader.py: attack remaining uncovered branches with precise tests, no regressions. Avoid unreachable paths.
- quality.py: cover remaining if hitable safely.
- BAB TOTAL >= 97% with chain intact.
- ZERO new regressions anywhere. BAB suite MUST remain fully green.

EXACT UNCOVERED LINES TO HIT (data_loader.py, current):
- data_loader.py (90%, 293 stmts, 33 miss): 37-41, 44, 64-65, 72-73, 107, 117-119, 133, 137, 142, 189-190, 227-228, 253, 282-283, 308-310, 327, 337-339
- quality.py (98%, 183 stmts, 4 miss): 132, 259, 266, 277

VERIFICATION METHOD (USE THIS EXACT METHOD):
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
- RUN GATES AFTER CHANGES: focused module coverage + BAB suite (tests/test_bab*.py) + spot-check full suite if risky. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. NO IDLE TURNS. NO EXCUSES.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. Focus on data_loader.py (90%) — hit real branches where possible; quality.py is already 98%. Every turn must produce substantive test/logic changes covering real branches.

## VERIFIED GATES (CURRENT)
- beta.py: 97% (dead misses only)
- data_loader.py: 90% (293 stmts, 33 miss)
- quality.py: 98% (183 stmts, 4 miss)
- BAB suite (tests/test_bab*.py): 1048 passed, 5 skipped, GREEN
- Full suite: 1572 passed, 11 skipped, 2 failed (pre-existing workflow sync in test_controller_progress_accounting.py — ALLOWED)

## EXACT NEXT STEPS (CHAINED, NO STALLING)
1. **IMMEDIATE**: Run verification method on data_loader.py; focus on hitable lines (e.g., exception paths in loaders/coercion/normalization that can be triggered safely).
2. **HIT BRANCHES**: Add precise tests with assertions; keep BAB suite green.
3. **GATE**: Re-run focused coverage; if stuck on unreachable paths, move to other BAB modules with same rigor.
4. **FINAL GATE**: Before ending session, run BAB suite + spot-check full suite. Only the 2 pre-existing failures may remain.

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST. Heavy substantive work every session - no idle passes.
- Change smallest set of files needed.
- Use inline coverage driver (coverage run has numpy C-extension issues; full suite times out on perf).
- If stall, move to next highest leverage with same rigor.
- Never leave gates red.
- Momentum mandatory.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

(End of file)
