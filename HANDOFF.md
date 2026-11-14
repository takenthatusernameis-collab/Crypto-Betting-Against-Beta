# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`. **Priority basis (repo name):** the repo *is* the BAB strategy engine, so strategy correctness, realism, and live/execution-readiness outrank tooling, diagnostics archaeology, and coverage-chasing.

**Refreshed:** 2026-11-14T06:19:45Z (UTC)
**HEAD at refresh:** `34e734b` (main, `git rev-parse --short HEAD` at refresh). **Live run wins** — if any recorded number conflicts with live output on current `HEAD`, re-measure, record the delta, and update this file immediately.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff/session docs. (`.kilo/task_handoff.md` removed — duplicate source of truth.)

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T06:19:45Z UTC) — BINDING

**Baseline verified green on `34e734b` (2026-11-14T06:19:45Z):** R2 preflight RC=0 (155 passed, 37.87s @5000×200 / 425 ms @5000×500, within ceilings), R4 preflight RC=0 (31 R4 + 217 R2/R3 baseline passed), R5 integration RC=0 (23 passed, 18.10s), R5-D CLI productization verified (`--adapter paper --reconcile --output` emits execution + reconciliation sidecars, strict-JSON-safe, default-path byte-identical: 0.413704 / 252 periods). **Full gate RC=0 on `34e734b` (5644 passed / 35 skipped / 426.48s / coverage 93%) — blocker cleared.** R1–R5 + R5-D are complete; do not reopen them without new reproducible evidence of a defect.

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
   # R5-D CLI sanity: additive flags, strict-JSON-safe, default-path invariant
   PYTHONPATH=. "$VENV/bin/python" -m strategies.betting_against_beta.cli --synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json; echo "R5D_CLI_RC=$?"
   PYTHONPATH=. "$VENV/bin/python" -m strategies.betting_against_beta.cli --synthetic; echo "DEFAULT_PATH_RC=$?"
   ```
   If any fail: fix the regression first (smallest fix + targeted regression test), record evidence, re-run, then continue.
3. **Full gate (green on current HEAD `34e734b` — re-run before any release-grade claim):**
   ```bash
   PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh; echo "GATE_RC=$?"
   ```
   Record RC/counts/timings/coverage in this handoff. Last green: `34e734b` (5644 passed / 35 skipped / 426.48s / coverage 93%).
4. **Next focus campaign (binds the session — do not stop at analysis): R5-E execution-realism / live-readiness hardening (additive, deterministic, no live creds, no faking).** Wire realism into `PaperAdapter`/`MockAdapter` (partial fill, slippage, `max_participation` caps) and broaden `reconcile_costs`/`reconcile_fills_to_backtest` to production fill schemas already representable by adapters; add deterministic stress fixtures + focused regression tests; preserve default-path invariance and existing `--dry-run`/`--output` contracts. Live venue execution with real credentials is an **external dependency** — proceed only when creds/sandbox/fill data are actually available; do not fake.
5. **Proof sequence:** targeted R5-E tests → `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` → `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`. Record all RCs/counts/timings in this handoff.

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts); no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

**Bottleneck policy:** environment is not a blocker (bootstrap venv + prefix `PATH`). Historical diagnostics are not a blocker (live run wins). No real-venue creds present — external dependency, not a stall reason: execute R5-E productization now. Single durable handoff only — no parallel/session docs. If no real blocker exists, proceed with implementation; do not stop at analysis.

---

## VERIFIED EVIDENCE SNAPSHOT (live on current HEAD `34e734b`)

Captured on HEAD `34e734b` (2026-11-14T06:19:45Z UTC). Re-verified live this session (env: `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` present). A real regression surfaced during the gate run (see BOTTLENECK CLEARED below) and was fixed before this refresh.

| Check | Command | Live result |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | RC=0 — 155 passed, 6 warnings, 37.87s |
| Live scale (median/9 warm) | same preflight | 5000×200 = 197 ms (≤800), 5000×500 = 425 ms (≤2000) [OK] |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | RC=0 — R4-A/B/C present + green; R2/R3 baseline green (31 R4 + 217 baseline passed, 14 warnings, ~52.8s total) |
| R5 integration tests | `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` | RC=0 — 23 passed, 18.10s |
| R5-D CLI sanity | `--synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json` | RC=0 — PaperAdapter (1 batch, 2 intents, 2 fills), execution + reconciliation sidecars written, strict-JSON-safe, default-path byte-identical when unconfigured (0.413704 / 252 periods) |
| Default-path CLI | `--synthetic` (no adapter) | RC=0 — 0.413704 / 252 periods, byte-identical to pre-R5-D behavior |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | RC=0 — 5644 passed / 35 skipped / 426.48s / coverage 93% on `34e734b` |

**BOTTLENECK CLEARED (this session):** The full gate on `34e734b` initially failed 14 CLI tests (root cause: `cli.py` always passed `execution_adapter=` to `BABStrategy(...)` even when `None`, breaking fakes/monkeypatches whose `__init__` accepts only `config`). Fixed in `strategies/betting_against_beta/cli.py:506` — `execution_adapter` is now passed only when an adapter is actually configured, preserving default-path byte-identical behavior. Gate re-run: green (5644 passed / 35 skipped).

`VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` may or may not exist on a fresh runner; bootstrap idempotently.

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4:** shipped and re-verified green on `1e067e3`:
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.
- **R5:** **COMPLETE** (2026-11-14T04:19:52Z) — R5-A execution adapter contract, R5-B modeled-vs-executed cost reconciliation, R5-C executed-fills backtest reconciliation. `tests/test_bab_execution_integration_r5.py` — 23 passed.
- **R5-D:** **COMPLETE** (verified 2026-11-14T06:19:45Z on `34e734b`) — CLI `--adapter` (paper/mock), `--reconcile`, `--fills`; execution + reconciliation artifacts sidecar `--output`; strict-JSON-safe; default-path byte-identical when unconfigured. `strategies/betting_against_beta/cli.py` modified (additive only; `execution_adapter` passed only when an adapter is configured).
- **Full gate:** **GREEN on `34e734b`** (2026-11-14T06:19:45Z) — 5644 passed / 35 skipped / 426.48s / coverage 93%. Re-run before any release-grade claim.

---

## R5 CAMPAIGN (complete — 2026-11-14T04:19:52Z)

**Objective:** make the strategy executable-adapter-ready with evidence-backed realism, without regressing R1–R4. **ACHIEVED.**

1. **Baseline gate (blocking):** re-verified R2/R4 preflights on current `HEAD`; all green before and after feature work.
2. **R5-A Adapter contract:** `strategies/betting_against_beta/execution.py` — paper + injectable/mock exchange, deterministic strict-JSON-safe intents; no network in tests; default `BABStrategy.run()` unchanged when unconfigured (byte-identical verified by test).
3. **R5-B Modeled-vs-executed reconciliation:** `reconcile_costs` in `strategies/betting_against_beta/reconciliation.py` — per-period + aggregate deltas, strict-JSON-safe artifact/report, deterministic fixtures proving math (no live-data claims).
4. **R5-C Executed-fills reconciliation:** `reconcile_fills_to_backtest` in `reconciliation.py` — realized PnL/cost/equity from fill/execution log vs model backtest for same weights/prices window; explicit mismatches surfaced; additive API/CLI/report integration only (default path untouched).
5. **Proof:** 23 focused R5 tests in `tests/test_bab_execution_integration_r5.py` (adapter contract, reconciliation math, determinism/JSON-safety, default-path invariance). Targeted tests → R2/R4 preflights → full gate all green. Evidence recorded in VERIFIED EVIDENCE SNAPSHOT above.

**New product files:** `strategies/betting_against_beta/execution.py`, `strategies/betting_against_beta/reconciliation.py`.
**New test file:** `tests/test_bab_execution_integration_r5.py` (23 tests).
**Modified files:** `strategies/betting_against_beta/strategy.py` (execution_adapter wiring + BABResult.execution field), `strategies/betting_against_beta/__init__.py` (export execution + reconciliation), `strategies/betting_against_beta/cli.py` (R5-D `--adapter`/`--reconcile`/`--fills` + artifacts).

---

## R5-E NEXT FOCUS CAMPAIGN (execution-realism / live-readiness, no creds)

**Objective:** harden execution realism and live-readiness without faking live venues or requiring credentials. Additive, deterministic, strict-JSON-safe, default-path invariant.

1. **Adapter realism:** extend `PaperAdapter`/`MockAdapter` in `strategies/betting_against_beta/execution.py` with partial-fill modeling, slippage drag, and `max_participation` caps; deterministic on fixed seeds/fixtures; no network.
2. **Reconciliation broadening:** extend `reconcile_costs` / `reconcile_fills_to_backtest` in `strategies/betting_against_beta/reconciliation.py` to map production fill schemas already representable by adapters (no invented/live data); per-period + aggregate deltas + SHA-256 checksum; strict-JSON-safe artifacts.
3. **CLI/report surfacing:** keep `--adapter`/`--reconcile`/`--fills` additive; ensure default path (no adapter) remains byte-identical; `--dry-run`/`--output` contracts unchanged.
4. **Tests:** focused regression tests for adapter realism, reconciliation correctness on deterministic fixtures, JSON-safety/determinism, default-path invariance.
5. **Proof:** R5-E tests → R5 tests → R2/R4 preflights → full gate. Record all RCs/counts/timings.

**Live venue execution (external dependency):** wire real exchange adapters only when credentials/sandbox + real fill data are available; do not fake. Broaden reconciliation mapping to production fill schemas once real samples exist.

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
- **Default-path invariant:** no-model/flat/default path must remain behaviorally/byte-identically consistent with shipped behavior; pay new overhead only when configured. R5-A/D: `BABStrategy.run()`/`cli` with no adapter is byte-identical to pre-R5-D behavior (verified by test).
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

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence (RCs, counts, timings, HEAD) on every material run.**
