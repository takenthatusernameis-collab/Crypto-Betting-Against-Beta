# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T11:44:00Z
**HEAD:** `e5dc8ce` — prior session's `construct_portfolio` broadcast-product work is **committed**; tree was clean at handoff start (this refresh adds only the handoff/benchmark/oracle-guard files).
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

**Gate baseline (verified 2026-11-13T11:35Z at `e5dc8ce`):** `bash scripts/bab_gate.sh` → **5173 passed, 35 skipped, RC=0** (303.59s, python 3.12.3; `coverage` not installed → no coverage report). **Re-run with the new oracle guard (2026-11-13T11:42Z):** **5182 passed, 35 skipped, RC=0** (304.58s).

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T11:44:00Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN):
>
> **Mission:** Ship a **vectorized, oracle-equivalent `enforce_beta_neutrality`** in `strategies/betting_against_beta/portfolio.py:232-346`. This is the dominant remaining hot spot by a wide margin. The per-row Python loop (line 307, up to 50 inner iterations) costs **~208–249 ms** at production scale, while `run_backtest` is **~1.7–2.7 ms** and `construct_portfolio` is **~1.8–3.0 ms**. Do **not** spend the session on `run_backtest`; it is noise next to this stage.
>
> **Why this is the target (fresh measurements, 2026-11-13T11:35Z, warm medians, 15 reps):**
>
> | Stage | 2500×40 | 2500×50 | 2500×120 |
> |---|---|---|---|
> | `enforce_beta_neutrality` | **212.9 ms** | **215.3 ms** | **249.2 ms** |
> | `construct_portfolio` | 1.83 ms | 2.18 ms | 2.95 ms |
> | `run_backtest` | 1.67 ms | 1.78 ms | 2.67 ms |
>
> cProfile at 2500×120 (20 reps): the function body is **4.29 s tottime of 6.83 s total**, with ~735k `np.sum` calls — the 50-pass Python loop dominates. It is called from `strategy.py:364` whenever `beta_neutral=True` / `beta_neutral_enforcement=True`; at production scale it dominates the pipeline (249 ms vs ~2–3 ms for the other stages).
>
> **Required execution (complete in this order):**
> 1. **Reproduce the baseline now:**
>    `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35`
>    `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --profile`
>    Record the numbers. Scratch goes in `/home/runner/work/_temp/kilo-tmp/`.
> 2. **Implement one materially different optimization:** replace the per-row loop with a 2-D vectorized correction over the `(n_rows, n_assets)` arrays. Precompute per row: finite-beta mask, `b_mean`, `centered = b_f - b_mean`, `s2_centered`; then run the same up-to-50-pass update over all rows with an **active-row mask**. Preserve every break condition exactly: `s2_centered < 1e-18` skip, `denom < 1e-18` break, `|port_beta - target| <= tol` break, `correction=False` no-op. Preserve the public signature, index/column alignment, non-finite cleaning, and unused-parameter behavior (`max_drift`, tracking-error args are currently unused — keep them unused).
> 3. **Prove oracle equivalence:** `tests/test_beta_neutrality_performance.py` already contains `_reference_enforce` (the row-wise oracle) and randomized cases. Extend it with randomized NaN/inf/tie/all-equal-beta/zero-row/all-NaN-beta/misaligned-index cases. Require `rtol=atol=1e-12` and identical index/columns. Add an explicit `correction=False` case.
> 4. **Add/adjust a CI-stable perf ceiling** for the optimized path, then **tighten it to the achieved win** (e.g. `< 0.08 s` at 2500×120 if you reach >3×). The existing ceiling is `< 1.5 s` and is only a non-regression guard, not the win.
> 5. **Targeted tests** (fast, use during iteration):
>    `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py tests/test_bab_portfolio_coverage_campaign.py tests/test_bab_portfolio_coverage_campaign3.py tests/test_bab_portfolio_uncovered_branches.py tests/test_bab_signals_portfolio_edgecases.py`
> 6. **Full gate:** `bash scripts/bab_gate.sh` → must be **RC=0**. Record pass/skip/RC/time (full gate is ~5 min; run it once at the end, not after every edit).
> 7. **Record evidence in this file:** before/after warm medians + deltas, profile before/after, what changed, what was disproven, remaining candidates. Refresh the timestamp/HEAD/gate/shipped/status. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
>
> **Fallback ladder (if no measurable win after a genuine attempt):** document the numbers, **revert the non-winning code**, and move to the next stage: profile `BABStrategy.run` end-to-end with `beta_neutral=True` at 2500×120 for redundant DataFrame copies/reindex/`to_numpy` passes in `strategy.py`. Do **not** stop at profiling. Do **not** reopen `beta.py`, `signals.py`, or the shipped `construct_portfolio` broadcast product without a new reproducible regression + evidence.
>
> **Session is incomplete until:** a real vectorized implementation is attempted, oracle equivalence is proven at 1e-12, a tightened perf ceiling exists and holds, the full gate is RC=0, and before/after deltas are recorded here.

## SHIPPED / SCAFFOLDED (do NOT reopen without new evidence)
- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.**
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book (committed at `e5dc8ce`); DN both-block renormalization + net-fix retained for oracle fidelity. **Locked.**
- `backtest.py` `run_backtest`: reuses `w_shifted` for turnover. Measured 1.7–2.7 ms — **not a meaningful target**.
- `data_loader.py` `_run_data_quality_campaign`: vectorized stale-run scan.
- **This refresh:** `scripts/bench_beta_neutrality.py` (reproducible production-scale benchmark) and `tests/test_beta_neutrality_performance.py` (row-wise oracle + randomized equivalence + perf guard). These are scaffolding, not the optimization; the next session must still ship the vectorized win.

## Environment / bottlenecks (current)
- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage` **not installed** (gate still runs, without a coverage report). `pytest-xdist` **not installed** (full gate is serial).
- **Full gate ~303 s.** Do not run it after every edit; use the targeted command above, then run the gate once before recording.
- **No active blocker:** HEAD `e5dc8ce`, no stashes, no extra branches, tree clean at handoff start. The previous handoff's "dirty tree / HEAD `314f433`" note was stale and has been corrected.
- **Scratch:** `/home/runner/work/_temp/kilo-tmp/`. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root.

## Anti-churn / execution rules (binding)
- **Ship code, not commentary:** progress = measured win + oracle tests + tightened perf ceiling + green gate + recorded deltas.
- **No** re-profiling old recorded baselines except as before/after measurements for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
- If a stage yields no measurable win after a genuine implementation attempt, document evidence and immediately move to the next stage; do not stop the session.

## Session exit requirements (mandatory)
1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0 (record pass/skip/RC/time).
2. Record per-stage before/after warm medians + delta, or evidenced no-win with next action taken.
3. Refresh this file: timestamp, HEAD, gate result, shipped changes, remaining candidates/status.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested (the controller checkpoints).

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**