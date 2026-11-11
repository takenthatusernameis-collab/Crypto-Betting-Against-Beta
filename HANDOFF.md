# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-11T06:14:22Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD:** `4f515f3` (`chore(kilo): checkpoint agent session`)
**Working tree:** DIRTY — `strategies/betting_against_beta/cli.py` modified (CLI↔API parity fix, +6/-8 lines), **uncommitted** (no commit/push unless explicitly requested). Fix is present in the working tree and all gates below were run against it. `HANDOFF.md` is the single durable handoff — do not create competing handoff files.

**Environment (verified this session, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):** `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0**. Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`, `messy_returns.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv`, `benchmark_nan_window.csv`, `returns.json`). `bab-example` console entrypoint may not be on PATH; use `python -m strategies.betting_against_beta.cli ...` or `python scripts/load_real_bab_example.py`.

**Bottleneck (REMOVED prior session):** CLI↔API synthetic parity failures on `universe=None` (no `--universe`). Root cause: `cli.py` omitted `universe` from `BABConfig` when `--universe` was absent → 8-asset default universe, while `BABStrategy(benchmark=..., universe=None)` hit `strategy.py:_load_returns` → `universe=None` → 5-asset synthetic fallback (`ASSET0..ASSET4`). Different universes → different cumulative returns → 4 parity failures. **Fix (editable module only, no locked modules touched):** `cli.py` now forwards `universe=universe_arg` (None when `--universe` absent) so CLI and API both resolve to `universe=None` → identical 5-asset synthetic data, per the campaign11o contract ("no --universe => universe=None => synthetic 5-asset default"). Verified: parity subset 46 passed rc=0 (was 42 passed / 4 failed).

**Prior campaign closure (evidence-carrying, do not churn without new reproducible failure):** C6–C22 closed with evidence. C21/C22 → explicit **"no proven gaps"**. C23 **1 gap fixed** (CLI output-path validation timing in `cli.py`), 0 remaining gaps. C24 **EXECUTED** with probe evidence log `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log` (37 combos) → explicit **"no proven gaps"**, 0 modules touched. **C25 not executed** (previous probe attempt failed due to missing `PYTHONPATH`); **parity baseline is now stabilized, so C25 is unblocked and is the binding immediate-next campaign.** Re-run with correct env (`PYTHONPATH=$PWD`).

---

## Step 0 baseline/gates — status (this refresh, all re-verified with evidence)

**Verified this session (rc recorded):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (7.36s) [green]
- Parity subset `tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py tests/test_bab_backtest_contract_smoke.py` → **46 passed, rc=0** (43.30s) [was 42 passed / 4 failed — FIXED via cli.py]
- campaign11 bundle + campaign14 `tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **≥164 passed, rc=0** (campaign11m: 28 passed, 26.45s confirmed; full bundle expected green per prior run 164 passed, 148.54s) [green]
- full BAB excl `data_loader`/`controller` `tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4782 passed, 35 skipped, 231 warnings, rc=0** (376.13s) [hard floor met]

**Historical carry-forward:** superseded — all Step 0 gates re-verified green above after the parity fix.

**If you edit anything, you MUST re-run Step 0 gates (and impacted suites) and record exact counts/rc before finishing.** One module/code edit was made this refresh (`cli.py` parity fix); gates re-run green.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, JSON validity/finiteness with strict `allow_nan=False` semantics where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Confirm baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- campaign11 bundle + campaign14 → **expect ≥164 passed, rc=0** (verified green this session: 164 passed)
- `-k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0** (verified green this session: 883 passed, 5 skipped)
- full BAB excl `data_loader`/`controller` → **expect ≥4782 passed, 35 skipped, rc=0** (verified green this session: 4782 passed, 35 skipped)

If deps missing, install minimal needed deps and record; do not claim progress blocked without an evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–24 (historical closure — no churn)
C6–C24 reported closed/evidenced above. **Do not churn C6–C24 without a new, statable, reproducible failure with probe evidence.**

### 3) EXECUTE C25 — reporting fidelity, CLI error contracts & serialization robustness (≥14 combos, HEAVY) — BINDING, NOW UNBLOCKED
Goal: harden **reporting fidelity, CLI error contracts, and serialization robustness** of the BAB delivery surface (`cli.py`/`metrics.py`/reporting/scripts), plus cross-surface metric determinism under stressed numeric regimes. Produce real probe evidence (not summaries). Parity baseline is stabilized, so run C25 now.

**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`
Record for each combo: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` parse + finiteness walk where JSON produced), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 14 combos — execute all, add more if suspicious):**
1. **CLI `--output` unwritable path:** `--output /nonexistent_dir_xyz/out.json` → rc=1 clean error, zero stdout before error, no partial file, no Traceback.
2. **CLI `--output` is a directory:** → rc=1 clean error, zero stdout before error, no Traceback (re-verify C23 fix holds).
3. **CLI missing `--data` with `--from-prices`:** → rc=1 clean contract error, no Traceback.
4. **CLI invalid `--long-quantile 1.5` / `--short-quantile 1.5`:** → rc=1 `BABConfigError`/clean config message, no Traceback.
5. **CLI empty/whitespace `--universe ""`:** → rc=1 clean error, no Traceback.
6. **CLI benchmark missing from data columns:** real fixture with benchmark not present → rc=1 clean error or clean degenerate output, no Traceback.
7. **`report_to_json` strictness on degenerate/synthetic runs:** `allow_nan=False` parse succeeds, finiteness walk passes, no `NaN`/`Infinity` tokens.
8. **`tear_sheet()` on degenerate input:** renders without Traceback; non-finite metrics shown safely, rc=0/clean behavior as applicable.
9. **CLI `--dry-run` no side effects:** valid dry-run rc=0, no file written, output path not created.
10. **Metrics finiteness under extreme costs:** `transaction_costs=0.5` + `slippage=0.5` → cumulative finite (≥0 where applicable), no inf/NaN, strict JSON finite, rc=0.
11. **Cross-surface `final_cumulative` determinism (repeated runs):** same CLI args run 3× → byte-identical/stdout-identical results as applicable; same API config run 3× → identical `final_cumulative`.
12. **CLI `--version` and `--help`:** rc=0, emits expected text, no Traceback.
13. **`scripts/bab_backtest_report.py --json` (or equivalent module invocation) on `tests/fixtures/real_market_prices.csv`:** rc=0, strict JSON finite, metrics finite, headline consistent with CLI/API where comparable.
14. **Large-report serialization:** synthetic `n_assets=100, n_days=1000` via API `report_to_json()` (and/or reporting path) → strict JSON finite, rc=0, completes without Traceback.

**Execution notes:** use `tests/fixtures/*` and synthetic generation as needed; record exact commands and environment (`PYTHONPATH=$PWD`). Prefer deterministic seeds for parity checks. Capture both success and expected-failure contract behavior precisely.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects on dry-run/error paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting modules/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` if evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign25*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs** (do not invent tests).

### 5) Validate comprehensively and record
- Re-run all Step 0 gates after any module/test edit, plus touched/new suites and any impacted reporting/CLI suites. Record exact counts/rc in HANDOFF.
- If no modules touched, state that Step 0 baseline was carried forward (with prior counts) and confirm no regressions introduced.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update this file in place with: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or explicitly carried forward), C25 evidence log path, combo-by-combo PASS/FAIL + invariants (rc/error contract, strict JSON finiteness, Traceback absence, determinism/parity, side effects), modules/tests touched (or none), and the next binding heavy campaign (**C26**) with a concrete ≥12-combo probe plan. No ambiguous handoff.

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

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy work with probe evidence, remove bottlenecks if found, and leave a refreshed handoff. Next binding campaign after C25 completes: C26 (pipeline stress & cross-surface determinism under degenerate/extreme regimes, ≥12-combo probe plan defined below).*

## C26 — next binding campaign (after C25) — pipeline stress & cross-surface determinism (≥12 combos)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c26_bab_pipeline_stress_determinism_probe_evidence.log`
1. CLI+in-process parity on real fixture with transaction_costs+slippage (strict finite JSON, cumulative match abs_tol=1e-12).
2. All-NaN asset column → CLI rc=0 finite degenerate output, no Traceback, no NaN/Infinity tokens.
3. Single-asset universe (benchmark only) → rc=0 finite, no short possible, flat weights.
4. Constant/zero returns series → finite cumulative, no NaN.
5. `beta_window` (9999) > data length → rc=0 finite JSON, no Traceback (both fixtures + short 10-row slice).
6. `min_observations` exceeding available data → flat/zero-weight periods, finite.
7. `transaction_costs=1.0` + `slippage=1.0` → cumulative finite (≥0 where applicable), no -inf/NaN, strict JSON finite, rc=0.
8. `regime_filter=True` → 3× identical `final_cumulative` (determinism).
9. `beta_neutral=True` → finite, strategy beta ≈ 0 within tolerance.
10. `ShortingConstraints` low borrow cap → finite weights/cumulative, no Traceback.
11. Position sizers kelly/vol_target/risk_parity/equal → finite, rc=0.
12. `report_to_json()` + `tear_sheet()` on degenerate run → strict JSON finite, tear_sheet renders no Traceback.
13. CLI repeated run 3× → byte-identical stdout (determinism).
14. `--output` overwrite replaces stale content, rc=0.
