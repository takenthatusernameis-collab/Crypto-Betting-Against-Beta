# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T16:40:02Z
**HEAD:** `79207f1` (`chore(kilo): checkpoint agent session`) on `main` (clean working tree, in sync with origin/main per session start)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or proven regressions. No unrelated refactors, no workflow edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST EXECUTE HEAVY WORK IMMEDIATELY

**Do not plan-only. Do not run a single-pass probe. Start implementing the required campaign now and produce durable evidence every slice.**

- **C28 items 1–4:** CLOSED with evidence (no proven product gaps). **Do not reopen/churn without a new, statable, reproducible failure + probe evidence.**
- **C28 item 5 (expand matrix): PARTIAL — continue and close it immediately.** Remaining: additional CLI knob combos; API `report()`/`tear_sheet()` strict finiteness on degenerate inputs (`allow_nan=False`); all relevant defect fixtures/modes; output-path edges (incl. unwritable if feasible); regime/cost/slippage/rebalance combos. Determinism = identical outputs/strict JSON across repeated runs. Record per-combo PASS/FAIL with evidence refs; add minimal regressions only for proven gaps.
- **C29 heavy campaign (all 12 mandatory combos): THE FOCUS — execute now per the matrix below.** Minimum ≥12 combos total with durable logs in `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`.

**INITIAL TASK (next session, execute immediately):** Run C29 combo 1 — Real-fixture E2E determinism: `tests/fixtures/real_market_prices.csv` and `tests/fixtures/real_market_prices_expanded.csv` via CLI `--from-prices` and API `load_prices→BABStrategy.run()`, 3× each, byte/strict-JSON identical, `rc=0`. Log each run to the C29 evidence log with timestamp, command, output hash, and PASS/FAIL. Then proceed through combos 2–12 in order. Do not stop at combo 1.

Working tree is clean and preflight deps are available in prior baselines; re-run preflight if env changed:
`export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH && python3 -c "import numpy,pandas,scipy,pytest; print('ok')"`

**Do not declare "blocked" without an evidenced attempt and durable logs.** Do not churn C6–C27 without a new statable reproducible failure supported by probe evidence. Work in small verified slices but make material progress every session. This file is the sole durable coordination artifact for this repo state.

## Current baseline (last confirmed; reconfirm only if code/tests/env change)

- **campaign_d gate floor:** `883 passed, 5 skipped, rc=0` (re-confirmed 2026-11-11T15:49Z on clean tree at `148e6ce`). Recon-firm after any BAB product/test edit.
- **Full BAB excl `data_loader`/controller floor:** `4782 passed, 35 skipped, rc=0` — `/home/runner/work/_temp/kilo-tmp/c28_step0_full_bab.log` (2026-11-11T11:53Z).
- **campaign11+14 closure bundle floor:** `164 passed in 206.53s, rc=0` (re-run 2026-11-11T13:34Z; log `/home/runner/work/_temp/kilo-tmp/c28_gate_campaign11_14_complete.log`).
- **Known non-BAB (excluded from BAB gates, not a blocker):** full-suite includes 2 controller/infra failures in `tests/test_controller_progress_accounting.py` (workflow `stage_safe_changes` missing nested `*/.github/workflows/*` vs `scripts/controller_progress.py EXCLUDE_PATTERNS`). **Do not edit `.github/workflows/*`; do not weaken tests.** Treat as historical/non-BAB discrepancy only.

**Gate floors (must stay green):** campaign_d ≥883 passed/5 skipped/rc=0; full BAB excl data_loader/controller ≥4782 passed/35 skipped/rc=0; campaign11+14 ≥164 passed/0 failed/rc=0. Re-run affected gates after any product/test edit.

## Known bottlenecks / environment notes

- **NO proven BAB runtime bottlenecks.** No repo-level BAB code/test blockers identified; working tree clean.
- **Historical CI/workflow diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior captured log excerpts/signals, not evidence of current source/test failure in this checkout. Do not use to justify inaction.
- **Session hygiene:** transient `/home/runner/work/_temp/kilo-tmp/*` logs may not persist across sessions. Preserve new probe/gate evidence to durable, uniquely named paths in `/home/runner/work/_temp/kilo-tmp/` and cite them here before exit.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).

## C28 review items — resolutions (evidence-first, carry forward)

Primary evidence: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (+ `c28_probe.py|2|3`), `/home/runner/work/_temp/kilo-tmp/c28_session_closure_probe_evidence.log` (2026-11-11T13:47Z, HEAD `7fe0345`), and `/home/runner/work/_temp/kilo-tmp/c28_item2_boundary_probe.log`, `c28_item3_attribution_probe2.log`, `c28_item4_betaneutral_probe4.log`, `c28_item4_report_probe.log`.

1. **CLI↔API synthetic parity — CLOSED (no proven gap).** Intentional contract: CLI forwards `universe=None` (5 ASSET synthetic) vs `BABConfig()` 8-asset default; API with `universe=None` matches CLI exactly. No product fix.
2. **Config boundary contract — CLOSED (no proven gap).** `long_quantile`/`short_quantile` sum≥1 or ==1 accepted with finite results and intentional disjointing/overlap handling per contract/tests; benchmark inside universe accepted/finite with `resolved_universe` contract. No validation gap proven.
3. **Attribution API/cross-consistency — CLOSED (no proven gap).** Correct API `trade_attribution(res.backtest)` → `[gross_return,cost_drag,slippage_drag,net_return]`; synthetic and real fixture finite and `net_return` consistent with backtest returns (allclose). Prior `TypeError` was probe misuse.
4. **`beta_neutral=True` ex-post `strategy_beta` semantics — CLOSED (no proven gap).** Ex-post OLS beta of realized returns vs benchmark (finite) is correct/canonical; neutral enforcement targets portfolio beta exposure causally (tolerance/estimation/time-variation/cost effects can leave finite realized beta). Report/metrics consistent.
5. **Expand matrix — PARTIAL (MANDATORY NOW).** Exercised: real+synthetic attribution/report paths and deterministic strict-JSON report sanity (`allow_nan=False`, identical reruns, beta_neutral+costs+slippage) in session closure log. **Still required to close item 5:** additional CLI knob combos; API `report()`/`tear_sheet()` strict finiteness on degenerate inputs (`allow_nan=False`); all relevant defect fixtures/modes; output-path edges (incl. unwritable if feasible); regime/cost/slippage/rebalance combos. Determinism = identical outputs/strict JSON across repeated runs. Record per-combo PASS/FAIL with evidence refs; add minimal regressions only for proven gaps.

**Status:** items 1–4 closed (no proven gaps). Item 5 PARTIAL. C29 IN FOCUS — execute combos 1–12 now. **Do not invent gaps.**

## Phase C — Execute C29 heavy campaign (≥12 combos, mandatory) — IN FOCUS NOW

**Status:** C29 in progress. Combo 1 (Real-fixture E2E determinism) is the initial task above; combos 2–12 follow in order.
**Evidence log (create/append, durable):** `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
**Regressions for proven fixes only:** `tests/test_bab_cli_campaign29*.py` (or most specific allowed location).
If no proven gaps: record explicit **"no proven gaps"** per area with evidence refs and refresh this handoff.

### Required coverage (all mandatory)
1. **Real-fixture E2E determinism:** `tests/fixtures/real_market_prices.csv` and `tests/fixtures/real_market_prices_expanded.csv` via CLI `--from-prices` and API `load_prices→BABStrategy.run()` — **3× each**, byte/strict-JSON identical, `rc=0`.
2. **Attribution×sizing×shorting matrix:** sizing (`equal`,`kelly`,`vol_target`,`risk_parity`) × `max_short_weight` (0.2/0.5/1.0) × attribution on/off — finite, no Traceback, **2× deterministic**.
3. **Regime filter × costs × slippage × rebalance-freq factorial** on real fixture — finite, deterministic, `allow_nan=False`.
4. **Adversarial defect-fixture contracts:** `messy_returns.csv`, `junk_columns.csv`, `all_nan_column.csv`, `benchmark_nan_window.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv` across load/CLI paths — clean rc/errors vs intended contract, no silent corruption/partial output.
5. **Quality-gate edge branches** (constant/flat/insufficient-history): flat zero-weight periods finite, no NaN/Inf/Traceback.
6. **CLI/script hardening:** `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py` — missing/invalid args, nested `--output`, overwrite, stable rc/messages, no Traceback.
7. **Nonfinite serialization guard:** CLI/script/API JSON on degenerate runs — `allow_nan=False`, finiteness walk, no `Infinity`/`NaN` tokens.
8. **Dry-run side-effect absence** across valid/invalid inputs.
9. **Output-path edge matrix:** existing-dir target, nested create, overwrite-existing-file — clean rc, no corrupt partial output.
10. **Config↔CLI/API equivalence** on real fixture: each relevant CLI knob has equivalent `BABStrategy`/`BABConfig` path producing identical final cumulative (≤1e-12) with evidence.
11. **Repeated-invocation determinism:** same CLI **3×** quick succession, strict-JSON identical.
12. **Additional BAB-relevant stress** discovered during probing with finite/deterministic/contract evidence.

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Closed/locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with:
- refreshed timestamp/HEAD,
- exact gate counts + rc + log paths (re-run if code/tests/env changed),
- C28 item 5 resolution: per-combo results (fixed+regression or explicit **no-gap** + evidence refs),
- C29 per-combo progress/results (all 12), proven gaps/regressions (if any),
- next concrete heavy task message if work remains.

Keep it single, durable, and unambiguous.
