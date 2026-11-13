# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T13:22:21Z
**HEAD (at refresh):** `aaa1494` — `chore(kilo): checkpoint agent session`
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

---

## State reconciliation (handoff refresh session, 2026-11-13T13:22:21Z)

`enforce_beta_neutrality` remains **verified/closed for this cycle** (no regression). Sanity/lock checks re-run on current HEAD:
- Env: python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0 (`coverage`/`pytest-xdist` absent).
- `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile` (warm medians): 2500x40 **21.538 ms** (21.538/20.822/28.904), 2500x50 **30.155 ms** (28.298/33.472), 2500x120 **57.767 ms** (56.704/59.378); construct ~2.3/2.8/5.9 ms; run_backtest ~2.74/2.97/4.69 ms. Profile hot spot remains inside `portfolio.py:enforce_beta_neutrality` (locked).
- `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **27 passed** (0.82s).
- Prior full gate on parent checkpoint context: **5191 passed, 35 skipped, RC=0** (371.33s). Not rerun this handoff-only refresh.

**Bottleneck diagnosis for next campaign (measured, 2500x120, beta_neutral=True, synthetic seed=1234):**
- End-to-end `BABStrategy.run(beta_neutral=True)` warm medians: 2500x40 **35.272 ms** (27.084/40.168), 2500x50 **45.309 ms** (34.463/52.950), 2500x120 **94.282 ms** (85.473/142.669) (`/home/runner/work/_temp/kilo-tmp/bench_bab_e2e_bn.py`).
- Single-run component breakdown @2500x120: `calculate_rolling_beta` ~18.29 ms, `generate_bab_signals` ~6.33 ms, `construct_portfolio` ~12.45 ms, `enforce_beta_neutrality` ~73.07 ms, finiteness guard (`strategy.py:381-404`) ~0.26 ms (small but easy single-pass cleanup), `run_backtest` ~6.69 ms; total parts ~117.09 ms (one sample).
- Locked hot paths (`beta.py`, `signals.py`, `construct_portfolio`, `enforce_beta_neutrality`, core backtest logic) must not be reopened without a **new reproducible regression + evidence**. The remaining legal campaign surface is integration/allocation work in `BABStrategy.run`/call-chain glue (e.g. collapse double finiteness `to_numpy`+`iloc` pass in `strategy.py:381-404` to one pass, remove redundant work/alignment/copies where provable, trim avoidable `backtest.py` cleaning/allocation passes without changing semantics) while preserving public API and oracle behavior.

This handoff removes the main session-start bottleneck: fresh lock-check baselines + E2E breakdown are recorded; next session must do **code+oracle+gate** work, not rediscover baselines. `research_state/workflow_run_diagnostics.jsonl` remains **historical CI log excerpts only** (not current-checkout failures). Working tree in this refresh includes handoff doc updates.

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T13:22:21Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN)
>
> **Objective:** Deliver a **measured, correctness-proven optimization or correctness hardening** in the end-to-end `beta_neutral=True` `BABStrategy.run` path at 2500×120, without reopening locked hot spots.
>
> **Non-negotiable constraints:** Do **not** reopen `beta.py`, `signals.py`, shipped `construct_portfolio`, `enforce_beta_neutrality`, or core `run_backtest` semantics without a **new reproducible regression + evidence**. No probe-count churn, no "no reduction identified" artifacts, no reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`), no `data_loader.py` broad silent-except sweep, no weakening perf/oracle tests.
>
> **Execute in order (minimum expected work):**
> 1. **Lock checks (quick, once):** `python3 -c "import numpy,pandas,scipy,pytest; print(...)"`; `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile`; `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py`. Confirm medians are in-family with this handoff (~21–22 ms @2500x40, ~30 ms @2500x50, ~58 ms @2500x120 for enforce-only on this host class; E2E BN run ~35/45/94 ms). If regressed, treat as blocker and fix with evidence before other work.
> 2. **Implement (code, not just profiling):** optimize `strategy.py` integration path for `beta_neutral=True` at 2500×120. Primary targets with existing evidence: collapse the finiteness guard double pass/write in `strategy.py:381-404` to a single safe pass (preserve current exception/fallback semantics and BABDataError surfacing), remove avoidable redundant allocations/copies/reindex/`to_numpy` in the BN run path and adjacent call chain (`strategy.py` glue, `backtest.py` repeated clean/convert passes) **only where semantics are provably unchanged**. Create/use a reproducible E2E bench under `/home/runner/work/_temp/kilo-tmp/` for before/after.
> 3. **Correctness proof:** add/update targeted oracle/regression tests for every changed behavior path (including NaN/inf/non-finite cleanup, alignment/index-column preservation, BN behavior as applicable) with `rtol=atol=1e-12` for numerical parity claims. Do not weaken existing assertions or the 0.25s enforce perf ceiling.
> 4. **Validation:** run smallest relevant targeted suites (must include `tests/test_beta_neutrality_performance.py` and `tests/test_bab_beta_neutrality.py` when affected), iterate, then run `bash scripts/bab_gate.sh` once at end → **RC=0** (record pass/skip/RC/time).
> 5. **Record + handoff:** update this file with timestamp, HEAD, exact before/after warm medians (enforce + E2E BN @2500x40/50/120), deltas, what changed/disproven, gate result, remaining best next candidate. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
>
> **Fallback ladder (if a concrete attempt yields no safe/measurable win):** record measured numbers and attempted diff, **revert non-winning code**, then execute the next concrete fix in the same campaign (e.g. `backtest.py` redundant `replace/fillna/to_numpy`/cast passes or alignment churn in BN E2E path) with tests — **do not stop at profiling**.
>
> **Session incomplete until:** code change(s) attempted with evidence, oracle/regression proof for any change, targeted tests + full gate RC=0, and before/after deltas recorded here. No commit unless explicitly requested.

---

## Evidence (current HEAD, refreshed 2026-11-13T13:22:21Z)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. `coverage`/`pytest-xdist` not installed.
- **Lock checks (this refresh):** `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile`
  - 2500x40: `enforce_beta_neutrality` **21.538 ms** (min 20.822 / max 28.904), construct 2.302 ms, run_backtest 2.737 ms
  - 2500x50: `enforce_beta_neutrality` **30.155 ms** (min 28.298 / max 33.472), construct 2.801 ms, run_backtest 2.973 ms
  - 2500x120: `enforce_beta_neutrality` **57.767 ms** (min 56.704 / max 59.378), construct 5.925 ms, run_backtest 4.686 ms
  - cProfile confirms dominant time remains in `portfolio.py:enforce_beta_neutrality` (locked hot spot; no regression evidence).
- **Targeted lock tests:** `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **27 passed** (0.82s).
- **E2E beta-neutral baseline (this refresh, `/home/runner/work/_temp/kilo-tmp/bench_bab_e2e_bn.py`, seed=1234, reps=12):** `BABStrategy.run(beta_neutral=True)` warm medians 2500x40 **35.272 ms** (27.084/40.168), 2500x50 **45.309 ms** (34.463/52.950), 2500x120 **94.282 ms** (85.473/142.669).
- **Component breakdown @2500x120 (single sample):** beta 18.29 ms, signals 6.33 ms, construct 12.45 ms, enforce 73.07 ms, finite-guard 0.26 ms, backtest 6.69 ms (parts total 117.09 ms). Note variance vs e2e median; use repeated warm medians for before/after claims.
- **Last recorded full gate (prior checkpoint context):** `bash scripts/bab_gate.sh` → **5191 passed, 35 skipped, RC=0** (371.33s). Not rerun in this handoff-only refresh.
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
