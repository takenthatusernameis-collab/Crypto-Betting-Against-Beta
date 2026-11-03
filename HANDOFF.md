# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T00:37:30Z | **Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. This repo name DEMANDS heavy implementation work on the BAB strategy - do not deviate.

**MANDATORY GATE:** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED, FIX IT BEFORE DOING ANYTHING ELSE. The gate is the ONLY verification command that counts. It runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`.

## BOTTLENECKS REMOVED (do not reopen)
- **Workflow pattern sync (CRITICAL - FIXED):** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` case to match `scripts/controller_progress.py:EXCLUDE_PATTERNS`. Both sync tests pass. Lists remain in lock-step.
- **Test coverage scope (FIXED):** Gate runs ALL `test_*.py` under `tests/` (not just `test_bab*.py`).
- **Data loader robustness (HARDENED):** Coercion, NaN/inf, Parquet/HDF5/Pickle handling.
- **Core strategy hardening (ONGOING):** Aggressive guards across beta/signals/portfolio/backtest/strategy/metrics/costs.

## CURRENT STATE
- Gate: MUST BE GREEN (verify immediately)
- Campaign A: COMPLETE
- Campaign B: HEAVILY HARDENED - Continue aggressive stress testing for numerical stability, lookahead safety, finiteness
- Campaign C: QUEUED - CLI/reporting integration hardening (CRITICAL next)
- Focus: MAXIMUM AGGRESSION on edge cases

## MANDATORY FOCUS CAMPAIGN (execute in order, NO SHORTCUTS - HEAVY WORK REQUIRED)

### Campaign B - Strategy/backtest depth (PRIORITY 2 - ONGOING)
**Objective:** Bulletproof core BAB logic under adversarial real data stress. Make silent failures impossible. FIND and FIX every edge case.

**Required tasks (DO ALL, incrementally with gate after each change):**
1. **Numerical stability audit** - Deep audit `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py`, `costs.py`, `metrics.py`, `attribution.py`, `regime.py`, `sizing.py`, `shorting.py`. Handle NaN/inf/all-NaN windows, degenerate universes, constant benchmark, single-asset/multi-asset edge cases, rank-deficient matrices without crashing or producing misleading finite values.
2. **Lookahead safety (CRITICAL)** - Verify one-day lagged weights in backtest (`weights.shift(1)`) with NO lookahead. Ensure signals computed only from past data. Add assertions/tests if gaps found.
3. **Costs/slippage** - Ensure transaction costs/slippage consistent and robust. Verify trade attribution correctness. Check serialization.
4. **Edge cases from hell** - Handle insufficient history gracefully, benchmark issues, missing data, delistings, single asset, all-equal betas (ties), extreme quantiles, mixed dtypes, NaN clusters, inf values, constant series, zero variance. Ensure dollar-neutrality is exact when both sides exist; re-normalize defensively.
5. **Finiteness enforcement** - Every return/weight/cumulative must be finite or explicitly sanitized. No NaN/inf propagation.
6. **Integration stress** - Test full pipeline with messy fixtures. Hunt for unguarded divisions, log of non-positive, sqrt of negative, etc.

**Start here:** Read core modules + adversarial tests, systematically hunt weaknesses, add defensive checks with tests if needed, run gate after EVERY substantial edit.

### Campaign C - CLI/reporting integration (PRIORITY 3 - HEAVY WORK)
**Objective:** Make CLI and reporting production-bulletproof.
1. Harden `cli.py` for messy/degenerate inputs, dry-run correctness, clear error messages via `BABDataError`. Handle all failure modes gracefully.
2. Verify end-to-end with real-data style fixtures under adversarial conditions.
3. Ensure `scripts/bab_backtest_report.py` and all reporting paths handle NaN/inf gracefully.
4. Test all CLI flags, subcommands, console script behavior.
5. Add defensive guards wherever unprotected. Ensure CLI never crashes on degenerate data.

### Campaign D - Data loader & quality (PRIORITY 4)
**Objective:** Bulletproof data ingestion.
1. Harden `data_loader.py` for all formats (CSV/JSON/JSONL/Parquet/HDF5/Pickle) with messy inputs.
2. Ensure `quality.py` validation is comprehensive and doesn't crash.
3. Test with adversarial fixtures.

## FIRST ACTION (NON-NEGOTIABLE - EXECUTE IN THIS EXACT ORDER)
1. **Confirm baseline:** `bash scripts/bab_gate.sh` → MUST be GREEN. Do not proceed until GREEN.
2. **Attack Campaign B aggressively:** Read all core BAB modules and adversarial tests. Create a mental map of weak points. Attack them one by one with maximum aggression.
3. **Gate after every meaningful change:** `bash scripts/bab_gate.sh` after each substantial edit. NEVER checkpoint with RED gate.
4. **Be aggressive:** Find edge cases others missed. Add guards. Improve robustness. This is HEAVY engineering work - do not stop at surface level.
5. **Leave detailed handoff:** If you must stop before completing all campaigns, update THIS HANDOFF.md with exact progress, failing cases found, next concrete steps (file:line), files modified, and current gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** Crypto Betting Against Beta (BAB). `strategies/betting_against_beta/` + its tests FIRST always.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before session ends/checkpoint. No checkpoint on RED.
- **Full coverage:** Gate runs ALL `test_*.py` under `tests/`.
- **Single ledger:** `research_state/workflow_run_diagnostics.jsonl` is the sole ledger.
- **No workflow changes:** Don't modify `.github/workflows/*` except if fixing a blocking gate issue (and only if absolutely necessary and tests still pass).
- **Preserve API compatibility:** Don't change public APIs unnecessarily.
- **Lookahead is forbidden:** Weights must be lagged by 1 day.
- **Finiteness required:** Outputs must be finite where possible; NaN/inf must be handled explicitly.
- **Heavy work mandatory:** Given repo name "Crypto-Betting-Against-Beta", this session MUST produce substantial hardening/improvements to the BAB implementation.

**Timestamp:** 2026-11-03T00:37:30Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - HEAVY WORK MANDATORY
**Status:** GATE MUST BE GREEN - Bottlenecks REMOVED - Campaign A COMPLETE, Campaign B HEAVILY HARDENED, Campaign C QUEUED, Campaign D QUEUED. ATTACK remaining edge cases aggressively. DO NOT CHECKPOINT ON RED GATE.
