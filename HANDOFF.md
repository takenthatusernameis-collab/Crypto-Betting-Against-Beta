# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T20:25:30Z
**HEAD at refresh:** `c5a58e4e0d63fc9b2d428b8002482b685a561759` (`chore(kilo): checkpoint agent session`, 2026-11-12, `main`)
**Code state:** C52 adds 1 proven fix in allowed surface `strategies/betting_against_beta/cli.py` (`_extract_cumulative`: DataFrame without recognized cumulative/cum column now returns last scalar instead of whole frame to avoid ambiguous truth value; falls back to returning frame only when scalar extraction impossible) + regression `tests/test_bab_cli_c52_regressions.py` (2 tests). Working tree (tracked) at refresh: modified `HANDOFF.md`, `AGENT_HANDOFF.md`, `strategies/betting_against_beta/cli.py`; untracked `tests/test_bab_cli_c52_regressions.py` (intended C52 regression, uncommitted). Untracked `/home/runner/work/_temp/kilo-tmp/c52_{probes,gates}/` artifacts must not be committed.
**Env (verified):** Python 3.12.3, Linux, repo root `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`; run commands from repo root with `PYTHONPATH=.`; deps importable (`numpy,pandas,scipy,pytest,hypothesis,coverage`).

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` pointer-only. No parallel TODO/session handoff files.
- **HEAD drift is benign:** tracked baseline at session start was `c5a58e4`; C52 work done on that checkout (handoff/docs + allowed fix + regression only).
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts; treat as historical, not evidence of current-checkout failure, and never as justification for inaction/"blocked".
- **Env/blockers cleared (this session):** deps importable; Python 3.12.3; preflight `git rev-parse HEAD` = `c5a58e4`, clean tracked tree at start, deps OK.
- **C49–C51 closed and recorded (do not reopen without new reproducible failure + durable evidence):** C49 67/67 gates green (2 fixes), C50 60/60 probes/gates green, C51 60/60 probes (1 expected SKIP pyarrow)/gates green.
- **C52 CLOSED CLEAN.** 43/43 adversarial probes PASS (C52-012 initially exposed proven gap, fixed + regression added, rerun PASS). All 3 gates executed and GREEN 2026-11-12 with durable logs under `/home/runner/work/_temp/kilo-tmp/c52_gates/`. Probe artifacts under `/home/runner/work/_temp/kilo-tmp/c52_probes/`.
- **Gate invocation:** run from repo root with `PYTHONPATH=.`; G1 uses explicit `tests/test_bab_data_loader_campaign_d*` file list + batch148/149/172; save timestamped durable logs under `/home/runner/work/_temp/kilo-tmp/c<NN>_gates/`; always capture final summary + `rc`.
- **Gate 3 filenames (verified):** `test_bab_cli_campaign11ab_cli_surfaces.py`, `test_bab_cli_campaign11m_probe_regressions.py`, `test_bab_cli_campaign11n_expanded_probe_regressions.py`, `test_bab_cli_campaign11o_remaining_probe_regressions.py`, `test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py`, `test_bab_cli_campaign11q_followup_probe_regressions.py`, `test_bab_cli_campaign11s_validation_edges.py`, `test_bab_cli_campaign14_cli_reporting.py`.
- **C53 has not been started.** Start immediately per binding initial task message below.

## Gate status (C52, executed 2026-11-12 @ HEAD c5a58e4 + C52 fix)

| Gate | Status | Evidence / notes | Command | Log |
|---|---|---|---|---|
| 1 | **GREEN** | 898 passed, 5 skipped, 53 warnings, rc=0 | explicit `tests/test_bab_data_loader_campaign_d*.py` + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | `/home/runner/work/_temp/kilo-tmp/c52_gates/gate1_20261112T195030Z.log` (rc=0) |
| 2 | **GREEN** | 2265 passed, 5 skipped, 41 warnings, rc=0 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `/home/runner/work/_temp/kilo-tmp/c52_gates/gate2_20261112T195818Z.log` (rc=0) |
| 3 | **GREEN** | 164 passed in 161.37s, rc=0 | campaign11ab/11m/11n/11o/11p/11q/11s/14 CLI bundle (8 files, verified names) | `/home/runner/work/_temp/kilo-tmp/c52_gates/gate3_20261112T202050Z.log` (rc=0) |

## C52 — probes, fixes, evidence
- **Workspace:** `/home/runner/work/_temp/kilo-tmp/c52_probes/` (runner, per-probe logs `C52-001..043.log`, `runner.log`, `c52_probe_summary.json`, `c52_probe_summary.md`) and `/home/runner/work/_temp/kilo-tmp/c52_gates/`.
- **Probes:** 43 NEW adversarial probes (fresh C52 shapes, no C40–C51 reuse): `cli.py` (`--version/--help`, dry-run/output validation incl. directory/outside-allowed/overwrite, `--data` dir, universe whitespace/dups/empty-token, numeric parse/inf, `_json_safe`/`_json_default` nested numpy/pandas/NaN/Inf, `_extract_cumulative`/`_build_output_summary`/`_coerce_finite_scalar`/`_validate_rebalance_freq` edges, dry-run real-data CSV, `--from-prices` without data, invalid rebalance); `quality.py` (constant/all-nan/inf/zero-row/dup+NaT/extreme, detect gaps/outliers zscore+iqr/stale, None/strict-adjacent checks); `data_sources.py`/`DataCache` (LRU evict/mutation safety/overwrite/missing, `DataFrameDataSource`, `CSVDataSource` empty-file behavior); `costs.py` (basic non-negative, None/empty, negative-fee rejection, NaN weights + impact/borrow/adv); `regime.py` (vol/trend/state with constant col); `shorting.py` (borrowable + per-asset/total caps); `sizing.py` (Kelly/VolTarget/EqualWeight/risk_parity string); `attribution.py` (totals/empty, NaN/inf sanitization); `metrics.py` guarded (constant/empty/NaN-heavy, summary).
- **Result:** **43/43 PASS** after fix/rerun.
- **Proven gap (fixed):** `cli._extract_cumulative` returned whole DataFrame when backtest had columns but no `cumulative`/`cum` column, causing ambiguous truth value / non-scalar downstream risk (C52-012). **Fix:** prefer last scalar `iloc[-1,-1]` for such DataFrames; if extraction impossible fall back to returning frame (preserves prior fallback contract for malformed fakes that lack usable iloc/shape). File: `strategies/betting_against_beta/cli.py`. Regression: `tests/test_bab_cli_c52_regressions.py` (2 tests). Rerun C52-012 PASS; targeted existing CLI suites 100 passed / 1 failed (pre-fix expectation mismatch) -> updated logic, 3 passed after adjustment.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42–C48:** CLOSED (historical).
- **C49:** **CLOSED CLEAN** — 67/67 PASS, gates 3/3 GREEN, 2 proven gaps fixed with 7 regression tests.
- **C50:** **CLOSED CLEAN** — 60/60 PASS probes, 3/3 gates GREEN, no fixes required.
- **C51:** **CLOSED CLEAN** — 60/60 PASS probes (1 expected SKIP pyarrow), 3/3 gates GREEN, no fixes required.
- **C52:** **CLOSED CLEAN** — 43/43 PASS probes, 1 proven gap fixed + 2 regressions, 3/3 gates GREEN.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, execute now — refreshed 2026-11-12T20:25:30Z @ HEAD c5a58e4)

**Priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

**Current state:** C52 CLOSED CLEAN (43/43 probes PASS, 1 fix + regressions, gates 3/3 GREEN: G1 898p/5s rc=0, G2 2265p/5s rc=0, G3 164p rc=0). Tracked working tree has C52 fix/handoff edits + untracked `tests/test_bab_cli_c52_regressions.py`; deps importable. **C53 has not been started.**

**Campaign C53 (binding, start immediately — do not declare complete until gates green):**

**Preflight (verify first, record on exit):**
```bash
git rev-parse HEAD
git status --short
python3 -c "import numpy,pandas,scipy,pytest,hypothesis,coverage; print('deps ok')"
```
Run from repo root with `PYTHONPATH=.`

**Immediate execution (in order — heavy working, no planning-only):**
1. **Create durable probe workspace:** `/home/runner/work/_temp/kilo-tmp/c53_probes/` and `/home/runner/work/_temp/kilo-tmp/c53_gates/`. All probe scripts, per-probe logs (`C53-NNN.log`), runner output, and `c53_probe_summary.{json,md}` must live there (untracked). Do not reuse C40–C52 shapes/ids.
2. **Author and execute >=40 NEW adversarial probes (C53 shapes only)** targeting **not-yet-exhausted / cross-cutting edges** across allowed surfaces, with concrete reproducible inputs and durable per-probe pass/fail evidence:
   - **`cli.py`**: `_run_strategy`/`_extract_cumulative`/`_build_output_summary`/`_json_safe`/`_json_default` with adversarial `BABResult` shapes not covered by C52 (e.g. backtest as DataFrame with cumulative column but non-scalar iloc[-1] object, multiindex columns/index, ndarray cumulative, nested pandas objects in summary fields, `_coerce_finite_scalar` with numpy/pandas NA-like scalars/Decimal-like strings); `--output` to path in cwd subdir that becomes read-only? (probe allowed dirs semantics) / existing symlink-like?; `--dry-run` with `--from-prices` + invalid price schema / min_rows edge; universe containing only benchmark token after cleaning (if reachable) and duplicate+case variants as strings; ensure `main` never crashes on strategy returning malformed non-standard result objects (subprocess probes with monkeypatched module via `-c` only if isolated/untracked).
   - **`quality.py`**: `data_quality_report`/`compute_quality` with mixed tz-aware/naive DatetimeIndex (coercion boundaries), object columns mixing numbers/strings/None, extremely sparse frames, duplicate column names behavior, `detect_gaps` with unsorted index / NaT-heavy / freq-infer edge, `detect_outliers` on constant-zero-with-one-spike, `check_data_quality(strict=True)` paths.
   - **`data_sources.py`/`DataCache`**: `max_entries<=0`/1 behaviors, non-DataFrame payload storage/get copy semantics, key collision/overwrite ordering, source `load` kwargs passthrough (e.g. HDF5 key) and error surfaces for missing files (probe-only unless proven product gap).
   - **`costs.py`/`regime.py`/`shorting.py`/`sizing.py`**: empty/misaligned indices+columns combos, NaN/inf in intermediate inputs, zero-length windows, boundary params (e.g. borrow/impact caps, volatility windows, participation caps), strict/unborrowable interactions — **probe for proven bugs only**; smallest fix in editable surface if reproducible.
   - **`attribution.py`/`metrics.py` (guarded areas)**: mismatched/duplicate columns & indices, all-zero weights/returns, empty frames/series, non-float dtypes; respect existing C49 guards — do not weaken.
   - Prefer subprocess/isolated probes for CLI and import/runpy edges; keep probes untracked.
3. **Triage:** classify each result as **pass / expected-fail (current contract) / proven gap**. For every proven gap: apply the **smallest fix in allowed editable surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`) + add minimal regression tests `tests/test_bab_*_c53_regressions.py` (or narrowest appropriate existing test module only if clearly justified) + re-run affected tests.
4. **Run all 3 gates (mandatory before exit) — durable logs under `/home/runner/work/_temp/kilo-tmp/c53_gates/`:**
   - **Gate 1:** `PYTHONPATH=. python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
   - **Gate 2:** `PYTHONPATH=. python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
   - **Gate 3:** `PYTHONPATH=. python3 -m pytest -q tests/test_bab_cli_campaign11ab_cli_surfaces.py tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py tests/test_bab_cli_campaign11q_followup_probe_regressions.py tests/test_bab_cli_campaign11s_validation_edges.py tests/test_bab_cli_campaign14_cli_reporting.py` (use actual filenames present in `tests/`; record final list used)
   Capture final summary + `rc` for each.
5. **If all gates GREEN and no proven gaps remain:** record C53 CLOSED CLEAN here and set the next binding campaign to **C54** with the same heavy-execution bar (>=40 new adversarial probes on fresh shapes/surfaces, durable evidence, gates) — do not leave a planning-only state.
6. **On any gate failure/proven gap:** smallest allowed fix + regression + full gate re-run; do not exit until state is durably recorded with evidence and a concrete next action.

**Before exit (mandatory):** all 3 gates GREEN with timestamped logs; refresh this file (timestamp/HEAD, gate results+log paths+rc, C53 probe matrix/summary/fixes or "no proven gaps", next binding campaign C54 or concrete blocker with evidence, working-tree notes including untracked regressions); keep `AGENT_HANDOFF.md` pointer-only. No planning-only exit. No commit/push unless explicitly requested. Do not revert intentional changes.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py` (body), `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`. (Probes may exercise behavior; any fix must be the smallest proven one and only in these if strictly necessary and evidenced — prefer allowed surfaces.)
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes (notably `metrics.py` C49 guards, `tests/test_bab_metrics_c49_regressions.py`, C52 `cli.py` fix and `tests/test_bab_cli_c52_regressions.py`).
