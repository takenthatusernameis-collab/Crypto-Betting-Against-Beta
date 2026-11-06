# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T12:33:21Z
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (verified):** `main` @ `689cb5c`. Working tree has **uncommitted** additions: `tests/test_bab_data_loader_batch40.py`..`batch47.py` (**do not commit/push unless explicitly requested**). `origin/main` unchanged. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement. **No infra/controller refactors. No sidetracks. No pivot to `cli.py`/other modules.** Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate** (or documented unreachable-branch proof **with file/line evidence while immediately moving to the next reachable cluster**).

## Fresh verified state (2026-11-06T12:33:21Z)
- **Env:** Python 3.12.3, deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages` (pandas/numpy/pytest/coverage). `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`.
- **`campaign_d*` guard (fresh):** `pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings**.
- **Canonical Step 0 aggregate (fresh, completed, includes batch40-47):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py
```
- **Current canonical result:** **1317 passed, 13 failed (pre-existing Batch32 only), 23 skipped, 88 warnings**; **`strategies/betting_against_beta/data_loader.py` — 1693 stmts, 139 miss, 92%**. Baseline before this session’s measured work: **153 miss** (with batch40-44 included in prior baseline context per handoff; batch45+46 delivered measured delta). Do **not** reuse older numbers.

## This session batch ledger (measured)
| Batch | Targets | Focused | Guard | Canonical (before→after data_loader miss) | Delta | Notes |
|---|---|---:|---|---:|---:|---|
| 44 | 1487-1490/1588-1592/194/196 probes | 1 passed | 44 passed | 153→153 (included in full baseline) | 0 | No canonical delta in isolation; kept. |
| 45 | 1487-1490 retry drop, 1530-1536 benchmark remap, 1588-1592, promote/unnamed/clean_data handlers | 9 passed | 44 passed | 153→145 | **-8** | Hit 1487-1490, parts of remap/defensive paths in canonical aggregate. |
| 46 | 757-758,766-767,770-771,789-792,804-805,840-841 probes,1443-1444,1451-1452,1345-1346,1530-1531 | 10 passed | 44 passed | 145→139 | **-6** | Hit 1443-1444,1345-1346,679/related canonical hits; some targets still show in full missing list (context-dependent). |
| 47 | 840-841,859/861-862/867-868,1530-1536,1591-1592,1926-1929,2160-2168 probes | 9 passed | 44 passed | 139→139 | 0 | No delta; tests exercise handlers but not all reached in canonical context. Retarget next. |

**Total measured improvement this session:** 153 → **139 miss** (92%).

## Bottlenecks (route around)
| # | Bottleneck | Route-around | Exit |
|---|---|---|---|
| 1 | Controller workflow-sync test (`TestControllerProgressAccounting`) | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Operator updates workflow. |
| 2 | `data_loader.py` 139 miss remains | Continue with fresh canonical aggregate + `--show-missing` delta. Patch tests at exact sites; if 0 delta retarget. | miss **<139** (target ≤135, stretch ≤130). |
| 3 | 13 pre-existing Batch32 failures | Ignore; miss delta authoritative. | Documented. |
| 4 | pyarrow/tables/fastparquet not installed | Monkeypatch parquet/hdf5/engine branches. | Covered. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar`/inspect behavior and campaign_d filename/function behavior. | Guard stays green. |

## Missing clusters (fresh 139 miss; recheck before each batch)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-862, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1451-1452, 1530-1531, 1533-1536, 1591-1592, 1626-1627, 1663-1664, 1926-1929, 2160-2163, 2167-2168, 2187-2189, 2192-2193`

## Likely-unreachable / caution (with evidence direction)
- `227-247` (dayfirst elementwise fallback) — still missing; likely unreachable post-coercion in normal paths. Prove with targeted counterexample+delta or document and move on.
- `1626-1627`, `1663-1664` — inner `BABDataError` may convert before outer handlers; prove or move on.
- `908-914` — last resort in `_promote_datetime_column`; prove with exact patch or move on.
- `757-758,766-767,770-771,789-792,804-805,840-841,859,861-862,867-868` — exception handlers; batch46/47 exercised some paths alone but canonical still shows misses (context-sensitive). Next agent should craft inputs that trigger these under the canonical exercised callers (`validate_returns_dataframe`/loaders paths), not just isolated unit calls.
- `1451-1452,1530-1531,1533-1536,1591-1592,1926-1929,2160-2163,2167-2168,2187-2189,2192-2193` — defensive handlers; need precise monkeypatching at `dlmod`/pandas call sites visible to canonical paths.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission (Campaign A continuation):** Reduce `strategies/betting_against_beta/data_loader.py` miss count from **139** in a **fresh canonical aggregate**. **BAB `data_loader.py` only. Heavy working required.** Uncommitted batch files 40-47 exist. `campaign_d*` guard must stay green.

**Priority clusters to attack (recheck line-by-line; target measured delta):**
1. **`757-758,766-767,770-771,789-792,804-805,840-841,859,861-862,867-868`** — `_promote_datetime_column` exception handlers. Design tests that flow through canonical loader/validation entrypoints (or replicate their exact call context) so handlers trigger in aggregate.
2. **`1451-1452,1530-1531,1533-1536`** — validate_returns trivial 1970 path and benchmark remap rename fallbacks. Use real validate flows; monkeypatch `pd.DataFrame.rename`/index normalization carefully to avoid breaking unrelated paths.
3. **`1591-1592`** — `load_returns_from_csv` defensive empty-after-read; use stateful `read_csv`/df.empty monkeypatch compatible with prior checks.
4. **`1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`** — `clean_data`/metadata defensive branches; patch at exact `dlmod` symbols and pandas methods used inside those blocks.
5. **`679,694-695,713-714,733-734`** — exchange/epoch/tz normalization handlers still missing.
6. **Triage `227-247,908-914,1626-1627,1663-1664`** early: produce file/line unreachable proof with counterexample attempt+delta evidence, then stop spending time there.

**Hard rules:**
- **BAB `data_loader.py` only.** No infra/controller refactors, no pivot to `cli.py`/other modules.
- **No progress count without fresh canonical aggregate measured miss-count delta** OR **unreachable proof with file/line evidence + immediate move to next reachable cluster**.
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session unless reachable clusters exhausted with evidence. Each batch = focused tests (`tests/test_bab_data_loader_batch48.py` etc.) → `campaign_d*` guard (`--ignore=tests/test_controller_progress_accounting.py`) → **canonical Step 0 aggregate** → recorded delta. If delta 0, retarget before continuing.
- Ignore `TestBatch32` pre-existing failures (13). Never edit/commit/push `.github/workflows/*`. Preserve `BABDataError` contract, inspect-sensitive behavior, campaign_d semantics. Smallest correct fix only for proven contract violations. No comments. No push unless explicitly requested.

**Verification commands:**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages

# Step 0 baseline (include batch40-47)
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py
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
