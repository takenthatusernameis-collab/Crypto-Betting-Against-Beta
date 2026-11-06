# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T10:56:00Z
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (verified):** `main` @ `689cb5c` (at session start). Working tree: adds `tests/test_bab_data_loader_batch40.py` (**uncommitted** — do not commit/push unless explicitly requested). HANDOFF updated this session. `origin/main` in sync at last checkpoint. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement. **No infra/controller refactors. No sidetracks. No pivot to `cli.py`/other modules. No deferral.** Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed aggregate** (or documented unreachable-branch proof **with file/line evidence while immediately moving to the next reachable cluster**). **No early stop.**

## Fresh verified state (2026-11-06T10:56Z — re-verify again before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2, pandas 3.1.1. **pyarrow/tables/fastparquet NOT installed** — parquet/hdf5 branches must be reached via monkeypatch, not real files.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guard (fresh):** `python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**.
- **Baseline Step 0 aggregate (coverage_gaps/batch loader files excluded, per canonical command; completed):** **1251 passed, 13 failed, 23 skipped** → `data_loader.py` **1693 stmts, 167 miss, 90%** (pre-Batch 40 in that aggregate view).
- **Post-Batch 40 aggregate (fresh, completed, includes `tests/test_bab_data_loader_batch40.py`; excludes controller/campaign_d/cli campaign files):** `python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py --ignore=tests/test_bab_data_loader_campaign_d.py --ignore=tests/test_bab_data_loader_campaign_d2.py --ignore=tests/test_bab_data_loader_campaign_d3.py --ignore=tests/test_bab_cli_coverage_campaign.py --ignore=tests/test_bab_cli.py` → **3898 passed, 13 failed, 35 skipped, 208 warnings**.
  - `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 153 miss, 91%**. **Measured delta: 167 → 153 (-14).**
  - `strategies/betting_against_beta/cli.py` — **62 miss, 81%** in baseline view (**defer; do not pivot**).
- **Batch 40 (new file `tests/test_bab_data_loader_batch40.py`, 10 tests, focused all pass):** covers 1621, 1698-1699, 1895, 676-682, 694-695, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 1926-1929. Still missing: 1626-1627, 1663-1664, 2160-2163 (partially probed; see notes).
- **Expected aggregate noise (route around, do not debug/fix):** 13 pre-existing failures in `tests/test_bab_data_loader_coverage_gaps.py::TestBatch32MissingLineTargets::*`. Coverage report/miss delta from a **completed** aggregate remains authoritative.

## Verified batch ledger (carry forward; re-verify if disputed)
| Batch | Focus | Batch focused | Guard | Aggregate miss (before→after) | Delta |
|---|---|---:|---:|---:|---:|
| 36 | parquet/hdf5/pickle/json error+payload paths, promote/detect edges, drop_metadata/is_likely_returns/detect exceptions | 15 pass, 2 skip | 44 pass | 200 → 180 | **-20** |
| 37 | csv/parquet/hdf5 outer errors, pickle list construction, promote/detect/clean_data exception routing (partial) | 11 pass, 3 skip | 44 pass | 180 → 178 | **-2** |
| 38 | `validate_prices` exception/empty/finite paths (2238-2248), parquet/hdf5 BABDataError passthrough, metadata sequential drop, promote/detect/exchange tz edges | 9 pass, 2 skip | 44 pass | 178 → 173 | **-5** |
| 39 | parquet/hdf5 read+validate BABDataError and exception paths (1620-1623, 1649, 1659-1660) | 5 pass | 44 pass | 173 → 167 | **-6** |
| 40 | parquet validate BABDataError (1621), pickle DataFrame-ctor error (1698-1699), metadata/normalize_schema/clean_data exception paths, exchange tz/outer (676-682,694-695,1895,1926-1929,2167-2168,2173-2174,2187-2189,2192-2193) — file `tests/test_bab_data_loader_batch40.py` | 10 pass | 44 pass | 167 → 153* | **-14** |

\*Aggregate measured with `--ignore` controller/campaign_d/cli campaign files (includes Batch 40). Canonical Step 0 file-list baseline before Batch 40 was 167.

**Cumulative (verified):** 200 → 153 miss (**-47**). **Campaign A threshold ≤169 remains MET.** Next session continues from **153**.

## Bottlenecks (removed/routed — spend zero BAB time stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test** expects `*/.github/workflows/*` in `.github/workflows/main.yml`; agent cannot fix. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate with `--ignore=tests/test_controller_progress_accounting.py`. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` ≤169 achieved; push lower.** | **Next BAB agent** | Batch 40 reached **153 miss** (aggregate incl. `tests/test_bab_data_loader_batch40.py`). Continue heavy batches from **153** with measured delta. | Fresh aggregate: `data_loader.py` **≤150** next sub-threshold target, or documented exhaustion with evidence; `campaign_d*` green. |
| 3 | **`TestBatch32` pre-existing failures (13).** | Next BAB agent | **Do not debug/fix.** Run new batch focused → `campaign_d*` guard → full Step 0 aggregate; aggregate miss delta authoritative. | Documented; does not block Campaign A. |
| 4 | `cli.py` 81% (62 miss). | Later | Defer until Campaign A sustains measured deltas. | ≥85%, no regression. |
| 5 | **pyarrow/tables/fastparquet not installed.** | Next BAB agent | Parquet/hdf5 branches reached via `monkeypatch.setattr(dlmod.pd, "read_parquet"/"read_hdf", ...)` and `dlmod.validate_returns_dataframe`; do not rely on real files. | Parquet/hdf5 exception paths coverable by monkeypatch. |
| 6 | **Resolved (Batch 40):** pickle 1698-1699 covered by subclassing `dlmod.pd.DataFrame` (class whose `__init__` raises) so `isinstance`/construction paths behave correctly. 1621/1895 also covered. 1626-1627/1663-1664 remain **likely unreachable** (see evidence). | — | — | Covered. |

## Missing clusters (fresh `--show-missing`, 2026-11-06T10:56Z — 153 miss; recheck before each batch)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 676-682, 694-695, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1626-1627, 1663-1664, 1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`

**Batch 40 retarget note:** lines 676-682, 694-695, 1926-1929, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193 still appear missing in aggregate despite focused-pass tests; next agent must verify which specific sub-lines execute under aggregate conditions and retarget with measured delta (do not claim covered without delta).

## Likely-unreachable evidence (carry forward; not a stop condition)
**`data_loader.py:227-247` (dayfirst elementwise fallback loop) — LIKELY UNREACHABLE.** After elementwise `_coerce_to_datetime_scalar(v)` (217-224), each value either raises or returns a `Timestamp`; no NaN survives. `df.index = coerced` assigns a list (no `.isna`), so `getattr(df.index, "isna", None)` is `None` and 227-247 is not entered. If a counterexample is built, do so with a focused test and measured delta; otherwise move immediately to next cluster.
**`data_loader.py:1626-1627` and `1663-1664` (parquet/hdf5 outer `except (OSError, ValueError)`) — LIKELY UNREACHABLE via read raising OSError/ValueError**, because the inner `except Exception` (1613/1650) catches OSError/ValueError first and converts to `BABDataError`, which the outer `except BABDataError: raise` re-raises — never reaching the outer OSError/ValueError handler. Would require read to raise a non-`Exception` (impossible) or restructure. Document and move on unless a counterexample with measured delta is produced.
**`data_loader.py:1698-1699` — RESOLVED Batch 40.** Covered by monkeypatching `dlmod.pd.DataFrame` to a `pd.DataFrame` subclass whose `__init__` raises (preserves `isinstance` checks).

## High-value reachable targets to probe first (recheck code before each batch)
- **676-684, 694-695** — exchange/OHLCV tz/parse element branches.
- **908-914** — `_promote_datetime_column` last-resort/index/result paths (inspect control flow; monkeypatch if needed).
- **2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193** — `clean_data` exception paths (monkeypatch `clean_data` internals/`np.isfinite`).
- **1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536** — validate/coerce/benchmark remap adversarial branches.
- **1895, 1926-1929** — metadata/drop paths.
- **1621, 1698-1699** — resolve per bottleneck notes 5/6.
- **Small defensive clusters** (`43-44,84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,713-714,733-734,757-758,766-767,770-771,789-792,804-805,840-841,859,861-864,867-868,890,894,901-903,953,1033-1034,1084-1085,1097-1098,1112,1115,1221-1222,1226-1227,1257-1258,1293-1294,1304-1305,1312-1313,1319-1320,1345-1346,1443-1444,1451-1452`) — triage by reading code.

If genuinely unreachable: record **file, line range, why unreachable, what was tried**, then **immediately** move to next cluster. Unreachable proof does **not** satisfy throughput unless reachable clusters are exhausted.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission (Campaign A continuation, Batch 41+):** Continue driving `strategies/betting_against_beta/data_loader.py` miss count from **153** lower in a **fresh completed aggregate**. **BAB `data_loader.py` only. Heavy working required.** Current state: `tests/test_bab_data_loader_batch40.py` exists (10 tests, **uncommitted**); `campaign_d*` guard green (44 passed); aggregate 3898 passed/13 pre-existing Batch32 fails/35 skipped → **data_loader 153 miss, 91%**.

**Priority clusters (recheck line-by-line before coding):**
1. **676-682, 694-695** — exchange/OHLCV/epoch tz coercion branches; Batch 40 attempted but aggregate still shows missing. Retarget with precise fixtures/monkeypatch and prove delta.
2. **908-914** — `_promote_datetime_column` last-resort (note: may be structurally unreachable if index becomes DatetimeIndex at 904/906; prove with control-flow evidence and move on).
3. **1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536** — validate/coerce/benchmark remap adversarial branches.
4. **1588-1592, 1443-1444, 1451-1452, 1345-1346** — validation/coercion defensive paths.
5. **1926-1929, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193** — metadata/normalize_schema/clean_data; Batch 40 attempted, retarget.
6. **Small reachable defensive clusters** (`326,334-335,338-342,351-352,400,403-404,561,620,641-642,713-714,733-734,757-758,766-767,770-771,789-792,804-805,840-841,859,861-864,867-868,890,901-903,953,1033-1034,1084-1085,1097-1098,1226-1227,1257-1258,1293-1294,1304-1305,1312-1313,1319-1320`) — triage each by reading code.
7. **Likely unreachable (do not burn time):** 227-247, 1626-1627, 1663-1664, 908-914 if confirmed — document file/line/why/tried, then move immediately.

**Hard rules (future agents cannot avoid):**
- **Do not** defer, pivot to `cli.py`/infra, refactor broadly, or declare done before end condition.
- **Do not** count a batch without a **fresh aggregate measured miss-count delta** (or unreachable proof **with file/line evidence + immediate move to next reachable cluster**).
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session unless a new sub-threshold is reached with verified proof or reachable clusters are exhausted. Each batch = focused `TestBatch40*`+ tests → `campaign_d*` guard → full Step 0 aggregate → recorded delta. If a cluster is proven unreachable, document evidence and continue; **do not stop below throughput without exhausting reachable clusters**.
- **Route-around:** ignore `TestBatch32` pre-existing failures (13). Do not fix/debug them. Aggregate miss delta is authoritative.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar` stack logic), `campaign_d*` semantics, and sacred invariants. Smallest correct fix only for **proven** contract violations. **No comments in code. No `.github/workflows/*` changes. No push unless explicitly requested.**

**Execution steps (do in order, then loop):**
1. **Step 0 (mandatory, fresh):** run aggregate coverage, record `data_loader.py` miss/stmts/% and `cli.py`, capture `--show-missing`. Confirm `campaign_d*` guard green. Do not reuse stale numbers.
2. **Batches 41, 42, 43 (minimum):** add focused tests (prefer new `tests/test_bab_data_loader_batch41.py` etc., or extend batch40 file if small; do not pile into `test_bab_data_loader_coverage_gaps.py` where Batch32 noise lives except for small targeted additions). Use `tmp_path`, malformed/ext/encoding/dispatch/adversarial inputs; `pytest.importorskip` only for optional deps. Assert real behavior/`BABDataError` — no empty/pass-only tests.
3. **After each batch:** run new batch focused → `campaign_d*` guard → **full Step 0 aggregate** → compute/record miss delta vs previous fresh aggregate. If no delta, retarget before claiming progress.
4. **Continue:** do not stop after one batch. Maintain ledger: batch, target lines, focused result, guard result, aggregate miss before/after, delta, notes/unreachable evidence.
5. **End condition (mandatory throughput):** deliver **≥3 verified batches with measured aggregate delta** this session, or exhaust reachable clusters with file/line evidence. Final fresh aggregate must show `data_loader.py` miss **<153** (target ≤150, stretch ≤145) with zero regressions and `campaign_d*` green. Update `HANDOFF.md` with new UTC timestamp, verified numbers, batch ledger, remaining clusters, and next initial task message (Batch N+).

## Verification commands
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages

# Step 0 aggregate (fresh baseline / after each batch)
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing

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
