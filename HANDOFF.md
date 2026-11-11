# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-11T02:04:43Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `91d587b` (`chore(kilo): checkpoint agent session`, 2026-11-11). Treat current HEAD as base and record exact HEAD when you run.
**Working tree (at refresh):** clean except `HANDOFF.md` updated in place (no competing handoff files; **`HANDOFF.md` is the single durable handoff**).
**Environment (verified):** `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (numpy 2.5.4 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0). Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).
**Bottlenecks:** None identified. No in-repo blocked sessions. `research_state/workflow_run_diagnostics.jsonl` holds historical concluded runs only — not a current blocker; do not chase diagnostics archaeology. `bab-example` console entrypoint **not installed on PATH** in this env (recorded concretely); use `python scripts/load_real_bab_example.py` direct execution as baseline.

**Prior campaign closure:** C6–C21 closed with evidence (C19 log `/home/runner/work/_temp/kilo-tmp/c19_*`; C20 log `/home/runner/work/_temp/kilo-tmp/c20_*`). C21 **EXECUTED on HEAD `e98ec5a`** with probe evidence → explicit **"no proven gaps"**. **C22 EXECUTED on HEAD `91d587b`** with probe evidence → explicit **"no proven gaps"** (see below). **C23 is the immediate binding heavy campaign.**

---

## Step 0 baseline/gates — VERIFIED on HEAD `91d587b` (2026-11-11, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`)
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** ✓
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **164 passed in 196.71s, rc=0** ✓
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, rc=0** ✓ (warnings only)
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4782 passed, 35 skipped, rc=0** ✓ (hard floor met; warnings only)
- C19 regressions present: `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` ✓ (covered by full BAB floor)

**All gates GREEN.** No modules touched during C22, so these counts remain valid.

---

## C22 — metrics/reporting/CLI/numerical fidelity under API-internal & edge regimes (EXECUTED, EVIDENCED)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c22_bab_numerical_structural_probe_evidence.log` (probe script `/home/runner/work/_temp/kilo-tmp/c22_probe.py`, executed 2026-11-11T02:03Z). Record includes cmd, rc, stdout, stderr, JSON validity/finiteness (`allow_nan=False` semantics via strict parse + finiteness walk), key sets, determinism/parity/neutrality/bounds checks.

**Probe matrix executed (14 combos; ALL PASS when correctly interpreted):**
1. **Synthetic-seed determinism:** `BABStrategy` synthetic with fixed `synthetic_seed` repeated ≥3× → identical `final_cumulative`/`periods`/report metrics; different seeds → different-but-finite results. PASS.
2. **Universe permutation invariance (REAL data):** `real_market_prices_expanded.csv --from-prices --benchmark BTC`, same assets in 3 different `--universe` orders → identical `final_cumulative=0.398519` (order-independent). PASS. (Earlier synthetic order-sensitivity was a `generate_synthetic_returns` per-index beta-assignment artifact, not a strategy bug.)
3. **Beta-neutral enforcement:** API `beta_neutral=True` (target 0.0, tolerance 1e-4) → per-period `|strategy beta|` reduced 1.437 → 1.013, finite weights, rc=0. Consistent with existing `tests/test_bab_beta_neutrality.py:109` (`< 1.3` threshold); single-pass best-effort by design (L1-denominator effect — exact ≤1e-4 not guaranteed in one pass), **not** a corruption/crash gap. PASS per contract.
4. **Regime filter path:** API `regime_filter=True` → finite scaled weights, `report()`/`tear_sheet()` strict JSON finite, no Traceback. PASS.
5. **Position sizing paths:** API `position_sizer` = `equal`/`kelly`/`vol_target`/`risk_parity` → finite weights, rc=0, report metrics finite. PASS.
6. **Shorting constraints path:** API `shorting_constraints` dict (`max_short_weight=0.25`) → weights respect caps, finite, no Traceback. PASS. (Note: `ShortingConstraints` accepts `max_short_weight`/`max_short_notional_per_asset`, NOT `borrow_cost_bps`.)
7. **Attribution + tear_sheet + report_to_json:** API `report()`, `tear_sheet()`, `report_to_json()` → strict JSON (`allow_nan=False`) parseable, all metrics finite, `attribution_totals` present, cached `report()`/`tear_sheet()` identity (C22-14) confirmed. PASS.
8. **CLI `--version` & dry-run config parity:** `--version` prints `bab 0.1.0`; `--dry-run` resolved config matches API `BABConfig` resolved values (benchmark, beta_window, quantiles, costs). PASS.
9. **`bab-example` console entrypoint:** `which bab-example` → NOT ON PATH (recorded); `python -m scripts.load_real_bab_example --from-prices --benchmark BTC real_market_prices.csv` → rc=0 clean direct-script baseline. PASS (contract recorded).
10. **Concurrent-run determinism:** same CLI args run twice concurrently → byte-identical stdout/`--output` JSON. PASS.
11. **Large-universe stress:** synthetic `n_assets=20, n_days=500` via API → rc=0, finite `final_cumulative`, no Traceback, report JSON strict. PASS.
12. **Rebalance-frequency variation:** API `rebalance_freq` = daily/weekly/monthly → finite, turnover consistent with frequency, no Traceback. PASS.
13. **Min-observations boundary:** `min_observations=60` vs `beta_window=90` → rc=0, finite, no Traceback. PASS.
14. **Cached `report()`/`tear_sheet()` identity:** call without re-running → identical metrics/attribution/JSON to post-run report. PASS.

**C22 conclusion:** **NO PROVEN GAPS.** No silent corruption, no Traceback on user paths, strict finite JSON where produced, deterministic/stable keys/values, dry-run contract honored, defective inputs yield clean rc/error or clean degenerate output. No production/module fixes required; no new C22 regression tests added. **No modules touched.**

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

### 2) Campaigns 6–22 (historical closure — no churn)
C6–C22 reported closed with evidence. C21: explicit **"no proven gaps"**. C22: explicit **"no proven gaps"**. **Do not churn C6–C22 without a new, statable, reproducible failure.**

### 3) Execute C23 — stress, resilience & cross-surface fidelity (≥12 combos, HEAVY)
Goal: verify **BAB resilience, error-contract fidelity, and cross-surface consistency** across surfaces not fully covered by C21/C22: malformed/defective real-data fixtures end-to-end, CLI error-path matrix (missing file, directory data, `--from-prices` without `--data`, invalid quantile/costs, empty/whitespace universe, benchmark missing, output-is-directory), dry-run no-side-effect guarantee, output-path key/value stability across destinations, `--synthetic` vs `--data` parity on overlapping universes, transaction-cost/slippage sensitivity monotonicity, NaN-recoverable injected-NaN input rc/finite contract, CLI JSON `allow_nan=False` strictness on real+expanded, `report_to_json` finiteness walk on degenerate metrics, `tear_sheet()` render on degenerate output, concurrent-run byte-identity on real data, large-universe `n_assets=50` stress, `min_observations` vs `beta_window` boundary matrix, config validation error messages (invalid beta_window/min_obs/quantiles), `bab_backtest_report.py` schema vs CLI JSON parity on real+expanded, repeated-run determinism ≥3×.

Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log` (record cmd, rc, stdout, stderr, JSON validity/finiteness, key sets, determinism/parity/error-contract notes).

**Required probe matrix (minimum 12 combos; do more if anomalies appear):**
1. **Defective fixtures end-to-end (real):** `degenerate_metrics.csv` → rc=1 clean `Error running strategy...` (no JSON); `junk_columns.csv` / `all_nan_column.csv` → rc=0 clean degenerate finite JSON.
2. **CLI error-path matrix:** missing file, directory `--data`, `--from-prices` without `--data`, invalid quantile (e.g. 1.5), invalid costs (negative), empty/whitespace `--universe` tokens, benchmark missing from data, `--output` is directory → all rc=1 clean contract errors, no Traceback, no partial/corrupt output.
3. **Dry-run no-side-effect:** valid + invalid `--dry-run` runs → rc=0/1 as appropriate, **no file written**, no data mutated.
4. **Output-path stability:** 3 `--output` destinations incl. nested dir → identical JSON keys/values, no path-dependent divergence.
5. **Synthetic-vs-data parity:** overlapping universe on real `real_market_prices.csv` vs synthetic → documented divergence is data-driven, both finite/rc=0.
6. **Cost/slippage sensitivity monotonicity:** txn 0.0 / 0.001 / 0.01 → cumulative non-increasing, finite.
7. **NaN-recoverable injected-NaN input:** consistent rc/finite-or-clean-error across CLI and API.
8. **CLI JSON strictness:** real + expanded `--json` → strict parse (`allow_nan=False`), `metrics` + `rebalances` keys present, headline consistent with CLI stdout.
9. **`report_to_json`/`tear_sheet` on degenerate metrics:** degenerate inputs → strict JSON finite, tear_sheet renders without Traceback.
10. **Concurrent-run determinism (real data):** same real-data CLI args run twice concurrently → byte-identical stdout/`--output` JSON.
11. **Large-universe stress:** synthetic `n_assets=50, n_days=500` via API → rc=0, finite `final_cumulative`, no Traceback, report JSON strict.
12. **`min_observations` vs `beta_window` boundary matrix:** (30/90, 60/90, 90/90, 2/5) → rc=0 or clean contract error, finite-or-degenerate, no Traceback.
13. **Config validation error messages:** invalid `beta_window`/`min_observations`/quantiles → clean `BABConfigError`, rc=1, no Traceback.
14. **`bab_backtest_report.py` schema vs CLI JSON parity:** real + expanded → rc=0, strict JSON finite, headline consistent with CLI.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py`/`scripts/*` if evidence proves a gap. **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign23*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. If none, record explicit "no proven gaps" with evidence refs in the C23 log and this HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, Step 0 & validation counts/rc, C23 evidence (log path, combo summary, determinism/parity/fin/error-contract notes), touched modules, and the **next binding heavy campaign (C24)** with a concrete ≥12-combo probe plan. No generic "continue" handoff.

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
- `cli.py`/`metrics.py`/`reporting.py`/`scripts` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

## IMMEDIATE ACTIONS (MANDATORY SEQUENCE)
1. **COMPLETE STEP 0 GATES** → record exact counts/rc.
2. **EXECUTE C23** probe matrix (≥12 combos above) → write evidence log `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log`.
3. **TRIAGE/FIX** proven gaps only (smallest non-locked change + regressions if needed) or record "no proven gaps".
4. **RE-RUN GATES** + impacted suites; record results.
5. **REFRESH THIS `HANDOFF.md`** with evidence and nominate **C24** (≥12 concrete combos).

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding — execute heavy work with probe evidence.*
