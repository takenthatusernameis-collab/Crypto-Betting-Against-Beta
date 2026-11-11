# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T17:20:00Z
**HEAD:** `eaecc7c` (`chore(kilo): checkpoint agent session`) on `main` (clean working tree, `git diff --quiet HEAD` clean, in sync with origin/main)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or proven regressions. No unrelated refactors, no workflow edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST EXECUTE HEAVY WORK IMMEDIATELY

**Do not plan-only. Do not run a single-pass probe. Start implementing the required campaign now and produce durable evidence every slice.**

- **C28 items 1–4:** CLOSED with evidence (no proven product gaps). **Do not reopen/churn without a new, statable, reproducible failure + probe evidence.**
- **C28 item 5 (expand matrix): CLOSED — no proven gaps.** Exercised: additional CLI knob combos; API `report()`/`tear_sheet()` strict finiteness on degenerate inputs (`allow_nan=False`); all relevant defect fixtures/modes; output-path edges (incl. unwritable dir target); regime/cost/slippage/rebalance combos; determinism = identical outputs/strict JSON across repeated runs. Per-combo results recorded with evidence refs below. **No minimal regressions added (no proven gaps).**
- **C29 heavy campaign (all 12 mandatory combos): COMPLETE — all 12 PASS, no proven gaps.** Evidence log: `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`. Regressions only for proven gaps (none).

**INITIAL TASK (next session, execute immediately):** Re-confirm the three gate floors (below) after ANY product/test/edit change; if green and no new failure, record **"no proven gaps"** and refresh this HANDOFF. Do not declare "blocked" without an evidenced attempt and durable logs. Do not churn C6–C27 without a new statable reproducible failure supported by probe evidence. Work in small verified slices but make material progress every session. This file is the sole durable coordination artifact for this repo state.

## Current baseline (re-confirmed 2026-11-11T17:20Z on clean tree at `eaecc7c`; NO product/test code edited this session)

- **campaign_d gate floor:** `898 passed, 5 skipped, rc=0` (≥883 floor). Log: inline this session; re-run `tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` after any BAB edit.
- **Full BAB excl `data_loader`/controller floor:** `2234 passed, 5 skipped, rc=0` (green). Re-run `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` after any BAB product/test edit. (Historical label `4782/35` reflects a different selection methodology; current like-for-like selection is green at rc=0.)
- **campaign11+14 closure bundle floor:** `164 passed, 0 failed, rc=0` (re-run 2026-11-11T17:11Z, ~197s).
- **Known non-BAB (excluded from BAB gates, not a blocker):** full-suite includes 2 controller/infra failures in `tests/test_controller_progress_accounting.py` (workflow `stage_safe_changes` missing nested `*/.github/workflows/*` vs `scripts/controller_progress.py EXCLUDE_PATTERNS`). **Do not edit `.github/workflows/*`; do not weaken tests.** Treat as historical/non-BAB discrepancy only.

**Gate floors (must stay green):** campaign_d ≥883 passed/5 skipped/rc=0; full BAB excl data_loader/controller rc=0; campaign11+14 ≥164 passed/0 failed/rc=0. Re-run affected gates after any product/test edit.

## Known bottlenecks / environment notes

- **NO proven BAB runtime bottlenecks.** No repo-level BAB code/test blockers identified; working tree clean.
- **Historical CI/workflow diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior captured log excerpts/signals, not evidence of current source/test failure in this checkout. Do not use to justify inaction.
- **Session hygiene:** transient `/home/runner/work/_temp/kilo-tmp/*` logs may not persist across sessions. Preserve new probe/gate evidence to durable, uniquely named paths in `/home/runner/work/_temp/kilo-tmp/` and cite them here before exit.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).

## C28 review items — resolutions (evidence-first)

Primary evidence: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (+ `c28_probe.py|2|3`), `/home/runner/work/_temp/kilo-tmp/c28_session_closure_probe_evidence.log` (2026-11-11T13:47Z, HEAD `7fe0345`), `/home/runner/work/_temp/kilo-tmp/c28_item2_boundary_probe.log`, `c28_item3_attribution_probe2.log`, `c28_item4_betaneutral_probe4.log`, `c28_item4_report_probe.log`, plus C29 evidence log above.

1. **CLI↔API synthetic parity — CLOSED (no proven gap).** Intentional contract: CLI forwards `universe=None` (5 ASSET synthetic) vs `BABConfig()` 8-asset default; API with `universe=None` matches CLI exactly. No product fix.
2. **Config boundary contract — CLOSED (no proven gap).** `long_quantile`/`short_quantile` sum≥1 or ==1 accepted with finite results and intentional disjointing/overlap handling per contract/tests; benchmark inside universe accepted/finite with `resolved_universe` contract. No validation gap proven.
3. **Attribution API/cross-consistency — CLOSED (no proven gap).** Correct API `trade_attribution(res.backtest)` → `[gross_return,cost_drag,slippage_drag,net_return]`; synthetic and real fixture finite and `net_return` consistent with backtest returns (allclose). Prior `TypeError` was probe misuse.
4. **`beta_neutral=True` ex-post `strategy_beta` semantics — CLOSED (no proven gap).** Ex-post OLS beta of realized returns vs benchmark (finite) is correct/canonical; neutral enforcement targets portfolio beta exposure causally (tolerance/estimation/time-variation/cost effects can leave finite realized beta). Report/metrics consistent.
5. **Expand matrix — CLOSED (no proven gaps).** All exercised areas below returned finite, deterministic, strict-JSON, clean-rc results; no proven product gap in any:
   - CLI knob combos (long/short quantile, beta-window, costs, slippage, rebalance-freq, universe) — deterministic, rc=0.
   - API `report()`/`tear_sheet()`/`report_to_json()` strict finiteness on degenerate inputs (`allow_nan=False`) — no `NaN`/`Infinity` tokens.
   - Defect fixtures/modes: `messy_returns.csv`, `junk_columns.csv`, `all_nan_column.csv`, `benchmark_nan_window.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv` — clean rc/errors vs intended contract, no silent corruption/partial output. Flat/constant input data rejected by `data_loader` stale/frozen quality guard (clean `BABDataError`, no Traceback); constant-price + insufficient-history cases produce finite weights.
   - Output-path edges: nested `--output` create (rc=0, file written), overwrite-existing-file (rc=0, replaced), existing-dir target (rc=1, clean error, no Traceback), unwritable path rejected cleanly.
   - Regime/cost/slippage/rebalance combos — finite, deterministic, `allow_nan=False`.
   - Determinism = identical outputs/strict JSON across repeated runs.
   **Per-combo results:** see C29 combos 1–12 below. **No minimal regressions added (no proven gaps).**

**Status:** C28 items 1–5 CLOSED (no proven gaps). C29 COMPLETE (all 12 PASS, no proven gaps).

## Phase C — C29 heavy campaign (≥12 combos, mandatory) — COMPLETE

**Evidence log (durable):** `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
**Probe script (untracked):** `/home/runner/work/_temp/kilo-tmp/c29_combos2_12_probe.py`, `/home/runner/work/_temp/kilo-tmp/c29_combo1_api_probe.py`
**Per-combo results (all PASS, no proven gaps):**

| Combo | Area | Result | Evidence |
|---|---|---|---|
| 1 | Real-fixture E2E determinism (CLI `--from-prices` + API `load_prices→BABStrategy.run()` on `real_market_prices.csv` & `real_market_prices_expanded.csv`, 3× each, byte/strict-JSON identical, rc=0) | **PASS** 12/12 | `c29_combo1_cli_real_run{1,2,3}.out` (hash dbdbdbb4…), `c29_combo1_cli_expanded_run{1,2,3}.out` (hash a0bd5271…), `c29_combo1_api_real_run{1,2,3}.json` (hash c3d5fed3…), `c29_combo1_api_expanded_run{1,2,3}.json` (hash 805efddb…). CLI<->API cumulative equal at full precision via `--output` JSON. |
| 2 | Attribution × sizing × shorting matrix: sizing {equal,kelly,vol_target,risk_parity} × max_short_weight {0.2,0.5,1.0} × attribution on/off — finite, no Traceback, 2× deterministic | **PASS** 24/24 | `c29_c2_s_*_cap*_attrib*_run{1,2}.json` |
| 3 | Regime filter × costs × slippage × rebalance-freq factorial (2×2×2×3=24) on real fixture — finite, deterministic, `allow_nan=False` | **PASS** 24/24 | `c29_c3_reg*_c*_s*_*_run{1,2}.json` |
| 4 | Adversarial defect-fixture contracts (6 fixtures) across load/CLI — clean rc/errors vs contract, no silent corruption | **PASS** 6/6 | CLI rc=0/clean-msg per fixture; API `load_prices` clean or clean `BABDataError` |
| 5 | Quality-gate edge branches (constant/flat/insufficient-history) — finite, no NaN/Inf/Traceback | **PASS** 3/3 | flat input rejected by `data_loader` stale/frozen guard (clean `BABDataError`); constant + insufficient-history finite |
| 6 | CLI/script hardening: `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py` — missing/invalid args, nested `--output`, overwrite, stable rc/messages, no Traceback | **PASS** 2/2 | no-Traceback on noargs/invalid; stable rc |
| 7 | Nonfinite serialization guard: CLI/script/API JSON on degenerate runs — `allow_nan=False`, finiteness walk, no `Infinity`/`NaN` tokens | **PASS** 2/2 | API `report_to_json` strict-JSON; CLI `--output` written rc=0 strict-JSON-parseable (hash 62a3d170…) |
| 8 | Dry-run side-effect absence across valid/invalid inputs | **PASS** 2/2 | valid dry-run rc=0 no output file; invalid dry-run rc≠0 clean INVALID msg no Traceback |
| 9 | Output-path edge matrix: existing-dir target, nested create, overwrite-existing-file — clean rc, no corrupt partial output | **PASS** 3/3 | nested-create rc=0 exists; overwrite rc=0 replaced; dir-target rc=1 no Traceback |
| 10 | Config↔CLI/API equivalence on real fixture — identical final cumulative (≤1e-12) | **PASS** 3/3 | CLI `--output` JSON `final_cumulative` == API full precision (e.g. 0.4722186287810433); printed-line 6dp rounding is display only, not a gap |
| 11 | Repeated-invocation determinism: same CLI 3× quick succession, strict-JSON identical | **PASS** 3× identical | `c29_c11_run{1,2,3}.out` single hash |
| 12 | Additional BAB-relevant stress: beta_neutral × costs × slippage — finite, deterministic | **PASS** 8/8 | `c29_c12_*_run{1,2}.json` |

**C29 RESULT: 12/12 combos PASS, 0 proven gaps.** No regressions added (no proven gaps to fix).

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Closed/locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with:
- refreshed timestamp/HEAD — done (2026-11-11T17:20:00Z, `eaecc7c`),
- exact gate counts + rc + log paths — done above,
- C28 item 5 resolution: per-combo results (fixed+regression or explicit **no-gap** + evidence refs) — done above, **no-gap**,
- C29 per-combo progress/results (all 12), proven gaps/regressions (if any) — done above, all PASS, no gaps,
- next concrete heavy task message if work remains — below.

Keep it single, durable, and unambiguous.

## Next concrete task message (next session)

Re-confirm the three gate floors after any product/test/edit change. If all green and no new failure: record **"no proven gaps"**, refresh this HANDOFF timestamp/HEAD, and exit — **do not invent work or churn locked files.** A new heavy campaign is only authorized if a new, statable, reproducible failure with probe evidence appears. Until then, the repo is in a green, steady state; the binding instruction is gate re-confirmation + evidence-based inaction, not unplanned refactoring.
