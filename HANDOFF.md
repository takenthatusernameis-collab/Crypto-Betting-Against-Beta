# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-02T10:47:16Z (Gate 0 verified green: 150 passed, 6 skipped; BABStrategy cumulative == 0.31664543005633267)
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - Market-neutral long low-beta / short high-beta vs benchmark. ALL WORK MUST DIRECTLY ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign MANDATORY.
**Status:** GATE 0 GREEN - Core BAB tests pass (142 passed in core suites, 101 passed across combined BAB/core+messy+exchange suites). BABStrategy cumulative == 0.31664543005633267. Multi-source normalization hardened; exchange-format loaders extended; datetime/index normalization hardened.

## BOTTOM LINE - RUN GATE 0 FIRST, NO EXCEPTIONS

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta /home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_betting_against_beta.py tests/test_betting_against_beta_data_loader.py tests/test_betting_against_beta_data_loader_exchange.py tests/test_bab_messy_data.py -q
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"
```

**If red → fix before doing anything else.**

## COMPLETED THIS SESSION
1. **Campaign 7 Item 2 - Multi-source normalization (MASSIVELY HARDENED):**
- Extended `_normalize_columns` with aggressive whitespace/unit/duplicate-header handling, better asset name normalization (parentheses/brackets/slashes/concatenated pairs like BTCUSDT, common quotes), deterministic duplicate detection.
- Strengthened `_normalize_asset_name` for units/suffixes/mappings (BTC/ETH/SOL/BNB/XRP/ADA/AVAX/DOT).
- Enhanced `normalize_schema`: handles MultiIndex columns, headers-in-first-row/duplicate-header-row, drops junk non-numeric columns, integrates exchange normalization, robust coercion.
- Added tests for messy units/multi-level headers/duplicate header rows in `tests/test_betting_against_beta_data_loader.py` - all passing.
2. **Robust datetime parsing hardening:**
- Improved `_normalize_index` to coerce mixed tz/strings more defensively (coerce with/without utc, elementwise via `_coerce_to_datetime_scalar`), epoch seconds/ms heuristics, tz-aware → UTC → naive normalization, duplicate timestamps dropped, sorted index.
- Strengthened `_promote_datetime_column` to try exchange normalization first, recognize more datetime column names, better promotion of unnamed/epoch columns.
3. **Gate 0 + related suites verified green.** Controller/workflow pattern sync already fixed in previous session (tests/test_controller_progress_accounting.py green).

## IMMEDIATE TASK FOR NEXT SESSION (START HERE - HEAVY WORK REQUIRED, NOT OPTIONAL)

**CAMPAIGN 7: PRODUCTION HARDENING FOR REAL CRYPTO DATA** - DO NOT STOP UNTIL SUBSTANTIAL PROGRESS

**NEXT CONCRETE ITEM (Priority 1, item 3) - ROBUST DATETIME PARSING (MUST DO NOW):**

Harden datetime normalization utilities for real-world messiness. This blocks reliable ingestion from mixed sources. Make substantial, tested changes - trivial edits insufficient.

**REQUIRED ACTIONS (HEAVY - NON-NEGOTIABLE):**
1. **Harden `_promote_datetime_column`** in `strategies/betting_against_beta/data_loader.py`:
- Better detection of datetime columns when mixed with numeric/string metadata
- Handle cases where date is split across columns or in non-obvious positions
- More aggressive promotion for epoch seconds/ms strings, ISO8601 with/without Z/offsets
- Ensure idempotent behavior

2. **Harden `_normalize_index`**:
- Strengthen mixed timezone handling (naive vs aware), normalize everything to naive UTC consistently
- Handle dayfirst/ambiguous formats more robustly where safe
- Better error messages with clear `BABDataError`
- Preserve sort + duplicate removal behavior

3. **Tighten integration**:
- Ensure `normalize_schema`, `load_prices`, `load_returns` all use hardened paths
- Handle common exchange variants (Binance/OKX/Bybit/Coinbase/Kraken long/wide formats)

4. **ADD TESTS (substantial):**
- Epoch seconds (not just ms), microseconds, mixed naive/aware, strings with Z/+00:00/-07:00
- Dayfirst formats where unambiguous
- Index promotion from various column names
- Duplicate timestamps across sources
- All tests must stay green

**AFTER ITEM 3 COMPLETE:** Move to Priority 1 item 4 (comprehensive data quality checks - gaps, duplicate timestamps across assets, stale data, implausible returns |r|>X, missing benchmark coverage with clear BABDataError messages). Same rigor - heavy work, comprehensive tests.

**MANDATE:** Not a quick fix. Add comprehensive tests. Verify Gate 0 + new tests pass. Evidence required for each major change.

## PRIORITY 1 - CRITICAL (DO FIRST)
1. **DONE**: Exchange-format loader support - CoinGecko/Binance/Coinbase CSV formats
2. **DONE (hardened)**: Multi-source normalization - utilities to normalize mixed schemas into canonical datetime index + numeric columns; defensive vs whitespace/units/multi-level headers/duplicate headers
3. **NEXT**: Robust datetime parsing - harden `_promote_datetime_column` and `_normalize_index` (epoch seconds/ms, mixed timezones, dayfirst). Preserve existing behavior.
4. **TODO**: Comprehensive data quality checks - gaps, duplicate timestamps across assets, stale data, implausible returns (|r| > X), missing benchmark coverage. Clear `BABDataError` messages.

## PRIORITY 2-5 (see original handoff) - continue as before

## EXECUTION RULES (NON-NEGOTIABLE)
- **Gate 0 first. ALWAYS.** Confirm green baseline before any change.
- **Maintain green.** Add tests, don't weaken them.
- **BAB-first.** Every change must advance Crypto Betting Against Beta.
- **No workflow changes unless absolutely necessary.** If touching `.github/workflows/*`, pattern-sync tests must pass.
- **Preserve APIs/contracts.** Synthetic defaults must remain. Public APIs stable unless absolutely required with full coverage.
- **No lookahead.** Weights must be lagged by 1 day. This is invariant.
- **Defensive by default.** Validate inputs, fail with clear errors.
- **Heavy work only.** Trivial edits are insufficient. Tackle substantial improvements.
- **Bottleneck removal verified.** Controller/workflow pattern-sync tests green.
- **Evidence required.** For each major change, verify tests still pass and core behavior unchanged.

## KEY FILES
- `strategies/betting_against_beta/data_loader.py` - Data loading/validation (prime target)
- `strategies/betting_against_beta/beta.py`, `strategy.py`, `portfolio.py` - Core
- `strategies/betting_against_beta/cli.py`, `scripts/` - CLI/examples
- `tests/test_bab_*`, `tests/test_betting_against_beta*` - BAB tests (must stay green)

## START NOW
1. Run Gate 0 (confirm green on core BAB suites).
2. Pick ONE concrete item from Priority 1 (start with robust datetime parsing - item 3) and implement it fully with tests.
3. Run tests after each change - never let them go red.
4. Repeat with heavy work until substantial progress on real-data robustness.
