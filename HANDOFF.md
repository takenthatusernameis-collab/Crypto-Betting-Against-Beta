# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T04:20:44Z @ `9d8ea39`, refreshed after Batch 140; Batch 142 initial task message below is binding). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` miss floor.** Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 142** immediately. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Batch status (this session)

- **Batch 140 (@ `ed0fda2`):** COMPLETED — state confirmed only, 0 delta. Canonical aggregate 1496/0/17, **35 miss / 1683 stmts / 98%**, guard 44/5. No new production-realistic mechanism found; `docs/unreachable_proofs.md` batch139 appendix already recorded the non-production 351–352 boundary trace. Batch 140 produced **no miss reduction**.
- **Batch 141 (@ `d97339d`, this session):** COMPLETED — materially-new **cross-module contract audit** executed (AST caller map + `sys.settrace` end-to-end `BABStrategy.run` trace, 12 run shapes + 3 public-entrypoint shapes): **0 target-line hits** on all 35 misses. Canonical aggregate **1496/0/17, 35 miss / 1683 stmts / 98%**, guard **44/5**. **Delta 0; no miss reduction.** Complete Batch141 non-repeat materially-new appendix appended to `docs/unreachable_proofs.md` covering all remaining clusters with strict 4-criteria verdicts; HANDOFF ledger updated with measured results. `322,326` preserved; no semantics/workflow changes.

## Measured state (fresh rebaseline, 2026-11-08T04:20:44Z @ `9d8ea39`)

- **Branch/SHA:** `main` @ `d97339d` (`data_loader.py` unchanged since `e945fde` for miss line→code; two checkpoint commits `4b108ba`/`d97339d` ahead of `9d8ea39` do not touch `data_loader.py`; floor SHA `24db195`). Working tree clean; local scratch/untracked probes (`probe*`, `debug_beta*`) are `.gitignore`d — do not commit unless requested.
- **Canonical aggregate (fresh rebaseline, 2026-11-08T05:06Z @ `d97339d`, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1496 passed, 0 failed, 17 skipped, 109 warnings** (25.16s).
- **Coverage (`--rcfile=/dev/null`, `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings** (0.41s). **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest`, `coverage`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — all removed/routed (verified 2026-11-08T04:20:44Z)

| # | Bottleneck | Route | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; never commit probes. | Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** | Routed |
| 3 | Deps fragility | `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; install there only if missing. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect/caller behavior and campaign_d behavior. **Never alter `322,326` semantics.** | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96** (no 70,75,90-92,94). Reconcile in Step 0 if needed. | Routed |
| 10 | Repeated 0-delta inefficiency | Batches 103–139 mechanism-closed/probed; Batch 140 state-confirmed only. **No repeat probes.** 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed. Blockers eliminated: scratch clutter ignored, controller test excluded, deps pinned via pylib, coverage DB cleaned each run, path filtering fixed, missing engines handled, aggregate sensitivity scoped, `322,326` preserved, canonical batch set pinned, 0-delta repeats forbidden.

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–139) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer never returns NaT (raises); 224 completion => 225 false; element failure re-raises at 223. B138 L/N; B139 re-confirmed. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 raises/re-raises `BABDataError`; 266 catches before 268; `BABDataError⊂ValueError`. B138 K; B139 re-confirmed. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | **Closed for production-realistic scalars:** unmodified numpy 0 hits; reachable only by monkeypatched `np.isnan` raising non-`ValueError` (non-production boundary, criterion 3 fails — B139 C). |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | **Closed:** re-raise before generic pass. B138 L; B139 re-confirmed. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed:** regex-admitted strings + builtin float/guarded branches. B138/B139 re-confirmed. |
| `_not_null` outer except | `43-44` | **Closed (structural).** |
| `_normalize_asset_name` empty token continue | `953` | **Closed:** `str.split()` cannot yield `''`. AST proof B139 A. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames:** inner guards swallow. B138/B139 re-confirmed. |
| `_promote_datetime_column` outer handler | `791-792` | **Closed:** 760–790 individually guarded. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–139 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## INITIAL TASK MESSAGE — 2026-11-08T05:11:44Z (Batch 142) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `9d8ea39`. **Fresh baseline (measured this session):** 1496/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. `data_loader.py` unchanged since `e945fde`; Batch 140 measured at `ed0fda2` produced 0 delta / no miss reduction. **No baseline-only/review-only/planning-only/status-only exit.**

### Mission (binary, both acceptable as heavy work; primary preferred)

1. **Primary:** Push `data_loader.py` **below 35 miss** in a fresh canonical aggregate via a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all 4 criteria on a real `DataFrame`/index/dtype/column-label/file-format path. No semantic changes. Preserve `322,326`. Implement as `tests/test_bab_data_loader_batch141.py`, run focused → guard → fresh canonical aggregate including batch141, record measured delta.
2. **Fallback (only after exhaustive new-method work on all 10 clusters):** Add genuinely new unreachable-proof evidence to `docs/unreachable_proofs.md` using a **materially new method** not recorded in B103–140. Required: per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict for **every** remaining cluster. Do not repeat disproven mechanisms. Append Batch141 appendix and update HANDOFF/ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–140 disproven mechanisms), semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 141 materially-new methods (use ≥1 substantively; record commands/cases/outcomes)

- **Cross-module contract audit (not yet recorded):** `grep`/AST all `strategies.betting_against_beta` callers of loader public/private helpers; exercise untested real-pipeline shapes (`beta`, `signals`, `portfolio`, `backtest`, `metrics`, `cli`, `strategy`) and trace. Document per-caller shape and outcome.
- **Hypothesis stateful fuzz on `BABStrategy.run` end-to-end:** randomized universes/beta windows/quantiles/transaction costs through the full pipeline (`strategy.py` entrypoint) with `deadline=None`; trace loader line hits; any target-line hit under realistic inputs is a candidate 4-criteria path.
- **pandas 3.1.1 parser seams beyond recorded orientations:** `read_csv`/`read_json` with `dtype_backend`, `engine="python"`, file-like/Path/BytesIO/`StringIO` objects, malformed-but-plausible file content (mixed delimiters, embedded headers, quoted NaN markers, BOM/TSV/gzip already partly covered — extend to exotic encodings and multi-index JSON), public loader entrypoints only.
- **NumPy 2.5.4 scalar-dispatch audit (non-pathological):** `np.float64`/`np.float32`/`np.longdouble`/`np.int64` NaN/inf/epoch through coercer gates and `_strip_units_and_parse`; `np.datetime64` units (ns/us/ms/s/D); verify no non-`ValueError` escape to 351–352 under unmodified NumPy (criterion 3). Record per-dtype outcome.
- **Downstream-consumption trace:** `BABStrategy.run(returns_df=dl.load_returns(...))` / `load_prices` with realistic exchange-like frames (OHLCV with symbol/close_time, long-format pivot, multi-asset wide) through full strategy pipeline; trace loader misses hit downstream.
- **Exception-origin audit with plausible single monkeypatch:** monkeypatch one seam corresponding to plausible library behavior (e.g. `pd.DatetimeIndex`/`pd.to_datetime` raising under realistic malformed index after normalization); document why plausible; `sys.settrace` hits count only if criterion 3 holds.
- If a concrete 4-criteria path is found, implement as `tests/test_bab_data_loader_batch141.py` and verify in fresh canonical aggregate.

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py tests/test_bab_data_loader_batch78.py tests/test_bab_data_loader_batch79.py tests/test_bab_data_loader_batch80.py tests/test_bab_data_loader_batch81.py tests/test_bab_data_loader_batch82.py tests/test_bab_data_loader_batch83.py tests/test_bab_data_loader_batch84.py tests/test_bab_data_loader_batch85.py tests/test_bab_data_loader_batch86.py tests/test_bab_data_loader_batch87.py tests/test_bab_data_loader_batch88.py tests/test_bab_data_loader_batch89.py tests/test_bab_data_loader_batch93.py tests/test_bab_data_loader_batch95.py tests/test_bab_data_loader_batch96.py
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 35 miss / 1496/0/17 / guard 44/5.

### Forced campaign (no early exit)

For each cluster `234-244,246-247`, `268-269`, `351-352`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only):
1. Verify file:line at current SHA (`9d8ea39`).
2. Apply strict 4 criteria. If all 4 met: create `tests/test_bab_data_loader_batch141.py`, run focused → guard → fresh canonical aggregate including batch141, record measured delta.
3. If not: run ≥1 materially-new Batch 141 check (from the method list above, not a B103–140 repeat), document method/result, append Batch141 appendix to `docs/unreachable_proofs.md`.
4. Never repeat B103–140 disproven mechanisms.
5. Every cluster must end the session with either a 4-criteria verdict or a recorded materially-new-method proof — **no cluster may be left unevaluated**.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete Batch141 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering **all** remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | canonical aggregate included campaign_d_core tests; **35/1683**, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable/JSON-orient/tz/index/coercer evidence; 0 hits. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence; 0 hits. |
| 139 | `24db195` | 0 | heavy proof | 1496/0/17, 35/1683, guard 44/5 (measured). AST/MRO/coercer static proofs; pandas 3.1.1 public-loader/downstream `sys.settrace` 0 target hits; 351–352 hit only via monkeypatched `np.isnan` RuntimeError (non-production boundary, criterion 3 fails). Batch139 appendix added to `docs/unreachable_proofs.md`. |
| 140 | `ed0fda2` | 0 | state confirmed | 1496/0/17, 35/1683, guard 44/5 (rebaselined @ `ed0fda2`; tree now @ `9d8ea39`, same miss set/count). Bottlenecks re-routed; Batch 141 campaign appended. **Batch 141 executed (this session @ `d97339d` — see below).** |
| 141 | `d97339d` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5 (measured, `--rcfile=/dev/null`). **No miss reduction (delta 0); no canonical test added.** Materially-new **cross-module contract audit** (AST caller map + `sys.settrace` end-to-end `BABStrategy.run` trace, 12 run shapes + 3 public-entrypoint shapes): **0 target-line hits** on all 35 misses. Batch141 appendix added to `docs/unreachable_proofs.md` covering all remaining clusters with strict 4-criteria verdicts; `322,326` preserved; no semantics/workflow changes. **Floor mechanism-closed.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
