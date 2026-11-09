# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T10:02:30Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta)
**HEAD:** 066192a (origin/main synced context)
**data_loader blob:** 596ee9e (UNCHANGED - GATE CLOSED)
**Status:** Environment blocker in this runtime (pytest/numpy/pandas/scipy missing for /usr/bin/python3). **Do not stop at planning.**

**MISSION:** Drive significant BAB package coverage progress. Focus on uncovered paths in `strategies/betting_against_beta/` with real tests/fixes, no data_loader churn, no workflow edits, no tracked probe/debug edits.

**IMMEDIATE ACTIONS (in order):**
1. **Unblock env** - Run in environment with deps: `export PYTHONPATH=$PWD && rm -f .coverage .coverage.* && python -m pytest --version && python -c "import numpy,pandas,scipy,pytest"`
2. **Establish baseline** - `python -m pytest -q --ignore=tests/test_controller_progress_accounting.py` (expect ~4367 passed, 35 skipped). `python -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` (expect 883/5/3514).
3. **Measure coverage gaps** - Target `backtest.py` (28 miss/74%), `beta.py` (28 miss/91%), `regime.py` (11 miss/94%). Run coverage on those modules.
4. **Finish backtest.py** - This session added `tests/test_bab_backtest_coverage_campaign2.py` and a minimal defensive fix in `backtest.py` (forward-fill bad cumulative entries only). Validate it in proper env; close remaining uncovered lines with production-realistic tests.
5. **Continue campaign** - After backtest.py green with delta, do `beta.py` then `regime.py`. Keep changes minimal and semantic-correct.
6. **Verify gates** - Full BAB (excl controller) green, campaign_d unchanged/green. Update HANDOFF with evidence.

**RULES:** No data_loader probe/gate churn; don't touch `322,326` in data_loader; don't edit `.github/workflows/*`; don't edit tracked `probe*/debug*/ast_probe.py`; don't commit/push unless asked.

**CONTEXT:** See HANDOFF.md §"START HERE" for full details. `docs/unreachable_proofs.md` has evidence.

---

# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T10:00:39Z** @ workspace `main` (`HEAD 066192a`, `origin/main` synced in this checkout context; `git status --short` clean before this session's changes — this session adds `tests/test_bab_backtest_coverage_campaign2.py` and a minimal `backtest.py` defensive fix; **do not commit/push unless explicitly requested**). `strategies/betting_against_beta/data_loader.py` blob **596ee9e** (unchanged, verified). `docs/unreachable_proofs.md` is the evidence appendix. **Repo-name priority = Betting Against Beta.** `data_loader.py` target-miss floor is **GATE-CLOSED** (B103–B192; no new strict-4 mechanism; do not churn). **Significant progress continues via BAB Package Coverage Campaign.** **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Baseline (last verified 2026-11-09T09:50Z, prior session):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`. Full BAB suite (excl. controller): `python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py` → **4367 passed, 35 skipped, 237 warnings, `rc=0`**. Campaign scope: `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3514 deselected, 53 warnings, `rc=0`**. `data_sources.py` **100% (CLOSED)**. `322,326` in `data_loader.py` is **LIVE/GUARD — DO NOT ALTER**. `data_loader` coverage remains gate-closed; do not churn it.

> **Bottleneck status (2026-11-09T10:00Z, this session):** **ENVIRONMENT BLOCKER (not a repo logic blocker).** This runtime has no `pytest`/`numpy`/`pandas`/`scipy` importable for `/usr/bin/python3` (and no usable pytest in discovered hostedtoolcache/miniconda paths). **Step 0 baseline rerun and new-test execution could not be performed here.** The next agent must run in the project test environment (deps installed) and complete the gates below. Any session that exits with planning-only output is **inefficient and unacceptable** once deps are available.

## Bottlenecks — RESOLVED / REMOVED / ACTIVE (do not reintroduce resolved ones)

Cleared and forbidden as excuses: scratch/probe clutter (tracked `debug_beta*`/`probe*`/`ast_probe.py` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility when deps exist (`coverage`/`pytest` via `python -m`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (`--rcfile=/dev/null --source=strategies.betting_against_beta`), canonical batch-set drift (enumerate explicitly), parquet/hdf5 engines (monkeypatch read APIs/call sites as needed), **and data_loader 0-delta gate churn** (B103–B192 exhausted; `data_loader.py` floor is baseline/unreachable per recorded evidence — **no more probe/gate-only sessions on data_loader without a concretely demonstrated, non-repeat strict-4 mechanism discovered from a production bug/feature need**).

**ACTIVE (2026-11-09T10:00Z):** missing `pytest`/`numpy`/`pandas`/`scipy` in this execution runtime. Unblock by running in the normal CI/dev environment for this repo (where `python -m pytest` and project deps are available). Minimal repro: `python3 -m pytest --version` → `/usr/bin/python3: No module named pytest`; `python3 -c "import numpy,pandas,scipy"` fails with `ModuleNotFoundError: No module named 'numpy'`.

## Session progress (BAB package coverage campaign)

| Date (UTC) | Module | Before (module miss/%) | After (module miss/%) | Tests / evidence | Gates |
|---|---|---:|---:|---|---|
| 2026-11-09T07:38Z (prior) | `cli.py` | 48 / 85% | 2 / 99% | `tests/test_bab_cli_coverage_push.py` (+25) | campaign_d 883/5/3444; no data_loader/probe edits |
| 2026-11-09T07:53Z (prior) | `strategy.py` | 37 / 88% | **7 / 98%** | `tests/test_bab_strategy_coverage_campaign.py` (**23**) + minimal `_np.where` fix | canonical preserved; campaign_d green |
| 2026-11-09T08:45Z (prior) | `signals.py` + `portfolio.py` | signals 72/128/44%; portfolio 66/244/73% | signals 19/128/85%; portfolio 44/244/82% | +47 tests | full BAB 4367/35; campaign_d 883/5/3514 |
| 2026-11-09T09:19Z (prior) | baseline + bottleneck removal | — | `data_sources.py` **100% (CLOSED)** | full BAB 4365/35/2d `rc=0`; campaign_d 883/5/3514 | stale coverage claim removed |
| **2026-11-09T10:00Z (this session)** | **`backtest.py` (code + tests added; gates BLOCKED by env)** | **28 miss / 109 stmts / 74%** (09:19Z targeted evidence: 15,17,103-108,116-117,122-125,130,133-149) | **PENDING MEASUREMENT (run Step 0 + targeted coverage in proper env)** | Added `tests/test_bab_backtest_coverage_campaign2.py` (production-realistic DataFrames + scoped monkeypatches for defensive fallback branches: tc/slippage aliases, modeled `TransactionCostModel` path, nonfinite log/exp/cumprod repairs, hardening exceptions, final sanitization). **Minimal real defensive fix** in `backtest.py` cumulative fallback (lines ~137-147): removed dead `np.where(..., 1.0 if False else 1.0, 1.0)` overwrite + redundant `if np.any(bad)` that would reset *all* finite cumulative values to 1.0 on any non-finite; now forward-fills only bad entries. `py_compile` OK on modified files. **No pytest/numpy/pandas/scipy available in this runtime → tests/gates not executed.** | **BLOCKED in this runtime:** cannot verify full BAB (expected 4367/35 baseline) or campaign_d (883/5/3514). data_loader blob unchanged; `322,326` untouched; no workflows/probes touched. |

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T10:02:41Z (BAB Package Coverage Campaign, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** deliver **significant, production-relevant BAB package progress** by reducing real uncovered paths in `strategies/betting_against_beta/` **without** regressing data_loader/campaign_d baselines. `data_loader.py` miss-floor work is **GATE-CLOSED**.

**Current state (HEAD 066192a, data_loader blob 596ee9e):** prior verified baseline (09:50Z) full BAB **4367 passed, 35 skipped, `rc=0`**; campaign_d **883/5/3514, `rc=0`**. This session added `tests/test_bab_backtest_coverage_campaign2.py` and a minimal defensive fix in `backtest.py` (cumulative fallback now forward-fills only bad entries; no overwrite of valid values). **Gates are not re-verified in this runtime due to missing deps.** Highest-value slices remain `backtest.py` → `beta.py` → `regime.py`. **Future agents must produce heavy engineering output (tests/fixes/evidence), not status narration.**

### Residual uncovered lines (prior evidence; re-measure before edits)

**`backtest.py` (28 misses, 74%, 09:19Z):** 15,17,103-108,116-117,122-125,130,133-149. Cover lagged weights/no-lookahead, tc/slippage aliases, `TransactionCostModel` path, turnover/cost/slippage drag, cumulative/log/exp fallback, and empty/NaN/degenerate/non-finite guards with production-realistic data.

**`beta.py` (28 misses, 91%):** 101-102,124,143,145-146,149-150,162,169-170,188,210,212-218,356-359,429-433.

**`regime.py` (11 misses, 94%):** 301-315.

### Forced steps (execute in order; heavy work required)

1. **Step 0 — fresh baseline in proper env (mandatory):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; `python -m pytest -q --ignore=tests/test_controller_progress_accounting.py` → expect **4367 passed, 35 skipped, `rc=0`** or explain delta with evidence; `python -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883/5/3514, `rc=0`**. Capture targeted before-coverage for `backtest.py,beta.py,regime.py`: `python -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_backtest*.py tests/test_bab_beta*.py tests/test_bab_regime*.py` (adjust to narrowest meaningful set) then `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/backtest.py,*/strategies/betting_against_beta/beta.py,*/strategies/betting_against_beta/regime.py' --show-missing`. Record exact miss/stmts/% before further edits.
2. **Validate this session's `backtest.py` fix + `test_bab_backtest_coverage_campaign2.py`:** run targeted `python -m pytest -q tests/test_bab_backtest*.py` and the coverage report for `backtest.py`; confirm before/after delta vs 09:19Z/Step 0. If any new test is invalid/flaky, fix the test (not production semantics) unless a real bug is proven.
3. **Continue heavy work:** after `backtest.py` delta is evidenced and green, ship real tests for remaining `backtest.py` misses, then `beta.py`, then `regime.py`. Use `tmp_path`/monkeypatch/controlled DataFrames; no semantic production changes solely for coverage. Add/extend narrowest targeted test files (e.g. `test_bab_beta_coverage_campaign2.py`).
4. **Non-regression gates (all required):** full BAB suite (excl. controller) green; `campaign_d` green (**883/5/3514**); touched-module tests green. Fix failures caused by new tests; minimally fix real bugs with evidence/regression tests.
5. **Handoff update (durable):** refresh this HANDOFF with timestamp/SHA/blob, exact Step 0 + final commands/counts, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep it single-file canonical.
6. **Forbidden:** data_loader probe/gate churn without a new strict-4 mechanism; semantic production changes solely for coverage; altering `322,326` in `data_loader.py`; weakening/deleting batch148/149/172 or `campaign_d*`; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** materially improved coverage/tests on `backtest.py` (and/or `beta.py`/`regime.py`) with all gates green and before/after evidence, **plus** refreshed HANDOFF naming the following slice — **OR** **(B)** a concrete, evidence-backed blocker with minimal reproduction and the exact unblocked next action. This session reports **(B) environment blocker** plus real code/test artifacts added; next session must achieve **(A)** in a proper environment.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T10:00:39Z** @ `066192a` / data_loader blob `596ee9e` verified; **data_loader gate closed; `data_sources.py` 100% CLOSED.** This session added `tests/test_bab_backtest_coverage_campaign2.py` and a minimal `backtest.py` cumulative-fallback defensive fix (forward-fill only bad entries; no valid-value overwrite) — **not gate-verified here due to missing pytest/numpy/pandas/scipy**. Next focus = validate/finalize `backtest.py` delta → `beta.py` (91%, 28 miss) → `regime.py` (94%, 11 miss).
