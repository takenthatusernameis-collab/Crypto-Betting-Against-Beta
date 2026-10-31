# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T00:54:00Z

## TIMESTAMP
2026-10-31T00:54:00Z

## INITIAL TASK MESSAGE FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/beta.py | REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE
beta.py coverage is 89% (275 stmts, 29 miss). CRUSH remaining UNCOVERED BRANCHES.
TARGET: beta.py >= 95% | BAB TOTAL >= 97%.
DO NOT TOUCH FILES FOR VANITY. CHANGE ONLY SMALLEST SET NEEDED FOR REAL UNCOVERED BRANCHES.
HIT HARD LINES (current missing): estimate_betas fallthrough (55-56); calculate_beta alignment/disjoint/mask/min_obs/linalg/constant_x/None (90-91, 103, 113, 123, 125-126, 129-130); calculate_beta_fast masks/degenerate/nonfinite/LinAlgError/empty/min_obs (151, 163, 165-170); calculate_rolling_beta bench conversion/outer except/_finalize_betas (249-253, 343-347).
PROVE WITH COVERAGE (WORKING METHOD — do NOT use `coverage run -m pytest`; it crashes on numpy double-import in this env):
  cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
  python3 - <<'EOF'
  import glob, sys, coverage, pytest
  ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
  sys.path.insert(0, ROOT)
  files = sorted(glob.glob(ROOT + "/tests/test_bab_beta*.py") + glob.glob(ROOT + "/tests/test_beta*.py"))
  cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"])
  cov.start()
  rc = pytest.main(["-q"] + files)
  cov.stop()
  cov.report(show_missing=True, include=ROOT + "/strategies/betting_against_beta/beta.py")
  sys.exit(rc)
  EOF
ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
FULL SUITE MUST STAY GREEN. BAB SUITE MUST STAY GREEN (note: 2 pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are allowed; everything else must pass).
DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% starting with beta.py (biggest gap). Every turn must produce substantive test/logic changes that cover uncovered branches. No churn.

## VERIFIED GATES (CURRENT)
- Full suite: 1492 passed, 11 skipped, 2 failed (unrelated workflow pattern sync in controller_progress - pre-existing, ALLOWED)
- BAB suite: 1282 passed, 11 skipped (GREEN)
- BAB total coverage: ~96% overall; beta.py 89% (29 misses) - PRIMARY BOTTLENECK

## EXACT NEXT STEPS
1. Run the WORKING coverage driver above on beta.py; capture exact missing lines.
2. Identify 5-10 highest-value uncovered lines from term-missing (focus estimate_betas, calculate_beta, calculate_beta_fast, _calc_rolling_beta_series, calculate_rolling_beta).
3. Write REAL tests in existing test files (or minimal new test files) with concrete assertions hitting those exact branches. If a branch cannot be safely hit by tests without weakening invariants, fix the test strategy or add minimal safe defensive handling only if it matches existing BAB behavior.
4. Re-run focused coverage on beta.py. Repeat until beta.py >= 95%. Then reassess next bottleneck (data_loader.py 94%, quality.py 95%).
5. Before ending, run full BAB suite + full suite to confirm GREEN (only the 2 unrelated workflow sync failures may remain).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST. Heavy substantive work every session.
- Change smallest set of files needed. File count is NOT a metric.
- VERIFICATION BOTTLENECK REMOVED: `coverage run -m pytest` is broken here (numpy C-extension double-import). Use the inline coverage driver above instead. Never ship a gate you cannot run.
- If stall on beta.py (no new branch hitable safely), move to next highest leverage (data_loader.py/quality.py) with same rigor.
- Never leave gates red. If you make changes, verify gates immediately.
