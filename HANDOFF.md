# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T14:04:48Z (refreshed; next session starts here)
- **Repo:** `Crypto-Betting-Against-Beta` (prioritized: ship a credible crypto Betting-Against-Beta research→backtest→ops workflow with deterministic offline defaults, dry-run-safe live execution, and gateable quality)
- **Git HEAD (verified this refresh):** `9bb93e7` (`chore(kilo): checkpoint agent session`, `main...origin/main`)
- **Working tree:** clean (`git status --porcelain -b` shows only branch line) at refresh before this edit.
- **Toolchain (verified this runner):** `python3 3.12.3`; `ruff 0.17.5`; runtime/test deps installed (`numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt`). `ruff check .` clean. **Env/bootstrap bottleneck REMOVED.**

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T14:04:48Z UTC) — BINDING (DO NOT IGNORE)

You are the next agentic worker on **Crypto-Betting-Against-Beta**. Your job is **heavy, measurable progress** toward a release-ready crypto BAB pipeline (research correctness, backtest realism hooks, ops/CLI safety, and gate-level coverage). This is the **only** active task list. Follow top-down. **No archaeology** (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), **no new parallel handoff/session docs**, **no “analysis-only” ending**.

### Hard rules (non-negotiable)
- **A session that ends without new tests/code AND fresh gate evidence is a FAILED session.** If something is externally blocked, record the exact command + output and continue with the next unblocked item—never stop at analysis.
- Preserve **byte-identical default offline/deterministic behavior** and **live execution is dry-run-safe-by-default** (env-only creds, no implicit network). **No real (non-dry-run) live execution, no network, no credentials** in tests.
- Prefer small, tested diffs. Do not “re-litigate” P11 unless a regression appears.
- **Single durable handoff:** only `HANDOFF.md` is canonical; keep `AGENT_HANDOFF.md` pointer-only.

### Repo-prioritized mission (inferred from name `Crypto-Betting-Against-Beta`)
Make the repo unambiguously useful and shippable for crypto BAB:
1. **Correctness & determinism:** offline/synthetic paths stable; rolling-beta/BAB signal semantics unchanged unless a bug is proven (with test).
2. **Ops readiness:** CLI + config paths documented by behavior (tests as contract), paper/live paths remain **dry-run-safe-by-default**.
3. **Coverage + gates:** close remaining real gaps on lowest-covered production modules (P12), drive **TOTAL coverage to ≥ 96%** with **zero** regressions, full gate green with fresh evidence.
4. **No dead-end work:** every step ends with commands run and results recorded in this file.

### Current verified state (this refresh)
- **Git:** `9bb93e7` (`chore(kilo): checkpoint agent session`, `main...origin/main`), working tree clean.
- **Fresh quick preflight (2026-11-15T14:04Z UTC, this runner):**
  - `bash scripts/bab_quick.sh` → **ruff clean**; targeted trio **104 passed** (1.39s); smoke (strategy/cli/costs) **195 passed** (16.77s); `== quick preflight OK ==`
- **Baseline full-gate evidence (carried forward, baseline-to-preserve; RECONFIRM after each P12 slice and at end):** prior full run at commit `48f4be5` recorded **5931 passed, 35 skipped in ~554.86s, TOTAL 95% (340 missed)**, ruff clean, `perf_baseline --check` `failures: []`. Live state is `4484697` (checkpoint commit); treat carried numbers as “last known good” until you produce fresh full-gate output.
- **P12 status:** **UNSTARTED** — no `tests/*p12*` files present. P11 coverage files exist (`test_bab_*_p11_coverage.py`) and are not the current target except “no regression”.

### Per-file coverage baseline (carried from prior full gate at `48f4be5`; re-measure in every full gate you run)

| Module | Cover (prior) | Miss | Gate-missed lines (missing) |
|--------|---------------|------|------------------------------|
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

## Immediate execution order (mandatory, heavy work first)
0. **Env/toolchain — DONE.** Do not reopen unless a command fails; if it fails, fix deps in the same session and record output.
1. **Baseline sanity (fast):** `bash scripts/bab_quick.sh` (must stay green). Then proceed.
2. **Data prerequisite for step 7 smokes (do once, before final verification):** `mkdir -p data` (repo root `data/` is absent this refresh; the CLI smoke in step 7 writes `data/crypto_returns.csv`). Creating the directory is sufficient; the smoke command generates the file itself.
3. **P12-A — `strategy.py` orchestration branches (HEAVY, do FIRST).** Create `tests/test_bab_strategy_p12_coverage.py`.
   - Cover real missed orchestration branches with synthetic data + fakes/mocks only (no network): non-daily `rebalance_freq` (688), `shorting_constraints` error/apply (712–721), `position_sizer` dict/normalize/apply/error (727–742), `regime_filter` scaling path (747–752), beta-neutral enforcement incl. tracking-error tolerance (759–772), finite-guard cleanup (790–798). Also gaps 280–283, 285, 298–301, 306, 643, 646–647, 655, 982–983 as applicable.
   - **Do not** modify production logic except the smallest bugfix proven by a new failing test (rare). Assert observable behavior.
   - Target: `strategy.py` **≥ 93%** under full gate.
4. **P12-B — `beta.py` rolling fast paths (HEAVY).** Create `tests/test_bab_beta_p12_coverage.py`.
   - Cover 1D/2D `_rolling_sum_finite` (315–328), `_rolling_sum_finite_stack` (372–386), `_rolling_sum` finite/NaN paths (125, 150–151, 163, 170–171, 189, 216–219), 435–436, 544–558. Prove semantic equivalence to reference behavior on finite/NaN/window/min-period inputs (property-style assertions ok).
   - Target: `beta.py` **≥ 92%** under full gate.
5. **P12-C — `backtest.py` error/edge paths (MEDIUM).** Create `tests/test_bab_backtest_p12_coverage.py` for 15–21, 27–30, 161–189. Target **≥ 90%**.
6. **P12-D — `risk.py` and `data_sources.py` final gaps (MEDIUM).** Add focused cases for `risk.py` 55–56,90,93,104,164,223–227,242–245,326–328,347,353,356,525,566–568,583–584,589,599–600 (target **≥ 93%**) and `data_sources.py` 236–237,311,320–324,376–378,424,476–508 (target **≥ 95%**). Fakes/mocks only; public API opt-in, dry-run-safe.
7. **Optional only if trivial/safe (do NOT churn):** `cli.py` 589–590,746–748,803–804; `config.py` 173; `metrics.py` 94,139–145; `signals.py` 37,75. Migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` only if semantics identical and covered.
8. **Final verification + handoff refresh (REQUIRED):** run in order: `python3 -m ruff check .`, `bash scripts/bab_quick.sh`, full `bash scripts/bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (must be `failures: []`), then paper/live dry-run CLI smokes:
   - `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --n-days 60 --csv data/crypto_returns.csv --benchmark BTC`
   - `python3 -m strategies.betting_against_beta.cli --source live --live-dry-run --health-check-only --exchange kraken --benchmark BTC --universe "BTC,ETH,ADA,SOL"`
   Update this file with new UTC timestamp, HEAD, exact command evidence, **per-file coverage delta vs table above**, remaining gaps, and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

**Cadence:** run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P12 step (A→B→C→D) and at the end.

## Definition of Done (session not done until ALL hold)
1. New P12 test files for steps completed exist and pass.
2. `python3 -m ruff check .` clean.
3. `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**, TOTAL **≥ 96%**.
4. Per-file coverage meets targets with **no regression** on any previously-green module.
5. `python3 scripts/perf_baseline.py --check` → `failures: []`.
6. Paper (`--dry-run --synthetic`) + live `--dry-run` health-check smokes pass.
7. This `HANDOFF.md` refreshed (and `AGENT_HANDOFF.md` pointer-only) with fresh evidence.

## Hard targets / acceptance
- `ruff check .` clean.
- `bash scripts/bab_gate.sh`: 0 failed, 0 errors.
- No regression elsewhere; targets: `strategy.py ≥ 93%`, `beta.py ≥ 92%`, `backtest.py ≥ 90%`, `risk.py ≥ 93%`, `data_sources.py ≥ 95%`, **TOTAL ≥ 96%**.
- `perf_baseline --check` `failures: []`.
- Dry-run CLIs pass as above.
- Default offline/deterministic unchanged; live dry-run-safe-by-default.

## Bottlenecks removed / constraints (do not reopen)
- Env/bootstrap: **REMOVED** (ruff + deps installed this environment; quick green verified). If missing in a new env, install with `python3 -m pip install --quiet -e ".[test,live]" ruff` and record.
- Gate speed: `scripts/bab_gate.sh` parallel (`pytest-xdist`, loadscope, sysmon on CPython≥3.12), serial fallback via `BAB_GATE_SERIAL=1` / `BAB_GATE_JOBS=N`. Do not make gate serial-only by default.
- Parallel-safety: follow `_*_cell_record`/`_*_records_full` patterns in stress/realism tests; summary tests must recompute deterministically under any worker subset.
- Historical noise: ignore root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli`.
- Safety: no real live trading, no network, no credentials in tests. Live defaults to dry-run/health-check only.

## Protocol (for this session and every next session)
1. Read this file fully (and `AGENT_HANDOFF.md` pointer only).
2. Run `bash scripts/bab_quick.sh`; if red, fix before feature work.
3. Execute P12 A→B→C→D top-down with minimal tested diffs; create only named P12 test files unless absolutely necessary (justify in commit message/body notes in this file if you do).
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run full verification suite above and rewrite this file’s “Current verified state”, tables/deltas, and the new INITIAL TASK MESSAGE timestamp if you hand off again (otherwise keep this timestamp but update evidence sections accurately).
