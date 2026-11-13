# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T13:32:15Z
**HEAD (at refresh):** `c5b271c` — `chore(kilo): checkpoint agent session`
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

---

## State reconciliation (handoff refresh, 2026-11-13T13:32:15Z)

Repo prioritized by name (**Crypto-Betting-Against-Beta**) → next focus is BAB engine correctness/perf hardening in the end-to-end `beta_neutral=True` run path (core strategy value). Tree is clean at `c5b271c` (no uncommitted code changes in this refresh). `research_state/workflow_run_diagnostics.jsonl` is **historical CI log excerpts only** (old SHAs/tool noise/collection issues in past runs) — not current-checkout failures; do not reopen as blockers.

**Lock checks (this refresh, current checkout):**
- Env: python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0 (`coverage`/`pytest-xdist` absent).
- `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile` (warm medians): enforce 2500x40 **20.241 ms** (19.745/21.935), 2500x50 **28.590 ms** (27.883/32.257), 2500x120 **55.128 ms** (53.110/62.235); construct ~2.44/3.05/5.80 ms; run_backtest ~2.44/3.28/4.17 ms. Profile hot spot remains `portfolio.py:enforce_beta_neutrality` (locked).
- `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **27 passed** (0.83s).
- Last recorded full gate (prior context): **5191 passed, 35 skipped, RC=0**. Not rerun in this handoff-only refresh.

**E2E beta-neutral baselines (this refresh, current checkout, `/home/runner/work/_temp/kilo-tmp/bench_bab_e2e_bn.py`, seed=1234, reps=12, warm):** `BABStrategy.run(beta_neutral=True)` 2500x40 **37.199 ms** (33.122/50.771), 2500x50 **45.437 ms** (41.486/53.225), 2500x120 **95.680 ms** (87.116/108.183).

**Component medians @2500x120 (single-component bench, current checkout):** `calculate_rolling_beta` ~9.97 ms, `generate_bab_signals` ~19.42 ms, `construct_portfolio` ~10.17 ms, `enforce_beta_neutrality` ~52.57 ms (locked), `run_backtest` ~4.00 ms. `strategy.py:381-404` finiteness guard is **already single-pass** in current HEAD (prior target satisfied) — do not churn it without new evidence.

**Remaining legal campaign surface (evidence-based):** integration/allocation glue only — primarily `backtest.py` redundant pandas passes (e.g. final `results.replace([np.inf,-np.inf], np.nan).fillna(0.0)` sanitization is a full-frame pandas pass after cumulative/column construction; can be collapsed to a single numpy finite-pass over the result buffer with **provably identical** semantics/index/columns/dtypes behavior) and any other provably-redundant clean/convert/alignment work in BN call chain (`strategy.py`/`backtest.py`) without changing math/API. Locked: `beta.py`, `signals.py`, `construct_portfolio`, `enforce_beta_neutrality`, core `run_backtest` P&L/cost/turnover semantics.

---

> ## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T13:32:15Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN)
>
> **Objective:** Ship a **measured, correctness-proven** E2E `beta_neutral=True` `BABStrategy.run` improvement/hardening at 2500×120 by optimizing `backtest.py` + call-chain glue (no reopening locked hot spots).
>
> **Non-negotiable constraints:** Do **not** reopen `beta.py`, `signals.py`, shipped `construct_portfolio`, `enforce_beta_neutrality`, or core `run_backtest` semantics/math without a **new reproducible regression + evidence**. No probe-count churn, no "no reduction identified" artifacts, no reopening historical diagnostics, no `data_loader.py` broad silent-except sweep, no weakening perf/oracle tests/gates.
>
> **Execute in order (minimum expected work):**
> 1. **Lock checks (quick, once):** `python3 -c "import numpy,pandas,scipy,pytest; print(...)"`; `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile`; `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py`. Confirm in-family with this handoff (~20/29/55 ms enforce-only; ~37/45/96 ms E2E BN on this host class). If regressed, fix with evidence before other work.
> 2. **Implement (code, not just profiling):** target `strategies/betting_against_beta/backtest.py` final sanitization/allocation passes (primary: replace final `results.replace([np.inf,-np.inf], np.nan).fillna(0.0)` with a single finite-repair pass over result values preserving index/columns/dtypes/values exactly, including NaN/inf behavior) and any other provably-safe redundant work in BN glue. Keep `strategy.py` finiteness guard as-is unless a proven win. Use reproducible before/after E2E bench in `/home/runner/work/_temp/kilo-tmp/`.
> 3. **Correctness proof:** add/update targeted oracle/regression tests for every changed behavior path (NaN/inf/-inf in returns/weights/cost paths, index/column preservation, cumulative/drag/turnover parity) with `rtol=atol=1e-12` where numerical parity is claimed. Do not weaken existing assertions or 0.25s enforce perf ceiling.
> 4. **Validation:** run smallest relevant targeted suites (must include impacted backtest/BAB tests + lock suites when affected), iterate, then `bash scripts/bab_gate.sh` once at end → **RC=0** (record pass/skip/RC/time).
> 5. **Record + handoff:** update this file with timestamp, HEAD, exact before/after warm medians (enforce + E2E BN @2500x40/50/120), deltas, what changed/disproven, gate result, remaining best next candidate. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
>
> **Fallback ladder (if a concrete attempt yields no safe/measurable win):** record measured numbers and attempted diff, **revert non-winning code**, then execute the next concrete fix in the same campaign (e.g. other `backtest.py` redundant casts/alignment or safe `strategy.py` glue) with tests — **do not stop at profiling**.
>
> **Session incomplete until:** code change(s) attempted with evidence, oracle/regression proof for any change, targeted tests + full gate RC=0, and before/after deltas recorded here. No commit unless explicitly requested.

---

## Evidence (current HEAD, refreshed 2026-11-13T13:32:15Z)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. `coverage`/`pytest-xdist` not installed.
- **Lock checks (this refresh):** `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35 --profile`
  - 2500x40: `enforce_beta_neutrality` **20.241 ms** (min 19.745 / max 21.935), construct 2.439 ms, run_backtest 2.435 ms
  - 2500x50: `enforce_beta_neutrality` **28.590 ms** (min 27.883 / max 32.257), construct 3.048 ms, run_backtest 3.277 ms
  - 2500x120: `enforce_beta_neutrality` **55.128 ms** (min 53.110 / max 62.235), construct 5.800 ms, run_backtest 4.170 ms
  - cProfile confirms dominant time remains in `portfolio.py:enforce_beta_neutrality` (locked hot spot; no regression evidence).
- **Targeted lock tests:** `PYTHONPATH="$PWD" python3 -m pytest -q tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → **27 passed** (0.83s).
- **E2E beta-neutral baseline (this refresh, `/home/runner/work/_temp/kilo-tmp/bench_bab_e2e_bn.py`, seed=1234, reps=12, warm):** `BABStrategy.run(beta_neutral=True)` 2500x40 **37.199 ms** (33.122/50.771), 2500x50 **45.437 ms** (41.486/53.225), 2500x120 **95.680 ms** (87.116/108.183).
- **Component medians @2500x120 (single-component bench):** beta ~9.97 ms, signals ~19.42 ms, construct ~10.17 ms, enforce ~52.57 ms (locked), backtest ~4.00 ms. `strategy.py` finiteness guard already single-pass in HEAD c5b271c.
- **Last recorded full gate (prior context):** `bash scripts/bab_gate.sh` → **5191 passed, 35 skipped, RC=0** (371.33s). Not rerun in this handoff-only refresh.
- **Historical note:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts (old SHAs/runs/tool noise); treat as historical diagnostics only, not current failures. Working tree clean.

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
- **Full gate ~371 s (prior observed).** Do not run it after every edit; use targeted suites, then run gate once before recording.
- **No active blocker:** working tree clean at `c5b271c`, no stashes/branches noted. Scratch: `/home/runner/work/_temp/kilo-tmp/`. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root. `research_state/workflow_run_diagnostics.jsonl` is historical CI log excerpts only (not current failures) — do not treat as blocker.
- **Removable bottleneck (next campaign):** `backtest.py` final `results.replace([np.inf,-np.inf], np.nan).fillna(0.0)` is a full-frame pandas pass; replace with provably-equivalent single finite-repair pass (and audit other redundant cleans/casts/alignment in BN path) with oracle parity + measured before/after. `strategy.py` finiteness guard already single-pass — not a target unless new evidence.

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
