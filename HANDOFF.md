# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T11:15:00Z
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (verified):** `main` @ `689cb5c`. Working tree has **uncommitted** additions: `tests/test_bab_data_loader_batch40.py`, `tests/test_bab_data_loader_batch41.py`, `tests/test_bab_data_loader_batch42.py`, `tests/test_bab_data_loader_batch43.py` (**do not commit/push unless explicitly requested**). HANDOFF updated this session. `origin/main` unchanged. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement. **No infra/controller refactors. No sidetracks. No pivot to `cli.py`/other modules. No deferral.** Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed aggregate** (or documented unreachable-branch proof **with file/line evidence while immediately moving to the next reachable cluster**). **No early stop.**

## Fresh verified state (2026-11-06T11:15Z — re-verify again before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2, pandas 3.1.1. **pyarrow/tables/fastparquet NOT installed** — parquet/hdf5 branches must be reached via monkeypatch, not real files.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guard (fresh):** `python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**.
- **Canonical Step 0 aggregate (fresh, completed, includes batch40-43):** `python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py` → **1288 passed, 13 failed, 23 skipped, 87 warnings**.
  - `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 153 miss, 91%** (fresh canonical aggregate, 2026-11-06T11:15Z).
- **Batch files (all focused pass; uncommitted):** `tests/test_bab_data_loader_batch40.py` (10), `batch41.py` (7), `batch42.py` (10), `batch43.py` (10) → **37 tests pass** focused/combined. **Aggregate delta from batches 41-43 vs batch40-inclusive canonical baseline: 153 → 153 (no measured delta).** Batch 40’s earlier `--ignore`-style aggregate reported 153 in handoff context; canonical Step 0 file-list aggregate is the authoritative baseline going forward — use it consistently.
- **Expected aggregate noise (route around, do not debug/fix):** 13 pre-existing failures in `tests/test_bab_data_loader_coverage_gaps.py::TestBatch32MissingLineTargets::*`. Coverage report/miss delta from a **completed** aggregate remains authoritative.

## Verified batch ledger (carry forward; re-verify if disputed)
| Batch | Focus | Focused | Guard | Canonical aggregate miss (before→after) | Delta |
|---|---|---:|---:|---:|---:|
| 36 | parquet/hdf5/pickle/json error+payload paths, promote/detect edges, drop_metadata/is_likely_returns/detect exceptions | 15 pass, 2 skip | 44 pass | 200 → 180 | **-20** |
| 37 | csv/parquet/hdf5 outer errors, pickle list construction, promote/detect/clean_data exception routing (partial) | 11 pass, 3 skip | 44 pass | 180 → 178 | **-2** |
| 38 | `validate_prices` exception/empty/finite paths (2238-2248), parquet/hdf5 BABDataError passthrough, metadata sequential drop, promote/detect/exchange tz edges | 9 pass, 2 skip | 44 pass | 178 → 173 | **-5** |
| 39 | parquet/hdf5 read+validate BABDataError and exception paths (1620-1623, 1649, 1659-1660) | 5 pass | 44 pass | 173 → 167 | **-6** |
| 40 | parquet validate BABDataError, pickle DF-ctor error, metadata/normalize_schema/clean_data/exchange edges (file `tests/test_bab_data_loader_batch40.py`) | 10 pass | 44 pass | 167 → 153* | **-14** |
| 41 | `_not_null`/normalize_index retry BAB passthrough attempts, promote/validate/CSV defensive edges (`tests/test_bab_data_loader_batch41.py`) | 7 pass | 44 pass | 153 → 153 | **0** (no delta; tests added) |
| 42 | exchange epoch/tz/outer attempts, validate parseable/retry drops, clean_data/metadata edges (`tests/test_bab_data_loader_batch42.py`) | 10 pass | 44 pass | 153 → 153 | **0** (no delta; tests added) |
| 43 | promote tz/unnamed, benchmark remap, CSV empty, clean_data duplicate header/exchange/junk/metadata, validate retry (`tests/test_bab_data_loader_batch43.py`) | 10 pass | 44 pass | 153 → 153 | **0** (no delta; tests added) |

\*Historical measured delta recorded when batch 40 landed in a completed aggregate view; canonical authoritative count is now **153**.
**Cumulative (verified canonical):** 200 → 153 miss (**-47**). **Campaign A threshold ≤169 MET.** Next session continues from **153** and must produce **measured delta**.

## Bottlenecks (removed/routed — spend zero BAB time stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test** expects `*/.github/workflows/*`; agent cannot fix. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate with `--ignore=tests/test_controller_progress_accounting.py`. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` at 153 miss; batches 41-43 added coverage attempts but no aggregate delta.** | **Next BAB agent** | Do **not** claim progress without `--show-missing` delta. Pick clusters with precise control-flow reachability; use monkeypatch at exact call sites (`dlmod.*` and `pd.*`/`np.*` where code binds). If aggregate unchanged, retarget immediately. | Fresh canonical aggregate: `data_loader.py` **<153** (target ≤150, stretch ≤145), `campaign_d*` green. |
| 3 | **`TestBatch32` pre-existing failures (13).** | Next BAB agent | **Do not debug/fix.** Run new batch focused → `campaign_d*` guard → canonical aggregate; miss delta authoritative. | Documented; does not block Campaign A. |
| 4 | `cli.py` lower priority. | Later | Defer until `data_loader.py` shows sustained measured deltas. | ≥85%, no regression. |
| 5 | **pyarrow/tables/fastparquet not installed.** | Next BAB agent | Parquet/hdf5 branches reached via monkeypatch. | Monkeypatch coverage. |
| 6 | **`_coerce_to_datetime_scalar` is inspect-sensitive** (`inspect.stack` checks `campaign_d` filenames/functions). | Next BAB agent | Do not alter inspect logic. Tests hitting 322/326/334-335/338-342 must not run under `campaign_d*.py` filenames and must account for stack behavior. | `campaign_d*` remains green. |

## Missing clusters (fresh canonical `--show-missing`, 2026-11-06T11:15Z — 153 miss; recheck before each batch)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 678-680, 694-695, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1626-1627, 1663-1664, 1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`

## Likely-unreachable / caution evidence (carry forward; not a stop condition)
- **`227-247` (dayfirst elementwise fallback)** — likely unreachable: post-`_coerce_to_datetime_scalar` values become Timestamps; `df.index = coerced` assigns list (no `.isna`), so NaN/NaT guard path not entered. Prove with counterexample+delta or move on.
- **`1626-1627`, `1663-1664`** — likely unreachable: inner `except Exception` converts read OSError/ValueError to `BABDataError`; outer `except BABDataError` reraises before outer OSError/ValueError handlers. Prove with counterexample+delta or move on.
- **`908-914`** — `_promote_datetime_column` last-resort after `df2.index = parsed`/drop sets a DatetimeIndex-like result; 906/907 often return early. Inspect control flow; if unreachable, document file/lines/why/tried and move on.
- **`43-44`** — `_not_null` outer `except Exception` covers `pd.isna` and returns; outer catch only for non-Exception/BaseException escapes (not normal). Low value unless a concrete path exists.
- **Batches 41-43:** focused tests passed and guard stayed green, but **no canonical aggregate miss delta**. Do not reuse the same blind fixtures; instrument by reading exact branch guards and patching the precise object/method the code reads.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission (Campaign A continuation, Batch 44+):** Reduce `strategies/betting_against_beta/data_loader.py` miss count from **153** in a **fresh canonical aggregate**. **BAB `data_loader.py` only. Heavy working required.** Uncommitted batch files 40-43 exist (37 tests total); `campaign_d*` guard green (44 passed); canonical aggregate 1288 passed/13 pre-existing Batch32 fails/23 skipped → **data_loader 153 miss, 91%**.

**Priority clusters (recheck line-by-line before coding; target measured delta):**
1. **`757-758, 766-767, 770-771, 789-792, 804-805`** — `_promote_datetime_column` named-column path: `isna` iteration exception, `parsed.tz`/dtype tz attribute access exceptions, elementwise tz apply exception, index tz_convert exception after set_index. Use tz-aware scalars/series and monkeypatch `pd.Timestamp.tz_convert`/attribute access carefully to hit each handler.
2. **`840-841, 859, 861-864, 867-868`** — named-column `except (ValueError, TypeError, KeyError)` and unnamed-column tz elementwise/cleanup exceptions.
3. **`1487-1488, 1490, 1530-1531, 1533-1536`** — `validate_returns_dataframe` BABDataError retry loop append/drop and benchmark remap rename fallback. Craft a case where first `_coerce_numeric` raises `BABDataError`, then specific columns make `_series_is_parseable`/drop hit 1487-1490; for 1530-1536 force `rename` to raise while case-insensitive remap remains possible.
4. **`1588-1592`** — `load_returns_from_csv` defensive empty-after-read path (subclass/monkeypatch to make `df.empty` behave oddly / raise from second check) — ensure contract still raises `BABDataError`.
5. **`678-680, 694-695`** — exchange format date-coercion inner/outer exception handlers (epoch/tz path). Patch `_coerce_to_datetime_scalar`/`pd.Timestamp` and the specific operations around 645-695.
6. **`1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`** — metadata/clean_data defensive branches. Monkeypatch `np.allclose`/`pd.api.types.is_numeric_dtype`/iteration at the exact loop sites; preserve BABDataError contract where code reraises.
7. **Small reachable defensive clusters** — triage `84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,713-714,733-734,890,894,901-903,953,1033-1034,1084-1085,1097-1098,1112,1115,1221-1222,1226-1227,1257-1258,1293-1294,1304-1305,1312-1313,1319-1320,1345-1346,1443-1444,1451-1452` by reading code first.
8. **Likely unreachable (do not burn time):** `227-247, 1626-1627, 1663-1664, 908-914, 43-44` — document file/line/why/tried, then move immediately.

**Hard rules (future agents cannot avoid):**
- **Do not** defer, pivot to `cli.py`/infra, refactor broadly, or declare done before end condition.
- **Do not** count a batch without a **fresh canonical aggregate measured miss-count delta** (or unreachable proof **with file/line evidence + immediate move to next reachable cluster**).
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session unless reachable clusters are exhausted with evidence. Each batch = focused tests (prefer `tests/test_bab_data_loader_batch44.py` etc.) → `campaign_d*` guard → **canonical Step 0 aggregate** → recorded delta. If a batch yields **no delta**, analyze why, retarget, and count only batches with delta toward throughput.
- **Route-around:** ignore `TestBatch32` pre-existing failures (13). Do not fix/debug them.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar`), `campaign_d*` semantics, and sacred invariants. Smallest correct fix only for **proven** contract violations. **No comments in code. No `.github/workflows/*` changes. No push unless explicitly requested.**

**Execution steps (do in order, then loop):**
1. **Step 0 (mandatory, fresh):** run canonical aggregate coverage, record `data_loader.py` miss/stmts/% and capture `--show-missing`. Confirm `campaign_d*` guard green. Do not reuse stale numbers.
2. **Batches 44, 45, 46 (minimum with delta):** add focused adversarial tests using `tmp_path`, malformed/ext/encoding/dispatch inputs; `pytest.importorskip` only for optional deps. Assert real behavior/`BABDataError` — no empty/pass-only tests. Patch `dlmod.*` and bound `pd`/`np` symbols as needed.
3. **After each batch:** focused tests → `campaign_d*` guard → **canonical aggregate** → compute/record miss delta vs previous fresh aggregate. **If delta is 0, fix targeting before moving on.**
4. **Continue:** maintain ledger: batch, target lines, focused result, guard result, aggregate miss before/after, delta, notes/unreachable evidence.
5. **End condition (mandatory throughput):** deliver **≥3 verified batches with measured aggregate delta** this session, or exhaust reachable clusters with file/line evidence. Final fresh canonical aggregate must show `data_loader.py` miss **<153** (target ≤150, stretch ≤145) with zero regressions and `campaign_d*` green. Update `HANDOFF.md` with new UTC timestamp, verified numbers, batch ledger, remaining clusters, and next initial task message.

## Verification commands
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages

# Canonical Step 0 aggregate (fresh baseline / after each batch) — include batch40+ files
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py
python3 -m coverage report --include='*data_loader.py' --show-missing

# campaign_d* guard (after every batch)
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

## Sacred invariants (never regress)
- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` and campaign_d semantics keep `campaign_d*` passing.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.** No push unless explicitly requested.
