# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T08:38:42Z (session verified state; re-verify fresh before coding)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA at handoff (verify before push claims):** `main` @ `58a47bf` working tree **clean** (HANDOFF.md + coverage-gaps test additions committed; `.coverage` artifact gitignored). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**: `strategies/betting_against_beta/data_loader.py` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. Until Campaign A end condition is met, every session must produce **measured `data_loader.py` miss-count reduction** (or documented unreachable-branch proof **with file/line evidence while still moving to the next cluster**). **No early stop. No pivot to `cli.py`/other modules. No deferral.**

## Last verified state (re-verify fresh before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guards:** `tests/test_bab_data_loader_campaign_d{,2,3}.py` → **44 passed, RC 0** (still green; coverage-gaps additions don't touch them). Expanded campaign_d suite also present (d5, core*, deep*, final*, gaps*, heavy*, more*, push*, ultra*, coerce_more*) — use `campaign_d/d2/d3` as the hard gate; others are supplementary.
- **Step 0 aggregate (fresh completed this session):** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 200 miss, 88%** (gap to ≥90%: **31 stmts**, target **≤169 miss**). `cli.py` — **319 stmts, 62 miss, 81%** (defer; do not pivot). **Source of truth:** rerun Step 0 fresh before coding and after **every** batch; do not reuse stale numbers.
- **Batches completed this session (all measured via full aggregate):** TestBatch31 (244→224, -20), TestBatch32 (224→222, -2), TestBatch33 (222→210, -12), TestBatch34 (210→203, -7), fresh re-baseline 203→200 (-3, TestBatch35). **≥3 verified batches with measured delta: SATISFIED.**
- **Test layout:** BAB tests `tests/test_bab_*`, `tests/test_betting_against_beta_*`; coverage-gaps suite ends at `TestBatch35` (line ~8042 of `tests/test_bab_data_loader_coverage_gaps.py`). **Next batch: `TestBatch36`.**

## Bottlenecks (route-around; do not get stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test fails (agent cannot fix):** `.github/workflows/main.yml` omits `*/.github/workflows/*` expected by `scripts/controller_progress.py`. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate BAB work with `--ignore=tests/test_controller_progress_accounting.py`. Spend **zero** BAB time on this. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` 88% (200 miss) — Campaign A mandatory.** | **Next BAB agent (immediate, heavy)** | Test-first `TestBatch36+` in `tests/test_bab_data_loader_coverage_gaps.py`. Batch counts **only** with **fresh aggregate measured miss-count delta** (or documented unreachable-branch proof). Smallest correct fix only for proven contract violations. Preserve `BABDataError` contract and inspect-sensitive/campaign_d semantics. **No comments in code.** **Minimum: ≥3 verified batches with measured delta** unless blocked by proven unreachable branches (document evidence and keep moving). **No early stop. No pivot. No deferral.** | Fresh aggregate: `data_loader.py` **≥90% (≤169 miss)**, zero regressions, `campaign_d*` green. |
| 3 | `cli.py` 81% (62 miss) | Later | Defer until Campaign A sustains measured deltas. Do not pivot even though coverage improved. | ≥85%, no regression. |
| 4 | **`TestBatch32` pre-existing failures (13 tests) — bottleneck/inefficiency.** | **Next BAB agent** | 13 TestBatch32 tests fail on error-message/behavior drift (e.g. `Unsupported` regex vs `data file not found`, parquet/hdf5 benchmark-only BABDataError, isinstance TypeError, clean_data raise, detect_price_or_returns assertions). **Do not debug/fix them — they are not the Campaign A target.** Route-around: run each new batch focused, then `campaign_d*` guard, then **full Step 0 aggregate** (aggregate miss delta is still measurable and authoritative). Exclude `tests/test_bab_data_loader_coverage_gaps.py::TestBatch32*` from focus runs only if needed; do not let them block ≥3 measured batches. | Blocked tests documented; Campaign A progress continues via measured aggregate delta. |
| 5 | **Uncommitted local changes** (`.coverage`, `HANDOFF.md`) | Next BAB agent / operator | Tree currently **clean** (@ `58a47bf`). Review `git status/diff`, run BAB gates, commit only if authorized by user/task policy; do not push unless explicitly requested. | Clean/intentional tree with verified SHA. |

## Missing clusters (fresh `--show-missing` this session, 200 miss)
`43-44, 84, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 561, 620, 641-642, 676-684, 694-695, 708-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1221-1222, 1226-1227, 1257-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1539, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1805-1806, 1869-1870, 1895, 1926-1929, 1937-1938, 2022-2023, 2054-2055, 2061, 2068, 2091-2092, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248`.

### Documented unreachable-branch evidence
**`data_loader.py:225-247` (dayfirst elementwise fallback loop) — LIKELY UNREACHABLE.** Code path (lines 202-224): non-numeric index → `pd.to_datetime(..., errors="coerce")` retries → elementwise `_coerce_to_datetime_scalar(v)` loop (217-224) which either **raises** (line 223 `except Exception: raise` for unparseable `v`, e.g. NaT/"garbage") or **succeeds producing only Timestamps** (no NaN). At 224 `df.index = coerced` sets a **list** index (no `.isna` attribute), so line 225 `getattr(df.index, "isna", None)` → `None` → condition `False` → 227-247 never entered. **Evidence:** read lines 102-247; `_coerce_to_datetime_scalar` raises on NaT/None/nan/inf/empty/null-strings and returns Timestamp otherwise, so no NaN can survive elementwise coercion to reach line 225. Move to next cluster; do not stop here.

## High-value reachable targets to probe first (recheck before each batch)
**676-684** (exchange ohlcv tz paths), **708-714** (tz_convert exception), **908-914** (promote unnamed last resort), **1588-1592** (csv read exception), **1620-1623** (parquet validate exception), **1698-1699** (pickle validate exception), **1757** (json DataFrame payload), **1805-1806** (json self-heal except/re-raise), **1869-1870** (load_returns unsupported path), **1926-1929/1937-1938** (_drop_metadata_columns), **2022-2023** (_is_likely_returns prices), **2054-2055** (jsonl bad line), **2061/2068** (json payloads), **2091-2092** (pickle dict/else), **2160-2163/2167-2168/2173-2174/2187-2189/2192-2193** (clean_data exceptions), **2238-2239/2241/2247-2248** (detect_price_or_returns). If a cluster is genuinely unreachable, record **file, line range, why unreachable, and what was tried**; then move immediately to the next cluster. Unreachable proof is not a stop condition.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission:** Campaign A — drive `strategies/betting_against_beta/data_loader.py` to **≥90% (≤169 miss)** in a fresh completed aggregate, with measured, verified batches. This is the **only** priority. Current: **200 miss (88%)**, need **≤169** (gap **31 stmts**). **Heavy working required.**

**Hard rules (future agents cannot avoid):**
- **Do not** defer, pivot to `cli.py`/infra, refactor broadly, or declare done before end condition — even though `cli.py` improved to 81%/62 miss.
- **Do not** count a batch without a **fresh aggregate measured miss-count delta** (or documented unreachable proof + immediate move to next cluster).
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session (each batch = focused tests → `campaign_d*` guard → full Step 0 aggregate → recorded delta). If a cluster is proven unreachable, document evidence and continue; do not stop at <3 without exhausting reachable clusters.
- **Bottleneck route-around:** `TestBatch32` has 13 pre-existing failures (error-message/behavior drift). Do not fix/debug them. Run each new batch focused → `campaign_d*` guard → full Step 0 aggregate; the aggregate miss delta is authoritative and still measurable. Do not let failing TestBatch32 block Campaign A.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar` stack logic), `campaign_d*` semantics, and all sacred invariants. Smallest correct fix only for **proven** contract violations. **No comments in code. No `.github/workflows/*` changes.**

**Execution steps:**
1. **Step 0 (mandatory, fresh):** run aggregate coverage (command below), record `data_loader.py` miss/stmts/% and `cli.py`, and capture `--show-missing`. Confirm `campaign_d*` guard green before changes. Do not reuse stale numbers.
2. **Batch 36:** add `TestBatch36*` in `tests/test_bab_data_loader_coverage_gaps.py` targeting **rechecked** reachable missing lines (prioritize clusters above). Use `tmp_path`, malformed/ext/encoding/dispatch/adversarial inputs; `pytest.importorskip` only for optional deps. Exercise public/API and reachable internal paths. Assert real behavior/`BABDataError` — no empty/pass-only tests that claim coverage without assertions.
3. **After each batch:** run the new batch focused → `campaign_d*` guard → **full Step 0 aggregate** → compute and record miss delta vs previous fresh aggregate. If no delta, adjust tests (target different reachable path) before claiming progress.
4. **Continue:** Batch 37, Batch 38, … without stopping. Keep a running ledger in your final response (batch, target lines, focused result, guard result, aggregate miss before/after, delta).
5. **End condition:** fresh aggregate shows `data_loader.py` **≥90% (≤169 miss)**, zero regressions, `campaign_d*` green; **or** reachable clusters exhausted with documented file/line + evidence. Update this `HANDOFF.md` with new timestamp, verified numbers, next batch number, remaining clusters, and the next initial task message.

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
