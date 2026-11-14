# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`. **Priority basis:** the repo *is* the BAB strategy engine, so correctness + live-readiness of the strategy outranks tooling/coverage-chasing.

**Refreshed:** 2026-11-14T00:51:57Z (UTC)
**HEAD:** `40e5c34` (main). **Working tree:** clean at refresh. Baseline gate/preflight evidence below was captured on `45563ba` and no product/test code changed in the subsequent checkpoint commits through `40e5c34`; re-verify on current `HEAD` before claiming green.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff docs. If live evidence conflicts with a recorded number here, **live run wins** — re-measure, record the delta, update this file.

---

## LIVE VERIFICATION EVIDENCE (measured this session on HEAD `45563ba`)

| Check | Command | Result |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | **RC=0** — 155 passed, 6 warnings, 33.58s |
| Live scale (median/9 warm) | same preflight | 5000×200 = **163 ms** (≤800 ms), 5000×500 = **393 ms** (≤2000 ms) |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | **RC=0** — **5590 passed / 35 skipped / 416.96s / coverage 96%** |

- All numbers above were reproduced on `45563ba`; they supersede the prior `ee1d42c`/`4dfbc17` recordings (same suite counts, fresh wall-clock).
- `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` exists and is populated (Python 3.12.3; numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis 6.170.15).

---

## STATUS

- **R1:** closed/locked — do not reopen without new reproducible evidence.
- **R2:** closed/locked — stress regimes + horizon + scale guards green (155 passed; scale within ceilings).
- **R3:** closed/locked — `tests/test_bab_execution_realism_r3.py` (R3-A cost realism + R3-B rebalance sweep) present and green; full gate RC=0. Do not reopen.
- **R4 (ACTIVE CAMPAIGN):** live-readiness — R4-A dry-run/portfolio-risk report, R4-B drawdown-limit kill switch, R4-C deterministic paper-trading replay harness. **Not started.** Only a `cli.py --dry-run` config/data-validation skeleton exists (`cli.py:329`); R4-B and R4-C are unimplemented.

---

## INITIAL TASK FOR NEXT SESSION (binding, timestamped 2026-11-14T00:51:57Z, HEAD 40e5c34)

**Objective:** Ship **R4 (Live-Readiness)** end-to-end on current `HEAD` (`40e5c34`) with hard evidence. **All three components (R4-A, R4-B, R4-C) must be implemented with green regression tests and wired into the gate/behavioral contracts.** Partial completion or analysis-only is a failed session. Do not stop at "next steps"; land code + tests + measured evidence.

**Bottleneck check (recorded 2026-11-14T00:51:57Z, HEAD `40e5c34`):** `scripts/bab_r4_preflight.py` exists as the mechanical campaign gate and must be treated as authoritative. R4 is **not shipped** until it returns **RC=0** on current HEAD. Expected pending items until implemented: R4-A (`dry_run`/portfolio-risk-report capability + `tests/test_bab_dryrun_risk_report_r4.py`), R4-B (`max_drawdown_limit`/`kill_switch` + `tests/test_bab_drawdown_kill_switch_r4.py`), R4-C (`ReplayHarness`/replay harness + `tests/test_bab_replay_harness_r4.py`). This is the sole active blocker — no other campaign is open; remove it by implementing and verifying all three. Re-run and record live preflight/gate output on `40e5c34` before claiming status.

### R4-A — Dry-run / portfolio-risk report
- **Deliverable:** `BABStrategy.dry_run(returns_df=None) -> dict` (programmatic) plus `--dry-run` CLI output that prints the resolved config, tradable universe, beta window/quantiles, and a **portfolio-risk summary**: gross exposure, net exposure, gross leverage, max single-position weight, estimated turnover/cost drag, data-health (rows, columns, NaN counts, benchmark presence). No backtest/trades executed.
- **Contract:** result is a plain dict of **finite** floats/ints/bools/str/lists; strict-JSON serializable via `json.dumps(..., allow_nan=False)`; `--output` must **not** write in dry-run. Invalid inputs raise `BABDataError`/`BABConfigError` loudly (no silent fallback).
- **Tests:** `tests/test_bab_dryrun_risk_report_r4.py` — valid fixture → required keys present and finite; JSON round-trip strict; no trade execution (assert weights/backtest untouched); invalid config/data raises; CLI `--dry-run` returns 0 on valid and non-zero on invalid; `--output` not created.
- **Reuse:** `tests/fixtures/real_market_prices.csv` (400 rows, BTC + 8 assets + all-NaN `DEL`) and `load_prices`/`load_returns`.

### R4-B — Drawdown-limit kill switch
- **Deliverable:** new `max_drawdown_limit: Optional[float]` on `BABConfig` (validated to `(0,1]` or `None`), plus a `strategies/betting_against_beta/risk.py` implementing the kill switch: monitor running max drawdown of the strategy cumulative path; on first breach, **halt/flatten** the book (weights → 0 from the breach date onward) and emit a `kill_switch` event `{triggered: bool, date, observed_drawdown, limit}`.
- **Contract:** when `max_drawdown_limit is None`, behavior is **byte-identical** to pre-R4 (default path invariant). When breached, weights after the trigger are zero and the event is surfaced in `report()` (new key `kill_switch`, JSON-safe).
- **Tests:** `tests/test_bab_drawdown_kill_switch_r4.py` — breaching fixture triggers exactly once and flattens; non-breaching fixture does not trigger; `None` limit is a no-op and matches baseline; event is finite/JSON-safe; invalid limit raises `BABConfigError`.

### R4-C — Reproducible paper-trading replay harness
- **Deliverable:** `strategies/betting_against_beta/replay.py` — `ReplayHarness` that replays a `BABResult`'s weights against a price/returns fixture **deterministically**, recording per-period orders, fills, and costs, and emitting a reproducible artifact (stable schema + SHA-256 checksum).
- **Contract:** two runs on identical inputs produce **byte-identical** artifacts (same checksum); artifact is strict-JSON-safe; includes orders/fills/costs/equity; no wall-clock or random nondeterminism.
- **Tests:** `tests/test_bab_replay_harness_r4.py` — determinism (two runs equal), schema keys present, finite, checksum stable, records orders/fills/costs; works against `tests/fixtures/real_market_prices.csv`.

### Required work order (complete all; heavy)
1. **Baseline on current HEAD:** re-run preflight + R2 suites + R3 suite; record RC/pass/time. Any regression → fix first.
2. **Implement R4-A, R4-B, R4-C** with the tests above. Wire R4-B into `BABStrategy.run`/`report` and R4-A into CLI without regressing the default/no-cost path.
3. **Gate + durable evidence:** run `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`; record RC, pass/skip, timing, coverage. Then refresh this `HANDOFF.md` with concrete evidence (commands, results, per-component summaries, defects fixed, remaining risks) and keep `AGENT_HANDOFF.md` pointer-only/in-sync.
4. **Commit nothing unless explicitly requested.**

**Definition of done:** R2/R3 green on final HEAD; R4-A/B/C implemented with green tests; `bash scripts/bab_gate.sh` RC=0 recorded; `HANDOFF.md` refreshed with evidence. If blocked on one sub-item, document the exact error/evidence and continue with the next unblocked R4 item — never stop at analysis.

---

## MANDATORY START (every session, ~90s, idempotent)

```bash
VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet "numpy==2.5.4" "pandas==3.1.1" "scipy==1.18.1" "pytest==9.2.0" "hypothesis==6.170.15" "coverage==7.17.3" "pytest-cov==7.1.0"

cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py; echo "R4_PREFLIGHT_RC=$?"
```
- `bab_gate.sh` invokes bare `python3`; **prefix `PATH="$VENV/bin:$PATH"`** so the gate uses the venv interpreter (otherwise system `python3` may lack numpy/pandas/coverage).
- Do **not** claim missing deps (`pytest`/`numpy`/etc.) as blockers — run the bootstrap above.
- Do **not** claim green status without fresh command output on the current `HEAD`.
- `scripts/bab_r4_preflight.py` is the mechanical campaign gate: it fails (non-zero) with an itemized TODO until R4-A/B/C artifacts + tests exist and pass. Treat its output as the authoritative "what's left" list.

---

## BOTTLENECKS REMOVED / VERIFIED (current refresh 2026-11-14T00:51:57Z)

1. **Handoff HEAD/timestamp drift** — refreshed to current `HEAD` `40e5c34` and 2026-11-14T00:51:57Z so next session starts from true repo state.
2. **Single durable handoff enforced** — `HANDOFF.md` remains sole source of truth; `AGENT_HANDOFF.md` kept pointer-only/in-sync.
3. **Mechanical R4 gate present** — `scripts/bab_r4_preflight.py` provides an itemized, failing-by-default gate for R4-A/B/C; next session must run it on `HEAD` and record RC/evidence (no hand-waving).
4. **Execution blockers pre-empted** — mandatory idempotent venv bootstrap and `PATH="$VENV/bin:$PATH"` gate invocation documented; missing deps must not be claimed as blockers.
5. **Historical CI noise quarantined** — `research_state/workflow_run_diagnostics.jsonl` remains historical-only and must not justify inaction; live run on current `HEAD` wins.

---

## KEY ANCHORS / CONTRACTS (verified; do not guess)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` where `df` is simple returns (DatetimeIndex, columns assets, benchmark column present). `res` fields: `betas`, `signals`, `weights`, `backtest`, `config`, `returns`.
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]` (do not change without updating all dependents and recording delta).
- **Dollar neutrality:** when configured, `max|weights.sum(axis=1)| <= 1e-9` (project convention `DN_TOL`).
- **Config validation:** `BABConfig` is effectively frozen after `__post_init__`; unknown/wrong types raise `BABConfigError` (config.py:18). Cost knobs: `cost_model` (dict coerced to `TransactionCostModel` or instance), `prices`, `adv_usd`, `partial_fill` (bool), `max_participation` in `(0,1]`.
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(linear_fee,bid_ask_bps,impact_coefficient,participation_cap,borrow_bps_per_year,fixed_fee_per_trade,trading_days_per_year,adv_usd)`; `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd=...)`.
- **Default-path invariant:** no-model/flat path must remain behaviorally/byte-identically consistent with pre-R4 (do not regress performance/semantics).
- **Hostile regime builders for reuse:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, `BETA_WINDOW`, `MIN_OBS`, `DN_TOL`, `BACKTEST_COLUMNS`).
- **Canonical commands:** preflight `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; R4 preflight `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py`; gate `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` (from repo root).

---

## PERFORMANCE GUARDRAILS (do not regress; live-run wins)

- Current medians (this session, `45563ba`): 5000×200 ~163 ms (ceiling 800 ms), 5000×500 ~393 ms (ceiling 2000 ms). Scale guards assert ceilings, not exact medians.
- Keep default/no-model path model-free/lightweight; pay cost-model overhead only when configured.

---

## LOCKS / PROHIBITIONS (binding)

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts as applicable); use `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting shipped regression suites/guards (incl. `tests/test_beta_neutrality_performance.py`, historical `batch*`/`campaign*` regressions, R2/R3 suites) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure (historical only).
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **No** probe-count/churn campaigns or commentary-only progress. **Commit nothing unless explicitly requested.**

---

## AFTER R4 SHIPS (next candidates)

1. **R5 — Execution integration:** live-order adapter stubs, slippage/impact calibration against real fill data, cost-model backtest vs executed-fills reconciliation.
2. Revisit locked `data_loader.py` broad-`except` sweep only with concrete reproducible defect + regression test.

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence on every material run.**