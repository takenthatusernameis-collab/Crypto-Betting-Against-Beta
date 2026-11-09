# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T17:10:39Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `be250a3` (`chore(kilo): checkpoint agent session`, local main). Working tree: **modified (untracked test added by this session: `tests/test_bab_cli_reporting_robustness.py`)** — do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `be250a3`, deps installed `numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`
- `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3738 deselected, 53 warnings, rc=0**
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1813 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 134.28s** (FULL RUN COMPLETED; verified floor **1813/5**). Use `background_process` action `monitor` with `timeout>=360000` if a shell tool timeout would interrupt capture.
- Combined real-data repro: `tests/test_bab_real_data_cli_repro.py tests/test_bab_real_data_repro.py` → **8 passed, rc=0** (repro file) / prior combined 13 passed baseline unchanged in intent; `test_bab_real_data_cli_repro.py` **8 passed**.

**campaign11 — IN PROGRESS (slices a/b/c implemented & verified this session):**
- **Added `tests/test_bab_cli_reporting_robustness.py` (34 tests, rc=0, no production changes).** No real bug found requiring fix.
  - **Slice (a) CLI/output robustness:** nested `--output` path created by CLI → rc=0, finite schema-stable JSON; overwrite existing file → rc=0, byte-identical repeat; schema keys/types stable + finite + byte-deterministic across all 4 sources (parametrized): `tests/fixtures/returns.json`, `tests/fixtures/real_market_prices.csv` (`--from-prices`), `tests/fixtures/real_market_prices_expanded.csv` (`--from-prices`), `--synthetic --output --beta-window 30` (`periods>0`, finite cumulative).
  - **Dry-run:** `--dry-run --synthetic` rc=0; `--dry-run --output <path>` validates without writing (assert file NOT created); existing file not overwritten under dry-run.
  - **Slice (b) numeric invariants (real fixtures):** on `real_market_prices*.csv` via `load_prices`→`BABStrategy.run`: backtest index monotonic increasing; `cumulative` first/last finite; no NaN/Inf in cumulative array; `weights` contain no Inf when present (NaN warmup allowed).
  - **Slice (c) README↔CLI contract (evidence-first, test-only):** README-documented flags accepted via parse/smoke (`--dry-run --synthetic` + flags), `--version` exits 0 and contains `__version__`, `cli.__version__ == "0.1.1"?` **no — verified `__version__ == "0.1.0"` matches module**; README presence asserted for all documented flags. No production mismatch proven.

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1813/5. Fix regressions before new work.
2. **Slice (d) — CLI error-path/reporting robustness (committed fixtures + synthetic; no external data):** add `tests/test_bab_cli_error_reporting.py` (preferred). Evidence-based against current behavior:
   - `--output` to an unwritable/protected target (e.g., path under a read-only dir in tmp, or a directory path passed as file where CLI rejects) → clean nonzero rc + actionable error (CLI validates via `_validate_output_path`; assert rc!=0 and message/behavior stable). Use tmp permissions carefully (cross-platform safe) or existing-directory-as-output case.
   - `--dry-run --data <nonexistent>` / bad fixture path → rc!=0, no crash/trace leak beyond normal CLI error text (assert rc!=0).
   - `--from-prices` misuse / incompatible combos only if contract is clear from CLI; otherwise skip speculative cases.
   - `--output` JSON remains schema-stable on successful synthetic runs with explicit config flags (`--universe` subset behavior if accepted, or document via test what argparse accepts) — **evidence-first**: inspect CLI before asserting.
3. **Slice (e) — broader numeric/reporting invariants:** extend robustness tests (or new file) to assert `periods` equals backtest length for CLI-output runs across fixtures; `final_cumulative` equals `result.backtest['cumulative'].iloc[-1]` parity (synthetic deterministic config) where practical; no NaN/Inf in any JSON numeric field (`allow_nan=False` path exercised). Fix minimally with regression only if a real bug is proven.
4. **Slice (f) — backtest/metrics contract smoke on real fixtures:** parametrize real fixtures to confirm `result.backtest` has `cumulative` column and finite tail; if `result.metrics` or other exposed stable attributes exist, assert finite scalars only when present (do not invent APIs).
5. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
6. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1813/5 (or updated verified count with explanation); all touched BAB tests green.
7. **Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1813/5). Fix regressions before new work.
1. Execute campaign11 slice (d) end-to-end (evidence-first); run new tests + campaign_d + full excl (monitor if needed); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**). BAB package slice **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes (unblock next agent):**
- Full excl run completes (~134s) — not a blocker; capture with `background_process monitor timeout>=360000` if the shell tool times out.
- `rm -f .coverage .coverage.*` before canonical runs to avoid stale coverage artifacts.
- `real_market_prices*.csv` produce meaningful cumulatives (≈0.384 / 0.652) unlike `returns.json` (1.0, flat-zero weights at window 90/8 rows) — assert finite/deterministic, not specific alpha.
- Synthetic with `--beta-window 30` yields `periods=252`, finite cumulative (~0.452) — deterministic; default config may differ.
- `--dry-run --output` validates path without writing (`cli.py:231-241`); dry-run also prints resolved config and validates `--data`.
- CLI output schema (`_build_output_summary`): `final_cumulative` (float, finite-coerced), `periods` (int), `benchmark`, `universe` (list[str]); JSON uses `allow_nan=False` + `_json_default`/`_json_safe`.
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit**.
- `tests/test_bab_cli_reporting_robustness.py` added this session (untracked) — keep/extend as campaign11 evidence; do not weaken.

**ACTIVE:** campaign11 next = slice (d) CLI error-path/reporting robustness (evidence-first). Slices (a)/(b)/(c) implemented in `tests/test_bab_cli_reporting_robustness.py` (34 passed). campaign10 complete. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T17:10:39Z @ `be250a3`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
