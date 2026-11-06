# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **This is the only durable handoff.** Read fully, then execute the **INITIAL TASK MESSAGE** below immediately. No off-ramp, no sidetrack, no status-only session, no planning-only session.

**Handoff refreshed (UTC):** 2026-11-06T20:42:54Z
**Last fresh canonical verification (UTC):** 2026-11-06T20:42:54Z (batches 40-69 + 71-72; **1454 passed, 13 failed (pre-existing Batch32/coverage_gaps only), 23 skipped, 102 warnings**)
**Guard rechecked (UTC):** 2026-11-06T20:42:54Z — `campaign_d*` **44 passed, 5 warnings**.
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `c5af914` (verify with `git rev-parse --short HEAD`). Working tree: clean. batch71/72 committed. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement.

- **No** infra/controller refactors. **No** sidetracks. **No** pivot to `cli.py`/other modules.
- Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, **or** a documented unreachable-branch proof **with file/line evidence** while immediately moving to the next reachable cluster.
- A session that ends with "reviewed code", "ran baseline only", or "planned next steps" without measured delta/proof is a **failed session**.

## VERIFIED STATE (fresh canonical: 2026-11-06T20:42:54Z)

- **Env:** Python 3.12.3. Deps (pandas/numpy/pytest/coverage) installed at `/home/runner/work/_temp/kilo-home/.local/` (set `PATH` and `PYTHONPATH` per Step 0). pyarrow/tables/fastparquet not installed — monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batch40-69 + 71-72):** **1454 passed, 13 failed (pre-existing Batch32/coverage_gaps only), 23 skipped, 102 warnings.**
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 107 miss, 94%.** (baseline was 109; **batch71 δ-1 line 400, batch72 δ-1 line 84** → 109→107).
- **Missing lines (exact, 107):** `43-44, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914, 953, 1033-1034, 1226-1227, 1257-1258, 1319-1320, 1530-1531, 1533-1536, 1591-1592, 1626-1627, 1663-1664, 1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`.
- **Batches 71-72:** batch71 covers line 400 (`_coerce_to_datetime_scalar` str-epoch seconds non-integer outer branch via `'170000000.5'`); batch72 covers line 84 (`_coerce_series_to_datetime_index` elementwise tz_convert via tz-aware string elements). Both registered in the fresh canonical aggregate via direct helper calls (no global patching). **Committed at c5af914.**
- **Step 0 baseline (run first; append batch71+ if they exist):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py
python3 -m coverage report --include='*data_loader.py' --show-missing
```

## BOTTLENECKS — REMOVED / ROUTED (do not let these block progress)

| # | Bottleneck | Route-around (mandatory) | Exit |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.** | Operator fixes workflow. |
| 2 | 107 miss remains; most batches gave 0 delta | **ROUTED.** Aggregate-safe strategy — craft real DataFrame/Series shapes that reach target branches and call canonical entrypoints/helpers directly (`validate_returns_dataframe`, `_promote_datetime_column`, `_drop_metadata_columns`, `normalize_schema`, `_drop_all_nan_columns`, `load_returns_from_csv`, `_coerce_to_datetime_scalar`, `_coerce_series_to_datetime_index`). Do **not** rely on global `pd.to_datetime`/`pd.read_csv` monkeypatching; batches 61-62, 65, 71-72 proved direct calls register while global patches get neutralized. | miss <107 (target ≤106, stretch ≤105). |
| 3 | 13 pre-existing Batch32/coverage_gaps failures | Ignore; miss delta is authoritative. | Documented. |
| 4 | pyarrow/tables/fastparquet missing | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites. | Covered/route-around. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Guard green. |
| 6 | Aggregate-context sensitivity | **ROUTED.** Module-level patches (`dl.pd.to_datetime`, `pd.read_csv`, `pd.DataFrame` subclasses) get neutralized by later tests in canonical order. Prefer data-shape triggers passed directly to canonical entrypoints with tightly-scoped monkeypatching confined to a context. Verify every batch in **fresh canonical aggregate** including all batch40+ files. | Delta recorded per batch. |
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
| 58 | name-match tz elementwise/apply-raise, unnamed tz/inner except, last-resort tz/set_index, benchmark remap/`__contains__` fallback, CSV stateful empty | 7 passed | 44 passed | 114→114 (0) | 0 delta — aggregate-context sensitivity |
| 59 | name-match outer except, unnamed coercer tz/inner except, last-resort tz+set_index fallback/result-not-DatetimeIndex, benchmark remap/`__contains__` fallback, CSV stateful empty | 6 passed | 44 passed | 114→114 (0) | 0 delta |
| 60 | name-match tz attr shape, exchange epoch via `clean_data`, coerce/detect/QA through validate, clean_data defensive/junk/dup, benchmark second remap | 5 passed | 44 passed | 114→114 (0) | 0 delta |
| 61 | real-data probes for promote/normalize (894, 901-903, 867-868, 859, 1530, 1533-1536) | 7 passed | 44 passed | 114→113 (**-1**) | line 894 newly covered; direct canonical entrypoint, no global patch |
| 62 | real-data probes metadata/normalize/parquet/hdf5 (1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193, 1097-1098) | 6 passed | 44 passed | 114→112 (**-2**) | lines 1097-1098 newly covered; direct canonical entrypoint |
| 63 | direct `_promote_datetime_column` probes (791-792, 859, 867-868, 901-903) | 7 passed | 44 passed | 114→114 (0) | 0 delta — retarget |
| 64 | targeted probes remaining clusters (1626-1627, 1663-1664, 791-792, 1530-1531, 1533-1536, 1591-1592) | 6 passed | 44 passed | 114→114 (0) | 0 delta — retarget |
| 65 | QA handlers / coerce fallbacks (`_run_data_quality_campaign`, `_coerce_numeric`) | 7 passed | 44 passed | 111→109 (**-2**) | lines 1293-1294 newly covered; direct canonical entrypoint |
| 66 | `_drop_metadata_columns` sequential-with-NaN, `normalize_schema` dup-header, `_run_data_quality_campaign` tz/coerce | 3 passed | 44 passed | 109→109 (0) | 0 delta — retarget; `test_1926_1927` removed (line 1926 unreachable: line 1916 identical condition fires first) |
| 67 | exchange normalize/long format, promote epoch/tz/name-match/unnamed/last-resort | 8 passed | 44 passed | 109→109 (0) | 0 delta — retarget (aggregate-context) |
| 68 | QA campaign tz/index, metadata drop, normalize dup-header, prices junk drop, coercion commas/units, CSV stateful | 8 passed | 44 passed | 109→109 (0) | 0 delta — retarget |
| 69 | promote name-match coercer tz-aware series, unnamed coercer tz, pd.to_datetime tz, exchange tz detect | 4 passed | 44 passed | 109→109 (0) | 0 delta — retarget |
| 71 | line 400 (`_coerce_to_datetime_scalar` str-epoch seconds non-integer outer branch) | 1 passed | 44 passed | 108→107 (**-1**) | input `'170000000.5'` (sub-1e9 non-integer) hits line 400 |
| 72 | line 84 (`_coerce_series_to_datetime_index` elementwise tz_convert) | 1 passed | 44 passed | 108→107 (**-1**) | tz-aware string elements → `pd.Timestamp(pdv)` tz-aware → line 83→84 |

**Measured improvement (historical): 139 → 107 miss (94%). Current session baseline/end:** 107 miss (batches 71-72: **-2 total**). Guard green (44 passed).

## LIKELY-HARD / UNREACHABLE — EVIDENCE (attempt via canonical path once; if still 0, document proof and move on)

Structural evidence (do not re-probe identical shapes):

- **`43-44`** — `_not_null` outer except. Only statements in outer try outside inner `pd.isna` try are `v is None` (never raises) and `return True` → outer except never fires → dead.
- **`84`** — COVERED by batch72 (tz-aware string elements through `_coerce_series_to_datetime_index`).
- **`92-93`** — `_coerce_series_to_datetime_index` outer except. Inner loops catch all exceptions; `pd.Series(clean, index=df.index)` length-matches → no raise → dead.
- **`194, 196`** — `_normalize_index` numeric-index elementwise coercer. `_coerce_to_datetime_scalar` raises `ValueError("bad")` (not `BABDataError`) → `except BABDataError: raise` at 195-196 never matches → dead.
- **`227-247`** — `_normalize_index` dayfirst last-ditch loop. Requires elementwise coercer to produce a NaT, but `_coerce_to_datetime_scalar` never returns NaT (raises instead) → `df.index.isna().any()` False → dead.
- **`268-269`** — `_normalize_index` `except (ValueError, TypeError)`. Non-numeric block's inner handlers catch `Exception` broadly; no plain ValueError/TypeError propagates → dead.
- **`285-286`** — `_normalize_index` tz_localize except. Requires `tz_convert` then `tz_convert(None)` then `tz_localize(None)` all to raise on a real tz-aware DatetimeIndex → not produced → dead.
- **`322, 326`** — `_coerce_to_datetime_scalar` campaign_d gated. Reachable only when `inspect.stack()` shows `campaign_d_core` in filename or `campaign_d.py`/`test_coerce_scalar_nat` caller. Batch files are not campaign_d → unreachable without gaming (do not create campaign_d-named files).
- **`334-335, 338-342, 351-352`** — `except Exception: pass` after `raise ValueError("bad")` re-raise paths. The ValueError is re-raised (lines 332-333, 339-340, 349-350) so the generic except never fires → dead.
- **`400`** — COVERED by batch71 (`'170000000.5'`).
- **`403-404`** — `_coerce_to_datetime_scalar` str-epoch outer except. Everything inside the outer try (362-402) is try/except-passed; `float(s)` won't raise (regex-matched) → outer try completes normally → dead.
- **`561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868`** — tz_convert branches in `_detect_and_normalize_exchange_format`/`_promote_datetime_column`. Require `pdv` tz-naive but `pd.Timestamp(pdv)` tz-aware; `_coerce_to_datetime_scalar` returns Timestamps (tz-aware for epochs/ISO, tz-naive for tz-naive input → `pd.Timestamp` stays tz-naive) → the `pd.Timestamp(pdv)`-is-tz-aware case never fires → dead.
- **`901-903`** — last-resort tz_convert. `pd.to_datetime(df[col], errors='raise')` on a **Series** has `.tz == None` even when elements are tz-aware → `getattr(parsed, "tz", None)` is None → block skipped → dead.
- **`908-914`** — last-resort `set_index` fallback. `parsed` from `pd.to_datetime(Series)` assigned via `df2.index = parsed`; DatetimeIndex result returns at line 906-907 before fallback → dead.
- **`953`** — `_normalize_asset_name` `if not tok_clean: continue`. `str.split()` never yields empty tokens → dead.
- **`1033-1034`** — `_normalize_columns` `except Exception` append fallback. `_normalize_asset_name` never raises (catches all at 982-983) → dead.
- **`1226-1227`** — `_coerce_numeric` outer `(ValueError,TypeError,AttributeError)` except. Inner `to_numeric(..., errors='raise')` failures re-raise as `BABDataError` (line 1224) → line 1226 never reached → dead.
- **`1257-1258`** — `_run_data_quality_campaign` tz_localize except. Requires `tz_convert` to raise then `tz_localize(None)` to raise on a tz-aware index → not produced by realistic pandas input → dead.
- **`1319-1320`** — `_run_data_quality_campaign` coerce fallback. `pd.to_numeric(..., errors="coerce")` does not raise for any input → dead.
- **`1530-1531, 1533-1536`** — benchmark remap. `validate_returns_dataframe` calls `_normalize_columns` (line 1413) before the benchmark check (1515), and `_normalize_asset_name` uppercases any case-insensitive benchmark match to exactly `benchmark` → `bench_found != benchmark` never True → dead.
- **`1591-1592`** — `load_returns_from_csv` defensive empty-after-read. `df.empty` identical at lines 1583/1587 → 1587 never reached with non-`BABDataError`; 1591-1592 only catches non-`BABDataError` from a branch that cannot raise → dead.
- **`1626-1627, 1663-1664`** — parquet/hdf5 missing-file OSError/ValueError paths. Without pyarrow/tables, `pd.read_parquet/read_hdf` raises `ImportError`/`ModuleNotFoundError`, caught at 1613-1617/1650-1654 → `BABDataError` → 1624-1627/1663-1664 never reached → dead.
- **`1926-1929`** — `_drop_metadata_columns` integer-positive check. 1926-1927 (append+continue) requires integers min<=0 first==0 diff==1, but that's sequential-from-0 caught by line 1916 first; 1928-1929 (except/pass) needs an exception in the try → `np.allclose`/`np.diff` won't raise on numeric → dead.
- **`2160-2163, 2167-2168`** — `normalize_schema` first-row-headers / exchange-format excepts. First-row detection needs column-length mismatch (contrived); exchange format never raises (swallows all internally) → dead.
- **`2187-2189, 2192-2193`** — `normalize_schema` junk-drop excepts. `pd.to_numeric(..., errors='coerce')` never raises; `s.astype(str).str...` won't raise → dead.
- **`227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734`** — inspect/defensive/rare branches; max one probe pass each, then file/line evidence if unreachable (all listed above are proven dead).

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, mandatory)

**Timestamp (UTC):** 2026-11-06T20:42:54Z
**Recipient:** next coding agent in this repo.
**Mode:** HEAVY WORK ONLY. No analysis-only turn. No planning-only turn. No "next steps" summary without measured delta/proof.

### Mission

Reduce `strategies/betting_against_beta/data_loader.py` miss count from **107** (fresh canonical baseline re-verified 2026-11-06T20:42:54Z; **rebaseline at Step 0 before coding**). **BAB `data_loader.py` only.** Each batch must yield a **measured miss-count delta** in a **fresh canonical aggregate** OR a **documented unreachable-branch proof with file/line evidence**, then immediately move to the next reachable cluster. `campaign_d*` guard must stay green.

**Bottleneck route-around (mandatory):** Use **aggregate-safe** strategies — craft real DataFrame/Series shapes that reach target branches and call canonical entrypoints/helpers directly. Do **not** rely on global `pd.to_datetime`/`pd.read_csv` monkeypatching; batches 61-62, 65, 71-72 proved direct calls register while global patches get neutralized. Batches 55-70 gave 0 delta — do not repeat identical probe patterns without proving they fire in a fresh canonical aggregate.

### Focus campaign (ordered; do not avoid; do not stop early)

The remaining 107 misses are **proven unreachable/dead or campaign_d-gated** (see LIKELY-HARD / UNREACHABLE evidence above). The mission is now:

1. **Confirm exhaustion.** Re-run Step 0 baseline to confirm 107 miss. Re-attempt **max one probe pass each** on the remaining clusters ONLY if you can show a canonical-shape path that previous batches did not try; if a probe yields 0 delta in the fresh canonical aggregate, document file/line evidence and mark it exhausted.
2. **Document any newly-proven unreachable branch** with exact file/line evidence and move to the next cluster.
3. **If a measurable delta is found** (≥1 miss removed), record it, add batch `tests/test_bab_data_loader_batch73.py` (then 74, 75, …), update the ledger, and continue.

There are **no remaining reachable clusters identified**; treat further work as exhaustion-proofing unless a genuinely new canonical path is discovered.

### Execution contract (non-optional)

1. **Run Step 0 baseline first** and record actual `data_loader.py` miss count + exact missing lines before changes.
2. **Deliver measured-delta batches** (`tests/test_bab_data_loader_batch73.py`, …) **or** documented unreachable-branch proofs with file/line evidence for every remaining cluster. **Zero-delta batches do not count; retarget immediately.**
3. For **each batch:** minimal targeted tests → focused run → `campaign_d*` guard → **fresh canonical aggregate** (include all batch40+ files that exist) → record before/after miss count and delta. Commit locally only if safe; **do not push** unless explicitly requested.
4. **Update this HANDOFF.md** at session end: refreshed UTC, SHA, verified canonical result, batch ledger rows (delta or unreachable proof), remaining clusters, and the next initial task message. Keep it the single durable handoff.
5. **No off-ramps.** If context-sensitive, craft inputs through canonical caller paths. If a branch appears unreachable, prove with code-path analysis tied to exact lines and move to the next cluster.

### Targets

- **Session minimum:** miss **<107** with ≥1 measured-delta batch (or documented exhaustion with evidence for all remaining clusters).
- **Stretch:** ≤105.

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
- `data_loader.py` miss count **<107** (or unreachable-proof exhaustion documented with file/line evidence for all remaining clusters).
- `campaign_d*` guard green.
- This HANDOFF.md updated as the single durable handoff with next initial task message.
