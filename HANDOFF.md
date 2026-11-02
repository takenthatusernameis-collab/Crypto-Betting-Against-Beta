# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session)
**Time:** 2026-11-02T18:47:56Z | **Repo priority:** Crypto Betting Against Beta (BAB). All work must advance BAB. Nothing else takes precedence.
**Gate 0 baseline:** GREEN (1855 passed, 13 skipped). `python3 scripts/bab_gate.sh` is the ONLY verification command; it must exit 0 (GREEN) before any session is considered done.

## BOTTLENECKS REMOVED THIS SESSION (do not reopen)
- Workflow pattern sync: added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` case list to match `scripts/controller_progress.py` EXCLUDE_PATTERNS (which already had both `.github/workflows/*` and `*/.github/workflows/*`). This was a persistent bottleneck failing since 2026-10-27 across multiple sessions; now resolved. Fixed 2 controller progress tests. Gate re-verified GREEN (1855 passed, 13 skipped).

## REMAINING BOTTLENECKS = NEXT FOCUS CAMPAIGN (heavy work, mandatory, cannot be deferred)
None blocking gate. Gate is GREEN. Focus on advancing BAB strategy under `strategies/betting_against_beta/`.

## NEXT FOCUS CAMPAIGN (build to make future agents cannot avoid doing heavy work)
**Campaign A - Real data robustness (priority 1).**
- Harden `strategies/betting_against_beta/data_loader.py` for real CSV/JSON/Parquet/HDF5/Pickle/price-derived flows: ensure quality gates (`max_return_abs`, `max_gap_days`, `stale_run_threshold`) don't reject plausible real market data by default. Add sensible defaults or make validation strictness configurable per call while keeping existing passing tests green.
- Expand loader coverage for datetime normalization/index promotion, exchange/robust formats, NaN/coercion, and non-monotonic dates. Prefer fixing loader to be more permissive where semantically safe, not weakening invariants.

**Campaign B - Strategy/backtest depth (priority 2).**
- Review `strategies/betting_against_beta/{beta,signals,portfolio,backtest,strategy}.py` for numerical stability, lookahead safety, and edge cases (all-NaN windows, degenerate universes, single-asset). Add/strengthen tests only if gaps found; do not change public API unnecessarily.
- Ensure transaction cost/slippage handling is consistent and results are serializable (watch `test_nonfinite_result_serialization.py`).

**Campaign C - CLI/reporting integration (priority 3).**
- Polish `strategies/betting_against_beta/cli.py` and reporting paths for robustness on messy/degenerate inputs. Keep dry-run behavior correct.
- Verify end-to-end with real-data style fixtures from `tests/fixtures/`.

## FIRST ACTION (next session, non-negotiable)
1. Run `python3 scripts/bab_gate.sh` to confirm baseline (expect GREEN).
2. Pick Campaign A (real data robustness) first - directly unlocks using real market data as advertised in README.
3. Make incremental changes, re-run gate after each meaningful change; session ends only when gate is GREEN (0 failed).
4. Leave a clear, actionable handoff update if work remains or new bottlenecks appear.

## INVARIANTS
- Repo name drives priority: BAB strategy code under `strategies/betting_against_beta/` and its tests come first.
- Gate must be GREEN before checkpointing. No checkpoint on RED.
- Keep `tests/` coverage complete; gate collects every `test_*.py` under `tests/`.
- Do not add parallel diagnostic collectors or second ledger writers; `research_state/workflow_run_diagnostics.jsonl` is the sole ledger.

**Timestamp:** 2026-11-02T18:47:56Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB). Gate GREEN or the session is not done.
