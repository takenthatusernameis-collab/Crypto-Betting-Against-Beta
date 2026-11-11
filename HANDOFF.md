# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T07:26:19Z
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**HEAD:** `a82fd86` (`chore(kilo): checkpoint agent session`)
**Working tree:** clean at refresh (no uncommitted module/test changes). No commit/push. This file is the single durable handoff — do not create competing handoff files. (`.kilo/handoff.md`, if present, is superseded by this document.)

## Environment (verified this session)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`)
- Key fixtures present: `tests/fixtures/{real_market_prices.csv,real_market_prices_expanded.csv,degenerate_metrics.csv,junk_columns.csv,all_nan_column.csv,messy_returns.csv,non_monotonic_dates.csv,real_data_defects.csv,benchmark_nan_window.csv,returns.json}`
- CLI: `python -m strategies.betting_against_beta.cli --help` OK (`--data/--from-prices/--synthetic/--dry-run/--output/--transaction-costs/--slippage` supported). Use module form if `bab-example` not on PATH.

## Bottleneck removal status
- **No blocking bottlenecks found** in this refresh pass (deps present, tests collectible/runnable, gates healthy, prior probe evidence present under `/home/runner/work/_temp/kilo-tmp/`).
- Blocked/inefficient work: none identified. If a future agent hits missing deps/env, install minimal deps and record evidence before claiming blocked.

## Historical closure (do not churn without new reproducible failure + probe evidence)
- **C6–C22:** closed with evidence (C21/C22 explicit “no proven gaps”).
- **C23:** 1 gap fixed (CLI output-path validation timing in `cli.py`), 0 remaining gaps. Evidence: `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log`
- **C24:** EXECUTED (37 combos) → **“no proven gaps”**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log`
- **C25:** EXECUTED (14 required combos + corrected probes) → **“no proven gaps”**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`
- **Do not churn C6–C25** without a new, statable, reproducible failure with probe evidence.

## Step 0 baseline/gates (status at this refresh)

**Re-run this session:**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (6.85s)

**Carried forward (prior recorded green; re-run if you edit anything):**
- campaign11 bundle + campaign14 (`tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py`) → **≥164 passed, rc=0** (prior 164)
- full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`) → **≥4782 passed, 35 skipped, rc=0** (prior 4782/35)

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

### 2) Campaigns 6–25 (historical closure — no churn)
Closed/evidenced above. **Do not churn C6–C25 without a new, statable, reproducible failure with probe evidence.**

### 3) EXECUTE C26 — pipeline stress & cross-surface determinism (≥14 combos, HEAVY) — BINDING
Goal: stress end-to-end BAB pipeline under degenerate/extreme regimes and verify cross-surface (CLI/API/script) determinism, finiteness, and reporting fidelity. Produce real probe evidence.

**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c26_bab_pipeline_stress_determinism_probe_evidence.log`
Record for each combo: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` parse + finiteness walk where JSON produced), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 14 combos — execute all, add more if suspicious):**
1. CLI + in-process parity on real fixture with `transaction_costs` + `slippage` (strict finite JSON if produced, cumulative match `abs_tol=1e-12`).
2. All-NaN asset column → CLI/API rc=0 finite degenerate output, no Traceback, no NaN/Infinity tokens.
3. Single-asset universe (benchmark only) → rc=0 finite, no short possible, flat/valid weights.
4. Constant/zero returns series → finite cumulative, no NaN.
5. `beta_window` (e.g. 9999) > data length → rc=0 finite, no Traceback (real fixtures + short slice).
6. `min_observations` exceeding available data → flat/zero-weight periods, finite.
7. `transaction_costs=1.0` + `slippage=1.0` → cumulative finite (≥0 where applicable), no -inf/NaN, rc=0.
8. `regime_filter=True` (if supported via API/config path) → 3× identical `final_cumulative` (determinism).
9. `beta_neutral=True` → finite, strategy beta ≈ 0 within tolerance.
10. `ShortingConstraints` low borrow cap → finite weights/cumulative, no Traceback.
11. Position sizers (`kelly`/`vol_target`/`risk_parity`/`equal` or supported set) → finite, rc=0.
12. `report_to_json()` + `tear_sheet()` on degenerate run → strict JSON finite, tear_sheet renders no Traceback.
13. CLI repeated run 3× on same input → byte-identical stdout (determinism).
14. `--output` overwrite replaces stale content, rc=0, strict JSON finite.

Notes: CLI flags for regime/sizing/shorting/beta-neutral may be limited; exercise unsupported knobs via in-process API parity probes and record clearly. Prefer `tests/fixtures/real_market_prices*.csv`, `all_nan_column.csv`, `degenerate_metrics.csv`, synthetic generators as appropriate.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting modules/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` if evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign26*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs** (do not invent tests).

### 5) Validate comprehensively and record
- Re-run all Step 0 gates after any module/test edit, plus touched/new suites and any impacted reporting/CLI suites. Record exact counts/rc in HANDOFF.
- If no modules touched, state that Step 0 baseline was carried forward and confirm no regressions introduced.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update this file in place with: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or carried forward), C26 evidence log path, combo-by-combo PASS/FAIL + invariants, modules/tests touched (or none), and the next binding heavy campaign (**C27**) with a concrete ≥12-combo probe plan. No ambiguous handoff.

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

## Next binding campaign after C26 (pre-declared, execute if C26 clean)
**C27 — attribution, sizing/shorting edge interactions & script/report surface stress (≥12 combos, HEAVY):**
Evidence log: `/home/runner/work/_temp/kilo-tmp/c27_bab_attribution_sizing_shorting_report_probe_evidence.log`
Minimum plan: (1) attribution decomposition finite on real+degenerate runs; (2) `kelly`/`vol_target`/`risk_parity` with extreme vol/zero vol inputs; (3) `ShortingConstraints` borrow-cap/utilization edge cases; (4) `scripts/bab_backtest_report.py`/`load_real_bab_example.py` CLI-script parity & error contracts; (5) `strategy.report()`/`tear_sheet()`/JSON serialization under NaN/inf-guarded scenarios; (6) cost+slippage+regime combined determinism; (7) multi-rebalance freq comparisons deterministic; (8) overwrite/idempotence for report outputs; (9-12) additional stress combos from any suspicious C26/C27 observations. Same triage/fix/validate/handoff rules apply.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy C26 with probe evidence, remove bottlenecks if found, and leave a refreshed handoff.*
