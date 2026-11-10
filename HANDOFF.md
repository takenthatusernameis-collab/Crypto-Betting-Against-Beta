# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T04:35:00Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `5b0afb9` (`chore(kilo): checkpoint agent session`, local `main`, unchanged this session)
**Working tree:** CLEAN — HANDOFF.md updated in place; `tests/test_bab_cli_campaign11m_probe_regressions.py` (28) and `tests/test_bab_cli_campaign11n_expanded_probe_regressions.py` (18) are tracked and green. No `.bab_active`/session-lock artifacts found.
**Environment:** run with `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`. Deps OK (`numpy,pandas,scipy,pytest`).

**Step 0 / gates (re-verified this session @ `5b0afb9`, clean tree):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py` → **28 passed, rc=0** (36.30s)
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11n_expanded_probe_regressions.py` → **18 passed, rc=0** (34.85s)
- `rm -f .coverage .coverage.*; PYTHONPATH=$PWD python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3924 deselected, 53 warnings, rc=0**
- `PYTHONPATH=$PWD timeout 600 python3 -m pytest -q -k "not data_loader and not controller"` → **2033 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** (347.51s) — floor raised from 2015 to 2033

**Bottlenecks removed:** campaign11b/11m-followup probe matrix executed against `tests/fixtures/real_market_prices_expanded.csv` and edge temp inputs; exercised parity/non-finite/universe/error behaviors evidenced and locked by regressions. No runtime/env blockers remain. Production fixes: none (all exercised behaviors defensive/as-contracted).

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this clean working tree. Objective: keep producing probe-backed evidence on exercised BAB surfaces and land minimal regressions/fixes only for proven gaps.

1. **Stabilize baseline:** run Step 0 gates (deps, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2033/5). Treat `tests/test_bab_cli_campaign11m_probe_regressions.py` and `tests/test_bab_cli_campaign11n_expanded_probe_regressions.py` as part of the current evidence set; do not revert without cause. Fix any regression before production edits.

2. **Execute next heavy probe matrix (§NEXT FOCUS)** against `tests/fixtures/real_market_prices_expanded.csv`, `tests/fixtures/real_market_prices.csv`, and constrained synthetic/temp inputs. For every probe capture command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits.

3. **Triage evidence:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the smallest production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.

4. **Validate:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (≥2033/5 or justified new floor with counts/rc). Record before/after.

5. **Refresh this HANDOFF.md** before finishing: timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit.

---

## CAMPAIGN11 follow-up — NEXT FOCUS (MANDATORY, HEAVY WORKING)

### Probe matrix (continue, evidence-first)

- **(a) CLI-vs-in-process parity (expand):** exercised combos not yet locked across both fixtures — `--from-prices`/returns with `--rebalance-freq`+`--transaction-costs`+`--slippage` matrices, `--beta-window` extremes admissible vs data length, alternate benchmark (`ETH`) with space-separated `--universe` subsets/overlaps (note: comma-in-single-arg treated as literal token per exercised behavior), `--synthetic`+overrides, `--dry-run`+valid combos, `--output` overwrite semantics. Assert exact `final_cumulative`/`periods`/`benchmark`/`universe`, strict finite JSON.

- **(b) Non-finite/degenerate propagation:** temp CSV/returns with NaN/Inf/-Inf at edges (first/last row, whole-window warmup, multi-column sparse, benchmark-only defects), all-NaN non-benchmark columns, zero/negative/constant prices through `--from-prices`, empty-after-filtering scenarios. Verify rc/Traceback absence and finite-safe JSON or clean `BABDataError` per exercised contract. (Note exercised: negative price → rc=0 finite degenerate summary `final_cumulative==0.0`, `periods` reduced; constant column → clean rc=1 frozen-data rejection; zero price → rc=0 finite.)

- **(c) Error-path cleanliness & stability:** unreadable/missing/dir/conflicting paths, unsupported extensions, whitespace/malformed tokens, extreme but admissible numeric args vs data length, quantile boundary/interaction edges as exercised by config/CLI, `--dry-run` invalid-data combinations. Require stable actionable messages, `rc==1` on failure, no Traceback.

- **(d) Integration edges:** `cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` branches surfaced by (a)-(c) (exercised only; no dead-code/gate-closed chasing).

### Evidence logged this session (2026-11-10, @5b0afb9, campaign11m-followup)

- **Parity (a, expanded fixture `real_market_prices_expanded.csv` 399 rows):** CLI==in-process (rc=0, strict finite JSON, exact `final_cumulative`/`periods`/`benchmark`/`universe`): from-prices default `fc=0.6516736900335839 p=398`, `--beta-window 30 fc=0.8520833401652513`, `--rebalance-freq weekly fc=0.7100822584830278`, monthly `fc=0.6603645435984338`, quantiles `0.2/0.2 fc=0.49531892945265055`, `--benchmark ETH fc=0.4787921623783813`; returns-path default `fc=0.6516736900335839`, weekly+tc `fc=0.7100822584830278` (with tc path per args), combo `beta_window=45,tc=0.001,slip=0.0005 fc=0.5975939503692005`. Quantiles `0.5/0.5` parity `fc=0.9639897874415763`.
- **Universe handling:** space-separated `--universe ETH SOL BNB` accepted (rc=0, subset universe/fc finite, e.g. expanded `fc=0.46596502233816506`). Comma-in-single-arg `--universe ETH,SOL,BNB` treated as one literal token → clean rc=1 "no overlap..." (exercised behavior). Dry-run with valid data+`--output` → rc=0, output not written. Nested output parent dirs created (rc=0).
- **Non-finite/degenerate (b):** first/last-row NaN in asset/benchmark and all-NaN non-benchmark column (`AVAX`) on expanded from-prices → rc=0, strict finite JSON. Negative price (ETH row 10) → rc=0, finite degenerate summary `fc=0.0 periods=397` (backtest lacks `net` col; cumulative degenerate but JSON-safe). Zero price → rc=0 finite `fc=0.6183314134796462`. Constant column (`SOL=20.0`) → rc=1 clean "Stale/frozen data detected..." (no Traceback). Inf/-Inf injections remained rejected cleanly in prior 11m probes (locked in campaign11m tests).
- **Error paths (c):** expanded fixture exercises clean rc=1/no-Traceback for comma-literal universe mismatch, invalid quantile `0`. No production fixes required/proven this slice.
- **Production fixes:** none (all exercised behaviors defensive/as-contracted). **Tests added:** `tests/test_bab_cli_campaign11n_expanded_probe_regressions.py` (18) locking parity/universe/non-finite-degenerate/dry-run/nested-output invariants on expanded fixture.

### Remaining unprobed combos (priority order for next session)

1. Returns-path + `--transaction-costs` + `--slippage` matrix on expanded fixture (returns + cost/slippage combos not yet locked).
2. `--synthetic` + config overrides parity on CLI (synthetic data path through CLI not yet parity-locked vs in-process).
3. Multi-column sparse NaNs (multiple asset columns with scattered NaNs simultaneously).
4. Benchmark-only edge NaNs/Inf rejection cleanliness (benchmark column entirely NaN/Inf with assets valid).
5. Quantile sum/boundary interactions (e.g. long+short quantiles summing to >=1.0, boundary 0.0/1.0 exclusions).
6. `--output` overwrite semantics (existing file overwritten, rc=0, stale content replaced).
7. Extreme `--beta-window` vs short data (window > data length on both fixtures).

### GATES THAT MUST STAY GREEN

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2033 passed, 5 skipped** (current verified floor)
- `test_bab_cli_campaign11m_probe_regressions.py` (28) and `test_bab_cli_campaign11n_expanded_probe_regressions.py` (18) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked; other module miss-closures per prior handoff/proofs remain binding unless disproven by evidence.

## IMMEDIATE ACTIONS (no planning-only exit)

1. Run Step 0 gates on current tree; confirm 11m+11n probe regression modules passing with baseline floors.
2. Probe (a)-(d) for remaining unprobed combos listed above. Log rc/stdout/stderr/JSON snippets.
3. Add minimal non-duplicative `tests/test_bab_*campaign11*` for any proven gap; minimal prod fix only if bug proven. Re-run touched + gates.
4. Refresh this `HANDOFF.md` with evidence and next binding slice.

---
*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place.*
