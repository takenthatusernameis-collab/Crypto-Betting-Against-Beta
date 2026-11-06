# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **This is the only durable handoff.** Read fully, then execute the **INITIAL TASK MESSAGE** below. No off-ramp, no sidetrack, no status-only session.

**Handoff refreshed (UTC):** 2026-11-06T15:36:26Z
**Last fresh canonical verification (UTC):** 2026-11-06T15:36:26Z (Step 0 rerun this session, includes `tests/test_bab_data_loader_batch54-57.py`)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (pre-session, verify):** `main` @ `960c0e8` (recheck with `git rev-parse --short HEAD`). Working tree includes `HANDOFF.md` update + new `tests/test_bab_data_loader_batch55.py`, `batch56.py`, `batch57.py` (uncommitted). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

---

## PRIORITY (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement.

- **No** infra/controller refactors. **No** sidetracks. **No** pivot to `cli.py`/other modules.
- Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, **or** a documented unreachable-branch proof **with file/line evidence** while immediately moving to the next reachable cluster.
- A session that ends with "reviewed code", "ran baseline only", or "planned next steps" without measured delta/proof is a failed session.

## VERIFIED STATE (fresh canonical: 2026-11-06T15:36:26Z)
- **Env:** Python 3.12.3. Deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages` (pandas/numpy/pytest/coverage present). pyarrow/tables/fastparquet not installed — monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batch40-57 included):** **1384 passed, 13 failed (pre-existing Batch32/coverage_gaps only), 23 skipped, 93 warnings**.
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 114 miss, 93%.** **No canonical delta this session** (114→114); batches 55-57 added regression probes but did not hit the remaining missing lines in aggregate.
- **Missing lines (exact, 114; recheck with `--show-missing` at baseline):** `43-44,84,92-93,194,196,227-247,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,679,694-695,713-714,733-734,791-792,859,861-862,867-868,894,901-903,908-914,953,1033-1034,1097-1098,1226-1227,1257-1258,1293-1294,1319-1320,1530-1531,1533-1536,1591-1592,1626-1627,1663-1664,1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`.
- **Step 0 baseline command (run first; include all batch files that exist):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py
python3 -m coverage report --include='*data_loader.py' --show-missing
```
  *If batch58+ exist, append them to the command.*

## BOTTLENECKS — REMOVED / ROUTED (do not let these block progress)
| # | Bottleneck | Route-around (mandatory) | Exit condition |
|---|---|---|---|
| 1 | Controller workflow-sync test (`TestControllerProgressAccounting`) | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.** | Operator updates workflow. |
| 2 | `data_loader.py` 114 miss remains | Continue with fresh canonical aggregate + `--show-missing` delta. Patch tests at exact sites through canonical caller paths; if 0 delta, retarget immediately. | miss **<114** (target ≤110, stretch ≤105). |
| 3 | 13 pre-existing Batch32/coverage_gaps failures | Ignore; miss delta is authoritative. | Documented. |
| 4 | pyarrow/tables/fastparquet not installed | Monkeypatch parquet/hdf5/engine branches (`pd.read_parquet/read_hdf` and module call sites). | Covered/route-around. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Guard stays green. |
| 6 | Aggregate-context sensitivity | Isolated probes may differ from aggregate hits; always verify delta in **fresh canonical aggregate**. | Canonical delta recorded per batch. |
| 7 | Batches 55-57 gave 0 canonical delta | Do not count toward measured-delta requirement; retarget with canonical-caller/stateful patches and prove unreachable only with file/line evidence. | Next session records measured delta or proof. |

**No other blockers are recognized.** If a new issue appears, document it with evidence and route around it in the same session; do not stop.

## SESSION BATCH LEDGER (measured, cumulative)
| Batch | Targets | Focused | Guard | Canonical delta (data_loader miss) | Notes |
|---|---|---:|---|---:|---|
| 44 | 1487-1490/1588-1592/194,196 probes | 1 passed | 44 passed | 153→153 (0) | No canonical delta in isolation; kept. |
| 45 | 1487-1490 retry drop, 1530-1536 benchmark remap, promote/unnamed/clean_data handlers | 9 passed | 44 passed | 153→145 (**-8**) | Hit 1487-1490 and parts of remap/defensive paths. |
| 46 | range/epoch/tz/defensive probes | 10 passed | 44 passed | 145→139 (**-6**) | Context-dependent targets remain. |
| 47 | epoch/unnamed-tz/remap/clean_data probes | 9 passed | 44 passed | 139→139 (0) | Retargeted. |
| 48 | promote/unnamed-tz (`_promote_datetime_column`) | 4 passed | 44 passed | contributed in aggregate | Committed `5f5d7d0`. |
| 49 | 1530-1531 rename fallback, 1591-1592 CSV empty-after-read, 1451-1452 trivial-1970 except | 3 passed | 44 passed | 139→133 (**-6**) | Committed `5f5d7d0`. |
| 50 | dt-attr/dtype-tz, outer tz-normalize, name-match, unnamed-tz, remap probes | 6 passed | 44 passed | 133→131 (**-2**) | Committed `24264a2`. |
| 51 | set_index ValueError, RangeIndex year-raises, rename fallback, stateful empty, clean_data probes | 7 passed | 44 passed | 131→127 (**-4**, 51+52) | Committed `24264a2`. |
| 52 | promote handlers, exchange/epoch/tz, loaders, price metadata | 6 passed | 44 passed | (with 51) | Committed `24264a2`. |
| 53 | promote handlers, rename, CSV empty (canonical-leaning probes) | 6 passed | 44 passed | 127→124 (**-3**) | Committed `24264a2`. |
| 54 | promote/dtype-tz/elementwise/unnamed-tz/interval/parsed-tz/last-resort/QA handlers | 12 passed | 44 passed | 124→114 (**-10**, canonical aggregate) | `tests/test_bab_data_loader_batch54.py`. |
| 55 | name-match set_index/apply exception paths, unnamed-tz, last-resort tz, benchmark remap, CSV defensive, exchange epoch, clean_data, last-resort set_index | 10 passed | 44 passed | 114→114 (0) | **0 delta** in canonical aggregate (2026-11-06T15:36:26Z). Kept as probes; retarget required. |
| 56 | flaky benchmark remap, CSV stateful empty, duplicate header, exchange open_time epoch, detect unknown, parquet engine fallback | 6 passed | 44 passed | 114→114 (0) | **0 delta**. Kept. |
| 57 | coerce_series tz, clean_data junk drop, DatetimeIndex tz norm, exchange normalize, benchmark case, hdf5 fallback | 6 passed | 44 passed | 114→114 (0) | **0 delta**. Kept. |

**Measured improvement (historical window): 139 → 114 miss (93%). This session:** 114→114 (0 delta), guard green.

## LIKELY-UNREACHABLE / CAUTION (evidence required; do not stall)
- `227-247` (`_normalize_index` dayfirst elementwise fallback) — hard to reach after earlier `pd.to_datetime`/coercion; attempt via index values that pass first checks but fail later in canonical path, else file/line evidence.
- `791-792` (name-match elementwise tz apply fallback) — requires `parsed.apply` to raise in canonical promote path with exact object shape.
- `859,861-862,867-868,894,901-903,908-914` — `_promote_datetime_column` unnamed/last-resort handlers; require exact Series/parsed shapes and tz/dtype combinations visible in canonical flows.
- `1530-1531,1533-1536` — `validate_returns_dataframe` remap fallbacks; batch55/56 probed but did not hit in aggregate; need precise column/index state after cleaning.
- `1591-1592` — `load_returns_from_csv` second empty check; may need subclass/stateful `df.empty` that survives read/validation sequence.
- `1926-1929,2160-2163,2167-2168,2187-2189,2192-2193` — `clean_data` duplicate-header/junk/drop defensive branches.
- `679,694-695,713-714,733-734` — exchange epoch/tz normalization branches.
- `1226-1227,1257-1258,1293-1294,1319-1320` — coerce/detect loader handlers.
- `1626-1627,1663-1664` — inner `BABDataError` may convert before outer handlers; prove or move on.
- `43-44,84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,953,1033-1034,1097-1098` — inspect/defensive/rare parse/QA branches; triage early with evidence.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, mandatory)

**Timestamp (UTC):** 2026-11-06T15:36:26Z
**Recipient:** next coding agent in this repo.
**Mode:** HEAVY WORK ONLY. No analysis-only turn. No planning-only turn.

### Mission
Reduce `strategies/betting_against_beta/data_loader.py` miss count from **114** (fresh canonical 2026-11-06T15:36:26Z; **rebaseline at Step 0**) in a **fresh canonical aggregate**. **BAB `data_loader.py` only.** Every batch must yield a **measured miss-count delta** or a **documented unreachable-branch proof with file/line evidence**, then immediately move to the next reachable cluster. `campaign_d*` guard must stay green.

### Focus campaign (ordered; do not avoid)
1. **`791-792,859,861-862,867-868,894,901-903,908-914`** — `_promote_datetime_column` handlers. Use canonical callers (`validate_returns_dataframe`/`load_returns*`/`clean_data` paths) and stateful `pd.to_datetime`/`DataFrame.set_index`/module attribute patches that fire in aggregate. Target exact object shapes (parsed with `apply` raising; unnamed coerced tz-aware elements; last-resort parsed tz/DatatimeIndex coercion failures).
2. **`1530-1531,1533-1536`** — `validate_returns_dataframe` benchmark remap. Reproduce the exact state where `bench_found != benchmark` is set, first rename raises, `benchmark` still absent, then bench_map fallback renames. Avoid flaky rename affecting unrelated columns.
3. **`1591-1592`** — `load_returns_from_csv` defensive empty-after-read. Use a `pd.DataFrame` subclass whose `empty` property is stateful across first/second checks in that function.
4. **`679,694-695,713-714,733-734`** — `_detect_and_normalize_exchange_format` epoch/tz branches via canonical `clean_data`/`load_prices`/`validate` entrypoints.
5. **`1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`** — `clean_data` defensive branches (duplicate header row removal, junk column drop/to_numeric/exception paths).
6. **`1226-1227,1257-1258,1293-1294,1319-1320,1097-1098`** — coerce/detect/QA handlers through canonical APIs.
7. **Triage early with evidence (max one probe pass each, then move on):** `227-247`, `43-44,84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,953,1033-1034,1626-1627,1663-1664`.

### Execution contract (non-optional)
1. **Run Step 0 baseline first** and record actual `data_loader.py` miss count + exact missing lines before changes.
2. **Deliver ≥3 verified batches** this session (`tests/test_bab_data_loader_batch58.py`, `batch59.py`, `batch60.py`, …) unless reachable clusters are exhausted with evidence. **Zero-delta batches do not count toward the 3; retarget immediately.**
3. For **each batch:** minimal targeted tests → focused run → `campaign_d*` guard → **fresh canonical aggregate** (include all batch40+ files that exist) → record before/after miss count and delta. Commit locally only if safe; **do not push** unless explicitly requested.
4. **Update this HANDOFF.md** at session end: refreshed UTC timestamp, SHA, verified canonical result, batch ledger rows (delta or unreachable proof), remaining clusters, and the next initial task message. Keep it the single durable handoff.
5. **No off-ramps:** no stopping at analysis/planning. If context-sensitive, craft inputs through canonical caller paths.

### Targets
- **Session minimum:** miss **<114** with ≥3 measured-delta batches (or documented exhaustion with evidence).
- **Target:** ≤110. **Stretch:** ≤105.

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
- `data_loader.py` miss count **<114** (or unreachable-proof exhaustion documented with file/line evidence).
- `campaign_d*` guard green.
- This HANDOFF.md updated as the single durable handoff with next initial task message.
