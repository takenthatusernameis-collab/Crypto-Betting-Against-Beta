# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`.

**Priority basis (repo name):** this repository *is* the BAB strategy engine, not a tooling sandbox. Priority order is: (1) BAB beta/signal/backtest correctness; (2) execution realism and reconciliation; (3) live/execution readiness; (4) tests, docs, and coverage. Diagnostics, probe archaeology, and coverage-chasing are means to those ends and must not displace P0/P1 work.

**Refreshed:** 2026-11-14T06:51:19Z (UTC)
**HEAD at refresh:** `88707a7` (main, `git rev-parse --short HEAD` at refresh). **Live run wins** — if any recorded number conflicts with live output on the current `HEAD`, re-measure, record the delta, and update this file immediately.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff/session docs. (`.kilo/task_handoff.md` does not exist — do not create one.)

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T06:51:19Z UTC) — BINDING

**Baseline last verified live on `a01118d` (2026-11-14T06:49:52Z):** R2 preflight RC=0 (green; 5000×500 = 386 ms ≤ 2000 ceiling), R4 preflight RC=0 (R4-A/B/C present + green, R2/R3 baseline green), R5 integration RC=0 (23 passed, 10.03s), R5-D CLI sanity RC=0 (`--adapter paper --reconcile --output` emits execution + reconciliation sidecars), default-path CLI RC=0 (0.413704 / 252 periods, byte-identical to pre-R5-D). **Code is byte-identical to `fde12bf`** (only `HANDOFF.md`/`AGENT_HANDOFF.md` changed in `fde12bf..88707a7`), so the recorded full-gate green on `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%) still holds for the code, but **re-run the full gate before any release-grade claim**. R1–R5 + R5-D are complete; do not reopen them without new reproducible evidence of a defect. **Step 2 fast re-verify on current HEAD is mandatory before any new work.**

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
   PYTHONPATH=. "$VENV/bin/python" -m strategies.betting_against_beta.cli --synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json; echo "R5D_CLI_RC=$?"
   PYTHONPATH=. "$VENV/bin/python" -m strategies.betting_against_beta.cli --synthetic; echo "DEFAULT_PATH_RC=$?"
   ```
   If any fail: fix the regression first (smallest fix + targeted regression test), record evidence, re-run, then continue.
3. **Full gate (green on code `a01118d` — re-run before any release-grade claim):**
   ```bash
   PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh; echo "GATE_RC=$?"
   ```
   Record RC/counts/timings/coverage in this handoff. Last full-gate green: `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%), code identical on `a01118d`.
4. **Next focus campaign (binds this session — implement it; analysis is not completion): R5-E execution-realism / live-readiness hardening.** Additive, deterministic, strict-JSON-safe, default-path invariant. **This is the only binding campaign. Do not start a new lettered campaign or parallel test suite; extend R5.**

   **R3 vs R5-E boundary (do NOT re-implement R3):** R3 already ships the *cost-model* realism layer — `BABConfig.partial_fill` (bool), `max_participation` (∈(0,1], default 0.10), `prices`, `adv_usd`, `cost_model`, and `compute_transaction_costs` applying sqrt-impact/participation caps to **modeled backtest costs**. `tests/test_bab_execution_realism_r3.py` already covers cost-model sanity, partial-fill-on-slippage, borrow asymmetry, and rebalance-frequency sensitivity. **R5-E is the *execution-adapter* + *reconciliation* layer that consumes those same knobs — it is currently a stub that ignores them.** Do not duplicate R3's cost math.

   **Verified code gaps to close (anchored, on `a01118d`):**
   - `strategies/betting_against_beta/execution.py:93-118` — `PaperAdapter.__init__` accepts `prices_df` but `submit_intents()` never reads it; every fill is full-size `filled_weight = target_weight`, `slippage = 0.0`, `status = "filled"`. No partial fills, no participation cap, no slippage.
   - `strategies/betting_against_beta/execution.py:170-246` — `order_batches_from_weights(weights, prices_df, adv_usd)` computes `notional_usd`/`price` from `prices_df` but **never reads `adv_usd`**, so participation cannot be enforced from order batches. `OrderIntent` (`execution.py:24-50`) has no `adv_usd`/`max_participation`/`requested_weight`/`fill_ratio` fields.
   - `strategies/betting_against_beta/strategy.py:526-546` — wires `prices_df`/`adv_usd` into `order_batches_from_weights` but the adapter cannot consume them.
   - `strategies/betting_against_beta/reconciliation.py:216-320` — `reconcile_fills_to_backtest` replays **target weights** (`prev_w = w.iloc[t]`), ignoring `filled_weight`; partial/rejected fills are mis-costed/ignored. `_fill_cost` (`reconciliation.py:88-99`) reads `order_weight`/`slippage` but not realized filled weight. `reconcile_costs` (`reconciliation.py:108+`) has the same target-vs-realized gap.
   - `MockAdapter` (`execution.py:120-167`) canned fills are fine; the gap is the missing shared deterministic realism path.

   **Minimum heavy-work package (all required):**
   - **`PaperAdapter` realism:** deterministic partial-fill modeling, `max_participation` cap, and slippage using supplied `prices_df` / `adv_usd`. Preserve the existing **full-fill / zero-slippage default** when realism is not configured (i.e. when `prices_df`/`adv_usd`/`partial_fill`/`max_participation` are absent) — default path must stay byte-identical. Fill records must expose `requested_weight`, `filled_weight`, `fill_ratio`, `order_weight`, `notional_usd`, `price`, `slippage`, `status`, and an explicit rejection/partial `reason` where applicable. `MockAdapter` must keep canned `fill_map`/`fill_fn` behavior and remain deterministic.
   - **`order_batches_from_weights` plumbing:** actually read `adv_usd`; propagate ADV/participation inputs into `OrderIntent`/`OrderBatch` (extend the dataclass fields or add an adapter-visible side channel) so participation can be enforced end-to-end. Keep deterministic column ordering and strict-JSON-safe output (`execution_payload_to_json`, `allow_nan=False`).
   - **`reconciliation.py` correctness:** `reconcile_costs` / `reconcile_fills_to_backtest` must use **realized filled weights**, not target weights; handle partial/rejected fills and fill-level slippage/fees. Broaden mapping only to production fill schemas already representable by the adapters (no invented/live data). Keep per-period + aggregate deltas and SHA-256 checksums.
   - **Integration/CLI:** keep `--adapter`, `--reconcile`, `--fills` additive; with no adapter, `BABStrategy.run()` must keep `execution=None` and the backtest/weights byte-identical. Do not change the default `--output` contract or `--dry-run` behavior.
   - **Tests (required):** add focused deterministic regression tests for partial fills, participation caps, slippage, rejected/unfilled orders, reconciliation math, strict-JSON/determinism, and default-path invariance. Put them in `tests/test_bab_execution_realism_r5e.py` or extend `tests/test_bab_execution_integration_r5.py`; do not duplicate an entire parallel campaign.
   - **Proof sequence:** targeted R5-E tests → `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` → `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` → `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`. Record all RCs/counts/timings in this handoff.
5. **Definition of done (all required):** implementation + focused tests + full gate green + this handoff updated with live evidence. No TODO-only stubs, no analysis-only completion, no skipped tests, no fake credentials, and no claim of live-venue readiness without real sandbox/fill evidence.

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts); no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

**Bottleneck policy (removed/enforced):** environment is not a blocker (bootstrap venv + prefix `PATH`); historical diagnostics are not a blocker (live run wins); no real-venue credentials are present — that is an external dependency, not a stall reason: execute the adapter/reconciliation R5-E productization now with deterministic paper/mock data; single durable handoff only — no parallel/session docs; no probe archaeology. If a new blocker appears, fix the smallest reproducible cause with a regression test; do not stop at analysis.

---

## VERIFIED EVIDENCE SNAPSHOT (last live-verified on `a01118d`; code unchanged on `88707a7`)

Captured on HEAD `a01118d` (2026-11-14T06:49:52Z UTC). Re-verify fast checks on current HEAD before new work (env: `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv` present, Python 3.12.3). No product/test code changed in `fde12bf..88707a7` (handoff docs only).

| Check | Command | Live result |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | RC=0 — green; 5000×500 = 386 ms (≤2000) [OK] |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | RC=0 — R4-A/B/C present + green; R2/R3 baseline green |
| R5 integration tests | `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider` | RC=0 — 23 passed, 10.03s |
| R5-D CLI sanity | `--synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json` | RC=0 — execution + reconciliation sidecars written, strict-JSON-safe |
| Default-path CLI | `--synthetic` (no adapter) | RC=0 — 0.413704 / 252 periods, byte-identical to pre-R5-D behavior |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | Last green on `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%); code identical on `a01118d` — re-run before release claim |

**HEAD delta note:** `git diff --stat fde12bf 88707a7` = only `AGENT_HANDOFF.md` + `HANDOFF.md` changed. No product/test code changed, so `fde12bf` full-gate evidence carries; live fast-checks above last re-confirmed on `a01118d`. Re-verify on `88707a7` before new work.

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4:** shipped and last re-verified green on `a01118d` (code unchanged through `88707a7`):
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.
- **R5:** **COMPLETE** (2026-11-14T04:19:52Z) — R5-A execution adapter contract, R5-B modeled-vs-executed cost reconciliation, R5-C executed-fills backtest reconciliation. `tests/test_bab_execution_integration_r5.py` — 23 passed.
- **R5-D:** **COMPLETE** (verified 2026-11-14T06:46:17Z on `fde12bf`, re-confirmed 2026-11-14T06:49:52Z on `a01118d`) — CLI `--adapter` (paper/mock), `--reconcile`, `--fills`; execution + reconciliation artifacts sidecar `--output`; strict-JSON-safe; default-path byte-identical when unconfigured. `strategies/betting_against_beta/cli.py` modified (additive only; `execution_adapter` passed only when an adapter is configured).
- **R5-E:** **ACTIVE / BINDING** — execution-adapter realism + reconciliation hardening described above. Do not mark complete without implementation, focused tests, full gate, and evidence in this file.

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

## R5-E ACTIVE CAMPAIGN (execution-adapter realism / live-readiness, no creds)

**Objective:** harden the execution-adapter and reconciliation layers to consume the already-shipped R3 cost-model knobs (`partial_fill`, `max_participation`, `adv_usd`, `prices`, `cost_model`) deterministically — without faking live venues, requiring credentials, or regressing R1–R4. Additive, deterministic, strict-JSON-safe, default-path invariant. **This is the binding next campaign; it is not optional analysis, and it must not be replaced by a new lettered campaign.**

**R3 boundary (do not re-implement):** R3 already ships `partial_fill`/`max_participation`/`adv_usd`/`prices`/`cost_model` on `BABConfig` and applies them in `compute_transaction_costs` (modeled backtest costs), tested by `tests/test_bab_execution_realism_r3.py`. R5-E is the **execution-adapter** (`PaperAdapter.submit_intents`, `order_batches_from_weights`, `OrderIntent`) and **reconciliation** (`reconcile_costs`, `reconcile_fills_to_backtest`) layer that currently *ignores* those knobs. Close that gap; do not duplicate R3 cost math.

**Current gaps to close (verified in code on `a01118d`):**
- `PaperAdapter.__init__` (`execution.py:93`) accepts `prices_df` but `submit_intents()` (`execution.py:99-118`) never uses it; all fills are full-size with `slippage=0.0`, `status="filled"`.
- `order_batches_from_weights(..., adv_usd=...)` (`execution.py:170-246`) accepts `adv_usd` but never reads it; `OrderIntent` (`execution.py:24-50`) has no `requested_weight`/`fill_ratio`/`adv_usd`/`max_participation` fields.
- `reconcile_costs` (`reconciliation.py:108+`) and `reconcile_fills_to_backtest` (`reconciliation.py:216-320`) replay **target** weights (`prev_w = w.iloc[t]`); `_fill_cost` (`reconciliation.py:88-99`) reads `order_weight`/`slippage` but not realized `filled_weight`; partial/rejected fills are mis-costed or ignored.
- No shared deterministic realism path for partial fills, participation caps, or slippage in the adapters.

**Required implementation surface:**
1. **Adapter realism:** deterministic partial-fill modeling, `max_participation` caps, and slippage drag on `PaperAdapter` (and optionally `MockAdapter` defaults) using supplied `prices_df`/`adv_usd`; preserve full-fill/zero-slippage default when realism is not configured. Fill records must expose `requested_weight`, `filled_weight`, `fill_ratio`, `order_weight`, `notional_usd`, `price`, `slippage`, `status`, and rejection/partial metadata where applicable.
2. **Order-intent plumbing:** make `adv_usd`/participation inputs actually reach the adapter (extend `OrderIntent`/`OrderBatch` or an adapter-visible side channel); keep deterministic ordering and strict-JSON-safe output.
3. **Reconciliation broadening:** make `reconcile_costs`/`reconcile_fills_to_backtest` consume **realized filled weights**, handle partial/rejected fills, and use fill-level costs; map only production fill schemas already representable by adapters. Preserve per-period + aggregate deltas and SHA-256 checksums.
4. **CLI/report surfacing:** keep `--adapter`/`--reconcile`/`--fills` additive; no adapter means `execution=None` and byte-identical backtest/weights; `--dry-run`/`--output` contracts unchanged.
5. **Tests:** deterministic regression tests for partial fills, participation caps, slippage, rejected/unfilled orders, reconciliation correctness, JSON-safety/determinism, and default-path invariance. Add `tests/test_bab_execution_realism_r5e.py` or extend the existing R5 suite; no duplicate parallel campaign.
6. **Proof:** targeted R5-E tests → R5 tests → R2/R4 preflights → full gate. Record all RCs/counts/timings in this handoff.

**Live venue execution (external dependency):** wire real exchange adapters only when credentials/sandbox + real fill data are available; do not fake. Broaden reconciliation mapping to production fill schemas once real samples exist.

---

## KEY ANCHORS / CONTRACTS (do not guess; verify before changing)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` (DatetimeIndex, asset columns, benchmark present). `res`: `betas, signals, weights, backtest, config, returns, kill_switch, execution` (R5-A: `execution` is None when no adapter configured, else dict with adapter name, batches, intents, fills).
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`.
- **Dollar neutrality:** `max|weights.sum(axis=1)| <= 1e-9` when configured (`DN_TOL`).
- **Config:** `BABConfig` frozen-ish after `__post_init__`; unknown/wrong types -> `BABConfigError`. Cost knobs: `cost_model`, `prices`, `adv_usd`, `partial_fill` (bool), `max_participation` (∈(0,1]) in `config.py:107-117`. R4-B: `max_drawdown_limit` in `(0,1]` or `None`. R5-A: `execution_adapter` passed to `BABStrategy.__init__` (not a BABConfig field; stored on instance, `strategy.py:162-191`).
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(...)`, `compute_transaction_costs(...)`.
- **Execution adapter (R5-A):** `strategies/betting_against_beta/execution.py` — `OrderIntent` (`:24`), `OrderBatch` (`:53`), `ExecutionAdapter` (Protocol, `:67`), `PaperAdapter` (`:88`), `MockAdapter` (`:120`), `order_batches_from_weights()` (`:170`), `execution_payload_to_json()` (`:280`). Deterministic, strict-JSON-safe, no network.
- **R5-E fill realism fields:** requested vs filled weight, fill ratio, order weight, notional, price, slippage, status, rejection/partial metadata, and participation inputs must be explicit and deterministic.
- **Reconciliation (R5-B / R5-C):** `strategies/betting_against_beta/reconciliation.py` — `reconcile_costs()` (`:108`), `reconcile_fills_to_backtest()` (`:216`), `_fill_cost()` (`:88`), `ReconciliationResult` (strict-JSON-safe, SHA-256 checksum).
- **R4 contracts:** `dry_run()` strict-JSON-safe/no execution/no `--output`; kill switch `None` = byte-identical default path; replay artifacts deterministic + checksum-stable on identical inputs.
- **Default-path invariant:** no-model/flat/default path must remain behaviorally/byte-identically consistent with shipped behavior; pay new overhead only when configured. R5-A/D: `BABStrategy.run()`/`cli` with no adapter is byte-identical to pre-R5-D behavior (verified by test).
- **Hostile regime builders:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, `DN_TOL`, `BACKTEST_COLUMNS`); reuse, do not duplicate.
- **Canonical commands:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py -q -p no:cacheprovider`; `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`.

## PERFORMANCE GUARDRAILS (do not regress)

- Current medians (live, `a01118d` fast-check): 5000×200 well under 800 ms; 5000×500 = 386 ms (≤2000). Guards are ceilings; re-measure live before claiming.

## LOCKS / PROHIBITIONS

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts; use `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting shipped regression suites/guards (R2/R3/R4, historical `batch*`/`campaign*`, `tests/test_beta_neutrality_performance.py`) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure.
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **No** new lettered campaign or parallel test suite; R5-E extends R5 only.
- **Commit nothing unless explicitly requested.**

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence (RCs, counts, timings, HEAD) on every material run.**