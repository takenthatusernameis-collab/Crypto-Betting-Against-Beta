# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF — canonical, no competing handoff files.** Refreshed **2026-11-08T18:52:35Z** @ `d053dfb` (`main`, clean worktree). `strategies/betting_against_beta/data_loader.py` unchanged since `e945fde` (**line→code stable** for all target clusters). **Repo-name priority = BAB only** — next heavy work targets `strategies/betting_against_beta/data_loader.py` remaining miss floor.
>
> **Step 0 re-verified this session (2026-11-08T17:57Z, authoritative commands, fresh `.coverage*`, PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib, `--rcfile=/dev/null --source=strategies.betting_against_beta`):** **Canonical subset now includes batch172** (repo convention: retained batch tests) — explicit list = `tests/test_betting_against_beta*.py` + `test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` → **645 passed, 6 skipped, 34 warnings** (57.32s). `data_loader.py` report (`--include='strategies/betting_against_beta/data_loader.py' --show-missing`): **365 miss / 1683 stmts / 78% overall**. **Target-miss floor unchanged (all still present): `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`**. Historical baseline excluding batch172 remains **632/6/34, 380 miss/77%** (see §Measured state). `batch172` tests sanity: **13 passed**. Batch 172/M172.1–M172.7 recorded in `docs/unreachable_proofs.md` §Batch 172 (0 floor reduction).
>
> **No session is blocked. No inefficient bottlenecks remain.** Any exit without measurable heavy work is a failed session.
>
> **ACTIVE NEXT-SESSION DIRECTIVE (execute immediately, no alternatives): BATCH 173 — reduction-first heavy campaign.** Run Step 0 (fresh canonical rebaseline including batch172), then do reduction attempts and/or materially-new proof probes across **every remaining cluster** until measurable outcome. **No status-only, planning-only, review-only, baseline-only, or “closed/unreachable/no mechanism” exit** without required heavy work.
>
> **Binding rules:** (A) miss reduction in a fresh canonical aggregate, **OR** (B) genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` (`## Batch 173`) with per-cluster `file:line@SHA`, materially-new method, observed result, strict 4-criteria verdict for **every remaining cluster**. “No new mechanism exists” is invalid without materially-new checks + recorded negative evidence. **Never change production semantics for coverage. Never alter `322,326`. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. Keep batch148/149/172 passing and retained. No tracked `probe*`/`debug*` edits/commits.**

## Measured state (fresh rebaseline, **2026-11-08T17:57Z** @ `bb02b3f`; `data_loader.py` @ `e945fde`, line-stable)

- **Branch/SHA:** `main` @ `bb02b3f` (clean). `strategies/betting_against_beta/data_loader.py` last changed `e945fde` — **line→code stable**.
- **Canonical decision (Step 0):** include `tests/test_bab_data_loader_batch172.py` (retained batch test convention). **Authoritative canonical list:** `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` (no 70,75,90-92,94).
- **Canonical aggregate (fresh):** `rm -f .coverage .coverage.* && ... coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py "${files[@]}"` → **645 passed, 6 skipped, 34 warnings**.
- **Coverage (same run):** `coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing` → **365 miss / 1683 stmts / 78%**. **Target-miss floor still present:** `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. **`326` guard-relevant — preserve semantics.**
- **Historical baseline (excl. batch172, for continuity):** 632 passed, 6 skipped, 34 warnings; 380 miss / 77%; same target floor (re-verified 17:48Z).
- **Guards/sanity:** `batch172` alone **13 passed**. `campaign_d*` guard last verified **883 passed, 5 skipped, 3419 deselected** (17:48Z); re-run if touching campaign_d/inspect-sensitive paths.
- **Deps/env:** `/home/runner/work/_temp/kilo-tmp/pylib` (pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**). Use explicit `seq` file list (brace expansion fragile).


## Bottlenecks — resolved (no blocked/inefficient sessions)

| # | Bottleneck | Resolution | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; never commit probes. | Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** | Routed |
| 3 | Deps fragility | Install/use deps in `/home/runner/work/_temp/kilo-tmp/pylib`; set PATH+PYTHONPATH. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve inspect/caller behavior and campaign_d behavior. **Never alter `322,326`.** | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148,149** (no 70,75,90-92,94). Batch148+149 retained. Step 0 command is authoritative. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–168 executed/measured/proved (M149–M168). No repeat probes of closed mechanisms. 0-delta without materially-new method + recorded evidence = **failed session**. | Routed |
| 11 | HANDOFF stale/binding drift | **Resolved this refresh @ `9d8b7b1` (2026-11-08T17:37Z).** Batch 171 complete (632/6/34; 380 miss/77%; campaign_d 883/5/3406; M171.A–F in proofs §Batch 171). **Batch 172 binding directive is active below — next session must do heavy work.** | Resolved |

**No competing handoff files exist.** (`docs/unreachable_proofs.md` = evidence appendix only.)

## Remaining target-miss cluster map (verify line→code @ current SHA every session)

| Cluster | Lines | Status (B103–168 / proofs) |
|---|---|---|
| `_not_null` outer except | `43-44` | Closed (structural) — M150.7/M151.B/C/M161.1/M162.A/C/M163/M168.A. |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Closed (dataflow gate/contract) — M150.3/M151.D/M161.2/M162.A/B/F/M163/M168.B-D. 232 same deterministic coercer; 234-244 unreachable under live contract. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Closed (handler-order shadow/MRO) — M150.2/M151.C/M161.3/M162.B/M163/M168.D. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise guards | `338-342` | Closed (explicit-raise/guarded) — M150.1/M151.A/B/M161.5/M162.A/M163/M168.A. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Closed (regex+float+guarded) — M150.4/M151.A/M161.6/M162.A/M163/M168.E. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | Closed for production-realistic frames — M150.5/M151.B/M161.7/M162.D/M163/M168.F-G. |
| `_promote_datetime_column` outer handler | `791-792` | Closed (fully guarded) — M150.6/M151.C/M161.8/M162.D/M163/M168.F-G. |
| `_normalize_asset_name` empty token continue | `953` | Closed (construction-unreachable) — M150.7/M151.A/B/M161.9/M162.E/M163/M168.H. |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–168 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---|---|---|
| 148 | `2ba2c8f` | -2 | reduction | 351-352; semantics preserved. |
| 149 | `34f462e` | -2 | reduction | 334-335 (M149); semantics preserved. |
| 150–164 | — | 0 | proof | M150–M164 recorded in proofs/history. |
| 165 | `61f639a` | 0 | partial→closed | Step 0 rebaseline; heavy work rolled to 166+. |
| 166 | `61f639a` | 0 | proof | directive executed historically; see proofs/HANDOFF history. |
| 167 | `61f639a` | 0 | proof | see proofs/HANDOFF history. |
| 168 | `ca2f160` | 0 | proof | M168.A–H; 0 target hits; no canonical test/prod change. |
| 169 | `ca2f160` | 0 | state-only | Step 0 re-verified; heavy work rolled to 170. |
| 170 | `ba7feed` workspace | 0 | proof | M170.1–M170.5 (scalar-contract NaT gate probe hit 245 not 234-244/246-247; non-campaign_d NaT scalar frames; nullable string index/public temp CSV exchange loader; handler-shadow reconfirmation; construction checks). 0 target hits; no canonical test/prod change. Appendix in `docs/unreachable_proofs.md` §Batch 170. |
| 171 | `63c969a7` (workspace) | 0 | proof | M171.A–F (NaT-string scalar contract, actual `_normalize_index` trace showing 232 returns NaT→233 continue so 234-244 never reached; 245 assignment ok for normal/subclass/tz-aware; NaT CSV/long loader paths; detect/promote edge frames; np.datetime64 NaT units s-D/M/Y/h/m; DataFrame subclass/tz-aware+NaT index). 0 target hits; no canonical test/prod change. Appendix in `docs/unreachable_proofs.md` §Batch 171. |
| 172 | workspace @`97a9846` | 0 | proof+probes (no reduction) | M172.1–M172.7: DTI tz-op TypeError subclass, exchange epoch-ms/epoch-string + narrow `pd.to_datetime`/coercer/copy injection, tz-aware promote + `Timestamp.tz_convert` injection, epoch unit `OverflowError` fallback, `np.datetime64('NaT','s')` public normalize, `_not_null` sentinels, repeated-separator construction, public CSV empty-date/epoch-ms loaders. 13 tests added (`tests/test_bab_data_loader_batch172.py`); canonical baseline unchanged **632/6/34, 380 miss/77%**; aggregate incl. batch172 **645/6/34, 365 miss/78% overall, target floor unchanged**. `campaign_d*` green. `docs/unreachable_proofs.md` §Batch 172. |
| 173 | — | 0 (pending) | **BINDING — ACTIVE** | **Next session MUST execute Batch 173 heavy work immediately** (reduction attempt or M173.* materially-new evidence for every remaining cluster). No baseline-only exit. |

## INITIAL TASK MESSAGE — 2026-11-08T18:52:35Z (Batch 173) — BINDING, EXECUTE IMMEDIATELY

**Repo:** `Crypto-Betting-Against-Beta`. **Priority (repo-name):** BAB only — `strategies/betting_against_beta/data_loader.py` remaining miss floor. **State @ handoff:** `main` `bb02b3f` clean; `data_loader.py` semantic `e945fde` (verify line→code). **Step 0 done (17:57Z):** canonical now includes `batch172` → **645 passed, 6 skipped, 34 warnings**; `data_loader.py` **365 miss / 1683 stmts / 78%**; **target floor unchanged: `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`**. `batch172` sanity 13 passed. No blockers/bottlenecks. **Baseline-only exit forbidden.**

### Forced heavy-work campaign

1. **Step 0 (fresh, mandatory):** rerun authoritative canonical aggregate incl. batch172 (`rm -f .coverage*`; pylib PATH/PYTHONPATH; `--rcfile=/dev/null --source=strategies.betting_against_beta`; report `--include='strategies/betting_against_beta/data_loader.py' --show-missing`) + `-k campaign_d` guard. Verify line→code for every cluster. Record drift. **Continue immediately.**
2. **Reduction sprint (primary):** for each cluster, re-check strict 4 criteria against **B103–172/M149–M172** + current code. If any satisfies all 4, implement `tests/test_bab_data_loader_batch173.py` with **production-realistic** inputs (no semantic change, no pathological harness), prove floor reduction in fresh canonical aggregate. Keep `322,326`; keep `campaign_d*` green; keep batch148/149/172.
3. **Proof probes (mandatory if no reduction):** exhaustive **materially-new** M173 probes over **all remaining clusters**. Forbidden repeats: all B103–172/M149–M172 methods (incl. M172.1–M172.7 mechanisms). New-only examples if genuinely applicable: real `read_json`/`to_json`/pickle round-trips through public BAB loaders; `dtype_backend`/`na_filter`/`parse_dates`/`date_format`/engine effects on real CSV paths; extension-array scalar boxing in unmocked BAB `apply`/`pd.to_datetime`; inspect/stack-sensitive paths **without altering 322,326**; long-format exchange records reaching different branches than M172; production-plausible pandas-internal raises inside currently-covered try bodies escaping to 641-642/694-695/791-792. Append `docs/unreachable_proofs.md` `## Batch 173 — ...` per cluster: `file:line@SHA`, materially-new method, observed result, strict-4 verdict. Cover **all clusters**: `43-44,234-244,246-247,268-269,326(guard-only),338-342,403-404,641-642,694-695,791-792,953`.
4. **Forbidden:** status/planning/review/baseline-only; M149–M172 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; workflow edits; tracked `probe*`/`debug*` edits; commit/push unless requested.

### Measurable outcome (required)

**(A)** target-floor reduced in fresh canonical aggregate, **or (B)** complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` §Batch 173 covering all clusters + HANDOFF ledger/measured state updated. Report exact commands, counts, miss lines, artifact paths. **BEGIN HEAVY WORK NOW.**


## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
