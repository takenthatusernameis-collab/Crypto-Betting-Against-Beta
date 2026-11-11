# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T13:48:30Z
**HEAD:** `7fe0345` (`chore(kilo): checkpoint agent session`) on `main`
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or proven regressions. No unrelated refactors, no workflow edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST EXECUTE HEAVY WORK IMMEDIATELY

C28 items 1-4 are CLOSED with evidence (**no proven product gaps**; see resolutions below). **C28 item 5 (expand matrix) remains PARTIAL — START/CONTINUE IT NOW**, then execute the full **C29 campaign (all 12 required combos, mandatory)**. Working tree clean; preflight ok; no runtime bottlenecks. Do not plan-only, do not do a single-pass probe, do not declare "blocked" without an evidenced attempt and durable logs, and do not churn C6–C27 without a new statable reproducible failure supported by probe evidence. Work in small verified slices but make material progress every session. This handoff is the sole durable coordination artifact for this repo state.

## Current baseline (last confirmed; reconfirm only if code/tests/env change)

- **campaign_d gate:** `879 passed, 5 skipped, rc=0` — `/home/runner/work/_temp/kilo-tmp/c28_gate_campaign_d_refresh.log` (2026-11-11T12:43Z); reconfirmed `879 passed, 5 skipped` at 2026-11-11T13:34Z on clean tree at `3862705` (no BAB source/test edits since; still valid baseline for `7fe0345` which only added checkpoints/handoff-state in git history context — reconfirm if you touch code).
- **campaign11+14 closure bundle:** `164 passed in 206.53s (0:03:26), rc=0` — re-run at 2026-11-11T13:34Z; prior log `/home/runner/work/_temp/kilo-tmp/c28_gate_campaign11_14_complete.log`.
- **Full BAB excl `data_loader`/controller:** `4782 passed, 35 skipped, 231 warnings in 527.00s (0:08:46), rc=0` — `/home/runner/work/_temp/kilo-tmp/c28_step0_full_bab.log` (2026-11-11T11:53Z; unchanged-product baseline).

**Gate floors (must stay green):** campaign_d ≥879 passed/5 skipped/rc=0; full BAB excl data_loader/controller ≥4782 passed/35 skipped/rc=0; campaign11+14 bundle ≥164 passed/0 failed/rc=0. Re-run affected gates after any product/test edit (full as required). If environment changed, preflight:
`export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH && python3 -c "import numpy,pandas,scipy,pytest; print('ok')"`

## Known bottlenecks / environment notes

- **NO BOTTLENECKS.** Preflight `import numpy,pandas,scipy,pytest` ok. Working tree clean on `main` (`7fe0345`). No repo-level code/test blockers.
- **Historical CI/workflow diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior captured log excerpts/signals, not evidence of current source/test failure in this checkout. Treat as historical; do not use to justify inaction.
- **Session hygiene:** transient `/home/runner/work/_temp/kilo-tmp/*` logs may not persist. Preserve new probe/gate evidence to durable, uniquely named paths in `/home/runner/work/_temp/kilo-tmp/` and cite them here. Tracked `probe*`/`debug*`/`ast_probe.py` remain off-limits for edits/commits.

## C28 review items — resolutions (evidence-first)

Primary evidence: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (+ `c28_probe.py|2|3`), **session closure log** `/home/runner/work/_temp/kilo-tmp/c28_session_closure_probe_evidence.log` (2026-11-11T13:47Z, HEAD `7fe0345`), and item probes `/home/runner/work/_temp/kilo-tmp/c28_item2_boundary_probe.log`, `c28_item3_attribution_probe2.log`, `c28_item4_betaneutral_probe4.log`, `c28_item4_report_probe.log`.

1. **CLI↔API synthetic parity — CLOSED (no proven gap).** CLI `0.4124625210306529` vs API default-universe `0.3156954937661637`; API with `universe=None` = `0.4124625210306529` (exact). Divergence is intentional CLI forwarding of `universe=None` (5 ASSET synthetic) vs `BABConfig()` 8-asset default (campaign11o contract). No product fix.

2. **Config boundary contract — CLOSED (no proven gap).** `long_quantile=0.6, short_quantile=0.6` (sum≥1) accepted/ran finite `final=0.5035753195459134` (config preserves values); signal generation intentionally disjoints overlapping quantiles by shrinking short set (`signals.py`: "Never let the long and short sets overlap..."). `sum==1` (0.5/0.5) accepted/ran finite. `benchmark='BTC'` inside `universe=['BTC','ETH']` accepted/ran finite `final=0.9620761095211079`, `resolved_universe=['BTC','ETH']` — consistent with `resolved_universe` contract and existing tests (`test_bab_cli_campaign11o_remaining_probe_regressions.py`, `test_bab_cli_campaign11q_followup_probe_regressions.py`). No validation gap proven.

3. **Attribution API/cross-consistency — CLOSED (no proven gap).** Prior `TypeError` was probe signature misuse. Correct API: `trade_attribution(res.backtest)` → cols `[gross_return,cost_drag,slippage_drag,net_return]`. Synthetic (default): shape `[252,4]`, totals finite, `net_return` matches `res.backtest['returns']` (allclose 1e-12). Real fixture (`tests/fixtures/real_market_prices.csv`, load_prices+run, BTC): shape `[398,4]`, totals finite, consistent. No API/cross-consistency gap.

4. **`beta_neutral=True` ex-post `strategy_beta` semantics — CLOSED (no proven gap).** Real fixture (BTC, `beta_neutral=True`): direct `metrics.strategy_beta(res.backtest['returns'], res.returns['BTC']) == 0.059632543547352916` (finite); `BABStrategy.report(res)` dict reports same finite `metrics.strategy_beta`. Canonical semantic: ex-post OLS beta of realized strategy returns vs benchmark (full-sample slope). `beta_neutral` enforcement targets portfolio beta exposure causally with tolerance; realized return beta can remain finite/non-zero (estimation error, time variation, constraints, cost/regime effects). Finite (not NaN) is correct contract.

5. **Expand matrix — PARTIAL (carry forward, mandatory).** Items 2-4 exercised on real+synthetic; attribution/report paths and a deterministic strict-JSON report sanity (`allow_nan=False`, identical across rerun, beta_neutral+costs+slippage) recorded in session closure log. **Still required:** additional CLI knob combos; API `report()/tear_sheet()` strict finiteness on degenerate inputs (`allow_nan=False`); all relevant defect fixtures/modes; output-path edges (incl. unwritable if feasible); regime/cost/slippage/rebalance combos. Determinism = identical outputs/strict JSON across repeated runs. **Next agent must continue item 5 then proceed to C29.**

**Status:** items 1-4 closed (no proven gaps). Item 5 partial. C29 NOT STARTED. Do not invent gaps.

## Phase C — Execute C29 heavy campaign after C28 closure (≥12 combos, mandatory)

Evidence log: `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
Regressions for proven fixes: `tests/test_bab_cli_campaign29*.py` (or most specific allowed location). If no proven gaps: record explicit "no proven gaps" per area with evidence refs and refresh this handoff.

Required coverage (all mandatory):
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

Update this same `HANDOFF.md` with: refreshed timestamp/HEAD, exact gate counts+rc+log paths, C28 item 5 resolution (fixed+regression or explicit no-gap + evidence), C29 per-combo progress/results (all 12), proven gaps/regressions, and the next concrete heavy task message if work remains. Keep it single, durable, and unambiguous.
