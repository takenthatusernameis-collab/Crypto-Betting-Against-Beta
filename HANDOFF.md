# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-02T20:22:52Z | **Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence.

**MANDATORY GATE:** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED, FIX IT BEFORE DOING ANYTHING ELSE. The gate is the ONLY verification command that counts. It runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`.

## BOTTLENECKS REMOVED THIS SESSION (do not reopen)
- **Workflow pattern sync (CRITICAL - FIXED):** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` case list. Python `controller_progress.EXCLUDE_PATTERNS` already had both variants; workflow bash list was missing the nested variant causing controller-progress tests to fail and gate to go RED. Verified GREEN.
- **Campaign A - Real data robustness (COMPLETED):** Rewrote `strategies/betting_against_beta/data_loader.py` coercion into a single shared `_strip_units_and_parse()` helper used by both `_coerce_numeric()` and pre/post junk-column filters. Handles currency symbols (`$`,`€`,`£`,`¥`), unit tokens (`USDT`,`USDC`,...) via word-boundary regex (doesn't strip "USD" from "USDT"), European decimal commas, thousand separators, percentages (`"1.5%" -> 0.015`), malformed numerics -> NaN, pure garbage -> raises. Added `standardize_columns()`, `clean_data()`, `validate_prices()`. Extended `load_prices()`/`detect_price_or_returns()` to Parquet/HDF5/Pickle. Relaxed `load_prices` min_rows accounting for pct_change row drop. Hardened against all fixtures in `tests/fixtures/`.

## CURRENT STATE
- Gate: GREEN (1855 passed, 13 skipped, 87% coverage)
- Campaign A: COMPLETE
- Campaign B: ACTIVE - Strategy/backtest depth hardening (PRIORITY 2)
- Campaign C: QUEUED - CLI/reporting integration (PRIORITY 3)

## MANDATORY FOCUS CAMPAIGN (execute in order, no shortcuts)

### Campaign B - Strategy/backtest depth (PRIORITY 2 - ACTIVE NOW)
**Objective:** Bulletproof core BAB logic under real data stress. Make it impossible to have silent failures.

**Required tasks (DO ALL, incrementally with gate after each):**
1. **Numerical stability** - Audit `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py`. Ensure NaN/inf/all-NaN windows, degenerate universes, constant benchmark, single-asset cases are handled without crashing or producing misleading finite values. Pay special attention to `calculate_beta_fast()`, rolling beta paths (pandas + numpy vectorized), and degenerate denom cases.
2. **Lookahead safety** - Verify one-day lagged weights in backtest (`weights.shift(1)`) with no lookahead. Ensure signals computed only from past data. Check rebalance logic doesn't leak future info.
3. **Costs/slippage** - Ensure transaction costs/slippage consistent. Verify results serializable (watch `test_nonfinite_result_serialization.py`). Check trade attribution, cost drag accounting, log-returns/cumulative paths.
4. **Edge cases** - Handle insufficient history gracefully, benchmark issues (all-NaN/constant), missing data, delistings, single asset, all-equal betas (ties), extreme quantiles, mixed dtypes. Ensure dollar-neutrality is exact when both sides exist.
5. **Integration hardening** - Test full pipeline with messy fixtures. Ensure `BABStrategy.run()` resolves universe correctly, applies rebalance masks properly, handles shorting constraints/sizers without breaking.

**Start here (HEAVY WORK):**
- Read `strategies/betting_against_beta/beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py` fully
- Read all tests related to edges: `tests/test_bab_signals_portfolio_edgecases.py`, `tests/test_beta_adversarial_hardening.py`, `tests/test_bab_adversarial_e2e_hardening.py`, `tests/test_beta_crush_missing.py`, `tests/test_bab_integration_chaos_campaign.py`
- Review fixtures in `tests/fixtures/` (all of them)
- MAKE INCREMENTAL HEAVY CHANGES to harden code. Don't just read.

### Campaign C - CLI/reporting integration (PRIORITY 3 - QUEUED)
**Objective:** Make CLI and reporting production-robust.
1. Harden `cli.py` for messy/degenerate inputs, dry-run correctness, clear error messages via `BABDataError`
2. Verify end-to-end with real-data style fixtures
3. Ensure `scripts/bab_backtest_report.py` and reporting paths handle NaN/inf gracefully
4. Test all CLI flags and console script behavior

## FIRST ACTION (NON-NEGOTIABLE - DO IN THIS ORDER)
1. **Confirm baseline:** `bash scripts/bab_gate.sh` → must be GREEN. If not, fix immediately.
2. **Start Campaign B NOW.** Read the 5 core modules + edge case tests as specified above.
3. **Hunt for weaknesses.** Look for places where NaN/inf could propagate, where assumptions break on single asset/all-NaN/constant benchmark, where lookahead could exist, where costs aren't applied correctly.
4. **Harden aggressively.** Add defensive checks, fix numerical issues, ensure finiteness guards everywhere. MODIFY code.
5. **Gate after every meaningful change:** `bash scripts/bab_gate.sh` after each substantial edit. NEVER checkpoint with RED gate.
6. **Leave detailed handoff:** If you must stop before completing all campaigns, update THIS HANDOFF.md with exact progress, failing cases found, next concrete steps, files modified. Make it impossible for next agent to be confused.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** Crypto Betting Against Beta (BAB). `strategies/betting_against_beta/` + its tests FIRST always.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before session ends/checkpoint. No checkpoint on RED.
- **Full coverage:** Gate runs ALL `test_*.py` under `tests/`. Don't skip tests.
- **Single ledger:** `research_state/workflow_run_diagnostics.jsonl` is the sole ledger. Don't create parallel collectors/writers.
- **No workflow changes:** Don't modify `.github/workflows/*` except if fixing a blocking gate issue (and only if necessary). Keep maintainer-managed.
- **Preserve API compatibility:** Don't change public APIs unnecessarily. Fix by making code more robust/flexible.
- **Lookahead is forbidden:** Weights must be lagged by 1 day. No future information leakage.
- **Finiteness required:** Outputs must be finite where possible; NaN/inf must be handled explicitly, never produce corrupt results.

**Timestamp:** 2026-11-02T20:22:52Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - HEAVY WORK MANDATORY
**Status:** GATE GREEN - CAMPAIGN A COMPLETE, CAMPAIGN B ACTIVE (STRATEGY/BACKTEST DEPTH) - CONTINUE HEAVY WORK NOW
