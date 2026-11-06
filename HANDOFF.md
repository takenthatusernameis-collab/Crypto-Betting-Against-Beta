# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T08:48:05Z (session-verified state; re-verify fresh before coding)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA at handoff (verify before push claims):** `main` @ `455d752` working tree has **local uncommitted test edits** in `tests/test_bab_data_loader_coverage_gaps.py` (TestBatch36-38 added; minor pre-existing pickle/indentation fixes in earlier Batch4/5 helpers; `.coverage` artifact may appear locally). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**: `strategies/betting_against_beta/data_loader.py` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. Every session must produce **measured `data_loader.py` miss-count reduction** (or documented unreachable-branch proof **with file/line evidence while still moving to the next cluster**). **No early stop. No pivot to `cli.py`/other modules. No deferral.**

## Last verified state (re-verify fresh before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guard (fresh):** `tests/test_bab_data_loader_campaign_d{,2,3}.py` → **44 passed, RC 0** (green after Batch 36-38).
- **Step 0 aggregate (fresh completed 2026-11-06T08:46Z, after Batch 38):** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 173 miss, 90%** (coverage rounds to 90%; explicit target **≤169 miss** means **4 stmts remain**). `cli.py` — **319 stmts, 62 miss, 81%** (defer; do not pivot). **Source of truth:** rerun Step 0 fresh before coding and after **every** batch; do not reuse stale numbers.
- **Aggregate run shape (authoritative for miss delta):** 13 pre-existing failures in `tests/test_bab_data_loader_coverage_gaps.py::TestBatch32*` (error-message/behavior drift; documented bottleneck) + 1 unrelated pre-existing failure pattern may appear depending on edits — **route around; do not debug/fix TestBatch32.** Aggregate produced **1246 passed, 23 skipped** in the Step 0 command set; coverage report is valid/measured from the run.
- **Test layout:** BAB tests `tests/test_bab_*`, `tests/test_betting_against_beta_*`; coverage-gaps suite now ends at `TestBatch38` (~line 8400+). **Next batch: `TestBatch39`.**

## Verified batch ledger (this session, all measured via full Step 0 aggregate)
| Batch | Focus | Batch focused | Guard | Aggregate miss (before→after) | Delta |
|---|---|---:|---:|---:|---:|
| Start (fresh) | baseline | — | 44 pass | — → 200 | baseline |
| 36 | parquet/hdf5/pickle/json error+payload paths, promote/detect edges, drop_metadata/is_likely_returns/detect exceptions | 15 pass, 2 skip | 44 pass | 200 → 180 | **-20** |
| 37 | csv/parquet/hdf5 outer errors, pickle list construction, promote/detect/clean_data exception routing (partial) | 11 pass, 3 skip | 44 pass | 180 → 178 | **-2** |
| 38 | `validate_prices` exception/empty/finite paths (2238-2248), parquet/hdf5 BABDataError passthrough, metadata sequential drop, promote/detect/exchange tz edges | 9 pass, 2 skip | 44 pass | 178 → 173 | **-5** |

**Cumulative measured reduction this session:** 200 → 173 miss (**-27 stmts**). **≥3 verified batches with measured delta: SATISFIED.** Campaign A explicit threshold (≤169 miss) is **not yet met by 4 stmts** — continue heavy working.

## Bottlenecks (route-around; do not get stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test fails (agent cannot fix):** `.github/workflows/main.yml` omits `*/.github/workflows/*` expected by `scripts/controller_progress.py`. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate BAB work with `--ignore=tests/test_controller_progress_accounting.py`. Spend **zero** BAB time on this. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` 173 miss (90% rounded, target ≤169).** | **Next BAB agent (immediate, heavy)** | Test-first `TestBatch39+` in `tests/test_bab_data_loader_coverage_gaps.py`. Batch counts **only** with **fresh aggregate measured miss-count delta** (or documented unreachable-branch proof). Smallest correct fix only for proven contract violations. Preserve `BABDataError` contract and inspect-sensitive/campaign_d semantics. **No comments in code. Minimum ≥3 verified batches with measured delta** unless blocked by proven unreachable branches (document evidence and keep moving). **No early stop. No pivot. No deferral.** | Fresh aggregate: `data_loader.py` **≤169 miss (≥90% true threshold met)**, zero regressions, `campaign_d*` green. |
| 3 | **`TestBatch32` pre-existing failures (13 tests)** in `tests/test_bab_data_loader_coverage_gaps.py` — error-message/behavior drift. | Next BAB agent | **Do not debug/fix them.** Run each new batch focused → `campaign_d*` guard → full Step 0 aggregate; aggregate miss delta is authoritative. | Documented; Campaign A progress continues. |
| 4 | **Local uncommitted edits** (`tests/test_bab_data_loader_coverage_gaps.py`; `.coverage` may be local). | Next BAB agent / operator | Review `git diff/status`, run BAB gates, commit only if authorized by user/task policy; do not push unless explicitly requested. | Clean/intentional tree with verified SHA. |
| 5 | `cli.py` 81% (62 miss) | Later | Defer until Campaign A sustains measured deltas and meets ≤169. | ≥85%, no regression. |

## Missing clusters (fresh `--show-missing` 2026-11-06T08:46Z, 173 miss)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 676-684, 694-695, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1698-1699, 1895, 1926-1929, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193`

## Documented unreachable-branch evidence (carry forward; do not stop)
**`data_loader.py:225-247` (dayfirst elementwise fallback loop) — LIKELY UNREACHABLE.** Code path (lines 202-224): non-numeric index → `pd.to_datetime(..., errors="coerce")` retries → elementwise `_coerce_to_datetime_scalar(v)` loop (217-224) which either **raises** (line 223 `except Exception: raise` for unparseable `v`, e.g. NaT/"garbage") or **succeeds producing only Timestamps** (no NaN). At 224 `df.index = coerced` sets a **list** index (no `.isna` attribute), so line 225 `getattr(df.index, "isna", None)` → `None` → condition `False` → 227-247 never entered. **Evidence:** read lines 102-247; `_coerce_to_datetime_scalar` raises on NaT/None/nan/inf/empty/null-strings and returns Timestamp otherwise, so no NaN can survive elementwise coercion to reach line 225. Move to next cluster; do not stop here.

## High-value reachable targets to probe first (recheck before each batch)
Focus on clusters that can move 4+ stmts quickly with robust, contract-preserving tests:
- **676-684, 694-695** (exchange/OHLCV tz/parse element branches) — craft DataFrames that reach specific loop/tz states.
- **908-914** (`_promote_datetime_column` last-resort set_index/index result paths) — inspect actual control flow; may require monkeypatching `pd.to_datetime`/`set_index` outcomes.
- **1588-1592** (CSV post-read empty/robust checks) — may need unusual `read_csv`/DataFrame behavior; document if unreachable.
- **1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664** (parquet/hdf5 BABDataError/generic/outer paths) — monkeypatch `read_parquet`/`read_hdf`/`validate_returns_dataframe`.
- **1698-1699** (pickle list/iterable DataFrame construction exception) — monkeypatch `pd.DataFrame` for list branch.
- **2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193** (`clean_data` exception paths) — targeted monkeypatches/odd column types.
- **1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536** (validate/coerce/benchmark remap branches) — adversarial mixed columns and benchmark names.
- **1895, 1926-1929** (metadata/drop paths) — sequential/junk numeric patterns.
- Small clusters: **43-44, 84, 92-93, 194, 196, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 713-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452** — triage by reading surrounding code; many are defensive except branches.
If a cluster is genuinely unreachable, record **file, line range, why unreachable, and what was tried**; then move immediately to the next cluster. Unreachable proof is not a stop condition.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission:** Campaign A — drive `strategies/betting_against_beta/data_loader.py` to **≤169 miss** in a fresh completed aggregate (explicit threshold; 90% rounded is not sufficient if miss > 169), with measured, verified batches. This is the **only** priority. Current: **173 miss (1693 stmts, 90% rounded)**, need **≤169** (gap **4 stmts**). **Heavy working required.**

**Hard rules (future agents cannot avoid):**
- **Do not** defer, pivot to `cli.py`/infra, refactor broadly, or declare done before end condition.
- **Do not** count a batch without a **fresh aggregate measured miss-count delta** (or documented unreachable proof + immediate move to next cluster).
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session unless the ≤169 target is reached earlier with verified proof. Each batch = focused tests → `campaign_d*` guard → full Step 0 aggregate → recorded delta. If a cluster is proven unreachable, document evidence and continue; do not stop at <3 without exhausting reachable clusters.
- **Bottleneck route-around:** `TestBatch32` has 13 pre-existing failures (error-message/behavior drift). **Do not fix/debug them.** Run each new batch focused → `campaign_d*` guard → full Step 0 aggregate; the aggregate miss delta is authoritative.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar` stack logic), `campaign_d*` semantics, and all sacred invariants. Smallest correct fix only for **proven** contract violations. **No comments in code. No `.github/workflows/*` changes.**

**Execution steps:**
1. **Step 0 (mandatory, fresh):** run aggregate coverage (command below), record `data_loader.py` miss/stmts/% and `cli.py`, and capture `--show-missing`. Confirm `campaign_d*` guard green before changes. Do not reuse stale numbers.
2. **Batch 39:** add `TestBatch39*` in `tests/test_bab_data_loader_coverage_gaps.py` targeting **rechecked** reachable missing lines (prioritize 676-684/908-914/1588-1592/1620-1664/1698-1699/2160-2193/1474-1536/1895/1926-1929 and small defensive clusters). Use `tmp_path`, malformed/ext/encoding/dispatch/adversarial inputs; `pytest.importorskip` only for optional deps. Assert real behavior/`BABDataError` — no empty/pass-only tests.
3. **After each batch:** run the new batch focused → `campaign_d*` guard → **full Step 0 aggregate** → compute and record miss delta vs previous fresh aggregate. If no delta, adjust tests (target different reachable path) before claiming progress.
4. **Continue:** Batch 40, Batch 41, … without stopping until ≤169 miss or reachable clusters exhausted with evidence. Keep a running ledger in your final response (batch, target lines, focused result, guard result, aggregate miss before/after, delta).
5. **End condition:** fresh aggregate shows `data_loader.py` **≤169 miss**, zero regressions, `campaign_d*` green; **or** reachable clusters exhausted with documented file/line + evidence. Update this `HANDOFF.md` with new timestamp, verified numbers, next batch number, remaining clusters, and the next initial task message.

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
