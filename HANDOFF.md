# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T13:02:01Z
**HEAD:** `c138353` — `chore: capture completed workflow run diagnostics` (latest commit on `main`; checkout not re-verified as clean by a fresh commit in this session).
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

**State reconciliation (this session):** prior handoff (`2026-11-13T11:44Z`, `e5dc8ce`) stated `enforce_beta_neutrality` optimization/scaffold work was pending. Current checkout now contains `scripts/bench_beta_neutrality.py`, `tests/test_beta_neutrality_performance.py`, and a vectorized masked-pass implementation in `strategies/betting_against_beta/portfolio.py:enforce_beta_neutrality`. **No benchmark, targeted tests, or full gate were re-run in this session** (deps were missing at start), so oracle equivalence, performance win, and gate health at `c138353` are **unverified here** and must be proven before claiming completion.

**Historical gate baselines (as previously recorded, not re-run now):**
- 2026-11-13T11:35Z @ `e5dc8ce`: `bash scripts/bab_gate.sh` → 5173 passed / 35 skipped / RC=0 (303.59s).
- 2026-11-13T11:42Z @ `e5dc8ce` (+oracle guard): 5182 passed / 35 skipped / RC=0 (304.58s).
- 2026-11-13T11:44Z bench @ `e5dc8ce`: 2500×40 209.5 ms, 2500×50 212.3 ms, 2500×120 244.9 ms (`enforce_beta_neutrality`, warm medians).

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T13:02:01Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN):
>
> **Mission:** **Verify, harden, and close** the `enforce_beta_neutrality` optimization at HEAD. The vectorized implementation and perf/oracle scaffolding appear present in-tree but are **not yet evidenced at `c138353`**. Do **not** reopen `beta.py`, `signals.py`, or shipped `construct_portfolio`/`run_backtest` without a new reproducible regression + evidence.
>
> **Required execution (complete in this order):**
> 1. **Install/confirm deps and reproduce baseline now (before changing code):**
>    `python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"`
>    `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35`
>    `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --profile`
>    Record warm medians (min/max) and profile tottime/call counts. Scratch in `/home/runner/work/_temp/kilo-tmp/`.
> 2. **Validate current implementation against contract:** `strategies/betting_against_beta/portfolio.py:enforce_beta_neutrality` must preserve all semantics: `s2_centered < 1e-18` skip, `denom < 1e-18` break, `|port_beta - target| <= tol` break, `correction=False` no-op, same up-to-50-pass convergence, NaN/inf cleaning, index/column alignment/intersection, non-finite-target/tolerance handling, and unused params (`max_drift`, tracking-error args) remain behavior-compatible/unused as today. If any divergence is found, fix it with the smallest oracle-equivalent change.
> 3. **Prove oracle equivalence at 1e-12:** extend `tests/test_beta_neutrality_performance.py` as needed to cover randomized NaN/inf, tie/all-equal-beta, zero-row, all-NaN-beta, misaligned index/columns, single-row/column, and explicit `correction=False` cases. Require `rtol=atol=1e-12` and identical index/columns. Do not weaken existing assertions or the existing perf guard without evidence.
> 4. **Performance closeout:** if the current vectorization is a real win (target: materially below prior ~210–250 ms, ideally >3× at 2500×120), **tighten** the CI-stable perf ceiling in `tests/test_beta_neutrality_performance.py` to the achieved safe bound (e.g. `< 0.08 s` only if demonstrated with margin on this runner). If no measurable win or parity is unstable, document numbers, revert non-winning code, and move down the fallback ladder (do not stop).
> 5. **Targeted tests (iterate fast):**
>    `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py tests/test_bab_portfolio_coverage_campaign.py tests/test_bab_portfolio_coverage_campaign3.py tests/test_bab_portfolio_uncovered_branches.py tests/test_bab_signals_portfolio_edgecases.py`
> 6. **Full gate (once, at end):** `bash scripts/bab_gate.sh` → must be **RC=0**. Record pass/skip/RC/time.
> 7. **Record evidence in this file:** before/after warm medians + deltas, profile before/after, what changed, what was disproven, remaining candidates. Refresh timestamp/HEAD/gate/shipped/status. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
>
> **Fallback ladder (if verification shows no win or correctness issues that cannot be fixed safely):** document the numbers, **revert the non-winning/incorrect change**, then profile `BABStrategy.run` end-to-end with `beta_neutral=True` at 2500×120 for redundant DataFrame copies/reindex/`to_numpy` passes in `strategy.py:364+`. Do **not** stop at profiling. Do **not** reopen historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
>
> **Session is incomplete until:** benchmarked baseline is recorded at current HEAD, oracle equivalence is proven at 1e-12 (or a regression fixed), a tightened/safe perf ceiling is in place, targeted tests + full gate are RC=0, and before/after deltas/status are recorded here.

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