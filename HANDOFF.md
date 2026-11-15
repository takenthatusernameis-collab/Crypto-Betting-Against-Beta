# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T13:34:02Z (refreshed; next session starts here)
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified this refresh):** `3e5e39b` (`chore(kilo): checkpoint agent session`, `main`)
- **Working tree:** clean at refresh (`git status --porcelain` empty).
- **Toolchain (verified present):** `python3` 3.12.3, `pytest 9.2.0`, `pytest-xdist`, `pytest-cov`, `coverage 7.17.3`, `numpy 2.5.4`/`pandas 3.1.1`/`scipy`/`hypothesis`/`ccxt`. `ruff 0.17.5` available as **`python3 -m ruff`** (bare `ruff` may be missing from `$PATH`; use module form). CLI `bab 0.1.0`.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T13:34:02Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **A session that ends without new tests/code and fresh gate evidence is a FAILED session.** If an item is externally blocked, record the exact command+output and continue with the next unblocked item — never stop at analysis.

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close the remaining real coverage gaps on the lowest-covered production modules (P12) and drive TOTAL coverage to **≥ 96%** with **zero** regressions. Heavy, real work only: new tests must assert observable behavior, not smoke imports.

### Current state at HEAD `3e5e39b` (verified this session, 2026-11-15T13:34Z)

- `python3 -m ruff check .` → **clean** (exit 0, verified this refresh).
- `bash scripts/bab_quick.sh` → **green** (targeted trio **104 passed** 1.75s; smoke **195 passed** 24.85s; verified this refresh).
- `bash scripts/bab_gate.sh` (full, parallel `jobs=4`, coverage sysmon) → **green at `48f4be5`**: **5931 passed, 35 skipped in 554.86s (0:09:14), `TOTAL 95%` (340 missed)**. `3e5e39b` changed only `AGENT_HANDOFF.md`/`HANDOFF.md`; no code/test delta since `48f4be5`, so this gate evidence still holds. Re-confirm with a full gate at the end of the next session.
- `python3 scripts/perf_baseline.py --check` → **`failures: []`** (verified at `48f4be5`; do not re-baseline).
- CLI smokes (verified at `48f4be5`, exit 0): `--synthetic --dry-run` prints resolved config; `--adapter live --health-check` → `{"mode":"live","exchange":"binance","connected":false,"dry_run":true,"testnet":false,"connector_type":null,"n_submitted":0,"n_fills":0}`.
- Bottlenecks: **none blocking** observed at refresh (clean tree; ruff + quick green; full gate green at prior HEAD). Use `scripts/bab_quick.sh` for the inner loop; budget ~9 min for a full `scripts/bab_gate.sh` after each P12 slice. Historical root `probe_*/debug/ast_probe` files are noise — do not touch. No new parallel handoff docs. Live execution remains dry-run-safe-by-default only; no network/credentials in tests.

Per-file coverage baseline (verified full-gate at `48f4be5`, 2026-11-15T13:31Z):

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

P11 test files present: `tests/test_bab_cli_p11_coverage.py`, `tests/test_bab_data_sources_p11_coverage.py`, `tests/test_bab_reconciliation_p11_coverage.py`, `tests/test_bab_execution_p11_coverage.py` (all passing).

**Conclusion of prior P11:** the P11 acceptance targets (execution ≥92%, data_sources ≥90%, reconciliation ≥90%, cli ≥90%, TOTAL ≥93%) are all met. **P11 is DONE. Do not re-run or extend it.** The next campaign is P12, and it is **unstarted** — no `*_p12_*.py` test file exists at HEAD `3e5e39b`.

## Immediate execution order (mandatory)

0. **Toolchain/PATH:** use `python3 -m ruff check .` if bare `ruff` is unavailable. Keep `PYTHONPATH=$PWD` for ad-hoc pytest when needed.
1. **Re-confirm baseline (fast, do this first every session):** `python3 -m ruff check .` + `bash scripts/bab_quick.sh`. If either is red, fix with minimal diffs before adding coverage.
2. **P12-A — `strategy.py` orchestration branches (HEAVY, do FIRST):** create `tests/test_bab_strategy_p12_coverage.py`. Cover the real gate-missed orchestration branches reachable with synthetic data + fakes only: non-daily `rebalance_freq` (line 688), `shorting_constraints` error/apply (712-721), `position_sizer` dict/normalize/apply/error (727-742), `regime_filter` scaling path (747-752), beta-neutral enforcement incl. tracking-error tolerance (759-772), and the finite-guard cleanup (790-798). Also cover `_safe_float` defaults (643, 646-647) and the remaining early gaps (280-283, 285, 298-301, 306, 655, 982-983). Do not modify production logic; assert observable behavior. Target `strategy.py` **≥ 93%** under full gate.
3. **P12-B — `beta.py` rolling fast-path variants (HEAVY):** extend/create `tests/test_bab_beta_p12_coverage.py` for the uncovered rolling-sum/median fast paths and validation edges: 1-D and 2-D `_rolling_sum_finite` (315-328), `_rolling_sum_finite_stack` (372-386), `_rolling_sum` finite/NaN paths (125, 150-151, 163, 170-171, 189, 216-219), and 435-436, 544-558. Prove semantic equivalence to the reference path on finite/NaN/window/min-period inputs (property-style assertions, not smoke). Target `beta.py` **≥ 92%** under full gate.
4. **P12-C — `backtest.py` error/edge paths (MEDIUM):** extend/create `tests/test_bab_backtest_p12_coverage.py` for lines 15-21, 27-30, 161-189 (cost/slippage/lag/empty-window/validation errors). Target `backtest.py` **≥ 90%** under full gate.
5. **P12-D — `risk.py` and `data_sources.py` final gaps (MEDIUM):** add focused cases for `risk.py` lines 55-56, 90, 93, 104, 164, 223-227, 242-245, 326-328, 347, 353, 356, 525, 566-568, 583-584, 589, 599-600 (target **≥ 93%**) and `data_sources.py` 236-237, 311, 320-324, 376-378, 424, 476-508 (target **≥ 95%**). Use fakes/mocks only; keep public API opt-in and dry-run-safe.
6. **Optional only if trivial/safe (do NOT chase churn):** `cli.py` 589-590, 746-748, 803-804; `config.py` 173; `metrics.py` 94, 139-145; `signals.py` 37, 75. Migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` only when semantics identical and covered.
7. **Final verification + handoff refresh (REQUIRED, not optional):** re-run `python3 -m ruff check .`, `bash scripts/bab_quick.sh`, full `bash scripts/bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (`failures: []`), and paper/live dry-run CLI smokes. Update this file with new UTC timestamp, HEAD, exact evidence, and **per-file coverage delta vs the table above**, remaining gaps (if any), and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

Run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P12 step (A→B→C→D) and at the end.

## Definition of Done (a session is not done until ALL hold)

1. New P12 test files (A/B/C/D as applicable) exist and pass.
2. `python3 -m ruff check .` clean.
3. `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**, TOTAL **≥ 96%**.
4. Per-file coverage meets the targets below with **no regression** on any previously-green module.
5. `python3 scripts/perf_baseline.py --check` → `failures: []`.
6. Paper (`--dry-run --synthetic`) + live `--dry-run` health-check smokes pass.
7. This `HANDOFF.md` refreshed with new timestamp/HEAD/evidence + coverage delta; `AGENT_HANDOFF.md` still pointer-only.

## Hard targets / acceptance (must all hold)

- `python3 -m ruff check .` clean.
- `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**.
- Per-file coverage (no regression elsewhere): `strategy.py` **≥ 93%**, `beta.py` **≥ 92%**, `backtest.py` **≥ 90%**, `risk.py` **≥ 93%**, `data_sources.py` **≥ 95%**; all previously-green modules must not regress.
- **TOTAL ≥ 96%**.
- `python3 scripts/perf_baseline.py --check` → `failures: []`.
- Paper (`--dry-run --synthetic`) + live `--dry-run` health-check smokes pass.
- Default offline/deterministic behavior unchanged; live path remains dry-run-safe-by-default; **no real (non-dry-run) live execution, no network, no credentials**.

## Bottlenecks removed / constraints (do not reopen)

- **No blocked bottlenecks observed at refresh (2026-11-15T13:34Z, HEAD 3e5e39b):** tree clean; `ruff` and `bab_quick.sh` green this refresh; full `bab_gate.sh` green at `48f4be5` (docs-only delta since); perf baseline `failures: []`; dry-run smokes exit 0. Gate parallelized; use `bab_quick.sh` inner loop and budget ~9 min for full `bash scripts/bab_gate.sh` after each P12 slice. Do not stop at analysis.
- **Gate speed:** `scripts/bab_gate.sh` runs parallel (`pytest-xdist`, `--dist loadscope`, sysmon on CPython ≥3.12) with serial fallback (`BAB_GATE_SERIAL=1`, `BAB_GATE_JOBS=N`). Do not reintroduce serial-only gate or claim suite-timeout excuse.
- **Parallel-safety:** any new module-level record list must follow the `_*_cell_record`/`_*_records_full` pattern used in `tests/test_bab_execution_realism_r3.py`, `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py`. Summary tests must recompute deterministically under any worker subset.
- **Single durable handoff:** only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only.
- **Historical noise (no archaeology):** root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** real (non-dry-run) live execution out of scope; never enable without explicit opt-in and credential review. No network/credentials in tests. Live path dry-run-safe-by-default.
- **Do not re-run P11** (`*_p11_coverage.py` files) except to confirm they still pass; P11 acceptance is met.

## Protocol

1. Read this file fully.
2. Re-confirm baseline (ruff + quick). If red, fix first.
3. Execute P12 steps 2→3→4→5 top-down with minimal, tested diffs and gate evidence after each step; create/extend only the P12 test files named above.
4. Never stop at analysis; if blocked record exact command+output and continue unblocked work.
5. Refresh this file (and keep `AGENT_HANDOFF.md` pointer-only) before finishing.