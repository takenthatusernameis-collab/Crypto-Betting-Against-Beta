# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T12:43:36Z
**HEAD:** `38f56b4` (`chore(kilo): checkpoint agent session`) on `main`
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or proven regressions. No unrelated refactors, no workflow edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST EXECUTE HEAVY WORK IMMEDIATELY

C28 item 1 (CLI↔API synthetic parity) is CLOSED — **no proven product gap** (see resolution below). **Start with C28 item 2 (config boundary contract) NOW, then C28 items 3-5, then execute the full C29 campaign (12 combos, mandatory).** Do not plan-only, do not do a single-pass probe, do not declare "blocked" without an evidenced attempt and durable logs, and do not churn C6–C27 without a new statable reproducible failure supported by probe evidence. Work in small verified slices but make material progress every session. This handoff is the sole durable coordination artifact for this repo state.

## Current baseline (last confirmed; reconfirm only if code/tests/env change)

- **campaign_d gate:** `879 passed, 5 skipped, rc=0` — `/home/runner/work/_temp/kilo-tmp/c28_gate_campaign_d_refresh.log` (2026-11-11T12:43Z)
- **campaign11+14 closure bundle:** `164 passed in 196.07s (0:03:16), rc=0` — `/home/runner/work/_temp/kilo-tmp/c28_gate_campaign11_14_complete.log` (2026-11-11T12:43Z)
- **Full BAB excl `data_loader`/controller:** `4782 passed, 35 skipped, 231 warnings in 527.00s (0:08:46), rc=0` — `/home/runner/work/_temp/kilo-tmp/c28_step0_full_bab.log` (2026-11-11T11:53Z; reconfirm if product/edit changes)

**Gate floors (must stay green):** campaign_d ≥879 passed/5 skipped/rc=0; full BAB excl data_loader/controller ≥4782 passed/35 skipped/rc=0; campaign11+14 bundle ≥164 passed/0 failed/rc=0. Re-run affected gates after any product/test edit (full as required). If environment changed, preflight:
`export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH && python3 -c "import numpy,pandas,scipy,pytest; print('ok')"`

## Known bottlenecks / environment notes

- **BOTTLENECK REMOVED (C28 item 1):** CLI↔API synthetic parity was blocking ("START HERE"). Root cause confirmed: CLI forwards `universe=None` → 5 ASSET assets (per campaign11o contract), while `BABConfig()` defaults to 8 named assets. API-equivalent run with `universe=None` produces `0.4124625210306529`, byte-identical to CLI `0.4124625210306529` (≤1e-12). **No product fix required; intended divergence documented with evidence.** Future agents must not re-probe this as a gap.
- **No repo-level code/test blockers observed at handoff refresh.** Working tree clean on `main` (`38f56b4`).
- **Historical CI/workflow diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior run log excerpts/signals (e.g. historical invalid tool-argument/write failures and old traces in captured logs), not evidence of current source/test failure in this checkout. Treat as historical; do not use them to justify inaction.
- **Session hygiene:** transient `/home/runner/work/_temp/kilo-tmp/*` logs may not persist across sessions. Preserve new probe/gate evidence to durable, uniquely named paths in `/home/runner/work/_temp/kilo-tmp/` and cite them in this handoff. Tracked `probe*`/`debug*`/`ast_probe.py` remain off-limits for edits/commits.

## Phase B — CLOSE C28 review items (mandatory, heavy, evidence-first)

Primary evidence: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (+ `c28_probe.py|2|3`). For each item: apples-to-apples repro, capture durable evidence, then either land **smallest proven product fix in allowed modules + targeted regression** or record explicit **"no proven gap"** with evidence refs. Append new findings to `/home/runner/work/_temp/kilo-tmp/c28_closure_probe_evidence.log`.

1. **CLI↔API synthetic parity — CLOSED (no proven gap).** CLI `0.4124625210306529` vs API default-universe `0.3156954937661637`; API with `universe=None` = `0.4124625210306529` (exact match). Divergence is CLI's intentional `universe=None` forwarding (5 ASSET assets) vs `BABConfig()` 8-asset default — intended per campaign11o contract, not a bug. Evidence: c28 probe log §1; live re-run confirmed. **Close with "no proven gap" + evidence refs.**

2. **Config boundary contract (REVIEW, unresolved) — NEXT:** `long_quantile=0.6, short_quantile=0.6` (sum≥1) accepted/ran (`final=0.5035753195459134`); `benchmark='BTC'` inside `universe=['BTC','ETH']` accepted/ran (`final=0.9620761095211079`). Confirm intended contract; if validation gap, minimal fix in allowed modules + regression.

3. **Attribution API/cross-consistency (PARTIAL):** prior probe raised `TypeError: trade_attribution() takes 1 positional argument but 2 were given` — **signature misuse in probe, not a proven product gap**. Re-probe with correct API and reconcile attribution vs weights/returns/report/tear_sheet on real + synthetic fixtures.

4. **`beta_neutral=True` ex-post `strategy_beta` semantics (REVIEW, unresolved):** `metrics.strategy_beta` finite `0.059632543547352916` on real fixture (not NaN). State canonical apples-to-apples semantic/tolerance expectation with evidence; fix only if proven.

5. **Expand matrix (required):** additional CLI knob combos; API `report()/tear_sheet()` strict finiteness on degenerate inputs (`allow_nan=False`); all relevant defect fixtures/modes; output-path edges (incl. unwritable if feasible); regime/cost/slippage/rebalance combos. Determinism = identical outputs/strict JSON across repeated runs.

**Status:** item 1 closed (no proven gap); items 2-5 remain REVIEW/PARTIAL pending canonical closure. Do not invent gaps.

## Phase C — Execute C29 heavy campaign after C28 closure (≥12 combos, mandatory)

Evidence log: `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
Regressions for proven fixes: `tests/test_bab_cli_campaign29*.py` (or most specific allowed location). If no proven gaps: record explicit "no proven gaps" per area with evidence refs and refresh this handoff.

Required coverage:
1. Real-fixture E2E determinism: `tests/fixtures/real_market_prices.csv` and `tests/fixtures/real_market_prices_expanded.csv` via CLI `--from-prices` and API `load_prices→BABStrategy.run()` — 3× each, byte/strict-JSON identical, rc=0.
2. Attribution×sizing×shorting matrix: sizing (`equal`,`kelly`,`vol_target`,`risk_parity`) × `max_short_weight` (0.2/0.5/1.0) × attribution on/off — finite, no Traceback, 2× deterministic.
3. Regime filter × costs × slippage × rebalance-freq factorial on real fixture — finite, deterministic, `allow_nan=False`.
4. Adversarial defect-fixture contracts: `messy_returns.csv`, `junk_columns.csv`, `all_nan_column.csv`, `benchmark_nan_window.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv` across load/CLI paths — clean rc/errors vs intended contract, no silent corruption/partial output.
5. Quality-gate edge branches (constant/flat/insufficient-history): flat zero-weight periods, finite, no NaN/Inf/Traceback.
6. CLI/script hardening: `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py` — missing/invalid args, nested `--output`, overwrite, stable rc/messages, no Traceback.
7. Nonfinite serialization guard: CLI/script/API JSON on degenerate runs — `allow_nan=False`, finiteness walk, no `Infinity`/`NaN` tokens.
8. Dry-run side-effect absence across valid/invalid inputs.
9. Output-path edge matrix: existing-dir target, nested create, overwrite-existing-file — clean rc, no corrupt partial output.
10. Config↔CLI/API equivalence on real fixture: each relevant CLI knob has equivalent `BABStrategy`/`BABConfig` path producing identical final cumulative (≤1e-12) with evidence.
11. Repeated-invocation determinism (same CLI 3× quick succession), strict-JSON identical.
12. Any additional BAB-relevant stress found during probing with finite/deterministic/contract evidence.

## Locks / prohibitions

- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` closed — no changes without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- Editable **only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- No commit/push unless explicitly requested.

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with: refreshed timestamp/HEAD, exact gate counts+rc+log paths, C28 item-by-item resolution (fixed+regression or explicit no-gap + evidence), C29 progress/results, proven gaps/regressions, and the next concrete heavy task message if work remains. Keep it single, durable, and unambiguous.
