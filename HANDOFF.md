# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T09:38:16Z (refreshed; re-verify fresh before coding)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (verify before any push claim):** `main` @ `924aba9` (`origin/main` in sync at handoff). `git status --porcelain=v1` showed **no tracked/untracked changes** at refresh time except normal local artifacts may exist outside git tracking (e.g., `.coverage`); recheck. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**: `strategies/betting_against_beta/data_loader.py` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. Every session must produce **measured `data_loader.py` miss-count reduction** (or documented unreachable-branch proof **with file/line evidence while still moving to the next reachable cluster**). **No early stop. No pivot to `cli.py`/other modules. No deferral.**

## Last verified state (re-verify fresh before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guard (fresh, 2026-11-06T09:38Z):** `tests/test_bab_data_loader_campaign_d{,2,3}.py` → **44 passed, RC 0**.
- **New batches present/focused (fresh):** `TestBatch36/37/38` in `tests/test_bab_data_loader_coverage_gaps.py` → **35 passed, 7 skipped** (focused run).
- **Prior Step 0 aggregate (2026-11-06T08:46Z, after Batch 38 — rerun fresh before coding):** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 173 miss, 90%** (rounded). **Explicit Campaign A threshold is ≤169 miss** → **4 stmts remain**. `cli.py` — **319 stmts, 62 miss, 81%** (defer; do not pivot). **Source of truth:** rerun Step 0 fresh before coding and after **every** batch.
- **Aggregate caveat (documented):** 13 pre-existing failures in `tests/test_bab_data_loader_coverage_gaps.py::TestBatch32*` (error-message/behavior drift) may appear in aggregate; **route around, do not debug/fix TestBatch32.** Coverage report/miss delta from a completed aggregate is still authoritative for Campaign A measurement.
- **Next batch:** `TestBatch39` in `tests/test_bab_data_loader_coverage_gaps.py` (file currently ends at `TestBatch38`, ~line 8334+).

## Verified batch ledger (carry forward; re-verify if numbers disputed)
| Batch | Focus | Batch focused | Guard | Aggregate miss (before→after) | Delta |
|---|---|---:|---:|---:|---:|
| Start | baseline | — | 44 pass | — → 200 | baseline |
| 36 | parquet/hdf5/pickle/json error+payload paths, promote/detect edges, drop_metadata/is_likely_returns/detect exceptions | 15 pass, 2 skip | 44 pass | 200 → 180 | **-20** |
| 37 | csv/parquet/hdf5 outer errors, pickle list construction, promote/detect/clean_data exception routing (partial) | 11 pass, 3 skip | 44 pass | 180 → 178 | **-2** |
| 38 | `validate_prices` exception/empty/finite paths (2238-2248), parquet/hdf5 BABDataError passthrough, metadata sequential drop, promote/detect/exchange tz edges | 9 pass, 2 skip | 44 pass | 178 → 173 | **-5** |

**Cumulative (prior verified):** 200 → 173 miss (**-27**). **≥3 verified batches with measured delta: satisfied historically.** **Campaign A end condition NOT met:** **173 > 169** — next session must continue heavy working.

## Bottlenecks (removed/routed — do not get stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test** (`scripts/controller_progress.py` expects `*/.github/workflows/*` in `.github/workflows/main.yml`). Agent cannot fix. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate with `--ignore=tests/test_controller_progress_accounting.py`. Spend **zero** BAB time on this. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` 173 miss (target ≤169).** | **Next BAB agent (immediate, heavy)** | Test-first `TestBatch39+`. Count only **fresh aggregate measured miss delta** (or documented unreachable proof **and immediate move to next cluster**). Smallest correct fix only for proven contract violations. Preserve `BABDataError`, inspect-sensitive/campaign_d semantics. **No comments in code. Minimum ≥3 verified batches with measured delta** unless ≤169 reached earlier with proof. **No early stop. No pivot. No deferral.** | Fresh aggregate: `data_loader.py` **≤169 miss**, zero regressions, `campaign_d*` green. |
| 3 | **`TestBatch32` pre-existing failures (13)** — error-message/behavior drift. | Next BAB agent | **Do not debug/fix.** Run new batch focused → `campaign_d*` guard → full Step 0 aggregate; aggregate miss delta authoritative. | Documented; does not block Campaign A. |
| 4 | `cli.py` 81% (62 miss) | Later | Defer until Campaign A sustains measured deltas and meets ≤169. | ≥85%, no regression. |

## Missing clusters (from prior fresh `--show-missing`, 173 miss — recheck before each batch)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 676-684, 694-695, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1698-1699, 1895, 1926-1929, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193`

## Documented likely-unreachable evidence (carry forward; not a stop condition)
**`data_loader.py:225-247` (dayfirst elementwise fallback loop) — LIKELY UNREACHABLE.** After elementwise `_coerce_to_datetime_scalar(v)` (217-224), each value either **raises** (unparseable/NaT/None/nan/inf/empty/null-strings) or returns a `Timestamp`; therefore no NaN survives. `df.index = coerced` assigns a **list** (no `.isna`), so `getattr(df.index, "isna", None)` is `None` and 227-247 is not entered. **Evidence:** source read of lines 102-247 and `_coerce_to_datetime_scalar` contract. If you can construct a counterexample, do so with a focused test and measured delta; otherwise move immediately to next cluster.

## High-value reachable targets to probe first (recheck actual code before each batch)
- **676-684, 694-695** — exchange/OHLCV tz/parse element branches.
- **908-914** — `_promote_datetime_column` last-resort/index/result paths (inspect control flow; monkeypatch if needed).
- **1588-1592** — CSV post-read empty/robust checks.
- **1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664** — parquet/hdf5 BABDataError/generic/outer paths (monkeypatch readers/validators).
- **1698-1699** — pickle list/iterable DataFrame construction exception (monkeypatch `pd.DataFrame` for that branch).
- **2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193** — `clean_data` exception paths.
- **1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536** — validate/coerce/benchmark remap adversarial branches.
- **1895, 1926-1929** — metadata/drop paths.
- **Small defensive clusters** (`43-44,84,92-93,194,196,268-269,285-286,322,326,334-335,338-342,351-352,400,403-404,561,620,641-642,713-714,733-734,757-758,766-767,770-771,789-792,804-805,840-841,859,861-864,867-868,890,894,901-903,953,1033-1034,1084-1085,1097-1098,1112,1115,1221-1222,1226-1227,1257-1258,1293-1294,1304-1305,1312-1313,1319-1320,1345-1346,1443-1444,1451-1452`) — triage by reading code.
If genuinely unreachable: record **file, line range, why unreachable, what was tried**, then **immediately** move to next cluster.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission:** Campaign A — drive `strategies/betting_against_beta/data_loader.py` from **173 miss** to **≤169 miss** in a **fresh completed aggregate** (explicit threshold). This is the **only** priority. **Heavy working required.**

**Hard rules (future agents cannot avoid):**
- **Do not** defer, pivot to `cli.py`/infra, refactor broadly, or declare done before end condition.
- **Do not** count a batch without a **fresh aggregate measured miss-count delta** (or documented unreachable proof **and immediate move to next reachable cluster**).
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session unless ≤169 is reached earlier with verified proof. Each batch = focused tests → `campaign_d*` guard → full Step 0 aggregate → recorded delta. If a cluster is proven unreachable, document evidence and continue; do not stop below throughput without exhausting reachable clusters.
- **Route-around:** ignore `TestBatch32` pre-existing failures (13). Do not fix/debug them. Aggregate miss delta is authoritative.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar` stack logic), `campaign_d*` semantics, and sacred invariants. Smallest correct fix only for **proven** contract violations. **No comments in code. No `.github/workflows/*` changes. No push unless explicitly requested.**

**Execution steps:**
1. **Step 0 (mandatory, fresh):** run aggregate coverage (below), record `data_loader.py` miss/stmts/% and `cli.py`, capture `--show-missing`. Confirm `campaign_d*` guard green. Do not reuse stale numbers.
2. **Batch 39:** add `TestBatch39*` in `tests/test_bab_data_loader_coverage_gaps.py` targeting **rechecked** reachable missing lines. Use `tmp_path`, malformed/ext/encoding/dispatch/adversarial inputs; `pytest.importorskip` only for optional deps. Assert real behavior/`BABDataError` — no empty/pass-only tests.
3. **After each batch:** run new batch focused → `campaign_d*` guard → **full Step 0 aggregate** → compute/record miss delta vs previous fresh aggregate. If no delta, retarget before claiming progress.
4. **Continue:** Batch 40, 41, … without stopping until ≤169 miss or reachable clusters exhausted with evidence. Keep a running ledger (batch, target lines, focused result, guard result, aggregate miss before/after, delta).
5. **End condition:** fresh aggregate shows `data_loader.py` **≤169 miss**, zero regressions, `campaign_d*` green; **or** reachable clusters exhausted with documented file/line evidence. Update this `HANDOFF.md` with new UTC timestamp, verified numbers, next batch number, remaining clusters, and the next initial task message.

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
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.**
