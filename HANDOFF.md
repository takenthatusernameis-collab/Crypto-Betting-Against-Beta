# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T18:49:11Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `b391c6e` (`chore(kilo): checkpoint agent session`, local main). Working tree: **clean except untracked** `tests/test_bab_cli_edge_robustness_campaign11g.py` (new this session, 12 tests, all passing). All prior campaign11 slices (a)–(f) tracked/committed @ `4b0ce91`. Do not commit/push unless explicitly requested.
**Baseline/gates (re-verified this session @ `b391c6e`, deps installed `numpy/pandas/scipy/pytest`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3778 deselected, 53 warnings, rc=0**
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1887 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 168.48s** (FULL RUN COMPLETED; floor raised 1875→1887 by +12 campaign11g tests; no production code changed)
- campaign11 tests: `tests/test_bab_backtest_contract_smoke.py tests/test_bab_cli_numeric_reporting.py tests/test_bab_cli_reporting_robustness.py tests/test_bab_cli_error_reporting.py tests/test_bab_cli_edge_robustness_campaign11g.py` → **74 passed, rc=0** (9 + 10 + 34 + 9 + 12)

**campaign11 — IN PROGRESS (slices a–g implemented & verified; no production changes):**
- **`tests/test_bab_cli_reporting_robustness.py`** (tracked): 34 tests — output path/schema/determinism across fixtures; dry-run/output validation; numeric/backtest invariants; README↔CLI contract smokes.
- **`tests/test_bab_cli_error_reporting.py`** (tracked, slice d): 9 tests — evidence-first CLI error paths (missing `--data`, `--from-prices` missing, `--output` directory, unwritable parent best-effort, `--data` directory, valid dry-run fixture). **No production bug proven.**
- **`tests/test_bab_cli_numeric_reporting.py`** (tracked, slice e): 10 tests — strict JSON/finite summary invariants across committed fixtures + synthetic; CLI `periods`/`final_cumulative` parity with `BABStrategy(BABConfig(...))` for deterministic synthetic configs (CLI synthetic uses `BABConfig(universe=None,...)`); `--universe` subset contract/parity; NaN/Infinity token absence. **No production bug proven.**
- **`tests/test_bab_backtest_contract_smoke.py`** (tracked, slice f): 9 tests — backtest/metrics/report contract smoke on committed real fixtures and deterministic synthetic. Evidence-based contracts: `result.backtest` DataFrame columns `['returns','gross_return','cost_drag','slippage_drag','cumulative']` (`backtest.py`/`strategy.run`), monotonic index, finite scalar tail, positive cumulative, non-negative drags, CLI parity. `report()`/`tear_sheet()` finite/JSON-serializable (`default=str`) with `config/metrics/rebalances/attribution/attribution_totals`. **No production bug proven.**
- **`tests/test_bab_cli_edge_robustness_campaign11g.py`** (**untracked, NEW slice g**): 12 tests — adversarial backtest shapes at CLI/strategy boundary via monkeypatch (unnamed Series, named cumulative Series, ndarray, NaN/inf cumulative tail coerced finite, empty DataFrame, list, scalar) and `BABDataError`/generic-exception propagation on real-data + strategy paths (clean stdout, no traceback). **No production bug proven; no production edits.**

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1887/5 (current verified floor). Fix regressions before new work.
2. **Slice (h) — expand defensive robustness evidence (only if gaps remain):** (a) inspect `cli._json_safe/_json_default` handling of `np.datetime64` in nested structures (evidence: `_json_safe` passes `np.datetime64` through unchanged at top-level object checks except `hasattr(isoformat)`-less path — `json.dumps` with `default=_json_default` succeeds in probe, but `_json_safe` alone does not coerce; confirm end-to-end safety and add test if missing), `np.void`/bytes edge, and non-finite `np.float64` round-tripping via `_json_default` (returns string `'inf'` vs `_json_safe` returns `0.0` — two paths, verify `--output` always goes through `_json_safe` first so `allow_nan=False` holds). (b) strategy `run()` error wrapping for `BABDataError` on real-data boundary already covered; inspect `load_returns`/`load_prices` propagation through CLI `--from-prices` on malformed-but-existing fixtures (if any committed) for clean messages. Add tests only for proven/defensive gaps; **do not weaken assertions**. No speculative refactors. No production edits unless a real bug is proven with evidence + minimal regression test.
3. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
4. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1887/5 (or updated verified count with explanation); all touched BAB tests green.
5. **Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1887/5). Fix regressions before new work.
1. Execute campaign11 slice (h) end-to-end (inspect `cli._json_safe/_json_default` np.datetime64/np.void/bytes/non-finite path evidence before asserting; check committed fixtures for malformed cases if useful). Add tests only for proven/defensive gaps; run new tests + campaign_d + full excl (monitor `timeout>=450000`); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes (unblock next agent):**
- Full excl run completes (~168s) — use `background_process monitor timeout>=450000` or large shell timeout if needed.
- `rm -f .coverage .coverage.*` before canonical runs.
- **New untracked:** `tests/test_bab_cli_edge_robustness_campaign11g.py` (12 tests, slice g) — passes; keep/extend/track as appropriate; do not weaken.
- Slice e parity: CLI synthetic `BABStrategy(BABConfig(universe=None,...))` differs from shorthand defaults; assert against equivalent `BABConfig`.
- CLI `--output` path: `_build_output_summary` → `_json_safe` (sanitizes) → `json.dumps(..., default=_json_default, allow_nan=False)`. `_json_safe` returns `np.datetime64` unchanged (no `isoformat`); `json.dumps` resolves via `_json_default` → iso string (probe-verified). `_json_safe` coerces non-finite floats to `0.0`; `_json_default` may stringify in fallback — `_json_safe`-first ordering is the safety invariant.
- `_extract_cumulative`: unnamed Series/non-cum returns object → CLI `_coerce_finite_scalar` defaults to `1.0` (defensive). NaN/inf cumulative tail extracted as `None` by iloc path? (probe: `df cumulative [1.0,nan].iloc[-1]` returns `nan` from pandas → `_extract_cumulative` returns it; CLI coerces to default `1.0` at `main:315` — verified finite output).
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit**.
- Gates: `campaign_d` 883/5, full excl 1887/5 (re-verified this session @ `b391c6e`).

**ACTIVE:** campaign11 next = slice (h) defensive JSON/serialization path evidence + any proven gap (inspect `_json_safe/_json_default` np.datetime64/void/bytes/non-finite, `_json_safe`-first invariant). Slices (a)–(g) implemented/verified (74 campaign11 tests passing). campaign10 complete. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T18:49:11Z @ `b391c6e`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
