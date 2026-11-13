# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T13:19:24Z
**HEAD:** `674fc28` — `chore(kilo): checkpoint agent session` (working tree clean; committed checkpoint).
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

---

## State reconciliation (this session)

The `enforce_beta_neutrality` hot spot in `strategies/betting_against_beta/portfolio.py` is **verified/closed for this cycle**: vectorized masked-pass implementation present, oracle strengthened (randomized NaN/inf, tie/all-equal-beta, zero-row, all-NaN-beta, misaligned index/columns, single-row/column, explicit `correction=False`, index/column preservation) at `rtol=atol=1e-12`, perf ceiling tightened to **0.25 s**. Baseline warm medians: 2500x40 ~21.7 ms, 2500x50 ~20.9 ms, 2500x120 ~63.7 ms. Targeted suites green (124 passed). Full gate **5191 passed, 35 skipped, RC=0** (371.33s). **No uncommitted changes.**

The closed hot spot is NOT the next target. Next real work must move to the **end-to-end `beta_neutral=True` path efficiency/correctness beyond this hot spot** — `BABStrategy.run` at 2500×120, targeting redundant DataFrame copies/reindex/`to_numpy` passes and avoidable alignment work in `strategy.py:~364+` and the call chain (including `backtest.py` lag/cost/slippage passes). Preserve oracle semantics and public API/contract.

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T13:19:24Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN):
>
> **Mission:** Preserve and build on the closed `enforce_beta_neutrality` milestone. Do **not** reopen `beta.py`, `signals.py`, shipped `construct_portfolio`, `run_backtest`, or `enforce_beta_neutrality` without a **new reproducible regression + evidence**. The next campaign is end-to-end `beta_neutral=True` `BABStrategy.run` efficiency/correctness at 2500×120.
>
> **Required execution (complete in this order):**
> 1. **Sanity/lock checks (before changing code):**
>    - `python3 -c "import numpy,pandas,scipy,pytest; print(numpy.__version__, pandas.__version__, scipy.__version__, pytest.__version__)"`
>    - `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile` (confirm no regression vs recorded medians; warm medians should remain ~21–22 ms @2500x40, ~21 ms @2500x50, ~63–65 ms @2500x120).
>    - `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` (must pass; do not weaken assertions/ceilings without measured evidence).
> 2. **New performance campaign (code work, not profiling-only):** profile and optimize `BABStrategy.run` end-to-end with `beta_neutral=True` at 2500×120 (create/use a reproducible bench script under `/home/runner/work/_temp/kilo-tmp/` unless a tracked bench is warranted). Target redundant DataFrame copies/reindex/`to_numpy` passes and avoidable alignment work in `strategy.py:~364+` region and call chain — e.g. the finiteness guard's double `weights.to_numpy(dtype=float)` pass (`strategy.py:381-404`) collapsible to one pass, redundant Series extraction (`strategy.py:363`), and `backtest.py` repeated `.replace`/`.fillna`/`.to_numpy`/shift allocations. Preserve oracle semantics and public API/contract.
> 3. **Prove correctness:** add/update targeted oracle/regression tests for any changed path (include alignment, NaN/inf, and neutrality behavior where applicable) with `rtol=atol=1e-12` for numerical parity claims. Do not weaken existing assertions or locked perf guards.
> 4. **Targeted tests (iterate fast):** run the smallest relevant set covering changed modules (include `tests/test_beta_neutrality_performance.py` and `tests/test_bab_beta_neutrality.py` if touched/affected), then broaden only as needed.
> 5. **Full gate (once, at end):** `bash scripts/bab_gate.sh` → must be **RC=0**. Record pass/skip/RC/time.
> 6. **Record evidence in this file:** before/after warm medians + deltas/profile findings, what changed, what was disproven, remaining candidates. Refresh timestamp/HEAD/gate/shipped/status. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
>
> **Fallback ladder (if no safe/measurable end-to-end win):** document numbers and attempted changes, **revert non-winning code**, then investigate next-largest measurable cost in `beta_neutral=True` run path (e.g. repeated beta/signal/weight alignment or downstream portfolio application) with a concrete fix + tests. Do **not** stop at profiling. Do **not** reopen locked hot paths, `data_loader.py` broad silent-except sweep, or historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) without new reproducible defect + evidence.
>
> **Session is incomplete until:** baseline/evidence is recorded for work done, any code change has oracle/regression proof, targeted tests + full gate are RC=0, and before/after deltas/status are recorded here.

---

## Evidence (this session, 2026-11-13)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. `coverage` and `pytest-xdist` not installed.
- **Baseline benchmark (HEAD state):** `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35`
  - 2500x40: `enforce_beta_neutrality` 21.702 ms (min 21.108/max 35.015), construct 2.233 ms, run_backtest 2.773 ms
  - 2500x50: 20.898 ms (min 20.545/max 24.257), construct 2.197 ms, run_backtest 2.980 ms
  - 2500x120: 63.726 ms (min 62.302/max 76.769), construct 6.223 ms, run_backtest 4.678 ms
- **Profile (`--profile`, reps 10 subset):** dominant time inside `strategies/betting_against_beta/portfolio.py:enforce_beta_neutrality` (~0.112s tottime of 0.134s for 2 calls @2500x120 in sampled profile run), with numpy reductions/copies and pandas alignment/replace overhead present but much reduced vs historical notes.
- **Oracle/perf work shipped in tests:** `tests/test_beta_neutrality_performance.py` expanded to cover randomized NaN/inf-heavy cases, tie/all-equal-beta, zero-row, all-NaN-beta, misaligned index/columns, single-row/column, explicit `correction=False`, and index/column preservation at `rtol=atol=1e-12`; perf ceiling tightened from 1.5 s to **0.25 s** for 2500x120 workload (large margin vs ~64 ms baseline).
- **Targeted tests:** `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py tests/test_bab_portfolio_coverage_campaign.py tests/test_bab_portfolio_coverage_campaign3.py tests/test_bab_portfolio_uncovered_branches.py tests/test_bab_signals_portfolio_edgecases.py` → **124 passed** (1.10s).
- **Full gate:** `bash scripts/bab_gate.sh` → **5191 passed, 35 skipped, RC=0** (371.33s / 0:06:11). `coverage` not installed (suite ran without coverage report).
- **Not run:** end-to-end `beta_neutral=True` strategy profiling/optimization (next campaign).

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
- **Full gate ~371 s (observed this session).** Do not run it after every edit; use targeted suites, then run gate once before recording.
- **No active blocker:** no stashes/branches noted. Working tree clean. Scratch: `/home/runner/work/_temp/kilo-tmp/`. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root.
- **Removable bottleneck (next campaign):** `strategy.py:381-404` finiteness guard does `weights.to_numpy(dtype=float)` twice plus `weights.iloc[:] = wa` write — collapsible to a single pass; `strategy.py:363` redundant Series extraction; `backtest.py` repeated alignment/cleaning passes. Attack these with measured before/after.

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
