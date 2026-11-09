# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T06:52:11Z** @ workspace `main` (`HEAD 5a4b535`, 2026-11-09 05:26:26 +0000). `strategies/betting_against_beta/data_loader.py` blob verified `596ee9e` (unchanged). `docs/unreachable_proofs.md` is the evidence appendix. **Repo-name priority = Betting Against Beta.** `data_loader.py` target-miss floor is **GATE-CLOSED** (B103–B192, no new strict-4 mechanism; do not churn). **Significant progress continues via BAB Package Coverage Campaign (below).** **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Authoritative data_loader baseline (RE-VERIFIED 2026-11-09T06:52Z this session):** `PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical file list `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` (64 files). Canonical coverage via `coverage.Coverage(source=['strategies.betting_against_beta'], config_file='/dev/null')` API driving `pytest -q --ignore=tests/test_controller_progress_accounting.py` → **645 passed, 6 skipped, 34 warnings** (`pytest_rc=0`). Report `--include='*/strategies/betting_against_beta/data_loader.py' --show-missing` → **365 miss / 1683 stmts / 78%** (78.31%). `pytest -q -k campaign_d` → **883 passed, 5 skipped, 3487 deselected, 53 warnings**. **Target-miss floor UNCHANGED** (line→code re-verify @ fresh SHA/blob before any edit): `40-41,43-44,57-61,68,72,86-89,98-99,110-111,121-123,128-130,134,136-143,145-149,153-155,161,167,171-176,180,186,188,213-214,234-244,246-247,258,268-269,289,296-297,305,320-322,324-328,338-342,344,356,358,386,403-404,423-429,431-434,436-439,447-453,455-458,460-463,465-468,479-483,498,525-526,539-540,566-567,571,580-586,606,625-626,630,641-642,664,694-695,708-712,755-756,791-792,821,917-918,953,964,968,972,974,976,978,982-983,996,1008-1009,1055-1056,1082-1083,1110,1136-1141,1147,1153-1154,1174-1175,1177-1178,1186,1188-1189,1198,1202,1207,1241,1243,1249-1250,1262-1267,1288,1292,1307,1311,1325-1327,1338,1344,1539,1553-1554,1581-1582,1611,1621-1622,1639,1643,1649-1654,1676-1677,1683,1691,1694-1695,1697,1727,1730-1731,1733,1739-1742,1747,1754-1755,1759-1765,1768-1773,1782-1783,1787-1797,1811-1816,1836,1852,1859-1860,1866,1868-1869,1872,1891-1892,1921,1923-1924,1932,1944,1977-1989,2000,2012-2013,2041,2044-2045,2048-2060,2062-2065,2067-2070,2077-2084,2115,2117,2119,2127-2128,2201-2203,2212,2224-2239`. `326` is **LIVE/GUARD — DO NOT ALTER**.

> **BAB package coverage snapshot (same canonical run scope, 2026-11-09T06:52Z):** TOTAL **4409 stmts / 1487 miss / 66%**. Biggest actionable gaps (production-relevant): `cli.py` 319 miss/0%, `attribution.py` 32/14%, `data_sources.py` 39/42% (abstract `NotImplementedError` expected), `strategy.py` 178/40%, `signals.py` 72/44%, `portfolio.py` 116/52%, `beta.py` 155/52%, `backtest.py` 44/60%, `regime.py` 70/65%, `config.py` 52/74%. `data_loader.py` excluded from reduction churn (gate-closed).

## Bottlenecks — RESOLVED / REMOVED (do not reintroduce)

Cleared and forbidden as excuses: scratch/probe clutter (tracked `debug_beta*`/`probe*`/`ast_probe.py` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility (`coverage`/`pytest` via `python -m`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (`--rcfile=/dev/null --source=strategies.betting_against_beta`), canonical batch-set drift (enumerate explicitly), parquet/hdf5 engines (monkeypatch read APIs/call sites as needed; handlers may wrap as `BABDataError`), **and data_loader 0-delta gate churn** (B103–B192 exhausted; `data_loader.py` floor is baseline/unreachable per recorded evidence — **no more probe/gate-only sessions on data_loader without a concretely demonstrated, non-repeat strict-4 mechanism discovered from a production bug/feature need**).

## data_loader.py remaining target-miss clusters (GATE-CLOSED; verify line→code @ SHA only if a real mechanism appears)

| Cluster | Lines | Current verdict |
|---|---|---|
| `_not_null` outer except | `43-44` | Not reducible (production-realistic, structural outer except). |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Not reducible (dataflow/contract-shadow; 232 deterministic for elements that reach 227). |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Not reducible (handler-order shadow/MRO; BABDataError dominates). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | Not reducible (earlier NaT guards dominate). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Not reducible (defensive/guarded). |
| exchange detect outer handlers | `641-642,694-695` | Not reducible (structural shadow). |
| promote datetime column outer handler | `791-792` | Not reducible (nested/guarded). |
| `_normalize_asset_name` empty token continue | `953` | Not reducible (construction-unreachable; `str.split()` default). |

## Strict 4 criteria (only for any future data_loader reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA/blob.
2. Mechanism not disproven by B103–B183/M149–M183/B186–B192 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path (no semantic change, no pathological harness).
4. Stated control-flow path consistent with (2)-(3).

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T06:52:11Z (BAB Package Coverage Campaign, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** deliver **significant, production-relevant BAB package progress** by closing the largest real coverage/test gaps in `strategies/betting_against_beta/` **without** regressing the data_loader baseline or campaign_d. `data_loader.py` miss-floor work is **GATE-CLOSED** — do not spend the session on B193 gate/probe churn unless a concrete new production bug/feature path gives a strict-4 mechanism.

**State (verified 2026-11-09T06:52Z, HEAD 5a4b535 / data_loader blob 596ee9e):** canonical 645 passed, 6 skipped, 34 warnings; data_loader 365 miss/1683/78% unchanged; campaign_d 883/5/3487. Package snapshot (canonical scope): **4409 stmts / 1487 miss / 66%**. Priority gaps: `cli.py` 319/0%, `attribution.py` 32/14%, `data_sources.py` 39/42%, `strategy.py` 178/40%, `signals.py` 72/44%, `portfolio.py` 116/52%, `beta.py` 155/52%, `backtest.py` 44/60%, `regime.py` 70/65%, `config.py` 52/74%.

### Forced steps (execute in order; heavy work required)

1. **Step 0 — fresh baseline (mandatory):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; run canonical data_loader scope coverage (API method as above) → must reproduce 645/6/34, 365 miss/78%, campaign_d 883/5/3487 (or record exact drift with root cause). Also capture package-wide `--source=strategies.betting_against_beta` report for target modules. **Record exact numbers before edits.**
2. **Pick the highest-value module slice and ship tests (minimum one substantial slice):** default priority order — `cli.py` (arg parsing, `--dry-run`, `--from-prices`, output validation/serialization, error paths; use `tmp_path`/monkeypatch/subprocess-style `main(argv)`), then `attribution.py`, then `data_sources.py` (CSV/Parquet/HDF5/Pickle/DataFrame/cache; monkeypatch read APIs; cover `NotImplementedError`/base contract as appropriate), then `strategy.py`/`signals.py`/`portfolio.py`. **Tests must exercise real production behavior** (no vacuous mocks that bypass logic, no weakening assertions). Prefer adding `tests/test_bab_<module>_coverage_campaign.py` (or extend existing targeted files only when cleaner).
3. **Non-regression gates (all required before declaring done):** rerun canonical data_loader scope → 645/6/34, data_loader still 365 miss/78%; rerun `pytest -q -k campaign_d` → 883/5/3487; rerun all BAB tests relevant to touched modules plus full `pytest -q` **excluding** `tests/test_controller_progress_accounting.py` (report counts). Any failure caused by new tests = fix the test; any failure exposing a real bug = fix minimally with evidence.
4. **Coverage proof:** report before/after miss% for touched module(s) and BAB package TOTAL under the same command. **A session that only plans, only reruns baseline, or only touches data_loader gate docs is blocked/inefficient.**
5. **Handoff update (durable):** refresh this HANDOFF with timestamp/SHA/blob, exact Step 0 + final commands/counts, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep it single-file canonical.
6. **Forbidden:** data_loader probe/gate churn without a new strict-4 mechanism; semantic production changes solely for coverage; altering `322,326`; weakening/deleting batch148/149/172 or `campaign_d*`; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** materially improved coverage/tests on at least one priority BAB module slice with all gates green and before/after evidence, **plus** refreshed HANDOFF naming the next slice — **OR** **(B)** a concrete, evidence-backed blocker (failing environment/dep/real bug) with minimal reproduction and the exact unblocked next action. No baseline-only exit.

## Session batch ledger (data_loader, historical)

| Batch | Delta | Result | Notes |
|---|---|---|---|
| 148 | -2 | reduction | 351-352; semantics preserved. |
| 149 | -2 | reduction | 334-335 (M149). |
| 150–171 | 0 | proof | M150–M171 recorded. |
| 172 | 0 | proof+probes | M172.1–M172.7; batch172 retained; target floor unchanged. |
| 173–183 | 0 | proof+probes | M173–M183 complete strict-4 evidence; no reduction. |
| 184–185 | 0 | superseded/unverified | see appendix/history. |
| 186 | 0 | proof+probes (complete) | materially-new CLI/real-file/exotic-dtype/NA-marker evidence; 365 miss/78% unchanged. |
| 187–192 | 0 | gate complete | no new strict-4 mechanism; canonical baseline preserved; no probe churn. **GATE CLOSED for data_loader.** |

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T06:52:11Z** @ `5a4b535` / data_loader blob `596ee9e` verified; **data_loader gate closed; next focus = BAB package coverage campaign (cli→attribution→data_sources→strategy/signals/portfolio).**