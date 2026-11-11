# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T11:46:45Z
**HEAD:** `a6f8f2d` (`chore(kilo): checkpoint agent session`) on `main` (no product code changes in this handoff refresh)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting fidelity, or proven regressions. No unrelated refactors, no workflow edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST EXECUTE HEAVY WORK IMMEDIATELY

**No planning-only exits. No single-pass probes. No evidence-free claims. No declaring “blocked” without an evidenced attempt and captured logs.** Do not churn C6–C27 without a new, statable, reproducible failure supported by probe evidence.

### Phase A — Unblock & finalize Step 0 baseline gates (do first, capture to logs)

Preflight (record rc):
`export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH && python3 -c "import numpy,pandas,scipy,pytest"`

Run each gate to completion with captured output (prior bottleneck: timeouts without final summary). Use `tee` to durable logs under `/home/runner/work/_temp/kilo-tmp/` and record **exact pass/skip/fail counts + rc** in the next handoff refresh:

1. `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py 2>&1 | tee /home/runner/work/_temp/kilo-tmp/c28_gate_campaign_d.log`
   - **Floor:** ≥883 passed, 5 skipped, rc=0
2. `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller* 2>&1 | tee /home/runner/work/_temp/kilo-tmp/c28_gate_full_bab.log`
   - **Floor:** ≥4782 passed, 35 skipped, rc=0 (raise floor only if legitimately increased)
3. `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py 2>&1 | tee /home/runner/work/_temp/kilo-tmp/c28_gate_campaign11_14.log`
   - **Floor:** ≥164 passed, 0 failed, rc=0 (**currently NOT confirmed complete** — this is a mandatory closure item)

If any gate regresses: stop feature work, produce probe evidence, apply the smallest proven fix + targeted regression, and re-run affected gates.

**Known prior evidence (verify, do not assume):** campaign_d green `883 passed, 5 skipped, 1808 deselected, rc=0` (2026-11-11T11:32Z); full-BAB log-complete `4782 passed, 35 skipped, rc=0` in `/home/runner/work/_temp/kilo-tmp/c28_step0_full_bab.log` (527.00s). Re-confirm if any edit occurs.

### Phase B — Close C28 REVIEW items with canonical probe evidence (heavy, mandatory)

Existing C28 evidence (read first): `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (2026-11-11T11:34Z, combos 1–12), probes `c28_probe.py|2|3` in `/home/runner/work/_temp/kilo-tmp/`. For each item below: produce an apples-to-apples repro, capture evidence, then either land the smallest proven product fix + regression or record explicit **“no proven gap”** with evidence refs.

1. **CLI↔API synthetic parity (REVIEW):** CLI `--synthetic` (BTC, beta_window=90, q=0.3/0.3, tx=0.001, slip=0.0005) final `0.4124625…` vs direct `BABStrategy/BABConfig` run `0.3156954…`. Identify canonical equivalent config/data-generation/defaults path; prove parity or document intended divergence with precise evidence (no hand-waving).
2. **Config boundary contract (REVIEW):** `long_quantile=0.6, short_quantile=0.6` (sum≥1) and `benchmark='BTC'` inside `universe=['BTC','ETH']` accepted/ran. Confirm intended contract; if validation gap, implement minimal fix in allowed modules + regression.
3. **Attribution API/cross-consistency (PARTIAL):** prior probe misused `trade_attribution` signature (TypeError, not a product gap). Re-probe with correct API and reconcile attribution vs weights/returns/report/tear_sheet.
4. **`beta_neutral=True` ex-post `strategy_beta` semantics (REVIEW):** `metrics.strategy_beta` finite (0.0596325…) on real fixture, not NaN. State canonical apples-to-apples semantic/tolerance expectation with evidence; fix only if proven.
5. **Expand matrix (required):** additional CLI knob combos; API `report()/tear_sheet()` strict finiteness on degenerate inputs; all relevant defect fixtures/modes; output-path edges (incl. unwritable if feasible); regime/cost/slippage/rebalance combos. Determinism = identical outputs/strict JSON across repeated runs.

Append all new findings to a fresh evidence log: `/home/runner/work/_temp/kilo-tmp/c28_closure_probe_evidence.log`.

**Proven gaps so far:** none fixed this cycle. Do not invent gaps; do not leave REVIEW items unresolved without evidence.

### Phase C — Execute C29 heavy campaign after C28 closure (≥12 combos, mandatory)

Evidence log: `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
Regression tests for any proven fix: `tests/test_bab_cli_campaign29*.py` (or most specific allowed location). If no proven gaps: record explicit “no proven gaps” per area with evidence refs and refresh handoff.

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

### Gates that must stay green (non-negotiable)
- `campaign_d` ≥883 passed, 5 skipped, rc=0
- full BAB excl `data_loader`/`controller` ≥4782 passed, 35 skipped, rc=0
- campaign11 bundle incl. 11ab + campaign14 ≥164 passed, 0 failed, rc=0

Re-run all Step 0 gates + any touched suites after every product/test edit.

### Locks / prohibitions
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` closed — no changes without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/reporting/`scripts`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` editable **only** for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested.

### Handoff refresh requirement (before exit)
Update this same `HANDOFF.md` with: refreshed timestamp/HEAD, exact gate counts+rc+log paths, C28 item-by-item resolution (fixed+regression or explicit no-gap + evidence), C29 progress/results, proven gaps/regressions, and the next concrete heavy task message if work remains. Keep it single, durable, and unambiguous.
