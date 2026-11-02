# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T10:37:09Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - Market-neutral long low-beta / short high-beta vs benchmark. ALL WORK MUST DIRECTLY ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign MANDATORY.
**Status:** GATE 0 GREEN - Core BAB tests pass (142 passed, 6 skipped). BABStrategy cumulative == 0.31664543005633267. Exchange-format loader support added; normalization/datetime hardening in progress.

## BOTTOM LINE - RUN GATE 0 FIRST, NO EXCEPTIONS

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta /home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_betting_against_beta.py tests/test_betting_against_beta_data_loader.py tests/test_betting_against_beta_data_loader_exchange.py -q
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"
```

**If red → fix before doing anything else.**

## COMPLETED THIS SESSION
1. Extended `strategies/betting_against_beta/data_loader.py` with robust exchange-format support:
- Enhanced column/symbol normalization (case-insensitive, common exchange naming).
- Improved `_detect_and_normalize_exchange_format` for long-format (symbol/ticker/coin/pair + date + close/price) → pivot to wide prices.
- Better OHLCV handling (Binance/Coinbase) with epoch ms/sec and string timestamps; prefers Close/Adj Close.
- Aggressive datetime promotion for epoch/string timestamps.
- Added comprehensive tests in `tests/test_betting_against_beta_data_loader_exchange.py` (CoinGecko long, Binance OHLCV, Coinbase OHLCV, symbol case handling) - all passing.
2. Gate 0 verified: core BAB suites green; baseline cumulative unchanged.
3. Multi-source normalization hardening: strengthened `normalize_schema`, robust column normalization for messy headers (whitespace/case/units), auto-drop of junk extra columns on load; added tests for messy CSVs and normalize_schema.
4. Robust datetime parsing: hardened `_normalize_index`/coercion for epoch seconds/ms and mixed timezones (UTC normalization); added tests.
5. Gate 0 re-verified: all core BAB suites green (142 passed, 6 skipped).


## IMMEDIATE TASK FOR NEXT SESSION (START HERE - HEAVY WORK REQUIRED)

**CAMPAIGN 7: PRODUCTION HARDENING FOR REAL CRYPTO DATA** - DO NOT STOP UNTIL SUBSTANTIAL PROGRESS

**NEXT CONCRETE ITEM (Priority 1, item 2) - MULTI-SOURCE NORMALIZATION (MUST DO NOW):**
Harden normalization utilities to unify schemas across sources. This is blocking real-data ingestion.

**REQUIRED ACTIONS (HEAVY):**
1. **Strengthen `_normalize_columns`** in `strategies/betting_against_beta/data_loader.py`:
- More aggressive whitespace/unit/duplicate-header handling across mixed schemas
- Better asset name normalization (handle units like "BTC (Bitcoin)", "BTC-USD", "XBT", common exchange suffixes)
- Normalize redundant metadata columns that appear in real exports
- Ensure deterministic behavior with duplicate column names raising clear BABDataError

2. **Add schema unification helpers**:
- Create/extend utilities to normalize mixed schemas into canonical datetime index + numeric columns
- Handle cases where headers are spread across rows, or have multi-level headers
- Make `load_prices`/`load_returns` resilient to header casing, extra junk columns, units in headers

3. **Harden datetime normalization**:
- Strengthen `_normalize_index` and `_promote_datetime_column` for epoch seconds/ms, mixed timezones, dayfirst
- Better handling of strings like "2023-01-01T00:00:00Z", Unix timestamps as strings
- Ensure UTC normalization is consistent

4. **ADD TESTS** (must be substantial):
- Create/extend tests for messy real-world CSVs: extra columns, spaces, mixed case headers, units in headers
- Test multi-source schemas (CoinGecko, Binance, Coinbase variants, CoinMarketCap-like exports)
- Test normalization edge cases
- Keep ALL tests green

**AFTER ITEM 2 COMPLETE:** Move to Priority 1 item 3 (robust datetime parsing) with same rigor.

**MANDATE:** This is NOT a quick fix. Do heavy, thorough work. Add comprehensive tests. Verify Gate 0 + new tests all pass.

## PRIORITY 1 - CRITICAL (DO FIRST)
1. **DONE**: Exchange-format loader support - CoinGecko/Binance/Coinbase CSV formats, column mapping, symbol case, price-vs-returns auto-detect. Added tests.
2. Multi-source normalization - utilities to normalize different schemas into canonical datetime index + numeric columns; defensive vs whitespace/units. Add tests.
3. Robust datetime parsing - harden `_promote_datetime_column` and `_normalize_index` (epoch seconds/ms, mixed timezones, dayfirst). Preserve existing behavior.

## PRIORITY 2 - CRITICAL (DATA QUALITY)
4. Comprehensive data quality checks - gaps, duplicate timestamps across assets, stale data, implausible returns (|r| > X), missing benchmark coverage. Clear `BABDataError` messages.
5. Survivorship bias awareness - explicit, tested delisting handling (already partially addressed).
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
- **Maintain green.** Add tests, don't weaken them.
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
1. Run Gate 0 (confirm green on core BAB suites).
2. Pick ONE concrete item from Priority 1 (start with multi-source normalization) and implement it fully with tests.
3. Run tests after each change - never let them go red.
4. Repeat with heavy work until substantial progress on real-data robustness.
