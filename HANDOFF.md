# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T07:02Z @ `86d318b`; Batch 147 initial task message below is binding, re-confirmed at 07:02Z — data_loader.py unchanged since `88ef267`, same 35-miss floor). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` miss floor.** Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 147** immediately. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Batch status (this session)

- **Batch 146 (@ `88ef267`):** COMPLETED — materially-new methods executed (0 target hits, no delta, no canonical test added): **M1** parsing path variants via public loaders (tab-sep CSV, `#` comment/quoted CSV, `ts` column, NDJSON `.jsonl`, JSON records, `load_prices` CSV); **M2** malformed-but-parseable/realistic frames (duplicate index, mixed bad index token, `MultiIndex` columns, object dtype with non-numeric token, `Jan 1 2020` strings) — expected guarded `BABDataError`/normalization paths only; **M3** targeted `_normalize_index` 268–269 control-flow probe (scoped `pd.to_datetime` `ValueError` shim at 261/249): both cases converted to `BABDataError` before 268–269, **0 hits** (control-flow evidence only; criterion 3 not met for production); **M4** inspect/caller gate audit for 316–327/326 (AST + runtime wrap during `load_returns`): public stack is pandas-internal apply frames, **no `campaign_d*` gate match** — 326 remains guard-only/preserved. Fresh canonical: **1467 passed, 0 failed, 17 skipped, 109 warnings**; coverage **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`; guard **44 passed, 5 warnings**. Batch146 appendix appended to `docs/unreachable_proofs.md` (all clusters, strict 4 criteria). **Batch 147 binding below.**

## Measured state (fresh rebaseline, 2026-11-08T07:02Z @ `86d318b`)

- **Branch/SHA:** `main` @ `86d318b`. `data_loader.py` unchanged since `e945fde` (line→code stable). Local probe scratch cleaned; `.gitignore` ignores `probe*`/`debug*`/`diag*` (13 historical probe/debug files remain git-tracked in tree — **do not modify/commit them**).
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1467 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage (`--rcfile=/dev/null`, `--source=strategies.betting_against_beta`, report `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — all removed/routed (verified 2026-11-08T06:49Z)

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
| 10 | Repeated 0-delta inefficiency | B103–145 executed/measured (floor mechanism-closed across recorded methods). **No repeat probes.** 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed.

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–145) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer deterministic; 220–224 cannot leave NaT while raising-consistently except NaT-return values which 230–233 `continue` over; 234–244 need coercer-raise at 230–233 but not 220–223 on same value (impossible). B138/139/145. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 convert/raise; 266 re-raises `BABDataError` before 268; `BABDataError⊂ValueError`; trace 259→261→262–267, not 268. B138/139/145. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | **Closed for production-realistic scalars:** unmodified numpy no non-VE; float subclasses/np float16/longdouble/Decimal probed 0 hits (B139/B145). |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | **Closed:** re-raise before generic pass; inspect/campaign_d semantics preserved. B138/139/145. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed:** regex-admitted strings + builtin float/guarded branches. B138/139/145. |
| `_not_null` outer except | `43-44` | **Closed (structural).** B103+/145. |
| `_normalize_asset_name` empty token continue | `953` | **Closed:** Python `str.split()` cannot yield `''`; Unicode whitespace probed. B139/145. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames:** inner guards swallow. B138/139/145. |
| `_promote_datetime_column` outer handler | `791-792` | **Closed:** 760–790 individually guarded. B138/139/145. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–145 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | canonical aggregate included campaign_d_core tests; **35/1683**, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable/JSON-orient/tz/index/coercer evidence; 0 hits. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence; 0 hits. |
| 139 | `24db195` | 0 | heavy proof | 1496/0/17, 35/1683, guard 44/5. AST/MRO/coercer static proofs; pandas 3.1.1 traces 0 hits; 351–352 only monkeypatched `np.isnan` RuntimeError (non-production, criterion 3 fails). |
| 140 | `ed0fda2` | 0 | state confirmed | 1496/0/17, 35/1683, guard 44/5 rebaselined. |
| 141 | `d97339d` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5. Cross-module contract audit (`BABStrategy.run`/CLI/loaders, 15 shapes) + AST caller map; **0 target hits**. |
| 142 | `2a272a7` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5. File-path loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz; **0 target hits**. |
| 143 | `5af2dda` | 0 | baseline confirmed | 1467/0/17, **35/1683**, guard 44/5 (data_loader unchanged since `e945fde`). |
| 144 | — | — | — | (reserved in prior handoff text; no separate batch recorded) |
| 145 | `2848cf7` | 0 | appendix | 1467/0/17, **35/1683**, guard 44/5 (fresh). IO/parsing seams (StringIO/temp CSV/JSON/`load_prices`), realistic dtype/Unicode boundaries, **ladder-state satisfiability** (NaT-return/continue blocks 234–244; coercer determinism), exception-type boundaries; `sys.settrace` **0 target hits**. Batch145 appendix in `docs/unreachable_proofs.md`; all clusters strict 4 criteria. `322,326` preserved. |
| 146 | `88ef267` | 0 | appendix | 1467/0/17, **35/1683**, guard 44/5 (fresh rebaseline). **M1** parse path variants (tab/comment/quoted/ts/NDJSON/JSON records/`load_prices`); **M2** malformed-but-parseable frames (dup/mixed index, MultiIndex cols, obj non-numeric, dateutil-like strings); **M3** 268–269 control-flow probe (`pd.to_datetime` VE shim) → **0 hits, converted to BABDataError before 268–269** (control-flow evidence only); **M4** inspect/caller gate audit → public `load_returns` stack pandas-internal, **no `campaign_d*` gate match** (326 preserved). Batch146 appendix in `docs/unreachable_proofs.md`; all clusters strict 4 criteria. **Batch 147 binding below.** |

## INITIAL TASK MESSAGE — 2026-11-08T07:02Z (Batch 147) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `86d318b` (`data_loader.py` unchanged since `e945fde`). **Fresh baseline (measured this session):** 1467/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. `data_loader.py` unchanged since `e945fde`. **B103–146 executed (0-delta/floor mechanism-closed across recorded methods). No baseline-only/review-only/planning-only/status-only exit.**



### Mission (binary, both acceptable as heavy work; primary preferred)

1. **Primary:** Push `data_loader.py` **below 35 miss** in a fresh canonical aggregate via a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all 4 criteria on a real `DataFrame`/index/dtype/column-label/file-format path. No semantic changes. Preserve `322,326`. Implement as `tests/test_bab_data_loader_batch147.py` (only if a concrete 4-criteria path is found), run focused → guard → fresh canonical aggregate including it, record measured delta.
2. **Fallback (only after exhaustive new-method work on all clusters):** Add genuinely new unreachable-proof evidence to `docs/unreachable_proofs.md` using a **materially new method** not recorded in B103–146. Required: per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict for **every** remaining cluster. Do not repeat disproven methods. Append Batch147 appendix and update HANDOFF/ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–146), semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 147 materially-new methods (use ≥1 substantively; record commands/cases/outcomes; must differ from B103–146)

B103–146 already recorded: AST/MRO/coercer determinism; inspect/caller frame gates + **B146 M4 gate audit** (public stack pandas-internal); pandas 3.1.1 public/downstream traces; cross-module `BABStrategy.run`/CLI/loader contract audit (B141); file-path CSV/JSON loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz (B142); IO/parsing seams incl. BOM/mixed NL/decimal/thousands/parse_dates/JSON orients (B145); parse path variants tab/comment/quoted/ts/NDJSON/JSON records/`load_prices` (B146 M1); malformed-but-parseable dup/mixed index/MultiIndex cols/obj non-numeric/dateutil-like (B146 M2); **268–269 scoped `pd.to_datetime` VE shim control-flow trace (B146 M3)**; ladder-state satisfiability NaT-return/continue (B145); Unicode whitespace/realistic dtype/exception-type boundaries (B145). **Do not repeat.**

- **`pd.read_json`/CSV realistic `dtype`/`converters`/`date_parser`-adjacent public behavior without changing loader semantics:** create temp files exercising pandas read paths that produce nullable/pyarrow-free object shapes, then pass resulting `DataFrame` through public loaders; focus on shapes that can make `to_datetime`/`astype`/`isna`/`map` raise *unexpected* exception types in inner try blocks (record actual exception MRO). Only counts if it uses public loader entry points or a production-realistic `DataFrame` shape pandas can emit.
- **Exchange/column-detection adversarial-but-plausible public frames:** frames with `timestamp`/`ts`/`datetime`/`date` column name collisions, mixed-case duplicate-like names after normalization, `open/high/low/close/volume` partial presence, symbol columns with NaN/empty/Unicode, and `DatetimeIndex` already present — target **641–642/694–695/791–792** by tracing which specific inner operation can raise and escape its local `except`.
- **`_coerce_to_datetime_scalar` 334–335/338–342/351–352/403–404 with numpy/pandas scalars produced by real operations:** `np.datetime64` from `pd.Timestamp(...).to_datetime64()` edge forms, `pd.Series([...]).iloc[0]` on nullable/extension dtypes, `np.generic` subclasses that arise from `np.array(...)[0]` on object arrays — but **only** if reachable via a plausible `DataFrame` cell/index element that `load_returns/load_prices/_normalize_index/_coerce_to_datetime_scalar` can receive in production; record criterion 3 explicitly.
- **268–269 criterion-3 closure attempt (evidence-only, no semantic change):** audit whether any pandas 3.1.1 `to_datetime` call at 249/250/261 can raise `ValueError`/`TypeError` (not `BABDataError`) that is *not* converted by 251–267 in that specific branch ordering — cite actual pandas behavior/exception types; if none plausible, record a final handler-order + pandas-exception-type proof (new angle vs B146 shim).
- **43–44 / 953 final construction proof (evidence-only):** for `_not_null`, enumerate value categories produced by pandas parsing/indexing in this codebase and show none trigger the outer catch except already-handled paths (or show the catch is defensive-only but unreachable by construction) — must be a materially-new argument tied to actual call sites/types, not restating B103. For `953`, tie `str.split()` semantics to all normalization inputs reaching that function.
- **Targeted source/control-flow oracle per miss line:** for each remaining cluster, list every operation inside the guarded region and the exception types it can raise under pandas 3.1.1/numpy 2.5.4 on realistic inputs; if any operation can raise a type *not* caught by the local `except`, demonstrate with a production-realistic `DataFrame`; otherwise append per-line oracle verdict. (Evidence-only reasoning must be grounded in measured behavior.)
- If a concrete 4-criteria path is found, implement as `tests/test_bab_data_loader_batch147.py` and verify in fresh canonical aggregate.

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__, pytest.__version__, coverage.__version__, scipy.__version__)"
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
2. Apply strict 4 criteria. If all 4 met: create `tests/test_bab_data_loader_batch147.py`, run focused → guard → fresh canonical aggregate including batch147, record measured delta.
3. If not: run ≥1 materially-new Batch 147 check (not a B103–146 repeat), document method/result, append Batch147 appendix to `docs/unreachable_proofs.md`.
4. Never repeat B103–146 disproven methods.
5. Every cluster must end the session with either a 4-criteria verdict or a recorded materially-new-method proof — **no cluster may be left unevaluated**.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete Batch147 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering **all** remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
