# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T04:51:18Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `6d7bbfd` (`chore(kilo): checkpoint agent session`, local `main`, unchanged this session)
**Working tree:** one untracked addition `tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py` (18 tests, green); no `.bab_active`/session-lock artifacts; nothing committed/pushed this session.
**Environment:** `python3 -m pip install --user numpy pandas scipy pytest hypothesis coverage` required this session (deps were missing). Run with `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`.

**Step 0 / gates (re-verified this session @ `6d7bbfd`, new module added):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py` → **65 passed, rc=0** (28+18+19)
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py` → **18 passed, rc=0**
- `rm -f .coverage .coverage.*; PYTHONPATH=$PWD python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3943 deselected, 53 warnings, rc=0**
- `PYTHONPATH=$PWD python3 -m pytest -q -k "not data_loader and not controller"` → **2052 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** (observed in ~231s via monitor; baseline floor unchanged)

**Bottlenecks removed:** missing Python deps installed in-session; prior campaign11o handoff's §NEXT FOCUS probes executed and locked where behavior is exercised-safe. No runtime/env blockers remain. Production fixes: none — **no proven gaps** requiring code change.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB surfaces and land minimal regressions/fixes only for proven gaps.

1. **Stabilize baseline:** run Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2052/5). Treat `tests/test_bab_cli_campaign11{m,n,o,p}_probe_regressions.py` as current evidence; do not revert without cause. Fix any regression before production edits.

2. **Execute next heavy probe matrix (§NEXT FOCUS)** against `tests/fixtures/real_market_prices_expanded.csv`, `tests/fixtures/real_market_prices.csv`, and constrained synthetic/temp inputs. For every probe capture command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits.

3. **Triage evidence:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the smallest production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.

4. **Validate:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (≥2052/5 or justified new floor with counts/rc). Record before/after.

5. **Refresh this HANDOFF.md** before finishing: timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit.

---

## CAMPAIGN11 follow-up — NEXT FOCUS (MANDATORY, HEAVY WORKING)

### Probe matrix (executed & locked @ `6d7bbfd` — no proven gaps)

| # | Combo | Evidence | Verdict |
|---|-------|----------|---------|
| 1 | Returns-path + `--transaction-costs`/`--slippage` parity on **real** fixture `tests/fixtures/real_market_prices.csv` (4 combos: 0.001/0.0005, 0.01/0, 0/0.01, 0.005/0.005) vs in-process `BABStrategy`, strict finite JSON | rc=0 all; exact `final_cumulative`/`periods`/`benchmark`/`universe` match in-process (diff=0.0, finite); CLI output keys `final_cumulative,periods,benchmark,universe` | PASS — locked in 11p |
| 2 | `--dry-run` invalid-data cleanliness on **both** fixtures: missing file, directory, unsupported extension (`README.md`), bad benchmark (`NOTHERE` on from-prices) | all rc=1, `Traceback` absent, actionable `INVALID: ...` messages (e.g. "data file not found", "Path is a directory", "Unsupported data source extension", "Benchmark ... not found") | PASS — locked in 11p |
| 3 | `--dry-run` whitespace-only `--universe` tokens (`""`, `"   "`) on expanded fixture | rc=1, no Traceback, clean "must contain at least one non-empty asset token" | PASS — locked in 11p |
| 4 | `--synthetic` parity on CLI vs in-process across alternate configs: BTC/None, SOL/None, BTC/[BTC,ETH,SOL], ETH/[BTC,ETH,SOL,ADA] | rc=0, strict finite JSON, exact `final_cumulative`/`periods`/`benchmark`/`universe` (diff=0.0) | PASS — locked in 11p |

**Observed exercised behaviors (not proven gaps this slice):**
- `--dry-run` validates data loading/benchmark presence and prints config, but does **not** enforce all run-time/config semantics (probed: `--long-quantile 0.6 --short-quantile 0.6`, `--universe ZZZ,YYY`/`,,,` with from-prices reported `valid` rc=0 on dry-run; actual run rejects no-overlap universe rc=1 clean and accepts quantile-sum≥1.0 rc=0 finite per existing contracts/tests). No evidence of crash/Traceback; treat as potential contract-clarity follow-up only if proven harmful.
- `--synthetic --data ...` and `--from-prices` without `--data` run synthetic path (rc=0 finite) — exercised, not newly regressed.

**Gaps found/fixed:** explicit **no proven gaps** requiring production change. New regression locks only: `tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py`.

### Remaining unprobed combos (priority order for next session) — §NEXT FOCUS

1. **Dry-run semantic gap audit (evidence-first):** determine whether dry-run should reject `--universe` tokens with zero overlap / quantile-invalid configs the same way a real run does (compare to existing dry-run contract/tests like `test_bab_cli_*dry*`, `campaign11m` output-validation semantics). If contract requires stricter validation, add minimal fix+regression; if intentional, lock current behavior explicitly in campaign11 tests (avoid duplicating existing dry-run suites).
2. **Real fixture (`real_market_prices.csv`) CLI parity:** from-prices path with `--transaction-costs`/`--slippage`/`--rebalance-freq` combos vs in-process `load_prices`+`BABStrategy` (returns-path parity locked in 11p; price-input parity still worth explicit lock).
3. **Malformed/edge data dry-run:** empty CSV, header-only, single-column, duplicate index/columns, NaT-heavy dates, mixed inf/nan rows on both fixtures/temp files — require rc=1 clean actionable INVALID or documented rc=0 finite behavior per loader contract (no Traceback).
4. **`--output` edge cases:** pre-existing read-only target/unwritable parent (if creatable in sandbox), deep nested path creation, `--dry-run --output` with invalid data (must fail for data/output reason as appropriate, never write).

### GATES THAT MUST STAY GREEN

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2052 passed, 5 skipped**
- `test_bab_cli_campaign11m_probe_regressions.py` (28), `test_bab_cli_campaign11n_expanded_probe_regressions.py` (18), `test_bab_cli_campaign11o_remaining_probe_regressions.py` (19), `test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py` (18) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked per prior notes; other module miss-closures per prior handoff/proofs remain binding unless disproven by evidence.

## IMMEDIATE ACTIONS (no planning-only exit)

1. Run Step 0 gates on current tree; confirm 11m–11p probe regression modules passing with baseline floors.
2. Probe §NEXT FOCUS #1 (dry-run semantic audit) first — gather evidence against existing tests/contracts before any fix; then #2–#4. Log rc/stdout/stderr/JSON snippets.
3. Add minimal non-duplicative `tests/test_bab_*campaign11*` for any proven gap; minimal prod fix only if bug proven. Re-run touched + gates.
4. Refresh this `HANDOFF.md` with evidence and next binding slice.

---
*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place.*
