# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T10:34:59Z
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**HEAD:** `4b80110` (`chore(kilo): checkpoint agent session`)
**Working tree at refresh:** clean tracked state observed except this `HANDOFF.md` update in progress and stale `.kilo/handoff.md` removed this session (bottleneck cleanup). No other product changes. No commit/push. **This file is the single durable handoff** — do not create competing handoff files.

## Environment / quick start (verified this session)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`)
- Python deps present; gates runnable. CLI: `python -m strategies.betting_against_beta.cli --help` OK (historically verified).
- Key fixtures present under `tests/fixtures/` (real/degenerate/messy/benchmark-nan etc.).

## Bottleneck removal status (this session)
- **Removed stale handoff:** `.kilo/handoff.md` deleted to eliminate competing durable handoff sources.
- **No blocking runtime/env bottlenecks found now:** deps installed, repo readable, tests runnable. Prior `research_state/workflow_run_diagnostics.jsonl` contains historical tool-error diagnostics but no current reproducible in-repo blocker observed. If deps/env break, install minimal deps and record evidence before claiming blocked.

## Historical closure (do not churn without new reproducible failure + probe evidence)
- **C6–C22:** closed with evidence.
- **C23:** 1 gap fixed (CLI output-path validation timing), 0 remaining. Evidence: `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log`
- **C24:** 37 combos, **no proven gaps**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log`
- **C25:** 14 required combos + corrected probes, **no proven gaps**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`
- **C26:** executed (14 combos), **0 production module/test edits**, probe artifacts under `/home/runner/work/_temp/kilo-tmp/`. Evidence: `/home/runner/work/_temp/kilo-tmp/c26_bab_pipeline_stress_determinism_probe_evidence.log`, `c26_followup_evidence.log`, `c26_final_verify.log` (repro scripts `c26_probe.py`, `c26_followup.py`, `c26_final_verify.py`).
  - Clean/PASS themes: degenerate all-NaN asset, single-asset universe, extreme window/min-observations, max costs/slippage, regime determinism, supported sizing/shorting finite behavior, repeated-run stdout determinism, output overwrite.
  - **REVIEW (resolve only with canonical apples-to-apples repro before claiming gap):** C01 CLI↔API parity harness comparability, C04 stale/frozen constant-series guard contract (expected vs desired UX), C09 `beta_neutral=True` tolerance/semantic expectation vs observed `strategy_beta`. C12 strict JSON/tear_sheet clean on 5-row degenerate fixture; raw 50-row zero hits C04 guard.
- **Do not churn C6–C26** without a new, statable, reproducible failure with probe evidence.

## Step 0 baseline/gates (this refresh)

**Re-run this session (recorded):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`)
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (10.16s)

**Not re-run this session (carried forward from prior recorded green; MUST re-run before finishing if you edit anything):**
- campaign11 bundle + campaign14 (`tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py`) → **expect ≥164 passed, rc=0**
- full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`) → **expect ≥4782 passed, 35 skipped, rc=0**

**If you edit anything, re-run ALL Step 0 gates (and impacted suites) and record exact counts/rc before finishing.**

---

## BINDING INITIAL TASK MESSAGE (execute immediately — heavy work required)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, JSON validity/finiteness with strict `allow_nan=False` where JSON produced) and either (a) regressions for proven gaps or (b) explicit **"no proven gaps"** with evidence references.

### 1) Confirm baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- campaign11 bundle + campaign14 → **expect ≥164 passed, rc=0**
- full BAB excl `data_loader`/`controller` → **expect ≥4782 passed, 35 skipped, rc=0**

If deps missing, install minimal deps and record; do not claim blocked without evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–26 (historical closure — no churn)
Closed/evidenced above. **Do not churn C6–C26 without a new, statable, reproducible failure with probe evidence.** Resolve C26 review items only via canonical apples-to-apples repros proving a real defect.

### 3) EXECUTE C27 — attribution, sizing/shorting edge interactions & script/report surface stress (≥12 combos, HEAVY) — BINDING
**Goal:** stress attribution decomposition, sizing/shorting interactions, script/report surfaces, and resolve C26 review items only when canonically proven/disproven. Produce real probe evidence.

**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c27_bab_attribution_sizing_shorting_report_probe_evidence.log`
For each combo record: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` + finiteness walk where applicable), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 12 combos — execute all; add more if suspicious):**
1. **C26-C01 canonical parity repro:** identical input/loader/config for CLI (`--output` JSON) vs in-process API → full-precision `final_cumulative`, `abs` diff vs `1e-12`, conclude proven parity gap or probe artifact.
2. **Attribution decomposition finite (real run):** `real_market_prices.csv`/returns fixture → components finite, keys stable, reconciliation sane per contract, strict JSON if serialized.
3. **Attribution on degenerate/flat run:** quality-safe degenerate fixture (e.g. 5-row) → finite, no NaN/Infinity, no Traceback.
4. **Sizing edges:** `kelly`/`vol_target`/`risk_parity`/`equal` on extreme/zero-vol inputs (API as needed) → finite weights/cumulative, rc=0, no Traceback.
5. **Shorting constraints:** borrow-cap/utilization edges per supported `ShortingConstraints` API → constraints respected, finite, no Traceback.
6. **C26-C09 canonical beta-neutral check:** `beta_neutral=True` with explicit config/tolerance on real fixture → `strategy_beta`, tolerance, finiteness, 3× determinism; conclude proven gap vs expected behavior.
7. **Script surface:** `scripts/bab_backtest_report.py` and/or `scripts/load_real_bab_example.py` with valid fixtures → rc=0, finite/valid output, no Traceback; determinism if stable.
8. **Script/CLI error-contract parity:** missing/invalid inputs → rc!=0 clean actionable errors, no Traceback, no partial/corrupt output.
9. **`strategy.report()` / `tear_sheet()` / JSON serialization:** guarded/degenerate cases → strict JSON finite, tear_sheet renders without Traceback.
10. **Combined stress determinism:** `transaction_costs` + `slippage` + `regime_filter` (+ sizing/shorting if supported) → 3× identical key outputs.
11. **Rebalance-frequency comparison:** daily/weekly/monthly on same input → finite, deterministic per-freq, no Traceback.
12. **Report/output overwrite & idempotence:** repeated `--output`/script report generation replaces stale content, strict JSON finite, rc=0.

Notes: exercise API paths where CLI flags unavailable and record unsupported knobs explicitly. Prefer `tests/fixtures/*` and minimal deterministic synthetic slices. **C26-C04:** confirm stale/frozen constant-series contract with canonical probe; treat as proven gap only if behavior contradicts intended contract.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` when evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign27*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required/justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs** (do not invent tests).

### 5) Validate comprehensively and record
- After any module/test edit, re-run all Step 0 gates plus touched/new suites and impacted reporting/CLI suites; record exact counts/rc in HANDOFF.
- If no modules touched, state baseline carried forward/partially re-run and confirm no regressions introduced.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update this file in place with: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or carried forward), C27 evidence log path, combo-by-combo PASS/FAIL/REVIEW + invariants, modules/tests touched (or none), and the next binding heavy campaign (**C28**) with concrete ≥12-combo probe plan. No ambiguous handoff.

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
Minimum plan: (1) CLI↔API parity on all supported CLI knobs with `--output` full-precision JSON; (2) `--dry-run` contract matrix (valid/invalid/missing/dir/conflict) no side effects; (3) config boundary/validation error contracts (quantiles, windows, costs/slippage, universe/benchmark) stable rc/messages; (4) synthetic reproducibility (`seed`/determinism) 3×; (5) real-fixture multi-run determinism across costs/slippage/regime/sizing combos; (6) metrics/report JSON schema stability & strict finiteness; (7) attribution/report/tear_sheet cross-consistency; (8) script outputs deterministic & overwrite-safe; (9) edge universes (2-asset, benchmark-heavy, sparse history) finite; (10) non-monotonic/defect fixture handling contracts per supported paths; (11) output path/permission-like edge handling; (12) any residual C26/C27 review items with canonical repro. Same triage/fix/validate/handoff rules apply.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy C27 with probe evidence, remove bottlenecks if found, and leave a refreshed handoff.*
