# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T06:54:33Z
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA at handoff (verify before push claims):** `main` @ `3a54ee0` working tree dirty (uncommitted test additions; `git status` / `git rev-parse --short HEAD`). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. Until Campaign A end condition is met, every session must produce **measured `data_loader.py` miss-count reduction** (or documented unreachable-branch proof **with file/line evidence while still moving to the next cluster**).

## Last verified state (re-verify fresh before coding)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guards:** `tests/test_bab_data_loader_campaign_d{,2,3}.py` → **44 passed, 5 warnings, RC 0** (verified 2026-11-06T06:42Z).
- **Step 0 aggregate (fresh completed 2026-11-06T06:42Z, 1157 passed / 16 skipped / 86 warnings):** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 236 miss, 86%** (gap to ≥90%: **67 stmts**, target **≤169 miss**). `cli.py` — **319 stmts, 62 miss, 81%** (defer). **Source of truth:** rerun Step 0 fresh before coding and after **every** batch; do not reuse stale numbers.
- **This session (measured):** added `TestBatch28/29/30` to `tests/test_bab_data_loader_coverage_gaps.py` (+247 lines, uncommitted). Fresh aggregate improved `data_loader.py` **243 → 236 miss (-7)** with `campaign_d*` green and zero regressions in the BAB gate.
- **Test layout:** BAB tests `tests/test_bab_*`, `tests/test_betting_against_beta_*`; coverage-gaps suite ends at `TestBatch30` (`tests/test_bab_data_loader_coverage_gaps.py`). **Next batch: `TestBatch31`.**

## Bottlenecks (route-around; do not get stuck)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test fails (agent cannot fix):** `.github/workflows/main.yml` omits `*/.github/workflows/*` expected by `scripts/controller_progress.py`. | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always gate BAB work with `--ignore=tests/test_controller_progress_accounting.py`. Spend zero BAB time on this. | Operator updates workflow; full gate green. |
| 2 | **`data_loader.py` 86% (236 miss, fresh-verified) — Campaign A mandatory.** | **Next BAB agent (immediate)** | Test-first `TestBatch31+` in `tests/test_bab_data_loader_coverage_gaps.py`. Batch counts **only** with **fresh aggregate measured miss-count delta** (or documented unreachable-branch proof). Smallest correct fix only for proven contract violations. Preserve `BABDataError` contract and inspect-sensitive/campaign_d semantics. **No comments in code.** **Minimum: ≥3 verified batches with measured delta this session** unless blocked by proven unreachable branches (document evidence and keep moving). **No early stop. No pivot. No deferral.** | Fresh aggregate: `data_loader.py` **≥90% (≤169 miss)**, zero regressions, `campaign_d*` green. |
| 3 | `cli.py` 81% | Later | Defer until Campaign A sustains measured deltas. | ≥85%, no regression. |
| 4 | **Uncommitted local changes** (`.coverage`, `HANDOFF.md`, `tests/test_bab_data_loader_coverage_gaps.py`) | Next BAB agent / operator | Review `git status/diff`, run BAB gates, commit only if authorized by user/task policy; do not push unless explicitly requested. | Clean/intentional tree with verified SHA. |

## Missing clusters (last-known Step 0 2026-11-06T06:42Z; recheck fresh with `--show-missing`)
`43-44, 84, 92-93, 128-130, 134, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 482-483, 561, 620, 641-642, 676-684, 694-695, 708-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1174-1175, 1186, 1221-1222, 1226-1227, 1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942, 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248`.

High-value reachable targets to probe first (recheck): **227-247** (string-index dayfirst/elementwise fallback after coercer raises), **840-841/859-868/890-914** (promote_datetime_column unnamed/last-resort/tz/set_index fallbacks), **1033-1034/1084-1098/1112-1186/1221-1227** (normalize/parse/coerce residuals), **1254-1258+** (deeper loader/validation paths), **561/620/641-642/676-695/708-734/757-805** (exchange/detect/promote tz/parse branches). If a cluster is genuinely unreachable, record file/line + why and move immediately to the next cluster.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute now — no lighter track, no deferral, no off-ramp)
**Mission:** Campaign A — drive `data_loader.py` to **≥90% (≤169 miss)** with measured, verified batches. Heavy work required; no deferral, no pivot, no off-ramp until end condition.

1. **Step 0 (mandatory, fresh):** run aggregate coverage, record `data_loader.py` miss/stmts/% and `cli.py`, recheck `--show-missing`. Do not reuse stale numbers. Confirm `campaign_d*` guard green before changes.
2. **Batch 31:** add `TestBatch31*` in `tests/test_bab_data_loader_coverage_gaps.py` targeting **rechecked** reachable lines (prioritize clusters above). Use `tmp_path`, malformed/ext/encoding/dispatch/adversarial cases; `pytest.importorskip` only for optional deps. Exercise public/API and reachable internal paths; preserve behavior and `BABDataError` semantics. **No comments in code.**
3. **After each batch:** focused batch run → `campaign_d*` guard → **full Step 0 aggregate** → record miss-count delta. **No delta = batch does not count.**
4. **Continue without stopping:** Batch 32, 33, … Deliver **≥3 verified batches with measured delta** this session unless a cluster is proven unreachable (document file/line evidence and keep moving). There is no off-ramp other than ≥90% or documented unreachable proof.
5. **End condition:** `data_loader.py` ≥90% in fresh completed aggregate, zero regressions, `campaign_d*` green, **or** reachable clusters exhausted with documented proof. **Do not declare done early. Do not pivot to cli.py or other modules.**

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
