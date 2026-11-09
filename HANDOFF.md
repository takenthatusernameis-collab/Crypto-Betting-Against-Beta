# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T07:38:12Z** @ workspace `main` (`HEAD cf40dfb` / latest local commit observed this session; 2026-11-09 07:10:53 +0000). `strategies/betting_against_beta/data_loader.py` blob verified `596ee9e` (unchanged). `docs/unreachable_proofs.md` is the evidence appendix. **Repo-name priority = Betting Against Beta.** `data_loader.py` target-miss floor is **GATE-CLOSED** (B103–B192, no new strict-4 mechanism; do not churn). **Significant progress continues via BAB Package Coverage Campaign (below).** **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Authoritative data_loader baseline (RE-VERIFIED 2026-11-09T07:38Z this session):** `PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical file list `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` (64 files). Canonical coverage via `coverage.Coverage(source=['strategies.betting_against_beta'], config_file='/dev/null')` API driving `pytest -q --ignore=tests/test_controller_progress_accounting.py` over that exact file list → **374 passed, 26 warnings, `pytest_rc=0`** (same canonical scope command/count pattern recorded in HANDOFF history) and report `--include='*/strategies/betting_against_beta/data_loader.py'` → **417 miss / 1683 stmts / 75%** (canonical command output: `TOTAL 1683 417 75% rc=0`). **Target-miss floor UNCHANGED** (data_loader blob `596ee9e`, line→code basis preserved; no data_loader production edits). `pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3444 deselected, 53 warnings**. `326` is **LIVE/GUARD — DO NOT ALTER**.

> **BAB package/module evidence (2026-11-09T07:38Z):** existing CLI tests only (`tests/test_bab_cli.py tests/test_bab_cli_console_adversarial.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli_report_hardening.py tests/test_bab_cli_strategy_edge.py tests/test_bab_report_cli_edge_cases.py`, API coverage, `-o addopts=`) → `strategies/betting_against_beta/cli.py` **319 stmts / 48 miss / 85%** (68 passed, 1 warning). Added `tests/test_bab_cli_coverage_push.py` (25 tests) targeting real defensive/error/serialization/arg-path behavior; same CLI suite + push → **93 passed, 1 warning**, `cli.py` **319 stmts / 2 miss / 99%**, missing only `381-382` (deep defensive `_extract_cumulative` cum-column `iloc` fallback). `attribution.py` and `data_sources.py` measured **100%** with existing `test_bab_attribution*` / `test_bab_data_sources*` suites (API, `-o addopts=`). Full-suite package TOTAL snapshot was not re-run to completion this session due command time; use module-slice evidence + gates above and rerun package TOTAL in Step 0 next session.

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

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T07:38:12Z (BAB Package Coverage Campaign, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** deliver **significant, production-relevant BAB package progress** by closing the largest real coverage/test gaps in `strategies/betting_against_beta/` **without** regressing the data_loader baseline or campaign_d. `data_loader.py` miss-floor work is **GATE-CLOSED** — do not spend the session on B193 gate/probe churn unless a concrete new production bug/feature path gives a strict-4 mechanism.

**State (verified 2026-11-09T07:38Z, HEAD cf40dfb / data_loader blob 596ee9e):** canonical data_loader scope 374 passed, 26 warnings, `pytest_rc=0`, data_loader 417 miss/1683/75% (canonical command); campaign_d 883/5/3444. **This session shipped `tests/test_bab_cli_coverage_push.py`** (25 tests, real `cli.main`/helper paths, no vacuous bypass): `cli.py` improved **48 miss/85% → 2 miss/99%** (missing only deep defensive lines 381-382). All CLI/report-cli tests green: 93 passed, 1 warning. `attribution.py` and `data_sources.py` are **100%** by existing suites. **Next slice:** `strategy.py` (largest remaining production gap after cli/attribution/data_sources), then `signals.py`/`portfolio.py`/`beta.py`/`backtest.py` as value dictates.

### Forced steps (execute in order; heavy work required)

1. **Step 0 — fresh baseline (mandatory):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; run canonical data_loader scope coverage (API method as above) → must reproduce 374/26/`rc=0`, data_loader 417 miss/1683/75%, campaign_d 883/5/3444 (or record exact drift with root cause). Capture module baseline for the next target (`strategy.py` recommended) and package TOTAL if practical. **Record exact numbers before edits.**
2. **Ship tests for next highest-value module slice (minimum one substantial slice):** default `strategy.py` — cover real `BABStrategy`/strategy-path behavior (config handling, run inputs, signal/portfolio/beta integration edges, error/validation paths, output/result shape). Use `tmp_path`/monkeypatch/controlled data; no semantic production changes solely for coverage, no vacuous mocks. Add `tests/test_bab_strategy_coverage_campaign.py` (or extend existing targeted files only when cleaner).
3. **Non-regression gates (all required before declaring done):** rerun canonical data_loader scope → 374/26/`rc=0`, data_loader still 417 miss/1683/75%; rerun `pytest -q -k campaign_d` → 883/5/3444; rerun all BAB tests relevant to touched modules plus full `pytest -q` **excluding** `tests/test_controller_progress_accounting.py` (report counts). Fix test failures caused by new tests; minimally fix real bugs with evidence.
4. **Coverage proof:** report before/after miss% for touched module(s) and BAB package TOTAL under the same command where practical. **A session that only plans, only reruns baseline, or only touches data_loader gate docs is blocked/inefficient.**
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

## Session progress (BAB package campaign)

| Date (UTC) | Module | Before (module miss/%) | After (module miss/%) | Tests | Gates |
|---|---|---:|---:|---|---|
| 2026-11-09T07:38Z | `cli.py` | 48 / 85% (existing CLI tests) | 2 / 99% (existing CLI tests + push) | `tests/test_bab_cli_coverage_push.py` (+25); CLI/report-cli 93 passed, 1 warning | canonical data_loader 374/26 `rc=0`, 417/1683/75%; campaign_d 883/5/3444; no data_loader/probe edits |

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T07:38:12Z** @ `cf40dfb` / data_loader blob `596ee9e` verified; **data_loader gate closed; cli.py pushed to 99% (2 defensive misses remain at 381-382). Next focus = `strategy.py` coverage campaign slice, then `signals.py`/`portfolio.py`/`beta.py`/`backtest.py`. Baseline-only/planning-only/0-delta probe sessions are blocked and forbidden as exits; the session must ship at least one substantial module-slice test with before/after coverage evidence.**
