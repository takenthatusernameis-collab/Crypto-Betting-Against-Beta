# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T19:58:28Z (refreshed; recon + focused tests + coverage re-measured this session)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `538e8b0` (`chore(kilo): checkpoint agent session`). **Working tree:** `M tests/test_bab_data_loader_coverage_gaps.py` (uncommitted BAB test additions from this session) + this `HANDOFF.md` update. **No production code changed. No `.github/workflows/*` edits/commits/pushes.** Ignore transient `.coverage`/`.pytest_cache/`/`.hypothesis/` if present.

**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks. Do not explore unrelated files.

## Recon re-verified (2026-11-05T19:58Z)

- Env: Python 3.12.3, pytest 9.2.0.
- `tests/test_bab_data_loader_coverage_gaps.py` passes after this session's additions: **521 passed, 5 skipped, 43 warnings, RC 0** (focused file).
- Inspect-sensitive suites preserved: `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. **`_coerce_to_datetime_scalar` inspect/caller branches preserved.**
- Handoff aggregate (exact command set below, fresh completed): **630 passed, 11 skipped, 49 warnings, RC 0**.

## This session — measured progress (BAB-only)

Added deterministic tests in `tests/test_bab_data_loader_coverage_gaps.py` (test-only; no production changes):
- **Batch 1 — `TestCampaignABatch1ExchangeFormatFallbacks`** (7 tests): long-format pivot tz/timestamp/fallbacks, OHLCV single-asset coerce fallback, epoch/ISO/aggressive date coercion paths, epoch-coerce-raises fallback, pivot symbol/tz-localize fallback branches in `_detect_and_normalize_exchange_format`.
- **Batch 2 — `TestCampaignABatch2PromoteAndScalarFallbacks`** (15 tests): `_coerce_series_to_datetime_index` direct/tz/empty cases; `_promote_datetime_column` candidate coercer bad→handled, `set_index`-fails-keeps-column, unnamed/last-resort/exchange-normalization-exception paths; `_coerce_to_datetime_scalar` tz convert, numpy int, parse/dayfirst/numeric-string fallbacks.

**Measured delta (handoff aggregate, completed):** `data_loader.py` improved from **74% (437 miss / 1693 stmts)** → **76% (406 miss / 1693 stmts)**. `cli.py` **81% (62 miss / 319 stmts)** unchanged. Measured slice total **76%** (468 miss / 2012 stmts) on that aggregate.

## Verified state (fresh completed measurement)

- **Infra blocker (NOT BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync` fails because `.github/workflows/main.yml` `stage_safe_changes`/related exclusions are missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- **Coverage — fresh completed aggregate (2026-11-05T19:58Z, `coverage run`):**

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 406 | **76%** | **≥90%** (Campaign A, mandatory, heavy) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **≥85%** (full scope, low priority) |
| **Measured slice total** | 2012 | 468 | **76%** | **≥85%** |

- **Coverage command (bounded, completed):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing
```
- **Note:** Coverage can show no data if a bad `--source`/subset invocation is used; rerun the exact aggregate command above. Core engines beyond loader/CLI slice not freshly re-measured as a single BAB-only all-modules table.
- **Transient local artifacts (ignore, not committed):** `.coverage`, `.pytest_cache/`, `.hypothesis/`.

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.**

## Environment

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -V && python3 -m pytest --version
```

## Bottlenecks (remove / route around)

| # | Bottleneck | Owner | Action | Exit criteria |
|---|------------|-------|--------|---------------|
| 1 | Workflow/controller exclude-pattern sync blocks full un-ignored gate (`main.yml` missing `*/.github/workflows/*` in `stage_safe_changes` path patterns) | **Operator with `workflows` scope** | Add pattern in workflow file only. **Agents lacking permission must not touch `.github/workflows/*`.** Route BAB verification with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate unblocked |
| 2 | `data_loader.py` **76% (406 miss / 1693 stmts)** — largest BAB risk/coverage surface; this session proved only +2pp with narrow batches; **deeper exception/optional-dep/file-I/O branches remain** | **Next BAB agent (heavy, immediate, non-optional)** | **Test-first per batch.** Target remaining uncovered clusters with `monkeypatch`/`tmp_path`/optional-dep skips. Use smallest correct fix only on proven contract violation. **No broad refactor; never silent wrong success; preserve `BABDataError` contract. Preserve inspect-based caller branches in `_coerce_to_datetime_scalar`. No comments in code.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` — **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |
| 4 | Core engines not in a single fresh BAB-only all-modules coverage table | **Next BAB agent (after A gains each batch)** | Close high-value branches with invariant assertions across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 5 | Full un-ignored repo gate blocked by #1 | **Operator** | Fix workflow sync per #1. | All tests pass without controller ignore |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T19:58Z, `main@538e8b0`, handoff aggregate 630 passed/11 skipped; `data_loader.py` 76% (406 miss).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff. Read it, run Step 0, then execute Campaign A immediately. Do not idle, do not explore unrelated files, do not stop after one small patch.**

## Non-negotiable operating rules
- **BAB-only scope.** Work only in `strategies/betting_against_beta/*`, BAB tests, and this handoff.
- **Heavy session required.** Deliver **≥3 verified batches** (more if stable). Each batch = new/updated tests + focused run + aggregate/coverage delta + recorded numbers.
- **No workflow/infra changes.** Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`.
- **Production code secondary.** Keep unchanged unless a **tested contract violation** requires the **smallest correct fix**. Never silent wrong success. Preserve `BABDataError` semantics and public APIs.
- **Preserve inspect-sensitive behavior.** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- **No false claims.** No GREEN/coverage claims without actual completed output.

## Step 0 — Recon (run to completion; record truth)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -4
python3 -m pytest -q --tb=no tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py 2>&1 | tail -2
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -2
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing 2>&1 | tail -14
```

## Campaign A — `data_loader.py` (PRIMARY, HEAVY — DO NOT DEFER)
**Baseline (fresh, 2026-11-05T19:58Z):** **76% (406 miss / 1693 stmts)**; handoff aggregate **630 passed, 11 skipped**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Target:** extend `tests/test_bab_data_loader_coverage_gaps.py` with deterministic batch classes (no comments in code). Use `monkeypatch`/`tmp_path`. After each batch: focused run, aggregate+coverage, `campaign_d*` spot-check.

**Concrete batch targets (reconfirm fresh with `--show-missing`; current measured missing clusters):**
1. **227-247, 258/260/268-269/285-286/289/296-297**: `_normalize_index` tail/dtype/elementwise coercer/dayfirst/last-resort fallback branches (mixed bad strings, object-numeric strings, dayfirst-only values, coerce-fails-then-scalar success paths).
2. **320-483**: `_coerce_to_datetime_scalar` fallback chains (ns/us/ms/s boundaries, bad epoch parse fallbacks, Timestamp/datetime conversion branches, final pandas parse fallbacks). **Do not break inspect-sensitive caller behavior.**
3. **558-565/571/582-586/620/623-626/630/632-633/641-642/664/676-684/694-695/708-714/729-734/757-758/766-767/770-771/789-792**: `_detect_and_normalize_exchange_format` remaining pivot/OHLCV/tz/coercion/exception paths (symbol/date tz objects, malformed epoch fallbacks, OHLCV choice/parse failures, conservative preserve branches).
4. **804-805/821-823/832/840-841/859/861-864/867-868/878-879/882-883/890/894/901-903/908-914/917-918**: `_promote_datetime_column` candidate parse/coerce/set_index fallbacks, unnamed-column parse coercion, last-resort object scan tz/DatetimeIndex set_index branches.
5. **1562-1699, 1711-1806, 1825-1826**: CSV/Parquet/HDF5/Pickle loader tails; JSON/JSONL/split/table/records/default orient/error paths (monkeypatch missing optional deps/readers, empty/malformed payloads, parser exceptions).
6. **1926-1942, 1990-1993, 2010-2092, 2137-2193, 2213, 2238-2248**: `load_prices`/`_drop_metadata_columns`/`_prices_to_returns`/`detect_price_or_returns`/metadata/dispatch/`clean_data`/`validate_prices` tails.
7. **110-214, 953/982-983/1030-1034/1055-1056/1082-1090/1097-1098/1110-1126/1139/1147/1153-1154/1163/1174-1189/1198/1202/1207/1221-1222/1226-1227/1254-1258/1293-1294/1304-1320/1345-1346/1418-1419/1443-1452/1474-1490/1530-1539**: `_normalize_index`/QC/validation/coercion remaining branches.

**Required cadence:** complete **≥3 batches** this session, measuring after each. If a branch is genuinely unreachable without unsafe production changes, document it with evidence here and move to the next highest-value cluster.

## Campaign B — `cli.py` (low priority)
Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn.

## Campaign C — core engines (after A gains each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: assert **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes.

## Close-out (required before ending session)
- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker). Keep `campaign_d*` inspect-sensitive suites passing.
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commit/file-state notes (no false SHA claims), remaining blockers, and the next **concrete command + target files/lines/tests**.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**
