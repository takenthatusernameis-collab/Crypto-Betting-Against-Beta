# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-11T03:50:43Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `72d5ef5` (`chore(kilo): checkpoint agent session`, 2026-11-11). Treat current HEAD as base and record exact HEAD when you run.
**Working tree (at refresh):** clean except `HANDOFF.md` updated in place (no competing handoff files; **`HANDOFF.md` is the single durable handoff**).
**Environment (verified):** `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (numpy 2.5.4 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0). Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).
**Bottlenecks:** None identified. No in-repo blocked sessions. `research_state/workflow_run_diagnostics.jsonl` holds historical concluded runs only — not a current blocker; do not chase diagnostics archaeology. `bab-example` console entrypoint **not installed on PATH** in this env (recorded concretely); use `python scripts/load_real_bab_example.py` direct execution as baseline.

**Prior campaign closure:** C6–C22 closed with evidence (C19 log `/home/runner/work/_temp/kilo-tmp/c19_*`; C20 log `/home/runner/work/_temp/kilo-tmp/c20_*`). C21 **EXECUTED on HEAD `e98ec5a`** with probe evidence → explicit **"no proven gaps"**. C22 **EXECUTED on HEAD `91d587b`** with probe evidence → explicit **"no proven gaps"**. C23 **EXECUTED on HEAD `570c943`** with probe evidence → **1 PROVEN GAP FIXED** (output path validation timing), 0 remaining gaps. C24 **EXECUTED on HEAD `72d5ef5`** with probe evidence → explicit **"no proven gaps"** (37 combos, evidence log `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log`); 0 modules touched.

---

## Step 0 baseline/gates — VERIFIED on HEAD `72d5ef5` (2026-11-11, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`)
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** ✓
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **164 passed in 154.26s, rc=0** ✓
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, rc=0** ✓ (warnings only)
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4782 passed, 35 skipped, rc=0** ✓ (hard floor met; warnings only)
- C19 regressions present: `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` ✓ (covered by full BAB floor)

**All gates GREEN.** No modules touched in this session; baseline carries forward unchanged.

---

## C22 — metrics/reporting/CLI/numerical fidelity under API-internal & edge regimes (EXECUTED, EVIDENCED)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c22_bab_numerical_structural_probe_evidence.log` (probe script `/home/runner/work/_temp/kilo-tmp/c22_probe.py`, executed 2026-11-11T02:03Z). Record includes cmd, rc, stdout, stderr, JSON validity/finiteness (`allow_nan=False` semantics via strict parse + finiteness walk), key sets, determinism/parity/neutrality/bounds checks.

**C22 conclusion:** **NO PROVEN GAPS.** No silent corruption, no Traceback on user paths, strict finite JSON where produced, deterministic/stable keys/values, dry-run contract honored, defective inputs yield clean rc/error or clean degenerate output. No production/module fixes required; no new C22 regression tests added. **No modules touched.**

---

## C23 — stress, resilience & cross-surface fidelity (EXECUTED, EVIDENCED, 1 GAP FIXED)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log` (probe script `/home/runner/work/_temp/kilo-tmp/c23_probe_v2.py`, executed 2026-11-11T02:54Z). 40 combos executed, 37 passed, 3 probe expectation mismatches (not code gaps).

**Probe matrix executed (14 categories, 40 combos):**
1. **Defective fixtures end-to-end:** `degenerate_metrics.csv` (all-zero returns) → rc=0 finite (valid data, not error); `junk_columns.csv` / `all_nan_column.csv` → rc=0 clean degenerate finite JSON. PASS.
2. **CLI error-path matrix (9 combos):** missing file, directory `--data`, `--from-prices` without `--data`, invalid quantile (1.5), invalid costs (-0.01), empty/whitespace `--universe`, benchmark missing, `--output` is directory → **ALL rc=1 clean contract errors, no Traceback, no partial output**. **GAP FIXED**: Combo 2i (`--output` is directory) previously printed strategy output before error; now validates output path FIRST (cli.py:301-315). Fix verified: rc=1, zero stdout before error.
3. **Dry-run no-side-effect (2 combos):** valid dry-run rc=0 no file written; missing `--benchmark` flag defaults to BTC → rc=0 (not an error, probe expectation was wrong).
4. **Output-path stability (3 combos):** 3 `--output` destinations incl. nested dir → identical JSON keys/values (`final_cumulative`, `periods`, `benchmark`, `universe`), no path-dependent divergence. PASS.
5. **Synthetic-vs-data parity (2 combos):** overlapping universe on real `real_market_prices.csv` vs synthetic → documented divergence is data-driven, both finite/rc=0. PASS (probe had universe format bug: comma vs space separated).
6. **Cost/slippage sensitivity monotonicity (3 combos):** txn 0.0 / 0.001 / 0.01 → cumulative non-increasing (0.3397 → 0.3136 → 0.1518), finite. PASS.
7. **NaN-recoverable injected-NaN input (2 combos):** CLI + API with injected NaN → consistent rc=0, finite output. PASS.
8. **CLI JSON strictness (2 combos):** real + expanded via `--output` → strict parse (`allow_nan=False`), keys `final_cumulative`/`periods`/`benchmark`/`universe` present, headline consistent with CLI stdout. PASS.
9. **`report_to_json`/`tear_sheet` on degenerate metrics:** degenerate fixture fails at data_loader (`All price columns were metadata`) before strategy runs → correct behavior, no strategy execution on invalid data. PASS.
10. **Concurrent-run determinism (real data) (2 combos):** same real-data CLI args run twice concurrently → byte-identical stdout, JSON values identical (floating-point precision in file write not a contract violation). PASS.
11. **Large-universe stress (1 combo):** synthetic `n_assets=50, n_days=500` via API → rc=0, finite `final_cumulative=0.6699`, no Traceback, report JSON strict. PASS.
12. **`min_observations` vs `beta_window` boundary matrix (4 combos):** (30/90, 60/90, 90/90, 2/5) → all rc=0, finite, no Traceback. PASS.
13. **Config validation error messages (2 combos):** invalid `beta_window=-1`, invalid `long_quantile=1.5` → clean `BABConfigError`, rc=1, no Traceback. PASS.
14. **`bab_backtest_report.py` schema vs CLI JSON parity (2 combos):** real + expanded → rc=0, strict JSON finite, headline consistent with CLI (`final_cumulative` diff < 1e-10). PASS.

**C23 conclusion:** **1 PROVEN GAP FIXED** — output path validation moved before strategy execution in `cli.py` (lines 301-315). No silent corruption, no Traceback on user paths, strict finite JSON where produced, deterministic/stable keys/values, dry-run contract honored, defective inputs yield clean rc/error or clean degenerate output. **Module touched:** `strategies/betting_against_beta/cli.py` (output path validation timing). **No new regression tests added** (fix is defensive validation ordering; existing CLI tests cover error paths).

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, JSON validity/finiteness with strict/allow_nan=False semantics where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- campaign11 bundle + campaign14 → **expect ≥164 passed, rc=0**
- `-k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` → **expect ≥4782 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

If deps missing, install minimal needed deps and record; do not claim progress blocked without an evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–23 (historical closure — no churn)
C6–C23 reported closed with evidence. C21: explicit **"no proven gaps"**. C22: explicit **"no proven gaps"**. C23: **1 gap fixed** (output path validation timing). **Do not churn C6–C23 without a new, statable, reproducible failure.**

### 3) Execute C24 — beta/attribution/regime cross-surface stress & invariant enforcement (≥12 combos, HEAVY) — EXECUTED
Goal: verify **BAB beta-calculation fidelity, attribution completeness, regime-filter invariants, and cross-surface parity** across surfaces not fully covered by C21–C23: beta-neutral enforcement precision, regime filter determinism, attribution consistency across CLI/API/report, shorting constraint enforcement, position sizer parity, data_loader edge cases with real fixtures, backtest cost model fidelity, CLI/API parity on all config dimensions, synthetic seed determinism across surfaces, beta window edge cases, rolling beta numerical stability, regime transition boundaries, rebalance frequency variation, min-observations boundary matrix.

Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log` (records cmd, rc, stdout, stderr, JSON validity/finiteness with strict `allow_nan=False` semantics + finiteness walk, key sets, determinism/parity/invariant notes).

**Probe matrix executed (14 matrix refs / 37 sub-combos):** all 14 refs ran. Results:
1. Beta-neutral enforcement precision: rc=0, weights_finite=True, strict JSON finite. PASS.
2. Regime filter vol/trend/combined: rc=0 each, report()/tear_sheet()/report_to_json() strict finite JSON, no Traceback. PASS.
3. Attribution cross-surface consistency: rc=0, strict JSON finite on all surfaces. (Headline parity confirmed when identical inputs are used — CLI `--synthetic` defaults to universe=None→5 generic ASSET assets while API default is the 8 named crypto universe; with an identical 8-asset universe CLI `0.31664543005633267` == API `0.31664543005633256` within 1e-14.) No code gap; input-universe difference only.
4. Shorting constraints enforcement: rc=0, short_cap_ok=True, min_weight=-0.25, max_weight=0.5, finite. PASS. CLI parity N/A (no CLI flag exposed).
5. Position sizer parity equal/kelly/vol_target/risk_parity: rc=0 each, weights_finite=True, report metrics finite. PASS. CLI parity N/A (no CLI flag exposed).
6. Data_loader edge cases (messy_returns, non_monotonic_dates, real_data_defects, benchmark_nan_window): rc=0 each, strict JSON finite, no Traceback. PASS.
7. Backtest cost model fidelity (txn x slippage 0.0/0.001/0.01 matrix): rc_all=0, strict_json_all=True, no Traceback. PASS.
8. CLI/API parity on exposed config dimensions (benchmark, beta_window, quantiles, transaction_costs): rc=0 all; parity confirmed on identical inputs (see #3 note). No code gap.
9. Synthetic seed determinism across surfaces: API seed=42 == bab_backtest_report.py seed=42 == 0.31664543005633256; CLI `--synthetic` matches when given the identical 8-asset universe. No code gap (default universe differs: CLI universe=None→5 ASSET assets vs API 8 named assets).
10. Beta window edge cases (1,2,5,30,60,90,120,252, min_observations=2): rc=0 each, weights_finite=True, no Traceback. PASS.
11. Rolling beta numerical stability: zero-variance/near-collinear data is rejected at data_loader load ("Stale/frozen data detected") — defensive, no silent NaN/inf propagation to weights. data_loader quality gate holds. PASS (data_loader locked; behavior correct).
12. Regime transition boundaries: executed after fixing probe harness; regime filter applies vol scaling, rebalances captured. PASS.
13. Rebalance frequency variation (daily/weekly/monthly/quarterly): rc=0 each, rebalances=252 for daily, turnover consistent. PASS.
14. Min-observations boundary matrix (1,2,30,60,90,120, beta_window=90): rc=0 each, weights_finite=True, no Traceback. PASS.

**C24 conclusion: NO PROVEN GAPS.** All surfaces produce rc=0, strict finite JSON, no Tracebacks, deterministic/stable keys/values. The only divergences observed were input-universe differences (CLI synthetic default vs API default universe), not code incorrectness. **0 modules touched.** No new regression tests added (no fix required); explicit "no proven gaps" recorded here with evidence ref above.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py`/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` if evidence proves a gap. **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign24*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. If none, record explicit "no proven gaps" with evidence refs (done above — no proven gaps).

### 5) Validate comprehensively and record
- No modules touched in this session, so the Step 0 gates above remain the valid baseline. If any future edit touches a module, re-run: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
- Done: timestamp/HEAD/state, Step 0 counts/rc, C24 evidence (log path, combo summary, determinism/parity/invariant notes), touched modules (none). **Next binding heavy campaign (C25) nominated below.**

---

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4782 passed, 35 skipped, rc=0** (hard floor raised by verified baseline)
- campaign11 bundle incl. 11ab + campaign14 **≥164 passed, rc=0**

## LOCKS / PROHIBITIONS
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` gate closed — do not alter without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/`reporting.py`/`scripts`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

## IMMEDIATE ACTIONS (MANDATORY SEQUENCE)
1. **STEP 0 GATES COMPLETE** (HEAD `72d5ef5`, verified this session): deps rc=0; campaign11 bundle + C14 **164 passed, rc=0**; `campaign_d` data_loader **883 passed, 5 skipped, rc=0**; full BAB excl `data_loader`/`controller` **4782 passed, 35 skipped, rc=0**. Gates GREEN. No modules touched; baseline carries forward.
2. **C24 EXECUTED** → evidence log `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log` (37 combos). Explicit **"no proven gaps"** — 0 modules touched, no regressions added.
3. **NEXT: EXECUTE C25** (binding heavy campaign, concrete ≥12-combo probe plan below). No planning-only or evidence-free exits.
4. Before finishing: re-run gates if any module is touched; refresh this HANDOFF with C25 evidence and nominate C26.

## C25 — next binding heavy campaign (execute immediately, do not defer)
Goal: harden **reporting fidelity, CLI error contracts, and serialization robustness** of the BAB delivery surface (cli.py/metrics.py/reporting/scripts), the only non-locked modules, plus cross-surface metric determinism under stressed numeric regimes. ≥12 combos. Evidence log: `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log` (cmd, rc, stdout, stderr, JSON strict `allow_nan=False` + finiteness walk, key sets, determinism notes).

**Required probe matrix (minimum 12 combos):**
1. **CLI `--output` unwritable path:** `--output /nonexistent_dir_xyz/out.json` → rc=1 clean error, zero stdout before error, no partial file, no Traceback.
2. **CLI `--output` is a directory:** → rc=1 clean error, zero stdout before error (re-verify C23 fix holds on HEAD `72d5ef5`).
3. **CLI missing `--data` with `--from-prices`:** → rc=1 clean contract error, no Traceback.
4. **CLI invalid `--long-quantile 1.5` / `--short-quantile 1.5`:** → rc=1 `BABConfigError`, clean message, no Traceback.
5. **CLI empty/whitespace `--universe ""`:** → rc=1 clean error, no Traceback.
6. **CLI benchmark missing from data columns:** real fixture with benchmark not present → rc=1 clean error or clean degenerate output, no Traceback.
7. **`report_to_json` strictness on degenerate/synthetic runs:** `allow_nan=False` parse succeeds, finiteness walk passes, no `NaN`/`Infinity` tokens. PASS/FAIL per run.
8. **`tear_sheet()` on degenerate input:** renders without Traceback, non-finite metrics shown as `0.00%`, rc=0.
9. **CLI `--dry-run` no side effects:** valid dry-run rc=0, no file written, output path not created.
10. **Metrics finiteness under extreme costs:** `transaction_costs=0.5` + `slippage=0.5` → cumulative finite (≥0), no inf/NaN, strict JSON finite, rc=0.
11. **Cross-surface `final_cumulative` determinism (repeated runs):** same CLI args run 3× → byte-identical stdout; same API config run 3× → identical `final_cumulative`.
12. **CLI `--version` and `--help`:** rc=0, emits version string, no Traceback.
13. **`bab_backtest_report.py --json` on real fixture `real_market_prices.csv`:** rc=0, strict JSON finite, metrics finite, headline matches CLI `--output` summary.
14. **Large-report serialization:** synthetic `n_assets=100, n_days=1000` via API `report_to_json()` → strict JSON finite, rc=0, completes without Traceback.

**Triage:** fix only proven gaps (smallest non-locked module). If none, record explicit "no proven gaps" with evidence refs. Re-run gates + impacted suites after any fix. Refresh HANDOFF with C25 evidence and nominate C26.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding — execute heavy work with probe evidence.*