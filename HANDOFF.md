# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T11:25:00Z
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (verified):** `main` @ `689cb5c`. Working tree has **uncommitted** additions: `tests/test_bab_data_loader_batch40.py`, `tests/test_bab_data_loader_batch41.py`, `tests/test_bab_data_loader_batch42.py`, `tests/test_bab_data_loader_batch43.py` (**do not commit/push unless explicitly requested**). `origin/main` unchanged. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement. **No infra/controller refactors. No sidetracks. No pivot to `cli.py`/other modules. No deferral.** Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed aggregate** (or documented unreachable-branch proof **with file/line evidence while immediately moving to the next reachable cluster**). **No early stop.**

## Fresh verified state (2026-11-06T11:25Z)
- **Env:** Python 3.12.3, dependencies installed via pip in user site (`/home/runner/work/_temp/kilo-home/.local/`); pandas/numpy/pytest/coverage available.
- **`campaign_d*` guard (fresh):** must run with `--ignore=tests/test_controller_progress_accounting.py`. Expected green (44 passed previously).
- **Canonical Step 0 aggregate (fresh, completed, includes batch40-43):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py
```
- **Current:** **1288 passed, 13 failed (pre-existing Batch32), 23 skipped, 87 warnings**; **`strategies/betting_against_beta/data_loader.py` — 1693 stmts, 153 miss, 91%** (fresh, 2026-11-06T11:25Z). Do **not** reuse numbers from older timestamps.

## Bottlenecks (route around)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test** | Operator with `workflows` scope only | Never edit/commit/push `.github/workflows/*`. Always gate with `--ignore=tests/test_controller_progress_accounting.py`. | Operator updates workflow. |
| 2 | **`data_loader.py` at 153 miss** | Next BAB agent | No progress without fresh canonical aggregate + `--show-missing` delta. Target reachable clusters with precise patching. | `data_loader.py` miss **<153** (target ≤150, stretch ≤145). |
| 3 | **TestBatch32 pre-existing failures (13)** | Next BAB agent | Ignore; do not fix/debug. Miss delta is authoritative. | Documented. |
| 4 | **pyarrow/tables/fastparquet not installed** | Next BAB agent | Reach parquet/hdf5 branches via monkeypatch. | Covered via monkeypatch. |
| 5 | **_coerce_to_datetime_scalar inspect-sensitive** | Next BAB agent | Do not alter inspect logic; respect campaign_d filename/function behavior. | `campaign_d*` stays green. |

## Missing clusters (fresh 153 miss; recheck before each batch)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 678-680, 694-695, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1626-1627, 1663-1664, 1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`

## Likely-unreachable / caution
- `227-247` (dayfirst elementwise fallback) — likely unreachable post-coercion; prove with counterexample+delta or move on.
- `1626-1627`, `1663-1664` — inner BABDataError likely converts before outer handlers; prove or move on.
- `908-914` — last resort in `_promote_datetime_column`; if unreachable document with evidence.
- `43-44` — `_not_null` outer catch; low value unless concrete path exists.
- Batches 41-43 gave focused passes but no canonical delta — avoid blind fixtures, instrument exact guards/sites.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission (Campaign A continuation):** Reduce `strategies/betting_against_beta/data_loader.py` miss count from **153** in a **fresh canonical aggregate**. **BAB `data_loader.py` only. Heavy working required.** Uncommitted batch files 40-43 exist (37 tests). `campaign_d*` guard must stay green. Current canonical: 1288 passed/13 pre-existing fails/23 skipped → **data_loader 153 miss, 91%**.

**Priority clusters to attack (recheck line-by-line; target measured delta):**
1. **`757-758, 766-767, 770-771, 789-792, 804-805`** — `_promote_datetime_column` named-column: isna iteration exceptions, tz attribute access, elementwise tz apply, index tz_convert after set_index. Patch `pd.Timestamp.tz_convert` / attribute access.
2. **`840-841, 859, 861-864, 867-868`** — named/unnamed column tz elementwise/cleanup exceptions.
3. **`1487-1488, 1490, 1530-1531, 1533-1536`** — `validate_returns_dataframe` retry loop (first `_coerce_numeric` raises BABDataError, drop unparseable cols via `_series_is_parseable`) and benchmark remap rename fallback (force `rename` to raise while case-insensitive remap possible). Batches 41-43 attempted but no delta — hit exact code paths.
4. **`1588-1592`** — `load_returns_from_csv` defensive empty-after-read path.
5. **`678-680, 694-695`** — exchange format epoch/tz exception handlers.
6. **`1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`** — metadata/clean_data defensive branches (patch at exact sites).
7. **Triage remaining small clusters** from the missing list by reading code first.

**Hard rules:**
- **BAB `data_loader.py` only.** No infra/controller refactors, no pivot to `cli.py`/other modules.
- **No progress count without fresh canonical aggregate measured miss-count delta** OR **unreachable proof with file/line evidence + immediate move to next reachable cluster**.
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session unless reachable clusters exhausted with evidence. Each batch = focused tests (e.g. `tests/test_bab_data_loader_batch44.py`) → `campaign_d*` guard (`--ignore=tests/test_controller_progress_accounting.py`) → **canonical Step 0 aggregate** → recorded delta. If delta 0, retarget before continuing.
- **Route around:** ignore `TestBatch32` pre-existing failures (13). Never edit/commit/push `.github/workflows/*`.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar`), campaign_d semantics. Smallest correct fix only for proven contract violations. No comments. No push unless explicitly requested.

**Execution steps (in order):**
1. **Step 0 (mandatory):** Run canonical aggregate + `coverage report --include='*data_loader.py' --show-missing`. Record baseline (153 miss). Confirm `campaign_d*` guard green.
2. **Batches 44,45,46+:** Create adversarial focused tests using `tmp_path`. Monkeypatch at exact call sites (`dlmod.*`, bound `pd`/`np` symbols). Assert real behavior/`BABDataError`. No empty/pass-only tests.
3. **After each batch:** focused → `campaign_d*` guard → canonical aggregate → compute delta vs previous fresh aggregate. If delta==0, analyze and retarget (count only batches with delta toward throughput).
4. **Loop until** ≥3 batches with measured delta OR reachable clusters exhausted with file/line evidence.
5. **End condition:** Fresh canonical aggregate shows `data_loader.py` miss **<153** (target ≤150). Update `HANDOFF.md` with new UTC timestamp, verified numbers, batch ledger (batch/targets/focused/guard/aggregate before→after/delta/notes), remaining clusters, and next initial task message.

**Verification commands:**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages

# Step 0 baseline
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py
python3 -m coverage report --include='*data_loader.py' --show-missing

# Guard after each batch
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

## Sacred invariants
- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** invalid parse/validation → `BABDataError` (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` and campaign_d semantics.
- No force-push/history rewrite. No fake persistence/remote claims. **No `.github/workflows/*` edits/commits/pushes.** No push unless explicitly requested.
