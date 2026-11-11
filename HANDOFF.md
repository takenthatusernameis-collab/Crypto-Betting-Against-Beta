# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-11T06:33:00Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD:** `2f5851e` (`chore(kilo): checkpoint agent session`)
**Working tree:** CLEAN at refresh start except this handoff update (`HANDOFF.md` modified in-session). No module edits this session; no commit/push unless explicitly requested. `HANDOFF.md` is the single durable handoff — do not create competing handoff files.

**Environment (verified this session, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):** `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0**. Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`, `messy_returns.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv`, `benchmark_nan_window.csv`, `returns.json`). `bab-example` console entrypoint may not be on PATH; use `python -m strategies.betting_against_beta.cli ...` or `python scripts/load_real_bab_example.py`.

**Bottleneck removal status:** No blocking bottlenecks found in C25 probe pass. Prior parity bottleneck (CLI↔API synthetic `universe=None`) remains fixed in-tree (`cli.py`). C25 executed with real probe evidence → **explicit "no proven gaps"** (no reproducible incorrectness / silent corruption / wrong parity / rc-contract Traceback / side-effect-on-error requiring module fix found). No modules/tests added.

**Prior campaign closure (evidence-carrying, do not churn without new reproducible failure):** C6–C22 closed with evidence. C21/C22 → explicit **"no proven gaps"**. C23 **1 gap fixed** (CLI output-path validation timing in `cli.py`), 0 remaining gaps. C24 **EXECUTED** (`/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log`, 37 combos) → explicit **"no proven gaps"**, 0 modules touched. **C25 EXECUTED this session** (`/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`, 14 required combos + corrected verification probes appended) → explicit **"no proven gaps"**, 0 modules touched, 0 regressions added.

---

## Step 0 baseline/gates — status (this refresh)

**Verified this session (rc/count recorded):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (6.85s) [green]

**Carried forward from prior verified baseline (no module edits this session, gates not fully re-captured in-turn due runtime):**
- campaign11 bundle + campaign14 `tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0** (last recorded green baseline this repo state: 164 passed, 148.54s)
- full BAB excl `data_loader`/`controller` `tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4782 passed, 35 skipped, rc=0** (last recorded green baseline: 4782 passed, 35 skipped, 376.13s)
- parity subset (11o/11p/contract smoke) previously **46 passed, rc=0** after `cli.py` fix.

**If you edit anything, you MUST re-run Step 0 gates (and impacted suites) and record exact counts/rc before finishing.** No module/test code edits this session.

---

## C25 execution evidence (2026-11-11T06:33:00Z, PYTHONPATH=$PWD)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`

| # | Combo | Result | Notes (rc / contract / strict JSON / Traceback / determinism / side effects) |
|---|---|---|---|
| 1 | `--output /nonexistent_dir_xyz/out.json` | PASS | rc=1, clean error `cannot create parent directory for --output...`, stdout empty, **no partial file**, no Traceback |
| 2 | `--output` is directory (`.../kilo-tmp/outdir`) | PASS | rc=1, clean error `--output path is a directory, not a file`, stdout empty, no Traceback (C23 fix holds) |
| 3 | `--from-prices` without `--data` | PASS | rc=1, clean `--from-prices requires --data`, no Traceback |
| 4a/4b | invalid `--long-quantile 1.5` / `--short-quantile 1.5` | PASS | rc=1, clean config/BABDataError message, no Traceback |
| 5a/5b | empty/whitespace `--universe ""` / `"   "` | PASS | rc=1, clean `--universe must contain at least one non-empty asset token`, no Traceback |
| 6 | benchmark missing from data columns (temp CSV w/o BTC) | PASS | rc=1, clean `Benchmark 'BTC' not found... (missing benchmark coverage)`, no Traceback |
| 7 | `report_to_json` strictness (synthetic/API) | PASS (corrected API usage) | initial probe used non-existent `BABResult.report_to_json` (probe-script error); corrected: `BABStrategy.report_to_json(BABStrategy().report(result))` → strict `allow_nan=False` parse OK, finiteness walk OK, keys `[config,rebalances,metrics,attribution,attribution_totals]` |
| 8 | `tear_sheet()` degenerate input | PASS (corrected) | initial probe used wrong import/API and non-datetime input; corrected: datetime-indexed zero/degenerate returns → `tear_sheet` renders rc=0, no non-finite tokens, `len=807`, strict JSON report parse OK |
| 9 | `--dry-run` no side effects w/ `--output` | PASS | rc=0, resolved config printed, `file_exists=False` (no file written) |
| 10 | extreme costs `--transaction-costs 0.5 --slippage 0.5` | PASS (contract) | rc=0, `Final cumulative return: 0.000000`, finite, no NaN/inf/Traceback; stdout is text summary (no `--output` JSON) — expected CLI behavior |
| 11a | CLI determinism 3× `--synthetic` | PASS | rc=0, byte-identical stdout across 3 runs |
| 11b | API determinism 3× | PASS | `[0.31664543005633267, 0.31664543005633267, 0.31664543005633267] True` |
| 12a/12b | `--version` / `--help` | PASS | rc=0, expected output, no Traceback |
| 13 | `scripts/bab_backtest_report.py --json` on `tests/fixtures/real_market_prices.csv` | PASS | rc=0, strict JSON finite (`strict=True msg=ok`), metrics finite, consistent structure |
| 14 | large-report serialization (n_assets=100, n_days=1000) | PASS (corrected API usage) | initial probe wrong API; corrected: `report_to_json` strict parse OK, finiteness OK, `len=2899`, finite final cumulative |

**C25 conclusion:** **No proven gaps.** All required error/contract probes behaved correctly (clean rc/messages, no Tracebacks, no side effects on dry-run/error). Reporting/serialization APIs (`BABStrategy.report`, `BABStrategy.tear_sheet`, `BABStrategy.report_to_json`) are strict-JSON finite and deterministic under exercised degenerate/large cases. Initial probe failures for 7/8/14 were probe-script/API-shape mistakes, not module defects (corrected and appended in evidence log). No module edits, no regression tests added.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, JSON validity/finiteness with strict `allow_nan=False` semantics where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Confirm baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- campaign11 bundle + campaign14 → **expect ≥164 passed, rc=0**
- full BAB excl `data_loader`/`controller` → **expect ≥4782 passed, 35 skipped, rc=0**

If deps missing, install minimal needed deps and record; do not claim progress blocked without an evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–25 (historical closure — no churn)
C6–C25 reported closed/evidenced above. **Do not churn C6–C25 without a new, statable, reproducible failure with probe evidence.**

### 3) EXECUTE C26 — pipeline stress & cross-surface determinism (≥12 combos, HEAVY) — BINDING
Goal: stress the end-to-end BAB pipeline under degenerate/extreme regimes and verify cross-surface (CLI/API/script) determinism, finiteness, and reporting fidelity. Produce real probe evidence.

**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c26_bab_pipeline_stress_determinism_probe_evidence.log`
Record for each combo: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` parse + finiteness walk where JSON produced), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 12 combos — execute all, add more if suspicious):**
1. CLI+in-process parity on real fixture with `transaction_costs`+`slippage` (strict finite JSON if produced, cumulative match `abs_tol=1e-12`).
2. All-NaN asset column → CLI/API rc=0 finite degenerate output, no Traceback, no NaN/Infinity tokens.
3. Single-asset universe (benchmark only) → rc=0 finite, no short possible, flat/valid weights.
4. Constant/zero returns series → finite cumulative, no NaN.
5. `beta_window` (9999) > data length → rc=0 finite, no Traceback (real fixtures + short slice).
6. `min_observations` exceeding available data → flat/zero-weight periods, finite.
7. `transaction_costs=1.0` + `slippage=1.0` → cumulative finite (≥0 where applicable), no -inf/NaN, rc=0.
8. `regime_filter=True` (if supported) → 3× identical `final_cumulative` (determinism).
9. `beta_neutral=True` → finite, strategy beta ≈ 0 within tolerance.
10. `ShortingConstraints` low borrow cap → finite weights/cumulative, no Traceback.
11. Position sizers (`kelly`/`vol_target`/`risk_parity`/`equal` or supported set) → finite, rc=0.
12. `report_to_json()` + `tear_sheet()` on degenerate run → strict JSON finite, tear_sheet renders no Traceback.
13. CLI repeated run 3× on same input → byte-identical stdout (determinism).
14. `--output` overwrite replaces stale content, rc=0, strict JSON finite.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting modules/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` if evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign26*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs** (do not invent tests).

### 5) Validate comprehensively and record
- Re-run all Step 0 gates after any module/test edit, plus touched/new suites and any impacted reporting/CLI suites. Record exact counts/rc in HANDOFF.
- If no modules touched, state that Step 0 baseline was carried forward (with prior counts) and confirm no regressions introduced.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update this file in place with: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or explicitly carried forward), C26 evidence log path, combo-by-combo PASS/FAIL + invariants, modules/tests touched (or none), and the next binding heavy campaign (**C27**) with a concrete ≥12-combo probe plan. No ambiguous handoff.

---

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4782 passed, 35 skipped, rc=0** (hard floor; raise if legitimately increased by added regressions)
- campaign11 bundle incl. 11ab + campaign14 **≥164 passed, rc=0**

## LOCKS / PROHIBITIONS
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` gate closed — do not alter without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/reporting/`scripts`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy work with probe evidence, remove bottlenecks if found, and leave a refreshed handoff. Next binding campaign: C26 (above).*
