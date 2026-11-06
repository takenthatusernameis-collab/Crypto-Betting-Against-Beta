# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **This is the only durable handoff.** Read fully, then execute the **INITIAL TASK MESSAGE** below. No off-ramp, no sidetrack, no status-only session.

**Handoff refreshed (UTC):** 2026-11-06T15:28:03Z
**Last fresh canonical verification (UTC):** 2026-11-06T14:48:04Z (Step 0 rerun completed prior session, includes `tests/test_bab_data_loader_batch54.py`)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `af6b646` (`origin/main` not pushed; recheck). Working tree has `HANDOFF.md` update in progress only. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

---

## PRIORITY (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement.

- **No** infra/controller refactors. **No** sidetracks. **No** pivot to `cli.py`/other modules.
- Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, **or** a documented unreachable-branch proof **with file/line evidence** while immediately moving to the next reachable cluster.
- A session that ends with "reviewed code", "ran baseline only", or "planned next steps" without measured delta/proof is a failed session.

## VERIFIED STATE (fresh canonical: 2026-11-06T14:48:04Z)
- **Env:** Python 3.12.3. Deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages` (pandas/numpy/pytest/coverage present). pyarrow/tables/fastparquet not installed — monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batch40-54 included):** **1362 passed, 13 failed (pre-existing Batch32/coverage_gaps only), 23 skipped, 93 warnings**.
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 114 miss, 93%.**
- **Missing lines (exact, 114; recheck with `--show-missing` at baseline):** `43-44,84,92-93,194,196,227-247,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,679,694-695,713-714,733-734,791-792,859,861-862,867-868,894,901-903,908-914,953,1033-1034,1097-1098,1226-1227,1257-1258,1293-1294,1319-1320,1530-1531,1533-1536,1591-1592,1626-1627,1663-1664,1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`.
- **Step 0 baseline command (run first; include all batch files that exist):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py
python3 -m coverage report --include='*data_loader.py' --show-missing
```
  *If batch55+ exist, append them to the command.*

## BOTTLENECKS — REMOVED / ROUTED (do not let these block progress)
| # | Bottleneck | Route-around (mandatory) | Exit condition |
|---|---|---|---|
| 1 | Controller workflow-sync test (`TestControllerProgressAccounting`) | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.** | Operator updates workflow. |
| 2 | `data_loader.py` 114 miss remains | Continue with fresh canonical aggregate + `--show-missing` delta. Patch tests at exact sites through canonical caller paths; if 0 delta, retarget immediately. | miss **<114** (target ≤110, stretch ≤105). |
| 3 | 13 pre-existing Batch32/coverage_gaps failures | Ignore; miss delta is authoritative. | Documented. |
| 4 | pyarrow/tables/fastparquet not installed | Monkeypatch parquet/hdf5/engine branches (`pd.read_parquet/read_hdf` and module call sites). | Covered/route-around. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Guard stays green. |
| 6 | Aggregate-context sensitivity | Batch54 showed isolated probes may differ from aggregate hits; always verify delta in **fresh canonical aggregate**. | Canonical delta recorded per batch. |
| 7 | No batch55+ yet | Next session creates `tests/test_bab_data_loader_batch55.py`+ and adds to canonical command/ledger. | New files committed locally only if safe. |

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
| 54 | promote/dtype-tz/elementwise/unnamed-tz/interval/parsed-tz/last-resort/QA handlers | 12 passed | 44 passed | 124→114 (**-10**, canonical aggregate) | `tests/test_bab_data_loader_batch54.py` present; included in fresh canonical this session. Focused isolated run had collection issue due env/cov source mode in that invocation; canonical aggregate is authoritative. |

**Measured improvement (window): 139 → 114 miss (93%).**

## LIKELY-UNREACHABLE / CAUTION (evidence required; do not stall)
- `227-247` (dayfirst elementwise fallback) — likely unreachable post-coercion in normal paths. Prove with targeted counterexample + delta, or document file/line evidence and move on.
- `908-914` — last resort in `_promote_datetime_column`; prove with exact canonical-flow patch or move on.
- `1626-1627`, `1663-1664` — inner `BABDataError` may convert before outer handlers; prove or move on.
- `791-792,859,861-862,867-868,894,901-903,1097-1098,1293-1294,1319-1320` — context-sensitive; trigger via **canonical caller context** (`_promote_datetime_column`/QA/validate/clean_data flows), not isolated probes only.
- `1530-1531,1533-1536,1591-1592,1926-1929,2160-2163,2167-2168,2187-2189,2192-2193` — defensive handlers; need precise monkeypatching at `dlmod`/pandas call sites visible to canonical paths.
- `679,694-695,713-714,733-734,1226-1227,1257-1258` — exchange/epoch/tz/loader handlers partially context-sensitive.
- `43-44,84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,953,1033-1034` — inspect/defensive/rare parse branches; triage early with evidence.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, mandatory)

**Timestamp (UTC):** 2026-11-06T15:28:03Z
**Recipient:** next coding agent in this repo.
**Mode:** HEAVY WORK ONLY. No analysis-only turn. No planning-only turn.

### Mission
Reduce `strategies/betting_against_beta/data_loader.py` miss count from **114** (fresh canonical 2026-11-06T14:48:04Z; **rebaseline at Step 0**) in a **fresh canonical aggregate**. **BAB `data_loader.py` only.** Every batch must yield a **measured miss-count delta** or a **documented unreachable-branch proof with file/line evidence**, then immediately move to the next reachable cluster. `campaign_d*` guard must stay green.

### Focus campaign (ordered; do not avoid)
1. **`791-792,859,861-862,867-868,894,901-903,908-914`** — `_promote_datetime_column` remaining handlers. Trigger via **canonical caller context** (validate/loader/clean_data paths) with stateful monkeypatches visible to the full aggregate; prefer `monkeypatch.setattr(dlmod.pd, ...)`/module call sites where relevant.
2. **`1530-1531,1533-1536`** — `validate_returns_dataframe` benchmark-remap rename fallbacks under real validate flows.
3. **`1591-1592`** — `load_returns_from_csv` defensive empty-after-read; craft stateful `read_csv`/`df.empty` sequence that fires on the *defensive* check without breaking aggregate.
4. **`1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`** — `clean_data`/metadata/defensive branches via exact `dlmod`/pandas patch points in canonical paths.
5. **`679,694-695,713-714,733-734,1226-1227,1257-1258`** — exchange/epoch/tz normalization and loader error handlers.
6. **`1097-1098,1293-1294,1319-1320`** — QA/drop/coerce defensive handlers; hit through canonical QA/validate callers.
7. **Triage early with evidence (max one probe pass each, then move on):** `227-247`, `908-914` (if still unresolved), `1626-1627,1663-1664`, `43-44,84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,953,1033-1034`.

### Execution contract (non-optional)
1. **Run Step 0 baseline first** and record actual `data_loader.py` miss count + exact missing lines before changes.
2. **Deliver ≥3 verified batches** this session (`tests/test_bab_data_loader_batch55.py`, `batch56.py`, `batch57.py`, …) unless reachable clusters are exhausted with evidence. **Zero-delta batches do not count toward the 3; retarget immediately.**
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
