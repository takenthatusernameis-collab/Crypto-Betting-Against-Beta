# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-11T00:45:18Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `2d867ac` (`chore(kilo): checkpoint agent session`, 2026-11-11). Treat current HEAD as base and record exact HEAD when you run.
**Working tree (at refresh):** clean before this session's handoff update except `HANDOFF.md` updated in place (no competing handoff files; **`HANDOFF.md` is the single durable handoff**).
**Environment (verified):** `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (numpy 2.5.4 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0). Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).

**Bottlenecks/status:** No in-repo blocked sessions identified. `research_state/workflow_run_diagnostics.jsonl` contains historical captured workflow runs (all concluded success) and log excerpts (timeouts/tool-arg noise in past agent logs) — **not a current blocker**; do not chase diagnostics archaeology. Prior campaigns C6–C19 reported closed with probe evidence; C19 regressions exist (`tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py`). **C20 executed on this HEAD (`2d867ac`) with probe evidence — explicit "no proven gaps" (see below). C21 is the immediate binding heavy campaign.**

## Step 0 baseline/gates — VERIFIED on HEAD `2d867ac` (2026-11-11T00:45Z, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`)
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** ✓
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **164 passed in 197.65s, rc=0** ✓
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, rc=0** ✓ (warnings only)
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4782 passed, 35 skipped, rc=0** ✓ (hard floor met; warnings only)
- C19 regressions present: `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` ✓ (covered by full BAB floor)

**All gates GREEN.**

## C20 — metrics/reporting/CLI fidelity under stressed-but-valid and edge-valid regimes (EXECUTED, EVIDENCED)
**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c20_bab_metrics_reporting_stress_fidelity_probe_evidence.log` (probe script `/home/runner/work/_temp/kilo-tmp/c20_probe.py`, executed 2026-11-11T00:43Z+). Record includes cmd, rc, stdout/stderr, traceback presence, and JSON validity/finiteness checks; summary JSON files inspected.

**Probe matrix executed (≥12 combos):**
1. **Short history near limits:** `--from-prices` slice of expanded real prices (40 rows, `--beta-window 30`) → rc=0, no Traceback, finite result `final_cumulative=0.9866031585744475 periods=39`, strict JSON output written/finite. Too-short slice (10 rows, window 30) → rc=0, no Traceback, degenerate-but-clean `final_cumulative=1.0 periods=9` (contract-consistent clean behavior, no corruption).
2. **Sparse but valid universe:** REAL (`real_market_prices.csv`, `--from-prices`, `--universe BTC ETH SOL`) → rc=0, no Traceback, `final_cumulative=0.40408157008657847 periods=398`, JSON finite/stable keys `{benchmark,final_cumulative,periods,universe}` with expected subset.
3. **High-NaN-but-recoverable:** injected NaNs in SOL/XRP windows on expanded prices (otherwise valid) → rc=0, no Traceback, `final_cumulative=0.6727179717916878 periods=398`, finite JSON.
4. **Zero/near-zero return regimes:** constant-price columns (ETH/SOL/BNB) constructed from real fixture → rc=1, **clean contract error** `Error running strategy: Stale/frozen data detected in column 'ETH': 50 consecutive equal values`, no Traceback, no partial/corrupt JSON (handled invalid/degenerate input surfaced cleanly).
5. **Benchmark presence / valid edge:** expanded real prices with explicit universe including benchmark (`BTC,ETH,BNB,XRP`) → rc=0, no Traceback, `final_cumulative=0.6024885647369919 periods=398`, finite JSON.
6. **Extreme but valid cost/slippage:** REAL `--transaction-costs 0.05 --slippage 0.05` → rc=0, no Traceback, heavy but finite drag `final_cumulative=6.997015346277106e-05 periods=398`, strict JSON finite.
7. **`--dry-run` vs run config parity:** dry-run on REAL (`--from-prices --beta-window 90 --transaction-costs 0.001`) → rc=0, resolved config printed (version 0.1.0, benchmark BTC, empty derived universe, beta_window 90, costs/slippage/min_rows as expected, `data: ... valid, --from-prices=True`), no Traceback. Matching run → rc=0, `final_cumulative=0.31357452508222267 periods=398`, finite JSON consistent with run intent.
8. **JSON key stability/determinism:** 3 repeated runs on expanded REAL (same args/output names varied) and 2 runs to different output paths → all rc=0, identical stdout `Final cumulative return: 0.651674 / Periods: 398`, identical JSON objects/keys/values across repeats and paths (`final_cumulative=0.6516736900335839`), strict JSON `allow_nan=False` parseable, all finite.
9. **`bab-example` console script parity:** `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output .../ex1.json` → rc=0, no Traceback, `cumulative_return=0.456327 periods=398`, JSON finite (`universe=[]` per script semantics). Console entrypoint `bab-example` **not installed on PATH** in this env (`FileNotFoundError`) — recorded concretely; module/script direct execution baseline used (note: example script uses different defaults/CLI contract than `python -m strategies.betting_against_beta.cli`, so numeric parity differs as expected by interface, not a fidelity bug).
10. **`--from-prices` vs precomputed returns equivalence:** REAL prices converted to returns vs `--from-prices` on same underlying fixture → both rc=0, identical finite results `final_cumulative=0.3397354969330525 periods=398`, identical JSON semantics.
11. **Explicit `--universe` subset valid overlap:** expanded REAL `--universe BTC ADA DOT LINK` → rc=0, no Traceback, `final_cumulative=0.49476996862389383 periods=398`, universe in JSON reflects resolved subset `["BTC","ADA","DOT"]` (overlap with data) — finite/deterministic, no unintended assets.
12. **Defective-but-handled fixtures:** `degenerate_metrics.csv` + `--from-prices` → rc=1 clean `Error running strategy: All price columns were metadata; no tradable assets remain`, no Traceback. `junk_columns.csv` → rc=0 clean degenerate `Final cumulative return: 1.000000 Periods: 7`, no Traceback. `all_nan_column.csv` → rc=0 clean degenerate `Final cumulative return: 1.000000 Periods: 7`, no Traceback. No partial/corrupt JSON observed.

**C20 conclusion:** **NO PROVEN GAPS.** No silent corruption, no Traceback on exercised user paths, strict JSON outputs finite/parseable where produced, deterministic/stable keys/values across repeats/paths, from-prices vs precomputed-returns parity exact on tested fixture, dry-run config reporting consistent, and defective/edge inputs yielded clean rc/error or clean degenerate outputs per observed contracts. No production/module fixes required; no new C20 regression tests added.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, JSON validity/finiteness with `allow_nan=False` where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4782 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

If deps missing, install minimal needed deps and record; do not claim progress blocked without an evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–20 (historical closure — no churn)
C6–C20 reported closed with evidence (C19 log `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log`; C20 log `/home/runner/work/_temp/kilo-tmp/c20_bab_metrics_reporting_stress_fidelity_probe_evidence.log`). C19/C20 conclusions: explicit **"no proven gaps"** on exercised matrices. **Do not churn C6–C20 without a new, statable, reproducible failure.**

### 3) Execute C21 — end-to-end stress/parity fidelity across API/CLI/script/reporting surfaces (≥12 combos, HEAVY)
Goal: verify **BAB end-to-end parity and reporting/schema fidelity** across surfaces (CLI `python -m strategies.betting_against_beta.cli`, in-process `BABStrategy`/API, `scripts/load_real_bab_example.py`, and `scripts/bab_backtest_report.py`/backtest report outputs where applicable) — strict JSON/finite outputs, deterministic keys/values, clean equivalent error contracts, and no Traceback on user paths.

Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c21_bab_e2e_parity_stress_probe_evidence.log` (record cmd, rc, stdout, stderr, JSON validity/finiteness `allow_nan=False`, key sets, determinism, parity/neutrality/shorting/bounds/metrics checks where applicable).

**Required probe matrix (minimum 12 combos; do more if anomalies appear):**
1. **CLI vs in-process `BABStrategy.run` parity (REAL prices):** run `python -m strategies.betting_against_beta.cli --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output ...` and equivalent in-process call (`load_prices` + `BABStrategy(...).run`) → compare final cumulative/periods/key metrics & config-resolved behavior per contract; no divergence, finite JSON.
2. **CLI vs in-process parity (EXPANDED + params):** same on `real_market_prices_expanded.csv` with explicit `--beta-window/--long-quantile/--short-quantile/--transaction-costs/--slippage` variants (≥2 param sets) → deterministic parity and finite outputs.
3. **`bab-example` script vs in-process parity with matching args:** run `python scripts/load_real_bab_example.py ...` and in-process with matching defaults/args (note script defaults differ from module CLI) → parity under equivalent configuration; record console-script availability/contract explicitly.
4. **`bab_backtest_report.py` / report output schema & finiteness vs CLI JSON:** generate report artifacts (if supported) on REAL/EXP and compare schema keys, finiteness, and consistency of headline metrics vs CLI `--output` JSON; no NaN/inf leakage, strict JSON where applicable.
5. **Repeated-run determinism under varied params:** ≥3 repeats each for varied `--beta-window` (e.g. 60, 90) and quantile/universe subsets on REAL/EXP → byte/value-identical outputs per contract across repeats and output paths.
6. **Universe subset + benchmark interaction:** explicit `--universe` subsets including/excluding non-benchmark assets on REAL/EXP (and overlap edge) → correct resolved universe, neutral/finite/deterministic results, no unintended assets.
7. **Error-path parity (CLI vs API):** same invalid/malformed inputs exercised via CLI and in-process/API (e.g. missing file, directory path, unreadable/unsupported where safely constructible, benchmark missing, invalid quantiles/costs/windows, `--from-prices` without `--data`, empty/whitespace universe tokens) → clean equivalent contract errors (rc/messages/exceptions), no Traceback/partial output.
8. **Defective-but-handled fixtures end-to-end:** `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv` via CLI (and API if meaningful) → clean rc/error or clean degenerate finite outputs, no Traceback/corrupt JSON.
9. **Dry-run parity & validation:** `--dry-run` vs run for REAL/EXP and parameterized cases (including `--output` path validation behavior as applicable) → resolved config consistent, no side-effect writes on dry-run, clean errors on invalid targets.
10. **Cost/slippage sensitivity monotonicity/consistency:** same input/params with increasing valid `--transaction-costs`/`--slippage` (incl. zero vs nonzero) → finite outputs and consistent drag direction/values per contract across surfaces.
11. **Short/edge-valid regimes parity:** minimal/short valid slices near window/min-rows boundaries and NaN-recoverable inputs (constructed safely) across CLI/API → consistent rc/finite-or-clean-error behavior per contract.
12. **Output path/key stability:** multiple `--output` destinations (nested dirs) and repeated runs → stable JSON schema/keys/finite values, deterministic content; no path-dependent divergence.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py`/`scripts/*` (if in-scope for proven gap) if evidence proves a gap. **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign21*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required and justified) for every proven fix. If none, record explicit "no proven gaps" with evidence refs in the C21 log and this HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, Step 0 & validation counts/rc, C21 evidence (log path, combo summary, determinism/parity/fin/error-contract notes), touched modules, and the **next binding heavy campaign (C22)** with a concrete ≥12-combo probe plan. No generic "continue" handoff.

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
2. **EXECUTE C21** probe matrix (≥12 combos above) → write evidence log `/home/runner/work/_temp/kilo-tmp/c21_bab_e2e_parity_stress_probe_evidence.log`.
3. **TRIAGE/FIX** proven gaps only (smallest non-locked change + regressions if needed) or record "no proven gaps".
4. **RE-RUN GATES** + impacted suites; record results.
5. **REFRESH THIS `HANDOFF.md`** with evidence and nominate **C22** (≥12 concrete combos).

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding — execute heavy work with probe evidence.*
