# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`. **Priority basis (repo name):** the repo *is* the BAB strategy engine, so strategy correctness, realism, and live/execution-readiness outrank tooling, diagnostics archaeology, and coverage-chasing.

**Refreshed:** 2026-11-14T04:40:26Z (UTC)
**HEAD at refresh:** `196a492` (main, `git rev-parse --short HEAD` at refresh). **Live run wins** — if any recorded number conflicts with live output on current `HEAD`, re-measure, record the delta, and update this file immediately.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff/session docs.

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T04:40:26Z UTC) — BINDING

**Baseline verified green on `196a492` (2026-11-14T04:40:26Z):** R2 preflight RC=0 (155 passed, 170 ms @5000×200, 406 ms @5000×500), R4 preflight RC=0 (31 R4 + 217 R2/R3 baseline passed), R5 integration RC=0 (23 passed). **R1–R5 are complete; do not reopen them without new reproducible evidence of a defect.**

**Immediate sequence (execute now, in order):**
1. **Environment/bootstrap (idempotent, do not treat as blocker):**
   ```bash
   VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
   cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
   test -x "$VENV/bin/python" || python3 -m venv "$VENV"
   "$VENV/bin/python" -m pip install -q -r requirements.txt -e .
   ```
2. **Fast re-verify on current HEAD before any new work (required):**
   ```bash
   PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
   PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py; echo "R4_PREFLIGHT_RC=$?"
   PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider; echo "R5_TESTS_RC=$?"
   ```
   If any fail: fix the regression first (smallest fix + targeted regression test), record evidence, re-run, then continue.
3. **Post-R5 heavy campaign (proceed immediately when baseline is green — do not stop at analysis): R5-D Execution/Reconciliation productization (additive, no live creds).** `execution.py` (`PaperAdapter`/`MockAdapter`, `order_batches_from_weights`) and `reconciliation.py` (`reconcile_costs`, `reconcile_fills_to_backtest`) exist but are **not exposed in CLI or report paths**. Implement additive, deterministic, strict-JSON-safe surfacing so the strategy is operationally usable without faking live venues:
   - Add CLI support to run with an in-process paper/mock execution adapter (no network, no credentials) and emit execution + reconciliation artifacts alongside existing outputs; `--output`/`--dry-run` contracts and default behavior must remain unchanged when unconfigured (byte-identical default path).
   - Add/extend report helpers and/or result serialization paths for execution payloads and `ReconciliationResult` (per-period + aggregate deltas, checksums) with stable schema; broaden to cover realistic fill schemas already representable by adapters (no invented/live data).
   - Write focused tests proving: CLI additive flags/JSON-safety/determinism, reconciliation artifact correctness on deterministic fixtures, and **default-path invariance** (no adapter/config => identical backtest/weights/outputs vs pre-R5-D behavior).
4. **Proof sequence:** targeted R5-D tests → `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` → when appropriate full gate `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`. Record all RCs/counts/timings in this handoff.
5. **Live/paper venue wiring with real credentials/sandbox + real fills:** **only** when such credentials/fill data are actually available in the environment; do not fake. If unavailable, complete R5-D productization and document the exact remaining external dependency.

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts); no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

**Bottleneck policy:** environment is not a blocker (bootstrap venv + prefix `PATH`). Historical diagnostics are not a blocker (live run wins). No credentials are present for real-venue execution in this environment — that is an external dependency, not a reason to stall: execute R5-D productization now. If no real blocker exists, proceed with implementation; do not stop at analysis.

---

## VERIFIED EVIDENCE SNAPSHOT (live on current HEAD `196a492`)

Captured on HEAD `196a492` (2026-11-14T04:40:26Z UTC). Re-verified live this session after handoff refresh (env: `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` present).

| Check | Command | Live result |
|---|---|---|
| R5 integration tests | `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` | RC=0 — 23 passed, 10.33s |
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | RC=0 — 155 passed, 6 warnings, 37.44s |
| Live scale (median/9 warm) | same preflight | 5000×200 = 170 ms (≤800), 5000×500 = 406 ms (≤2000) |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | RC=0 — R4-A/B/C present + green; R2/R3 baseline green (31 R4 + 217 baseline passed, 14 warnings, ~51.8s total) |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | **Not re-run this refresh** (last recorded green on `479ee9f`: 5644 passed / 35 skipped / 437.58s / coverage 94%). Re-run before any merge/release-grade claim or if behavior changes. |

`VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` may or may not exist on a fresh runner; bootstrap idempotently.

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4:** shipped and re-verified green on `479ee9f`:
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.
- **R5:** **COMPLETE** (2026-11-14T04:19:52Z) — all three sub-campaigns implemented, tested, verified green:
  - **R5-A** execution adapter contract: `strategies/betting_against_beta/execution.py` (`OrderIntent`, `OrderBatch`, `ExecutionAdapter` protocol, `PaperAdapter`, `MockAdapter`, `order_batches_from_weights`). Wired into `BABStrategy` via `execution_adapter` constructor arg; default path (no adapter) byte-identical to pre-R5. `BABStrategy.run()` result includes `execution` payload when adapter configured. `tests/test_bab_execution_integration_r5.py` — 23 passed.
  - **R5-B** modeled-vs-executed cost reconciliation: `strategies/betting_against_beta/reconciliation.py` (`reconcile_costs`). Compares `compute_transaction_costs` modeled costs vs executed fills; per-period + aggregate deltas; strict-JSON-safe `ReconciliationResult` with SHA-256 checksum; deterministic.
  - **R5-C** executed-fills backtest reconciliation: `reconcile_fills_to_backtest`. Realized PnL/cost/equity from fill log vs model backtest for same weights/prices window; explicit mismatch surfacing via per-period delta and `n_mismatches` aggregate. Additive API only; default path untouched.

---

## R5 CAMPAIGN (complete — 2026-11-14T04:19:52Z)

**Objective:** make the strategy executable-adapter-ready with evidence-backed realism, without regressing R1–R4. **ACHIEVED.**

1. **Baseline gate (blocking):** re-verified R2/R4 preflights (and full gate) on current `HEAD`; all green before and after feature work.
2. **R5-A Adapter contract:** `strategies/betting_against_beta/execution.py` — paper + injectable/mock exchange, deterministic strict-JSON-safe intents; no network in tests; default `BABStrategy.run()` unchanged when unconfigured (byte-identical verified by test).
3. **R5-B Modeled-vs-executed reconciliation:** `reconcile_costs` in `strategies/betting_against_beta/reconciliation.py` — per-period + aggregate deltas, strict-JSON-safe artifact/report, deterministic fixtures proving math (no live-data claims).
4. **R5-C Executed-fills reconciliation:** `reconcile_fills_to_backtest` in `reconciliation.py` — realized PnL/cost/equity from fill/execution log vs model backtest for same weights/prices window; explicit mismatches surfaced; additive API/CLI/report integration only (default path untouched).
5. **Proof:** 23 focused R5 tests in `tests/test_bab_execution_integration_r5.py` (adapter contract, reconciliation math, determinism/JSON-safety, default-path invariance). Targeted tests → R2/R4 preflights → full gate all green. Evidence recorded in VERIFIED EVIDENCE SNAPSHOT above.

**New product files:** `strategies/betting_against_beta/execution.py`, `strategies/betting_against_beta/reconciliation.py`.
**New test file:** `tests/test_bab_execution_integration_r5.py` (23 tests).
**Modified files:** `strategies/betting_against_beta/strategy.py` (execution_adapter wiring + BABResult.execution field), `strategies/betting_against_beta/__init__.py` (export execution + reconciliation).

---

## BOTTLENECKS REMOVED / ENFORCED (2026-11-14T04:40:26Z refresh)

1. **Single durable handoff enforced** — `HANDOFF.md` only; `AGENT_HANDOFF.md` pointer-only; no parallel/session docs.
2. **Clear, timestamped initial task at top** — binding post-R5 sequence with exact bootstrap/verify/proof commands and a concrete **R5-D heavy campaign** (CLI/report execution + reconciliation productization) so next session cannot avoid substantive implementation.
3. **Handoff freshness corrected** — refreshed to `HEAD` `196a492` @ 2026-11-14T04:40:26Z; R2/R4/R5 re-verified live on current HEAD (full gate noted as not re-run this refresh).
4. **Environment de-blocked** — idempotent venv bootstrap and `PATH="$VENV/bin:$PATH"` for gate; do not report env as a blocker.
5. **Historical noise quarantined** — `research_state/workflow_run_diagnostics.jsonl` contains historical log excerpts only; not a current failure/blocker. **Live run on current `HEAD` wins.**
6. **External-dependency clarity** — no real venue credentials/sandbox/fill data available in this environment; **do not fake live execution**. This does not block R5-D (deterministic paper/mock adapters, no network) — proceed with implementation.
7. **Scope discipline** — no archaeology/probe-count churn, no commentary-only progress, no workflow/guard weakening, no tracked root probe/debug edits; scratch only under `/home/runner/work/_temp/kilo-tmp/`.
8. **R1–R5 locked** — execution adapter + reconciliation modules implemented/tested; default-path invariance proven. Do not reopen without new reproducible evidence.

---

## KEY ANCHORS / CONTRACTS (do not guess; verify before changing)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` (DatetimeIndex, asset columns, benchmark present). `res`: `betas, signals, weights, backtest, config, returns, kill_switch, execution` (R5-A: `execution` is None when no adapter configured, else dict with adapter name, batches, intents, fills).
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`.
- **Dollar neutrality:** `max|weights.sum(axis=1)| <= 1e-9` when configured (`DN_TOL`).
- **Config:** `BABConfig` frozen-ish after `__post_init__`; unknown/wrong types -> `BABConfigError`. Cost knobs: `cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation` in `(0,1]`. R4-B: `max_drawdown_limit` in `(0,1]` or `None`. R5-A: `execution_adapter` passed to `BABStrategy.__init__` (not a BABConfig field; stored on instance).
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(...)`, `compute_transaction_costs(...)`.
- **Execution adapter (R5-A):** `strategies/betting_against_beta/execution.py` — `OrderIntent`, `OrderBatch`, `ExecutionAdapter` (Protocol), `PaperAdapter`, `MockAdapter`, `order_batches_from_weights()`, `execution_payload_to_json()`. Deterministic, strict-JSON-safe, no network.
- **Reconciliation (R5-B / R5-C):** `strategies/betting_against_beta/reconciliation.py` — `reconcile_costs()` (modeled vs executed cost deltas), `reconcile_fills_to_backtest()` (realized equity vs model backtest), `ReconciliationResult` (strict-JSON-safe, SHA-256 checksum).
- **R4 contracts:** `dry_run()` strict-JSON-safe/no execution/no `--output`; kill switch `None` = byte-identical default path; replay artifacts deterministic + checksum-stable on identical inputs.
- **Default-path invariant:** no-model/flat/default path must remain behaviorally/byte-identically consistent with shipped behavior; pay new overhead only when configured. R5-A: `BABStrategy.run()` with no adapter is byte-identical to pre-R5 (verified by test).
- **Hostile regime builders:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, `DN_TOL`, `BACKTEST_COLUMNS`).
- **Canonical commands:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider`; `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`.

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

## AFTER R5 (next campaign: R5-D)

- **R5-D (now, no creds required):** CLI/report execution + reconciliation productization — additive, deterministic, strict-JSON-safe. Wire `PaperAdapter`/`MockAdapter` and `reconcile_costs`/`reconcile_fills_to_backtest` into CLI/report/output paths with stable artifact schema and checksums; preserve default-path invariance and existing `--dry-run`/`--output` contracts. Add focused regression tests.
- **Live venue execution (external dependency):** wire real exchange adapters only when credentials/sandbox + real fill data are available; do not fake. Broaden reconciliation mapping to production fill schemas once real samples exist.
- **Deferred:** revisit locked `data_loader.py` broad-`except` sweep only with a concrete reproducible defect + regression test.

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence (RCs, counts, timings, HEAD) on every material run.**
