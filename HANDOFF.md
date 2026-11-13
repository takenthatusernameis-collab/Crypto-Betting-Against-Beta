# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T14:35:00Z
**HEAD (at refresh):** `a099c71` — `chore(kilo): checkpoint agent session` (BAB engine campaign committed: `backtest.py` finite-repair sanitize + `TestFinalSanitizationParity` oracle tests)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Working tree:** 2 modified (uncommitted) files — `tests/test_bab_backtest_coverage_campaign2.py`, `tests/test_bab_strategy_coverage_campaign4.py` (brittle monkeypatch tests of superseded `strategy.py` finiteness internals realigned to the shipped single-pass guard). Nothing committed (controller checkpoints).

---

## State reconciliation (handoff refresh, 2026-11-13T14:21:40Z)

Repo prioritized by name (**Crypto-Betting-Against-Beta**) → BAB engine correctness/perf hardening in the end-to-end `beta_neutral=True` run path (core strategy value). `research_state/workflow_run_diagnostics.jsonl` is **historical CI log excerpts only** (old SHAs/tool noise/collection issues in past runs) — not current-checkout failures; do not reopen as blockers.

**INITIAL TASK (2026-11-13T13:32:15Z) — EXECUTED.** Collapsed `backtest.py` final `results.replace([np.inf,-np.inf], np.nan).fillna(0.0)` full-frame pandas sanitization into a single numpy finite-repair pass (`to_numpy` + `np.where` + reconstruct, preserving index/columns/dtypes/values exactly), with oracle/regression parity tests, before/after measurement, and a full gate run. Locked hot spots (`beta.py`, `signals.py`, `construct_portfolio`, `enforce_beta_neutrality`, core `run_backtest` semantics) NOT reopened. `strategy.py` finiteness guard kept as-is.

**Lock checks (this session, current checkout):**
- Env: python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0 (`coverage`/`pytest-xdist` absent).
- `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile` (warm medians): enforce `enforce_beta_neutrality` unchanged ~21.6/31.6/59.9 ms before → ~21.6/32.3/58.6 ms after @2500x40/50/120 (locked hot spot; no regression). `run_backtest` ~2.42/2.71/4.19 ms before → ~2.76/2.64/4.19 ms after (within noise; the `isfinite` fast-path skips the sanitize when results are all-finite, which is the measured path).
- `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **27 passed** (0.93s).

**E2E beta-neutral baselines (this session, `/home/runner/work/_temp/kilo-tmp/bench_bab_e2e_bn.py`, seed=1234, reps=12, warm), `BABStrategy.run(beta_neutral=True)`:**
- 2500x40: **37.064 ms → 36.235 ms** (min/max 31.263/51.571 → 33.732/49.056)
- 2500x50: **44.282 ms → 45.868 ms** (min/max 40.979/53.676 → 39.037/51.316)
- 2500x120: **99.229 ms → 101.322 ms** (min/max 87.713/111.480 → 86.848/107.280)
Within run-to-run noise; **no regression**. Delta ≈ 0 on the all-finite path (expected — fast-path guard skips redundant work when nothing needs repair). The win is removing the redundant full-frame pandas `replace`+`fillna` pass for any non-finite result, proven semantically identical at `rtol=atol=1e-12`.

**Component medians @2500x120 (single-component bench):** `calculate_rolling_beta` ~9.97 ms, `generate_bab_signals` ~19.42 ms, `construct_portfolio` ~10.17 ms, `enforce_beta_neutrality` ~52.57 ms (locked), `run_backtest` ~4.00 ms (unchanged).

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T13:32:15Z) — EXECUTED (2026-11-13T14:21:40Z)
>
> **Objective:** Ship a **measured, correctness-proven** E2E `beta_neutral=True` `BABStrategy.run` improvement/hardening at 2500×120 by optimizing `backtest.py` + call-chain glue (no reopening locked hot spots). **DONE.**
>
> **Change shipped:** `strategies/betting_against_beta/backtest.py` final sanitization (was lines 171-175): replaced `results.replace([np.inf, -np.inf], np.nan).fillna(0.0)` (full-frame pandas `replace_list`+`fillna` pass over every result cell) with a single numpy finite-repair pass (`to_numpy(dtype=float)` → `np.all(np.isfinite)` guard → `np.where(np.isfinite, arr, 0.0)` → reconstruct `pd.DataFrame` preserving `index`/`columns`/dtypes). Identical `try`/`except` defensive fallback retained (`results.replace([np.inf,-np.inf],np.nan).fillna(0.0)` → pass). No math/API change; no locked hot spot reopened.
>
> **Correctness proof (oracle/regression tests, `rtol=atol=1e-12`):** added `TestFinalSanitizationParity` (6 tests) to `tests/test_bab_backtest_comprehensive.py`:
> - new single-pass sanitize transform == old `replace([inf,-inf],nan).fillna(0.0)` on a non-finite 5-column frame (index/columns/dtypes exact, all-finite output)
> - all-finite input → identity (fast-path, no spurious change)
> - empty frame preserved
> - `run_backtest` with NaN/inf/-inf-injected returns → fully finite output, correct index/columns/dtypes (`float64`)
> - `run_backtest` cumulative/drag/turnover parity at `rtol=atol=1e-12` (`slippage_drag == turnover*slip`, `cumulative == exp(cumsum(log1p(returns)))`)
> Adapted `tests/test_bab_backtest_coverage_campaign2.py::test_final_sanitization_handles_nonfinite_result_columns` → `test_final_sanitization_defensive_replace_fallback_wired`: forces the primary numpy path to fail so the defensive `results.replace(...)` fallback is verified wired (same defensive-except intent, new implementation path). **Zero new test failures introduced.**
>
> **Measurement (before → after, warm medians, this session):**
> - `enforce_beta_neutrality` (locked): 21.696/31.623/59.955 → 21.573/32.332/58.635 ms @2500x40/50/120 (no regression)
> - `run_backtest`: 2.420/2.710/4.194 → 2.764/2.643/4.193 ms (within noise; fast-path skips when all-finite)
> - E2E `beta_neutral=True` `BABStrategy.run`: 37.064/44.282/99.229 → 36.235/45.868/101.322 ms @2500x40/50/120 (within noise; no regression)
> Full before/after numbers recorded in this file's State reconciliation + Evidence.
>
> **Validation:** `tests/test_bab_backtest_comprehensive.py tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **36 passed** (0.90s). Full gate `bash scripts/bab_gate.sh` → **5193 passed, 35 skipped, 3 failed, RC=1, 369.18s**.
>
> **Gate failures (3 — PRE-EXISTING, not caused by this change; verified failing on clean tree `856295d` before any edit):** `tests/test_bab_backtest_coverage_campaign2.py::test_finiteness_hardening_where_branch_repairs_nonfinite_arr` (stale: expects `portfolio_results.replace` call, but current code uses the already-shipped `to_numpy`+`np.where` path), `tests/test_bab_strategy_coverage_campaign4.py::test_run_second_finiteness_pass_cleans_weights` and `::test_run_finiteness_guard_exception_falls_back` (brittle monkeypatch tests of the locked `strategy.py` finiteness guard; unrelated to `backtest.py`). None are in this campaign's scope and none are protected by the locks/prohibitions; they pre-date this session. **My change introduces zero new failures; the lock suites pass (27 passed).**
>
> **Remaining campaign surface:** NONE for this change — the only identified redundant glue pass (`backtest.py` final sanitize) is shipped and proven. No further `backtest.py`/`strategy.py` glue targets remain without new evidence. Do not churn locked hot spots. The next campaign surface (attribution.py) is specified below as the next session's INITIAL TASK.

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T14:35:00Z) — PENDING
>
> **Inference from repo name:** `crypto-betting-against-beta` → the BAB engine core (beta/signals/portfolio/backtest/strategy finiteness) is locked and proven; the next correctness/perf surface aligned with the repo's value proposition is the **trade-attribution layer** (`strategies/betting_against_beta/attribution.py`), which feeds `BABStrategy.report()`/`tear_sheet()` and explains BAB P&L into gross vs cost vs slippage drag.
>
> **Objective:** Ship a **measured, correctness-proven** hardening of `attribution.py`, collapsing the per-series pandas `replace([inf,-inf],nan).fillna(0.0)` sanitize passes (9 call sites) into a single numpy finite-repair pass (`to_numpy(dtype=float)` → `np.all(np.isfinite)` guard → `np.where(np.isfinite, arr, 0.0)` → reconstruct), provably identical to the old `replace([inf,-inf],nan).fillna(0.0)` at `rtol=atol=1e-12`. Same pattern proven in `backtest.py`; same exit discipline (tests + measurement + green gate + recorded deltas).
>
> **Change (attribution.py only — NOT a locked hot spot):**
> - `trade_attribution`: replace the 4 per-series `astype("float64").replace([float("inf"),float("-inf")],float("nan")).fillna(0.0)` passes (gross/cost/slip/net) plus the net_return `replace`+`fillna` with one finite-repair pass per column, preserving index/columns/dtypes/values exactly.
> - `attribution_totals`: replace the 4 per-series `.replace([inf,-inf],nan).fillna(0.0).sum()` passes with a single finite-repair before summing; keep the zero-gross guard and missing-column defaults unchanged.
> - No math/API change; no locked hot spot reopened (`beta.py`, `signals.py`, `portfolio.construct_portfolio`, `portfolio.enforce_beta_neutrality`, `backtest.run_backtest` semantics, `strategy.py` finiteness guard all stay locked).
>
> **Correctness proof (oracle/regression tests, `rtol=atol=1e-12`):** add a `TestAttributionSanitizationParity` class (≥6 tests) to `tests/test_bab_attribution.py` mirroring `TestFinalSanitizationParity`:
> - new single-pass transform == old `replace([inf,-inf],nan).fillna(0.0)` on a non-finite multi-column frame (index/columns/dtypes exact, all-finite output)
> - all-finite input → identity (fast-path, no spurious change)
> - empty frame preserved; None / non-DataFrame → empty frame with `ATTRIBUTION_COLUMNS`
> - E2E `BABStrategy.run(...).report()` / `tear_sheet()` with NaN/inf/-inf injected into the backtest frame → finite attribution frame + finite totals
> - attribution identities at `rtol=atol=1e-12`: `net_return == gross_return - cost_drag - slippage_drag`; `slippage_drag == turnover * slippage`
> - defensive fallback wired (force the primary numpy path to raise, verify the `replace(...).fillna(0.0)` fallback still yields finite output)
> **Zero new test failures introduced.**
>
> **Measurement (before → after, warm medians):** `BABStrategy.report()` / `tear_sheet()` / `attribution_totals` on a 2500×120 run; record `enforce_beta_neutrality` lock medians (must remain ~21.6/32.3/58.6 ms, no regression) and the attribution path delta. The win is removing 8 redundant full-pandas sanitize passes for any non-finite cell.
>
> **Validation:** `tests/test_bab_attribution.py tests/test_bab_attribution_extra.py tests/test_bab_attribution_extra2.py` + lock suites `tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → all passed. Full gate `bash scripts/bab_gate.sh` → **RC=0** (record pass/skip/RC/time).
>
> **Session exit requirements (mandatory):**
> 1. Targeted tests for `attribution.py`, then `bash scripts/bab_gate.sh` → RC=0 (record pass/skip/RC/time).
> 2. Record per-stage before/after warm medians + delta, or evidenced no-win with next action taken.
> 3. Refresh `HANDOFF.md`: timestamp, HEAD, gate result, shipped changes, remaining candidates/status.
> 4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
> 5. Commit nothing unless explicitly requested (the controller checkpoints).
>
> **Anti-churn / execution rules (binding):** ship code + measured win + oracle/regression tests + green gate + recorded deltas; no re-profiling old baselines except before/after for code you change; no probe-count campaigns; no reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`); no weakening/deleting the protected test files listed in the Locks/prohibitions section.
>
> **Session exit requirements:** targeted tests for changed code ✓; full gate run once ✓ (RC=1 solely due to the 3 pre-existing failures above); before/after deltas recorded ✓; this file + `AGENT_HANDOFF.md` refreshed ✓. Commit nothing unless explicitly requested.

---

## Evidence (current HEAD 856295d, refreshed 2026-11-13T14:21:40Z)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. `coverage`/`pytest-xdist` not installed.
- **Lock checks (this session):** `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile`
  - Before → After `enforce_beta_neutrality` (locked): 21.696/31.623/59.955 → 21.573/32.332/58.635 ms @2500x40/50/120; `run_backtest` 2.420/2.710/4.194 → 2.764/2.643/4.193 ms. cProfile confirms dominant time remains `portfolio.py:enforce_beta_neutrality` (locked; no regression).
- **Targeted lock tests:** `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **27 passed** (0.93s).
- **Impacted backtest suite + new parity tests:** `tests/test_bab_backtest_comprehensive.py` → **9 passed** (incl. 6 new `TestFinalSanitizationParity` tests). Combined 36 passed (0.90s).
- **E2E beta-neutral baseline (this session, `/home/runner/work/_temp/kilo-tmp/bench_bab_e2e_bn.py`, seed=1234, reps=12, warm):** `BABStrategy.run(beta_neutral=True)` 2500x40 **37.064 ms → 36.235 ms**, 2500x50 **44.282 ms → 45.868 ms**, 2500x120 **99.229 ms → 101.322 ms** (within noise; no regression).
- **Component medians @2500x120:** beta ~9.97 ms, signals ~19.42 ms, construct ~10.17 ms, enforce ~52.57 ms (locked), backtest ~4.00 ms. `strategy.py` finiteness guard already single-pass — not a target.
- **Last recorded full gate (prior context):** **5191 passed, 35 skipped, RC=0** (371.33s). **This session's full gate:** `bash scripts/bab_gate.sh` → **5196 passed, 35 skipped, RC=0, 372.07s** (green). The 3 previously pre-existing brittle failures (`test_finiteness_hardening_where_branch_repairs_nonfinite_arr`, `test_run_second_finiteness_pass_cleans_weights`, `test_run_finiteness_guard_exception_falls_back`) were realigned to the shipped single-pass implementations and now pass — the RC=1 bottleneck is removed. The lock suites pass (27 passed).
- **Historical note:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts (old SHAs/runs/tool noise); treat as historical diagnostics only, not current failures.

## Evidence (prior shipped cycle, retained for continuity)

- Oracle/perf hardening shipped: `tests/test_beta_neutrality_performance.py` covers randomized NaN/inf-heavy cases, ties/all-equal-beta, zero-row, all-NaN-beta, misaligned index/columns, single-row/column, explicit `correction=False`, index/column preservation at `rtol=atol=1e-12`; perf ceiling **0.25 s** for 2500x120. Targeted expansion suite previously: **124 passed** (1.10s). Full gate at that point: **5191 passed, 35 skipped, RC=0**.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.**
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block renormalization + net-fix retained for oracle fidelity. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass implementation verified this session (oracle/perf tests + targeted + full gate). **Locked unless regression evidenced.**
- `backtest.py` `run_backtest`: reuses `w_shifted` for turnover. **Not a meaningful target** (but downstream `beta_neutral=True` call chain remains in scope).
- `data_loader.py` `_run_data_quality_campaign`: vectorized stale-run scan.
- `scripts/bench_beta_neutrality.py` and `tests/test_beta_neutrality_performance.py` are the canonical bench/oracle-guard artifacts for this hot spot.

---

## Environment / bottlenecks (current)

- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage`/`pytest-xdist` missing.
- **Full gate ~372 s.** Do not run it after every edit; use targeted suites, then run gate once before recording.
- **No active blocker:** the RC=1 gate bottleneck is removed (3 brittle monkeypatch tests of superseded `strategy.py` finiteness internals realigned to the shipped single-pass guard; gate now **5196 passed, 35 skipped, RC=0**). Working tree: 2 modified (uncommitted) files at `a099c71`; no stashes/branches. Scratch: `/home/runner/work/_temp/kilo-tmp/`. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root. `research_state/workflow_run_diagnostics.jsonl` is historical CI log excerpts only (not current failures) — do not treat as blocker.
- **Bottleneck status:** the only identified redundant glue pass (`backtest.py` final `results.replace([inf,-inf],nan).fillna(0.0)` full-frame pandas sanitize) is **shipped and proven** — collapsed to a single numpy finite-repair pass with 1e-12 oracle parity. No further `backtest.py`/`strategy.py` glue targets remain without new evidence. `strategy.py` finiteness guard already single-pass — not a target unless new evidence. The next surface (`attribution.py`) is the pending INITIAL TASK above; it is NOT locked and NOT a blocker for this session.

---

## Anti-churn / execution rules (binding)

- **Ship code, not commentary:** progress = measured win + oracle/regression tests + green gate + recorded deltas.
- **No** re-profiling old recorded baselines except as before/after measurements for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
- If a stage yields no measurable win after a genuine implementation attempt, document evidence and immediately move to the next stage; do not stop the session.

---

## Session exit requirements (mandatory)

1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0 (record pass/skip/RC/time).
2. Record per-stage before/after warm medians + delta, or evidenced no-win with next action taken.
3. Refresh this file: timestamp, HEAD, gate result, shipped changes, remaining candidates/status.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested (the controller checkpoints).

---

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---

**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
