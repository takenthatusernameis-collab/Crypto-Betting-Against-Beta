# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **This is the only durable handoff.** Read fully, then execute the **INITIAL TASK MESSAGE** below immediately. No off-ramp, no sidetrack, no status-only session, no planning-only session.

**Handoff refreshed (UTC):** 2026-11-06T19:11:10Z
**Last fresh canonical verification (UTC):** 2026-11-06T18:04:55Z (Step 0 baseline re-run with batches 40-64; 1429 passed, 13 pre-existing Batch32 failures, 23 skipped, 102 warnings)
**Guard rechecked (UTC):** 2026-11-06T18:04:55Z — `campaign_d*` **44 passed, 5 warnings**.
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `3b9b51e` (verify with `git rev-parse --short HEAD`). Working tree clean at handoff refresh (no tracked/untracked strategy/test changes observed). Batches 61-64 already committed; **batch65+ not yet created**. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement.

- **No** infra/controller refactors. **No** sidetracks. **No** pivot to `cli.py`/other modules.
- Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, **or** a documented unreachable-branch proof **with file/line evidence** while immediately moving to the next reachable cluster.
- A session that ends with "reviewed code", "ran baseline only", or "planned next steps" without measured delta/proof is a **failed session**.

## VERIFIED STATE (fresh canonical: 2026-11-06T17:42:08Z)

- **Env:** Python 3.12.3. Deps (pandas/numpy/pytest/coverage) installed at `/home/runner/work/_temp/kilo-home/.local/` (set `PATH` and `PYTHONPATH` per Step 0). pyarrow/tables/fastparquet not installed — monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batch40-64):** **1429 passed, 13 failed (pre-existing Batch32/coverage_gaps only), 23 skipped, 102 warnings.**
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 111 miss, 93%.** (baseline 114 at Step 0; batches 61-64 contributed -3)
- **Missing lines (exact, 111):** `43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914, 953, 1033-1034, 1226-1227, 1257-1258, 1293-1294, 1319-1320, 1530-1531, 1533-1536, 1591-1592, 1626-1627, 1663-1664, 1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`.
- **Newly covered since 114-baseline:** `894` (batch61), `1097-1098` (batch62). Batches 63-64 gave 0 delta individually and in aggregate.
- **Step 0 baseline (run first; append batch65+ if they exist):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py
python3 -m coverage report --include='*data_loader.py' --show-missing
```

## BOTTLENECKS — REMOVED / ROUTED (do not let these block progress)

| # | Bottleneck | Route-around (mandatory) | Exit |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.** | Operator fixes workflow. |
| 2 | 111 miss remains; batches 55-60 gave 0 delta | **ROUTED.** Batches 61-64 proved **direct canonical-entrypoint calls with real DataFrame/Series shapes** (no global `pd.to_datetime`/`pd.read_csv` patching) register in a fresh canonical aggregate: batch61 δ1 (line 894), batch62 δ2 (lines 1097-1098), combined 61-64 δ3 (114→111). Next session must use this aggregate-safe strategy; global monkeypatch patches are overwritten/neutralized in canonical order. | miss <111 (target ≤108, stretch ≤105). |
| 3 | 13 pre-existing Batch32/coverage_gaps failures | Ignore; miss delta is authoritative. | Documented. |
| 4 | pyarrow/tables/fastparquet missing | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites. | Covered/route-around. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Guard green. |
| 6 | Aggregate-context sensitivity | **ROUTED.** Module-level patches (`dl.pd.to_datetime`, `pd.read_csv`, `pd.DataFrame` subclasses) get neutralized by later tests in canonical order. Prefer **data-shape triggers passed directly to canonical entrypoints** (`validate_returns_dataframe`, `_promote_datetime_column`, `_drop_metadata_columns`, `normalize_schema`, `_drop_all_nan_columns`, `load_returns_from_csv`) with tightly-scoped monkeypatching confined to a context. Verify every batch in **fresh canonical aggregate** including all batch40+ files. | Delta recorded per batch. |
| 7 | Confusing handoff sources | **This file is the only durable handoff.** No other HANDOFF/TODO/NEXT files exist. | N/A. |

**No other blockers recognized.** If a new issue appears, document it with file/line/evidence and route around it in the same session; do not stop.

## SESSION BATCH LEDGER (measured, cumulative)

| Batch | Targets | Focused | Guard | Canonical delta (miss) | Notes |
|---|---|---:|---|---:|---|
| 44 | 1487-1490/1588-1592/194,196 probes | 1 passed | 44 passed | 153→153 (0) | probes |
| 45 | 1487-1490 retry drop, 1530-1536 remap, promote/unnamed/clean_data handlers | 9 passed | 44 passed | 153→145 (**-8**) | |
| 46 | range/epoch/tz/defensive probes | 10 passed | 44 passed | 145→139 (**-6**) | |
| 47 | epoch/unnamed-tz/remap/clean_data probes | 9 passed | 44 passed | 139→139 (0) | retarget |
| 48 | promote/unnamed-tz (`_promote_datetime_column`) | 4 passed | 44 passed | contributed | `5f5d7d0` |
| 49 | 1530-1531 rename fallback, 1591-1592 CSV empty-after-read, 1451-1452 | 3 passed | 44 passed | 139→133 (**-6**) | `5f5d7d0` |
| 50 | dt-attr/dtype-tz, outer tz-normalize, name-match, unnamed-tz, remap probes | 6 passed | 44 passed | 133→131 (**-2**) | `24264a2` |
| 51 | set_index ValueError, RangeIndex year-raises, rename fallback, stateful empty, clean_data probes | 7 passed | 44 passed | 131→127 (**-4**, 51+52) | `24264a2` |
| 52 | promote handlers, exchange/epoch/tz, loaders, price metadata | 6 passed | 44 passed | (with 51) | `24264a2` |
| 53 | promote handlers, rename, CSV empty (canonical-leaning) | 6 passed | 44 passed | 127→124 (**-3**) | `24264a2` |
| 54 | promote/dtype-tz/elementwise/unnamed-tz/interval/parsed-tz/last-resort/QA handlers | 12 passed | 44 passed | 124→114 (**-10**) | `batch54` |
| 55 | name-match/unnamed-tz/last-resort/benchmark remap/CSV defensive/exchange epoch/clean_data probes | 10 passed | 44 passed | 114→114 (0) | 0 delta — retarget |
| 56 | flaky remap, stateful CSV empty, duplicate header, exchange open_time epoch, detect unknown, parquet engine fallback | 6 passed | 44 passed | 114→114 (0) | 0 delta |
| 57 | coerce_series tz, clean_data junk drop, DatetimeIndex tz norm, exchange normalize, benchmark case, hdf5 fallback | 6 passed | 44 passed | 114→114 (0) | 0 delta |
| 58 | name-match tz elementwise/apply-raise, unnamed tz/inner except, last-resort tz/set_index, benchmark remap flaky rename, CSV stateful empty | 7 passed | 44 passed | 114→114 (0) | 0 delta — aggregate-context sensitivity |
| 59 | name-match outer except, unnamed coercer tz/inner except, last-resort tz+set_index fallback/result-not-DatetimeIndex, benchmark remap/`__contains__` fallback, CSV stateful empty | 6 passed | 44 passed | 114→114 (0) | 0 delta |
| 60 | name-match tz attr shape, exchange epoch via `clean_data`, coerce/detect/QA through validate, clean_data defensive/junk/dup, benchmark second remap | 5 passed | 44 passed | 114→114 (0) | 0 delta |
| 61 | real-data probes for promote/normalize (894, 901-903, 867-868, 859, 1530, 1533-1536) | 7 passed | 44 passed | 114→113 (**-1**) | line 894 newly covered; direct canonical entrypoint, no global patch |
| 62 | real-data probes metadata/normalize/parquet/hdf5 (1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193, 1097-1098) | 6 passed | 44 passed | 114→112 (**-2**) | lines 1097-1098 newly covered; direct canonical entrypoint |
| 63 | direct `_promote_datetime_column` probes (791-792, 859, 867-868, 901-903) | 7 passed | 44 passed | 114→114 (0) | 0 delta — retarget |
| 64 | targeted probes remaining clusters (1626-1627, 1663-1664, 791-792, 1530-1531, 1533-1536, 1591-1592) | 6 passed | 44 passed | 114→114 (0) | 0 delta — retarget |

**Measured improvement (historical): 139 → 111 miss (93%). Current session baseline/end:** 111 miss (batches 61-64: **-3**, lines 894 and 1097-1098). Guard green (44 passed).

## LIKELY-HARD / CAUTION (attempt via canonical path; if still 0, produce file/line unreachable proof and move on)

- `791-792` — name-match elementwise tz outer catch (`_promote_datetime_column`, ~780-792). batch63/64 probes gave 0 delta. Try data where parsed elements are tz-aware objects but `dt_attr`/dtype-tz detection fails only via realistic pandas behavior through `validate_returns_dataframe`.
- `859, 861-862, 867-868, 901-903, 908-914` — unnamed/last-resort promote handlers (~843-919). Drive through `validate_returns_dataframe`/`load_returns*`/`clean_data` with unpatched module globals where possible.
- `1530-1531, 1533-1536` — `validate_returns_dataframe` benchmark remap fallbacks (~1515-1536). batch61 case-insensitive bench covered but remap-fallback branches still missing; need `bench_found != benchmark` with first rename raising.
- `1591-1592` — `load_returns_from_csv` second empty-check defensive (~1585-1592). Stateful `empty` across checks is hard; try inputs that raise only at the 1587 boundary, or prove unreachable.
- `679, 694-695, 713-714, 733-734` — exchange epoch/tz normalization (~660-734).
- `1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193` — `clean_data`/`normalize_schema` duplicate-header/junk/drop defensive branches. batch62 gave 0 delta; try canonical `normalize_schema`/`_drop_metadata_columns` shapes that reach the except/drop paths.
- `1226-1227, 1257-1258, 1293-1294, 1319-1320, 1033-1034, 953` — coerce/detect/QA handlers through canonical APIs.
- `1626-1627, 1663-1664` — parquet/hdf5 missing-file (`load_returns_from_parquet/hdf5` nonexistent path). batch64 gave 0 delta; verify exact raise path.
- `227-247, 43-44, 84, 92-93, 194, 196, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642` — inspect/defensive/rare branches; max one probe pass each, then file/line evidence if unreachable.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, mandatory)

**Timestamp (UTC):** 2026-11-06T19:11:10Z
**Recipient:** next coding agent in this repo.
**Mode:** HEAVY WORK ONLY. No analysis-only turn. No planning-only turn. No "next steps" summary without measured delta/proof.

### Mission

Reduce `strategies/betting_against_beta/data_loader.py` miss count from **111** (fresh canonical baseline re-verified 2026-11-06T18:04:55Z; **rebaseline at Step 0 before coding**). **BAB `data_loader.py` only.** Each batch must yield a **measured miss-count delta** in a **fresh canonical aggregate** OR a **documented unreachable-branch proof with file/line evidence**, then immediately move to the next reachable cluster. `campaign_d*` guard must stay green.

**Bottleneck route-around (mandatory):** Use **aggregate-safe** strategies — craft real DataFrame/Series shapes that reach target branches and call canonical entrypoints directly (`validate_returns_dataframe`, `_promote_datetime_column`, `_drop_metadata_columns`, `normalize_schema`, `_drop_all_nan_columns`, `load_returns_from_csv`). Do **not** rely on global `pd.to_datetime`/`pd.read_csv` monkeypatching; batches 61-64 proved direct entrypoint calls register in the fresh canonical aggregate while global patches get neutralized. Batches 63-64 gave 0 delta — do not repeat identical probe patterns without proving they fire in a fresh canonical aggregate.

### Focus campaign (ordered; do not avoid; do not stop early)

1. **`791-792, 859, 861-862, 867-868, 901-903, 908-914`** — `_promote_datetime_column` handlers. Batches 63-64 probed (0 aggregate delta). Use aggregate-safe real-data shapes through `validate_returns_dataframe`.
2. **`1530-1531, 1533-1536`** — `validate_returns_dataframe` benchmark remap fallbacks. Need `bench_found != benchmark`, benchmark absent, first rename raises (1530-1531), post-rename checks still trigger 1533-1536.
3. **`1591-1592`** — `load_returns_from_csv` defensive empty-after-read. Try malformed inputs that make `.empty`/isinstance raise only at the 1587 boundary, or prove unreachable with file/line evidence.
4. **`679, 694-695, 713-714, 733-734`** — exchange epoch/tz normalization via canonical entrypoints.
5. **`1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`** — `clean_data`/`normalize_schema` duplicate-header/junk/drop defensive branches.
6. **`1226-1227, 1257-1258, 1293-1294, 1319-1320, 1033-1034, 953`** — coerce/detect/QA handlers through canonical APIs.
7. **`1626-1627, 1663-1664`** — parquet/hdf5 missing-file paths.
8. **Triage with evidence (max one probe pass each, then move on):** `227-247, 43-44, 84, 92-93, 194, 196, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642`.

### Execution contract (non-optional)

1. **Run Step 0 baseline first** and record actual `data_loader.py` miss count + exact missing lines before changes.
2. **Deliver ≥3 verified batches** (`tests/test_bab_data_loader_batch65.py`, `batch66.py`, `batch67.py`, …) unless reachable clusters are exhausted with file/line evidence. **Zero-delta batches do not count; retarget immediately.**
3. For **each batch:** minimal targeted tests → focused run → `campaign_d*` guard → **fresh canonical aggregate** (include all batch40+ files that exist) → record before/after miss count and delta. Commit locally only if safe; **do not push** unless explicitly requested.
4. **Update this HANDOFF.md** at session end: refreshed UTC, SHA, verified canonical result, batch ledger rows (delta or unreachable proof), remaining clusters, and the next initial task message. Keep it the single durable handoff.
5. **No off-ramps.** If context-sensitive, craft inputs through canonical caller paths. If a branch appears unreachable, prove with code-path analysis tied to exact lines and move to the next cluster.

### Targets

- **Session minimum:** miss **<111** with ≥3 measured-delta batches (or documented exhaustion with evidence).
- **Target:** ≤108. **Stretch:** ≤105.

### Guard

```bash
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

### Hard rules

- BAB `data_loader.py` only. No infra/controller refactors, no `cli.py`/other-module pivot.
- Ignore 13 pre-existing Batch32/coverage_gaps failures. Never edit/commit/push `.github/workflows/*`.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar`), campaign_d semantics, no-lookahead, dollar-neutral defaults, public APIs.
- Smallest correct fix only for proven contract violations. **No comments.** No push unless explicitly requested.
- No force-push/history rewrite. No fake persistence/remote claims.

### Sacred invariants

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** invalid parse/validation → `BABDataError` (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` and campaign_d semantics.

### Definition of done for next session

- Fresh canonical aggregate completed with all existing batch40+ files included.
- `data_loader.py` miss count **<111** (or unreachable-proof exhaustion documented with file/line evidence).
- `campaign_d*` guard green.
- This HANDOFF.md updated as the single durable handoff with next initial task message.
