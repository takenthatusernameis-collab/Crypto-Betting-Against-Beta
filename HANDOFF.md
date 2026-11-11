# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T08:46:35Z
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**HEAD:** `00f9c84` (`chore: capture completed workflow run diagnostics`)
**Working tree:** clean at refresh (no uncommitted module/test changes). No commit/push. This file is the single durable handoff — do not create competing handoff files. (`.kilo/handoff.md`, if present, is superseded by this document.)

## Environment (verified this session)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`)
- Key fixtures present: `tests/fixtures/{real_market_prices.csv,real_market_prices_expanded.csv,degenerate_metrics.csv,junk_columns.csv,all_nan_column.csv,messy_returns.csv,non_monotonic_dates.csv,real_data_defects.csv,benchmark_nan_window.csv,returns.json}`
- CLI: `python -m strategies.betting_against_beta.cli --help` OK.

## Bottleneck removal status
- **No blocking bottlenecks found** this session (deps present, gates runnable/green, no missing env). Prior workflow diagnostics in `research_state/workflow_run_diagnostics.jsonl` show `kilo_edit_tool_invalid_arguments` log signals in past runs but no current reproducible blocker in-repo; blocked/inefficient work: none identified now. If a future agent hits missing deps/env, install minimal deps and record evidence before claiming blocked.

## Historical closure (do not churn without new reproducible failure + probe evidence)
- **C6–C22:** closed with evidence.
- **C23:** 1 gap fixed (CLI output-path validation timing in `cli.py`), 0 remaining gaps. Evidence: `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log`
- **C24:** EXECUTED (37 combos) → **“no proven gaps”**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log`
- **C25:** EXECUTED (14 required combos + corrected probes) → **“no proven gaps”**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`
- **Do not churn C6–C25** without a new, statable, reproducible failure with probe evidence.

## C26 — pipeline stress & cross-surface determinism (EXECUTED, ≥14 combos)
**Status:** Executed; evidence recorded. **No production module/test edits made this session** (probe artifacts exist only under `/home/runner/work/_temp/kilo-tmp/`).
**Primary evidence logs:**
- `/home/runner/work/_temp/kilo-tmp/c26_bab_pipeline_stress_determinism_probe_evidence.log` (detailed entries, 14 combos)
- `/home/runner/work/_temp/kilo-tmp/c26_followup_evidence.log`
- `/home/runner/work/_temp/kilo-tmp/c26_final_verify.log`
- Probe scripts (repro): `/home/runner/work/_temp/kilo-tmp/c26_probe.py`, `c26_followup.py`, `c26_final_verify.py`

| Combo | Description | Result | Key observations / invariants |
|---|---|---|---|
| C01 | CLI + in-process API parity, real fixture, `tx=0.001 slippage=0.0005` | **REVIEW / needs canonical parity repro** | CLI rc=0, stdout `Final cumulative return: 0.301249`, periods 398, output JSON strict finite. Main probe reported stdout-parsed parity mismatch vs API (method/data-path sensitivity noted); `c26_final_verify.log` shows `--output` JSON `final_cumulative=0.3012494853747545` vs its API run `0.0` (diff ~0.301) — **probe harness/setup inconsistency must be resolved with a single canonical apples-to-apples repro** before claiming parity gap/fix. No Traceback. |
| C02 | All-NaN asset column degenerate | **PASS** | rc=0, `Final cumulative return: 0.000000`, periods 396, no Traceback, no NaN/Infinity tokens. |
| C03 | Single-asset universe (benchmark only) | **PASS** | rc=0, `Final cumulative return: 1.000000`, periods 398, no Traceback, no non-finite tokens, flat/valid degenerate outcome. |
| C04 | Constant/zero returns series (API, 50-row zero) | **GUARDED/REVIEW** | Data quality campaign raises `BABDataError: Stale/frozen data detected in column 'BTC': 50 consecutive equal values` (traceback captured by probe harness; not silent corruption). Expected guard behavior; confirm desired user-facing contract (CLI vs API) in follow-up if needed. |
| C05 | `beta_window=9999` > data length (real fixture + short slice) | **PASS** | rc=0, no Traceback, finite JSON/cumulative (real: ~0.436061, periods 398; short slice finite). |
| C06 | `min_observations` exceeding data (999) | **PASS** | rc=0, cumulative finite (~0.387568), no Traceback. |
| C07 | `transaction_costs=1.0` + `slippage=1.0` | **PASS** | rc=0, `Final cumulative return: 0.000000`, periods 398, cumulative finite (0.0), no NaN/-inf, no Traceback. |
| C08 | `regime_filter=True` 3× determinism | **PASS (per probe summary)** | 3× identical `final_cumulative` reported in evidence summary, rc=0. |
| C09 | `beta_neutral=True` (strategy beta ~0 target) | **REVIEW** | `c26_final_verify.log`: `strategy_beta=0.09715019913360234` (not within 1e-3), cumulative/metrics finite in recorded run context shown; needs a definitive, minimal reproducible check against current API semantics/tolerance expectations before classifying as gap. No Traceback. |
| C10 | `ShortingConstraints` low borrow cap | **PASS (per probe summary)** | Finite weights/cumulative, no Traceback (see detailed evidence). |
| C11 | Position sizers (kelly/vol_target/risk_parity/equal) | **PASS (per probe summary)** | Finite, rc=0 across supported sizers (see detailed evidence). |
| C12 | `report_to_json()` + `tear_sheet()` on degenerate run | **PASS (on 5-row degenerate fixture)** | Raw 50-row zero probe hit stale/frozen guard (as C04); `c26_final_verify.log` on `degenerate_metrics.csv` (5 rows): `json_strict_finite=True`, `tear_sheet_ok=True`, cumulative 1.0 finite, no Traceback. |
| C13 | CLI repeated run 3× on same input → byte-identical stdout | **PASS** | rc=0, 3 runs, byte-identical stdout. |
| C14 | `--output` overwrite replaces stale content | **PASS** | rc=0, stale replaced, output JSON strict finite, no non-finite tokens. |

**C26 triage conclusion:** **No production fixes applied this session.** Several combos are clean PASS; C01/C04/C09/C12(raw) are **REVIEW items requiring a tight, canonical repro to determine if a statable defect exists** (parity harness comparability, stale-data guard contract, beta-neutral tolerance/metric expectation, degenerate fixture choice). **Do not claim a proven gap or add regressions without a new, reproducible, apples-to-apples failure.** No modules touched.

## Step 0 baseline/gates (status at this refresh)

**Re-run this session:**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (10.00s)

**Carried forward (prior recorded green; not re-run this session — re-run if you edit anything):**
- campaign11 bundle + campaign14 (`tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py`) → **≥164 passed, rc=0** (prior)
- full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`) → **≥4782 passed, 35 skipped, rc=0** (prior)

**If you edit anything, you MUST re-run all Step 0 gates (and impacted suites) and record exact counts/rc before finishing.**

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

### 2) Campaigns 6–26 (historical closure — no churn)
C6–C25 closed/evidenced above. **C26 executed with evidence** (see section above) — 0 modules touched, review items remain (C01/C04/C09). **Do not churn C6–C26 without a new, statable, reproducible failure with probe evidence.** Resolve C26 review items only via canonical apples-to-apples repros that prove a real defect.

### 3) EXECUTE C27 — attribution, sizing/shorting edge interactions & script/report surface stress (≥12 combos, HEAVY) — BINDING
Goal: stress attribution decomposition, sizing/shorting interactions, script/report surfaces, and resolve C26 review items only when canonically disproven/proven. Produce real probe evidence.

**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c27_bab_attribution_sizing_shorting_report_probe_evidence.log`
Record for each combo: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` parse + finiteness walk where JSON produced), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 12 combos — execute all, add more if suspicious):**
1. **C26-C01 canonical parity repro:** same input path/loader path/config for CLI (`--output` JSON) vs in-process API → record full-precision `final_cumulative`, `abs` diff vs `1e-12`, and determine proven parity gap or probe-artifact mismatch.
2. **Attribution decomposition finite (real run):** run on `real_market_prices.csv` (and/or returns fixture) → attribution components finite, keys stable, sums/reconciliation sane per implementation contract, strict JSON if serialized.
3. **Attribution decomposition on degenerate/flat run:** zero/degenerate-safe fixture (e.g. 5-row degenerate where quality allows) → finite, no NaN/Infinity, no Traceback.
4. **Sizing edge — `kelly`/`vol_target`/`risk_parity`/`equal` on extreme/zero-vol inputs:** verify finite weights/cumulative, rc=0, no Traceback (API path as needed).
5. **Shorting constraints borrow-cap/utilization edges:** low cap, tight utilization-style limits (per supported `ShortingConstraints` API) → weights respect caps/constraints, finite, no Traceback.
6. **C26-C09 canonical beta-neutral check:** `beta_neutral=True` with explicit config/tolerance on real fixture → record `strategy_beta`, tolerance, finiteness, determinism (3×) and conclude proven gap vs expected behavior with evidence.
7. **Script surface — `scripts/bab_backtest_report.py` and/or `scripts/load_real_bab_example.py`:** run with valid fixtures → rc=0, finite/valid output, no Traceback; include determinism check if output is stable.
8. **Script/CLI error-contract parity:** missing/invalid inputs to scripts/CLI paths → rc!=0 clean actionable errors, no Traceback, no partial/corrupt output.
9. **`strategy.report()` / `tear_sheet()` / JSON serialization under guarded scenarios:** NaN/inf-guarded/degenerate cases → strict JSON finite, tear_sheet renders without Traceback.
10. **Combined stress determinism:** `transaction_costs` + `slippage` + `regime_filter` (and/or sizing/shorting where supported) → 3× identical key outputs (`final_cumulative`/metrics as applicable).
11. **Rebalance-frequency comparison deterministic:** daily/weekly/monthly on same input → finite outputs, deterministic per-freq, no Traceback.
12. **Report/output overwrite & idempotence:** repeated `--output`/script report generation replaces stale content, strict JSON finite, rc=0.

Notes: exercise API paths where CLI flags are unavailable; record unsupported knobs explicitly. Prefer `tests/fixtures/*` and minimal deterministic synthetic slices. **C26-C04 (stale/frozen guard on constant series)**: confirm contract (clean error vs accepted flat run) with a minimal canonical probe and document; treat as proven gap only if behavior contradicts intended contract.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting modules/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` if evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign27*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs** (do not invent tests).

### 5) Validate comprehensively and record
- Re-run all Step 0 gates after any module/test edit, plus touched/new suites and any impacted reporting/CLI suites. Record exact counts/rc in HANDOFF.
- If no modules touched, state that Step 0 baseline was carried forward/partially re-run and confirm no regressions introduced.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update this file in place with: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or carried forward), C27 evidence log path, combo-by-combo PASS/FAIL/REVIEW + invariants, modules/tests touched (or none), and the next binding heavy campaign (**C28**) with a concrete ≥12-combo probe plan. No ambiguous handoff.

---

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4782 passed, 35 skipped, rc=0** (hard floor; raise if legitimately increased)
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

## Next binding campaign after C27 (pre-declared, execute if C27 clean)
**C28 — end-to-end reproducibility, config/CLI-API contract closure & reporting fidelity hardening (≥12 combos, HEAVY):**
Evidence log: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log`
Minimum plan: (1) CLI↔API parity on all supported CLI knobs with `--output` full-precision JSON; (2) `--dry-run` contract matrix (valid/invalid/missing/dir/conflict) no side effects; (3) config boundary/validation error contracts (quantiles, windows, costs/slippage, universe/benchmark) rc/messages stable; (4) synthetic reproducibility (`seed`/determinism) 3×; (5) real-fixture multi-run determinism across costs/slippage/regime/sizing combos; (6) metrics/report JSON schema stability & strict finiteness; (7) attribution/report/tear_sheet cross-consistency; (8) script outputs deterministic & overwrite-safe; (9) edge universes (2-asset, benchmark-heavy, sparse history) finite; (10) non-monotonic/defect fixture handling contracts (clean rc/error vs load) per supported paths; (11) output path/permission-like edge handling; (12) any residual C26/C27 review items with canonical repro. Same triage/fix/validate/handoff rules apply.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy C27 with probe evidence, remove bottlenecks if found, and leave a refreshed handoff.*
