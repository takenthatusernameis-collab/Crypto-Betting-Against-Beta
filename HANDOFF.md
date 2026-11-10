# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T22:40:00Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `e4b6e4ca91ec06959ba20da473dfdf74aca9d5e3` (`chore(kilo): checkpoint agent session`, recorded 2026-11-10T22:2xZ). Treat current HEAD as base and record exact HEAD when you run.
**Working tree (this session end):** modified/new only by intended C19 work — added `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py`, wrote probe evidence `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log`, updated this `HANDOFF.md`. No competing handoff files; this file is the single durable handoff.

**Environment (observed 2026-11-10T22:2xZ):** `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 (deps ok). Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).

**Bottlenecks/status:** No in-repo blocked sessions identified. Prior workflow diagnostics (`research_state/workflow_run_diagnostics.jsonl`) are historical (captured runs success) — not a current blocker. **C19 executed and evidenced this session** (see below). No production-code fixes required (no proven gaps). C20 is the next binding heavy campaign.

**Step 0 gate status (this session, 2026-11-10T22:2xZ, `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, all completed and recorded):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 ✓
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **164 passed in 206.27s (0:03:26), rc=0** ✓
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings in 16.33s, rc=0** ✓
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **4764 passed, 35 skipped, 231 warnings in 511.25s (0:08:31), rc=0** ✓ (exceeds hard floor ≥4708)
- New regressions: `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` → **18 passed in 7.26s, rc=0** ✓

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, and JSON validity/finiteness with `allow_nan=False` where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4764 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

Do not revert prior fixes without cause.

### 2) Campaigns 6–19 (historical closure — no churn)
C6–C19 reported closed with evidence. C19 evidence: `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log` (HEAD `e4b6e4c`, 15 combos probed). Summary:
- (1) `BABConfig(beta_window=0)` → `BABConfigError` clean (no Traceback). PASS
- (2) `long_quantile` 0.0/1.0 → `BABConfigError` clean. PASS
- (3) `short_quantile=0.0` → `BABConfigError` clean. PASS
- (4) `transaction_costs=-0.001` → `BABConfigError` clean. PASS
- (5) `vol_thresholds`+`vol_percentiles` both set → `BABConfigError` clean. PASS
- (6) REAL × costs {0,0.0005,0.001,0.005} → `final_cumulative` [0.3397354969330525, 0.3263966105648454, 0.31357452508222267, 0.22738172195446477] monotonic non-increasing, all finite, periods=398. PASS
- (7) REAL × slippage {0,0.001} → `slippage_drag_total` 0.0→0.08 (>0), all finite, net cum ≤ no-slippage. PASS
- (8) Explicit universe no-overlap `['ZZZ','YYY']` on REAL → `BABConfigError` clean user-path (`configured universe ... has no overlap...`). NOTE: exception is clean; probe log records `traceback_in_exc=True` inside captured traceback string but no user-visible Traceback emitted. PASS (clean contract)
- (9) `rebalance_freq` daily/weekly/monthly on REAL ×2 runs → all finite, dollar-neutral (row-sum abs max 0.0), deterministic per freq (fc daily 0.3397354969330525, weekly 0.38215059713934335, monthly 0.5930166842166542). PASS
- (10) Shorting constraints: valid `{'max_short_weight':0.5,'max_short_notional_per_asset':1.0}` runs finite, neutral, shorts present (fc 0.3397354969330525). Invalid shorthand keys (`allow_shorting`, `max_gross_leverage`) and sign-mismatched `max_short_weight:-0.5` rejected cleanly as `BABConfigError` by contract (validated). PASS (no proven gap)
- (11) `max_position_size=0.5` on REAL feasible → finite, bounded (maxabs 0.5). `max_position_size=0.3` rejected with `BABDataError: Position size exceeds max_position_size` (clean, by contract; portfolio cannot satisfy). PASS (no proven gap)
- (12) CLI `--data REAL --from-prices --benchmark BTC --output <tmp>` → rc=0, stderr empty, no Traceback, strict JSON valid, keys {benchmark, final_cumulative, periods, universe}, periods=398, benchmark BTC. PASS
- (13) CLI `--output` to nonexistent nested dir → rc=0, parents created, valid strict JSON. PASS
- (14) CLI `--dry-run --output <existing-dir>` → rc=1, clean `Error validating output path: --output path is a directory...`, no Traceback. PASS
- (15) CLI determinism: two identical REAL runs → stdout_equal True, file_equal True (193 bytes), rc 0/0. PASS

**C19 conclusion:** explicit **"no proven gaps"** — all probes matched contracts (clean errors, finite/deterministic/neutral where required, monotonic drag, strict JSON). Regressions added in `tests/test_bab_cli_campaign19_config_cost_sizing_fidelity.py` (18 tests) to lock behavior. Do not churn C6–C19 without a new, statable, reproducible failure.

### 3) Execute C20 — metrics/reporting/CLI fidelity under stressed-but-valid and edge-valid regimes (≥12 combos, HEAVY)
Goal: verify **BAB metrics/reporting/CLI fidelity** under stressed-but-valid regimes — no silent corruption, strict JSON/finite outputs where contract requires, deterministic/stable keys, and correct clean errors on invalid-but-user-facing edges.

Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c20_bab_metrics_reporting_stress_fidelity_probe_evidence.log` (record cmd, rc, stdout, stderr, JSON validity/finiteness `allow_nan=False`, key sets, determinism, neutrality/shorting/bounds checks where applicable).

**Required probe matrix (minimum 12 combos; do more if anomalies appear):**
1. Very short history near limits: slice REAL to minimal rows around `beta_window`/`min_periods`/`min_rows` behavior (e.g. small window like 30 with enough rows, and boundary-ish short slices) → rc/behavior per contract, no Traceback, metrics finite or clean BABDataError as specified.
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
- full BAB excl `data_loader`/`controller` **≥4764 passed, 35 skipped, rc=0** (hard floor, raised by C19 regressions)
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
