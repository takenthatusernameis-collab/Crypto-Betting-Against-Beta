# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T07:07:59Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - Market-neutral long low-beta / short high-beta vs benchmark. ALL WORK MUST DIRECTLY ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign MANDATORY.
**Status:** GATE 0 GREEN - 1828 passed, 13 skipped, 0 failures. BABStrategy cumulative == 0.31664543005633267. Bottlenecks removed this session (see below).

## BOTTOM LINE - RUN GATE 0 FIRST, NO EXCEPTIONS

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # MUST be: 1828 passed, 13 skipped
python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"  # MUST be ~0.31664543005633267
```

**If red → fix before doing anything else.**

## BOTTLENECKS REMOVED THIS SESSION (DO NOT REGRESS)

1. `strategies/betting_against_beta/data_loader.py` - fixed an empty/dangling `try:` block (`IndentationError`) that broke module import and all 123 test collections. Collection now works.
2. `.github/workflows/main.yml` - added `*/.github/workflows/*` to the `stage_safe_changes` case list to re-sync with Python `EXCLUDE_PATTERNS` in `scripts/controller_progress.py`. Pattern-sync tests now pass.
3. `strategies/betting_against_beta/data_loader.py` - `_promote_datetime_column` last-resort loop now skips a named date-like column already attempted via `set_index`, so a failed `set_index` is not silently bypassed. `test_promote_datetime_column_set_index_fails` now passes.

## IMMEDIATE TASK FOR NEXT SESSION (START HERE - HEAVY WORK REQUIRED)

**CAMPAIGN 7: PRODUCTION HARDENING FOR REAL CRYPTO DATA** (from prior HANDOFF, still open)

Do NOT do cosmetic changes. Do heavy, verifiable work. The very next concrete item is:

**NEXT CONCRETE ITEM (Priority 1, item 1): Exchange-format loader support**
Extend `strategies/betting_against_beta/data_loader.py` to robustly handle common exchange CSV formats:
- CoinGecko exports, Binance OHLCV/price CSVs, Coinbase exports.
- Flexible column mapping (date/time/open/high/low/close/adj_close/volume), symbol case handling, auto-detect price vs returns.
- Add tests under `tests/` covering each exchange format end-to-end through `load_returns` / `load_prices` and `validate_returns_dataframe`.
- Must keep Gate 0 green (1828 passed, 13 skipped) after adding tests.

Then continue down Priority 1 (items 2-3: multi-source normalization, robust datetime parsing) before touching Priorities 2-5.

## PRIORITY 1 - CRITICAL (DO FIRST)
1. Exchange-format loader support - CoinGecko/Binance/Coinbase CSV formats, column mapping, symbol case, price-vs-returns auto-detect. Add tests.
2. Multi-source normalization - utilities to normalize different schemas into canonical datetime index + numeric columns; defensive vs whitespace/units.
3. Robust datetime parsing - harden `_promote_datetime_column` and `_normalize_index` (epoch seconds/ms, mixed timezones, dayfirst). Preserve existing behavior.

## PRIORITY 2 - CRITICAL (DATA QUALITY)
4. Comprehensive data quality checks - gaps, duplicate timestamps across assets, stale data, implausible returns (|r| > X), missing benchmark coverage. Clear `BABDataError` messages.
5. Survivorship bias awareness - explicit, tested delisting handling.
6. Timezone/alignment tests - cross-timezone datasets; verify no lookahead (1-day lagged weights invariant).

## PRIORITY 3 - HIGH (PERFORMANCE & SCALABILITY)
7. Profile & optimize `calculate_rolling_beta` in `beta.py`. Vectorize bottlenecks without changing API/results. Add perf tests / extend `scripts/perf_bench.py`.
8. Large dataset testing - multi-year, 500+ assets synthetic tests for memory/performance.
9. Efficient I/O - loader improvements for large files where easy wins exist.

## PRIORITY 4 - HIGH (RISK/REALISM)
10. Transaction costs realism - market impact/slippage tiers, backward compatible.
11. Risk controls - position/leverage limits, max drawdown monitoring hooks.
12. Attribution & metrics - Sharpe, Sortino, Calmar, max DD, turnover, hit rate.

## PRIORITY 5 - MANDATORY (TEST COVERAGE)
13. Property-based tests - hypothesis tests for dollar-neutrality, weight bounds, no lookahead, idempotency.
14. Stress tests - correlation regime shifts, extreme vol, missing data patterns matching real exchanges.
15. CLI integration tests - `--from-prices`, `bab-example`, real file formats end-to-end.

## EXECUTION RULES (NON-NEGOTIABLE)
- **Gate 0 first. ALWAYS.** Confirm green baseline before any change.
- **Maintain green.** Keep 1828 passed + 13 skipped. Add tests, don't weaken them.
- **BAB-first.** Every change must advance Crypto Betting Against Beta.
- **No workflow changes unless absolutely necessary.** If touching `.github/workflows/*`, pattern-sync tests must pass.
- **Preserve APIs/contracts.** Synthetic defaults must remain. Public APIs stable unless absolutely required with full coverage.
- **No lookahead.** Weights must be lagged by 1 day. This is invariant.
- **Defensive by default.** Validate inputs, fail with clear errors.
- **Heavy work only.** Trivial edits are insufficient. Tackle substantial improvements.
- **Evidence required.** For each major change, verify tests still pass and core behavior unchanged.

## KEY FILES
- `strategies/betting_against_beta/data_loader.py` - Data loading/validation (prime target)
- `strategies/betting_against_beta/beta.py`, `strategy.py`, `portfolio.py` - Core
- `strategies/betting_against_beta/cli.py`, `scripts/` - CLI/examples
- `tests/test_bab_*` - All BAB tests (must stay green)

## START NOW
1. Run Gate 0 (confirm green: 1828 passed, 13 skipped).
2. Pick ONE concrete item from Priority 1 (start with exchange-format loader support) and implement it fully with tests.
3. Run tests after each change - never let them go red.
4. Repeat with heavy work until substantial progress on real-data robustness.
