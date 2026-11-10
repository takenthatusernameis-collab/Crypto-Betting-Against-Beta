# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T21:21:21Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `ef281ac` (`chore(kilo): checkpoint agent session`, `main` at read time; treat current HEAD as base and record exact HEAD when you run).
**Working tree:** clean at session start (no uncommitted changes observed). No competing handoff files; this file is the single durable handoff.

**Environment (observed 2026-11-10):** `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 (pytest 9.2.0 present). Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).

**Bottlenecks/status:** No in-repo blocked sessions identified. Prior workflow diagnostics (`research_state/workflow_run_diagnostics.jsonl`) show historical agent-loop tool/timeout/import noise in earlier runs but all captured runs concluded success; treat as historical context, not a current blocker. **C19 is unexecuted in this workspace:** no `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log`, no `tests/test_bab_cli_campaign19*.py`. Step 0 gates were **not re-run in this handoff-only session** — next agent MUST run and record them before any edit.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, and JSON validity/finiteness with `allow_nan=False` where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0** (investigate regressions before production edits)
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4708 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

Do not revert prior fixes without cause.

### 2) Campaigns 6–18 (historical closure — no churn)
C6–C18 reported closed in prior sessions (benchmark/NaN/universe/parity/cost/dry-run/reporting/pipeline/schema-metrics/strategy-core/metrics-attribution-sizing-regime/beta-neutral fidelity per prior handoff context). Prior probe logs may not be present locally; rely on fresh Step 0 gates and new evidence. Do not churn without a new, statable, reproducible failure.

### 3) Execute C19 — config-validation edges, cost/slippage monotonic drag, universe/rebalance/shorting/sizing robustness (≥12 combos, HEAVY)
Goal: verify **BAB configuration robustness and cost/slippage/position-sizing fidelity** — clean `BABConfigError` (no Traceback) on invalid configs, transaction-cost monotonic drag, slippage accounting, explicit-universe no-overlap rejection, rebalance freq (`daily`/`weekly`/`monthly`) behavior, shorting constraints, `max_position_size` bounding, and CLI `--output` strict-JSON/schema/determinism on real & defective data.

Fixtures: `REAL`=`tests/fixtures/real_market_prices.csv`, `EXP`=`tests/fixtures/real_market_prices_expanded.csv`, plus defective fixtures as relevant (`degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).
Evidence log (mandatory): `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log` (record cmd, rc, stdout, stderr, JSON validity/finiteness `allow_nan=False`, key sets, determinism, neutrality/shorting/bounds checks where applicable).

**Required probe matrix (minimum 12 combos; do more if anomalies appear):**
1. `BABConfig(beta_window=0)` → `BABConfigError` clean, no Traceback.
2. `BABConfig(long_quantile=0.0)` and `BABConfig(long_quantile=1.0)` → `BABConfigError` clean (must be in (0,1)).
3. `BABConfig(short_quantile=0.0)` → `BABConfigError` clean.
4. `BABConfig(transaction_costs=-0.001)` → `BABConfigError` clean.
5. `BABConfig(vol_thresholds=[...], vol_percentiles=[...])` both set → `BABConfigError` clean ("set only one").
6. Cost monotonic drag: REAL default × `transaction_costs` ∈ {0.0, 0.0005, 0.001, 0.005} → `final_cumulative` non-increasing as cost rises; metrics finite, strict JSON OK.
7. Slippage: REAL default × `slippage` ∈ {0.0, 0.001} → `slippage_drag` > 0 when slippage>0, finite, net = gross − cost − slippage (as contract states).
8. Explicit universe override with no data overlap (e.g. `["ZZZ","YYY"]` on REAL) → `BABConfigError` clean.
9. Rebalance freq `daily` vs `weekly` vs `monthly` on REAL default → all run, metrics finite, weights dollar-neutral; per-freq determinism across two identical runs.
10. Shorting constraints dict on REAL default → runs, weights finite, dollar-neutral, shorting present as expected.
11. `max_position_size=0.2` on REAL default → runs, `|weights|` bounded within tolerance, finite.
12. CLI: `python -m strategies.betting_against_beta.cli --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output <tmp>/out.json` → rc=0, valid strict JSON, keys {final_cumulative, periods, benchmark, universe}, periods=398, stderr empty.
13. CLI: `--output` to nonexistent nested dir → rc=0, parents created, valid JSON written.
14. CLI: `--dry-run --output <existing-dir>` → rc=1 clean "is a directory" error, no Traceback.
15. CLI determinism: two identical REAL `--from-prices --output` runs → byte-identical stdout/JSON.

(Items 12–15 included as required CLI coverage; total ≥15 — do not stop early if behavior is ambiguous.)

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics, unexpected non-finite, incorrect rc/error contract, Traceback on user paths).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py` if evidence proves a gap. **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`.
- Add regressions in `tests/test_bab_cli_campaign19*.py` for every proven fix. If none, record explicit "no proven gaps" with evidence refs in the C19 log and this HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, Step 0 & validation counts/rc, C19 evidence (log path, combo summary, determinism/neutrality/fin/parity notes), touched modules, and the **next binding heavy campaign (C20)** with a concrete ≥12-combo probe plan. No generic "continue" handoff.

---

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4708 passed, 35 skipped, rc=0** (hard floor)
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
1. **RUN STEP 0 GATES** → record exact counts/rc.
2. **EXECUTE C19** probe matrix (≥12 combos) → write evidence log.
3. **TRIAGE/FIX** proven gaps only (smallest non-locked change + `tests/test_bab_cli_campaign19*.py`) or record "no proven gaps".
4. **RE-RUN GATES** + impacted suites; record results.
5. **REFRESH THIS `HANDOFF.md`** with evidence and nominate **C20** (≥12 concrete combos).

---

## NEXT FOCUS HEAVY CAMPAIGN (execute after C19 is evidenced)
**C20 (binding after C19):** BAB metrics/reporting/CLI fidelity under stressed-but-valid and edge-valid regimes — probe (≥12 combos) `calculate_bab_metrics`/backtest reporting consistency on: (a) very short histories near `beta_window`/`min_periods`, (b) sparse but valid universes (few assets), (c) high-NaN-but-recoverable rows/columns, (d) zero/near-zero return regimes, (e) benchmark-equals-asset edge cases, (f) extreme but valid cost/slippage combos, (g) `--dry-run` vs run config parity on same inputs, (h) CLI JSON key stability/determinism across repeated runs and output paths, (i) `bab-example` console script parity with module CLI on REAL/EXP. Produce evidence log `/home/runner/work/_temp/kilo-tmp/c20_bab_metrics_reporting_stress_fidelity_probe_evidence.log`, fix only proven gaps, add `tests/test_bab_cli_campaign20*.py` if needed, keep gates green, then refresh handoff with C21 plan.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding — execute heavy work with probe evidence.*
