# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`.

**Priority basis (repo name):** this repository *is* the BAB strategy engine, not a tooling sandbox. Priority order is: (1) BAB beta/signal/backtest correctness; (2) execution realism and reconciliation; (3) live/execution readiness; (4) tests, docs, and coverage. Diagnostics, probe archaeology, and coverage-chasing are means to those ends and must not displace P0/P1 work.

**Refreshed:** 2026-11-14T06:46:17Z (UTC)
**HEAD at refresh:** `fde12bf` (main, `git rev-parse --short HEAD` at refresh). **Live run wins** — if any recorded number conflicts with live output on current `HEAD`, re-measure, record the delta, and update this file immediately.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff/session docs. (`.kilo/task_handoff.md` was removed — duplicate source of truth.)

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T06:46:17Z UTC) — BINDING

**Baseline verified live on `fde12bf` (2026-11-14T06:46:17Z):** R2 preflight RC=0 (155 passed, 6 warnings, 31.29s; live scale 155 ms @5000×200 / 378 ms @5000×500, both within ceilings), R4 preflight RC=0 (31 R4 + 217 R2/R3 baseline passed), R5 integration RC=0 (23 passed, 9.14s), R5-D CLI productization verified (`--adapter paper --reconcile --output` emits execution + reconciliation sidecars, strict-JSON-safe, default path 0.413704 / 252 periods). **Full gate RC=0 on `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%).** R1–R5 + R5-D are complete; do not reopen them without new reproducible evidence of a defect.

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
3. **Full gate (green on current HEAD `fde12bf` — re-run before any release-grade claim):**
   ```bash
   PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh; echo "GATE_RC=$?"
   ```
   Record RC/counts/timings/coverage in this handoff. Last green: `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%).
4. **Next focus campaign (binds this session — implement it; analysis is not completion): R5-E execution-realism / live-readiness hardening.** Additive, deterministic, strict-JSON-safe, default-path invariant. Minimum heavy-work package:
   - **`execution.py` adapter realism:** `PaperAdapter` currently stores `prices_df` but never uses it, and every intent fills in full with zero slippage. Wire deterministic partial-fill modeling, participation caps, and slippage using the supplied `prices_df` / `adv_usd`; preserve the existing default full-fill behavior when realism is not configured. Fill records must expose requested vs filled weight, fill ratio, order weight, notional, price, slippage, status, and an explicit rejection/partial reason where applicable. `MockAdapter` must preserve canned `fill_map`/`fill_fn` behavior and remain deterministic.
   - **`order_batches_from_weights` plumbing:** it accepts `adv_usd` but currently never reads it. Propagate ADV/participation inputs into `OrderIntent`/`OrderBatch` (or an adapter-visible side channel) so participation can be enforced end-to-end; keep strict-JSON-safe output and deterministic column ordering.
   - **`reconciliation.py` correctness:** `reconcile_costs` / `reconcile_fills_to_backtest` must use realized filled weights, not target weights, and must handle partial/rejected fills and fill-level slippage/fees. Broaden mapping only to production fill schemas already representable by the adapters (no invented/live data). Keep per-period + aggregate deltas and SHA-256 checksums.
   - **Integration/CLI:** keep `--adapter`, `--reconcile`, `--fills` additive; with no adapter, `BABStrategy.run()` must keep `execution=None` and the backtest/weights byte-identical. Do not change the default `--output` contract or `--dry-run` behavior.
   - **Tests (required):** add focused deterministic regression tests for partial fills, participation caps, slippage, rejected/unfilled orders, reconciliation math, strict-JSON/determinism, and default-path invariance. Put them in `tests/test_bab_execution_realism_r5e.py` or extend the existing R5 suite; do not duplicate an entire parallel campaign.
   - **Proof sequence:** targeted R5-E tests → `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` → `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`. Record all RCs/counts/timings in this handoff.
5. **Definition of done (all required):** implementation + focused tests + full gate green + this handoff updated with live evidence. No TODO-only stubs, no analysis-only completion, no skipped tests, no fake credentials, and no claim of live-venue readiness without real sandbox/fill evidence.

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts); no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

**Bottleneck policy:** environment is not a blocker (bootstrap venv + prefix `PATH`). Historical diagnostics are not a blocker (live run wins). No real-venue credentials are present — that is an external dependency, not a stall reason: execute R5-E productization now. Single durable handoff only — no parallel/session docs. If a new blocker appears, fix the smallest reproducible cause with a regression test; do not stop at analysis.

---

## VERIFIED EVIDENCE SNAPSHOT (live on current HEAD `fde12bf`)

Captured on HEAD `fde12bf` (2026-11-14T06:46:17Z UTC). Re-verified live this refresh (env: `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` present).

| Check | Command | Live result |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | RC=0 — 155 passed, 6 warnings, 31.29s |
| Live scale (median/9 warm) | same preflight | 5000×200 = 155 ms (≤800), 5000×500 = 378 ms (≤2000) [OK] |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | RC=0 — R4-A/B/C present + green; R2/R3 baseline green (31 R4 + 217 baseline passed, 14 warnings, 10.95s + 34.35s) |
| R5 integration tests | `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` | RC=0 — 23 passed, 9.14s |
| R5-D CLI sanity | `--synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json` | RC=0 — PaperAdapter (1 batch, 2 intents, 2 fills), execution + reconciliation sidecars written, strict-JSON-safe |
| Default-path CLI | `--synthetic` (no adapter) | RC=0 — 0.413704 / 252 periods, byte-identical to pre-R5-D behavior |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | RC=0 — 5644 passed / 35 skipped / 425.16s / coverage 93% on `fde12bf` |

**BOTTLENECK CLEARED (this refresh):** the previous handoff claimed green evidence on `34e734b` while the CLI regression fix (`execution_adapter` passed only when configured) was actually committed in `fde12bf`. That stale HEAD made the recorded evidence unreliable. Re-verified live on `fde12bf`; all checks above are green. No code change was required this refresh. `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` may or may not exist on a fresh runner; bootstrap idempotently.

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4:** shipped and re-verified green on `fde12bf`:
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.
- **R5:** **COMPLETE** (2026-11-14T04:19:52Z) — R5-A execution adapter contract, R5-B modeled-vs-executed cost reconciliation, R5-C executed-fills backtest reconciliation. `tests/test_bab_execution_integration_r5.py` — 23 passed.
- **R5-D:** **COMPLETE** (verified 2026-11-14T06:46:17Z on `fde12bf`) — CLI `--adapter` (paper/mock), `--reconcile`, `--fills`; execution + reconciliation artifacts sidecar `--output`; strict-JSON-safe; default-path byte-identical when unconfigured. `strategies/betting_against_beta/cli.py` modified (additive only; `execution_adapter` passed only when an adapter is configured).
- **R5-E:** **ACTIVE / BINDING** — execution-realism and live-readiness hardening described above. Do not mark complete without implementation, focused tests, full gate, and evidence in this file.
- **Full gate:** **GREEN on `fde12bf`** (2026-11-14T06:46:17Z) — 5644 passed / 35 skipped / 425.16s / coverage 93%. Re-run before any release-grade claim.

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

## R5-E ACTIVE CAMPAIGN (execution-realism / live-readiness, no creds)

**Objective:** harden execution realism and live-readiness without faking live venues or requiring credentials. Additive, deterministic, strict-JSON-safe, default-path invariant. This is the binding next campaign; it is not optional analysis.

**Current gaps to close (verified in code):**
- `PaperAdapter.__init__` accepts `prices_df` but `submit_intents()` never uses it; all fills are full-size with `slippage=0.0`.
- `order_batches_from_weights(..., adv_usd=...)` accepts `adv_usd` but never reads it, so participation cannot be enforced from order batches.
- Reconciliation cost/backtest replay uses target/order weights and assumes fill-level `order_weight`; partial fills represented only by `filled_weight` can be mis-costed or ignored.
- `MockAdapter` canned fills are useful, but there is no shared deterministic realism path for partial fills, participation caps, or slippage.

**Required implementation surface:**
1. **Adapter realism:** add deterministic partial-fill modeling, `max_participation` caps, and slippage drag to `PaperAdapter` (and optionally `MockAdapter` defaults) using supplied `prices_df` / `adv_usd`; preserve the current full-fill default when realism is not configured. Fill records must expose `requested_weight`, `filled_weight`, `fill_ratio`, `order_weight`, `notional_usd`, `price`, `slippage`, `status`, and rejection/partial metadata where applicable.
2. **Order-intent plumbing:** make `adv_usd`/participation inputs actually reach the adapter (extend `OrderIntent`/`OrderBatch` or an adapter-visible side channel); keep deterministic ordering and strict-JSON-safe output.
3. **Reconciliation broadening:** make `reconcile_costs` / `reconcile_fills_to_backtest` consume realized filled weights, handle partial/rejected fills, and use fill-level costs; map only production fill schemas already representable by adapters. Preserve per-period + aggregate deltas and SHA-256 checksums.
4. **CLI/report surfacing:** keep `--adapter`/`--reconcile`/`--fills` additive; no adapter means `execution=None` and byte-identical backtest/weights; `--dry-run`/`--output` contracts unchanged.
5. **Tests:** deterministic regression tests for partial fills, participation caps, slippage, rejected/unfilled orders, reconciliation correctness, JSON-safety/determinism, and default-path invariance. Add `tests/test_bab_execution_realism_r5e.py` or extend the existing R5 suite; no duplicate parallel campaign.
6. **Proof:** targeted R5-E tests → R5 tests → R2/R4 preflights → full gate. Record all RCs/counts/timings in this handoff.

**Live venue execution (external dependency):** wire real exchange adapters only when credentials/sandbox + real fill data are available; do not fake. Broaden reconciliation mapping to production fill schemas once real samples exist.

---

## KEY ANCHORS / CONTRACTS (do not guess; verify before changing)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` (DatetimeIndex, asset columns, benchmark present). `res`: `betas, signals, weights, backtest, config, returns, kill_switch, execution` (R5-A: `execution` is None when no adapter configured, else dict with adapter name, batches, intents, fills).
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`.
- **Dollar neutrality:** `max|weights.sum(axis=1)| <= 1e-9` when configured (`DN_TOL`).
- **Config:** `BABConfig` frozen-ish after `__post_init__`; unknown/wrong types -> `BABConfigError`. Cost knobs: `cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation` in `(0,1]`. R4-B: `max_drawdown_limit` in `(0,1]` or `None`. R5-A: `execution_adapter` passed to `BABStrategy.__init__` (not a BABConfig field; stored on instance).
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(...)`, `compute_transaction_costs(...)`.
- **Execution adapter (R5-A):** `strategies/betting_against_beta/execution.py` — `OrderIntent`, `OrderBatch`, `ExecutionAdapter` (Protocol), `PaperAdapter`, `MockAdapter`, `order_batches_from_weights()`, `execution_payload_to_json()`. Deterministic, strict-JSON-safe, no network.
- **R5-E fill realism fields:** requested vs filled weight, fill ratio, order weight, notional, price, slippage, status, rejection/partial metadata, and participation inputs must be explicit and deterministic.
- **Reconciliation (R5-B / R5-C):** `strategies/betting_against_beta/reconciliation.py` — `reconcile_costs()` (modeled vs executed cost deltas), `reconcile_fills_to_backtest()` (realized equity vs model backtest), `ReconciliationResult` (strict-JSON-safe, SHA-256 checksum).
- **R4 contracts:** `dry_run()` strict-JSON-safe/no execution/no `--output`; kill switch `None` = byte-identical default path; replay artifacts deterministic + checksum-stable on identical inputs.
- **Default-path invariant:** no-model/flat/default path must remain behaviorally/byte-identically consistent with shipped behavior; pay new overhead only when configured. R5-A/D: `BABStrategy.run()`/`cli` with no adapter is byte-identical to pre-R5-D behavior (verified by test).
- **Hostile regime builders:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, `DN_TOL`, `BACKTEST_COLUMNS`).
- **Canonical commands:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider`; `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`.

## PERFORMANCE GUARDRAILS (do not regress)

- Current medians (live, `fde12bf`): 5000×200 = 155 ms (≤800), 5000×500 = 378 ms (≤2000). Guards are ceilings; re-measure live before claiming.

## LOCKS / PROHIBITIONS

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts; use `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting shipped regression suites/guards (R2/R3/R4, historical `batch*`/`campaign*`, `tests/test_beta_neutrality_performance.py`) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure.
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **Commit nothing unless explicitly requested.**

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence (RCs, counts, timings, HEAD) on every material run.**
