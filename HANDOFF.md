# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T06:56:00Z (session verified state; re-verify fresh before coding)
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA at handoff (verify before push claims):** `main` @ `d165e60` working tree **dirty** (uncommitted: `.coverage` artifact, `HANDOFF.md`, `tests/test_bab_data_loader_coverage_gaps.py` adds `TestBatch28/29/30`, +247 lines). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**: `strategies/betting_against_beta/data_loader.py` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. Until Campaign A end condition is met, every session must produce **measured `data_loader.py` miss-count reduction** (or documented unreachable-branch proof **with file/line evidence while still moving to the next cluster**). **No early stop. No pivot to `cli.py`/other modules. No deferral.**

## Last verified state (re-verify fresh before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guards:** `tests/test_bab_data_loader_campaign_d{,2,3}.py` → **44 passed, 5 warnings, RC 0** (verified 2026-11-06T06:55Z).
- **Step 0 aggregate (fresh completed 2026-11-06T06:55Z, 1157 passed / 16 skipped / 86 warnings):** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 236 miss, 86%** (gap to ≥90%: **67 stmts**, target **≤169 miss**). `cli.py` — **319 stmts, 62 miss, 81%** (defer). **Source of truth:** rerun Step 0 fresh before coding and after **every** batch; do not reuse stale numbers.
- **Local uncommitted progress (measured in this tree):** `tests/test_bab_data_loader_coverage_gaps.py` contains `TestBatch28/29/30` (ends at `TestBatch30`); aggregate reflects **236 miss**. **Next batch: `TestBatch31`.**
- **Test layout:** BAB tests `tests/test_bab_*`, `tests/test_betting_against_beta_*`; coverage-gaps suite ends at `TestBatch30`.

## Bottlenecks (route-around; do not get stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test fails (agent cannot fix):** `.github/workflows/main.yml` omits `*/.github/workflows/*` expected by `scripts/controller_progress.py`. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate BAB work with `--ignore=tests/test_controller_progress_accounting.py`. Spend **zero** BAB time on this. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` 86% (236 miss, fresh-verified) — Campaign A mandatory.** | **Next BAB agent (immediate, heavy)** | Test-first `TestBatch31+` in `tests/test_bab_data_loader_coverage_gaps.py`. Batch counts **only** with **fresh aggregate measured miss-count delta** (or documented unreachable-branch proof). Smallest correct fix only for proven contract violations. Preserve `BABDataError` contract and inspect-sensitive/campaign_d semantics. **No comments in code.** **Minimum: ≥3 verified batches with measured delta this session** unless blocked by proven unreachable branches (document evidence and keep moving). **No early stop. No pivot. No deferral.** | Fresh aggregate: `data_loader.py` **≥90% (≤169 miss)**, zero regressions, `campaign_d*` green. |
| 3 | `cli.py` 81% | Later | Defer until Campaign A sustains measured deltas. | ≥85%, no regression. |
| 4 | **Uncommitted local changes** (`.coverage`, `HANDOFF.md`, `tests/test_bab_data_loader_coverage_gaps.py`) | Next BAB agent / operator | Review `git status/diff`, run BAB gates, commit only if authorized by user/task policy; do not push unless explicitly requested. | Clean/intentional tree with verified SHA. |

## Missing clusters (last-known Step 0 2026-11-06T06:55Z; recheck fresh with `--show-missing`)
`43-44, 84, 92-93, 128-130, 134, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 482-483, 561, 620, 641-642, 676-684, 694-695, 708-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1174-1175, 1186, 1221-1222, 1226-1227, 1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942, 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248`.

**High-value reachable targets to probe first (recheck before each batch):** **227-247** (string-index dayfirst/elementwise fallback paths), **840-841/859-868/890-914** (promote datetime unnamed/last-resort/tz/set_index fallbacks), **1033-1034/1084-1098/1112/1115/1174-1186/1221-1227** (normalize/parse/coerce/drop residuals), **1254-1258+** (deeper loader/validation paths), **561/620/641-642/676-695/708-734/757-805** (exchange/detect/promote tz/parse branches), **43-44/84/92-93/128-134/194-196** (module-level/import/early helper fallbacks — verify reachability). If a cluster is genuinely unreachable, record **file, line range, why unreachable, and what was tried**; then move immediately to the next cluster. Unreachable proof is not a stop condition.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately — heavy work, no off-ramp)
**Mission:** Campaign A — drive `strategies/betting_against_beta/data_loader.py` to **≥90% (≤169 miss)** in a fresh completed aggregate, with measured, verified batches. This is the **only** priority. **Heavy working required.**

**Hard rules (future agents cannot avoid):**
- **Do not** defer, pivot to `cli.py`/infra, refactor broadly, or declare done before end condition.
- **Do not** count a batch without a **fresh aggregate measured miss-count delta** (or documented unreachable proof + immediate move to next cluster).
- **Minimum throughput:** deliver **≥3 verified batches with measured delta** this session (each batch = focused tests → `campaign_d*` guard → full Step 0 aggregate → recorded delta). If a cluster is proven unreachable, document evidence and continue; do not stop at <3 without exhausting reachable clusters.
- Preserve `BABDataError` contract, inspect-sensitive behavior (`_coerce_to_datetime_scalar` stack logic), `campaign_d*` semantics, and all sacred invariants. Smallest correct fix only for **proven** contract violations. **No comments in code. No `.github/workflows/*` changes.**

**Execution steps:**
1. **Step 0 (mandatory, fresh):** run aggregate coverage (command below), record `data_loader.py` miss/stmts/% and `cli.py`, and capture `--show-missing`. Confirm `campaign_d*` guard green before changes. Do not reuse stale numbers.
2. **Batch 31:** add `TestBatch31*` in `tests/test_bab_data_loader_coverage_gaps.py` targeting **rechecked** reachable missing lines (prioritize clusters above). Use `tmp_path`, malformed/ext/encoding/dispatch/adversarial inputs; `pytest.importorskip` only for optional deps. Exercise public/API and reachable internal paths. Assert real behavior/`BABDataError` — no empty/pass-only tests that claim coverage without assertions.
3. **After each batch:** run the new batch focused → `campaign_d*` guard → **full Step 0 aggregate** → compute and record miss delta vs previous fresh aggregate. If no delta, adjust tests (target different reachable path) before claiming progress.
4. **Continue:** Batch 32, Batch 33, … without stopping. Keep a running ledger in your final response (batch, target lines, focused result, guard result, aggregate miss before/after, delta).
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
