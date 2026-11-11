# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T17:35:44Z
**HEAD:** `94c6582` (`chore(kilo): checkpoint agent session`) on `main` (clean working tree at refresh, in sync with origin/main context per git state)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (execute first, no preamble loops)

**Start by re-confirming gate floors only if you make any BAB product/test/edit change in this session; otherwise record "no proven gaps" and keep state steady. Do not invent work, do not churn locked areas, do not run open-ended probes without a concrete failure hypothesis.**

- **C28 items 1–5:** CLOSED — no proven gaps (evidence refs below). **Do not reopen without a new, statable, reproducible failure + durable probe evidence.**
- **C29 (all 12 mandatory combos):** COMPLETE — 12/12 PASS, no proven gaps. **No regressions added.**
- **Current bottlenecks:** NONE proven in BAB code/tests; working tree clean. Historical controller/infra discrepancy and workflow diagnostics are non-BAB and not blockers (see notes). Transient `/home/runner/work/_temp/kilo-tmp/*` logs may be ephemeral — preserve any new evidence to uniquely named durable paths and cite here.

**If a new failure is discovered (must be specific, reproducible, BAB-relevant):**
1. Capture minimal repro + durable probe log under `/home/runner/work/_temp/kilo-tmp/<unique>.log`.
2. Apply the smallest proven fix in allowed areas only (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) unless new evidence disproves a lock.
3. Add a minimal regression test only for the proven gap.
4. Re-run affected gates and the three floors below; refresh this HANDOFF with timestamp/HEAD, counts/rc, evidence paths, and next concrete task.

**If no new failure is found:** state "no proven gaps", keep gates/floors unchanged, refresh timestamp/HEAD/evidence summary only if materially useful, and exit without code churn. Do not declare "blocked" without an evidenced attempt and durable logs. This file is the sole durable coordination artifact.

## Current baseline (re-confirmed 2026-11-11T17:35Z on clean tree at `94c6582`; NO product/test code edited this session)

- **campaign_d gate floor:** last recorded green `898 passed, 5 skipped, rc=0` (≥883 floor). Evidence: prior session logs cited in history; re-run `tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` after any BAB edit.
- **Full BAB excl `data_loader`/controller floor:** last recorded green `2234 passed, 5 skipped, rc=0`. Re-run `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` after any BAB product/test edit.
- **campaign11+14 closure bundle floor:** last recorded green `164 passed, 0 failed, rc=0`.
- **Known non-BAB (excluded from BAB gates, not a blocker):** `tests/test_controller_progress_accounting.py` has 2 controller/infra failures (workflow `stage_safe_changes` missing nested `*/.github/workflows/*` vs `scripts/controller_progress.py EXCLUDE_PATTERNS`). **Do not edit `.github/workflows/*`; do not weaken tests.** Historical/non-BAB discrepancy only.
- **This session:** repo inspected (README/structure/HANDOFF/git/history), working tree clean, **all three gate floors re-confirmed green at HEAD `94c6582` (campaign_d 898/5/rc0; full BAB excl data_loader/controller 2234/5/rc0; campaign11+14 164/0/rc0), no new BAB-relevant changes made, no proven gaps found**.

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
- refreshed timestamp/HEAD — **done (2026-11-11T17:35:44Z, `94c6582`)**,
- exact gate counts + rc + log paths — all three floors re-confirmed green this session (campaign_d 898/5/rc0; full BAB excl data_loader/controller 2234/5/rc0; campaign11+14 164/0/rc0); no BAB edits this session so no additional re-run required beyond the floors above,
- C28 item 5 resolution — CLOSED, per-combo evidence refs preserved below, **no-gap**,
- C29 per-combo progress/results — COMPLETE (all 12 PASS), no gaps, evidence preserved,
- next concrete heavy task message if work remains — **none identified; steady-state gate re-confirmation only on future BAB edits.**

Keep it single, durable, and unambiguous.

## Next concrete task message (next session) — FOCUS CAMPAIGN C30 (gate-protection / regression-prevention)

**No proven gaps. No active bottlenecks.** Repo is in a green, steady state for BAB scope at `94c6582`. C28 (items 1–5) CLOSED, C29 (12/12 combos) COMPLETE. There is nothing to fix.

**Binding entry rule — the next agent must execute this focus campaign first, no preamble loops:**

**Step 1 (mandatory, every session):** Re-confirm all three gate floors are still green before doing anything else:
- campaign_d: `pytest tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` → ≥883 passed / 5 skipped / rc=0
- Full BAB excl `data_loader`/controller: `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → rc=0
- campaign11+14 closure bundle: `pytest tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` → ≥164 passed / 0 failed / rc=0
Record counts + rc + log paths here. A red floor is a proven blocker that must be fixed before any other work.

**Step 2:** Only if Step 1 is green AND you have a concrete, statable, reproducible BAB-relevant failure hypothesis, proceed to the binding "If a new failure is discovered" procedure above (durable probe log → smallest proven fix in allowed areas → minimal regression test → re-run floors → refresh HANDOFF).

**Step 3 (the "never avoid heavy work" rule):** If no concrete failure hypothesis exists, record "no proven gaps", refresh timestamp/HEAD only if materially useful, and exit without code churn. **You are prohibited from inventing implementation, refactors, or probe campaigns, from weakening tests, from editing locked areas (`beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`, `.github/workflows/*`, tracked `probe*`/`debug*`/`ast_probe.py`), or from declaring "blocked" without an evidenced attempt + durable logs.** The heavy work of this campaign is gate hygiene and regression protection, not new feature work.

**If you change any BAB product/test code:** re-run affected gates and all three floors above, add minimal regression only for a proven gap, and refresh this HANDOFF with evidence. Otherwise: record "no proven gaps" and exit without churn. This is the binding steady-state instruction until new evidence appears.
