# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **This is the only durable handoff.** Read fully, then execute the **INITIAL TASK MESSAGE** below. No off-ramp, no sidetrack, no status-only session.

**Handoff timestamp (UTC):** 2026-11-06T12:49:09Z (refreshed this session)
**Verified state timestamp (UTC):** 2026-11-06T12:49:09Z (fresh canonical aggregate verified this session; unchanged — working tree clean)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `53745db`. Working tree clean. `origin/main` unchanged. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

---

## PRIORITY (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**. The **only** priority is `strategies/betting_against_beta/data_loader.py`: correctness, robustness, adversarial handling, and **measured** coverage improvement.

- **No** infra/controller refactors. **No** sidetracks. **No** pivot to `cli.py`/other modules.
- Every session must produce **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, **or** a documented unreachable-branch proof **with file/line evidence** while immediately moving to the next reachable cluster.
- A session that ends with "reviewed code", "ran baseline only", or "planned next steps" without measured delta/proof is a failed session.

## FRESH VERIFIED STATE (2026-11-06T12:38:40Z)
- **Env:** Python 3.12.3, deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages` (pandas/numpy/pytest/coverage). `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`.
- **Canonical Step 0 aggregate (fresh, completed, includes batch40-47):** **1317 passed, 13 failed (pre-existing Batch32 only), 23 skipped, 88 warnings**.
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 139 miss, 92%.**
- **Missing lines (exact, 139):** `43-44,84,92-93,194,196,227-247,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,679,694-695,713-714,733-734,757-758,766-767,770-771,789-792,804-805,840-841,859,861-862,867-868,890,894,901-903,908-914,953,1033-1034,1084-1085,1097-1098,1112,1115,1221-1222,1226-1227,1257-1258,1293-1294,1304-1305,1312-1313,1319-1320,1451-1452,1530-1531,1533-1536,1591-1592,1626-1627,1663-1664,1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`.
- **Canonical baseline command (run first; include all prior batch files):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py
python3 -m coverage report --include='*data_loader.py' --show-missing
```

## BOTTLENECKS — REMOVED / ROUTED (do not let these block progress)
| # | Bottleneck | Route-around (mandatory) | Exit condition |
|---|---|---|---|
| 1 | Controller workflow-sync test (`TestControllerProgressAccounting`) | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.** | Operator updates workflow. |
| 2 | `data_loader.py` 139 miss remains | Continue with fresh canonical aggregate + `--show-missing` delta. Patch tests at exact sites; if 0 delta, retarget immediately. | miss **<139** (target ≤135, stretch ≤130). |
| 3 | 13 pre-existing Batch32 failures | Ignore; miss delta is authoritative. | Documented. |
| 4 | pyarrow/tables/fastparquet not installed | Monkeypatch parquet/hdf5/engine branches. | Covered by existing batches. |
| 5 | Inspect-sensitive / campaign_d semantics | Preserve `_coerce_to_datetime_scalar`/inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Guard stays green. |

**No other blockers are recognized.** If a new issue appears, document it with evidence and route around it in the same session; do not stop.

## SESSION BATCH LEDGER (measured, 2026-11-06T12:38Z window)
| Batch | Targets | Focused | Guard | Canonical (before→after data_loader miss) | Delta | Notes |
|---|---|---:|---|---:|---:|---|
| 44 | 1487-1490/1588-1592/194/196 probes | 1 passed | 44 passed | 153→153 | 0 | No canonical delta in isolation; kept. |
| 45 | 1487-1490 retry drop, 1530-1536 benchmark remap, 1588-1592, promote/unnamed/clean_data handlers | 9 passed | 44 passed | 153→145 | **-8** | Hit 1487-1490 and parts of remap/defensive paths. |
| 46 | 757-758,766-767,770-771,789-792,804-805,840-841 probes,1443-1444,1451-1452,1345-1346,1530-1531 | 10 passed | 44 passed | 145→139 | **-6** | Hit 1443-1444,1345-1346,679/related; some targets remain context-dependent. |
| 47 | 840-841,859/861-862/867-868,1530-1536,1591-1592,1926-1929,2160-2168 probes | 9 passed | 44 passed | 139→139 | 0 | Exercised handlers but not all reached in canonical context. Retarget next. |

**Total measured improvement (recent):** 153 → **139 miss** (92%).

## LIKELY-UNREACHABLE / CAUTION (evidence required; do not stall)
- `227-247` (dayfirst elementwise fallback) — still missing; likely unreachable post-coercion in normal paths. Prove with targeted counterexample + delta, or document file/line evidence and move on.
- `908-914` — last resort in `_promote_datetime_column`; prove with exact patch or move on.
- `1626-1627`, `1663-1664` — inner `BABDataError` may convert before outer handlers; prove or move on.
- `757-758,766-767,770-771,789-792,804-805,840-841,859,861-862,867-868` — exception handlers; batch46/47 exercised some paths alone but canonical still shows misses (context-sensitive). Next agent must trigger under **canonical caller context** (`validate_returns_dataframe`/loader flows), not isolated unit calls.
- `1451-1452,1530-1531,1533-1536,1591-1592,1926-1929,2160-2163,2167-2168,2187-2189,2192-2193` — defensive handlers; need precise monkeypatching at `dlmod`/pandas call sites visible to canonical paths.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, mandatory)

**Mission (Campaign A continuation):** Reduce `strategies/betting_against_beta/data_loader.py` miss count from **139** (verified 2026-11-06T12:38:40Z canonical) in a **fresh canonical aggregate**. **BAB `data_loader.py` only.** Every batch must yield a **measured miss-count delta** or a **documented unreachable-branch proof with file/line evidence**, then immediately move to the next reachable cluster. `campaign_d*` guard must stay green.

### Execution contract (non-optional)
1. **Run Step 0 baseline first** (command above) and record actual `data_loader.py` miss count before changes. Recheck missing lines line-by-line.
2. **Deliver ≥3 verified batches** in this session (`tests/test_bab_data_loader_batch48.py`, `batch49.py`, `batch50.py`, …) unless reachable clusters are exhausted with evidence. Zero-delta batches do not count toward the 3; retarget before continuing.
3. For **each batch:** write minimal targeted tests → focused run → `campaign_d*` guard → **fresh canonical aggregate** → record before/after miss count and delta. Commit locally only if appropriate and safe; **do not push** unless explicitly requested.
4. **Update this HANDOFF.md** at session end with: refreshed UTC timestamp, SHA, verified canonical result, batch ledger rows (delta or unreachable proof), remaining clusters, and the next initial task message. Keep it the single durable handoff.
5. **No off-ramps:** do not stop at analysis, planning, or a single 0-delta probe without retargeting. If a cluster is context-sensitive, craft inputs that trigger it through canonical caller paths.

### Priority clusters (recheck; target measured delta)
1. **`757-758,766-767,770-771,789-792,804-805,840-841,859,861-862,867-868`** — `_promote_datetime_column` exception handlers (tz-normalize/element-wise/unnamed-column). Trigger via **canonical caller context** (real `validate_returns_dataframe`/loader flows), not isolated unit calls.
2. **`1451-1452,1530-1531,1533-1536`** — `validate_returns_dataframe` trivial-1970 / benchmark-remap rename fallbacks. Use real validate flows; monkeypatch `pd.DataFrame.rename`/index normalization at call sites used by canonical paths.
3. **`1591-1592`** — `load_returns_from_csv` defensive empty-after-read; stateful `read_csv`/`df.empty` monkeypatch compatible with prior checks.
4. **`1926-1929,2160-2163,2167-2168,2187-2189,2192-2193`** — `clean_data`/metadata defensive branches; patch exact `dlmod` symbols and pandas methods inside those blocks.
5. **`679,694-695,713-714,733-734`** — exchange/epoch/tz normalization handlers.
6. **Triage early with evidence (max one probe pass each, then move on):** `227-247`, `908-914`, `1626-1627,1663-1664`. Produce counterexample attempt + delta result or file/line unreachable proof.

### Targets
- **Session minimum:** miss **<139** with ≥3 measured-delta batches (or documented exhaustion with evidence).
- **Target:** ≤135. **Stretch:** ≤130.

### Guard
```bash
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

### Hard rules
- BAB `data_loader.py` only. No infra/controller refactors, no `cli.py`/other-module pivot.
- Ignore 13 pre-existing Batch32 failures. Never edit/commit/push `.github/workflows/*`.
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
- Fresh canonical aggregate completed with all batch40+ files included.
- `data_loader.py` miss count **<139** (or unreachable-proof exhaustion documented with file/line evidence).
- `campaign_d*` guard green.
- This HANDOFF.md updated as the single durable handoff with next initial task message.
