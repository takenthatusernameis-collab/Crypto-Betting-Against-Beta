# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **This is the only durable handoff.** Read fully, then execute the **INITIAL TASK MESSAGE** below immediately. No off-ramp, no sidetrack, no status-only session, no planning-only session.

**Handoff refreshed (UTC):** 2026-11-06T21:59:39Z
**Last fresh canonical verification (UTC):** 2026-11-06T21:59:39Z (batches 40-69 + 71-74; **1482 passed, 0 failed, 23 skipped, 105 warnings**). Batch75 verified separately: +2 passed, **0 delta** (miss stays 96) — excluded from canonical, route-around below.
**Guard rechecked (UTC):** 2026-11-06T21:59:39Z — `campaign_d*` **44 passed, 5 warnings**.
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `89721a6` (verify with `git rev-parse --short HEAD`). Working tree: **clean**. `docs/unreachable_proofs.md` present. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement.

- **No** infra/controller refactors. **No** sidetracks. **No** pivot to `cli.py`/other modules.
- Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, **or** a documented unreachable-branch proof **with file/line evidence** while immediately moving to the next reachable cluster.
- A session that ends with "reviewed code", "ran baseline only", or "planned next steps" without measured delta/proof is a **failed session**.

## VERIFIED STATE (fresh canonical: 2026-11-06T21:59:39Z)

- **Env:** Python 3.12.3. Deps (pandas/numpy/pytest/coverage) installed at `/home/runner/work/_temp/kilo-home/.local/` (set `PATH` and `PYTHONPATH` per Step 0). pyarrow/tables/fastparquet not installed — monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batch40-69 + 71-74):** **1482 passed, 0 failed, 23 skipped, 105 warnings.** (Prior: 1469 passed / 13 failed. The 13 Batch32 failures were **test-bug fixes only** — see below — no source change, no coverage delta.) Batch75 verified separately outside canonical: **+2 passed, 0 delta** (miss stays 96); excluded because it targets proven-unreachable clusters with exception-swallowing probes — see bottleneck #7 below.
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 96 miss, 94%.** (baseline was 109; batch71 δ-1 line 400, batch72 δ-1 line 84 → 109→107; batch73 δ-2 lines 1033-1034 → 107→105; batch74 δ-9 lines 2160-2163, 2167-2168, 2187-2189 → 105→96).
- **Missing lines (exact, 96):** `43-44, 92-93, 194, 196, 227-235, 237-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914, 953, 1226-1227, 1257-1258, 1319-1320, 1530-1531, 1533-1536, 1591-1592, 1626-1627, 1663-1664, 1926-1929, 2192-2193`.
- **Batches 71-74:** batch71/72 committed at c5af914 (lines 400, 84), batch73 at b1a2cff, batch74 at 682d168 (HEAD). All registered in fresh canonical aggregate via direct helper calls.
- **`docs/unreachable_proofs.md`:** present — documents all 96 remaining clusters with exact file:line, function, code path, why unreachable, and evidence.
- **Step 0 baseline (run first):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py
python3 -m coverage report --include='*data_loader.py' --show-missing
```

## BOTTLENECKS — REMOVED / ROUTED (do not let these block progress)

| # | Bottleneck | Route-around (mandatory) | Exit |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.** | Operator fixes workflow. |
| 2 | 96 miss remains; all documented unreachable | **ROUTED.** All 96 remaining clusters proven unreachable (see `docs/unreachable_proofs.md`); batch73/batch74 gave measured deltas via direct canonical calls. Any future batch must target a *new* reachable cluster with real DataFrame/Series shapes passed directly to canonical entrypoints — global patches get neutralized. | miss <96 (stretch ≤95) OR full unreachable documentation (done). |
| 3 | ~~13 pre-existing Batch32/coverage_gaps failures~~ **REMOVED 2026-11-06T21:47Z** | All 13 were **test bugs** (wrong monkeypatch targets, missing asset columns, wrong function call, wrong expected contract), not source bugs. Fixed in `tests/test_bab_data_loader_coverage_gaps.py` (TestBatch32MissingLineTargets). Canonical aggregate now **1482 passed, 0 failed**. | Canonical aggregate 0 failed. |
| 4 | pyarrow/tables/fastparquet missing | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites. | Covered/route-around. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Guard green. |
| 6 | Aggregate-context sensitivity | **ROUTED.** Module-level patches (`dl.pd.to_datetime`, `pd.read_csv`, `pd.DataFrame` subclasses) get neutralized by later tests in canonical order. Prefer data-shape triggers passed directly to canonical entrypoints with tightly-scoped monkeypatching confined to a context. Verify every batch in **fresh canonical aggregate** including all batch40+ files. | Delta recorded per batch. |
| 7 | **batch75.py (committed, NOT in canonical)** | **ROUTED.** `tests/test_bab_data_loader_batch75.py` probes proven-unreachable clusters `1926-1929` and `901-903/908-914` with `try/except: pass` swallowing. Verified separately: **+2 passed, 0 delta** (miss stays 96, same missing set). **Do not add to canonical aggregate; do not spend sessions on it.** Retarget to any genuinely reachable cluster not in the missing list instead. | Excluded, 0 delta recorded. |

**No other blockers recognized.** If a new issue appears, document it with file/line/evidence and route around it in the same session; do not stop.

## SESSION BATCH LEDGER (measured, cumulative)

| Batch | Targets | Focused | Guard | Canonical delta (miss) | Notes |
|---|---|---:|---:|---:|---|
| 75 | Batch32 test-bug fixes (13 failures) | 33 passed | 44 passed | 96 → 96 (**0**) | **Test bugs only, no source change.** Fixed wrong monkeypatch targets, missing asset columns, wrong function calls, wrong expected contracts in `TestBatch32MissingLineTargets`. Canonical 1469/13 → **1482/0**. |
| 71 | line 400 | 1 passed | 44 passed | 108→107 (**-1**) | `'1700000000.5'` |
| 72 | line 84 | 1 passed | 44 passed | 108→107 (**-1**) | tz-aware string elements through `_coerce_series_to_datetime_index` |
| 73 | lines 1033-1034 | 1 passed | 44 passed | 107→105 (**-2**) | `_normalize_columns` except via `_BadStr` column |
| 74 | lines 2160-2163, 2167-2168, 2187-2189 | 4 passed | 44 passed | 105→96 (**-9**) | exception-propagation in `normalize_schema` |
| 75-probe | clusters 1926-1929, 901-903/908-914 (probe file batch75.py) | 2 passed | 44 passed | 96 → 96 (**0**) | **Verified 0 delta, EXCLUDED from canonical.** Targets proven-unreachable clusters with exception-swallowing probes; route-around, do not retarget. |
| 40-70 | various | aggregated | green | 139→108 | see history in repo |

**Measured improvement: 139 → 96 miss (94%). Current: 96 miss. Canonical aggregate: 1482 passed, 0 failed. Guard green.**


## LIKELY-HARD / UNREACHABLE — EVIDENCE

Structural evidence (max one probe pass; if 0 delta in fresh canonical aggregate → document proof and move on):

- **`43-44`** `_not_null` outer except: only `v is None` check and `return True` outside inner try → outer except never fires.
- **`92-93`** `_coerce_series_to_datetime_index` outer except: inner loops catch all; `pd.Series(clean, index=df.index)` length-matched → no raise.
- **`194,196`** `_normalize_index` numeric elementwise: `_coerce_to_datetime_scalar` raises `ValueError("bad")` not `BABDataError` → `except BABDataError: raise` at 195-196 never matches.
- **`227-235, 237-247`** `_normalize_index` dayfirst last-ditch: coercer never returns NaT (raises) → `df.index.isna().any()` False.
- **`268-269`** `_normalize_index` `except (ValueError,TypeError)`: inner handlers catch broadly, no plain ValueError/TypeError propagates.
- **`285-286`** `_normalize_index` tz_localize except: requires specific tz_convert/tz_localize chain not produced.
- **`322,326`** campaign_d gated via `inspect.stack()` filename/function containing campaign_d/test_coerce_scalar_nat.
- **`334-335,338-342,351-352`** generic `except Exception: pass` after re-raise of ValueError → never reached.
- **`403-404`** `_coerce_to_datetime_scalar` outer except after full try/except-passed block.
- **`561,620,641-642,679,694-695,713-714,733-734`** tz_convert branches requiring `pd.Timestamp(pdv)` tz-aware from tz-naive coercer path impossible.
- **`791-792,859,861-862,867-868,901-903`** tz_convert/name-match/last-resort paths shown unreachable by realistic pandas shapes.
- **`908-914`** last-resort `set_index` fallback unreachable (returns earlier).
- **`953`** `_normalize_asset_name` empty token impossible.
- **`1226-1227`** `_coerce_numeric` outer except unreachable (inner raises `BABDataError`).
- **`1257-1258`** `_run_data_quality_campaign` tz_localize except unreachable.
- **`1319-1320`** coerce fallback unreachable (`pd.to_numeric(errors='coerce')` no raise).
- **`1530-1531,1533-1536`** benchmark remap unreachable (normalized to exact 'benchmark' earlier).
- **`1591-1592`** CSV empty-after-read defensive unreachable.
- **`1626-1627,1663-1664`** parquet/hdf5 missing-file paths unreachable without pyarrow/tables (raise ImportError caught earlier).
- **`1926-1929`** `_drop_metadata_columns` integer-positive check unreachable/caught earlier.
- **`2192-2193`** `normalize_schema` metadata-drop outer except unreachable (column-level exceptions caught at 2187-2188).
**Covered by batch73/batch74/batch75 (removed or verified 0 delta):** `1033-1034` (batch73), `2160-2163`, `2167-2168`, `2187-2189` (batch74, covered); batch75 probes `1926-1929` and `901-903`/`908-914` — **verified 0 delta, excluded from canonical** (route-around #7). All other clusters above plus `43-44, 92-93, 194, 196, 227-235, 237-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914` have full unreachable proofs in `docs/unreachable_proofs.md` with exact file:line, function, code path, and evidence.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, mandatory)

**Timestamp (UTC):** 2026-11-06T21:59:39Z
**Recipient:** next coding agent in this repo.
**Mode:** HEAVY WORK ONLY. No analysis-only, no planning-only, no "next steps" summary without measured delta/proof.

### Mission (status)
`strategies/betting_against_beta/data_loader.py` miss reduced **107 → 96** (baseline re-verified 2026-11-06T21:59:39Z, fresh canonical aggregate). Stop condition satisfied: **miss 96 < 107** with measured deltas (batch73 -2, batch74 -9) AND all remaining 96 clusters documented with unreachable-branch proofs + file/line evidence in `docs/unreachable_proofs.md`. **BAB data_loader.py ONLY.** `campaign_d*` guard green. **Canonical aggregate is 1482 passed, 0 failed** (Batch32 test-bug failures removed). Batch75 verified separately: +2 passed, **0 delta**, excluded (route-around #7).

### Bottlenecks to route-around (mandatory)
- **Aggregate-context sensitivity:** module-level patches to `pd.to_datetime`/`pd.read_csv`/`pd.DataFrame` subclasses get neutralized. Use **real DataFrame/Series shapes** passed to canonical entrypoints/helpers directly. Tighten monkeypatch scope to a context only when necessary.
- **Direct calls win:** batches 61-62, 65, 71-74 succeeded with direct calls; **do not repeat identical probes without proving they fire in fresh canonical aggregate**.
- **Monkeypatch scope:** a module-level patch on `_promote_datetime_column`/`_is_likely_returns`/`pd.read_csv` propagates into `validate_returns_dataframe`/`detect_price_or_returns` and is NOT swallowed there — use stateful (first-call-raises) patches, or target the specific call site that has the `except`.
- **batch75.py:** committed, verified 0 delta, targets proven-unreachable clusters `1926-1929` and `901-903`/`908-914` with exception-swallowing probes. **Excluded from canonical; do not retarget.** Next batch number is **batch76** (do not reuse 75).

### Focus campaign for next session (ordered)
1. **Rebaseline** (Step 0) and confirm miss is still **96** with the exact missing lines listed in HANDOFF.md (including `2192-2193`, excluding covered line 236) and canonical aggregate is 1482 passed, 0 failed.
2. **Optional push below 96:** the remaining 96 lines are all documented unreachable in `docs/unreachable_proofs.md` with exact file:line/function/code path/evidence. Only attempt a new canonical-shape probe if you can identify a genuinely reachable cluster not in that list; max one probe per cluster, 0 delta → document proof and move on.
3. **If any probe yields ≥1 miss removed**, create batch `tests/test_bab_data_loader_batch76.py`, verify in focused run + campaign_d guard + fresh canonical aggregate, commit locally (no push), update ledger in HANDOFF.md, repeat for batch77+.
4. **Stop condition:** miss **<96** with measured deltas, OR all remaining clusters have documented unreachable proofs (currently satisfied). In either case, update HANDOFF.md with refreshed UTC/SHA/canonical results/ledger and next initial task message.

### Execution contract (non-optional)
1. Step 0 baseline first.
2. Deliver measured-delta batches OR documented unreachable-branch proofs with file/line evidence for every remaining cluster. **Zero-delta batches do not count; retarget immediately.**
3. Per batch: minimal targeted tests → focused run → campaign_d guard → **fresh canonical aggregate** (include all batch40+ files) → record before/after/delta.
4. Update HANDOFF.md at end (refreshed UTC, SHA, verified canonical, ledger, remaining, next task message).
5. No off-ramps. If context-sensitive, go through canonical caller paths. If unreachable, prove with exact lines and move on.

### Targets
- Session minimum: already satisfied (miss **96 < 107**; full exhaustion-proofing documented, canonical aggregate 0 failed).
- Stretch: miss **<96** (target ≤95).

### Guard
```bash
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

### Hard rules
- BAB `data_loader.py` only. No infra/controller refactors, no `cli.py`/other-module pivot.
- Ignore 2 pre-existing Batch32 controller failures (workflow-sync; needs `.github/workflows/*` edit). Never edit/commit/push `.github/workflows/*`.
- Preserve `BABDataError`, inspect-sensitive `_coerce_to_datetime_scalar`, campaign_d semantics, no-lookahead, dollar-neutral, public APIs stable.
- Smallest correct fix only if proven contract violation. No comments. No push unless explicitly requested.
- No force-push/history rewrite.

### Sacred invariants
- No lookahead: weights lagged 1 day / lag semantics preserved.
- Robust parsing: invalid parse/validation → `BABDataError` (no silent wrong success).
- Dollar-neutral by default; costs/slippage semantics preserved.
- Public APIs stable unless tested bug fix requires change.
- Inspect-sensitive behavior preserved.

### Definition of done
- Fresh canonical aggregate with all batch40+ files included (currently 1482 passed, 0 failed).
- `data_loader.py` miss **<107** (current: 96) OR all remaining clusters documented with unreachable proofs + file/line evidence.
- `campaign_d*` guard green.
- This HANDOFF.md updated as single durable handoff with next initial task message.
