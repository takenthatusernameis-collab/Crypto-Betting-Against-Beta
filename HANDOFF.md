# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`. **Priority basis (repo name):** the repo *is* the BAB strategy engine, so strategy correctness, realism, and live/execution-readiness outrank tooling, diagnostics archaeology, and coverage-chasing.

**Refreshed:** 2026-11-14T04:18:31Z (UTC)
**HEAD at refresh:** `479ee9f` (main, `git rev-parse --short HEAD` at refresh). **Live run wins** — if any recorded number conflicts with live output on current `HEAD`, re-measure, record the delta, and update this file immediately.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff/session docs.

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T04:18:31Z UTC) — BINDING

**Do not idle on analysis, commentary, archaeology, or probe-churn.** R1–R4 are shipped on prior evidence only; **treat baseline as unverified on current `HEAD` until you re-run it**. Your job is to drive **R5 Execution Integration** to tested, evidence-backed completion while preserving default-path behavior.

**Immediate sequence (execute now, in order):**
1. **Bootstrap env (idempotent, never a blocker):**
   ```bash
   VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
   if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
   "$VENV/bin/python" -m pip install --quiet --upgrade pip
   "$VENV/bin/python" -m pip install --quiet "numpy==2.5.4" "pandas==3.1.1" "scipy==1.18.1" "pytest==9.2.0" "hypothesis==6.170.15" "coverage==7.17.3" "pytest-cov==7.1.0"
   cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
   ```
2. **Re-verify baseline on current HEAD (required before R5 work):**
   ```bash
   PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
   PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py; echo "R4_PREFLIGHT_RC=$?"
   ```
   If either fails: **stop R5, fix the regression first** (smallest fix + targeted regression test), record evidence, then re-run. If both green, run full gate when appropriate: `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh; echo "GATE_RC=$?"` (gate needs venv on `PATH`).
3. **Implement R5 in order (heavy work, tests per step, additive/default-path-safe):**
   - **R5-A Live-order adapter contract (stub, no network in tests):** add `strategies/betting_against_beta/execution.py` (or equivalent) with a clean adapter interface for order-intent generation/submission abstraction (paper + injectable/mock exchange). Deterministic, strict-JSON-safe intents/serialization where applicable. **`BABStrategy.run()` default behavior unchanged when no adapter configured.**
   - **R5-B Slippage/impact calibration + reconciliation hook:** compare modeled costs (`costs.py`/cost-model path) vs supplied executed-fill data; emit per-period and aggregate deltas as strict-JSON-safe artifact/report. **No fake "live" claims** — use deterministic fixtures and prove reconciliation math in tests.
   - **R5-C Executed-fills backtest reconciliation:** given a fill/execution log, produce realized PnL/cost/equity series and compare to model backtest for the same weights/prices window; surface mismatches explicitly. Integrate via additive API/CLI/report (default path untouched).
4. **Proof & closeout:** add focused `tests/test_bab_execution_integration_r5*.py` covering adapter contract, reconciliation math, determinism/JSON-safety, and default-path invariance. Run targeted tests → R2/R4 preflights → full gate. **Update this HANDOFF with exact commands, RC, pass/skip counts, durations, and any contract/perf deltas.**

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts); no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

**Bottleneck policy:** environment is not a blocker (bootstrap venv + prefix `PATH`). Historical diagnostics are not a blocker (live run wins). If no real blocker exists, proceed with implementation; do not stop at analysis.

---

## VERIFIED EVIDENCE SNAPSHOT (stale unless re-verified on current HEAD)

Captured on HEAD `93b0c10` (2026-11-14T04:03:05Z). **Not re-verified on `479ee9f` in this refresh** — re-run and replace with live evidence.

| Check | Command | Prior result (snapshot) |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | RC=0 — 155 passed, 6 warnings, 31.82s |
| Live scale (median/9 warm) | same preflight | 5000×200 = 156 ms (≤800), 5000×500 = 381 ms (≤2000) |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | RC=0 — R4-A/B/C present + green; R2/R3 baseline green (217 passed, 32.17s) |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | RC=0 — 5621 passed / 35 skipped / 416.03s / coverage 95% |

`VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` may or may not exist on a fresh runner; bootstrap idempotently.

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4 (shipped on prior evidence, not re-verified on `479ee9f`):**
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.
- **R5:** **NOT STARTED — this is the only acceptable next focus campaign.**

---

## R5 CAMPAIGN (binding scope/acceptance)

**Objective:** make the strategy executable-adapter-ready with evidence-backed realism, without regressing R1–R4.

1. **Baseline gate (blocking):** re-verify R2/R4 preflights (and gate when appropriate) on current `HEAD`; fix regressions before feature work.
2. **R5-A Adapter contract:** paper + injectable/mock exchange, deterministic strict-JSON-safe intents; no network in tests; default `BABStrategy.run()` unchanged when unconfigured.
3. **R5-B Modeled-vs-executed reconciliation:** per-period + aggregate deltas, strict-JSON-safe artifact/report, deterministic fixtures proving math (no live-data claims).
4. **R5-C Executed-fills reconciliation:** realized PnL/cost/equity from fill/execution log vs model backtest for same weights/prices window; explicit mismatches; additive API/CLI/report integration only.
5. **Proof:** focused R5 tests + targeted run + preflights + full gate; record exact evidence and any perf/contract deltas in this file.

---

## BOTTLENECKS REMOVED / ENFORCED (2026-11-14T04:18:31Z refresh)

1. **Single durable handoff enforced** — `HANDOFF.md` only; `AGENT_HANDOFF.md` pointer-only; no parallel/session docs.
2. **Clear, timestamped initial task at top** — binding R5 sequence with exact bootstrap/verify/proof commands so next session cannot avoid heavy work.
3. **Handoff freshness corrected** — refreshed to `HEAD` `479ee9f` @ 2026-11-14T04:18:31Z; prior numeric evidence explicitly marked stale/unverified on current HEAD.
4. **Environment de-blocked** — idempotent venv bootstrap and `PATH="$VENV/bin:$PATH"` for gate; do not report env as a blocker.
5. **Historical noise quarantined** — `research_state/workflow_run_diagnostics.jsonl` is not a current failure/blocker; live run on current `HEAD` wins.
6. **Scope discipline** — no archaeology/probe-count churn, no commentary-only progress, no workflow/guard weakening, no tracked root probe/debug edits; scratch only under `/home/runner/work/_temp/kilo-tmp/`.

---

## KEY ANCHORS / CONTRACTS (do not guess; verify before changing)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` (DatetimeIndex, asset columns, benchmark present). `res`: `betas, signals, weights, backtest, config, returns, kill_switch`.
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`.
- **Dollar neutrality:** `max|weights.sum(axis=1)| <= 1e-9` when configured (`DN_TOL`).
- **Config:** `BABConfig` frozen-ish after `__post_init__`; unknown/wrong types -> `BABConfigError`. Cost knobs: `cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation` in `(0,1]`. R4-B: `max_drawdown_limit` in `(0,1]` or `None`.
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(...)`, `compute_transaction_costs(...)`.
- **R4 contracts:** `dry_run()` strict-JSON-safe/no execution/no `--output`; kill switch `None` = byte-identical default path; replay artifacts deterministic + checksum-stable on identical inputs.
- **Default-path invariant:** no-model/flat/default path must remain behaviorally/byte-identically consistent with shipped behavior; pay new overhead only when configured.
- **Hostile regime builders:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, `DN_TOL`, `BACKTEST_COLUMNS`).
- **Canonical commands:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py`; `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`.

## PERFORMANCE GUARDRAILS (do not regress)

- Prior medians (snapshot, `23d5145` era): 5000×200 ~161 ms (≤800), 5000×500 ~374 ms (≤2000). Guards are ceilings; re-measure live before claiming.

## LOCKS / PROHIBITIONS

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts; use `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting shipped regression suites/guards (R2/R3/R4, historical `batch*`/`campaign*`, `tests/test_beta_neutrality_performance.py`) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure.
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **Commit nothing unless explicitly requested.**

---

## AFTER R5

- Live/paper execution wiring with real venue adapters only when credentials/sandbox + fill data available (do not fake). Broaden reconciliation to production fill schemas.
- Revisit locked `data_loader.py` broad-`except` sweep only with concrete reproducible defect + regression test.

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence on every material run.**
