# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-02T20:14:32Z | **Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence.

**MANDATORY GATE:** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). Current state: GREEN (1855 passed, 13 skipped, 85% coverage). If gate ever goes RED, FIX IT BEFORE DOING ANYTHING ELSE. The gate is the ONLY verification command that counts.

## BOTTLENECKS REMOVED THIS SESSION (do not reopen)
- **Workflow pattern sync (CRITICAL):** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` case list. Python `controller_progress.EXCLUDE_PATTERNS` already had both patterns; workflow was missing the nested variant. Fixed 2 controller progress tests. Gate verified GREEN.
- **Campaign A - Real data robustness (COMPLETED):** Rewrote `strategies/betting_against_beta/data_loader.py` coercion into a single shared `_strip_units_and_parse()` helper used by both `_coerce_numeric()` and the pre/post junk-column filters. Fixes: currency symbols (`$`, `€`, `£`, `¥`), quote/unit tokens (`USDT`, `USDC`, `BTC`, `ETH`, ...) via word-boundary regex (no longer strips "USD" out of "USDT"), European decimal commas, thousand-separator commas, percent strings (`"1.5%" -> 0.015`), malformed numerics -> NaN, pure garbage -> raise. Also added `standardize_columns()`, `clean_data()`, `validate_prices()` public helpers, extended `load_prices()` + `detect_price_or_returns()` to Parquet/HDF5/Pickle, and relaxed `load_prices` min_rows accounting for the pct_change row drop. Gate GREEN.

## ACTIVE BOTTLENECKS / HEAVY WORK (DO NOT DEFER)
Gate is currently GREEN. Remaining heavy work: Campaign B (strategy/backtest depth) and Campaign C (CLI/reporting integration). Future agents must NOT be able to avoid heavy work - every session must advance BAB meaningfully.

## MANDATORY FOCUS CAMPAIGN (execute in order, no shortcuts)

### Campaign A - Real data robustness (PRIORITY 1 - COMPLETED THIS SESSION)
See "BOTTLENECKS REMOVED THIS SESSION". Verified against all `tests/fixtures/` (real_market_prices.csv, real_market_prices_expanded.csv, messy_returns.csv, real_data_defects.csv, junk_columns.csv, returns.json, non_monotonic_dates.csv, all_nan_column.csv, benchmark_nan_window.csv, degenerate_metrics.csv) plus end-to-end `BABStrategy.run()` on real prices.

### Campaign B - Strategy/backtest depth (PRIORITY 2 - NEXT)
**Objective:** Bulletproof core BAB logic under real data stress.

**Required tasks:**
1. **Numerical stability** - Review `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py` for NaN/inf/all-NaN windows, degenerate universes, single-asset cases.
2. **Lookahead safety** - Verify one-day lagged weights in backtest (no lookahead). Ensure signals computed only from past data.
3. **Costs/slippage** - Ensure transaction costs/slippage consistent, results serializable (watch `test_nonfinite_result_serialization.py`).
4. **Edge cases** - Handle insufficient history gracefully, benchmark issues, missing data.

### Campaign C - CLI/reporting integration (PRIORITY 3)
**Objective:** Make CLI and reporting production-robust.
1. Harden `cli.py` for messy/degenerate inputs, dry-run correctness.
2. Verify end-to-end with real-data style fixtures.
3. Ensure error messages are clear (use `BABDataError`).

## FIRST ACTION (NON-NEGOTIABLE - DO IN THIS ORDER)
1. **Confirm baseline:** `bash scripts/bab_gate.sh` → must be GREEN (1855 passed, 13 skipped). If not, fix immediately.
2. **Start Campaign B NOW.** Read `strategies/betting_against_beta/beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py` fully, understand all code paths. Look at all fixtures in `tests/fixtures/` and related tests.
3. **Make incremental, heavy changes.** Don't just read - MODIFY code to harden it. Add defensive handling where it makes sense.
4. **Gate after every meaningful change:** `bash scripts/bab_gate.sh` after each substantial edit. NEVER checkpoint with RED gate.
5. **Leave detailed handoff:** If you must stop before completing all campaigns, update THIS HANDOFF.md with exact progress, failing cases found, next concrete steps. Make it impossible for next agent to be confused.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** Crypto Betting Against Beta (BAB). `strategies/betting_against_beta/` + its tests FIRST always.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before session ends/checkpoint. No checkpoint on RED.
- **Full coverage:** Gate runs ALL `test_*.py` under `tests/`. Don't skip tests.
- **Single ledger:** `research_state/workflow_run_diagnostics.jsonl` is the sole ledger. Don't create parallel collectors/writers.
- **No workflow changes:** Don't modify `.github/workflows/*` except if fixing a blocking gate issue (and only if necessary). Keep maintainer-managed.
- **Preserve API compatibility:** Don't change public APIs unnecessarily. Fix by making code more robust/flexible.

**Timestamp:** 2026-11-02T20:14:32Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - HEAVY WORK MANDATORY
**Status:** GATE GREEN - CAMPAIGN A COMPLETE, START CAMPAIGN B IMMEDIATELY