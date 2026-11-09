# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T17:19:41Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `2ebbeb4` (`chore(kilo): checkpoint agent session`, local main). Working tree: **untracked `tests/test_bab_cli_error_reporting.py` added this session** (slice d); `HANDOFF.md` modified by this session. Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `2ebbeb4`, deps installed `numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3747 deselected, 53 warnings, rc=0**
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1856 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 149.51s** (FULL RUN COMPLETED; verified floor **1856/5**, above prior 1847/5)
- campaign11 tests: `tests/test_bab_cli_reporting_robustness.py tests/test_bab_cli_error_reporting.py` → **43 passed, rc=0** (34 + 9)

**campaign11 — IN PROGRESS (slices a/b/c/d implemented & verified this session/no production changes):**
- **`tests/test_bab_cli_reporting_robustness.py`** (committed @ `2ebbeb4`, 34 tests): CLI/output robustness across all 4 sources (returns.json, real_market_prices*.csv `--from-prices`, synthetic `--beta-window 30`) — nested `--output` path, overwrite byte-determinism, schema/finite/type stability; `--dry-run`/`--dry-run --output` validates without writing; real-fixture backtest index monotonic + cumulative finite/no NaN/Inf + weights no Inf; README↔CLI contract smokes (flags accepted, `--version` rc=0 contains `__version__=="0.1.0"`).
- **`tests/test_bab_cli_error_reporting.py`** (added this session, 9 tests, untracked): evidence-first CLI error-path robustness — `--dry-run --data <missing>` / `--from-prices` missing → rc=1 + INVALID/not-found message, no crash; `--output` is existing directory (real run + dry-run) → rc=1, directory preserved; unwritable parent (best-effort chmod, skip if FS ignores perms) → rc=1, file not created; nonexistent `--data` real run → rc=1 actionable error; `--dry-run --data <directory>` → rc=1; valid `--dry-run --from-prices` fixture → rc=0; successful synthetic with explicit flags keeps schema stable (`periods>0`, benchmark/universe keys present). **No production bug proven; no production edits.**

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1856/5 (current verified floor). Fix regressions before new work.
2. **Slice (e) — broader numeric/reporting invariants (evidence-first):** extend robustness/error tests (or `tests/test_bab_cli_numeric_reporting.py`) to assert: for CLI `--output` runs across committed fixtures + synthetic, `periods` equals `len(result.backtest)` parity where practically reproducible (or assert CLI `periods` equals strategy run length for same inputs/config); `final_cumulative` equals tail cumulative parity for deterministic synthetic config; confirm JSON numeric fields finite under `allow_nan=False` path (already exercised) and no unexpected NaN/Inf in summary; param `--universe` subset only if CLI argparse contract is confirmed (inspect CLI first — avoid speculation). Fix minimally with regression only if a real bug is proven.
3. **Slice (f) — backtest/metrics contract smoke on real fixtures:** parametrize real fixtures to confirm `result.backtest` has `cumulative` column and finite tail; if `result.metrics` or other exposed stable attributes exist, assert finite scalars only when present (do not invent APIs). Add CLI↔strategy parity smoke for a small deterministic synthetic config if cheap/stable.
4. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
5. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1856/5 (or updated verified count with explanation); all touched BAB tests green.
6. **Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1856/5). Fix regressions before new work.
1. Execute campaign11 slice (e) end-to-end (evidence-first, inspect CLI/strategy contracts before asserting); run new tests + campaign_d + full excl (monitor if needed); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes (unblock next agent):**
- Full excl run completes (~149s) — use `background_process monitor timeout>=360000` if shell tool times out.
- `rm -f .coverage .coverage.*` before canonical runs.
- `real_market_prices*.csv` produce meaningful cumulatives (≈0.384 / 0.652); `returns.json` can be flat at some windows — assert finite/deterministic, not specific alpha unless deterministic.
- Synthetic with `--beta-window 30` yields `periods=252`, finite cumulative (~0.452) — deterministic.
- CLI `--dry-run --output` validates path without writing (`cli.py:231-241`); dry-run validates `--data` and prints config.
- CLI output schema (`_build_output_summary`): `final_cumulative` (finite-coerced float), `periods` (int), `benchmark`, `universe` (list[str]); JSON `allow_nan=False` + `_json_default`/`_json_safe`.
- `_validate_output_path` rejects directory targets and non-writable probe targets (`cli.py:34-67`).
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit**.
- `tests/test_bab_cli_error_reporting.py` added this session (untracked) — keep/extend as campaign11 evidence; do not weaken.

**ACTIVE:** campaign11 next = slice (e) broader numeric/reporting invariants (evidence-first) → slice (f) backtest/metrics contract smoke. Slices (a)/(b)/(c)/(d) implemented/verified (43 tests passing). campaign10 complete. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T17:19:41Z @ `2ebbeb4`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.