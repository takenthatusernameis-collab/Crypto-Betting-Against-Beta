# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T04:25:00Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `a4d2f93` (`chore(kilo): checkpoint agent session`, local `main`, unchanged this session)
**Working tree:** one untracked addition `tests/test_bab_cli_campaign11o_remaining_probe_regressions.py` (19 tests, green); no `.bab_active`/session-lock artifacts; nothing committed/pushed this session.
**Environment:** run with `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`. Deps OK (`numpy,pandas,scipy,pytest`).

**Step 0 / gates (re-verified this session @ `a4d2f93`, new module added):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py` → **28 passed, rc=0**
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11n_expanded_probe_regressions.py` → **18 passed, rc=0**
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11o_remaining_probe_regressions.py` → **19 passed, rc=0**
- `rm -f .coverage .coverage.*; PYTHONPATH=$PWD python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3943 deselected, 53 warnings, rc=0**
- `PYTHONPATH=$PWD timeout 600 python3 -m pytest -q -k "not data_loader and not controller"` → **2052 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** — floor raised 2033 → 2052 (+19 from new campaign11o module)

**Bottlenecks removed:** campaign11b/11m/11n probe matrix previously executed against both fixtures; campaign11o (#1-7 below) executed and locked. No runtime/env blockers remain. Production fixes: none — **no proven gaps**; every exercised behavior defensive/as-contracted (one apparent #2 synthetic mismatch traced to probe construction, not product: apples-to-applies `universe=None` parity diff=0.0).

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB surfaces and land minimal regressions/fixes only for proven gaps.

1. **Stabilize baseline:** run Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2052/5). Treat `tests/test_bab_cli_campaign11{m,n,o}_probe_regressions.py` as part of the current evidence set; do not revert without cause. Fix any regression before production edits.

2. **Execute next heavy probe matrix (§NEXT FOCUS)** against `tests/fixtures/real_market_prices_expanded.csv`, `tests/fixtures/real_market_prices.csv`, and constrained synthetic/temp inputs. For every probe capture command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits.

3. **Triage evidence:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the smallest production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.

4. **Validate:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (≥2052/5 or justified new floor with counts/rc). Record before/after.

5. **Refresh this HANDOFF.md** before finishing: timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit.

---

## CAMPAIGN11 follow-up — NEXT FOCUS (MANDATORY, HEAVY WORKING)

### Probe matrix (#1-7 executed & locked @ `a4d2f93` — no proven gaps)

| # | Combo | Evidence | Verdict |
|---|-------|----------|---------|
| 1 | Returns-path + `--transaction-costs`/`--slippage` matrix on expanded fixture (5 combos) | CLI==in-process parity, rc=0, strict finite JSON, exact `final_cumulative`/`periods`/`benchmark`/`universe` | PASS — locked in 11o |
| 2 | `--synthetic` + config overrides parity on CLI | apparent mismatch was probe artifact (omitted `universe=None` → default 8 assets vs CLI's 5 ASSET); apples-to-apples `universe=None` diff=0.0, rc=0 finite | PASS — locked in 11o |
| 3 | Multi-column sparse NaNs (ETH/SOL/BNB scattered NaNs simultaneously, expanded from-prices) | rc=0, strict finite JSON | PASS — locked in 11o |
| 4 | Benchmark-only NaN / all-Inf (BTC column) with valid assets | rc=1 clean, no Traceback ("Benchmark not found" / "infinite values") | PASS — locked in 11o |
| 5 | Quantile sum/boundary (0.6/0.6 sum≥1 → finite; 0.0/1.0 boundaries → clean rc=1 config error) | no Traceback, actionable messages | PASS — locked in 11o |
| 6 | `--output` overwrite semantics | rc=0 both writes, stale content replaced, finite JSON | PASS — locked in 11o |
| 7 | Extreme `--beta-window` vs short data (expanded 9999/1000, real 9999, short 10-row slice window=500) | rc=0, no Traceback, finite JSON (short slice degenerate fc=1.0 periods=9) | PASS — locked in 11o |

**Gaps found/fixed:** explicit **no proven gaps** across all areas (a)-(d). No production fix required or applied.

### Remaining unprobed combos (priority order for next session) — §NEXT FOCUS

1. Returns-path + `--transaction-costs` + `--slippage` parity on `real_market_prices.csv` (real fixture; expanded done in 11o, real not yet locked) vs in-process `BABStrategy`, strict finite JSON.
2. `--dry-run` invalid-data combinations: missing/unreadable/dir/conflicting paths, unsupported extensions, whitespace/malformed tokens — require rc=1, stable actionable message, no Traceback (on both fixtures).
3. CLI `--dry-run` + invalid-data combinations (invalid quantile, bad benchmark, no-overlap universe) on expanded fixture.
4. `--synthetic` parity across alternate benchmarks (`BTC`, `SOL`) and `--universe` subsets on CLI vs in-process.

### GATES THAT MUST STAY GREEN

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2052 passed, 5 skipped** (current verified floor)
- `test_bab_cli_campaign11m_probe_regressions.py` (28), `test_bab_cli_campaign11n_expanded_probe_regressions.py` (18), `test_bab_cli_campaign11o_remaining_probe_regressions.py` (19) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked; other module miss-closures per prior handoff/proofs remain binding unless disproven by evidence.

## IMMEDIATE ACTIONS (no planning-only exit)

1. Run Step 0 gates on current tree; confirm 11m+11n+11o probe regression modules passing with baseline floors.
2. Probe §NEXT FOCUS combos (real fixture returns-path cost/slippage parity; `--dry-run` invalid-data cleanliness on both fixtures). Log rc/stdout/stderr/JSON snippets.
3. Add minimal non-duplicative `tests/test_bab_*campaign11*` for any proven gap; minimal prod fix only if bug proven. Re-run touched + gates.
4. Refresh this `HANDOFF.md` with evidence and next binding slice.

---
*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place.*
