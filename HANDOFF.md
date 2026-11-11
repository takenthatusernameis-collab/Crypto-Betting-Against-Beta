# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-11T01:30:21Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `e98ec5a` (`chore(kilo): checkpoint agent session`, 2026-11-11). Treat current HEAD as base and record exact HEAD when you run.
**Working tree (at refresh):** clean except `HANDOFF.md` updated in place (no competing handoff files; **`HANDOFF.md` is the single durable handoff**).
**Environment (verified):** `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (numpy 2.5.4 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0). Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).
**Bottlenecks:** None identified. No in-repo blocked sessions. `research_state/workflow_run_diagnostics.jsonl` holds historical concluded runs only — not a current blocker; do not chase diagnostics archaeology. `bab-example` console entrypoint **not installed on PATH** in this env (recorded concretely); use `python scripts/load_real_bab_example.py` direct execution as baseline.

**Prior campaign closure:** C6–C20 closed with evidence (C19 log `/home/runner/work/_temp/kilo-tmp/c19_*`; C20 log `/home/runner/work/_temp/kilo-tmp/c20_*`). C21 **EXECUTED on HEAD `e98ec5a`** with probe evidence → explicit **"no proven gaps"** (see below). **C22 is the immediate binding heavy campaign.**

---

## Step 0 baseline/gates — VERIFIED on HEAD `e98ec5a` (2026-11-11T01:30Z, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`)
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** ✓
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **164 passed in 207.96s, rc=0** ✓
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, rc=0** ✓ (warnings only)
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4782 passed, 35 skipped, rc=0** ✓ (hard floor met; warnings only)
- C19 regressions present: `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` ✓ (covered by full BAB floor)

**All gates GREEN.**

---

## C21 — metrics/reporting/CLI fidelity under stressed-but-valid and edge-valid regimes (EXECUTED, EVIDENCED)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c21_bab_e2e_parity_stress_probe_evidence.log` (probe script `/home/runner/work/_temp/kilo-tmp/c21_probe.py`, executed 2026-11-11T01:30Z). Record includes cmd, rc, stdout, stderr, JSON validity/finiteness (`allow_nan=False` semantics via strict parse + finiteness walk), key sets, determinism, parity, error-contract notes.

**Probe matrix executed (≥12 combos; all PASS):**
1. **CLI vs in-process `BABStrategy.run` parity (REAL):** `real_market_prices.csv --from-prices --benchmark BTC` → rc=0, `final_cumulative=0.3397354969330525 periods=398` identical to in-process `BABStrategy(...).run(returns_df=...)`, strict JSON finite.
2. **CLI vs in-process parity (EXPANDED + params, 2 sets):** `--beta-window 60`/`90`, quantile/cost variants → exact cumulative/periods parity, finite JSON.
3. **`bab-example` script vs in-process parity:** `python scripts/load_real_bab_example.py ... --from-prices --benchmark BTC` → rc=0, clean; console entrypoint `bab-example` not installed on PATH (recorded), direct script baseline used.
4. **`bab_backtest_report.py` / report schema & finiteness vs CLI JSON:** `--json` on REAL → rc=0, strict JSON finite, `metrics` + `rebalances` keys present, headline consistent with CLI.
5. **Repeated-run determinism (≥3 repeats, window 60 & 90):** byte/value-identical JSON across repeats and paths.
6. **Universe subset + benchmark interaction:** explicit `--universe` subsets incl. nonexistent-asset overlap edge → correct resolved universe, finite/deterministic, no unintended assets.
7. **Error-path parity (CLI vs API):** missing file, directory data, `--from-prices` without `--data`, invalid quantile/costs, empty/whitespace universe tokens, benchmark missing, output-is-directory → all rc=1 clean contract errors, no Traceback, no partial/corrupt output.
8. **Defective fixtures end-to-end:** `degenerate_metrics.csv` → rc=1 clean `Error running strategy: All price columns were metadata...` (no JSON — contract-consistent); `junk_columns.csv` / `all_nan_column.csv` → rc=0 clean degenerate finite JSON.
9. **Dry-run parity & validation:** REAL valid, synthetic valid, invalid output path rc=1, **no side-effect write** on dry-run.
10. **Cost/slippage sensitivity:** txn 0.0 / 0.001 / 0.01 → cumulative non-increasing `0.3397 → 0.3136 → 0.1518`, finite.
11. **Short/edge-valid regimes:** minimal slice window=30 near min-rows boundary; NaN-recoverable injected-NaN input → consistent rc/finite-or-clean-error across CLI/API.
12. **Output path/key stability:** 3 `--output` destinations incl. nested dir → identical JSON keys/values, no path-dependent divergence.

**C21 conclusion:** **NO PROVEN GAPS.** No silent corruption, no Traceback on user paths, strict finite JSON where produced, deterministic/stable keys/values, dry-run contract honored, defective inputs yield clean rc/error or clean degenerate output. No production/module fixes required; no new C21 regression tests added. **No modules touched.**

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

### 2) Campaigns 6–21 (historical closure — no churn)
C6–C21 reported closed with evidence. C21: explicit **"no proven gaps"**. **Do not churn C6–C21 without a new, statable, reproducible failure.**

### 3) Execute C22 — numerical/structural fidelity across API-internal paths & edge regimes (≥12 combos, HEAVY)
Goal: verify **BAB numerical determinism and structural fidelity** across surfaces not fully covered by C21: synthetic-seed determinism, universe permutation invariance, beta-neutral enforcement, regime filter, position-sizing (kelly/vol_target/risk_parity/equal), shorting constraints, attribution/tear_sheet/report_to_json serialization, CLI `--version`/dry-run config parity, `bab-example` entrypoint availability, concurrent-run determinism, large-universe stress, rebalance-frequency variation, min-observations boundary, cached `report()`/`tear_sheet()` identity.

Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c22_bab_numerical_structural_probe_evidence.log` (record cmd, rc, stdout, stderr, JSON validity/finiteness, key sets, determinism/parity/neutrality/bounds/metrics checks).

**Required probe matrix (minimum 12 combos; do more if anomalies appear):**
1. **Synthetic-seed determinism:** `BABStrategy` synthetic (no `--data`) with fixed `synthetic_seed` repeated ≥3× → identical `final_cumulative`/`periods`/report metrics; different seeds → different-but-finite results.
2. **Universe permutation invariance:** same assets in different `--universe` order on EXP → identical `final_cumulative`/`periods` (order-independent).
3. **Beta-neutral enforcement:** API `beta_neutral=True` (target 0.0, tolerance 1e-4) → computed strategy beta ≈ 0.0 (within tolerance), finite weights, rc=0.
4. **Regime filter path:** API `regime_filter=True` → finite scaled weights, `report()`/`tear_sheet()` strict JSON finite, no Traceback.
5. **Position sizing paths:** API `position_sizer` = `equal`/`kelly`/`vol_target`/`risk_parity` → finite weights, rc=0, report metrics finite.
6. **Shorting constraints path:** API `shorting_constraints` dict → weights respect configured caps, finite, no Traceback.
7. **Attribution + tear_sheet + report_to_json:** API `report()`, `tear_sheet()`, `report_to_json()` → strict JSON (`allow_nan=False`) parseable, all metrics finite, attribution_totals present.
8. **CLI `--version` & dry-run config parity:** `python -m ... --version` prints `bab 0.1.0`; `--dry-run` resolved config matches API `BABConfig` resolved values (benchmark, beta_window, quantiles, costs).
9. **`bab-example` console entrypoint:** check `which bab-example` / `python -m scripts.load_real_bab_example` availability; record contract explicitly (direct-script baseline used if not installed).
10. **Concurrent-run determinism:** same CLI args run twice concurrently → byte-identical stdout/`--output` JSON.
11. **Large-universe stress:** synthetic `n_assets=20, n_days=500` via API → rc=0, finite `final_cumulative`, no Traceback, report JSON strict.
12. **Rebalance-frequency variation:** API `rebalance_freq` = daily/weekly/monthly → finite, turnover consistent with frequency, no Traceback.
13. **Min-observations boundary:** `min_observations` near `beta_window` boundary (e.g. 60 vs 90) → rc=0 or clean contract error, finite-or-degenerate, no Traceback.
14. **Cached `report()`/`tear_sheet()` identity:** call `report()`/`tear_sheet()` without re-running → identical metrics to post-run report.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py`/`scripts/*` if evidence proves a gap. **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign22*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. If none, record explicit "no proven gaps" with evidence refs in the C22 log and this HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, Step 0 & validation counts/rc, C22 evidence (log path, combo summary, determinism/parity/fin/error-contract notes), touched modules, and the **next binding heavy campaign (C23)** with a concrete ≥12-combo probe plan. No generic "continue" handoff.

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
2. **EXECUTE C22** probe matrix (≥12 combos above) → write evidence log `/home/runner/work/_temp/kilo-tmp/c22_bab_numerical_structural_probe_evidence.log`.
3. **TRIAGE/FIX** proven gaps only (smallest non-locked change + regressions if needed) or record "no proven gaps".
4. **RE-RUN GATES** + impacted suites; record results.
5. **REFRESH THIS `HANDOFF.md`** with evidence and nominate **C23** (≥12 concrete combos).

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding — execute heavy work with probe evidence.*
