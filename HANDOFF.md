# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T19:10:37Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `7b4f89f` (`chore(kilo): checkpoint agent session`, local main). Working tree: **clean except untracked** `tests/test_bab_cli_slice_i_defensive_invariants.py` (new this session, slice (i), 22 tests, all passing). Do not commit/push unless explicitly requested.
**Environment:** deps `numpy/pandas/scipy/pytest` installed; `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`; `.coverage*` cleared before canonical runs.

**Baseline/gates (re-verified this session @ `7b4f89f`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, rc=0** (floor held)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1923 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 167s (0:02:47)** (floor raised 1901→1923 by +22 slice (i) tests; no production code changed)
- Real-data CLI end-to-end: `python -m strategies.betting_against_beta.cli --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output <tmp>` → **rc=0, `final_cumulative=0.3838`, `periods=398`, finite `allow_nan=False` JSON, no traceback** (README real-data path verified).

**campaign11 — BAB CLI/reporting + numeric robustness hardening:**
- Slices (a)–(h) implemented & verified (88 campaign11 tests passing incl. g/h). No production changes.
- **Slice (i) PROBED this session (defensive gaps beyond current evidence): NO production bug proven.**
  - (a) `_extract_cumulative`/`_coerce_finite_scalar` with `pd.NA`, `Decimal` NaN/inf, nullable/numpy scalar subclasses → always finite default, never raises. OK.
  - (b) `_json_safe`/`_json_default` with `pd.NaT`, `datetime.date`/`time`, `np.complexfloating`, `Decimal` NaN/inf, nested containers → `_json_safe`-first output remains `allow_nan=False`-safe (Decimal NaN → quoted `"NaN"` string; bare NaN/Infinity tokens never emitted). OK.
  - (c) CLI `--output` with `_build_output_summary` receiving exotic config/benchmark/universe (None, bytes, np.inf, pd.NaT, object) → finite JSON, no crash. OK.
  - (d) `--from-prices` on committed returns-like fixture `returns.json` → clean (rc 0/1, no traceback). OK.
  - **No production edits** (bug-fix rule: no proven bug → no edit).
- **Added:** `tests/test_bab_cli_slice_i_defensive_invariants.py` (22 tests) locking in the probed CLI JSON/finite boundary invariants so no future change can regress them silently.

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1923/5 (current verified floor). Fix regressions before new work.
2. **Real-data regression test (the heavy work):** add a test locking in the end-to-end real-data CLI path (`--data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output <tmp>` → rc 0, finite `allow_nan=False` JSON, `final_cumulative` finite scalar, `periods` int, no traceback; dry-run valid). Future agents must not skip this — the repo's purpose is real BAB backtests.
3. **Slice (i)-(d) defensive gaps only if proven:** probe before asserting; add tests only for proven/defensive gaps; **do not weaken assertions**. No speculative refactors. **No production edits unless a real bug is proven with evidence + minimal regression test.**
4. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
5. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1923/5 (or updated verified count with explanation); all touched BAB tests green.
6. **Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1923/5). Fix regressions before new work.
1. Add the real-data CLI end-to-end regression test (next focus campaign item 2). Run it + campaign_d + full excl (monitor `timeout>=450000`); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes (unblock next agent):**
- Full excl run completes (~167s) — use `background_process monitor timeout>=450000` or large shell timeout if needed.
- `rm -f .coverage .coverage.*` before canonical runs.
- New untracked: `tests/test_bab_cli_slice_i_defensive_invariants.py` (22 tests, slice i) — passes; keep/extend, do not weaken.
- CLI `--output` safety invariant (evidence): `_build_output_summary` → `_json_safe` → `json.dumps(..., default=_json_default, allow_nan=False)`. `_json_safe` coerces non-finite float/np.floating to `0.0`; leaves `np.datetime64` unchanged (no `isoformat`) but `_json_default`/json serializes it; handles np/pd containers, bytes, np.void stringification. Do not assume `_json_default` alone enforces `allow_nan=False`.
- `_extract_cumulative`: unnamed Series/non-cum returns object → CLI coerces to default `1.0`. NaN/inf cumulative tail values are extracted then coerced finite by CLI (`main:~315`) — verified.
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit**.
- Gates: `campaign_d` 883/5, full excl 1923/5 (re-verified this session @ `7b4f89f`).

**ACTIVE:** campaign11 next = real-data CLI end-to-end regression test (heavy, mandatory) + continue slice (i)-(d) defensive probing only if proven. Slices (a)–(i) implemented/verified; slice (i) probed — no bug, invariants locked in by 22 new tests. campaign10 complete. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T19:10:37Z @ `7b4f89f`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
