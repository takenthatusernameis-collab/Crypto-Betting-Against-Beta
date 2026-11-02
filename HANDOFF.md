# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session)
**Time:** 2026-11-02T13:39:17Z | **Repo priority:** Crypto Betting Against Beta (BAB) market-neutral long low-beta/short high-beta vs benchmark. All work must advance BAB.
**Gate 0 baseline:** GREEN (155 passed, 6 skipped). BABStrategy cumulative == 0.31664543005633267.
**Bottlenecks:** none blocking. Datetime parsing hardened (Item 3 done). Multi-source normalization done (Item 2).
**FIRST ACTION:** Run Gate 0. Then implement Campaign 7 Item 4 - Comprehensive data quality checks in `validate_returns_dataframe` (gaps, duplicate timestamps across assets, stale data, implausible returns |r|>X, missing benchmark coverage) with clear BABDataError messages and substantial tests. Heavy work mandatory; do not stop until significant progress. Maintain green. Evidence required.
**Timestamp:** 2026-11-02T13:39:17Z (Gate GREEN: 155 passed; Campaign 7 Item 4 data quality next)
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - Market-neutral long low-beta / short high-beta vs benchmark. ALL WORK MUST DIRECTLY ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign MANDATORY.
**Status:** GATE 0 GREEN - Core BAB tests pass (155 passed in Gate 0 suites). BABStrategy cumulative == 0.31664543005633267. ITEM 3 (Robust datetime parsing) COMPLETED - hardened `_promote_datetime_column` and `_normalize_index` for epoch seconds/ms/μs, mixed timezones/offsets (Z, +00:00, -07:00), elementwise coercion, normalization to naive UTC; added comprehensive datetime tests (all passing). Bottlenecks removed.

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
3. **Gate 0 + related suites verified green (now 155 passed).** Controller/workflow pattern sync already fixed in previous session.
4. **Bottleneck removed - `load_prices` metadata column fix.** (as above)
5. **Robust datetime parsing hardened (Campaign 7 Item 3):** Enhanced `_promote_datetime_column` and `_normalize_index` for epoch seconds/ms/microseconds, numeric/string mixing, mixed tz/offsets (Z, +HH:MM, -HH:MM), elementwise `_coerce_to_datetime_scalar` with normalization to naive UTC, better duplicate handling; added tests in `TestRobustDatetimeParsing`. Gate 0 + all datetime tests green.

## IMMEDIATE TASK FOR NEXT SESSION (START HERE - HEAVY WORK REQUIRED, NOT OPTIONAL)

**CAMPAIGN 7: PRODUCTION HARDENING FOR REAL CRYPTO DATA** - DO NOT STOP UNTIL SUBSTANTIAL PROGRESS

**NEXT CONCRETE ITEM (Priority 1, item 4) - COMPREHENSIVE DATA QUALITY CHECKS (MUST DO NOW):**

Harden data quality validation in `validate_returns_dataframe`. Add/strengthen checks for gaps, duplicate timestamps across assets, stale data, implausible returns (|r| > X), missing benchmark coverage with clear `BABDataError` messages. This is critical for real crypto data. Make substantial tested changes.

**REQUIRED ACTIONS (HEAVY - NON-NEGOTIABLE):**
1. **Enhance duplicate detection:** Ensure duplicate timestamps across the index are caught and handled robustly (across all code paths). Add explicit tests.
2. **Stale data / large gaps:** Strengthen gap detection (configurable thresholds, better messages). Already partially added - extend with tests for various frequencies.
3. **Implausible returns:** Enforce |r| > threshold (e.g., > 5-10 or configurable) with clear BABDataError messages. Add tests for extreme returns.
4. **Missing/invalid benchmark coverage:** Already present but harden messages and edge cases (benchmark all-NaN, benchmark missing). Add tests.
5. **ADD TESTS (substantial):** Create/extend tests in `tests/test_bab_*` or `tests/test_betting_against_beta_data_loader.py`. All must stay green.

**AFTER ITEM 4 COMPLETE:** Move to Priority 1 item 5+ as needed, continuing heavy work.

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
