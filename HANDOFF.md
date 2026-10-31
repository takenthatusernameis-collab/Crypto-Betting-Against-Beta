# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T06:00:58Z

## TIMESTAMP
2026-10-31T06:00:58Z

## INITIAL TASK MESSAGE FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/beta.py | REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE
beta.py coverage is 91% (289 stmts, 27 miss). CRUSH remaining UNCOVERED BRANCHES.
TARGET: beta.py >= 95% | BAB TOTAL >= 97%.
DO NOT TOUCH FILES FOR VANITY. CHANGE ONLY SMALLEST SET NEEDED FOR REAL UNCOVERED BRANCHES.
HIT HARD LINES (current missing): 66-67, 114, 124, 138, 140-141, 144-145, 166, 178, 180-185, 264-268, 358-362.
FOCUS AREAS: rolling_beta fallthrough paths (n==0/final excepts), calculate_beta y/None/empty/degenerate/LinAlgError/nonfinite beta, calculate_beta_fast empty/min_obs/degenerate/LinAlgError/outer excepts, calculate_rolling_beta bench_arr conversion excepts (264-268), outer except fallback path (358-362).
PROVE WITH COVERAGE (WORKING METHOD — do NOT use `coverage run -m pytest`; it crashes on numpy double-import and the full suite times out on perf tests):
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
ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
BOTTLENECK STATUS: vanity defensive try/except wrappers added in last checkpoint commit were removed (restored beta.py to 289 stmts / 91% coverage). Deps (numpy/pandas/pytest/coverage) installed in user site-packages; use PYTHONPATH above. Tests added (test_beta_gap_hunt*.py, test_beta_precise_missing.py) to accelerate hitting branches.
FULL SUITE MUST STAY GREEN. BAB SUITE MUST STAY GREEN (note: 2 pre-existing unrelated workflow-pattern-sync failures in test_controller_progress_accounting.py are allowed; everything else must pass).
DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% starting with beta.py (biggest gap). Every turn must produce substantive test/logic changes that cover uncovered branches. No churn. BAB-first per repo name (betting_against_beta).

## VERIFIED GATES (CURRENT)
- beta.py: 91% (289 stmts, 27 miss) — PRIMARY BOTTLENECK; missing: 66-67, 114, 124, 138, 140-141, 144-145, 166, 178, 180-185, 264-268, 358-362
- BAB beta-focused suite (bab/beta, excl. perf): 382 passed, GREEN in ~2.7s
- Full suite: 1566 passed, 11 skipped, 2 failed (unrelated workflow pattern sync in controller_progress - pre-existing, ALLOWED)
- BAB total coverage: ~96% overall; beta.py 91% — PRIMARY BOTTLENECK

## EXACT NEXT STEPS
1. Run the WORKING coverage driver above on beta.py; capture exact missing lines.
2. Hit each missing branch with precise tests. For rolling_beta fallthrough (66-67), construct objects where both _calc_rolling_beta_series paths fail after trying series/DataFrame-like conversions - may need to make np.asarray/len fail in specific order.
3. For calculate_beta (114, 124, 138, 140-141, 144-145): force y is None (114), empty after mask (124), nonfinite beta from lstsq (138), LinAlgError (140-141), ensure BABDataError re-raise path (144-145) is covered.
4. For calculate_beta_fast (166, 178, 180-185): cover empty after mask, nonfinite beta, LinAlgError and TypeError/ValueError/AttributeError in inner/outer excepts.
5. For calculate_rolling_beta (264-268, 358-362): force bench_arr conversion to fail to second except and raise BABDataError (264-268); force bad asset path in outer except to raise BABDataError (358-362).
6. Re-run focused coverage on beta.py until >= 95%. Then reassess next bottleneck (data_loader.py 94%, quality.py 95%).
7. Before ending, run full BAB suite + full suite to confirm GREEN (only the 2 unrelated workflow sync failures may remain).

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST. Heavy substantive work every session.
- Change smallest set of files needed. File count is NOT a metric.
- VERIFICATION BOTTLENECK REMOVED: `coverage run -m pytest` is broken here (numpy C-extension double-import) and the full suite times out on perf tests. Use the inline coverage driver above (excludes perf tests, runs ~2.5s). Dependencies installed.
- If stall on beta.py (no new branch hitable safely), move to next highest leverage (data_loader.py/quality.py) with same rigor.
- Never leave gates red. If you make changes, verify gates immediately.
