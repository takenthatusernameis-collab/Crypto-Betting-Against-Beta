# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp (refreshed):** 2026-11-10T23:31:35Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `403d8bb` (`chore(kilo): checkpoint agent session`, 2026-11-10 23:15:00 +0000). Treat current HEAD as base and record exact HEAD when you run.
**Working tree (at refresh):** clean (`git status --short` empty). No competing handoff files; **`HANDOFF.md` is the single durable handoff** (update in place only).
**Environment (expected/last observed):** `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0. Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).

**Bottlenecks/status:** No in-repo blocked sessions identified. `research_state/workflow_run_diagnostics.jsonl` contains historical captured workflow runs (all concluded success) and log excerpts (timeouts/tool-arg noise in past agent logs) — **not a current blocker**; do not chase diagnostics archaeology. Prior campaigns C6–C19 reported closed with probe evidence; C19 regressions exist (`tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py`). **C20 is NOT yet executed on this HEAD — it is the immediate binding heavy campaign.**

**Baseline/gates VERIFIED on current HEAD `403d8bb` (2026-11-10T23:31Z, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** ✓
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **164 passed in 197.51s, rc=0** ✓
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, rc=0** ✓
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4782 passed, 35 skipped, rc=0** ✓ (exceeds 4764 hard floor)
- C19 regressions: `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` → **18 passed, rc=0** ✓

**All gates GREEN. Ready for C20 execution.**

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, and JSON validity/finiteness with `allow_nan=False` where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4764 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

If deps missing, install minimal needed deps and record; do not claim progress blocked without an evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–19 (historical closure — no churn)
C6–C19 reported closed with evidence (C19 log: `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log`). C19 conclusion: explicit **"no proven gaps"** across config/cost/slippage/sizing/CLI fidelity probes; regressions locked in `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py`. **Do not churn C6–C19 without a new, statable, reproducible failure.**

### 3) Execute C20 — metrics/reporting/CLI fidelity under stressed-but-valid and edge-valid regimes (≥12 combos, HEAVY)
Goal: verify **BAB metrics/reporting/CLI fidelity** under stressed-but-valid regimes — no silent corruption, strict JSON/finite outputs where contract requires, deterministic/stable keys, and correct clean errors on invalid-but-user-facing edges.

Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c20_bab_metrics_reporting_stress_fidelity_probe_evidence.log` (record cmd, rc, stdout, stderr, JSON validity/finiteness `allow_nan=False`, key sets, determinism, neutrality/shorting/bounds checks where applicable).

**Required probe matrix (minimum 12 combos; do more if anomalies appear):**
1. Very short history near limits: slice REAL to minimal rows around `beta_window`/`min_periods`/`min_rows` behavior (e.g. small window like 30 with enough rows, and boundary-ish short slices) → rc/behavior per contract, no Traceback, metrics finite or clean `BABDataError` as specified.
2. Sparse but valid universe: run on a reduced valid subset (e.g. BTC + 2-3 assets) from REAL/EXP → finite metrics, neutral weights, deterministic.
3. High-NaN-but-recoverable rows/columns: construct/fixture inputs where some assets/rows are NaN but run remains valid per loader contract → verify finite outputs or clean contract error (no silent corruption).
4. Zero/near-zero return regimes: constant/near-zero columns or windows (using valid fixtures/synthetic-safe construction consistent with existing tests) → metrics/backtest finite, no NaN/inf leakage in CLI JSON.
5. Benchmark-equals-asset / benchmark presence edge cases on valid data → correct behavior (no division blow-ups, finite results).
6. Extreme but valid cost/slippage combos (e.g. high but valid `transaction_costs`/`slippage`) → monotonic/consistent drag, cumulative/metrics finite, strict JSON.
7. `--dry-run` vs run config parity on same inputs (REAL, EXP, and at least one parameterized variant) → resolved config consistent with run intent, no Traceback.
8. CLI JSON key stability/determinism across repeated runs and across different `--output` paths (REAL & EXP) → byte-identical or value-identical per contract, strict JSON `allow_nan=False`.
9. `bab-example` console script parity with module CLI on REAL/EXP (same args → equivalent stdout/JSON semantics, rc, no Traceback). If console script unavailable, record concrete evidence and use `python -m` baseline parity.
10. `--from-prices` vs precomputed returns equivalence/parity on same underlying REAL fixture (where loader semantics allow) → final metrics/periods consistent per contract, finite.
11. Explicit `--universe` subset valid overlap on REAL → runs, neutral/finite/deterministic, no unintended assets.
12. Defective-but-handled fixtures (`degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`) via CLI and/or API as appropriate → clean rc/error contract, no Traceback, no partial/corrupt JSON.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics, unexpected non-finite, incorrect rc/error contract, Traceback on user paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py` if evidence proves a gap. **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`.
- Add regressions in `tests/test_bab_cli_campaign20*.py` for every proven fix. If none, record explicit "no proven gaps" with evidence refs in the C20 log and this HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, Step 0 & validation counts/rc, C20 evidence (log path, combo summary, determinism/neutrality/fin/parity notes), touched modules, and the **next binding heavy campaign (C21)** with a concrete ≥12-combo probe plan. No generic "continue" handoff.

---

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4764 passed, 35 skipped, rc=0** (hard floor)
- campaign11 bundle incl. 11ab + campaign14 **≥164 passed, rc=0**

## LOCKS / PROHIBITIONS
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` gate closed — do not alter without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/`reporting.py` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

## IMMEDIATE ACTIONS (MANDATORY SEQUENCE)
1. **COMPLETE STEP 0 GATES** → record exact counts/rc.
2. **EXECUTE C20** probe matrix (≥12 combos above) → write evidence log `/home/runner/work/_temp/kilo-tmp/c20_bab_metrics_reporting_stress_fidelity_probe_evidence.log`.
3. **TRIAGE/FIX** proven gaps only (smallest non-locked change + `tests/test_bab_cli_campaign20*.py`) or record "no proven gaps".
4. **RE-RUN GATES** + impacted suites; record results.
5. **REFRESH THIS `HANDOFF.md`** with evidence and nominate **C21** (≥12 concrete combos).

---

## NEXT FOCUS HEAVY CAMPAIGN (execute after C20 is evidenced)
**C21 (binding after C20):** BAB end-to-end stress/parity fidelity — probe (≥12 combos) consistency across API/CLI/script/reporting surfaces on: (a) `bab-example` vs `python -m strategies.betting_against_beta.cli` vs in-process `BABStrategy.run` parity on REAL/EXP and parameterized configs, (b) `backtest_report`/report outputs schema stability & finiteness vs CLI JSON, (c) repeated-run determinism under varied `--beta-window`/quantile/universe subsets, (d) max-turnover/position constraints interaction (if exposed) or documented no-op behavior, (e) mixed valid inputs (CSV with unusual but valid column/index forms covered by loader contract) through CLI end-to-end, (f) error-path parity: same invalid input via CLI and API yields clean equivalent contract errors (no Traceback). Produce evidence log `/home/runner/work/_temp/kilo-tmp/c21_bab_e2e_parity_stress_probe_evidence.log`, fix only proven gaps, add `tests/test_bab_cli_campaign21*.py` if needed, keep gates green, then refresh handoff with C22 plan.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding — execute heavy work with probe evidence.*
