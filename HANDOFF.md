# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T20:52:15Z (active handoff for next session)
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `a99de0f` (`chore(kilo): checkpoint agent session`, `main`; prior recorded base in earlier handoff text: `dbe6e5c`).
**Working tree:** clean at start of this session. No competing handoff files. No production code changes made this session.

**Environment (observed 2026-11-10T20:52Z):** `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0; pytest 9.2.0. Fixtures present under `tests/fixtures/` (incl. `real_market_prices.csv`, `real_market_prices_expanded.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`).

**Probe evidence (this workspace, 2026-11-10T20:52Z):**
- `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log` **MISSING** — C19 is **unexecuted** and is the binding next campaign.
- `tests/test_bab_cli_campaign19*.py` **none**.
- Prior C16–C18 probe logs referenced by earlier handoff text are not present in `/home/runner/work/_temp/kilo-tmp/` in this environment; treat prior campaign closure claims as historical context only and do not churn without a new, statable, reproducible failure. Gates below must be re-run fresh before any production edit.

**Bottlenecks removed:** kept this single durable `HANDOFF.md` current/unambiguous (no competing handoff files). No blocked/inefficient in-repo sessions identified in this session.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr and JSON validity where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0** (investigate regressions before production edits)
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4708 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

Treat prior campaign regressions as evidence; do not revert without cause.

### 2) Campaigns 6–18 remain historically closed (evidence-backed per prior handoff context, no churn)
C6–C18 were reported closed in prior sessions (benchmark/NaN/universe/parity/cost/dry-run/reporting/pipeline/schema-metrics/strategy-core/metrics-attribution-sizing-regime/beta-neutral fidelity). Do not churn without a new, statable, reproducible failure. If you cannot reproduce prior evidence in this environment, rely on fresh Step 0 gates and C19 probes.

### 3) Execute C19 — BAB config-validation edges, cost/slippage monotonic drag, universe/rebalance/shorting/sizing robustness on real & defective data (≥12 distinct probe combos, HEAVY)
Goal: verify **BAB configuration robustness and cost/slippage/position-sizing fidelity** — `BABConfig` validation errors (clean `BABConfigError`, no Traceback), transaction-cost monotonic drag across cost levels, slippage application, explicit-universe override rejection (no overlap), rebalance freq (weekly/monthly vs daily), shorting constraints, max_position_size bounding, and CLI `--output` strict-JSON schema on real & defective data. Fixtures: `REAL` (`tests/fixtures/real_market_prices.csv`), `EXP` (`tests/fixtures/real_market_prices_expanded.csv`), `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`. Log: `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log` (cmd, rc, stdout, stderr, JSON validity/finiteness with `allow_nan=False`, key sets, determinism, neutrality/shorting/bounds checks where applicable).

**Required probe matrix (minimum 12 combos, in-process unless marked CLI):**
1. `BABConfig(beta_window=0)` → `BABConfigError` clean, no Traceback.
2. `BABConfig(long_quantile=0.0)` and `long_quantile=1.0` → `BABConfigError` clean (must be in (0,1)).
3. `BABConfig(short_quantile=0.0)` → `BABConfigError` clean.
4. `BABConfig(transaction_costs=-0.001)` → `BABConfigError` clean.
5. `BABConfig(vol_thresholds=[...], vol_percentiles=[...])` both set → `BABConfigError` clean ("set only one").
6. Cost monotonic drag: REAL default × `tc` ∈ {0.0, 0.0005, 0.001, 0.005} → `final_cumulative` non-increasing as `tc` rises; all metrics finite, strict JSON OK.
7. Slippage application: REAL default × `slippage` ∈ {0.0, 0.001} → `slippage_drag` > 0 when slippage>0, all finite, net_return = gross − cost − slippage.
8. Explicit universe override with no data overlap → `BABConfigError` clean (e.g. universe=["ZZZ","YYY"] on REAL).
9. Rebalance freq `weekly` vs `monthly` vs `daily` on REAL default → all run, metrics finite, weights dollar-neutral; determinism across two runs identical per freq.
10. Shorting constraints dict on REAL default → runs, weights finite, dollar-neutral, shorting present.
11. `max_position_size=0.2` on REAL default → runs, all |weights| ≤ ~0.2 + tolerance, weights finite.
12. CLI: `python -m strategies.betting_against_beta.cli --data REAL --from-prices --benchmark BTC --output <tmp>/out.json` → rc=0, valid strict JSON, keys {final_cumulative,periods,benchmark,universe}, periods=398, stderr empty.
13. CLI: `--output` to a nonexistent nested directory via module CLI → rc=0 (parents created), valid JSON written.
14. CLI: `--dry-run --output <existing-dir>` → rc=1 clean "is a directory" error, no Traceback.
15. (extra) CLI determinism: two identical REAL `--from-prices --output` runs → byte-identical stdout/JSON.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 4) Triage and fix only proven gaps
- Fix only behavior with statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics, non-finite where finite expected, incorrect rc/error contract, Traceback on user paths).
- Keep fixes to the **smallest non-locked module(s)**; prefer `cli.py`/`metrics.py`/`reporting.py`/`backtest_report.py` paths only if probe evidence proves a gap. Do **not** touch locked modules (`beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`) unless disproven by new evidence and fix is minimal.
- Add regressions in `tests/test_bab_cli_campaign19*.py` for every proven fix. If no proven gaps, record explicit "no proven gaps" with evidence refs in the C19 log and this HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, C19 evidence (log path, combo summary, parity/neutrality/fin determinism notes), gate results, touched modules, and the next binding heavy campaign (C20) with a concrete ≥12-combo probe plan. No generic "continue" handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by new evidence. `cli.py`/`metrics.py` editable only for smallest proven fix from probe evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T20:52:15Z @ a99de0f)
- Repo state: HEAD `a99de0f` on `main`; working tree clean at session start; no competing handoff files.
- Environment: deps import rc=0 (pytest 9.2.0). Real/defect fixtures confirmed in `tests/fixtures/`.
- C19 status: **not executed** (no evidence log, no `tests/test_bab_cli_campaign19*.py`). Prior C16–C18 log files not present in `/home/runner/work/_temp/kilo-tmp/` in this environment.
- Step 0 gates: **not re-run this session** (no full test execution performed); next agent MUST run Step 0 before any edit and record exact counts/rc.
- Action taken: refreshed this single durable handoff with current HEAD/timestamp, cleared ambiguity, and made C19 the binding next heavy campaign with explicit ≥12-combo probe plan.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C19 — BAB config-validation edges, cost/slippage monotonic drag, universe/rebalance/shorting/sizing robustness on real & defective data (≥12 probe combos).** Execute the matrix in §3 with subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log`. Triage/fix only proven gaps (smallest non-locked-module change + regressions), else record explicit "no proven gaps". Then refresh this `HANDOFF.md` with C19 evidence and nominate **C20** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **≥883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4708 passed, 35 skipped** (never below floor without investigation); campaign11 bundle incl. 11ab + campaign14 **≥164 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`. `.github/workflows/*` — do not edit. Commit/push only if explicitly requested.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record exact counts/rc. 2) EXECUTE C19 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only (smallest non-locked-module change + `tests/test_bab_cli_campaign19*.py` regressions) or record "no proven gaps". 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign (C20).

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
