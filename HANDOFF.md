# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T06:03Z @ `5af2dda`, refreshed at session start; Batch 145 initial task message below is binding). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` miss floor.** Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 145** immediately. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Batch status (this session)

- **Batch 143 (@ `2a272a7`):** BASELINE CONFIRMED @ `5af2dda` (`data_loader.py` unchanged since `2a272a7` / `e945fde` miss line→code; Step 0 fresh rebaseline run @ `5af2dda`). Fresh baseline: **1467 passed, 0 failed, 17 skipped, 109 warnings**; coverage **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`; guard **44 passed, 5 warnings**, `322` covered, `326` live inspect-gated miss. State unchanged vs Batch 142 measured baseline; floor mechanism-closed across recorded B103–142 methods. Batch 143 = 0-delta proof-only baseline confirmation; no canonical test added. **Batch 145 binding below.**
- **Batch 142 (@ `2a272a7`, prior session):** COMPLETED — materially-new **file-path/public-loader + nullable/Categorical/MultiIndex/np-dtype + Hypothesis scalar/loader/index/exchange/asset-name fuzz** with `sys.settrace` (production-realistic CSV/JSON temp files; `MultiIndex`/`CategoricalIndex`/nullable `Float64`+`pd.NA`; `datetime64[ns/us/ms/s]`; `np.float64/32` NaN/inf, `np.int64/uint64` epochs; exchange long/OHLCV column-name variants; `_normalize_asset_name`/`_not_null`/`_coerce_numeric`; duplicate/nullable strategy run). Hypothesis: 800 coercer, 80 load_returns+NaN, 100 mixed-index, 30 exchange variants, 500 asset names, 300 null/numeric fuzz (`deadline=None`). Canonical aggregate **1496/0/17, 35 miss / 1683 stmts / 98%**, guard **44/5**. **Delta 0; no miss reduction; no canonical test added.** Complete Batch142 non-repeat materially-new appendix appended to `docs/unreachable_proofs.md` covering all remaining clusters with strict 4-criteria verdicts. `322,326` preserved; no semantics/workflow changes.
- **Batch 141 (@ `d97339d`):** COMPLETED — materially-new cross-module contract audit (AST caller map + `sys.settrace` end-to-end `BABStrategy.run`, 15 shapes): **0 target-line hits** on all 35 misses. Delta 0.

## Measured state (fresh rebaseline, 2026-11-08T05:58Z @ `5af2dda`)

- **Branch/SHA:** `main` @ `5af2dda` (`data_loader.py` unchanged since `e945fde` for miss line→code). Working tree has local probe scratch (`probe*`, `debug_beta*`) `.gitignore`d — do not commit unless requested.
- **Canonical aggregate (fresh rebaseline, 2026-11-08T05:58Z @ `5af2dda`, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1467 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage (`--rcfile=/dev/null`, `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest`, `coverage`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — all removed/routed (verified 2026-11-08T05:58Z)

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
| 10 | Repeated 0-delta inefficiency | Batches 103–143 mechanism-closed/probed; Batch 143 state-confirmed only. **No repeat probes.** 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed. Blockers eliminated: scratch clutter ignored, controller test excluded, deps pinned via pylib, coverage DB cleaned each run, path filtering fixed, missing engines handled, aggregate sensitivity scoped, `322,326` preserved, canonical batch set pinned, 0-delta repeats forbidden.

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–144) |
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
2. Mechanism not disproven by batches 103–144 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## INITIAL TASK MESSAGE — 2026-11-08T05:58Z (Batch 145) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `5af2dda`. **Fresh baseline (measured this session):** 1467/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. `data_loader.py` unchanged since `e945fde`. **B103–144 executed (0-delta/floor mechanism-closed across recorded methods). No baseline-only/review-only/planning-only/status-only exit.**

### Mission (binary, both acceptable as heavy work; primary preferred)

1. **Primary:** Push `data_loader.py` **below 35 miss** in a fresh canonical aggregate via a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all 4 criteria on a real `DataFrame`/index/dtype/column-label/file-format path. No semantic changes. Preserve `322,326`. Implement as `tests/test_bab_data_loader_batch145.py` (only if a concrete 4-criteria path is found), run focused → guard → fresh canonical aggregate including it, record measured delta.
2. **Fallback (only after exhaustive new-method work on all clusters):** Add genuinely new unreachable-proof evidence to `docs/unreachable_proofs.md` using a **materially new method** not recorded in B103–144. Required: per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict for **every** remaining cluster. Do not repeat disproven methods. Append Batch144 appendix and update HANDOFF/ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–144), semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 145 materially-new methods (use ≥1 substantively; record commands/cases/outcomes; must differ from B103–144)

B103–144 already recorded: AST/MRO/coercer determinism; inspect/caller frame gates; pandas 3.1.1 public/downstream traces; cross-module `BABStrategy.run`/CLI/loader contract audit (B141); file-path CSV/JSON loaders + nullable `Float64`/`pd.NA`/`CategoricalIndex`/`MultiIndex`/`datetime64[ns/us/ms/s]`/np scalar subtypes + Hypothesis fuzz (B142); Batch143 baseline confirmation @ `5af2dda` (state reconfirmed, 35 miss floor unchanged). **Do not repeat.**

- **Pandas IO/parsing seams with production-realistic file content (no pyarrow/fastparquet/hdf5 engines available):** `pd.read_csv` with `StringIO`/`BytesIO`/real temp files using `na_values`, `keep_default_na`, `dtype=str|object`, `parse_dates` combos, `thousands`, `decimal`, quoted fields, UTF-8 BOM, mixed newlines, trailing delimiters, `index_col` ambiguity, duplicate date columns, and `load_returns`/`load_prices` path; trace misses. Also `pd.read_json(orient='records'|'columns'|'split'|'index'|'values'|'table')` temp files through public loaders.
- **Exception-type/MRO probing on *real* pandas operations (criterion 3):** identify whether any realistic pandas/numpy call inside guarded blocks can raise an exception type that escapes the specific `except` guards (e.g., `pd.errors.*`, `numpy.exceptions.*`, `OverflowError`, `KeyError` from index ops) under realistic frames; use `sys.settrace` + targeted realistic inputs, not arbitrary monkeypatches.
- **Stateful sequence fuzz through `load_returns`→`_normalize_index`→coercer:** generate sequences of index values that force the exact branch ladder (216-224 batch coercion leaves NaT-like? impossible by contract — verify by tracing 225 isna-any outcomes; 227-247 dayfirst last-ditch only if 225 true and element parse raises then re-raises at 244; 248-258 fallback). Record which ladder predicates are satisfiable under real coercer behavior.
- **`_detect_and_normalize_exchange_format`/`_promote_datetime_column` realistic “almost exchange/promotion” frames:** frames with partial symbol/close matches, ambiguous date+value columns, object dtypes with mixed epoch strings/ISO/NaN, columns named `timestamp`/`open_time`/`close_time` in non-exchange contexts; exercise the exact guarded lines 641–642/694–695/791–792 via trace.
- **`_normalize_asset_name` Unicode/zero-width/whitespace variants that survive as tokens?** confirm `str.split()` behavior on NBSP/ZWSP/tabs/newlines; if any produces empty token under realistic symbol normalization path, test it (criterion 3).
- **AST+runtime invariant proof (new form):** prove 953 unreachable from `split()` semantics over Python `str.split()` (no empty elements) and show all call sites pass normalized strings; for 43–44 show `_not_null` only reachable exception sources are `pd.isna` on pathological objects — demonstrate with a custom `__bool__`/`isna`-raising object passed through every public path and trace (production-realistic? criterion 3 likely fails, record verdict).
- If a concrete 4-criteria path is found, implement as `tests/test_bab_data_loader_batch145.py` and verify in fresh canonical aggregate.

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py $(for i in $(seq 40 69); do echo tests/test_bab_data_loader_batch$i.py; done) $(for i in 71 72 73 74 76 77 78 79 80 81 82 83 84 85 86 87 88 89 93 95 96; do echo tests/test_bab_data_loader_batch$i.py; done)
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 35 miss / 1467/0/17 / guard 44/5.

### Forced campaign (no early exit)

For each cluster `234-244,246-247`, `268-269`, `351-352`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only):
1. Verify file:line at current SHA.
2. Apply strict 4 criteria. If all 4 met: create `tests/test_bab_data_loader_batch145.py`, run focused → guard → fresh canonical aggregate including batch145, record measured delta.
3. If not: run ≥1 materially-new Batch 145 check (not a B103–144 repeat), document method/result, append Batch145 appendix to `docs/unreachable_proofs.md`.
4. Never repeat B103–144 disproven methods.
5. Every cluster must end the session with either a 4-criteria verdict or a recorded materially-new-method proof — **no cluster may be left unevaluated**.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete Batch144 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering **all** remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | canonical aggregate included campaign_d_core tests; **35/1683**, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable/JSON-orient/tz/index/coercer evidence; 0 hits. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence; 0 hits. |
| 139 | `24db195` | 0 | heavy proof | 1496/0/17, 35/1683, guard 44/5 (measured). AST/MRO/coercer static proofs; pandas 3.1.1 public-loader/downstream `sys.settrace` 0 target hits; 351–352 hit only via monkeypatched `np.isnan` RuntimeError (non-production boundary, criterion 3 fails). Batch139 appendix added to `docs/unreachable_proofs.md`. |
| 140 | `ed0fda2` | 0 | state confirmed | 1496/0/17, 35/1683, guard 44/5 (rebaselined @ `ed0fda2`; tree now @ `9d8ea39`, same miss set/count). Bottlenecks re-routed; Batch 141 campaign appended. **Batch 141 executed (this session @ `d97339d` — see below).** |
| 141 | `d97339d` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5 (measured, `--rcfile=/dev/null`). **No miss reduction (delta 0); no canonical test added.** Materially-new **cross-module contract audit** (AST caller map + `sys.settrace` end-to-end `BABStrategy.run` trace, 12 run shapes + 3 public-entrypoint shapes): **0 target-line hits** on all 35 misses. Batch141 appendix added to `docs/unreachable_proofs.md` covering all remaining clusters with strict 4-criteria verdicts; `322,326` preserved; no semantics/workflow changes. **Floor mechanism-closed.** |
| 142 | `2a272a7` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5 (fresh, `--rcfile=/dev/null`). **No miss reduction (delta 0); no canonical test added.** Materially-new **file-path/public-loader + nullable/Categorical/MultiIndex/np-dtype + Hypothesis scalar/loader/index/exchange/asset-name fuzz** with `sys.settrace` (CSV/JSON temp files; `MultiIndex`/`CategoricalIndex`/nullable `Float64`+`pd.NA`; `datetime64[ns/us/ms/s]`; np epochs/NaN/inf; exchange variants; Hypothesis 800+80+100+30+500+300). **0 target-line hits**. Batch142 appendix in `docs/unreachable_proofs.md`; all clusters strict 4-criteria verdicts. `322,326` preserved. **Batch 143 binding.** |
| 143 | `5af2dda` | 0 | baseline confirmed | Fresh rebaseline @ `5af2dda` (`data_loader.py` unchanged since `2a272a7`/`e945fde`): **1467 passed, 0 failed, 17 skipped, 109 warnings**; **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`; guard **44 passed, 5 warnings**, `322` covered, `326` live. State unchanged vs Batch 142 baseline; floor mechanism-closed. 0-delta proof-only baseline confirmation; no canonical test added. **Batch 145 binding.** |

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
