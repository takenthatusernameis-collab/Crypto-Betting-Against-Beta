# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-05T05:57:52Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**PRIORITY (NON-NEGOTIABLE):** `strategies/betting_against_beta/` - ALL effort MUST go here

## BOTTLENOCK RESOLVED (2026-11-05T05:50:00Z)

The gate was RED due to 2 failures in `tests/test_controller_progress_accounting.py`:
- `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow`
- Root cause: `.github/workflows/main.yml` `stage_safe_changes()` list was missing `*/.github/workflows/*` (present in Python `EXCLUDE_PATTERNS`).
- Fix: added `*/.github/workflows/*` to the workflow case pattern at `.github/workflows/main.yml:1163`. All 68 controller tests now pass. Gate is GREEN.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE THIS FIRST)

**Time:** 2026-11-05T05:57:52Z
**DIRECTIVE (Repo-name driven):** Betting Against Beta (crypto). Treat the BAB strategy as the sole product. No exploratory sidetracks. Every action must increase coverage/correctness of BAB modules and keep the gate green. Build momentum via targeted tests + minimal fixes. Do heavy, unrelenting work - close gaps until none obvious remain.

**MANDATORY FIRST ACTION (DO NOT SKIP):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -20
```
If RED → fix immediately before anything else. Gate must stay GREEN.

## CURRENT BASELINE (VERIFIED)

- **All tests under `tests/`:** Gate runs every `test_*.py` (302 files) with coverage of `strategies/betting_against_beta/`.
- **Coverage (from latest run, 87% TOTAL):**
  - data_loader.py: 79% (1693 stmts, 356 missing) - HIGHEST ROI, large surface
  - cli.py: 61% (318 stmts, 124 missing) - second-largest gap
  - backtest.py: 80% (109 stmts, 22 missing)
  - strategy.py: 89% (297 stmts, 32 missing)
  - signals.py: 91% (128 stmts, 11 missing)
  - beta.py: 92% (320 stmts, 25 missing)
  - portfolio.py: 93% (244 stmts, 16 missing)
  - config.py: 99%, costs.py: 98%, metrics.py: 99%, regime.py: 99%, sizing.py: 98%
  - attribution.py, data.py, data_sources.py, errors.py, quality.py, shorting.py: 100%
- **Dependencies:** pytest/coverage/numpy/pandas/scipy/sklearn/pyarrow/openpyxl/tables/hypothesis present.
- **Invariants enforced by tests:** weights lagged by 1 day (no lookahead), NaN/inf/NaT handled, dollar-neutral behavior, BABDataError on parse/validation failures, liquidity guards, slippage/rebalance, min-rows enforcement.

## NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER - NO SIDETRACKS)

**CAMPAIGN 1 (immediate): DATA LOADER - Target >= 90%+**
File: `strategies/betting_against_beta/data_loader.py`
Focus: `_coerce_to_datetime_scalar`, `_normalize_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, all `load_*` loaders, `validate_returns_dataframe`, `load_prices`/`load_returns`, error wrapping to `BABDataError`. Add adversarial tests for uncovered branches (356 missing lines). Test malformed inputs, mixed types, tz-aware/naive, duplicate indices, missing columns.

**CAMPAIGN 2: CLI - Target >= 85%**
File: `strategies/betting_against_beta/cli.py`
Focus: CLI parsing/validation/dry-run, all `--data/--benchmark/--universe/--beta-window/--long-quantile/--short-quantile/--rebalance-freq/--transaction-costs/--slippage/--output/--synthetic/--from-prices/--dry-run/--version` flag paths, error paths, version output.

**CAMPAIGN 3: CORE ENGINES**
Files: `backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`, `shorting.py`
Focus: rolling beta edge cases (min_obs, all-NaN, constant series), signal ranking/ties/quantiles, portfolio construction (equal-weight, dollar-neutral, lagged weights), backtest lookahead safety, transaction costs/slippage, NaN propagation. Property-style invariant tests.

## BINDING RULES
1. **Recon first** - run gate before changes. Fix immediately if red.
2. **Test-first for gaps** - add targeted tests for uncovered branches; only change implementation if a branch is truly unreachable via public APIs. Preserve all public APIs.
3. **Gate after every batch** - `bash scripts/bab_gate.sh` must stay GREEN. Never checkpoint/commit with RED.
4. **BAB-only** - ALL effort on `strategies/betting_against_beta/`. No sidetracks.
5. **Zero regressions** - every existing test must keep passing.
6. **No history rewriting** - no reset/rebase/force-push. HEAD intact.
7. **Invariants sacred** - weights lagged by 1 day (no lookahead), NaN/inf/NaT handled explicitly, `BABDataError` on parse/validation failures, dollar-neutral by default.

## EXECUTION PLAN FOR NEXT AGENT
- Run gate (confirm green).
- Generate coverage report focusing on missing lines in top untested modules (data_loader 356 missing, cli 124 missing).
- Add adversarial tests to close highest-impact gaps (data_loader Campaign 1 first, then cli Campaign 2).
- Run gate after each batch.
- Repeat until coverage is materially improved and all obvious gaps closed.
- Leave this handoff updated with progress if you make major structural improvements; at minimum keep gate green and momentum going.

**ACTION:** Execute CAMPAIGN 1 now. Do not stop. Build the next focus campaign as gaps close. Remove bottlenecks aggressively. Prioritize based on repo name (BAB).
