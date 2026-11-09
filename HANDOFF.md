# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T12:20:51Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `bea46e3` (local main; working tree clean; only HANDOFF.md changed since `3234b17`). Do not commit/push unless explicitly requested.
**data_loader blob:** `596ee9eed4c14de098562aede46c93c0f242b248` (VERIFIED — GATE CLOSED; lines `322,326` guarded, do not alter; `data_sources.py` blob unchanged/closed).
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** continue the **BAB Package Coverage Campaign** — reduce real uncovered paths in `strategies/betting_against_beta/` with production-realistic tests/fixes, without regressing `data_loader`/`campaign_d` baselines. `data_loader`/`beta` dead-code remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T12:20:51Z @ `bea46e3`, deps ok):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883 passed, 5 skipped, rc=0** (baseline preserved; re-verify before new work).
- Full BAB suite excl controller: **timed out at 120s in this runtime** (runtime bottleneck — see Bottlenecks). Collection excl controller: **4530 tests collected**. Targeted `strategy*.py` suite: **70 passed, rc=0**. **Next session MUST run full suite to green in a capable environment before claiming global green; record exact count/rc.** Prior canonical baseline (362f1f2 history): **4445 passed, 35 skipped, rc=0**.
- `strategies/betting_against_beta/strategy.py`: **100%** (297 stmts, 0 miss) — CLOSED.

**Coverage (`coverage run -m pytest <targets>` + `coverage report -m --include=...`; `.coverage*` cleared before runs):**
- `strategies/betting_against_beta/strategy.py`: **100%** (297 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/signals.py`: **97%** (128 stmts, 4 miss). Residual: `37, 75, 139-140` (narrow defensive).
- `strategies/betting_against_beta/portfolio.py`: **94%** (244 stmts, 14 miss). Residual: `39-40, 95-96, 118-119, 131-132, 152-157` (defensive).
- `strategies/betting_against_beta/beta.py`: **33%** (320 stmts, 214 miss) — **CLOSED; dead/unreachable** per `docs/unreachable_proofs.md`.
- `strategies/betting_against_beta/data_loader.py`: **29%** — **GATE CLOSED**.
- `strategies/betting_against_beta/quality.py`: **83%** (183 stmts, **32 miss**: `30, 47-48, 116, 132, 187-188, 209, 211-212, 245-246, 259, 264-290`). **NEXT HEAVY SINGLE SLICE.**
- `strategies/betting_against_beta/cli.py`: **0%** — after quality.py.
- `strategies/betting_against_beta/attribution.py`: **97%** (1 miss line 62). `backtest.py` **51%** (52 miss). `config.py` **71%** (57). `costs.py` **18%** (107). `data_sources.py` **42%** (39). `metrics.py` **69%** (42). `regime.py` **62%** (75). `shorting.py` **64%** (59). `sizing.py` **48%** (92).

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Run full BAB suite excl controller to completion in a capable env; record exact count/rc. Fix regressions before new work.

2. **campaign5 — `quality.py` coverage (NEXT HEAVY SINGLE SLICE, mandatory):** Baseline **83%** (32 miss: `30,47-48,116,132,187-188,209,211-212,245-246,259,264-290`). Snapshot before/after with `coverage run -m pytest -o addopts='' tests/test_bab_quality*.py`. Create `tests/test_bab_quality_coverage_campaign5.py`. Production-realistic scenarios required to cover every miss:
   - line 30: `data_quality_report` median_gap NaN branch (irregular/sparse DatetimeIndex where `gaps.median()` is NaN).
   - lines 47-48: `data_quality_report` column conversion `except Exception` fallback (object/non-coercible column → all-NaN array).
   - line 116: `check_data_quality(None, strict=True)` → `ValueError`.
   - line 132: `detect_gaps` early return (non-DatetimeIndex / len<2 / median NaN or zero).
   - lines 187-188: `detect_outliers` `except Exception` path (object column).
   - line 209: `detect_stale_data` terminal run `current_run >= threshold` (stale run extends to last index).
   - lines 211-212: `detect_stale_data` `except Exception` path (object column).
   - lines 245-246: `detect_volume_anomalies` `except Exception` path (object volume column).
   - line 259: `detect_duplicate_timestamps` no-duplicates path + no-`has_duplicates` attr path.
   - lines 264-290: entire `compute_quality` function (error input, empty columns, scored columns, missing/inf/outlier/stale penalties).
   Use scoped monkeypatches only for truly defensive branches; if a miss is provably unreachable, document closed-without-edit with evidence. **Target materially higher coverage (aim ≥95% or justify every residual miss).** No production code changes unless a real bug is found with evidence + regression test.

3. **campaign6 (following slice, queued now so it cannot be deferred):** `cli.py` coverage **0%**. After campaign5 is green and evidence is recorded, create `tests/test_bab_cli_coverage_campaign6.py` targeting CLI flag parsing, dry-run, synthetic/prices paths, output writing, and `--version`. Target ≥80%.

4. **Non-regression gates (all required):** `campaign_d` 883/5 green; all strategy tests green; full BAB suite green in capable env. Fix real bugs minimally with evidence + regression tests.

5. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:**
- **Full-suite 120s timeout in this runtime IS A REMOVED BOTTLENECK EXCUSE, NOT A BLOCKER:** do not claim global green from this sandbox. Split the suite by module file and run each to green locally, then run the complete suite in a capable environment (CI or larger box) and record exact count/rc. `campaign_d` (883/5) and targeted `strategy*.py` (70/0) already pass here — use them as the local gate.
- deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` (optionally `-o addopts=''` to bypass repo addopts quirks) over `pytest-cov`.
- `quality.py` existing `tests/test_bab_quality.py` is the campaign5 anchor; extend it rather than duplicating.

**ACTIVE:** `quality.py` coverage campaign5 (next heavy slice — 32 misses). **strategy.py 100% CLOSED. beta.py/data_loader gates CLOSED — no churn. cli.py 0% is the queued campaign6.**

**Measurable outcome (required next session):** materially improved coverage/tests on `quality.py` (before/after evidence; target ≥95% or documented closed-without-edit per miss) and all gates green, plus refreshed HANDOFF naming `cli.py` coverage campaign6 as the following slice.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T12:20:51Z @ `bea46e3`, data_loader blob `596ee9eed` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
