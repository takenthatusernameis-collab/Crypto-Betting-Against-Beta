# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T13:58:53Z (refreshed; next session starts here)
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified this refresh):** `ba33d5b` (`chore(kilo): checkpoint agent session`, `main...origin/main`)
- **Working tree:** clean at refresh before this handoff edit (`git status --porcelain -b` branch line only).
- **Toolchain (this runner, verified 2026-11-15T13:58Z):** `python3` 3.12.3; `ruff` 0.17.5; runtime/test deps (numpy/pandas/scipy/pytest/pytest-xdist/pytest-cov/hypothesis/ccxt) installed (`python3 -m pip install --quiet -e ".[test,live]" ruff`). **Env bootstrap bottleneck REMOVED.**

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T13:58:53Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **A session that ends without new tests/code and fresh gate evidence is a FAILED session.** If an item is externally blocked, record the exact command+output and continue with the next unblocked item — never stop at analysis.

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close the remaining real coverage gaps on the lowest-covered production modules (P12) and drive TOTAL coverage to **≥ 96%** with **zero** regressions. Heavy, real work only: new tests must assert observable behavior, not smoke imports.

### Current state at HEAD `ba33d5b` (verified this session, 2026-11-15T13:58Z UTC)

- **Git:** `ba33d5b` (`chore(kilo): checkpoint agent session`, `main...origin/main`), working tree clean at refresh. No `strategies/` or `tests/` code changes in recent checkpoint/diagnostics commits since prior full-gate baseline commit `48f4be5`.
- **Baseline verification in this runner (fresh evidence, env bootstrapped):**
  - `python3 -m ruff check .` → `All checks passed!` (ruff 0.17.5)
  - `python3 -c "import numpy, pandas, scipy, pytest, hypothesis, coverage, ccxt"` → `deps ok`
  - `bash scripts/bab_quick.sh` → ruff clean; targeted trio **104 passed**; smoke (strategy/cli/costs) **195 passed**; `== quick preflight OK ==`
- **Last known good full-gate evidence (carried forward, baseline-to-preserve):** at `48f4be5` full `bash scripts/bab_gate.sh` → **5931 passed, 35 skipped in 554.86s, TOTAL 95% (340 missed)**; `ruff` clean; `perf_baseline --check` `failures: []`. **Full gate must be re-confirmed with fresh evidence after each P12 slice and at session end.**
- **Bottlenecks (current):** P12 is **unstarted** — no `*_p12_*.py` tests exist. Historical root `probe_*.py`/`debug_*.py`/`ast_probe.py` are noise — do not touch. No new parallel handoff docs. Live execution remains dry-run-safe-by-default only; no network/credentials in tests.

Per-file coverage baseline (verified full-gate at `48f4be5`, 2026-11-15T13:31Z; carried forward — re-confirm after each P12 slice):

| Module | Cover | Miss | Gate-missed lines (missing) |
|--------|-------|------|------------------------------|
| `__init__.py` | 100% | 0 | — |
| `attribution.py` | 100% | 0 | — |
| `backtest.py` | **84%** | 23 | 15-21, 27-30, 161-189 |
| `beta.py` | **85%** | 57 | 125, 150-151, 163, 170-171, 189, 216-219, 315-328, 372-386, 435-436, 544-558 |
| `cli.py` | 99% | 7 | 589-590, 746-748, 803-804 |
| `config.py` | 99% | 1 | 173 |
| `costs.py` | 100% | 0 | — |
| `data.py` | 100% | 0 | — |
| `data_loader.py` | 97% | 62 | 100-101, 283-295, 299-300, 318-319, 373, 385-389, 453-454, 697-698, 749-750, 868-869, 1032, 1268, 1271-1272, 1391, 1636-1637, 1647, 1678-1679, 1684-1685, 1690-1692, 1702-1712, 1958-1959, 2742-2743, 2747, 2749-2750, 2756-2757, 2760-2761 |
| `data_sources.py` | **93%** | 21 | 236-237, 311, 320, 322, 324, 376-378, 424, 476-481, 484, 499-500, 507-508 |
| `errors.py` | 100% | 0 | — |
| `execution.py` | 94% | 45 | 139-141, 164-166, 177-178, 182-187, 380-381, 403-404, 463-464, 472-473, 479-480, 505-506, 555-556, 559-560, 783-784, 836-837, 847-848, 1047, 1281-1288, 1380-1381, 1386 |
| `metrics.py` | 98% | 4 | 94, 139, 142, 145 |
| `portfolio.py` | 95% | 11 | 152-153, 170-177, 180 |
| `quality.py` | 100% | 0 | — |
| `reconciliation.py` | **95%** | 10 | 78-79, 82-83, 112-113, 309, 377, 381, 385 |
| `regime.py` | 100% | 0 | — |
| `replay.py` | 92% | 11 | 172, 174, 205, 218-219, 234, 247-251 |
| `risk.py` | **89%** | 30 | 55-56, 90, 93, 104, 164, 223-227, 242-245, 326-328, 347, 353, 356, 525, 566-568, 583-584, 589, 599-600 |
| `shorting.py` | 100% | 0 | — |
| `signals.py` | 98% | 2 | 37, 75 |
| `sizing.py` | 100% | 0 | — |
| `strategy.py` | **88%** | 56 | 280-283, 285, 298-301, 306, 643, 646-647, 655, 688, 712-721, 727-742, 747-752, 759-772, 790-798, 982-983 |
| **TOTAL** | **95%** | 340 | — |

**P11 is DONE** (tests `test_bab_cli_p11_coverage.py`, `test_bab_data_sources_p11_coverage.py`, `test_bab_reconciliation_p11_coverage.py`, `test_bab_execution_p11_coverage.py` present; passed at prior gate). Do not re-run or extend P11 except to confirm no regression.

## Immediate execution order (mandatory)

0. **Bootstrap env/toolchain — DONE (this runner 2026-11-15T13:58Z):** `python3 -m pip install --quiet -e ".[test,live]" ruff`; verified `ruff check .` clean, deps importable, `bash scripts/bab_quick.sh` green (104+195 passed). Do not reopen.
1. **Baseline — CONFIRMED (quick):** proceed directly to P12-A. Full `bash scripts/bab_gate.sh` re-confirmation is required after each P12 slice and at the end.
2. **P12-A — `strategy.py` orchestration branches (HEAVY, do FIRST):** create `tests/test_bab_strategy_p12_coverage.py`. Cover real gate-missed orchestration branches reachable with synthetic data + fakes only: non-daily `rebalance_freq` (688), `shorting_constraints` error/apply (712-721), `position_sizer` dict/normalize/apply/error (727-742), `regime_filter` scaling path (747-752), beta-neutral enforcement incl. tracking-error tolerance (759-772), and finite-guard cleanup (790-798). Also cover `_safe_float` defaults (643, 646-647) and remaining early gaps (280-283, 285, 298-301, 306, 655, 982-983). Do not modify production logic; assert observable behavior. Target `strategy.py` **≥ 93%** under full gate.
3. **P12-B — `beta.py` rolling fast-path variants (HEAVY):** create `tests/test_bab_beta_p12_coverage.py` for uncovered rolling-sum/median fast paths and validation edges: 1-D and 2-D `_rolling_sum_finite` (315-328), `_rolling_sum_finite_stack` (372-386), `_rolling_sum` finite/NaN paths (125, 150-151, 163, 170-171, 189, 216-219), and 435-436, 544-558. Prove semantic equivalence to reference path on finite/NaN/window/min-period inputs (property-style assertions, not smoke). Target `beta.py` **≥ 92%** under full gate.
4. **P12-C — `backtest.py` error/edge paths (MEDIUM):** create `tests/test_bab_backtest_p12_coverage.py` for lines 15-21, 27-30, 161-189 (cost/slippage/lag/empty-window/validation errors). Target `backtest.py` **≥ 90%** under full gate.
5. **P12-D — `risk.py` and `data_sources.py` final gaps (MEDIUM):** add focused cases for `risk.py` lines 55-56, 90, 93, 104, 164, 223-227, 242-245, 326-328, 347, 353, 356, 525, 566-568, 583-584, 589, 599-600 (target **≥ 93%**) and `data_sources.py` 236-237, 311, 320-324, 376-378, 424, 476-508 (target **≥ 95%**). Use fakes/mocks only; keep public API opt-in and dry-run-safe.
6. **Optional only if trivial/safe (do NOT chase churn):** `cli.py` 589-590, 746-748, 803-804; `config.py` 173; `metrics.py` 94, 139-145; `signals.py` 37, 75. Migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` only when semantics identical and covered.
7. **Final verification + handoff refresh (REQUIRED):** re-run `python3 -m ruff check .`, `bash scripts/bab_quick.sh`, full `bash scripts/bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (`failures: []`), and paper/live dry-run CLI smokes. Update this file with new UTC timestamp, HEAD, exact evidence, and **per-file coverage delta vs the table above**, remaining gaps, and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

Run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P12 step (A→B→C→D) and at the end.

## Definition of Done (session not done until ALL hold)

1. New P12 test files (A/B/C/D as applicable) exist and pass.
2. `python3 -m ruff check .` clean.
3. `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**, TOTAL **≥ 96%**.
4. Per-file coverage meets targets with **no regression** on any previously-green module.
5. `python3 scripts/perf_baseline.py --check` → `failures: []`.
6. Paper (`--dry-run --synthetic`) + live `--dry-run` health-check smokes pass.
7. This `HANDOFF.md` refreshed with new timestamp/HEAD/evidence + coverage delta; `AGENT_HANDOFF.md` pointer-only.

## Hard targets / acceptance (must all hold)

- `python3 -m ruff check .` clean.
- `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**.
- Per-file coverage (no regression elsewhere): `strategy.py` **≥ 93%**, `beta.py` **≥ 92%**, `backtest.py` **≥ 90%**, `risk.py` **≥ 93%**, `data_sources.py` **≥ 95%**.
- **TOTAL ≥ 96%**.
- `python3 scripts/perf_baseline.py --check` → `failures: []`.
- Paper (`--dry-run --synthetic`) + live `--dry-run` health-check smokes pass.
- Default offline/deterministic behavior unchanged; live path dry-run-safe-by-default; **no real (non-dry-run) live execution, no network, no credentials**.

## Bottlenecks removed / constraints (do not reopen)

- **Env bootstrap (REMOVED 2026-11-15T13:58Z):** ruff 0.17.5 + runtime/test deps installed; ruff clean, deps ok, quick preflight green. Prior full-gate baseline `48f4be5` = 5931 passed, 35 skipped, TOTAL 95% (baseline-to-preserve). Budget ~9 min for full `bash scripts/bab_gate.sh`.
- **Gate speed:** `scripts/bab_gate.sh` parallel (`pytest-xdist`, `--dist loadscope`, sysmon on CPython ≥3.12) with serial fallback (`BAB_GATE_SERIAL=1`, `BAB_GATE_JOBS=N`). Do not reintroduce serial-only gate.
- **Parallel-safety:** any new module-level record list must follow `_*_cell_record`/`_*_records_full` pattern (see `tests/test_bab_execution_realism_r3.py`, `test_bab_stress_regimes.py`, `test_bab_stress_horizon.py`, `test_bab_scale_perf_guard.py`). Summary tests must recompute deterministically under any worker subset.
- **Single durable handoff:** only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only.
- **Historical noise (no archaeology):** root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** real (non-dry-run) live execution out of scope; never enable without explicit opt-in and credential review. No network/credentials in tests. Live path dry-run-safe-by-default.
- **Do not re-run P11** (`*_p11_coverage.py`) except to confirm no regression.

## Protocol

1. Read this file fully.
2. Baseline quick preflight is green (verified); if red, fix first.
3. Execute P12 steps 2→3→4→5 top-down with minimal, tested diffs and gate evidence after each step; create/extend only the P12 test files named above.
4. Never stop at analysis; if blocked record exact command+output and continue unblocked work.
5. Refresh this file (and keep `AGENT_HANDOFF.md` pointer-only) before finishing.
