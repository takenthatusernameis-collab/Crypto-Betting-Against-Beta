# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Repo:** `crypto-betting-against-beta` — Betting Against Beta (BAB) market-neutral crypto strategy (long low-beta / short high-beta vs benchmark, default BTC). See `README.md`, `strategies/betting_against_beta/`.

**Priority basis (repo name):** this repository *is* the BAB strategy engine, not a tooling sandbox. Priority order is: (1) BAB beta/signal/backtest correctness; (2) execution realism and reconciliation; (3) live/execution readiness; (4) tests, docs, and coverage. Diagnostics, probe archaeology, and coverage-chasing are means to those ends and must not displace P0/P1 work.

**Refreshed:** 2026-11-14T09:05:33Z (UTC)
**HEAD at refresh:** `80b9615` (main). **Live run wins** — if any recorded number conflicts with live output on the current `HEAD`, re-measure, record the delta, and update this file immediately.
**Single source of truth:** this file. `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create parallel handoff/session docs.

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T09:05:33Z UTC) — BINDING

**Live baseline verified on `80b9615` (2026-11-14T09:05:33Z UTC):** R2 preflight RC=0 (green; 155 passed; 5000×200 = 221 ms ≤ 800 ceiling, 5000×500 = 582 ms ≤ 2000 ceiling), R4 preflight RC=0 (R4-A/B/C present + green, R2/R3 baseline 217 passed), R5-E+R5 integration RC=0 (46 passed, 18.83s), R5-D CLI sanity RC=0 (`--adapter paper --reconcile --output` emits execution + reconciliation sidecars; strict-JSON-safe), default-path CLI RC=0 (0.413704 / 252 periods). **Full gate RC=0 on `80b9615` (2026-11-14T09:05:33Z UTC): 5667 passed / 35 skipped / 583.66s / coverage 92%** (5784 stmts, 462 missed). **R1–R5 + R5-D + R5-E are all COMPLETE — do NOT reopen them without new reproducible evidence of a defect.**

**Immediate sequence (execute now, in order):**
1. **Environment/bootstrap (idempotent, not a blocker):**
   ```bash
   VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
   cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
   test -x "$VENV/bin/python" || python3 -m venv "$VENV"
   "$VENV/bin/python" -m pip install -q -r requirements.txt -e .
   ```
2. **Fast re-verify on current HEAD before any new work (required):** use the **absolute venv path** inline — do NOT rely on a `VENV=...` variable across `&&`/subshell boundaries (some runners drop it and silently invoke `/bin/python`, which has no pytest, producing false "No module named pytest" / rc=1 noise). The preflight scripts use `sys.executable`, so invoke them directly with the venv interpreter:
   ```bash
   PY=/home/runner/work/_temp/kilo-tmp/bab-venv/bin/python
   cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
   PYTHONPATH=. "$PY" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
   PYTHONPATH=. "$PY" scripts/bab_r4_preflight.py; echo "R4_PREFLIGHT_RC=$?"
   PYTHONPATH=. "$PY" -m pytest tests/test_bab_execution_integration_r5.py tests/test_bab_execution_realism_r5e.py -q -p no:cacheprovider; echo "R5_TESTS_RC=$?"
   PYTHONPATH=. "$PY" -m strategies.betting_against_beta.cli --synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json; echo "R5D_CLI_RC=$?"
   PYTHONPATH=. "$PY" -m strategies.betting_against_beta.cli --synthetic; echo "DEFAULT_PATH_RC=$?"
   ```
   If any fail: fix the regression first (smallest fix + targeted regression test), record evidence, re-run, then continue.
3. **Full gate (green on `80b9615` — re-run before any release-grade claim):**
   ```bash
   PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh; echo "GATE_RC=$?"
   ```
   Record RC/counts/timings/coverage in this handoff. Last full-gate green: `80b9615` (5667 passed / 35 skipped / 583.66s / coverage 92%).
4. **Next focus campaign (binds this session — implement it; analysis is not completion): R5-F end-to-end execution-realism integration + hardening.** Additive, deterministic, strict-JSON-safe, default-path invariant. **This is the only binding campaign. Do not start a new lettered campaign or parallel test suite; extend R5.**

   **Why R5-F (evidence-based, not busywork):** R5-E implemented the *mechanisms* (deterministic partial fills, participation caps, sqrt-impact slippage on `PaperAdapter`; ADV plumbing into `OrderIntent`; realized-weight reconciliation), but the live gate shows the wiring/edge branches are still **under-exercised**: `execution.py` 72% coverage (uncovered 128–184 = realism-path branches, 527–545 = numpy JSON sanitizer), `reconciliation.py` 74% (uncovered 55–85 sanitizer, 104–138 cost/weight helpers, 291/300/318–319/358–381 realized-weight shortfall + non-finite guards), `backtest.py` 83% (150–176 participation-scaled slippage drag), `cli.py` 81%. R5-F closes the **integration + adversarial-edge** gap: prove the realism path actually changes end-to-end results (modeled vs executed vs reconciled) and that every guard branch is deterministic and non-crashing.

   **Verified code anchors (on `9dc4ac1`; verify before editing):**
   - `strategies/betting_against_beta/execution.py`: `PaperAdapter.__init__` (`:97`), `submit_intents` (`:186`, realism branches ~128–184), `flush` (`:276`), `MockAdapter` (`:281`), `configure_paper_adapter` (`:332`), `order_batches_from_weights` (`:382`), `execution_payload_to_json` (`:548`), `_sanitize_for_json` numpy branch (`:511`).
   - `strategies/betting_against_beta/reconciliation.py`: `_fill_executed_weight` (`:88`), `_fill_cost` (`:119`), `reconcile_costs` (`:141`), `reconcile_fills_to_backtest` (`:249`, shortfall/non-finite guards ~358–381), `_checksum` (`:47`), `_sanitize` (`:53`).
   - `strategies/betting_against_beta/backtest.py:150-176` — participation-scaled slippage drag (`_multiplier = 1 + participation_ratio`); its `except Exception: pass` fallback must never emit NaN/inf.
   - `strategies/betting_against_beta/strategy.py:526-571` — adapter wiring (`configure_paper_adapter`, `order_batches_from_weights`, `submit_intents`, `flush`, `execution_payload`).
   - `strategies/betting_against_beta/cli.py:23-103, 329-445` — `_build_adapter`, `_write_json`, `_run_reconciliation`, `--adapter`/`--reconcile`/`--fills` validation.

   **Minimum heavy-work package (all required):**
   - **End-to-end realism proof:** one deterministic test that runs `BABStrategy.run()` with a configured `PaperAdapter` (prices_df + adv_usd + `partial_fill=True` + `max_participation`) on synthetic data and asserts (a) at least one partial fill (`0 < fill_ratio < 1`), (b) nonzero slippage drag, (c) `reconcile_fills_to_backtest` realized equity diverges from pure-target-weight replay when fills are partial, (d) `execution_payload` is strict-JSON-safe with `allow_nan=False`.
   - **Branch coverage for realism edges (deterministic):** tests for `submit_intents` partial-fill branch (128–184), full-fill default (byte-identical), rejection when ADV exhausted, missing-price/missing-ADV fallback, `MockAdapter` `fill_map`/`fill_fn` still deterministic, `order_batches_from_weights` ADV propagation, `_sanitize_for_json` numpy int/float/bool/ndarray/Series/Index branches.
   - **Reconciliation correctness under stress:** `reconcile_costs` and `reconcile_fills_to_backtest` with mixed full/partial/rejected fills, missing fills for a period, non-finite PnL guard, shortfall absorption, checksum stability across runs and across dict-ordering permutations.
   - **Backtest slippage-drag edge:** participation ratio clipping (0 and ≥1), zero-ADV / zero-price fallback (no NaN/inf), `_multiplier` sanity; assert `except Exception` path leaves flat drag intact. **Live defect evidence:** R4 preflight emits `RuntimeWarning: invalid value encountered in sqrt` at `costs.py:213` (`np.sqrt(participation.values)`) — `participation` is `.clip(upper=cap)` but NOT lower-clipped, so a negative participation (bad/negative ADV) yields sqrt-of-negative → NaN + warning (cleaned later by the `.replace([inf,-inf],nan).fillna(0)` at `costs.py:227`, so no NaN escapes, but the warning is a latent hardening gap). Add a `participation.clip(lower=0.0, upper=cap)` and a regression test asserting no RuntimeWarning and finite costs for negative/zero ADV inputs.
   - **CLI hardening:** `--adapter paper` with realism-producing data, `--reconcile` sidecar schema, `--fills`+`--adapter mock` validation edges, unknown adapter rejection, default-path (`no adapter`) byte-identical.
   - **Tests (required):** extend `tests/test_bab_execution_realism_r5e.py` and/or add `tests/test_bab_execution_integration_r5f.py`; do not duplicate a parallel campaign. No new lettered campaign.
   - **Proof sequence:** targeted R5-F tests → `tests/test_bab_execution_integration_r5.py` + `tests/test_bab_execution_realism_r5e.py` → `scripts/bab_r2_preflight.py` → `scripts/bab_r4_preflight.py` → `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`. Record all RCs/counts/timings/coverage in this handoff.
5. **Definition of done (all required):** implementation + focused tests + full gate green + this handoff updated with live evidence. No TODO-only stubs, no analysis-only completion, no skipped tests, no fake credentials, and no claim of live-venue readiness without real sandbox/fill evidence.

**Non-negotiable constraints:** no `.github/workflows/*` edits; no edits/commits to tracked root probe/debug artifacts (`probe*`, `debug*`, `ast_probe.py`, scratch cov artifacts); no weakening shipped regression suites/guards or locked backtest columns; do not treat `research_state/workflow_run_diagnostics.jsonl` as a current blocker; commit nothing unless explicitly requested. Use `/home/runner/work/_temp/kilo-tmp/` for throwaway artifacts.

**Bottleneck policy (removed/enforced):** environment is not a blocker (bootstrap venv + prefix `PATH`); **fast re-verify must use the absolute venv path inline** — a `VENV=` variable that does not survive the runner's `&&`/subshell boundary silently falls back to `/bin/python` (no pytest) and fakes "No module named pytest"/rc=1 failures (observed 2026-11-14T08:55Z; resolved by absolute path); preflight scripts rely on `sys.executable`, so invoke them with the venv interpreter directly. Historical diagnostics are not a blocker (live run wins); no real-venue credentials are present — that is an external dependency, not a stall reason: execute R5-F integration/hardening now with deterministic paper/mock data; single durable handoff only — no parallel/session docs; no probe archaeology. If a new blocker appears, fix the smallest reproducible cause with a regression test; do not stop at analysis.

---

## VERIFIED EVIDENCE SNAPSHOT (live-verified on `80b9615`; 2026-11-14T09:05:33Z UTC)

Captured on HEAD `80b9615` (2026-11-14T09:05:33Z UTC). Product/test code is byte-identical to `9dc4ac1`/`bcebae0` where R5-E was proven; only handoff docs changed since. Re-verify fast checks on current HEAD before new work (env: `VENV=/home/runner/work/_temp/kilo-tmp/bab-venv`, Python 3.12.3). **Use the absolute venv path inline — see step 2 bottleneck note.**

| Check | Command | Live result |
|---|---|---|
| R2 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` | RC=0 — green; 155 passed; 5000×200 = 221 ms (≤800), 5000×500 = 582 ms (≤2000) [OK] |
| R4 preflight | `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` | RC=0 — R4-A/B/C present + green; R2/R3 baseline 217 passed (emits benign `costs.py:213` sqrt RuntimeWarning — see R5-F hardening target) |
| R5-E + R5 tests | `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py tests/test_bab_execution_realism_r5e.py -q -p no:cacheprovider` | RC=0 — 46 passed, 18.83s |
| R5-D CLI sanity | `--synthetic --adapter paper --reconcile --output /tmp/bab_r5d_sanity.json` | RC=0 — execution + reconciliation sidecars written, strict-JSON-safe (`json.load` OK) |
| Default-path CLI | `--synthetic` (no adapter) | RC=0 — 0.413704 / 252 periods |
| Full gate | `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh` | **RC=0 — 5667 passed / 35 skipped / 583.66s / coverage 92%** (live on `80b9615`) |

**Lowest-coverage product modules (R5-F targets):** `execution.py` 72% (uncovered 128, 134-140, 144, 149-162, 167-184, 329, 344, 350-351, 369-370, 378-379, 398, 426-427, 429-435, 444-445, 453-454, 460-461, 463, 478-479, 489-490, 516, 527-545), `reconciliation.py` 74% (55-85, 104-105, 108-114, 116, 137-138, 291, 300, 318-319, 358-359, 366, 373, 377, 381), `cli.py` 81% (34-103, 289-294, 415-446, 510, 559-617, 661), `backtest.py` 83% (150-176). Overall 92% (5784 stmts, 462 missed).

---

## STATUS

- **R1/R2/R3:** closed/locked — do not reopen without new reproducible evidence.
- **R4:** shipped, re-verified green on `9dc4ac1` (code unchanged through R5-E):
  - **R4-A** dry-run / portfolio-risk report: `BABStrategy.dry_run()` + CLI `--dry-run` (strict-JSON-safe; no trade execution; `--output` not created). `tests/test_bab_dryrun_risk_report_r4.py`.
  - **R4-B** drawdown-limit kill switch: `max_drawdown_limit` in `BABConfig`/`_validate_ranges`, `strategies/betting_against_beta/risk.py` (`apply_kill_switch`, `KillSwitchEvent`), integrated in `run()`/`report()`; `None` preserves pre-R4 default-path behavior. `tests/test_bab_drawdown_kill_switch_r4.py`.
  - **R4-C** deterministic paper-trading replay harness: `strategies/betting_against_beta/replay.py` (`ReplayHarness`) with stable schema, SHA-256 checksum, byte-identical artifacts on identical inputs. `tests/test_bab_replay_harness_r4.py`.
- **R5:** **COMPLETE** — R5-A execution adapter contract, R5-B modeled-vs-executed cost reconciliation, R5-C executed-fills backtest reconciliation. `tests/test_bab_execution_integration_r5.py` — 23 passed.
- **R5-D:** **COMPLETE** — CLI `--adapter` (paper/mock), `--reconcile`, `--fills`; execution + reconciliation artifacts sidecar `--output`; strict-JSON-safe; default-path byte-identical when unconfigured. `strategies/betting_against_beta/cli.py` modified (additive only).
- **R5-E:** **COMPLETE** (verified `bcebae0`, re-verified `9dc4ac1`) — execution-adapter realism (deterministic partial fills, `max_participation` caps, sqrt-impact slippage on `PaperAdapter`), order-intent ADV/participation plumbing (`order_batches_from_weights` reads `adv_usd`; `OrderIntent` exposes `requested_weight`/`filled_weight`/`fill_ratio`/`order_weight`/`notional_usd`/`price`/`slippage`/`status`/`reason`), reconciliation correctness (`reconcile_costs`/`reconcile_fills_to_backtest` consume realized filled weights, handle partial/rejected fills, fill-level costs, SHA-256 checksums). Preserves full-fill/zero-slippage default when realism is unconfigured (default-path byte-identical). `tests/test_bab_execution_realism_r5e.py` — 23 passed.

---

## KEY ANCHORS / CONTRACTS (do not guess; verify before changing)

- **Pipeline/API:** `from strategies.betting_against_beta import BABStrategy`; `res = BABStrategy(...).run(returns_df=df)` (DatetimeIndex, asset columns, benchmark present). `res`: `betas, signals, weights, backtest, config, returns, kill_switch, execution` (R5-A: `execution` is None when no adapter configured, else dict with adapter name, batches, intents, fills).
- **Locked backtest columns:** `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`.
- **Dollar neutrality:** `max|weights.sum(axis=1)| <= 1e-9` when configured (`DN_TOL`).
- **Config:** `BABConfig` frozen-ish after `__post_init__`; unknown/wrong types -> `BABConfigError`. Cost knobs: `cost_model`, `prices`, `adv_usd`, `partial_fill` (bool), `max_participation` (∈(0,1]) in `config.py:107-117`. R4-B: `max_drawdown_limit` in `(0,1]` or `None`. R5-A: `execution_adapter` passed to `BABStrategy.__init__` (not a BABConfig field; stored on instance, `strategy.py:162-191`).
- **Cost model:** `strategies/betting_against_beta/costs.py` — `TransactionCostModel(...)`, `compute_transaction_costs(...)`.
- **Execution adapter (R5-A/E):** `strategies/betting_against_beta/execution.py` — `OrderIntent` (`:25`), `OrderBatch` (`:65`), `ExecutionAdapter` (Protocol, `:79`), `PaperAdapter` (`:97`), `MockAdapter` (`:281`), `configure_paper_adapter` (`:332`), `order_batches_from_weights` (`:382`), `execution_payload_to_json` (`:548`). Deterministic, strict-JSON-safe, no network.
- **Reconciliation (R5-B/C/E):** `strategies/betting_against_beta/reconciliation.py` — `reconcile_costs()` (`:141`), `reconcile_fills_to_backtest()` (`:249`), `_fill_cost()` (`:119`), `_fill_executed_weight()` (`:88`), `ReconciliationResult` (strict-JSON-safe, SHA-256 checksum).
- **R4 contracts:** `dry_run()` strict-JSON-safe/no execution/no `--output`; kill switch `None` = byte-identical default path; replay artifacts deterministic + checksum-stable on identical inputs.
- **Default-path invariant:** no-model/flat/default path must remain behaviorally/byte-identically consistent with shipped behavior; pay new overhead only when configured. R5-A/D/E: `BABStrategy.run()`/`cli` with no adapter is byte-identical to pre-R5-D behavior (verified by test).
- **Hostile regime builders:** `tests/test_bab_stress_regimes.py` (`_base_frame`, `REGIMES`, `REGIME_BUILDERS`, `DN_TOL`, `BACKTEST_COLUMNS`); reuse, do not duplicate.
- **Canonical commands:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py`; `PYTHONPATH=. "$VENV/bin/python" -m pytest tests/test_bab_execution_integration_r5.py tests/test_bab_execution_realism_r5e.py -q -p no:cacheprovider`; `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`.

## PERFORMANCE GUARDRAILS (do not regress)

- Current medians (live, `80b9615` fast-check): 5000×200 = 221 ms (ceiling 800 ms); 5000×500 = 582 ms (ceiling 2000 ms). Guards are ceilings; re-measure live before claiming.

## LOCKS / PROHIBITIONS

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked root probe/debug artifacts; use `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting shipped regression suites/guards (R2/R3/R4, historical `batch*`/`campaign*`, `tests/test_beta_neutrality_performance.py`) or changing locked backtest columns without full dependent updates + recorded delta.
- **No** reopening `research_state/workflow_run_diagnostics.jsonl` as a current failure.
- **No** broad `data_loader.py` silent-`except` sweep unless tied to a specific reproducible defect + regression test.
- **No** new lettered campaign or parallel test suite; R5-F extends R5 only.
- **Commit nothing unless explicitly requested.**

**`HANDOFF.md` is the only durable handoff. Keep it current with evidence (RCs, counts, timings, HEAD) on every material run.**