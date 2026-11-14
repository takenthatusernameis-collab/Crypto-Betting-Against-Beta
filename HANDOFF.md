# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`.

**Refreshed:** 2026-11-14T00:36:21Z
**HEAD:** `4dfbc17` (main), working tree CLEAN — the previously recorded uncommitted `TestFreezeFallback` fix (`cfg.cost_model = None`) is now committed in `4dfbc17` (checkpoint commit at 00:36:13Z; commit message `chore(kilo): checkpoint agent session`, which also refreshed `AGENT_HANDOFF.md`/`HANDOFF.md`). **Commit nothing unless explicitly requested.**
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff docs. If live evidence conflicts with recorded numbers here, **live run wins** — re-measure, record the delta, and update this file.

---

## R3 COMPLETION EVIDENCE (completion bar met on final HEAD `ee1d42c`)

- **R2 green on current HEAD:** preflight `RC=0`; `tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py` => **155 passed, 6 warnings, 33.59s**; scale medians 5000×200=151ms (≤800ms OK), 5000×500=383ms (≤2000ms OK). *Verified 2026-11-14T23:46:03Z*
- **R3-A (execution-realism regression tests):** `tests/test_bab_execution_realism_r3.py` EXISTS and is GREEN — **62 passed, 1.06s**. Covers all 5 hostile regimes × dn on/off × cost on/off; locked columns + finite; `cost_drag>=0`; DN `max|Σw|<=1e-9`; costs-on vs flat deltas; borrow asymmetry (more short notional => strictly higher cost); byte-identical no-model/flat default path; finite `report()`/`tear_sheet()` + strict `report_to_json()`; loud `BABConfigError`/`BABDataError` on invalid `cost_model`/`partial_fill`/`max_participation`; causal betas (no lookahead under cost model). *Verified 2026-11-14T23:46:03Z*
- **R3-B (rebalance-frequency sweep):** daily/weekly/monthly × 5 hostile regimes × dn on/off with cost model; invariants hold (weekly/monthly rebalance periods ≤ daily; no daily regression vs R2; finite cumulative, locked columns, DN). Green (within the 62 above).
- **Bottleneck removed:** `tests/test_bab_strategy_campaign_gaps.py::TestFreezeFallback::test_freeze_fallback_path` previously raised `BABDataError: cost_model must be a TransactionCostModel, dict, or None, got MagicMock` because `MagicMock(spec=BABConfig).cost_model` returns a MagicMock child that tripped R3 loud validation (`strategy.py:_resolve_cost_model`, strategy.py:238). Minimal scope-correction fix: added `cfg.cost_model = None` (cost_model is a real BABConfig field, so this is allowed on the spec'd mock). **R3 validation untouched — not weakened.** Gate now green.
- **Full gate:** `bash scripts/bab_gate.sh` **RC=0** — **5590 passed / 35 skipped / ~419s / coverage 96%** (all of `strategies/betting_against_beta`). *Verified 2026-11-14T23:46:03Z*

**Definition of done for R3:** R2 green on final HEAD, R3-A tests written and green, R3-B sweep implemented/measured and green, `bash scripts/bab_gate.sh` RC=0 recorded, `HANDOFF.md` refreshed with concrete evidence. **ALL MET.** R3 is closed. Do not reopen without new reproducible evidence.

---

## INITIAL TASK FOR NEXT SESSION (binding, timestamped 2026-11-14T00:36:21Z)

**Objective:** R3 is closed. Begin **R4 (Live-Readiness)** end-to-end on current `HEAD` (`4dfbc17`) with hard evidence. Partial completion is not acceptable. Ship code/tests/evidence; do not stop at analysis.

R4 candidates (from prior handoff, now the active campaign):
1. **R4-A — Dry-run / portfolio-risk report:** CLI dry-run mode (`--dry-run` skeleton present in `cli.py:329`) that validates inputs and prints resolved config + portfolio-risk summary without executing trades; strict, finite, JSON-serializable output.
2. **R4-B — Drawdown-limit kill switch:** configurable drawdown limit that halts/flattens the book when breached; assert kill-switch triggers on a breaching fixture and does not trigger on a non-breaching one. **Not yet implemented.**
3. **R4-C — Reproducible paper-trading replay harness:** replay against real/fixture market data deterministically; record orders/fills/costs; output reproducible artifacts. **Not yet implemented.**

### Bottlenecks removed (this refresh)
- Env/bootstrap bottleneck solved by the mandatory start block below (idempotent venv at `/home/runner/work/_temp/kilo-tmp/bab-venv`).
- R3 `TestFreezeFallback` bottleneck closed: `cfg.cost_model = None` committed in `4dfbc17`; R3 validation untouched, gate green. Do not reopen.

### Mandatory start (every session, ~90s, idempotent)
```bash
VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet "numpy==2.5.4" "pandas==3.1.1" "scipy==1.18.1" "pytest==9.2.0" "hypothesis==6.170.15" "coverage==7.17.3" "pytest-cov==7.1.0"

cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
```
- Do **not** claim missing deps (`pytest`/`numpy`/etc.) as blockers — run bootstrap above.
- Do **not** claim green status without fresh command output on current `HEAD` (`4dfbc17`).

### Required work order (heavy; complete all)
1. **Baseline confirmation on current HEAD**
   - Run preflight and targeted R2 suites: `tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py`.
   - Record RC/pass/warn/time and live scale medians/ceilings. R2 must remain green (no regression from R3).
2. **R4-A/B/C implementation** (all three): dry-run/risk report, drawdown-limit kill switch, deterministic paper-trading replay harness against real fixtures, each with regression tests and finite/strict-JSON reporting.
3. **Gate and durable evidence (completion bar)**
   - Run targeted R2 + R4 suites, then `bash scripts/bab_gate.sh` on final `HEAD`. Record RC, pass/skip counts, timing, key warnings if material.
   - Refresh this `HANDOFF.md` with concrete evidence: commands run, results, per-R4-component summaries, any defects fixed, and remaining risks. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
   - **Commit nothing unless explicitly requested.**

**Definition of done:** R2 green on final HEAD, R4-A/B/C implemented with green tests, `bash scripts/bab_gate.sh` RC=0 recorded, `HANDOFF.md` refreshed with concrete evidence. If blocked on one sub-item, document exact error/evidence and continue with next unblocked R4 work — do not stop at analysis.

---

## Current state snapshot (verified at refresh unless noted)

- **HEAD / tree:** `4dfbc17`; tree CLEAN (the `TestFreezeFallback` fix is committed). Preflight + R2 + R3-A + R3-B + full gate were last verified green on `ee1d42c`; HEAD advanced only via checkpoint commits (handoff docs + test fix), no strategy-code change, so R3 evidence carries forward but must be re-confirmed with a fresh gate run on `4dfbc17`.
- **R1:** closed/locked (per prior verified handoff; do not reopen without new reproducible evidence).
- **R2:** closed/locked — green on `ee1d42c` (155 passed; scale within ceilings). Re-confirm on `4dfbc17`.
- **R3:** closed/locked — see R3 COMPLETION EVIDENCE above. `tests/test_bab_execution_realism_r3.py` present and green; `bash scripts/bab_gate.sh` RC=0 (verified on `ee1d42c`). Re-confirm on `4dfbc17`.
- **R4:** not started — this is the active campaign (see INITIAL TASK above). `cli.py --dry-run` skeleton present; kill switch (R4-B) and replay harness (R4-C) not yet implemented.

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

- Prior measured medians (this session, ee1d42c): 5000×200 ~151ms (ceiling 800ms), 5000×500 ~383ms (ceiling 2000ms). Scale guards assert ceilings, not exact medians.
- Keep default/no-model path model-free/lightweight; pay cost-model overhead only when configured.

---

## Locks / prohibitions (binding)

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts as applicable); use `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting shipped regression suites/guards (incl. `tests/test_beta_neutrality_performance.py`, historical `batch*`/`campaign*` regressions, R2 suites, R3 suite) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure (historical only).
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **No** probe-count/churn campaigns or commentary-only progress. Commit nothing unless explicitly requested.

---

## After R4 ships (next candidates)

1. **R5 — Execution integration:** live-order adapter stubs, slippage/impact calibration against real fill data, cost-model backtest vs executed-fills reconciliation.
2. Revisit locked `data_loader.py` broad-`except` sweep only with concrete reproducible defect + regression test.

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence on every material run.**