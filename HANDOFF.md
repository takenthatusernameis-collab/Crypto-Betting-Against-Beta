# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T19:44:25Z
**HEAD at refresh:** `edcb965439340ecbc29984e0f52e34516bfe3f63` (`chore(kilo): checkpoint agent session`, 2026-11-12, `main`)
**Code state:** identical to `814f6a4` (diff vs `814f6a4` touches only `HANDOFF.md`/`AGENT_HANDOFF.md`). Working tree (tracked): clean at refresh. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log/gate artifacts exist and must not be committed.
**Env (verified):** Python 3.12.3, Linux, repo root `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`; run commands from repo root with `PYTHONPATH=.`; deps installed/importable in-session (`numpy,pandas,scipy,pytest,hypothesis,coverage`).

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` pointer-only. No parallel TODO/session handoff files.
- **HEAD drift is benign:** `edcb965` vs `814f6a4` changes only handoff docs; no code regression, no unblock needed. Tracked tree clean.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts from other runs/heads; treat as historical, not evidence of current-checkout failure, and never as justification for inaction/"blocked".
- **Env/blockers cleared (this session):** runtime deps were missing at session start — installed successfully; Python 3.12.3; tracked tree clean at HEAD `edcb965`. Preflight re-verified 2026-11-12T19:44:25Z: `import numpy,pandas,scipy,pytest,hypothesis,coverage` OK.
- **C49 closed and recorded:** 67/67 PASS, gates 3/3 GREEN, 2 proven fixes landed (`metrics.py` guards + `tests/test_bab_metrics_c49_regressions.py`, 7 tests). Do not revert.
- **C50 CLOSED CLEAN.** Probes previously recorded 60/60 PASS, 0 FAIL, no proven gaps (`2026-11-12T15:52:04Z` @ HEAD `2697e5e`). All 3 C50 gates executed and GREEN 2026-11-12 with durable logs under `/home/runner/work/_temp/kilo-tmp/c50_gates/`. No fixes/regressions required.
- **C51 CLOSED CLEAN.** Probes 60/60 PASS, 0 FAIL, 0 ERROR (1 expected SKIP: parquet/pyarrow not installed). All 3 C51 gates executed and GREEN 2026-11-12 with durable logs under `/home/runner/work/_temp/kilo-tmp/c51_gates/` (gate1 898p/5s rc=0, gate2 2263p/5s rc=0, gate3 164p rc=0). Probe artifacts + summary under `/home/runner/work/_temp/kilo-tmp/c51_probes/`. No fixes/regressions required.
- **Gate invocation:** run from repo root with `PYTHONPATH=.`; G1 uses explicit `tests/test_bab_data_loader_campaign_d*` file list + batch148/149/172; save timestamped durable logs under `/home/runner/work/_temp/kilo-tmp/c<NN>_gates/`; always capture final summary + `rc`.
- **Gate 3 filename note (corrected):** actual bundle files are `test_bab_cli_campaign11ab_cli_surfaces.py`, `test_bab_cli_campaign11m_probe_regressions.py`, `test_bab_cli_campaign11n_expanded_probe_regressions.py`, `test_bab_cli_campaign11o_remaining_probe_regressions.py`, `test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py`, `test_bab_cli_campaign11q_followup_probe_regressions.py`, `test_bab_cli_campaign11s_validation_edges.py`, `test_bab_cli_campaign14_cli_reporting.py` (use the verified names present in `tests/`).
- **C52 has not been started (no `c52_gates`/`c52_probes` artifacts).** Start immediately per the binding initial task message below.

## Gate status (C50, executed 2026-11-12 @ HEAD ae5e8c7)

| Gate | Status | Evidence / notes | Command | Log |
|---|---|---|---|---|
| 1 | **GREEN** | 898 passed, 5 skipped, 53 warnings, rc=0 | explicit `tests/test_bab_data_loader_campaign_d*.py` + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | `/home/runner/work/_temp/kilo-tmp/c50_gates/gate1_20261112T184245Z.log` (rc=0) |
| 2 | **GREEN** | 2263 passed, 5 skipped, 41 warnings, rc=0 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `/home/runner/work/_temp/kilo-tmp/c50_gates/gate2_20261112T190915Z.log` (rc=0) |
| 3 | **GREEN** | 164 passed in 174.35s, rc=0 | campaign11ab/11m/11n/11o/11p/11q/11s/14 CLI bundle (8 files, verified names) | `/home/runner/work/_temp/kilo-tmp/c50_gates/gate3_20261112T190915Z.log` (rc=0) |

## Gate status (C51, executed 2026-11-12 @ HEAD 814f6a4)

| Gate | Status | Evidence / notes | Command | Log |
|---|---|---|---|---|
| 1 | **GREEN** | 898 passed, 5 skipped, rc=0 | explicit `tests/test_bab_data_loader_campaign_d*.py` + batch148/149/172 | `/home/runner/work/_temp/kilo-tmp/c51_gates/gate1_20261112T193014Z.log` (rc=0) |
| 2 | **GREEN** | 2263 passed, 5 skipped, rc=0 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `/home/runner/work/_temp/kilo-tmp/c51_gates/gate2_20261112T193027Z.log` (rc=0) |
| 3 | **GREEN** | 164 passed in 161.80s, rc=0 | campaign11ab/11m/11n/11o/11p/11q/11s/14 CLI bundle (8 files, verified names) | `/home/runner/work/_temp/kilo-tmp/c51_gates/gate3_20261112T193749Z.log` (rc=0) |

## C50 (closed) — summary
- **Probes:** 60 NEW adversarial probes, **60/60 PASS, 0 FAIL, no proven gaps** (recorded `2026-11-12T15:52:04Z` @ HEAD `2697e5e`; per-probe logs/summary noted under `/home/runner/work/_temp/kilo-tmp/c50_probes/` in prior state). Surfaces covered (no C40–C49 reuse): `cli.py` reporting/serialization/arg edges incl. `_build_output_summary`, `_json_default`, `_json_safe`, `_extract_cumulative`, `--output`/dry-run/rebalance/universe/benchmark; `data_loader.py` adversarial edges (datetime/numeric coercion, dup dates, all-NaN, mixed tz, format round-trips where deps present, `min_rows`, benchmark cases); `quality.py` numeric/boundary paths; cross-interaction `costs/regime/shorting/sizing/attribution/portfolio/signals/backtest/beta/data_sources`.
- **Fixes/regressions:** none required.
- **Gates:** 3/3 GREEN (logs above).

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42–C48:** CLOSED (see prior history; C48 66/66, gates green).
- **C49:** **CLOSED CLEAN** — 67/67 PASS, gates 3/3 GREEN, 2 proven gaps fixed with 7 regression tests.
- **C50:** **CLOSED CLEAN** — 60/60 PASS probes, 3/3 gates GREEN, no fixes required.
- **C51:** **CLOSED CLEAN** — 60/60 PASS probes (1 expected SKIP pyarrow), 3/3 gates GREEN, no fixes required.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, execute now — refreshed 2026-11-12T19:44:25Z @ HEAD edcb965)

**Priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

**Current state:** C51 CLOSED CLEAN (probes 60/60 PASS, 1 expected SKIP pyarrow, gates 3/3 GREEN). Tracked tree clean at HEAD `edcb965` (code state = `814f6a4`). Deps installed in-session; ensure `numpy,pandas,scipy,pytest,hypothesis,coverage` importable before probing (install if missing — cleared bottleneck this session). **C52 has not been started.**

**Campaign C52 (binding, start immediately — do not declare complete until gates green):**

**Preflight (verify first, record on exit):**
```bash
git rev-parse HEAD
git status --short
python3 -c "import numpy,pandas,scipy,pytest,hypothesis,coverage; print('deps ok')"
```
Run from repo root with `PYTHONPATH=.`

**Immediate execution (in order — heavy working, no planning-only):**
1. **Create durable probe workspace:** `/home/runner/work/_temp/kilo-tmp/c52_probes/` and `/home/runner/work/_temp/kilo-tmp/c52_gates/`. All probe scripts, per-probe logs (`C52-NNN.log`), runner output, and `c52_probe_summary.{json,md}` must live there (untracked). Do not reuse C40–C51 shapes/ids.
2. **Author and execute >=40 NEW adversarial probes (C52 shapes only)** targeting **not-yet-exhausted / cross-cutting edges** across allowed surfaces, with concrete reproducible inputs and durable per-probe pass/fail evidence:
    - **`cli.py`**: `_run_strategy`/reporting paths when `strategy.run` returns objects with missing/odd attributes (e.g. no `backtest`, empty/None weights, non-DataFrame beta/signals/weights), `_json_safe` on deeply nested/mixed numpy scalars/NaT/Timestamp-like objects, `--output` overwrite of existing file vs directory edge, argument combinations that pass argparse but stress downstream validation (e.g. universe containing benchmark-only after normalization if applicable, whitespace/duplicate symbols), `--version`/help exit behavior isolation in subprocess probes, dry-run summary completeness with real-data-like fixtures.
    - **`quality.py`**: `data_quality_report`/`compute_quality` with all-constant columns, single-column frames, zero-row-after-drop cases, inf-only series, extreme magnitude values, index with NaT rows, object-dtype numeric strings.
    - **`data_sources.py`/`DataCache`**: cache key/expiry behavior, missing/empty fetch results, non-finite or non-numeric payload coercion boundaries, duplicate-key/overwrite semantics (probe-only unless proven product gap).
    - **`costs.py` / `regime.py` / `shorting.py` / `sizing.py`**: boundary combos not in C50/C51 (e.g. zero/negative-like guardable inputs where API permits, empty frames, misaligned indices/columns, NaN propagation, extreme rates/multipliers) — **probe for proven bugs only**; smallest fix in editable surface if reproducible.
    - **`attribution.py` / `metrics.py` (guarded areas)**: `trade_attribution`/`attribution_totals` with mismatched columns/indices, all-zero or all-NaN returns/weights, empty inputs; `metrics` functions on constant/empty/NaN-heavy series (respect existing C49 guards — do not weaken).
    - Prefer subprocess/isolated probes for CLI and import/runpy edges; keep probes untracked.
3. **Triage:** classify each result as **pass / expected-fail (current contract) / proven gap**. For every proven gap: apply the **smallest fix in allowed editable surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`) + add minimal regression tests `tests/test_bab_*_c52_regressions.py` (or the narrowest appropriate existing test module only if clearly justified) + re-run affected tests.
4. **Run all 3 gates (mandatory before exit) — durable logs under `/home/runner/work/_temp/kilo-tmp/c52_gates/`:**
    - **Gate 1:** `PYTHONPATH=. python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
    - **Gate 2:** `PYTHONPATH=. python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
    - **Gate 3:** `PYTHONPATH=. python3 -m pytest -q tests/test_bab_cli_campaign11ab_cli_surfaces.py tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py tests/test_bab_cli_campaign11q_followup_probe_regressions.py tests/test_bab_cli_campaign11s_validation_edges.py tests/test_bab_cli_campaign14_cli_reporting.py` (use actual filenames present in `tests/`; record final list used)
    Capture final summary + `rc` for each.
5. **If all gates GREEN and no proven gaps remain:** record C52 CLOSED CLEAN here and set the next binding campaign to **C53** with the same heavy-execution bar (>=40 new adversarial probes on fresh shapes/surfaces, durable evidence, gates) — do not leave a planning-only state.
6. **On any gate failure/proven gap:** smallest allowed fix + regression + full gate re-run; do not exit until state is durably recorded with evidence and a concrete next action.

**Before exit (mandatory):** all 3 gates GREEN with timestamped logs; refresh this file (timestamp/HEAD, gate results+log paths+rc, C52 probe matrix/summary/fixes or "no proven gaps", next binding campaign C53 or concrete blocker with evidence, working-tree notes); keep `AGENT_HANDOFF.md` pointer-only. No planning-only exit. No commit/push unless explicitly requested. Do not revert intentional changes.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py` (body), `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`. (Probes may exercise behavior; any fix must be the smallest proven one and only in these if strictly necessary and evidenced — prefer allowed surfaces.)
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes (notably `metrics.py` C49 guards and `tests/test_bab_metrics_c49_regressions.py`).
