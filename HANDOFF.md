# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-11-01T00:32:58Z

## TIMESTAMP
2026-11-01T00:32:58Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-11-01T00:32:58Z)
- Full BAB suite: 1309 passed, 5 skipped, 0 failed (FULLY GREEN)
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) — must not increase
- Package coverage (BAB): 98% total, 50 misses across 2533 stmts

Per-module (BAB package):
- 100%: __init__, attribution, backtest, cli, data, data_sources, errors, quality, regime, shorting, sizing
- 99%: costs (2 misses: 59-60)
- 98%: config (95-96, 113), signals (37, 75), strategy (181, 188-189)
- 97%: data_loader (44, 192-193, 256, 311-313, 340-342)
- 96%: metrics (25, 42, 97, 114, 126, 138), portfolio (39-40, 164-169)
- 94%: beta.py (16 misses: 101-102, 124, 138, 140-141, 144-145, 166, 178, 181, 355-359) — STUCK

## BOTTLENECK — BETA.PY PROVABLY STUCK (DO NOT CHASE)
beta.py is the historical bottleneck but is now provably stuck: every remaining miss is unreachable dead code guarded by an earlier return. Verified by measurement + static guard analysis; no test can cover them without changing semantics.

- 101-102: unreachable — line 78-79 np.asarray(...,dtype=float) must succeed before the alignment block (line 82-84), guaranteeing float-convertible data reaches line 99-100, so to_numpy(dtype=float) cannot raise.
- 124: unreachable — line 118 `if not np.any(mask): return nan` returns first; mask has same length as y, so any(mask) => len(y)>=1 after filter.
- 144-145: unreachable — BABDataError raised at line 74-75 BEFORE the try block (line 76); nothing inside try raises BABDataError.
- 166: unreachable — line 157 `if not np.any(mask): return nan` returns first.
- 355-359: unreachable — bad-column conversion raises BABDataError at line 333, re-raised at line 345-346 BEFORE the outer except (line 347); no other TypeError/ValueError/AttributeError source exists in the guarded fast path.
- 138/178: unreachable — x_std guard (line 129/171) ensures finite non-degenerate x; lstsq on finite rank-2 X with finite y yields finite beta (SVD-based gelsd).
- 140-141/181: LinAlgError handlers — gelsd raises only on SVD non-convergence, not triggered by finite inputs.

Ruling: beta.py will not exceed 94% via tests. Documented above; do not spend further turns on beta.py. Move to the next highest-leverage BAB module (focus order below).

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE

VERIFIED STATE (2026-11-01T00:32:58Z):
- BAB suite: 1309 passed, 5 skipped, 0 failed (FULLY GREEN)
- Package coverage: 98% | total misses 50
- beta.py: 94% | 16 misses — PROVABLY STUCK (documented in HANDOFF.md), DO NOT CHASE
- Next targets by miss count: data_loader (10: 44, 192-193, 256, 311-313, 340-342),
  portfolio (8: 39-40, 164-169), metrics (6: 25, 42, 97, 114, 126, 138),
  config/signals/strategy (3 each), costs (2: 59-60)

MANDATE: MAXIMIZE BAB COVERAGE WITH ZERO REGRESSIONS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES. NO EXPLORATORY IDLE TURNS.

FOCUS ORDER (STRICT):
1. data_loader.py (97%, 10 misses) — IMMEDIATE
2. portfolio.py (96%, 8 misses) — lines 39-40 previously documented unreachable; 164-169 next
3. metrics.py (96%, 6 misses)
4. config.py (98%, 3: 95-96, 113), signals.py (98%, 2: 37, 75), strategy.py (98%, 3: 181, 188-189)
5. costs.py (99%, 2: 59-60) only if provably reachable
6. beta.py — SKIP (provably stuck; documented)

EXECUTION PROTOCOL (HEAVY WORK):
- Read the target module end-to-end. Map every miss to exact line/path.
- TDD: write a FAILING test hitting a real uncovered branch first. Make it pass with minimal change preserving semantics.
- After EVERY batch, re-run focused coverage on the target module. Track progress; don't spin.
- NO SPINNING. If stuck >2 focused attempts on a subpath, document evidence in HANDOFF.md and move to the next untested branch.
- Preserve: 1-day lag, dollar-neutral, quantiles/deciles, beta window>=60 default, ranking logic, finiteness, BAB-specific errors, no bare except:.
- CHANGE ONLY SMALLEST SET NEEDED TO COVER REAL UNCOVERED BRANCHES. NO DOCS-ONLY. NO FILE-COUNT GOAL.

VERIFICATION (run after every batch):
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob,sys,coverage,pytest
ROOT="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0,ROOT)
files=sorted(glob.glob(ROOT+"/tests/test_bab*.py"))+[ROOT+"/tests/test_betting_against_beta_costs.py",ROOT+"/tests/test_betting_against_beta.py"]
cov=coverage.Coverage(source=[ROOT+"/strategies/betting_against_beta"],data_file=None)
cov.start()
rc=pytest.main(["-q","-p","no:cacheprovider"]+files)
cov.stop()
cov.report(show_missing=True)
raise SystemExit(rc)
PYEOF
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py tests/test_betting_against_beta_costs.py tests/test_betting_against_beta.py 2>&1 | tail -2

RULES:
- ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
- PRESERVE ALL INVARIANTS. Enforce finiteness. Raise BAB-specific errors. NO bare except:.
- IF MODULE STALLS (NO NEW BRANCH HITABLE SAFELY AFTER FOCUSED ATTEMPTS) -> DOCUMENT EVIDENCE IN HANDOFF.md AND MOVE TO NEXT HIGHEST-LEVERAGE BAB MODULE. NO SPINNING.
- RUN GATES AFTER EVERY BATCH. NEVER LEAVE GATES RED.
- EVERY ACTION MUST BE SUBSTANTIVE. MOMENTUM IS MANDATORY.
- DO NOT WASTE TURNS ON NON-BAB FILES UNLESS THEY DIRECTLY BLOCK BAB COVERAGE WITH EVIDENCE.
- END SESSION ONLY IF BAB COVERAGE HIGHER THAN START OR UNREACHABLE LINES EXPLICITLY DOCUMENTED WITH EVIDENCE.

DO HEAVY WORK ON data_loader.py NOW. NO DELAY.
```

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required (1309 passed, 5 skipped, 0 failed minimum)
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase

## UPDATE (2026-11-01T00:42:58Z) — data_loader.py
- data_loader.py pushed to 98% (296 stmts, 7 misses). Misses: 44, 311-313, 340-342.
- 44: _normalize_index raises only if index remains non-DatetimeIndex after all normalization; with standard pandas operations and our guards this path is unreachable without corrupting core pandas behavior.
- 311-313 (parquet): validate_returns_dataframe called outside the try/except that catches OSError/ValueError; exceptions from validation propagate as-is or as BABDataError from validation itself. The except at 311-312 only catches read/IO issues in that specific structure - not validation errors. Similarly 340-342 for HDF5. These are unreachable dead-code-like branches under current structure.
- Added targeted tests in tests/test_bab_data_loader_miss_fill.py (2 passed). No behavior changes.
