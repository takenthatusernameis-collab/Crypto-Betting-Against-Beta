# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`.

**Refreshed:** 2026-11-13T22:06:11Z
**HEAD:** `3c585f2` (`chore(kilo): checkpoint agent session`, main)
**Working tree:** clean at refresh
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff docs. If live evidence conflicts with recorded numbers here, **live run wins** — re-measure, record the delta, and update this file.

---

## INITIAL TASK FOR NEXT SESSION (binding, timestamped 2026-11-13T22:06:11Z)

**Objective:** complete **R3 (Execution Realism)** end-to-end on current `HEAD` with hard evidence. Partial completion is not acceptable. Ship code/tests/evidence; do not stop at analysis.

### Mandatory start (every session, ~90s, idempotent — env bottleneck already solved by this block)
```bash
VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet "numpy==2.5.4" "pandas==3.1.1" "scipy==1.18.1" "pytest==9.2.0" "hypothesis==6.170.15" "coverage==7.17.3"

cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
```
- Do **not** claim missing deps (`pytest`/`numpy`/etc.) as blockers — run bootstrap above.
- Do **not** claim green status without fresh command output on current `HEAD`.

### Required work order (heavy; complete all)
1. **Baseline confirmation on current HEAD**
   - Run preflight and targeted R2 suites: `tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py`.
   - Record RC/pass/warn/time and live scale medians/ceilings. R2 must remain green.

2. **R3-A: add execution-realism regression tests (MISSING — must create)**
   - Create `tests/test_bab_execution_realism_r3.py`.
   - Reuse hostile-regime builders from `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`/`REGIME_BUILDERS`) — do not duplicate regime injectors.
   - Cover all 5 hostile regimes with R3-A cost model wired (`cost_model` / `prices` / `adv_usd` / `partial_fill` / `max_participation` as appropriate):
     - Backtest columns remain exactly `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`; all finite.
     - `cost_drag >= 0` and finite (and slippage/cost behavior consistent with model); dollar-neutral configs keep `max|Σw| <= 1e-9`.
     - **Costs-on vs costs-off per regime:** record drawdown, turnover, total `cost_drag` deltas; assert model-on total drag `>=` flat-only when impact/borrow effects are positive.
     - **Borrow asymmetry:** identical borrow cost but more short notional => strictly higher `cost_drag` than a long-biased/less-short book.
     - **Backward compatibility:** default/no-model path (`cost_model=None`, flat `transaction_costs`/`slippage` only) is byte-identical/behavior-identical to pre-R3 flat path.
     - **Reporting:** `report()`/`tear_sheet()` finite and `report_to_json()` strict JSON.
     - **Validation:** wrong-typed/invalid `cost_model` or invalid R3 config raises loudly (`BABConfigError`/`BABDataError` as contractually appropriate), never silently ignored.
   - If any behavior/contract is ambiguous, prove with current code + add regression assertions; fix defects with minimal targeted changes and tests.

3. **R3-B: rebalance-frequency sensitivity sweep (not implemented/measured — must deliver)**
   - Sweep `rebalance_freq ∈ {daily, weekly, monthly}` × 5 hostile regimes × `dollar_neutral` on/off with R3-A cost model enabled.
   - Assert: outputs finite, DN when configured, causality preserved (betas at `t` use data ≤ `t`), no non-finite cumulative, no `|Σw|` breach, locked columns preserved.
   - Record per-cell metrics: turnover, max drawdown, Sharpe (or available report metrics), total/mean `cost_drag` (and relevant drags). Assert turnover ordering/invariant expectations (weekly/monthly should not increase turnover vs daily in steady cases; use measured/invariant-based assertions, avoid arbitrary hard-coded targets beyond invariants/ceilings).
   - Daily cells must not regress vs R2 recorded behavior/ceilings/default-path performance expectations.

4. **Gate and durable evidence (completion bar)**
   - Run targeted R2 + R3 suites, then `bash scripts/bab_gate.sh` on final `HEAD`. Record RC, pass/skip counts, timing, key warnings if material.
   - Refresh this `HANDOFF.md` with concrete evidence: commands run, results, per-regime/per-cell R3-A/B summaries, any defects fixed, and remaining risks (if any). Keep `AGENT_HANDOFF.md` pointer-only and in sync.
   - **Commit nothing unless explicitly requested.**

**Definition of done:** R2 green on final HEAD, R3-A tests written and green, R3-B sweep implemented/measured and green, `bash scripts/bab_gate.sh` RC=0 recorded, `HANDOFF.md` refreshed with concrete evidence. If blocked on one sub-item, document exact error/evidence and continue with next unblocked R3 work — do not stop at analysis.

---

## Current state snapshot (verified at refresh unless noted)

- **HEAD / tree:** `3c585f2`, clean (`git status` clean at 2026-11-13T22:06:11Z).
- **R1:** closed/locked (per prior verified handoff; do not reopen without new reproducible evidence).
- **R2:** previously re-verified green on `5e715c5` (2026-11-13T21:27:51Z): preflight `RC=0`; `tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py` => 155 passed, 6 warnings, ~31.9s; scale medians 5000×200=164ms (≤800ms), 5000×500=384ms (≤2000ms). **Not re-run this refresh** — live run on current HEAD is required at session start.
- **R3-A code:** shipped in-tree (execution realism plumbing present): `strategies/betting_against_beta/config.py` (R3-A fields/coercion/validation incl. `cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation`), `strategies/betting_against_beta/strategy.py` (`_resolve_cost_model`, `run()` wiring), `strategies/betting_against_beta/backtest.py` (cost_model path, opt-in participation-aware slippage/partial-fill behavior), `strategies/betting_against_beta/costs.py` (`TransactionCostModel`, `compute_transaction_costs`).
- **R3-A tests:** **MISSING** — `tests/test_bab_execution_realism_r3.py` does not exist.
- **R3-B:** not implemented/measured.
- **Full gate:** prior historical baseline 5373 passed / 35 skipped / RC=0 (~657s, earlier HEAD); **must be re-run and recorded on final R3 HEAD**.

---

## Key anchors / contracts (verified; do not guess)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` where `df` is simple returns (DatetimeIndex/rows by date, columns assets, benchmark column present). `res` fields: `betas`, `signals`, `weights`, `backtest`.
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]` (do not change without updating all dependents and recording delta).
- **Dollar neutrality:** when configured, enforce/check `max|weights.sum(axis=1)| <= 1e-9` (project convention).
- **R3-A config/strategy knobs:** `cost_model` (dict coerced to `TransactionCostModel` or instance), `prices`, `adv_usd`, `partial_fill` (bool), `max_participation` in `(0,1]`; invalid/wrong-typed config must raise loudly.
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(linear_fee,bid_ask_bps,impact_coefficient,participation_cap,borrow_bps_per_year,fixed_fee_per_trade,trading_days_per_year,adv_usd)`; `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd=...)` returns per-period non-negative finite series.
- **Default path invariant:** no-model/flat path must remain behaviorally/byte-identically consistent with pre-R3 (do not regress performance/semantics).
- **Hostile regime builders for reuse:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, helpers/constants like `BETA_WINDOW=90`, `MIN_OBS=60`, `DN_TOL=1e-9`).
- **Canonical commands:** preflight `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; gate `bash scripts/bab_gate.sh` (from repo root, with deps available).

---

## Performance guardrails (do not regress; live-run wins)

- Prior measured medians (5e715c5/258f660 context): 5000×200 ~161-164ms (ceiling 800ms), 5000×500 ~384-392ms (ceiling 2000ms), 5000×40 ~35ms informational.
- Scale guards assert ceilings, not exact medians. Keep default/no-model path model-free/lightweight; pay cost-model overhead only when configured.

---

## Locks / prohibitions (binding)

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts as applicable); use `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting shipped regression suites/guards (incl. `tests/test_beta_neutrality_performance.py`, historical `batch*`/`campaign*` regressions, R2 suites) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure (historical only).
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **No** probe-count/churn campaigns or commentary-only progress. Commit nothing unless explicitly requested.

---

## After R3 ships (next candidates)

1. **R4 — Live-readiness:** dry-run/portfolio-risk report, drawdown-limit kill switch, reproducible paper-trading replay harness against real fixtures.
2. Revisit locked `data_loader.py` broad-`except` sweep only with concrete reproducible defect + regression test.

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence on every material run.**
