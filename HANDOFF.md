# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T00:40:00Z | **Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence.

**MANDATORY GATE:** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED, FIX IT BEFORE DOING ANYTHING ELSE. The gate is the ONLY verification command that counts. It runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`.

## BOTTLENECKS REMOVED THIS SESSION (do not reopen)
- **Workflow pattern sync (CRITICAL - FIXED FOR REAL):** Added missing `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` case (was missing causing gate RED). Tests `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` now pass. Lists must stay in lock-step with `scripts/controller_progress.py:EXCLUDE_PATTERNS`.
- **Campaign A - Real data robustness (COMPLETED):** Data loader coercion hardened with shared helpers, extended to Parquet/HDF5/Pickle, fixtures all handled.
- **Campaign B - Strategy/backtest depth (HEAVILY HARDENED):** Added aggressive defensive guards across `beta.py` (NaN/inf/constant benchmark/singular cases), `signals.py` (quantile clamping, tie handling, numeric coercion hardening), `portfolio.py` (dollar-neutrality re-normalization, finite guards), `backtest.py` (cumulative/log-return finiteness with robust fallbacks), `strategy.py` (pipeline finiteness guards). CLI hardened for NaN/inf outputs.

## CURRENT STATE
- Gate: GREEN (1855+ passed, 13 skipped) as of 2026-11-03T00:40:00Z
- Campaign A: COMPLETE
- Campaign B: HEAVILY HARDENED - Continue stress testing and plug any remaining gaps
- Campaign C: QUEUED - CLI/reporting integration (harden further)

## MANDATORY FOCUS CAMPAIGN (execute in order, no shortcuts)

### Campaign B - Strategy/backtest depth (PRIORITY 2 - ONGOING)
**Objective:** Bulletproof core BAB logic under real data stress. Make it impossible to have silent failures.

**Required tasks (DO ALL, incrementally with gate after each):**
1. **Numerical stability** - Audit `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py`. Ensure NaN/inf/all-NaN windows, degenerate universes, constant benchmark, single-asset cases are handled without crashing or producing misleading finite values.
2. **Lookahead safety** - Verify one-day lagged weights in backtest (`weights.shift(1)`) with no lookahead. Ensure signals computed only from past data.
3. **Costs/slippage** - Ensure transaction costs/slippage consistent. Verify results serializable. Check trade attribution.
4. **Edge cases** - Handle insufficient history gracefully, benchmark issues, missing data, delistings, single asset, all-equal betas (ties), extreme quantiles, mixed dtypes. Ensure dollar-neutrality is exact when both sides exist.
5. **Integration hardening** - Test full pipeline with messy fixtures. Ensure robustness.

**Start here:**
- Read core modules + edge case tests, hunt for weaknesses, add defensive checks, gate after each change.

### Campaign C - CLI/reporting integration (PRIORITY 3)
**Objective:** Make CLI and reporting production-robust.
1. Harden `cli.py` for messy/degenerate inputs, dry-run correctness, clear error messages via `BABDataError`
2. Verify end-to-end with real-data style fixtures
3. Ensure `scripts/bab_backtest_report.py` and reporting paths handle NaN/inf gracefully
4. Test all CLI flags and console script behavior

## FIRST ACTION (NON-NEGOTIABLE - DO IN THIS ORDER)
1. **Confirm baseline:** `bash scripts/bab_gate.sh` → must be GREEN.
2. **Continue Campaign B:** Look for any remaining uncovered branches or edge cases. Add more defensive guards where needed.
3. **Gate after every meaningful change:** `bash scripts/bab_gate.sh` after each substantial edit. NEVER checkpoint with RED gate.
4. **Leave detailed handoff:** If you must stop before completing all campaigns, update THIS HANDOFF.md with exact progress, failing cases found, next concrete steps, files modified.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** Crypto Betting Against Beta (BAB). `strategies/betting_against_beta/` + its tests FIRST always.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before session ends/checkpoint. No checkpoint on RED.
- **Full coverage:** Gate runs ALL `test_*.py` under `tests/`.
- **Single ledger:** `research_state/workflow_run_diagnostics.jsonl` is the sole ledger.
- **No workflow changes:** Don't modify `.github/workflows/*` except if fixing a blocking gate issue (and only if necessary).
- **Preserve API compatibility:** Don't change public APIs unnecessarily.
- **Lookahead is forbidden:** Weights must be lagged by 1 day.
- **Finiteness required:** Outputs must be finite where possible; NaN/inf must be handled explicitly.

**Timestamp:** 2026-11-03T00:40:00Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - HEAVY WORK MANDATORY
**Status:** GATE GREEN - Campaign A COMPLETE, Campaign B HEAVILY HARDENED, Campaign C QUEUED. Continue hardening aggressively with focus on finding and fixing any remaining edge cases. DO NOT CHECKPOINT ON RED GATE.
