# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session)
**Time:** 2026-11-02T17:32:50Z | **Repo priority:** Crypto Betting Against Beta (BAB). All work must advance BAB. Nothing else takes precedence.
**Gate 0 baseline:** RED (16 failed, 1839 passed, 13 skipped). `python3 scripts/bab_gate.sh` is the ONLY verification command; it must exit 0 (GREEN) before any session is considered done.

## BOTTLENECKS REMOVED THIS SESSION (do not reopen)
- `NameError: name 'quality' is not defined` in `load_returns_from_parquet`/`load_returns_from_hdf5`/`load_returns_from_pickle` (data_loader.py:1415/1440/1469). Added `quality: bool = True` param to each; csv/json already had it. Fixes 13 loader failures.
- Controller progress pattern sync: added `*/.github/workflows/*` to the workflow `stage_safe_changes()` case list (.github/workflows/main.yml:1163) to match Python `EXCLUDE_PATTERNS`. Fixes 2 `test_controller_progress_accounting.py` failures.

## REMAINING BOTTLENECKS = NEXT FOCUS CAMPAIGN (heavy work, mandatory, cannot be deferred)
The gate is RED until these are cleared. Target: 0 failed.

**Campaign 1 - Data-quality campaign (data-quality threshold/gap).**
`_run_data_quality_campaign` (data_loader.py:1058) rejects legitimate price-derived/exchange/robust-datetime fixtures:
- Implausible-return threshold `max_return_abs=20.0` (data_loader.py:1098) fires on real price moves (|r| up to 20590) and exchange fixtures.
- Gap threshold `max_gap_days=7.0` (data_loader.py:1100) fires on fixtures with 99-day gaps.
- Fix options (pick one, apply consistently): (a) raise/normalize `max_return_abs` and `max_gap_days` defaults so price-derived returns pass, or (b) make the affected datetime/exchange/robust-datetime tests call `validate`/`load_prices` with `quality=False`. Do NOT silence validation silently — the strategy needs real price data to work. Maintain green: every fix must keep previously-passing tests green.

**Campaign 2 - Stale/frozen data.**
`stale_run_threshold=3` (data_loader.py:1156) rejects columns with 3 consecutive equal values (BTC/ETH fixtures that legitimately repeat). Decide: allow short stale runs for price data, or raise threshold, or mark those fixtures `quality=False`.

**Campaign 3 - Other edge cases.**
- `test_bab_backtest_report.py` (2): degenerate-data human-readable/JSON report assertions.
- `test_bab_cli.py::test_cli_dry_run_valid_prices` (1): CLI dry-run `assert 1 == 0`.
- `test_bab_data_loader_precision_hits.py::test_promote_datetime_column_set_index_fails` (1): expects `date` in index but got `Date`.
- `test_bab_report_strict_json.py` (1): strict JSON payload on degenerate data.

## FIRST ACTION (next session, non-negotiable)
1. Run `python3 scripts/bab_gate.sh` to confirm baseline (expect 16 failed / 1839 passed / 13 skipped).
2. Fix Campaign 1 (data-quality threshold/gap) first — it is the largest blocker and directly gates real price/exchange data loading, which is core to BAB.
3. Then Campaign 2 (stale/frozen), then Campaign 3 (other).
4. Re-run gate after each fix; session ends only when gate is GREEN (0 failed).

## INVARIANTS
- Repo name drives priority: BAB strategy code under `strategies/betting_against_beta/` and its tests come first.
- Gate must be GREEN before checkpointing. No checkpoint on RED.
- Keep `tests/` coverage complete; the gate already collects every `test_*.py` under `tests/` (no more silent exclusions).
- Do not add parallel diagnostic collectors or second ledger writers; `research_state/workflow_run_diagnostics.jsonl` is the sole ledger.

**Timestamp:** 2026-11-02T17:32:50Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB). Gate GREEN or the session is not done.
