# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-10T02:59:52Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice; every change must serve BAB correctness/robustness and be justified by probe evidence)
**HEAD:** `258798c` (`chore(kilo): checkpoint agent session`) — local `main`.
**Working tree:** clean at handoff time. Tracked `probe*`/`debug*`/`ast_probe.py` exist — **do not edit/commit** unless explicitly requested.
**Environment:** deps `numpy/pandas/scipy/pytest` expected installed; run gates with `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`.

**Last verified gates (this session @ `258798c`, 2026-11-10T02:59Z):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; PYTHONPATH=$PWD python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3878 deselected, 53 warnings, rc=0**
- `PYTHONPATH=$PWD python3 -m pytest -q -k "not data_loader and not controller"` → **1987 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** (floor ≥1987/5)
- Spot-check green: `tests/test_bab_cli_universe_{subset,edge,explicit_contract}.py`, `tests/test_bab_cli_warmup_parity_campaign11.py`, `tests/test_bab_cli_real_data_regression_campaign11.py`, `tests/test_bab_cli_slice_i_defensive_invariants.py`, `tests/test_bab_cli_universe_whitespace_dryrun_campaign11k.py`, `tests/test_bab_cli_parity_error_campaign11l.py`

**State / bottlenecks:** `campaign11k`/`campaign11l` locked; campaign7 floor LOCKED. `beta.py` (92%) and `data_loader.py` (98%/40 miss) **GATE CLOSED — DO NOT ALTER**. No active session locks/`.bab_active` found. **No blocking bottlenecks**; heavy campaign11b work is required, not optional.

---

## BINDING INITIAL TASK MESSAGE (for next agent — execute immediately, do not defer)

You are resuming **campaign11b** on `Crypto-Betting-Against-Beta` at current HEAD `258798c`. Your first and only directive:

1. **Re-run Step 0 gates** (deps, `campaign_d` 883/5, full BAB excl `data_loader`/`controller` ≥1987/5). Fix any regression before touching production code.
2. **Run the heavy probe matrix (§2)** against `tests/fixtures/real_market_prices.csv` and synthetic/constrained inputs: (a) CLI-vs-in-process parity for additional exercised flag combos, (b) non-finite propagation boundaries (inject NaN/Inf), (c) error-path cleanliness & message stability, (d) integration edges in `cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`.
3. **Log rc/stdout/stderr/JSON snippets for every probe.** Do not stop at the first pass — probe combinations until you have evidence (pass or proven gap).
4. **For each proven gap:** write minimal non-duplicative regression test(s) in `tests/test_bab_*campaign11*`, fix production minimally if a real bug is proven, re-run gates + touched tests, record before/after counts.
5. **Refresh this HANDOFF.md** (timestamp/SHA/dirty-state, commands+counts+rc, modules touched, proven gaps/fixes, next slice) before finishing.

**Prohibited exits:** planning-only exit, no-evidence exit, gate-closed churn (`beta.py`, `data_loader.py`), tracked `probe*`/`debug*`/`ast_probe.py` edits, `.github/workflows/*` edits, weakening `campaign_d*`/`batch148/149/172`. No commit/push unless explicitly requested.

## CAMPAIGN11b — NEXT FOCUS (MANDATORY, HEAVY WORKING; NOT AVOIDABLE)

### 1) Step 0 gates (must pass before any edit)
- Deps import.
- `campaign_d` 883/5 green (ignore `tests/test_controller_progress_accounting.py`).
- Full BAB suite excluding `data_loader` and `controller` must stay ≥1987/5 (current verified floor). Fix any regressions before new work.

### 2) Heavy probe matrix (evidence-first; run before changing production)
Probe against real fixture `tests/fixtures/real_market_prices.csv` and synthetic/constrained inputs. Capture `rc/stdout/stderr/JSON` for each.

- **(a) CLI-vs-in-process parity** — extend beyond campaign11l: test additional exercised combos (`--beta-window` override, `--rebalance-freq`, `--long-quantile`/`--short-quantile`, combinations with `--transaction-costs`+`--slippage`, `--from-prices`, valid `--dry-run`+`--output` already locked but re-confirm). Assert exact match for `final_cumulative`/`periods`/`benchmark`/`universe` and strict finite JSON.
- **(b) Non-finite propagation boundaries** — inject constrained NaN/Inf via temp CSV/returns (single column, sparse, all-but-one NaN, Inf, -Inf). Probe CLI (`--data` + `--from-prices` or returns path) and `BABStrategy.run()` paths. Verify no Tracebacks, JSON remains finite-safe (`_json_safe`/`_json_default`/`_coerce_finite_scalar`/`_build_output_summary`, `allow_nan=False`), behavior is defensive (graceful/defined). Look for leaks into printed/`--output` JSON.
- **(c) Error-path cleanliness & message stability** — probe unreadable perms (if feasible), conflicting/unsupported extensions, extreme numeric args (e.g. very large/small `--beta-window` vs data length), empty universe after normalization, missing benchmark, directory as file, whitespace-only tokens, partial overlaps. Require `rc==1`, no Traceback, stable actionable messages.
- **(d) Integration edges** — probe `strategies/betting_against_beta/cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py` for reachable-but-untested branches surfaced by (a)-(c) (focus on exercised paths, not dead code).

### 3) Prove gaps, add minimal tests/fixes
- **Only** add tests for **proven, non-duplicative** gaps. Put in a focused `tests/test_bab_*campaign11*` module (do not bloat existing campaign modules).
- **Bug fix rule:** if a real bug is proven with evidence, fix **minimally** in production + add a regression test + re-run gates + record before/after.
- **No coverage-chasing** of gate-closed modules (`beta.py` dead/unreachable, `data_loader.py` strict-4 misses at 322/326 and closed mechanism misses).

### 4) Gates that must stay green
- `campaign_d` 883/5
- Full BAB excl `data_loader`/`controller` ≥1987/5 (or updated verified count with explanation)
- All touched/new BAB tests green

## IMMEDIATE ACTIONS (execute in order, no planning-only exit)
1. **Step 0 gates** — deps, `campaign_d`, full excl suite. Fix regressions before new work.
2. **Heavy probe pass** — run (a)-(c) with concrete commands against real fixture/synthetic/constrained inputs; log rc/stdout/stderr/JSON snippets. Do **not** stop at first pass — probe combinations until you have evidence (pass or proven gap).
3. **Act on evidence** — for each proven gap write minimal non-duplicative test(s); fix production minimally if bug proven. Re-test touched modules.
4. **Validate** — run new/touched tests + `campaign_d` + full excl (timeout ≥450000). Record counts/rc/modules touched/deltas.
5. **Handoff refresh** — update this file (timestamp/SHA/dirty-state, commands+counts+rc, modules touched, proven gaps/fixes, next slice). Keep §INITIAL TASK MESSAGE binding. Do not revert uncommitted tests without cause.

## PROHIBITED
- `.github/workflows/*` edits
- Gate-closed churn (`beta.py` dead/unreachable, `data_loader.py` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**)
- Tracked `probe*`/`debug*`/`ast_probe.py` edits/commits
- Weakening/deleting `batch148/149/172` or `campaign_d*`
- No commit/push unless explicitly requested

## COVERAGE EVIDENCE (LOCKED)
`portfolio.py` 100% (244/0). `sizing.py` 100% (176/0). `cli.py` 100% (320/0). `strategy.py` 100% (306/0). `signals.py` 98% (miss `37,75`), `metrics.py` 99% (miss `97`), `config.py` 99% (miss `123-124`), `costs.py` 98% (miss `59-60`) closed-without-edit. `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (**DO NOT ALTER**).

---

# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
Canonical handoff file: `HANDOFF.md` (refreshed 2026-11-10T02:59:52Z @ `258798c`, clean). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE + §BINDING INITIAL TASK MESSAGE above are binding. No competing handoff files.