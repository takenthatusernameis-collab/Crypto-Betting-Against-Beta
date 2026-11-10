# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T04:05:00Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD at session start:** `18339ed` (`chore(kilo): checkpoint agent session`, local `main`)
**Working tree:** DIRTY (intentional, uncommitted) — `M HANDOFF.md`, `?? tests/test_bab_cli_campaign11m_probe_regressions.py` (28 probe-backed regressions added this session). Tracked `probe*`/`debug*`/`ast_probe.py` untouched. No `.bab_active`/session-lock artifacts found.
**Environment:** run with `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`.

**Step 0 gates (re-verified this session @ `18339ed` baseline):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; PYTHONPATH=$PWD python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3878 deselected, 53 warnings, rc=0** (baseline); **883 passed, 5 skipped, 3906 deselected, 53 warnings, rc=0** (post-change recheck)
- `PYTHONPATH=$PWD timeout 300 python3 -m pytest -q -k "not data_loader and not controller"` → **1987 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** (baseline, 4:23); **2015 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** (post-change, 5:04; floor raised by +28 campaign11m tests)

**Bottlenecks removed:** stale handoff SHA/timestamp drift corrected; campaign11b probe matrix executed with evidence and locked by regressions. No runtime/env blockers remain.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11b/campaign11m-followup** for `Crypto-Betting-Against-Beta` from this dirty working tree. Objective: keep producing probe-backed evidence on exercised BAB surfaces and land minimal regressions/fixes only for proven gaps.

1. **Stabilize baseline:** run Step 0 gates (deps, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2015/5). Treat `tests/test_bab_cli_campaign11m_probe_regressions.py` as part of the current evidence set; do not revert without cause. Fix any regression before production edits.
2. **Execute next heavy probe matrix (§NEXT FOCUS)** against `tests/fixtures/real_market_prices.csv`, `real_market_prices_expanded.csv`, and constrained synthetic/temp inputs. For every probe capture command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits.
3. **Triage evidence:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the smallest production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.
4. **Validate:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (≥2015/5 or justified new floor with counts/rc). Record before/after.
5. **Refresh this HANDOFF.md** before finishing: timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit.

## CAMPAIGN11b/m — NEXT FOCUS (MANDATORY, HEAVY WORKING)

### Probe matrix (continue, evidence-first)
- **(a) CLI-vs-in-process parity (expand):** exercised combos not yet locked across both fixtures (`real_market_prices.csv`, `real_market_prices_expanded.csv`): `--from-prices` + `--beta-window`/`--rebalance-freq`/quantiles/cost/slippage permutations, `--universe` subsets/overlaps/order/duplicates/benchmark-in-universe, returns-path parity, `--dry-run`+valid data permutations, `--output` overwrite/parent-creation paths. Assert exact `final_cumulative`/`periods`/`benchmark`/`universe`, strict finite JSON.
- **(b) Non-finite/degenerate propagation:** temp CSV/returns with NaN/Inf/-Inf at edges (first/last row, whole-window warmup, multi-column sparse, benchmark-only defects), all-NaN non-benchmark columns, zero/negative/constant prices through `--from-prices`, empty-after-filtering scenarios. Verify rc/Traceback absence and finite-safe JSON or clean `BABDataError` per exercised contract.
- **(c) Error-path cleanliness & stability:** unreadable/missing/dir/conflicting paths, unsupported extensions, whitespace/malformed tokens, extreme but admissible numeric args vs data length, quantile boundary/interaction edges (e.g. sums, overlaps) as exercised by config/CLI, `--dry-run` invalid-data combinations. Require stable actionable messages, `rc==1` on failure, no Traceback.
- **(d) Integration edges:** `cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` branches surfaced by (a)-(c) (exercised only; no dead-code/gate-closed chasing).

### Evidence logged this session (2026-11-10, @18339ed baseline)
- **Parity (a) — all matched in-process, rc=0, strict finite JSON, no bad tokens:** real fixture `--from-prices` combos `{beta_window:30}`, `{rebalance_freq:weekly}`, `{rebalance_freq:monthly}`, `{long_quantile:0.2,short_quantile:0.2}`, `{beta_window:45,transaction_costs:0.002,slippage:0.001,rebalance_freq:weekly}`; returns-path CSV combos default and `{rebalance_freq:weekly,transaction_costs:0.001}`. Exact `final_cumulative`/`periods`/`benchmark`/`universe` parity confirmed.
- **Dry-run/output:** `--dry-run` with valid data+`--output` → rc=0, output file not written (validated only). `--dry-run` with directory `--output` → rc=1, clean "directory, not a file" message, no Traceback.
- **Non-finite (b):** admissible NaN injections (`single_nan_eth`, `sparse_nans_sol`, `nan_benchmark_btc`) → rc=0, finite JSON (fc/periods finite). Infinite injections (`inf_asset_bnb`, `-inf_asset_bnb`, `inf_benchmark_btc`) → rc=1, clean "Returns DataFrame contains infinite values", no payload/Traceback. All-but-one-NaN asset column (`ADA`) → rc=1, clean "Insufficient finite history..." (names asset), no Traceback.
- **Error paths (c) — all rc=1, no Traceback, actionable:** missing file, directory-as-data, unsupported extension, whitespace-only universe tokens, missing benchmark, universe with no overlap, `long_quantile` 0/-0.1, negative `transaction_costs`/`slippage`. Exercised (no Traceback): `--beta-window 1` and `9999` rc=0 with finite JSON; `long_quantile+short_quantile` sum>1 accepted by config/CLI and ran (rc=0) — treated as exercised behavior pending spec, not altered.
- **Production fixes:** none required/proven (behaviors defensive as exercised). **Tests added:** `tests/test_bab_cli_campaign11m_probe_regressions.py` (28 passed) locking parity/non-finite/dry-run/error invariants above.

## GATES THAT MUST STAY GREEN
- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2015 passed, 5 skipped** (current verified floor)
- All touched/new BAB tests green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)
- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked; other module miss-closures per prior handoff/proofs remain binding unless disproven by evidence.

## IMMEDIATE ACTIONS (no planning-only exit)
1. Run Step 0 gates on current dirty tree; confirm `test_bab_cli_campaign11m_probe_regressions.py` included/passing.
2. Probe (a)-(d) on `real_market_prices_expanded.csv` + edge-case temp inputs (first/last-row defects, constant/zero/negative prices, all-NaN non-benchmark, quantile/universe interaction edges). Log rc/stdout/stderr/JSON snippets.
3. Add minimal non-duplicative `tests/test_bab_*campaign11*` for any proven gap; minimal prod fix only if bug proven. Re-run touched + gates.
4. Refresh this `HANDOFF.md` with evidence and next binding slice.

---
*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place.*
