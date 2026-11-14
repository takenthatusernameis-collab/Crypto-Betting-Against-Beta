# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`. **Priority basis:** the repo *is* the BAB strategy engine, so correctness + live-readiness of the strategy outranks tooling/coverage-chasing.

**Refreshed:** 2026-11-14T03:56:48Z (UTC)
**HEAD at refresh:** `34af42d` (main).
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff docs. If live evidence conflicts with a recorded number here, **live run wins** — re-measure, record the delta, update this file.

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T03:56:48Z UTC)

**Do not idle on analysis.** R1–R4 are shipped on prior evidence; your job is to drive **R5 Execution Integration** to tested, evidence-backed completion while preserving default-path behavior.

**Immediate sequence (execute now):**
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
   If either fails: **stop R5, fix the regression first** (smallest fix + targeted test), record evidence. If both green, run full gate when appropriate: `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh; echo "GATE_RC=$?"` (gate needs venv on `PATH`).
3. **Implement R5 in order (heavy work, tests per step):**
   - **R5-A:** live-order adapter contract/stubs under `strategies/betting_against_beta/` (e.g. `execution.py`) — paper + injectable/mock exchange, deterministic strict-JSON-safe intents where serialized; **default `BABStrategy.run()` unchanged when no adapter configured**. No network in tests.
   - **R5-B:** slippage/impact calibration + reconciliation hook comparing modeled costs (`costs.py`) vs supplied executed-fill data; report per-period + aggregate deltas as strict-JSON-safe artifact/report. Use deterministic fixtures (no fake "live" claims).
   - **R5-C:** executed-fills backtest reconciliation — realized PnL/cost/equity from fill/execution log vs model backtest for same weights/prices window; surface mismatches explicitly. Additive API/CLI/report integration only (default path untouched).
4. **Proof & closeout:** add focused `tests/test_bab_execution_integration_r5*.py` covering adapter contract, reconciliation math, determinism/JSON-safety, and default-path invariance. Run targeted tests → R2/R4 preflights → full gate; **update this HANDOFF with exact commands, RC/counts/durations, and any contract/perf deltas**. Treat live output as truth.

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits to tracked root probe/debug artifacts; no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

---

## VERIFIED EVIDENCE SNAPSHOT (captured on HEAD `d84968c`, 2026-11-14T03:39:22Z)

Re-verify on current `HEAD` before claiming green; do not trust these numbers without fresh output.

| Check | Command | Result |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | **RC=0** — 155 passed, 6 warnings, 31.02s |
| Live scale (median/9 warm) | same preflight | 5000×200 = **165 ms** (≤800 ms), 5000×500 = **379 ms** (≤2000 ms) |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | **RC=0** — R4-A/B/C present + green; R2/R3 baseline green (217 passed, 33.60s) |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | **RC=0** — **5621 passed / 35 skipped / 418.43s / coverage 95%** |

`VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` may or may not exist on a fresh runner; bootstrap idempotently (below).

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4 (SHIPPED on prior evidence):** live-readiness components implemented and green on `23d5145`:
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.

---

## R5 CAMPAIGN (binding, 2026-11-14T03:56:48Z, execute in order)

**Objective:** make the strategy executable-adapter-ready with evidence-backed realism, without regressing R1–R4.

1. **Re-verify baseline on current HEAD (no guessing):** run Mandatory Start/bootstrap, then `bab_r2_preflight.py`, `bab_r4_preflight.py`. If green, run full `bab_gate.sh`. Record RC/counts/durations/deltas in this file. If anything fails, stop R5 and fix the regression first (smallest fix + targeted test).
2. **R5-A Live-order adapter contract (stub, no network in tests):** add a clean adapter interface under `strategies/betting_against_beta/` (e.g. `execution.py`) for order intent generation/submission abstraction (paper + injectable/mock exchange). Keep default `BABStrategy.run()` behavior unchanged when no adapter is configured. Output/intents must be deterministic and strict-JSON-safe where serialized.
3. **R5-B Slippage/impact calibration + reconciliation hook:** provide a calibration/reconciliation path that compares modeled costs (`costs.py`/cost-model path) against supplied executed-fill data and reports deltas (per-period and aggregate) in a strict-JSON-safe artifact/report. Do not claim live calibration without real fill data; ship deterministic fixtures + tests proving the math/reconciliation logic.
4. **R5-C Executed-fills backtest reconciliation:** given a fill/execution log, produce a realized PnL/cost/equity series and compare to model backtest for the same weights/prices window; surface mismatches explicitly. Integrate via additive API/CLI flag or report section (default path untouched).
5. **Proof:** add focused `tests/test_bab_execution_integration_r5*.py` (or equivalent) covering adapter contract, reconciliation math, determinism/JSON-safety, and default-path invariance. Run targeted tests, then R2/R4 preflights, then full gate; update this handoff with exact commands, results, and any perf/contract deltas.

**Bottleneck policy:** do not report "blocked" on environment — bootstrap venv and prefix gate with `PATH="$VENV/bin:$PATH"`. Historical `research_state/workflow_run_diagnostics.jsonl` is noise (not a current failure). If no real blocker exists, proceed with implementation; do not stop at analysis.

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
# Full gate (after targeted/preflights green): PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh
```
- `bab_gate.sh` invokes bare `python3`; **prefix `PATH="$VENV/bin:$PATH"`**.
- Do **not** claim missing deps as blockers — run bootstrap above.
- Do **not** claim green without fresh command output on current `HEAD`.

---

## BOTTLENECKS REMOVED / ENFORCED (2026-11-14T03:56:48Z refresh)

1. **Clear initial task at top** — `INITIAL TASK MESSAGE (START HERE...)` added with timestamp, exact bootstrap/verify commands, and ordered R5 deliverables so next session cannot avoid heavy work.
2. **Handoff freshness** — refreshed to `HEAD` `34af42d` and current timestamp; prior evidence explicitly marked snapshot requiring re-verification.
3. **Single durable handoff** — `HANDOFF.md` only; `AGENT_HANDOFF.md` pointer-only and aligned.
4. **Environment not a blocker** — idempotent venv bootstrap + `PATH="$VENV/bin:$PATH"` for gate preserved.
5. **Historical CI noise quarantined** — `research_state/workflow_run_diagnostics.jsonl` must not justify inaction; live run on current `HEAD` wins.
6. **Scratch discipline** — use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts; do not touch `.github/workflows/*` or tracked root probe/debug artifacts.

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

- Prior medians (`23d5145`): 5000×200 ~161 ms (≤800), 5000×500 ~374 ms (≤2000). Guards are ceilings.

## LOCKS / PROHIBITIONS

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts as applicable); use `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting shipped regression suites/guards (R2/R3/R4, historical `batch*`/`campaign*`, `tests/test_beta_neutrality_performance.py`) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure.
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **No** probe-count/churn campaigns or commentary-only progress. **Commit nothing unless explicitly requested.**

---

## AFTER R5

- Live/paper execution wiring with real venue adapters only when credentials/sandbox + fill data available (do not fake). Broaden reconciliation to production fill schemas.
- Revisit locked `data_loader.py` broad-`except` sweep only with concrete reproducible defect + regression test.

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence on every material run.**
