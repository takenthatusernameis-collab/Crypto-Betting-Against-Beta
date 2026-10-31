# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-31T14:34:24Z

## TIMESTAMP
2026-10-31T14:34:24Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## BOTTLENECKS REMOVED (THIS SESSION)
- The 2 workflow-pattern-sync failures in tests/test_controller_progress_accounting.py (test_python_patterns_are_subset_of_workflow, test_nested_workflow_pattern_is_present_in_workflow) REGRESSED (workflow lost `*/.github/workflows/*`) and are FIXED AGAIN. Added `*/.github/workflows/*` to .github/workflows/main.yml:1163 stage_safe_changes case list to match scripts/controller_progress.py EXCLUDE_PATTERNS (which has both `.github/workflows/*` and `*/.github/workflows/*`).
- Full suite is now 100% GREEN: 1652 passed, 11 skipped, 0 failed. No allowed failures remain.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T14:34:24Z)
- Full suite: 1652 passed, 11 skipped, 0 failed (FULLY GREEN; bottleneck removed)
- BAB suite (tests/test_bab*.py): 1126 passed, 5 skipped, GREEN
- data_loader.py: 97% (296 stmts, 10 miss) — TARGET >=97% MET NUMERICALLY, remaining misses: 44, 192-193, 256, 311-313, 340-342 (attempt or document as provably unreachable)
- quality.py: 92% (183 stmts, 14 miss) — PRIORITY #1 (>=93 required; currently 2 points short)

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (CLEAN MEASUREMENT - 2026-10-31T14:34:24Z):
- Full suite: 1652 passed, 11 skipped, 0 failed (FULLY GREEN; bottleneck removed)
- BAB suite (tests/test_bab*.py): 1126 passed, 5 skipped, GREEN
- data_loader.py: 97% (10 misses: 44, 192-193, 256, 311-313, 340-342)
- quality.py: 92% (14 misses: 3-11, 110, 124, 132, 145, 192, 216, 250, 259-262)

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

TARGETS (NON-NEGOTIABLE):
- quality.py >= 93% (hit remaining real branches: 110, 124, 132, 145, 192, 216, 250, 259-262)
- data_loader.py >= 97% maintained; attack 44, 192-193, 256, 311-313, 340-342 or document provably unreachable
- BAB TOTAL >= 97% with chain intact
- tests/test_bab*.py: 100% GREEN. Full suite: 0 failures allowed.

EXACT UNCOVERED LINES (RUN VERIFICATION BEFORE CLAIMING PROGRESS):
- quality.py (92%, 183 stmts, 14 miss): 3-11 (imports/module setup - SKIP unless provably hittable), 110, 124, 132, 145, 192, 216, 250, 259-262
- data_loader.py (97%, 296 stmts, 10 miss): 44, 192-193, 256, 311-313, 340-342

FOCUS ANALYSIS (quality.py):
- 110: `if report.get("error"):` in check_data_quality - call check_data_quality with a non-DataFrame/None input so data_quality_report returns {"error": ...} and the error branch executes (try strict=True too).
- 124: def detect_gaps - call detect_gaps on a DataFrame with a DatetimeIndex; cover median_gap == 0 / pd.isna(median_gap) early return and the large-gap branch.
- 132: `median_gap == 0` branch in detect_gaps - index with repeated identical timestamps (zero median gap).
- 145: def detect_outliers - call with zscore and iqr methods; cover std_f == 0, len(finite_arr) < 3, unknown method.
- 192: def detect_stale_data - call with columns containing consecutive equal finite values >= threshold, and runs shorter than threshold.
- 216: def detect_volume_anomalies - call with a volume-named column; cover median == 0 branch and anomaly ratios.
- 250: def detect_duplicate_timestamps - call with a DatetimeIndex that has duplicates (dup_mask path, line 255-256).
- 259-262: `return {"has_duplicates": False, "count": 0}` path (no has_duplicates attr or no dups) — likely covered via no-dup index; verify.

FOCUS ANALYSIS (data_loader.py):
- 44: _normalize_index after tz/localize still not DatetimeIndex -> raise BABDataError. Index that becomes non-datetime after coercion attempts.
- 192-193: _coerce_numeric outer except (ValueError, TypeError, AttributeError) fallback.
- 256: benchmark all-NaN finite check - validate_returns_dataframe with benchmark whose column has no finite values.
- 311-313, 340-342: parquet/hdf5 outer except (OSError, ValueError) - inner converts Exception->BABDataError first so these may be unreachable; verify, if truly unreachable document and move on.

VERIFICATION METHOD (USE EXACTLY THIS — AVOIDS NUMPY C-EXTENSION ISSUES & FULL-COV TIMEOUTS):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob, sys, coverage, pytest
ROOT = "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0, ROOT)
for mod, pat in [("quality", "tests/test_bab_quality*.py"), ("data_loader", "tests/test_bab_data_loader*.py")]:
    files = sorted(glob.glob(ROOT + "/" + pat))
    cov = coverage.Coverage(source=[ROOT + "/strategies/betting_against_beta"], data_file=None)
    cov.start()
    rc = pytest.main(["-q", "-p", "no:cacheprovider"] + files)
    cov.stop()
    print("="*60)
    print(f"COVERAGE: {mod}")
    cov.report(show_missing=True, include=ROOT + f"/strategies/betting_against_beta/{mod}.py")
    if rc != 0:
        sys.exit(rc)
PYEOF
# Gate 1: focused BAB module tests must stay green
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py
# Gate 2: full suite must be 0 failures
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider 2>&1 | tail -4
```

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- CHANGE ONLY THE SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES.
- PRESERVE: 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF A MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE WITH SAME RIGOR AND HEAVY WORK. NO SPINNING.
- RUN GATES AFTER CHANGES. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.

FOCUS ORDER (STRICT):
1. strategies/betting_against_beta/quality.py (push 92% -> >=93%) - Focus on 110, 124, 132, 145, 192, 216, 250, 259-262. Skip 3-11 (imports) unless provably hittable.
2. strategies/betting_against_beta/data_loader.py (hold >=97%) - Attack 44, 192-193, 256; document 311-313/340-342 if provably unreachable.
3. Any other BAB module if both stall on truly unreachable lines.

HEAVY-WORK FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID THIS):
- Each session must end with coverage strictly higher than it started, OR explicit evidence that remaining lines are provably unreachable (documented in this handoff).
- No session may end with gates red. If gates go red, the very next turn fixes them before any new coverage work.
- quality.py must reach >=93% before any non-BAB work is considered.
- Write a failing test first (TDD), then the minimal test/logic to make it green against existing correct behavior. Never add assertions-free tests.
- Re-run focused coverage + BAB suite after EVERY batch. If coverage is flat after hitting obvious paths, explicitly call out unreachable vs missed and move to the next module.

DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% with zero regressions. Prioritize quality.py (92% -> >=93%) then hold data_loader.py >=97% and attack/document remaining misses. Hit only real hitable branches. Every turn must produce substantive test/logic changes. Focus on the specific missing lines identified above.

## VERIFIED GATES (CURRENT - 2026-10-31T14:34:24Z)
- data_loader.py: 97% (10 misses: 44, 192-193, 256, 311-313, 340-342)
- quality.py: 92% (14 misses: 3-11, 110, 124, 132, 145, 192, 216, 250, 259-262)
- BAB suite (tests/test_bab*.py): 1126 passed, 5 skipped, GREEN
- Full suite: 1652 passed, 11 skipped, 0 failed (FULLY GREEN; bottleneck removed)

## EXACT NEXT STEPS (CHAINED)
1. **IMMEDIATE (quality.py)**: Run the exact verification method. Focus on 110, 124, 132, 145, 192, 216, 250, 259-262 — add precise tests calling check_data_quality, detect_gaps, detect_outliers, detect_stale_data, detect_volume_anomalies, detect_duplicate_timestamps against real hitable branches.
2. **ITERATE**: After each batch, re-run focused coverage + BAB suite. If coverage flat after hitting obvious paths, explicitly call out unreachable vs missed and move to data_loader.py.
3. **data_loader.py**: Hold >=97%; attack 44, 192-193, 256 or document provably unreachable.
4. **FINAL GATE**: Before ending session, run BAB suite (must be GREEN) and full suite (0 failures). Update this handoff only if genuinely new bottlenecks discovered and removed.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required
