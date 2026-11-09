# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T17:54:38Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `8cd7ffa` (`chore(kilo): checkpoint agent session`, local main). Working tree: **untracked `tests/test_bab_cli_error_reporting.py` (slice d), `tests/test_bab_cli_numeric_reporting.py` (slice e), `tests/test_bab_backtest_contract_smoke.py` (slice f, added this session)**; `HANDOFF.md` modified by this session. Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `8cd7ffa`, deps installed `numpy/pandas/scipy/pytest`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3766 deselected, 53 warnings, rc=0**
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1875 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 168.81s** (FULL RUN COMPLETED, post-fix; floor raised from 1866/5 → 1875/5 by slice f)
- campaign11 tests: `tests/test_bab_backtest_contract_smoke.py tests/test_bab_cli_numeric_reporting.py tests/test_bab_cli_reporting_robustness.py tests/test_bab_cli_error_reporting.py` → **62 passed, rc=0** (9 + 10 + 34 + 9)

**campaign11 — IN PROGRESS (slices a–f implemented & verified this session; no production changes):**
- **`tests/test_bab_cli_reporting_robustness.py`** (tracked history): 34 tests — output path/schema/determinism across returns.json, real_market_prices*.csv `--from-prices`, synthetic `--beta-window 30`; dry-run/output validation; numeric/backtest invariants on real fixtures; README↔CLI contract smokes.
- **`tests/test_bab_cli_error_reporting.py`** (untracked, slice d): 9 tests — evidence-first CLI error paths (missing `--data` dry-run/real, `--from-prices` missing, `--output` directory, unwritable parent best-effort, `--data` directory, valid dry-run fixture). **No production bug proven.**
- **`tests/test_bab_cli_numeric_reporting.py`** (untracked, slice e): 10 tests — strict JSON/finite summary invariants across all committed fixtures + synthetic; CLI `periods`/`final_cumulative` parity with `BABStrategy(BABConfig(...))` for deterministic synthetic configs (CLI synthetic uses `BABConfig(universe=None,...)` defaults); `--universe` subset contract reflected/stable with parity; NaN/Infinity token absence. **No production bug proven.**
- **`tests/test_bab_backtest_contract_smoke.py`** (untracked, slice f, added this session): 9 tests — backtest/metrics/report contract smoke on committed real fixtures (`real_market_prices*.csv`, `returns.json`) and deterministic synthetic. Evidence-based contracts only: `result.backtest` is a DataFrame with columns `['returns','gross_return','cost_drag','slippage_drag','cumulative']` (verified `backtest.py`/`strategy.run`), monotonic index, finite scalar tail, positive cumulative, non-negative drags, CLI periods/tail parity. `BABStrategy.report()`/`tear_sheet()` present (evidence: strategy API) — smoke finite/JSON-serializable (`default=str`) outputs; report includes `config/metrics/rebalances/attribution/attribution_totals`. **No production bug proven; no production edits.**

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1875/5 (current verified floor). Fix regressions before new work.
2. **Slice (g) — targeted edge/error robustness (only if evidence supports):** inspect `_extract_cumulative`/`_json_safe`/`_json_default`/`_build_output_summary` with adversarial-but-plausible `backtest` shapes the CLI already defends against (Series/list/ndarray/empty/non-DataFrame, non-string universe elements, malformed cumulative) and strategy↔CLI boundary for `BABDataError` propagation on real-data paths. Add tests only for proven gaps or missing coverage of existing defenses; **do not weaken assertions**. No speculative refactors. No production edits unless a real bug is proven with evidence + minimal regression test.
3. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
4. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1875/5 (or updated verified count with explanation); all touched BAB tests green.
5. **Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1875/5). Fix regressions before new work.
1. Execute campaign11 slice (g) end-to-end (inspect `cli._extract_cumulative/_json_safe/_json_default/_build_output_summary` + strategy/loader error surfaces before asserting); add tests only for proven/defensive gaps; run new tests + campaign_d + full excl (monitor if needed); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes (unblock next agent):**
- Full excl run completes (~169s) — use `background_process monitor timeout>=450000` if shell tool times out.
- `rm -f .coverage .coverage.*` before canonical runs.
- Slice e parity: CLI synthetic `BABStrategy(BABConfig(universe=None,...))` differs from shorthand defaults; assert against equivalent `BABConfig`.
- `tests/test_bab_cli_numeric_reporting.py`, `tests/test_bab_cli_error_reporting.py`, `tests/test_bab_backtest_contract_smoke.py` are **untracked** — keep/extend; do not weaken.
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit**.
- CLI summary schema: `final_cumulative` (finite float), `periods`, `benchmark`, `universe`; JSON `allow_nan=False`. `run_backtest` columns observed: `returns,gross_return,cost_drag,slippage_drag,cumulative`.
- Gates: `campaign_d` 883/5, full excl 1875/5 (verified this session).

**ACTIVE:** campaign11 next = slice (g) targeted edge/error robustness only if proven (inspect CLI JSON/cumulative extraction + strategy/loader boundaries). Slices (a)–(f) implemented/verified (62 campaign11 tests passing). campaign10 complete. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T17:54:38Z @ `8cd7ffa`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
