# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-05T06:35:39Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**PRIORITY (NON-NEGOTIABLE):** `strategies/betting_against_beta/` - ALL effort MUST go here. No sidetracks.

## BOTTLENECK STATUS (VERIFIED)

- Gate state: GREEN (2818 tests passed, exit 0). Previous controller workflow pattern bottleneck resolved (added `*/.github/workflows/*` to `.github/workflows/main.yml`).
- Primary bottlenecks to eliminate: `strategies/betting_against_beta/data_loader.py` (79%, 356 missing lines) and `strategies/betting_against_beta/cli.py` (61%, 124 missing lines). These are the highest-ROI gaps blocking confidence/completeness.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE THIS FIRST)

**Time:** 2026-11-05T06:35:39Z
**DIRECTIVE (Repo-name driven):** This is a Betting Against Beta (Crypto) repo. Treat BAB as the sole product. Do NOT explore unrelated code. Every action must increase correctness/coverage of BAB modules while keeping the full gate GREEN. Build unrelenting momentum: close gaps, fix root causes, remove bottlenecks. If blocked, remove the blocker - do not idle.

**MANDATORY FIRST ACTION (DO NOT SKIP):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -6
```
If RED → diagnose and fix immediately before anything else. Gate MUST stay GREEN after every change batch.

## CURRENT BASELINE (VERIFIED)

- **Tests:** Full gate runs every `test_*.py` under `tests/` (178 files, 2818 tests) with coverage of `strategies/betting_against_beta/`.
- **Coverage (latest):**
  - data_loader.py: 79% (1693 stmts, 356 missing) - HIGHEST ROI
  - cli.py: 61% (318 stmts, 124 missing) - SECOND HIGHEST ROI
  - backtest.py: 80% (109 stmts, 22 missing)
  - strategy.py: 89% (297 stmts, 32 missing)
  - signals.py: 91% (128 stmts, 11 missing)
  - beta.py: 92% (320 stmts, 25 missing)
  - portfolio.py: 93% (244 stmts, 16 missing)
  - config.py: 99%, costs.py: 98%, metrics.py: 99%, regime.py: 99%, sizing.py: 98%
  - attribution.py, data.py, data_sources.py, errors.py, quality.py, shorting.py: 100%
- **Dependencies present:** pytest/coverage/numpy/pandas/scipy/sklearn/pyarrow/openpyxl/tables/hypothesis
- **Invariants (sacred):** weights lagged by 1 day (no lookahead), NaN/inf/NaT handled explicitly, `BABDataError` on parse/validation failures, dollar-neutral by default, liquidity/transaction-cost/slippage semantics enforced.

## FOCUS CAMPAIGN (EXECUTE IN STRICT ORDER - NO DEVIATION)

### CAMPAIGN 1 - DATA LOADER (IMMEDIATE, UNRELENTING) → Target >= 90%+
**File:** `strategies/betting_against_beta/data_loader.py` (356 missing)

**Targets:** `_coerce_to_datetime_scalar`, `_normalize_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, `_maybe_read_table`, all `load_csv/load_json/load_jsonl/load_excel/load_parquet/load_pickle/load_hdf/load_returns/load_prices` paths, `validate_returns_dataframe`, error wrapping to `BABDataError`.
**Approach:** Write adversarial tests hitting uncovered branches (malformed inputs, mixed dtypes, tz-aware/naive, duplicate indices, missing/extra columns, index/column datetime promotion, float/string dates, NaT/inf). Prefer public API tests; only change impl if truly unreachable and fix is minimal and correct.

### CAMPAIGN 2 - CLI → Target >= 85%+
**File:** `strategies/betting_against_beta/cli.py` (124 missing)

**Targets:** argparse paths for `--data`, `--benchmark`, `--universe`, `--beta-window`, `--long-quantile`, `--short-quantile`, `--rebalance-freq`, `--transaction-costs`, `--slippage`, `--output`, `--synthetic`, `--from-prices`, `--dry-run`, `--version`, validation/errors, dry-run behavior, exit codes.

### CAMPAIGN 3 - CORE ENGINES (HARDEN)
**Files:** `backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`, `shorting.py`
**Targets:** rolling beta edge cases (min_obs, all-NaN/constant), ranking/ties/quantiles, lagged weights/no-lookahead, dollar-neutral, costs/slippage, NaN propagation, regime/sizing/shorting guards. Add property/invariant tests where valuable.

## BINDING RULES
1. **Recon first** - Run gate before any changes. Fix RED immediately.
2. **Test-first** - Add targeted tests for uncovered branches. Change implementation only if branch unreachable via public API; keep public APIs stable.
3. **Gate after every batch** - `bash scripts/bab_gate.sh` must stay GREEN. Never checkpoint/commit while RED.
4. **BAB-only** - ALL effort on `strategies/betting_against_beta/`. No sidetracks.
5. **Zero regressions** - All existing tests must continue to pass.
6. **No history rewriting** - No reset/rebase/force-push. HEAD intact.
7. **Invariants sacred** - Lagged weights (no lookahead), NaN/inf/NaT handled, `BABDataError` on parse/validation failures, dollar-neutral by default.

## EXECUTION PLAN FOR NEXT AGENT (DO NOT STOP)
- Run gate (confirm GREEN). If not, fix now.
- Generate coverage focus on missing lines for Campaign 1 (data_loader).
- Add adversarial tests batch by batch, run gate after each batch.
- Only move to Campaign 2 after data_loader meaningfully improved (>=90%) or all high-value uncovered branches addressed with no easy wins left.
- Do not stop at "good enough" - build next focus campaign as gaps close. Remove bottlenecks aggressively.
- Keep gate GREEN at all times. Leave handoff updated with concrete progress if major improvements made.

**ACTION:** START AT CAMPAIGN 1. Do heavy, unrelenting work. Never avoid hard gaps. Prioritize strictly by repo name (BAB).
